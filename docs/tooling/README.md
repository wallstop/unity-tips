# Development Tooling

Stop wasting time on code formatting, style debates, and manual quality checks. These tools automate
your workflow so you can focus on building games.

## The Problem

**Without automation:**

- Teams argue about brace styles, spacing, and naming conventions
- Code reviews waste time on formatting instead of logic
- GC allocations sneak into `Update()` and cause frame drops
- Missing .NET libraries means reinventing wheels

**With these tools:**

- Code auto-formats on save—no debates, no manual fixes
- Style violations show as IDE warnings before commit
- See allocations highlighted in your editor as you type
- Access thousands of .NET packages instantly

## What Each Tool Solves

| Tool                                                     | Problem                                  | Solution                                | Time Saved        |
| -------------------------------------------------------- | ---------------------------------------- | --------------------------------------- | ----------------- |
| [CSharpier](./01-csharpier.md)                           | "Move that brace!" in every PR           | Auto-format on save, 100% consistent    | 5-10 min/day      |
| [EditorConfig](./02-editorconfig.md)                     | Inconsistent naming breaks searchability | IDE warnings for style violations       | 3-5 min/day       |
| [NuGet For Unity](./03-nuget-for-unity.md)               | Can't use .NET ecosystem in Unity        | Install any NuGet package via UPM       | Hours per feature |
| [Heap Allocation Viewer](./04-heap-allocation-viewer.md) | GC spikes cause frame drops              | See allocations highlighted as you type | 1-2 hrs profiling |

## Quick Start (15 minutes)

**For Solo/Learning:**

1. [CSharpier](./01-csharpier.md) – 5 min setup, format on save forever
2. [Heap Allocation Viewer](./04-heap-allocation-viewer.md) – 5 min install, catch GC issues early

**For Teams:**

1. [CSharpier](./01-csharpier.md) – Eliminate formatting debates
2. [EditorConfig](./02-editorconfig.md) – Enforce conventions automatically
3. Add pre-commit hooks (both docs include CI/CD examples)

**For Production:**

- Add [NuGet For Unity](./03-nuget-for-unity.md) when you need .NET libraries
- Use [Heap Allocation Viewer](./04-heap-allocation-viewer.md) during optimization passes

---

## Detailed Guides

1. [CSharpier | Automatic Formatting](./01-csharpier.md)
2. [EditorConfig | Naming & Style Rules](./02-editorconfig.md)
3. [NuGet For Unity | .NET Packages](./03-nuget-for-unity.md)
4. [Heap Allocation Viewer | Catch GC Hotspots](./04-heap-allocation-viewer.md)
