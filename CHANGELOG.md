# Changelog

All notable changes to this project are documented in this file.

The entries below are based on the available development notes and repository state. Where a historical release's exact changes or hardware-test evidence could not be independently confirmed, the entry is intentionally limited to what is documented.

## [Unreleased]

- Add future changes, fixes, and test results here as they are made.
- Record validation performed and clearly distinguish static checks from tests against a physical wallbox.

## [0.2.7.3]

- Version reported by `custom_components/mennekes_amtron/manifest.json` when this changelog was created.
- The precise changes for this version have not yet been confirmed from release notes or commit history.

## [0.2.7.2]

- Corrected GitHub repository metadata URLs in the integration manifest.
- Bumped the integration version.

## [0.2.7.1]

- Changed the plug-lock status sensor so it is no longer categorized as diagnostic.

## [0.2.7]

- Added filtering for clearly invalid total-power readings, including the `0xFFFFFFFF` sentinel and values above 100,000 W.
- Invalid total-power readings do not overwrite the last valid value.
- The filter applies to total power, not to unrelated uint32 sensors.

## [0.2.6.1]

- Fixed a missing `EntityCategory` import.

## Earlier development

- Added local Modbus TCP communication and Home Assistant config-flow setup for the MENNEKES AMTRON Professional wallbox.
- Added charging measurements, vehicle/OCPP status, HEMS current-limit read/write support, RFID authorization controls, firmware and diagnostic/status sensors.
- Added German translations and user-facing installation/configuration documentation.
- RFID authorization uses a select to choose a configured ID and a separate button to send it to the wallbox; selection alone does not perform a write.

These earlier-development bullets summarize project history and are not assigned to a specific release because the exact version boundaries were not confirmed here.

---

## Release and testing notes

For each future release, record:

- **Version and date**
- **Added / Changed / Fixed / Removed**
- **Validation:** syntax checks, automated tests, or repository validation actually run
- **Hardware testing:** exact behavior verified against a wallbox, or state explicitly that no hardware test was performed

Do not describe code review or syntax validation as a successful hardware test.