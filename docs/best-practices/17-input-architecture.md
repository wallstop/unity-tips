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
2. Generate the C# wrapper (`InputActions.cs`) if you need compile-time safety.
3. Use `PlayerInput` with **Send Messages** or **Invoke C# Events** behavior mode to handle input
   via callback methods. This eliminates manual action lookups and subscription management:

```csharp
public class PlayerController : MonoBehaviour
{
    [SerializeField] private float _jumpForce = 10f;
    [SerializeField] private float _moveSpeed = 5f;

    private Rigidbody _rb;
    private bool _jumpRequested;
    private Vector2 _moveInput;

    void Awake() => _rb = GetComponent<Rigidbody>();

    // Called automatically by PlayerInput when Jump action is triggered
    public void OnJump(InputValue value)
    {
        if (value.isPressed)
        {
            _jumpRequested = true;
        }
    }

    // Called automatically when Move action changes
    public void OnMove(InputValue value)
    {
        _moveInput = value.Get<Vector2>();
    }

    void FixedUpdate()
    {
        // Process physics input in FixedUpdate for framerate independence
        if (_jumpRequested)
        {
            _rb.AddForce(Vector3.up * _jumpForce, ForceMode.Impulse);
            _jumpRequested = false;
        }

        Vector3 movement = new Vector3(_moveInput.x, 0f, _moveInput.y) * _moveSpeed;
        _rb.MovePosition(_rb.position + movement * Time.fixedDeltaTime);
    }
}
```

1. Scope action maps by context—disable Gameplay and enable UI when menus open, for example.

### Why OnEvent methods?

Using `PlayerInput` with callback methods (`OnJump`, `OnMove`, etc.) eliminates manual action
lookups and event subscription management:

- **No manual subscription**: PlayerInput automatically routes actions to matching method names.
- **No cleanup needed**: No `OnDisable`/`OnDestroy` to unsubscribe events.
- **Type-safe**: `InputValue` provides typed access via `Get<T>()`, `isPressed`, etc.
- **Designer-friendly**: Method names match action names, making the connection obvious.

### Physics & framerate independence

When using physics (Rigidbody), always **buffer input events** and **process them in
`FixedUpdate()`**:

- Input callbacks (`OnJump`, `OnMove`) fire in `Update()` and may be called zero, one, or multiple
  times between `FixedUpdate()` calls depending on framerate.
- Store input in fields (`_jumpRequested`, `_moveInput`) so `FixedUpdate()` consumes them
  consistently.
- Reset one-shot inputs (`_jumpRequested = false`) after processing to prevent double-jumps at low
  framerates.
- Continuous inputs (movement vectors) don't need resetting—just overwrite with the latest value.

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
