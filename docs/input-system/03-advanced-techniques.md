# Advanced Techniques

> **From prototype to production.** These recipes cover the systems you need when shipping:
> rebinding, multiplayer, mobile, Steam Input, and tooling for debugging.

---

## Table of Contents

1. [Runtime Rebinding](#runtime-rebinding)
2. [Multiplayer](#multiplayer)
3. [Mobile Input](#mobile-input)
4. [Steam Input Integration](#steam-input)
5. [Custom Processors & Interactions](#custom-processors--interactions)
6. [Input Buffering & Combos](#input-buffering--combos)
7. [Debugging & Profiling](#debugging--profiling)

---

## Runtime Rebinding

Runtime rebinding lets players personalise controls without touching your inspector.

```csharp
public IEnumerator RebindJump(InputActionReference actionRef)
{
    InputAction action = actionRef.action;
    action.Disable();

    var operation = action.PerformInteractiveRebinding()
        .OnMatchWaitForAnother(0.1f)
        .WithCancelingThrough("<Keyboard>/escape")
        .OnComplete(op =>
        {
            op.Dispose();
            action.Enable();
            SaveBindings(action);
        })
        .Start();

    yield return new WaitUntil(() => operation.completed || operation.canceled);
}
```

**Best practices**

- Persist overrides (`InputActionAsset.SaveBindingOverridesAsJson`) and restore on launch.
- Provide a cancel binding so players can escape the rebind UI.
- For composite bindings, call `Without(string partName)` to rebind specific directions (e.g.,
  composite `Up`).

---

## Multiplayer

Local multiplayer requires separate action maps per player.

1. Add a `PlayerInputManager` to a bootstrap scene.
2. Configure `joinBehavior = JoinPlayersWhenButtonIsPressed`.
3. Assign a prefab that contains `PlayerInput` and your player scripts.

```csharp
public class PlayerJoin : MonoBehaviour
{
    private void OnEnable()
    {
        PlayerInputManager.instance.playerJoinedEvent.AddListener(OnPlayerJoined);
    }

    private void OnPlayerJoined(PlayerInput player)
    {
        player.camera = CreateVirtualCamera(player);
    }
}
```

**Tips**

- Use **Split Screen** mode for Unity UI so each player has their own event system.
- Store player-specific data (color, score) on the spawned prefab rather than static singletons.
- For online multiplayer, serialise `InputAction` values and send through your networking layer.

---

## Mobile Input

The Input System supports touch, accelerometer, and virtual controls.

- Enable the **Touch Simulation** device in the Input Debugger for quick editor testing.
- Use the **On-Screen Button** / **On-Screen Stick** components for virtual UI controls.
- Read `Pointer` actions with `EnhancedTouchSupport.Enable()` to track multiple touches.
- Combine with adaptive input prompts to display touch icons instead of button glyphs.

```csharp
EnhancedTouchSupport.Enable();
TouchSimulation.Enable();
```

---

## Steam Input

Steam Input can provide glyphs and remapping support on Steam Deck and SteamOS.

- Use the
  [Steam Input for Unity](https://partner.steamgames.com/doc/features/steam_controller/steam_input_unity)
  plugin.
- Map Input System actions to Steam Action Sets and Actions so players can rebind via Steam.
- Provide fallbacks for non-Steam builds (e.g., direct gamepad glyphs via Input System).

> Tip: Expose glyph lookup through a service (e.g., `IInputGlyphProvider`) so your UI can ask for
> the correct icon regardless of platform.

---

## Custom Processors & Interactions

Processors tweak values; interactions decide when an action performs.

```csharp
[UnityEngine.InputSystem.InputProcessor]
public class DeadZoneProcessor : InputProcessor<Vector2>
{
    public float deadZone = 0.2f;

    public override Vector2 Process(Vector2 value, InputControl control)
    {
        return value.magnitude < deadZone ? Vector2.zero : value;
    }
}
```

- Register processors/interactions before enabling actions.
- Use interactions to differentiate tap vs hold without extra coroutines.

---

## Input Buffering & Combos

Buffer actions to make combat responsive:

```csharp
private readonly Queue<(InputAction, float)> _buffer = new();
private const float BufferDuration = 0.2f;

void OnActionPerformed(InputAction.CallbackContext ctx)
{
    _buffer.Enqueue((ctx.action, Time.time));
}

void Update()
{
    while (_buffer.Count > 0 && Time.time - _buffer.Peek().Item2 > BufferDuration)
    {
        _buffer.Dequeue();
    }
}
```

Combine buffering with state machines to execute stored actions when the character becomes ready.

---

## Debugging & Profiling

- Use **Window → Analysis → Input Debugger** to inspect devices, events, and layouts in real time.
- Enable **Input System → Diagnostics** to log performed/canceled events during play testing.
- Profile input-heavy scenes with the **Event Viewer** to spot redundant actions or over-polling.

---

**Next:** Jump to [Common Patterns](./04-common-patterns.md) for ready-to-use gameplay recipes.
