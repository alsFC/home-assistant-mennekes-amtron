# Project Context — Mennekes AMTRON Professional

This document preserves the project's technical context and decisions so development can continue across chats and machines. The repository and current source code are authoritative for the implementation; this file records the background and operational requirements learned during development.

## Project

- Repository: https://github.com/alsFC/home-assistant-mennekes-amtron
- Home Assistant integration domain: `mennekes_amtron`
- Display name: Mennekes AMTRON Professional
- Owner/codeowner: `alsFC`
- Communication: local Modbus TCP, normally port 502
- Integration setup uses a config flow; the integration depends on Home Assistant's Modbus integration.
- Current version: read `version` from `custom_components/mennekes_amtron/manifest.json`. At the time this context file was created, the repository manifest reported **0.2.7.3**. Always verify the file rather than relying on this note.

## Main functionality

The integration provides entities for:
- Vehicle state and OCPP charge-point status
- Total charging power
- Meter total energy, per-phase current and voltage
- EV charging-session energy and duration
- Active RFID ID/tag status
- HEMS current limit (read/write)
- RFID authorization selection and an explicit send button
- Firmware and diagnostic/status values, including CP availability, safe current, operator current limit and plug-lock status

Use the actual source and translations as the authority for current entity IDs, supported values and names.

## Important behavior and design decisions

### Total power / responsive automation

- The total-power sensor is used for PV-surplus charging and battery/energy automations.
- It should update quickly; the target discussed for this sensor is **every 10 seconds**. Verify the current polling implementation before changing it.
- Invalid total-power readings must not replace the last known valid value.
- The filtering added during development rejects the 32-bit sentinel `0xFFFFFFFF` and total-power values above **100,000 W**. Do not silently generalize this filter to unrelated uint32 sensors.

### RFID authorization

- The two user-facing choices are **Firmenwagen** and **Fremd**.
- The IDs are configured through the integration's options.
- The `RFID-Autorisierung` select chooses which configured ID to use; it does **not** write to the wallbox.
- The separate `RFID-Autorisierung senden` button performs the write.
- ID values are ASCII only and limited to 20 bytes. An unused option may be blank; do not send an unconfigured choice.
- The write targets registers 1110–1119 (10 registers = 20 bytes), with space padding/lowercasing as implemented in the source.
- After writing, the integration performs a targeted refresh after about one second to refresh OCPP status and vehicle state.
- This flow replaced a previous helper/automation-based Modbus write path. Do not reintroduce duplicate write mechanisms without a clear reason.

### HEMS current limit

- The integration exposes a writable HEMS current limit.
- A change from 16 A to 15 A was tested successfully, including read-back and confirmation in the wallbox web interface.
- Preserve read-back/verification behavior when modifying writes.

### Status/register interpretation established during testing

These mappings were checked against the device documentation or tested during development; verify against the current code and the documentation for the exact model/firmware before changing them:

| Value | Register | Interpretation |
|---|---:|---|
| Firmware | 100–101 | Firmware value |
| CP availability | 124 | 0 = unavailable, 1 = available |
| Safe current | 131 | Current value |
| Operator current limit | 134 | Current limit |
| Plug lock | 152 | 0 = unlocked, 1 = locked |
| RFID ID/tag write | 1110–1119 | 20-byte ASCII value |

Plug-lock status is a normal sensor, not a diagnostic entity. The diagnostic entities discussed during development were firmware, CP availability, safe current and operator current limit.

## Home Assistant deployment and migration notes

- The integration was developed for an AMTRON Professional wallbox over Modbus TCP.
- The old YAML Modbus configuration was disabled and old Modbus entity-registry entries were removed during migration.
- A grep for active legacy Modbus/RFID YAML references returned no matches at the time of the migration. If changing this area, confirm in the user's Home Assistant configuration rather than assuming the old setup is still active.
- The dashboard was migrated to the new integration and the user confirmed it fit.
- Two kWh template helpers were retained and switched to new integration entities:
  - `sensor.amtron_meter_total_energy_kwh` based on `sensor.amtron_professional_meter_total_energy`
  - `sensor.amtron_ev_charged_energy_large_kwh` based on `sensor.amtron_professional_ev_charged_energy`
- The user chose to keep legacy helper entities temporarily while later adapting surplus-charging automations:
  - `input_text.mennekes_amtron_id_tag`
  - `sensor.mennekes_amtron_id_tag_registerwerte`
  - `input_select.amtron_ev_rfid_auswahl`
  - `input_button.amtron_ev_rfid_senden`
  These are historical notes, not a recommendation to keep them permanently. Check the live configuration before removing them.
- Recorder exclusions were set for `sensor.amtron_professional_meter_current*` and `sensor.amtron_professional_meter_voltage*`. Total power was intentionally not excluded.
- An unrelated Uptime Kuma status entity with a similar Mennekes name was noted; do not confuse it with entities created by this integration.

## Development environment / operational caution

- Home Assistant runs on an Odroid N2 with approximately 3.7 GiB RAM.
- Home Assistant has previously experienced out-of-memory restarts (exit code 137); memory usage was high.
- The Studio Code Server add-on version 7.0.0 was stopped because it was associated with memory pressure/restarts.
- Prefer developing in VS Code on the user's PC, not by leaving VS Code Server running on the Home Assistant host.
- Test changes on the live wallbox cautiously, especially write controls. Never include actual IP addresses, credentials, RFID IDs, tokens or other private configuration values in this public repository.

## Repository and release history notes

The integration was iterated through versions 0.2.6.1, 0.2.7, 0.2.7.1 and subsequent releases:
- 0.2.6.1: fixed a missing `EntityCategory` import.
- 0.2.7: filtered implausible total-power readings without overwriting the last valid value.
- 0.2.7.1: plug-lock status was moved out of the diagnostic category.
- 0.2.7.2: corrected repository metadata URLs and bumped the version.
- The repository manifest currently reports 0.2.7.3 at the time this document was written; inspect Git history/releases to determine the exact contents of that release rather than inferring its change from the version alone.

## Working conventions

1. Inspect current source and Git history before proposing a change; this document can lag behind the implementation.
2. Prefer small, focused changes and explain the reason for each.
3. Preserve Home Assistant entity IDs and unique IDs unless a migration is intentional and documented.
4. Keep user-facing strings translatable; maintain the German translations already present.
5. Do not invent register meanings. Use the relevant MENNEKES documentation and note uncertainty.
6. For Modbus writes, validate input, handle communication errors, and verify read-back where feasible.
7. Keep the README user-facing; put contributor instructions in `docs/DEVELOPMENT.md`.
