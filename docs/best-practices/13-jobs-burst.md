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
    handle.Complete();
}
```

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

Jobs + Burst can produce order-of-magnitude performance gains, but only after profiling proves the
workload is CPU-bound. Start with a single hot loop, measure, and expand from there.
