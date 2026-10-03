# Instructions for AI coding agents

## Source of truth

- Treat the current repository source, tests, manifest and translations as authoritative for implementation details.
- Read `docs/PROJECT_CONTEXT.md` and `docs/DEVELOPMENT.md` before making changes.
- Project context is historical and may be stale. Check the actual code and Git history before relying on it.
- Do not claim to have read or tested anything that was not actually inspected or executed.

## Safety and correctness

- This is a Home Assistant custom integration for a physical EV wallbox using Modbus TCP. Writes can change real charging behavior or RFID authorization.
- Never invent register addresses, value mappings, Home Assistant APIs, test results or device capabilities.
- Before changing a Modbus write, validate data ranges/encoding and preserve error handling/read-back behavior where applicable.
- The RFID flow intentionally separates selection from transmission: selecting an option must not itself write to the wallbox; the explicit send button performs the write.
- Invalid total-power values must not overwrite the last valid value. The known filter rejects the `0xFFFFFFFF` sentinel and values above 100,000 W; verify current implementation before editing.
- Preserve entity IDs/unique IDs unless a migration is intentional and documented.
- Keep translations and user-facing text consistent with existing conventions.
- Do not add real IP addresses, credentials, RFID IDs, tokens, personal information or Home Assistant configuration secrets to the repository.

## Change discipline

- Make small, focused changes and explain the intent.
- Inspect related files and all references before editing.
- Add or update tests/validation where appropriate. Distinguish static checks from tests against real hardware.
- Review the diff for unintended changes and run `git diff --check`.
- Update README or docs when user-visible behavior, setup, controls or release steps change.
- Do not bump the integration version for a documentation-only change unless the maintainer explicitly requests it.
- Do not state that a commit, push, release or deployment succeeded unless the corresponding tool or command confirmed it.
