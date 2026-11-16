---
name: dejaos-device-control
description: Controls and validates DejaOS embedded devices through the dejaos CLI, with bounded retries for intermittent USB HID connection failures. Use when a user asks to connect, stop, sync, start, run, reboot, deploy, or inspect logs for a DejaOS/DX project containing app.dxproj, especially FaceLock or errors mentioning HID Device Not Ready.
---

# DejaOS Device Control

## Quick start

DejaOS CLI requires Node.js 18+. Install it with `npm install -g dejaos-cli` (a pnpm global install is also valid when `dejaos` is on `PATH`), then verify with `dejaos --help`.

Run commands from the directory containing `app.dxproj`, or pass `--project <path>`.

Use the bundled retry wrapper for device commands:

```bash
node ~/.agents/skills/dejaos-device-control/scripts/retry-dejaos.mjs connect --project FaceLock
```

It retries only `HID Device Not Ready`, at most 10 attempts with a 3-second delay. Other errors fail immediately.

## Preflight

1. Verify CLI availability with `dejaos --version` and `dejaos --help`.
2. Confirm the target directory contains `app.dxproj` and report its configured model.
3. Check for competing DXIDE processes with `ps aux | rg -i 'dxide|device_manager|dejaos'`.
4. If VSCode DXIDE owns the device, ask the user to close it. Do not kill editor processes without approval.
5. Test access with the retry wrapper and `connect`.

A successful connection contains `usb open success` and `connect success`.

## Official Workflows
For daily code changes, prefer the official combined workflow:

```bash
node ~/.agents/skills/dejaos-device-control/scripts/retry-dejaos.mjs run --project FaceLock
```

`run` connects to the device, stops the application, incrementally syncs changed files, and starts it again.

After first checkout or changes to component configuration in `app.dxproj`, run sequentially:

```bash
dejaos install --project FaceLock
node ~/.agents/skills/dejaos-device-control/scripts/retry-dejaos.mjs sync --all --project FaceLock
node ~/.agents/skills/dejaos-device-control/scripts/retry-dejaos.mjs start --project FaceLock
```

`install` downloads declared components into `dxmodules/` and does not require the device retry wrapper.

## Explicit Deploy Stages
When the user explicitly asks to stop, sync, and restart the app, run these sequentially:

```bash
node ~/.agents/skills/dejaos-device-control/scripts/retry-dejaos.mjs stop --project FaceLock
node ~/.agents/skills/dejaos-device-control/scripts/retry-dejaos.mjs sync --project FaceLock
node ~/.agents/skills/dejaos-device-control/scripts/retry-dejaos.mjs start --project FaceLock
```

Rules:

- Continue only after the previous step succeeds.
- Treat `sync success` as deployment success even when it reports `0 file(s)`.
- Report every file listed by incremental sync, including unrelated working-tree files.
- If sync fails, leave the application stopped and report that state clearly.
- `start` restarts the application. Do not substitute `reboot`, which restarts the whole device.

Use explicit stages instead of `run` when the user requests them or when precise failure state matters.

## Command Reference
- `edit`: terminal editor for `app.dxproj`; `s` saves and `q` exits.
- `install`: downloads components declared by `app.dxproj` into `dxmodules/`.
- `build`: builds a `.dpk` package in the project build output.
- `connect`: checks and opens the USB device connection.
- `start` / `stop`: starts or stops the application.
- `reboot`: restarts the whole device.
- `sync`: compares saved MD5 state and sends only files changed since the last successful sync.
- `sync --all`: sends every project file.
- `run`: stop, incremental sync, and start.
- `logs`: streams device logs until interrupted with `Ctrl+C`.

## Logs
Use the wrapper with `logs` only under a bounded terminal timeout because logs stream continuously:

```bash
node ~/.agents/skills/dejaos-device-control/scripts/retry-dejaos.mjs logs --project FaceLock
```

Inspect startup output for errors related to changed files. A timeout after logs have started is expected; distinguish it from connection failure.

## Full Sync And Reboot
Use `sync --all` only for first deployment, major component/resource changes, missing device files, known local/device divergence, or when incremental sync leaves files missing. State that all project files will be retransmitted.
Run `dejaos reboot` only when the user explicitly asks for a whole-device reboot or an explained recovery step requires it. Prefer `start` for an application restart.

## Failure Handling
- `HID Device Not Ready`: bounded retry; do not add extra standalone `connect` calls between stages because each CLI command opens its own HID session.
- Persistent HID failure after 10 attempts: check competing processes and USB enumeration, then ask for USB replug.
- No device enumeration: check cable, power, adapter, and USB connection.
- Any other CLI error: stop immediately and report the exact failing stage and key error.
