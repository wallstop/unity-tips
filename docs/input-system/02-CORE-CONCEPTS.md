# Core Concepts

> **Know the building blocks.** This chapter explains how actions, maps, bindings, and control
> schemes all fit together so you can reason about the Input System instead of guessing.

---

## Table of Contents

1. [Action Maps](#action-maps)
2. [Action Types](#action-types)
3. [Bindings & Composite Bindings](#bindings--composite-bindings)
4. [Control Schemes](#control-schemes)
5. [Working with PlayerInput](#working-with-playerinput)
6. [Events vs. Polling](#events-vs-polling)
7. [Devices & Auto-Switching](#devices--auto-switching)

---

## Action Maps

Action maps group related input actions together ("Player", "UI", "Menu"). They let you enable or
disable whole sets of actions at once:

```csharp
// Create from generated wrapper
actions.Player.Enable();
actions.UI.Disable();
```

### Guidelines

- Keep maps focused on player intentions (Movement, Combat, UI) rather than devices.
- Use separate maps for gameplay vs. menus so you can suspend one while the other is active.
- Generated C# wrappers expose maps as properties (`actions.Player`, `actions.UI`).

---

## Action Types

Action types control how the Input System reads devices and when callbacks fire:

- **Button**: True/false input. Fires `started`, `performed`, and `canceled` events.
- **Value**: Returns typed values such as `Vector2` for movement, `float` for triggers, etc.
- **Pass Through**: For raw data (tilt sensors, mouse delta) when you do the processing yourself.

```csharp
public void OnMove(InputAction.CallbackContext ctx)
{
    Vector2 value = ctx.ReadValue<Vector2>();
    if (ctx.performed)
    {
        MoveCharacter(value);
    }
}
```

> Need a refresher later? Jump back from any guide via
> [Action Types](./02-CORE-CONCEPTS.md#action-types).

---

## Bindings & Composite Bindings

Bindings connect actions to devices. Composites combine several controls into one value (WASD into a
`Vector2`).

```csharp
"Move" (Vector2)
    Up [Keyboard/W]
    Down [Keyboard/S]
    Left [Keyboard/A]
    Right [Keyboard/D]
```

- **Use composites** for directional input instead of reading four separate keys.
- **Use processors** (e.g., `NormalizeVector2`) to keep values consistent across devices.
- **Use interactions** (Tap, Hold, Press) to model input intent without extra code.

---

## Control Schemes

Control schemes describe which devices satisfy a map of actions. Examples: `Keyboard&Mouse`,
`Gamepad`, `Touch`.

- Let Unity auto-switch between schemes when devices connect/disconnect.
- Assign a default scheme in `PlayerInput` to decide which gets priority at startup.
- Use `InputUser` or `PlayerInput` events to respond to device changes.

```csharp
playerInput.onControlsChanged += input =>
{
    Debug.Log($"Now using {input.currentControlScheme}");
};
```

---

## Working with PlayerInput

`PlayerInput` is the high-level component that wires action maps to behaviours.

- **Behaviour modes**: `Send Messages`, `Invoke Unity Events`, `Invoke C# Events`. Prefer C# Events
  for type safety.
- **Switching maps**: Call `playerInput.SwitchCurrentActionMap("UI")` when opening menus.
- **Splitscreen/local co-op**: Combine with `PlayerInputManager` to spawn per-player prefabs.

---

## Events vs. Polling

Event-driven input reacts to changes, while polling checks every frame.

- Use callbacks (`performed`, `canceled`) for discrete actions like Jump or Interact.
- Poll in `Update` only when you need continuous values (movement vectors, analog sticks).
- Access `ctx.time` and `ctx.startTime` in callbacks for combo/buffer logic.

---

## Devices & Auto-Switching

The Input System can listen to many devices at once. A few tips:

- Enable **Support Multiple Devices** in the Input Actions asset if players can use keyboard and
  gamepad simultaneously.
- Use `InputSystem.onDeviceChange` to audit connected hardware.
- For splitscreen, use `PlayerInputManager.joinBehavior = JoinPlayersWhenButtonIsPressed` to map
  devices to players as they press controls.

---

**Next:** Continue to [Advanced Techniques](./03-ADVANCED-TECHNIQUES.md) for rebinding, multiplayer,
mobile, and more.
