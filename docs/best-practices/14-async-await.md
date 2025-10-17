# Async/Await Without Breaking Unity

C# `async/await` makes background work and web requests easier to reason about, but Unity's main
thread model requires extra care. Use lightweight schedulers to hop back to the Unity thread and
avoid hidden allocations in per-frame code.

## Common use cases

- Downloading configs or DLC in the background before enabling gameplay.
- Saving cloud progress or analytics without freezing the UI.
- Waiting for Addressables or async scene loads while keeping code linear.

## Threading basics

- Unity APIs must be called on the main thread.
- `Task.Run` executes on the .NET thread pool; returning to the main thread requires an explicit
  scheduler (e.g., `UnityMainThreadDispatcher`, `UniTask`, or `PlayerLoopHelper`).
- Avoid `async void` except for event handlers—use `async Task` so callers can await results.

## Recommended pattern with UniTask

```csharp
using Cysharp.Threading.Tasks;

public async UniTask InitializeAsync()
{
    // Run blocking IO off the main thread
    var json = await UniTask.RunOnThreadPool(() => File.ReadAllText(savePath));

    // Switch back to Unity thread before touching objects
    await UniTask.SwitchToMainThread();
    ApplySettings(JsonUtility.FromJson<PlayerSettings>(json));
}
```

- UniTask pools allocations and supports cancellation tokens; prefer it over raw `Task` in hot
  paths.
- If sticking with `Task`, capture the main thread context (`SynchronizationContext`) at startup and
  post back before interacting with Unity objects.

## Avoid these pitfalls

- **Async in Update** – `async void Update()` allocates state machines every frame. Use coroutines
  or cached tasks triggered by events instead.
- **Forgotten cancellations** – Pass `CancellationToken` to prevent orphaned downloads when scenes
  unload.
- **Deadlocks** – Do not block on `Task.Result` from the main thread; always `await` or continue via
  callbacks.

## Tooling

- Enable the **Heap Allocation Viewer** inspection to catch hidden allocations introduced by async
  state machines.
- Profile background work with the **Timeline** view to confirm tasks complete before you need their
  data.

Async/await keeps long-running work out of the main loop. Just ensure you return to Unity's thread
before touching scene objects and avoid allocating inside per-frame code.
