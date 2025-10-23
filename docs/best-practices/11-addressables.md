# Addressables & Memory-Safe Asset Delivery

Unity's Addressables system decouples asset references from scene files, letting you stream content
on demand, patch bundles remotely, and keep memory usage under control. Treat it as your default
asset pipeline once a project leaves prototype phase.

## Why switch to Addressables?

- **Predictable memory** – Load and unload asset groups explicitly instead of relying on scene
  unloads.
- **Content updates without client rebuilds** – Remote catalogs let you patch art, data, and balance
  without pushing a binary.
- **Dependency tracking** – Addressables charts dependencies, helping you avoid duplicate textures
  or audio clips in bundles.
- **Async-by-default** – All load APIs are asynchronous, keeping frame time stable during content
  swaps.

## Setup checklist

1. Install the Addressables package (Package Manager → Addressables).
2. Convert existing `Resources` or hard references to addressable groups:
   - Use the **Addressables Groups** window to create logical buckets (e.g., `Enemies`, `UI`,
     `Audio`).
   - Keep lightweight, always-on assets in a `Default Local Group`; stream large or optional content
     from remote groups.
3. Profile memory with the **Addressables Event Viewer** and **Profiler** to confirm loads/unloads
   do what you expect.
4. Enable **Build → New Build → Default Build Script** after grouping assets; commit generated
   catalog files so CI and teammates stay in sync.

## Usage patterns

```csharp
// Async load with handle tracking
AsyncOperationHandle<GameObject> enemyHandle = Addressables.LoadAssetAsync<GameObject>(enemyKey);
yield return enemyHandle;

// Prefab instantiation with automatic release handle
AsyncOperationHandle<GameObject> uiHandle = Addressables.InstantiateAsync(uiPanelKey, parent);
yield return uiHandle;
```

- Wrap load handles so you can `yield return handle;` inside coroutines and call
  `Addressables.Release(handle);` when the asset is no longer needed.
- For repeated loads, use `Addressables.LoadAssetAsync` once, cache the result, and release after
  the final consumer finishes.
- Keep catalogs lean by grouping per-level or per-feature; avoid monolithic groups that defeat the
  purpose of streaming.

## Production tips

- **Label everything.** Labels let you batch download or preload groups for a level or campaign.
- Use the **Build → Check for Content Update Restrictions** tool before shipping patches to catch
  breaking asset moves.
- Bake remote catalogs and bundles into a CDN path that matches your live environment structure.
- Pair with the **Memory Profiler** to verify there are no lingering references preventing unloads.

Adopting Addressables early keeps load times smooth, reduces build churn, and lays the groundwork
for live content updates without breaking runtime performance.
