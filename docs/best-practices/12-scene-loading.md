# Scene Organization & Additive Loading

Large Unity projects stay manageable when you split work into small, purpose-driven scenes and load
them additively. A clean scene strategy reduces merge conflicts, shortens iteration time, and keeps
runtime load spikes predictable.

## Core principles

- **Bootstrap vs content** – Keep a tiny bootstrap scene (systems, managers, analytics) that never
  unloads. Load gameplay scenes additively on top of it.
- **One responsibility per scene** – Use separate scenes for level geometry, lighting, UI overlays,
  and cinematics so teams can work in parallel.
- **Async everywhere** – Always load with `SceneManager.LoadSceneAsync` plus a loading screen or
  transition to hide streaming hitches.

## Recommended structure

```
Assets/Scenes/
├── Boot.unity            # Entry point: DI container, Service Locator, global singletons
├── PersistentSystems.unity # Audio, input, save systems (loaded additively)
├── UI.unity              # Global HUD, menus
├── Levels/
│   ├── Level_01.unity
│   └── Level_02.unity
└── Lighting/
    ├── OverworldLighting.unity
    └── DungeonLighting.unity
```

- Load `Boot` first. From there, additively load `PersistentSystems` and `UI`.
- When changing levels, unload only the outgoing content scenes and lighting scenes, leaving global
  systems untouched.

## Async loading pattern

```csharp
public IEnumerator LoadLevelAdditiveCoroutine(string sceneName, Scene currentScene)
{
    AsyncOperationHandle<GameObject> loadingScreenHandle = Addressables.InstantiateAsync("LoadingScreen");
    yield return loadingScreenHandle;

    AsyncOperation loadOp = SceneManager.LoadSceneAsync(sceneName, LoadSceneMode.Additive);
    loadOp.allowSceneActivation = false;

    while (loadOp.progress < 0.9f)
    {
        yield return null;
    }

    // Yield to your fade / transition coroutine before exposing the loaded content.
    loadOp.allowSceneActivation = true;

    while (!loadOp.isDone)
    {
        yield return null;
    }

    if (currentScene.IsValid())
    {
        AsyncOperation unloadOp = SceneManager.UnloadSceneAsync(currentScene);
        while (!unloadOp.isDone)
        {
            yield return null;
        }
    }

    Addressables.ReleaseInstance(loadingScreenHandle);
}
```

- [`SceneManager.LoadSceneAsync`](https://docs.unity3d.com/ScriptReference/SceneManagement.SceneManager.LoadSceneAsync.html)
  returns an [`AsyncOperation`](https://docs.unity3d.com/ScriptReference/AsyncOperation.html); stage
  additive loads by toggling [`allowSceneActivation`](https://docs.unity3d.com/ScriptReference/AsyncOperation-allowSceneActivation.html)
  once your transition completes.
- If the content scene is delivered through Addressables, prefer
  [`Addressables.LoadSceneAsync`](https://docs.unity3d.com/Packages/com.unity.addressables@1.21/api/UnityEngine.AddressableAssets.Addressables.LoadSceneAsync.html)
  so you can `yield return` the handle in a coroutine and release it with
  [`Addressables.UnloadSceneAsync`](https://docs.unity3d.com/Packages/com.unity.addressables@1.21/api/UnityEngine.AddressableAssets.Addressables.UnloadSceneAsync.html).
- Keep the [`Addressables.InstantiateAsync`](https://docs.unity3d.com/Packages/com.unity.addressables@1.21/api/UnityEngine.AddressableAssets.Addressables.InstantiateAsync.html)
  handle for UI such as loading screens and dispose it with
  [`Addressables.ReleaseInstance`](https://docs.unity3d.com/Packages/com.unity.addressables@1.21/api/UnityEngine.AddressableAssets.Addressables.ReleaseInstance.html)
  once the indicator is hidden.
- Chain lighting or additive detail scenes and update focus via
  [`SceneManager.SetActiveScene`](https://docs.unity3d.com/ScriptReference/SceneManagement.SceneManager.SetActiveScene.html)
  immediately after activation so lighting probes, event systems, and `GetActiveScene` calls line up
  with the new environment.

## Tips for collaboration

- Use **Scene Templates** or custom editor scripts to guarantee every new scene starts with the
  right setup (Lighting, Post-processing, etc.).
- Keep `DontDestroyOnLoad` usage minimal; persistent systems should live in explicitly loaded
  persistent scenes.
- Profile load spikes with the Editor Profiler and Addressables Event Viewer to spot missing
  preloads.

Additive scene loading keeps teams productive and delivers seamless transitions for players, without
locking level design to massive monolithic scenes.
