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

Use a `Vector2` value action (WASD / left stick) to drive movement in `Update`.

```csharp
public class PlayerMover : MonoBehaviour
{
    [SerializeField] private float _speed = 5f;
    private InputAction _move;

    void Awake()
    {
        _move = GetComponent<PlayerInput>().actions["Move"];
    }

    void Update()
    {
        Vector2 input = _move.ReadValue<Vector2>();
        Vector3 direction = new(input.x, 0f, input.y);
        transform.Translate(direction * _speed * Time.deltaTime, Space.World);
    }
}
```

Tips:

- Apply `NormalizeVector2` processor on the action to prevent diagonal speed boost.
- For physics-driven movement, sample input in `Update` but apply forces in `FixedUpdate`.

---

## Camera Controls

Read a `Vector2` for look deltas. Use separate bindings for mouse and right stick.

```csharp
public class FreeLookCamera : MonoBehaviour
{
    [SerializeField] private float _sensitivity = 3f;
    [SerializeField] private Transform _target;

    private InputAction _look;
    private float _pitch;
    private float _yaw;

    void Awake()
    {
        _look = GetComponent<PlayerInput>().actions["Look"];
    }

    void LateUpdate()
    {
        Vector2 delta = _look.ReadValue<Vector2>();
        _yaw += delta.x * _sensitivity * Time.deltaTime;
        _pitch = Mathf.Clamp(_pitch - delta.y * _sensitivity * Time.deltaTime, -70f, 80f);

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
public void OnSelectSlot(InputAction.CallbackContext ctx)
{
    int slotIndex = (int)ctx.ReadValue<float>();
    inventory.SelectSlot(slotIndex);
}
```

---

## Charging Attacks

Use a Hold interaction to get performed/canceled callbacks.

```csharp
private float _chargeStart;

public void OnCharge(InputAction.CallbackContext ctx)
{
    if (ctx.started)
    {
        _chargeStart = Time.time;
    }
    else if (ctx.canceled)
    {
        float duration = Time.time - _chargeStart;
        FireChargedShot(duration);
    }
}
```

- Configure thresholds on the Hold interaction to decide when `performed` fires.

---

## Context Actions

Change what an action does based on nearby interactables.

```csharp
public class InteractionPrompt : MonoBehaviour
{
    [SerializeField] private InputActionReference _action;
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

    public void OnInteract(InputAction.CallbackContext ctx)
    {
        if (ctx.performed && _current != null)
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
