# Troubleshooting & Best Practices

> **Running into issues?** Use this guide to diagnose common Input System problems quickly.

---

## Table of Contents

1. [Common Issues](#common-issues)
2. [Performance](#performance)
3. [Actions Firing Twice](#actions-firing-twice)
4. [Gamepad Detection](#gamepad-detection)
5. [Mobile Touch Problems](#mobile-touch-problems)
6. [UI Consuming Gameplay Input](#ui-consuming-gameplay-input)
7. [Migration Guide](#migration-guide)
8. [Checklist](#checklist)

---

## Common Issues

### No Input in Play Mode

- Confirm the Input System package is installed (`Window → Package Manager`).
- Set **Active Input Handling** to `Input System Package (New)` in Project Settings.
- Ensure the PlayerInput component references the correct Input Actions asset.

### Input Works in Editor, Not in Build

- Add the Input Actions asset to `PlayerInput` and tick "Auto-Save" before building.
- Register on-screen controls in a script (Edit Mode only controls won't exist in builds).

---

## Performance

- Disable unused action maps (`actions.UI.Disable()`) when not needed.
- Avoid per-frame calls to `Enable()`/`Disable()`; wrap state changes around screen transitions.
- Profile with the **Input Debugger → Event Trace** to find noisy devices.

---

## Actions Firing Twice

- Ensure you didn't subscribe to both `performed` and `canceled` when you only need one.
- Check for duplicated PlayerInput components on the same GameObject.
- In "Both" input handling mode, the legacy Input Manager may also fire events—use only the new
  system if possible.

---

## Gamepad Detection

- Watch `InputSystem.onDeviceChange` to log connected/disconnected devices.
- For XInput controllers on Windows, install the latest Visual C++ redistributables.
- On consoles, verify you're using the platform-specific input package if required (e.g., Switch).

---

## Mobile Touch Problems

- Enable `EnhancedTouchSupport` before reading touches.
- On Android, grant permission to use the touchscreen when requested.
- Ensure on-screen controls are active in the loaded scene (not hidden by UI states).

---

## UI Consuming Gameplay Input

- If using the Input System UI Input Module, assign a separate UI action map so gameplay actions can
  remain enabled.
- Disable the UI event system when switching back to gameplay.
- For world-space UI, ensure the correct event camera is set.

---

## Migration Guide

1. Enable **Both** input handling temporarily.
2. Convert scripts by reading from `InputAction`s instead of `Input.GetAxis`.
3. Swap out `StandaloneInputModule` for **Input System UI Input Module**.
4. Update tutorials/tooltips to display action names instead of hardcoded key names.
5. Once stable, switch project setting to **Input System Package (New)** only.

---

## Checklist

- [ ] Action maps organised and disabled when not in use
- [ ] Gameplay/UI maps separated
- [ ] Devices tested: keyboard, Xbox, PlayStation, Switch Pro, touch
- [ ] Rebinding UI saves overrides to disk
- [ ] Input buffering or coyote time implemented where needed

---

**Still stuck?** Join the [Unity forums](https://forum.unity.com/forums/input-system.103/) or file a
bug with repro steps attached.
