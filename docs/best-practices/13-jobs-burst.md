# Job System & Burst Fundamentals

Unity's C# Job System and Burst compiler unlock major CPU savings when you process large data sets.
Use them for math-heavy gameplay, procedural generation, or background simulation that does not need
main-thread access every frame.

## When to reach for Jobs + Burst

- You have thousands of entities or components to update each frame (particles, boids, crowd sims).
- Tight loops spend time in pure math or data transforms (pathfinding, damage queries, IK).
- Profiling shows the main thread dominated by scripts that could be parallelized.

## Minimal workflow

1. Mark data with `NativeArray`, `NativeList`, or `NativeSlice` so jobs can read/write safely.
2. Define a struct implementing `IJob`, `IJobParallelFor`, or `IJobChunk`.
3. Decorate with `[BurstCompile]` to get Burst’s vectorized machine code.
4. Schedule the job and complete it before you need the results.

- Common namespaces: `Unity.Burst`, `Unity.Collections`, `Unity.Jobs`, and `Unity.Mathematics`.

```csharp
[BurstCompile]
public struct DamageFalloffJob : IJobParallelFor
{
    [ReadOnly] public NativeArray<float> distances;
    public NativeArray<float> damage; // write output

    public void Execute(int index)
    {
        var d = distances[index];
        damage[index] = math.max(0f, 100f - d * 2f);
    }
}

// Usage inside a MonoBehaviour or system
void LateUpdate()
{
    var job = new DamageFalloffJob { distances = distances, damage = damageOutput };
    var handle = job.Schedule(distances.Length, 64);
    // Or check handle completion and complete later, for async processing
    handle.Complete();
}
```

- Schedule jobs from `MonoBehaviour`, `SystemBase`, or `PlayerLoop` code that already runs each
  frame. Think of jobs as fire-and-forget work packets—schedule, store the `JobHandle`, then pick up
  the results later.

## Example: batched physics probes

Sampling dozens of `Physics.Raycast` calls per frame tanks the main thread. Instead, feed raycast
commands into Unity's job-friendly `RaycastCommand` API, then process the hits with a Burst job.

```csharp
[BurstCompile]
public struct CollectRaycastHitsJob : IJobParallelFor
{
    [ReadOnly] public NativeArray<RaycastHit> Hits;
    public NativeArray<float> Heights;

    public void Execute(int index)
    {
        Heights[index] = Hits[index].collider != null
            ? Hits[index].point.y
            : float.MinValue;
    }
}

public void SampleTerrain(NativeArray<float3> origins, NativeArray<float> heights)
{
    var commands = new NativeArray<RaycastCommand>(origins.Length, Allocator.TempJob);
    var hits = new NativeArray<RaycastHit>(origins.Length, Allocator.TempJob);

    for (var i = 0; i < origins.Length; i++)
    {
        commands[i] = new RaycastCommand(origins[i], Vector3.down, 100f);
    }

    var raycastHandle = RaycastCommand.ScheduleBatch(commands, hits, 32);
    var collectHandle = new CollectRaycastHitsJob { Hits = hits, Heights = heights }
        .Schedule(hits.Length, 32, raycastHandle);

    // Or complete later, async
    collectHandle.Complete();
    commands.Dispose();
    hits.Dispose();
}
```

- Collect the `float3` origins on the main thread, schedule the built-in `RaycastCommand` batch, and
  read the results back into your movement system once `collectHandle` completes.
- Burst compiles the post-processing job, while Unity handles the raycasts natively on worker
  threads. You still avoid the main-thread spikes from looping over `Physics.Raycast`.

## Best practices

- **Burst-compatible data only** – No managed objects, `class` references, or virtual calls inside
  jobs. Convert to structs and `NativeArray` beforehand.
- **Minimize sync points** – Chain jobs with dependencies instead of calling `Complete()`
  immediately after scheduling.
- **Use the Profiler Timeline** – Verify jobs actually run off the main thread and that Burst is
  active (look for the lightning icon in the Profiler).
- **Guard with defines** – Wrap editor-only safety checks in `#if ENABLE_UNITY_COLLECTIONS_CHECKS`
  for production builds.

## Safety tips

- Dispose all native containers (`Dispose()` or `using` with `NativeArray`) to prevent memory leaks.
- Keep job structs small and pass large data via `NativeArray` references, not copies.
- Validate results on the main thread before pushing to systems that require Unity APIs.

## Scenario playbook

- **Crowd steering:** Run an `IJobParallelFor` to compute separation/seek vectors for every agent,
  then blend them on the main thread to update `Rigidbody` velocities.
- **Procedural terrain:** Generate heightmaps with Burst jobs that evaluate noise ahead of time while
  the player is still on the previous chunk.
- **Background economy sims:** Accumulate timers, interest, or crafting progress with `IJobFor`
  while the player is in menus. Merge the results once per second instead of every frame.
- **VFX batching:** Calculate billboard rotations, trail widths, or GPU instance matrices in jobs,
  copying the final buffer into `Graphics.DrawMeshInstanced` when ready.

Jobs + Burst can produce order-of-magnitude performance gains, but only after profiling proves the
workload is CPU-bound. Start with a single hot loop, measure, and expand from there.
