"""Device-specific Modbus communication for Mennekes AMTRON Professional."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from modbus_connection import ModbusUnit
from modbus_connection.decode import decode_uint32

from .const import (
    REG_FIRMWARE,
    REG_METER_COUNT,
    REG_METER_START,
    REG_OCPP_STATUS,
    REG_SESSION_COUNT,
    REG_SESSION_START,
    REG_TOTAL_POWER,
    REG_HEMS_CURRENT_LIMIT,
    REG_WRITE_IDTAG_START,
    REG_VEHICLE_STATE,
    REG_CP_AVAILABILITY,
    REG_SAFE_CURRENT,
    REG_OPERATOR_CURRENT_LIMIT,
    REG_PLUG_LOCK_STATUS,
)



# The AMTRON can transiently return 0xFFFFFFFF for an invalid/unavailable
# 32-bit measurement. Never expose that sentinel as a real power value.
_INVALID_UINT32 = 0xFFFFFFFF
_MAX_PLAUSIBLE_TOTAL_POWER_W = 100_000


def _valid_total_power(value: int) -> bool:
    return value != _INVALID_UINT32 and 0 <= value <= _MAX_PLAUSIBLE_TOTAL_POWER_W

def _u32(words: list[int], offset: int) -> int:
    return decode_uint32(words[offset : offset + 2])


def _decode_rfid(words: list[int]) -> str:
    raw = bytearray()
    for word in words:
        raw.extend(((word >> 8) & 0xFF, word & 0xFF))
    return raw.decode("ascii", errors="replace").rstrip("\x00").strip()


@dataclass
class AmtronSnapshot:
    """Latest values read from the wallbox."""
    firmware: str | None = None
    vehicle_state: int | None = None
    cp_availability: int | None = None
    safe_current_a: int | None = None
    operator_current_limit_a: int | None = None
    plug_lock_status: int | None = None
    total_power: int | None = None
    ocpp_status: int | None = None
    current_l1_ma: int | None = None
    current_l2_ma: int | None = None
    current_l3_ma: int | None = None
    total_energy_wh: int | None = None
    voltage_l1_v: int | None = None
    voltage_l2_v: int | None = None
    voltage_l3_v: int | None = None
    ev_max_current_a: int | None = None
    session_energy_wh: int | None = None
    charge_duration_s: int | None = None
    active_rfid: str | None = None
    hems_current_limit_a: int | None = None


class MennekesAmtronDevice:
    """Thin device library around a shared Home Assistant ModbusUnit."""

    def __init__(self, unit: ModbusUnit) -> None:
        self.unit = unit
        self.data = AmtronSnapshot()
        # Be deliberately gentle with the AMTRON ECU.
        # Some Home Assistant temporary Modbus unit implementations expose
        # message spacing, while others do not. Keep this optional and rely
        # on the connection library's default timeout.
        if hasattr(self.unit, "set_message_spacing"):
            self.unit.set_message_spacing(0.10)

    async def async_read_firmware(self) -> None:
        """Read firmware version (two holding registers / four ASCII bytes)."""
        words = await self.unit.read_holding_registers(REG_FIRMWARE, 2)
        raw = bytearray()
        for word in words:
            raw.extend(((word >> 8) & 0xFF, word & 0xFF))
        self.data.firmware = raw.decode("ascii", errors="replace").rstrip("\x00").strip()

    async def async_read_general_status(self) -> None:
        """Read low-frequency CP availability and plug-lock state."""
        self.data.cp_availability = (
            await self.unit.read_holding_registers(REG_CP_AVAILABILITY, 1)
        )[0]
        self.data.plug_lock_status = (
            await self.unit.read_holding_registers(REG_PLUG_LOCK_STATUS, 1)
        )[0]

    async def async_read_current_limits(self) -> None:
        """Read rarely changing current limits."""
        self.data.safe_current_a = (
            await self.unit.read_holding_registers(REG_SAFE_CURRENT, 1)
        )[0]
        self.data.operator_current_limit_a = (
            await self.unit.read_holding_registers(REG_OPERATOR_CURRENT_LIMIT, 1)
        )[0]

    async def async_read_power(self) -> None:
        """Read total power, the value HA needs most frequently."""
        total_power = decode_uint32(
            await self.unit.read_holding_registers(REG_TOTAL_POWER, 2)
        )
        if _valid_total_power(total_power):
            self.data.total_power = total_power

    async def async_read_vehicle_state(self) -> None:
        """Read the control-pilot vehicle state."""
        self.data.vehicle_state = (
            await self.unit.read_holding_registers(REG_VEHICLE_STATE, 1)
        )[0]

    async def async_read_status(self) -> None:
        self.data.ocpp_status = (
            await self.unit.read_holding_registers(REG_OCPP_STATUS, 1)
        )[0]

    async def async_read_meter(self) -> None:
        words = await self.unit.read_holding_registers(REG_METER_START, REG_METER_COUNT)
        self.data.current_l1_ma = _u32(words, 0)
        self.data.current_l2_ma = _u32(words, 2)
        self.data.current_l3_ma = _u32(words, 4)
        self.data.total_energy_wh = _u32(words, 6)
        total_power = _u32(words, 8)
        if _valid_total_power(total_power):
            self.data.total_power = total_power
        self.data.voltage_l1_v = _u32(words, 10)
        self.data.voltage_l2_v = _u32(words, 12)
        self.data.voltage_l3_v = _u32(words, 14)

    async def async_read_session(self) -> None:
        words = await self.unit.read_holding_registers(REG_SESSION_START, REG_SESSION_COUNT)
        self.data.ev_max_current_a = words[0]
        self.data.session_energy_wh = _u32(words, 1)
        self.data.charge_duration_s = _u32(words, 3)
        self.data.active_rfid = _decode_rfid(words[5:15])

    async def async_read_hems(self) -> None:
        """Read the configured HEMS current limit."""
        self.data.hems_current_limit_a = (
            await self.unit.read_holding_registers(REG_HEMS_CURRENT_LIMIT, 1)
        )[0]

    async def async_set_hems_current_limit(self, value: int) -> None:
        """Set HEMS current limit in amperes (0 pauses charging)."""
        if not 0 <= value <= 32:
            raise ValueError("HEMS current limit must be between 0 and 32 A")
        await self.unit.write_register(REG_HEMS_CURRENT_LIMIT, value)
        self.data.hems_current_limit_a = value

    async def async_authorize_rfid(self, rfid: str) -> None:
        """Present an RFID IDTag to the AMTRON through registers 1110-1119."""
        tag = rfid.strip().lower()
        if not tag:
            raise ValueError("RFID IDTag must not be empty")
        try:
            raw = tag.encode("ascii")
        except UnicodeEncodeError as err:
            raise ValueError("RFID IDTag must contain ASCII characters only") from err
        if len(raw) > 20:
            raise ValueError("RFID IDTag must not exceed 20 ASCII characters")
        raw = raw.rjust(20, b" ")
        words = [(raw[i] << 8) | raw[i + 1] for i in range(0, 20, 2)]
        await self.unit.write_registers(REG_WRITE_IDTAG_START, words)

    async def async_validate(self) -> None:
        """Probe a known register without writing anything."""
        words = await self.unit.read_holding_registers(REG_VEHICLE_STATE, 1)
        if len(words) != 1:
            raise ValueError("Unexpected response length")
