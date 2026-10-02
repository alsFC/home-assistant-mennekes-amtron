# Mennekes AMTRON Professional for Home Assistant

An independent custom integration for local monitoring and control of MENNEKES AMTRON Professional wallboxes over Modbus TCP.

## Features

- Local Modbus TCP communication
- Vehicle state and OCPP charge-point status
- Total charging power and energy measurements
- Phase currents and voltages
- Charging session energy and duration
- HEMS current-limit read/write support
- Selectable RFID authorization and explicit send button
- Firmware and diagnostic sensors
- German translations

## Installation with HACS

1. In GitHub, create a public repository named **`home-assistant-mennekes-amtron`** under the account `alsFC`.
2. Upload the contents of this repository so that `custom_components/mennekes_amtron/` is directly in the repository root.
3. Publish a GitHub Release named/tagged `v0.2.7.1`.
4. In Home Assistant, open **HACS → Integrations**.
5. Open the HACS menu and choose **Custom repositories**.
6. Add `https://github.com/alsFC/home-assistant-mennekes-amtron` and select **Integration** as the category.
7. Find **Mennekes AMTRON Professional** in HACS and install it.
8. Restart Home Assistant. If the integration is already installed manually, keep the existing integration entry; do not remove/re-add it just for the HACS migration.
9. If HACS reports that the integration is already present, use the existing files/repository entry and follow the update/reload instructions shown by HACS.

## Initial setup

After installation, go to **Settings → Devices & services → Add integration**, search for **Mennekes AMTRON Professional**, and enter the wallbox connection details requested by the config flow.

The wallbox must be reachable from Home Assistant over Modbus TCP. The default Modbus TCP port is usually `502`; use the actual port and unit ID configured for your device.

## Notes

- The total-power sensor rejects clearly invalid readings, including the `0xFFFFFFFF` 32-bit sentinel and values above 100,000 W. Invalid readings do not overwrite the last valid value.
- This project is community-developed and is not affiliated with, endorsed by, or supported by MENNEKES Elektrotechnik GmbH & Co. KG.
- Check the device and register documentation for your exact wallbox model/firmware before using control features.

## Support and bug reports

Please open an issue in the [GitHub issue tracker](https://github.com/alsFC/home-assistant-mennekes-amtron/issues). Include your Home Assistant version, integration version, relevant logs, and a description of the expected and actual behavior. Remove credentials, RFID values, and other private information from logs before posting.

## License

MIT. See [LICENSE](LICENSE).
