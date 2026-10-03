# Development Guide

## Local setup

Develop on a workstation with VS Code and Git. Avoid leaving a code-server add-on running on the Home Assistant Odroid N2: that host has limited memory and has previously experienced out-of-memory restarts.

Clone the repository:

```bash
git clone https://github.com/alsFC/home-assistant-mennekes-amtron.git
cd home-assistant-mennekes-amtron
```

Useful checks:

```bash
git status
git remote -v
git log -5 --oneline
```

## Before changing code

1. Read `README.md`, `AGENTS.md`, and `docs/PROJECT_CONTEXT.md`.
2. Inspect the relevant platform/module, translations and `manifest.json`.
3. Search for all uses of an entity, register, option or service before changing its behavior.
4. Confirm current Home Assistant APIs and Modbus semantics instead of relying on assumptions.
5. Avoid changing entity unique IDs unless a deliberate migration is included.

## Suggested workflow

Use a focused branch for non-trivial changes:

```bash
git switch main
git pull --ff-only
git switch -c fix/short-description
```

After editing:

```bash
git diff --check
git diff
git status
```

Run the available repository checks and any relevant syntax/format checks. Do not claim that hardware behavior was tested unless it was actually tested against a wallbox. For Modbus writes, prefer safe read-back checks and be explicit about what requires live hardware.

Stage specific files where possible:

```bash
git add path/to/changed_file.py path/to/translation.json
git commit -m "Short imperative description"
git push -u origin fix/short-description
```

Then open a pull request or merge according to the project's chosen workflow. For a small personal project, commits to `main` may be used if intentional, but review the diff first. Never commit secrets, real wallbox IPs, RFID IDs, logs with personal data, or local configuration.

## Release checklist

1. Update `version` in `custom_components/mennekes_amtron/manifest.json` when releasing a code change.
2. Update documentation/translations if behavior or user-facing entities changed.
3. Run repository validation and inspect the final diff.
4. Ensure the README accurately describes installation and control behavior.
5. Commit and push the release changes.
6. Create a GitHub Release with a tag matching the version, e.g. `vX.Y.Z`, if using tagged releases.
7. Install/update through HACS and restart Home Assistant.
8. Verify the integration loads and the relevant entities update. Test write controls only when it is safe to do so.
9. Record the tested Home Assistant version, integration version, test scope and any limitations.

## Debugging checklist

- Check Home Assistant Core logs for integration setup, Modbus communication and platform errors.
- Verify host, port and network reachability without publishing local network details.
- Distinguish a Modbus read failure from a legitimate zero value.
- For total power, preserve the last valid reading when a value is clearly invalid.
- Check entity registry/unique IDs before concluding that an entity was removed or renamed.
- Keep any live test result distinct from static code review or syntax checks.
