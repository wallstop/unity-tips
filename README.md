# Unity Tips & Tools - Complete Guide

> **Everything you need to build professional Unity games.** A comprehensive collection of best
> practices, tools, and documentation to accelerate your Unity development from beginner to expert.

---

## 🎯 What Is This?

This repository contains:

- **✅ Best practices guides** for Unity development (lifecycle methods, physics, serialization,
  etc.)
- **✅ In-depth documentation** for essential Unity tools and plugins
- **✅ Beginner-friendly explanations** of complex topics
- **✅ Real-world examples** from production games
- **✅ Quick reference cards** for common patterns

**Perfect for:** Unity developers of all skill levels who want to write better code, avoid common
pitfalls, and ship games faster.

---

## 🚀 Quick Start (5 Minutes)

### New to Unity?

Start here in order:

1. **[Best Practices](./docs/best-practices/README.md)** - Foundation concepts (lifecycle, null
   checks, components)
2. **[Unity Helpers](./docs/unity-helpers/README.md)** - Essential utilities to eliminate
   boilerplate
3. **[Hot Reload](./docs/hot-reload/README.md)** - Edit code without recompiling (save 2-3
   hours/day!)

### Building a 2D Game?

You need these tools:

1. **[Unity Helpers](./docs/unity-helpers/README.md)** - Component auto-wiring, object pooling, plus
   2D editor tools
2. **[Animancer](./docs/animancer/README.md)** - Code-driven animation control
3. **[Feel](./docs/feel/README.md)** - Game feel and juice (screen shake, particles, etc.)
4. **[PrimeTween](./docs/primetween/README.md)** - Zero-allocation animations and tweens

### Optimizing Performance?

Essential performance tools:

1. **[Graphy](./docs/graphy/README.md)** - Real-time FPS/memory monitor (FREE!)
2. **[Assembly Definitions](./docs/assembly-definitions/README.md)** - 10-100x faster compile times
3. **[Better Build Info PRO](./docs/better-build-info/README.md)** - Build size analysis
4. **[Object Pooling Best Practices](./docs/best-practices/09-object-pooling.md)** - Eliminate GC
   spikes

### Working on a Large Project?

Critical organization tools:

1. **[Assembly Definitions](./docs/assembly-definitions/README.md)** - Manage compile times and
   dependencies
2. **[Odin Inspector](./docs/odin/README.md)** - Serialize dictionaries, powerful Inspector tools
3. **[Asset Usage Finder](./docs/asset-usage-finder/README.md)** - Find where assets are used
4. **[DxMessaging](./docs/dxmessaging/README.md)** - Type-safe, zero-leak messaging

---

## 📚 Complete Tool Catalog

### Foundation & Best Practices

- [Unity Best Practices](./docs/best-practices/README.md) – Common pitfalls, organized in a learning
  path.
- [Development Tooling](./docs/tooling/README.md) – Keep formatting, naming, and workflow automation
  tight.

### Core Utilities

- [Unity Helpers](./docs/unity-helpers/README.md) – Component auto-wiring, pooling, and
  serialization helpers.
- [Hot Reload](./docs/hot-reload/README.md) – Modify code in play mode with sub-second iteration
  times.
- [Odin Inspector & Serializer](./docs/odin/README.md) – Advanced Inspector tooling and
  serialization upgrades.
- [Animancer](./docs/animancer/README.md) – Code-driven animation control without Animator
  spaghetti.
- [PrimeTween](./docs/primetween/README.md) – Zero-allocation animation and tweens.
- [Feel](./docs/feel/README.md) – Drop-in game juice (screenshake, particles, feedback systems).
- [NuGet For Unity](./docs/tooling/03-nuget-for-unity.md) – Install NuGet packages through UPM with
  a Unity-first workflow.

### Performance & Debugging

- [Graphy](./docs/graphy/README.md) – Real-time FPS, memory, and audio graphs in-game.
- [Better Build Info PRO](./docs/better-build-info/README.md) – Visual build size analysis and
  comparisons.
