# Robust Input Architecture

Unity's Input System supports action maps, rebinding, and multi-device play. Architect your input
handling around actions instead of raw polling to keep gameplay responsive and designer-friendly.

## Core concepts

- **Action maps** – Group related controls (Gameplay, UI, Photo Mode) so you can enable/disable them
  wholesale.
- **Control schemes** – Define keyboard/mouse, gamepad, touch, and VR bindings separately.
- **Player Input** – Use `PlayerInput` or multiplayer input components to spawn per-player action
  maps automatically.

## Recommended architecture

1. Create a single `InputActions` asset with multiple maps (Gameplay, UI, Debug).
2. Generate the C# wrapper (`InputActions.cs`) and inject it into systems that need input.
3. Use events instead of polling in `Update()`:

```csharp
public class PlayerJump : MonoBehaviour
{
    [SerializeField] private PlayerInput input;

    void OnEnable() => input.actions["Jump"].performed += OnJump;
    void OnDisable() => input.actions["Jump"].performed -= OnJump;

    private void OnJump(InputAction.CallbackContext ctx)
    {
        if (!ctx.ReadValueAsButton()) return;
        jumpController.Trigger();
    }
}
```

1. Scope action maps by context—disable Gameplay and enable UI when menus open, for example.

## Rebinding UX

- Use the built-in `InputActionRebindingExtensions.PerformInteractiveRebinding()` to capture new
  bindings.
- Persist bindings via `PlayerPrefs` or your save system and reapply them on boot.
- Present visual feedback (current binding, conflicts, restore default) to reduce player confusion.

## Multiplayer considerations

- Instantiate `PlayerInput` per player; assign control schemes manually or let Unity auto-assign
  when a device joins.
- For split-screen, use separate cameras and action maps so each player’s input stays isolated.
- Sync rebinding per-player—store them in profiles rather than global settings.

## Testing & maintenance

- Unit test gameplay logic by injecting fake input data instead of reading from `InputAction` inside
  tests.
- Profile input latency using the **Input Debugger** window and compare across devices.
- Document device-specific quirks (e.g., Nintendo Switch minus button) so bindings remain
  consistent.

Building an input architecture around actions keeps your controls flexible, supports accessibility,
and scales cleanly to additional devices or players without rewiring your entire codebase.
