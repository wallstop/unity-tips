# Heap Allocation Viewer | Catch GC Hotspots

Heap Allocations Viewer (Rider/ReSharper plugin) highlights every managed allocation that your C#
code would trigger at runtime. For Unity projects, that means you can spot `new` allocations,
boxing, closures, and LINQ calls inside per-frame code before they ever hit players.

## Why Update-loop allocations hurt

`Update()` can execute 30–120 times per second on every active `MonoBehaviour`. Even a few bytes of
transient heap memory per frame per object snowball into megabytes each minute. The .NET/Mono GC
then has to pause the main thread to reclaim that memory:

- **Frame drops & stutter** – GC collections stop the Unity player thread, so frequent collections
  show up as hitching and input lag.
- **Mobile impact** – Mobile CPUs are slower and often thermally throttled, so GC spikes are longer
  and more noticeable.
- **Background systems** – Allocations in AI, pathfinding, combat logs, or UI updates all add up
  when they run every frame.

Catching allocations as you type is the cheapest way to avoid these problems.

## Install in JetBrains Rider (Unity Hub default)

1. Open `File → Settings…` (`Ctrl+,` / `Cmd+,`).
2. Navigate to `Plugins → Marketplace` and search for **Heap Allocations Viewer**.
3. Click **Install**, then restart Rider.

> ✅ The plugin ships with the Unity/Rider integration, but installing it explicitly guarantees you
> have the latest version.

## Install in Visual Studio + ReSharper

1. Open `Extensions → ReSharper → Extension Manager…`.
2. Search for **Heap Allocations Viewer** (ID: `com.jetbrains.resharper.heapview`).
3. Install and restart Visual Studio.

## Configure “yell-at-me” highlighting

### Rider / IntelliJ-based IDEs

1. `File → Settings… → Editor → Inspections → C# → Performance`.
2. Set **Heap allocation (from Heap Allocations Viewer)** to **Error** severity so it stands out.
3. While still focused on the inspection, use the gear icon → **Edit Highlighting in Editor** to:
   - Change the effect to **Solid underline** or **Wavy underline**.
   - Enable **Bold** and **Italic** font styles to make the offending call sites scream.
4. Apply and restart if prompted.

You can further adjust colors at `Settings → Editor → Color Scheme → Inspections → Heap allocation`.

### Visual Studio + ReSharper

1. `Extensions → ReSharper → Options… → Code Inspection → Inspection Severity`.
2. Locate **Heap allocation** and change severity to **Error**.
3. Open `Tools → Options → Environment → Fonts and Colors`.
4. Filter the display items list for **ReSharper Heap Allocation** entries and set:
   - **Font style:** Bold + Italic.
   - **Item foreground:** attention-grabbing color (e.g., red/orange).
   - **Display items effect:** Single underline.

## What gets flagged

- Object, array, and delegate creation via `new`.
- Boxing conversions (e.g., assigning a struct to `object`, `string.Format` with value types).
- Captures that allocate hidden closure classes (lambdas, local functions).
- LINQ queries and iterator blocks that generate enumerator objects.
- `foreach` loops over value types that trigger boxing.

Hovering the underline shows a tooltip describing the exact allocation so you can refactor (pool the
object, reuse a struct, move work out of `Update()`, etc.).

## Workflow tips

- Audit per-frame methods (`Update`, `FixedUpdate`, `LateUpdate`, UI `OnValueChanged`) regularly—the
  plugin highlights issues instantly.
- Pair with Unity’s **Profile Analyzer** or **Timeline** to confirm GC spikes disappeared after
  refactors.
- Remember that some allocations are unavoidable; add a code comment when you intentionally keep one
  so future reviewers know it was a conscious trade-off.

Proactively catching allocations keeps your frame time flat and your players happy—especially on
mobile hardware with limited CPU headroom.
