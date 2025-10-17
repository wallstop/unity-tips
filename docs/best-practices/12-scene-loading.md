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
public async Task LoadLevelAsync(string sceneName)
{
    var loadingScreen = Addressables.InstantiateAsync("LoadingScreen");
    await loadingScreen.Task;

    await SceneManager.LoadSceneAsync(sceneName, LoadSceneMode.Additive);
    await SceneManager.UnloadSceneAsync(currentScene);

    await Addressables.ReleaseInstance(loadingScreen);
}
```

- Use `allowSceneActivation = false` to stage a scene, then flip it true once your fade-out
  completes.
- Chain lighting or additive detail scenes (`SceneManager.SetActiveScene`) immediately after the
  base scene activates.

## Tips for collaboration

- Use **Scene Templates** or custom editor scripts to guarantee every new scene starts with the
  right setup (Lighting, Post-processing, etc.).
- Keep `DontDestroyOnLoad` usage minimal; persistent systems should live in explicitly loaded
  persistent scenes.
- Profile load spikes with the Editor Profiler and Addressables Event Viewer to spot missing
  preloads.

Additive scene loading keeps teams productive and delivers seamless transitions for players, without
locking level design to massive monolithic scenes.