- [Asset Usage Finder](./docs/asset-usage-finder/README.md) – Trace asset references before deleting
  anything.
- [Assembly Definitions](./docs/assembly-definitions/README.md) – Split projects to slash compile
  times.
- [Unity Input System](./docs/input-system/README.md) – Modern, rebinding-friendly input across
  devices.
- [DxMessaging](./docs/dxmessaging/README.md) – Lightweight, type-safe messaging for large projects.
- [Heap Allocation Viewer](./docs/tooling/04-heap-allocation-viewer.md) – IDE highlights for GC
  allocations in hot paths.

### Production Extras

- [Unity Helpers – Editor Tools](./docs/unity-helpers/README.md#feature-5-editor-tools-suite) –
  Menu-driven utilities for sprites, prefabs, and more.
- [Better Build Info – Workflow](./docs/better-build-info/README.md#workflow-integration) – Bake
  build analysis into CI.

## 🎯 Recommended Stacks

- **PC / Console:** [Unity Helpers](./docs/unity-helpers/README.md),
  [Animancer](./docs/animancer/README.md), [PrimeTween](./docs/primetween/README.md),
  [Feel](./docs/feel/README.md), [Input System](./docs/input-system/README.md),
  [Hot Reload](./docs/hot-reload/README.md).
- **Mobile:** [Best Practices](./docs/best-practices/README.md),
  [Unity Helpers](./docs/unity-helpers/README.md), [Graphy](./docs/graphy/README.md),
  [Heap Allocation Viewer](./docs/tooling/04-heap-allocation-viewer.md),
  [Better Build Info PRO](./docs/better-build-info/README.md),
  [PrimeTween](./docs/primetween/README.md),
  [Assembly Definitions](./docs/assembly-definitions/README.md).
- **Large Team:** [Best Practices](./docs/best-practices/README.md),
  [CSharpier](./docs/tooling/01-csharpier.md), [EditorConfig](./docs/tooling/02-editorconfig.md),
  [Assembly Definitions](./docs/assembly-definitions/README.md),
  [NuGet For Unity](./docs/tooling/03-nuget-for-unity.md),
  [Heap Allocation Viewer](./docs/tooling/04-heap-allocation-viewer.md),
  [Odin Inspector](./docs/odin/README.md), [DxMessaging](./docs/dxmessaging/README.md),
  [Hot Reload](./docs/hot-reload/README.md).
- **Learning / Solo:** [Best Practices](./docs/best-practices/README.md),
  [CSharpier](./docs/tooling/01-csharpier.md), [EditorConfig](./docs/tooling/02-editorconfig.md),
  [Unity Helpers](./docs/unity-helpers/README.md), [Graphy](./docs/graphy/README.md),
  [Heap Allocation Viewer](./docs/tooling/04-heap-allocation-viewer.md), add
  [Hot Reload](./docs/hot-reload/README.md) once compile times hurt.

## 📖 Learning Paths

### Beginner Path (10-15 hours total)

**Week 1: Foundation**

1. [Best Practices - Lifecycle Methods](./docs/best-practices/01-lifecycle-methods.md) (15 min)
2. [Best Practices - Null Checks](./docs/best-practices/02-null-checks.md) (10 min)
3. [Best Practices - Component Access](./docs/best-practices/03-component-access.md) (15 min)
4. **Practice:** Build simple character controller

**Week 2: Core Tools**

1. [Unity Helpers - Quick Start](./docs/unity-helpers/README.md#quick-start) (30 min)
2. [PrimeTween - Getting Started](./docs/primetween/README.md) (30 min)
3. [Graphy - Setup](./docs/graphy/README.md) (5 min)
4. **Practice:** Add health system with animations

**Week 3: Advanced Concepts**

1. [Best Practices - Coroutines](./docs/best-practices/05-coroutines.md) (20 min)
2. [Best Practices - Physics](./docs/best-practices/06-physics.md) (18 min)
3. [Feel - Getting Started](./docs/feel/README.md) (30 min)
4. **Practice:** Add game feel to your project

---

### Intermediate Path (20-30 hours total)

**Prerequisites:** Complete Beginner Path

**Focus Areas:**

1. **Animation** - [Animancer complete guide](./docs/animancer/README.md) (2-3 hours)
2. **Input** - [Input System](./docs/input-system/README.md) (2-3 hours)
3. **Performance** - [Best Practices - Performance](./docs/best-practices/07-performance-memory.md)
   (1 hour)
4. **Architecture** - [ScriptableObjects](./docs/best-practices/08-scriptable-objects.md) (1 hour)
5. **Optimization** - [Object Pooling](./docs/best-practices/09-object-pooling.md) (1 hour)

**Practice Project:** Complete 2D platformer or top-down shooter

---

### Advanced Path (40+ hours total)

**Prerequisites:** Complete Intermediate Path

**Focus Areas:**

1. **Architecture** - [DxMessaging](./docs/dxmessaging/README.md) (2 hours)
2. **Workflow** - [Assembly Definitions](./docs/assembly-definitions/README.md) (2 hours)
3. **Data** - [Odin Inspector](./docs/odin/README.md) (3 hours)
4. **Optimization** - [Better Build Info PRO](./docs/better-build-info/README.md) (2 hours)
5. **Professional Polish** - Deep dive all tools' advanced sections

**Practice Project:** Mobile game with performance requirements or multi-system game

---

## 🎓 Recommended Free Tools (Start Here!)

If you're on a budget, these FREE tools will take you 80% of the way:

1. ✅ **[Best Practices](./docs/best-practices/README.md)** - FREE knowledge that prevents bugs
2. ✅ **[CSharpier](./docs/tooling/01-csharpier.md)** - FREE automatic code formatting
3. ✅ **[EditorConfig](./docs/tooling/02-editorconfig.md)** - FREE style enforcement
4. ✅ **[Graphy](./docs/graphy/README.md)** - FREE performance monitor (Unity Awards winner!)
5. ✅ **[PrimeTween](./docs/primetween/README.md)** - FREE zero-allocation animations
6. ✅ **[Input System](./docs/input-system/README.md)** - FREE official Unity package
7. ✅ **[Assembly Definitions](./docs/assembly-definitions/README.md)** - FREE built-in Unity
   feature
8. ✅ **[DxMessaging](./docs/dxmessaging/README.md)** - FREE open-source messaging
9. ✅ **[Asset Usage Detector](https://github.com/yasirkula/UnityAssetUsageDetector)** - FREE
   alternative to Asset Usage Finder
10. ✅ **[Heap Allocation Viewer](./docs/tooling/04-heap-allocation-viewer.md)** - FREE IDE plugin
    to flag per-frame GC allocations

**Add when budget allows:**

- [Hot Reload](./docs/hot-reload/README.md) - $10-15/month (Free tier available) - Pays for itself
  in 1-2 days
- [Unity Helpers](./docs/unity-helpers/README.md) - FREE! (Open source)
- [Feel](./docs/feel/README.md) - €46 (Free MMFeedbacks version available)
- [Animancer](./docs/animancer/README.md) - ~$50-100
- [Odin](./docs/odin/README.md) - ~$55

---

## 🤝 Contributing

Found an issue or want to suggest improvements? Please open an issue or pull request!

This documentation is a living resource that grows with Unity's ecosystem.

---

## 📄 License

Documentation and examples are provided for educational purposes. Individual tools have their own
licenses - check each tool's documentation for details.

---

## 🌟 Credits

This collection is built from:

- Official Unity documentation
- Community best practices
- Real-world production experience
- Tool developer documentation
- Years of Unity development knowledge

Special thanks to all tool developers who make Unity development better!

---

**Ready to level up your Unity development?**

👉 Start with [Best Practices](./docs/best-practices/README.md) to build a solid foundation!

---
