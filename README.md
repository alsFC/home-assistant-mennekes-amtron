# Mennekes AMTRON Professional for Home Assistant

An independent custom integration for local monitoring and control of MENNEKES AMTRON Professional wallboxes over Modbus TCP.

## Features

- Local Modbus TCP communication
- Vehicle state and OCPP charge-point status
- Total charging power and energy measurements
- Phase currents and voltages
- Charging session energy and duration
- HEMS current-limit read/write support
- RFID authorization with configurable RFID IDs
- Firmware and diagnostic sensors
- German translations

## Installation

### Install with HACS

1. Make sure [HACS](https://www.hacs.xyz/) is installed and working in Home Assistant.
2. Open **HACS → Integrations**.
3. Open the menu and choose **Custom repositories**.
4. Add this repository URL: `https://github.com/alsFC/home-assistant-mennekes-amtron`
5. Select **Integration** as the category and confirm.
6. Find **Mennekes AMTRON Professional** in HACS and select **Download**.
7. Restart Home Assistant when prompted.

### Add the integration to Home Assistant

1. Open **Settings → Devices & services**.
2. Select **Add integration**.
3. Search for **Mennekes AMTRON Professional**.
4. Enter the wallbox IP address or hostname and the Modbus TCP port. The default port is `502`.
5. Complete setup. Home Assistant must be able to reach the wallbox over Modbus TCP.

If the integration is already installed, update it through HACS and restart Home Assistant. Do not delete the existing integration entry just to update the files.

## Configure RFID IDs

The integration provides two RFID choices in Home Assistant: **Firmenwagen** and **Fremd**. Configure the ID associated with each choice in the integration's options:

1. Go to **Settings → Devices & services → Integrations**.
2. Open **Mennekes AMTRON Professional** and select **Configure** (the options/settings action).
3. Enter the RFID ID for **Firmenwagen** and/or **Fremd**, then save.
4. In the integration's entities, select the desired choice using **RFID-Autorisierung**.
5. Press **RFID-Autorisierung senden** to write the selected ID to the wallbox.

The select entity only chooses which configured ID to use; it does not send the ID by itself. The separate send button performs the write.

RFID ID values must be ASCII text and no longer than 20 bytes. Non-ASCII characters are not supported. You may leave an ID field empty if you do not use that choice; do not select and send a choice without a configured ID.

**Caution:** Sending an RFID ID changes the ID tag value written to the wallbox. Verify the configured IDs before using the send button.

## Sensors and controls

The integration exposes charging power and energy, phase measurements, vehicle and OCPP states, charging duration, current limits, RFID authorization controls, and diagnostic information. Some values are read-only; the HEMS current limit and RFID authorization are writable controls.

The total-power sensor rejects clearly invalid readings, including the `0xFFFFFFFF` 32-bit sentinel and values above 100,000 W. Invalid readings do not overwrite the last valid value.

## Troubleshooting and bug reports

Please open an issue in the [GitHub issue tracker](https://github.com/alsFC/home-assistant-mennekes-amtron/issues). Include your Home Assistant version, integration version, relevant logs, and a description of the expected and actual behavior. Remove credentials, RFID values, and other private information from logs before posting.

## Disclaimer

This is an independent community project and is not affiliated with, endorsed by, or supported by MENNEKES Elektrotechnik GmbH & Co. KG. Check the device and register documentation for your exact wallbox model and firmware before using control features.

## License

MIT. See [LICENSE](LICENSE).
