# Profiling & Telemetry Workflow

Performance issues only disappear when you measure them. Unity ships powerful profilers for CPU,
GPU, memory, and rendering—build them into your weekly routine so regressions never make it to
players.

## Core tools

- **Unity Profiler** – Real-time CPU/GPU timeline. Attach to editor and device builds.
- **Profile Analyzer** – Compare profiler captures and spot frame-time spikes.
- **Memory Profiler** – Inspect heap usage, track leaks, and verify Addressables unload correctly.
- **Frame Debugger** – Step through draw calls and overdraw.
- **Custom telemetry** – Instrument gameplay (e.g., combat length, load times) and send to
  dashboards.

## Weekly profiling loop

1. Capture a five-minute profiler session from a development build on target hardware.
2. Export it and run comparisons against last week's capture using Profile Analyzer.
3. Log findings in a living performance doc with owner + fix ETA.
4. Add automated checks (frame time thresholds, memory budgets) to CI where possible.

## Capturing tips

- Use **Deep Profiling** sparingly—it inflates numbers. Prefer development builds with specific
  profiler markers.
- Toggle `Development Build` + `Autoconnect Profiler` for quick device sessions.
- Wrap expensive gameplay systems with `ProfilerMarker` and `using (marker.Auto())` to create custom
  timeline entries.

```csharp
static readonly ProfilerMarker CombatTickMarker = new("Combat.System.Tick");

void Tick()
{
    using (CombatTickMarker.Auto())
    {
        // damage application
    }
}
```

## Ship-stopping metrics

- **Frame time budget** – 16.6 ms for 60 FPS, 33.3 ms for 30 FPS. Track CPU + GPU.
- **GC allocations** – Inspect the Profiler’s GC Alloc column; any spikes in `Update()` require
  action.
- **Memory footprint** – Stay within console/mobile limits with a 20% buffer for worst-case spikes.
- **Load times** – Record scene and Addressables load durations; establish targets per platform.

## Automation ideas

- Add `Unity -batchmode -profiler-log-file` runs in CI to capture standardized scenarios.
- Parse profiler logs to confirm GC allocations stay under an agreed threshold.
- Use telemetry dashboards (Datadog, Grafana, PlayFab) to flag regressions after each release.

Shipping without a profiling cadence invites hitches, crashes, and angry reviews. Bake profiling
into your workflow so every build earns the "production ready" badge before QA ever touches it.
