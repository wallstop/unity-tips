# Common Patterns

> **Practical building blocks.** Use these patterns as a starting point, then tailor them to your
> project.

---

## Table of Contents

1. [Character Movement](#character-movement)
2. [Camera Controls](#camera-controls)
3. [Menu Navigation](#menu-navigation)
4. [Inventory Hotkeys](#inventory-hotkeys)
5. [Charging Attacks](#charging-attacks)
6. [Context Actions](#context-actions)
7. [Input Hints & Prompts](#input-hints--prompts)
8. [Accessibility Features](#accessibility-features)

---

## Character Movement

Use a `Vector2` value action (WASD / left stick) with the `OnMove` callback method.

```csharp
public class PlayerMover : MonoBehaviour
{
    [SerializeField] private float _speed = 5f;
    private Vector2 _moveInput;

    // Called automatically by PlayerInput when Move action changes
    public void OnMove(InputValue value)
    {
        _moveInput = value.Get<Vector2>();
    }

    void Update()
    {
        Vector3 direction = new(_moveInput.x, 0f, _moveInput.y);
        transform.Translate(direction * _speed * Time.deltaTime, Space.World);
    }
}
```

Tips:

- Apply `NormalizeVector2` processor on the action to prevent diagonal speed boost.
- For physics-driven movement, buffer input in `OnMove()` but apply forces in `FixedUpdate()`:

```csharp
public class PhysicsPlayerMover : MonoBehaviour
{
    [SerializeField] private float _speed = 5f;
    private Rigidbody _rb;
    private Vector2 _moveInput;

    void Awake() => _rb = GetComponent<Rigidbody>();

    public void OnMove(InputValue value)
    {
        _moveInput = value.Get<Vector2>();
    }

    void FixedUpdate()
    {
        Vector3 movement = new(_moveInput.x, 0f, _moveInput.y) * _speed;
        _rb.MovePosition(_rb.position + movement * Time.fixedDeltaTime);
    }
}
```

---

## Camera Controls

Read a `Vector2` for look deltas with the `OnLook` callback. Use separate bindings for mouse and
right stick.

```csharp
public class FreeLookCamera : MonoBehaviour
{
    [SerializeField] private float _sensitivity = 3f;
    [SerializeField] private Transform _target;

    private Vector2 _lookInput;
    private float _pitch;
    private float _yaw;

    // Called automatically by PlayerInput when Look action changes
    public void OnLook(InputValue value)
    {
        _lookInput = value.Get<Vector2>();
    }

    void LateUpdate()
    {
        _yaw += _lookInput.x * _sensitivity * Time.deltaTime;
        _pitch = Mathf.Clamp(_pitch - _lookInput.y * _sensitivity * Time.deltaTime, -70f, 80f);

        transform.rotation = Quaternion.Euler(_pitch, _yaw, 0f);
        transform.position = _target.position;
    }
}
```

---

## Menu Navigation

Switch to a UI action map when showing menus.

```csharp
public class PauseMenu : MonoBehaviour
{
    [SerializeField] private GameObject _menuRoot;

    private PlayerInput _playerInput;

    void Awake() => _playerInput = GetComponent<PlayerInput>();

    public void TogglePause()
    {
        bool isActive = !_menuRoot.activeSelf;
        _menuRoot.SetActive(isActive);
        _playerInput.SwitchCurrentActionMap(isActive ? "UI" : "Player");
    }
}
```

- Use dedicated `Submit`, `Cancel`, and `Navigate` actions in the UI map.
- If you use the Input System UI Input Module, assign the same actions to the Event System.

---

## Inventory Hotkeys

Map number keys (or D-pad) to quick slots using a **1D Axis Composite** or discrete button actions.

```csharp
// Called automatically by PlayerInput when SelectSlot action triggers
public void OnSelectSlot(InputValue value)
{
    int slotIndex = (int)value.Get<float>();
    inventory.SelectSlot(slotIndex);
}
```

---

## Charging Attacks

Use a Hold interaction and track button state in the `OnCharge` callback.

```csharp
private float _chargeStart;
private bool _isCharging;

// Called automatically by PlayerInput when Charge action changes
public void OnCharge(InputValue value)
{
    bool isPressed = value.isPressed;

    if (isPressed && !_isCharging)
    {
        _chargeStart = Time.time;
        _isCharging = true;
    }
    else if (!isPressed && _isCharging)
    {
        float duration = Time.time - _chargeStart;
        FireChargedShot(duration);
        _isCharging = false;
    }
}
```

Tips:

- Configure thresholds on the Hold interaction to decide when `performed` fires.
- For continuous charging feedback (e.g., power bar), update in `Update()` while `_isCharging` is
  true.

---

## Context Actions

Change what an action does based on nearby interactables.

```csharp
public class InteractionPrompt : MonoBehaviour
{
    [SerializeField] private CanvasGroup _promptUI;

    private IInteractable _current;

    void OnTriggerEnter(Collider other)
    {
        if (other.TryGetComponent(out IInteractable interactable))
        {
            _current = interactable;
            _promptUI.alpha = 1f;
        }
    }

    void OnTriggerExit(Collider other)
    {
        if (_current != null && other.TryGetComponent(out IInteractable interactable) && interactable == _current)
        {
            _current = null;
            _promptUI.alpha = 0f;
        }
    }

    // Called automatically by PlayerInput when Interact action is triggered
    public void OnInteract(InputValue value)
    {
        if (value.isPressed && _current != null)
        {
            _current.Interact();
        }
    }
}
```

---

## Input Hints & Prompts

- Use `InputBinding.DisplayStringOptions` to customise `action.GetBindingDisplayString()`.
- Swap sprites based on `action.activeControl?.device` to show the right glyph (keyboard, Xbox,
  PlayStation, etc.).

---

## Accessibility Features

- Offer remapping ([Runtime Rebinding](./03-ADVANCED-TECHNIQUES.md#runtime-rebinding)).
- Provide input assist options (toggle hold vs. tap, auto-sprint).
- Support co-pilot by enabling multiple devices on the same player.

---

**Need fixes?** Continue to [Troubleshooting](./05-TROUBLESHOOTING.md).
