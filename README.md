# Unity Tips & Tools

<a href="https://wallstop.github.io/unity-tips/"><img src="https://img.shields.io/badge/docs-GitHub%20Pages-blue?style=for-the-badge" alt="Documentation"></a>
<a href="https://github.com/wallstop/unity-tips/wiki"><img src="https://img.shields.io/badge/wiki-GitHub%20Wiki-green?style=for-the-badge" alt="Wiki"></a>

> Battle-tested practices and tools to build better Unity games faster. From beginner to expert.

**[View the full documentation site](https://wallstop.github.io/unity-tips)** - Best viewed on
GitHub Pages with search, dark mode, and organized navigation.

---

> **AI-Assisted Documentation**
>
> This documentation was created with AI assistance. All asset recommendations, tips, and
> architectural patterns are sourced and driven by [wallstop](https://github.com/wallstop) based on
> real-world Unity development experience. AI (Claude) has been used to help generate code samples,
> format documents, create examples, and audit content for accuracy. All content has been reviewed
> for correctness.

---

> **⚠️ PAID ASSETS WARNING**
>
> This repository includes recommendations for 3rd party paid assets (unaffiliated). These assets
> are valuable tools that solve specific problems, but they **cost money** and sometimes have free
> alternatives.
>
> **Do NOT purchase these assets unless:**
>
> - You have personally experienced the problem they solve
> - You have exhausted all free alternatives
> - The time saved justifies the cost for your specific project
>
> Start with the free tools and best practices first. Only invest in paid tools when you hit their
> specific pain points.

---

## 🎯 What Problem Does This Solve?

**The Problem:** Unity is powerful but has hidden pitfalls—`is null` fails silently,
`GetComponent()` in `Update()` kills performance, physics in `Update()` causes jitter, and memory
leaks are easy to create.

**This Repository:**

- **Prevents common bugs** before you write them (lifecycle order, null checks, serialization)
- **Speeds up development** with tools that eliminate recompiles and manual formatting
- **Optimizes performance** from day one with pooling, caching, and allocation tracking
- **Scales with your team** through automation, standards, and architecture patterns

Start with [Best Practices](./docs/best-practices/README.md) to avoid 80% of Unity bugs, then add
[Development Tooling](./docs/tooling/README.md) to automate your workflow.

---

## 🚀 Quick Start

### **New to Unity?** → Start Here (15 min)

1. [Best Practices](./docs/best-practices/README.md) – Prevent 80% of bugs (lifecycle, null checks)
2. [Development Tooling](./docs/tooling/README.md) – Auto-format code, catch allocations

### **2D Game?** → Add Polish (30 min)

1. [Animancer](./docs/animancer/README.md) – Code-driven animation (no Animator spaghetti)
2. [Feel](./docs/feel/README.md) – Screen shake, particles, juice
3. [PrimeTween](./docs/primetween/README.md) – Zero-allocation tweens

### **Performance Issues?** → Optimize (1 hour)

1. [Graphy](./docs/graphy/README.md) – Real-time FPS/memory graphs (FREE)
2. [Heap Allocation Viewer](./docs/tooling/04-heap-allocation-viewer.md) – Catch GC spikes in IDE
3. [Object Pooling](./docs/best-practices/09-object-pooling.md) – Eliminate spawn stutters

### **Large Team/Project?** → Scale Up (2 hours)

1. [Assembly Definitions](./docs/assembly-definitions/README.md) – Cut compile time by 10-100x
2. [CSharpier + EditorConfig](./docs/tooling/README.md) – Enforce formatting automatically
3. [Odin Inspector](./docs/odin/README.md) – Serialize dictionaries, powerful editors

---

## 📚 All Tools by Problem

### **Foundation** (Start Here)

| Tool                                                                  | Problem It Solves                             | Cost |
| --------------------------------------------------------------------- | --------------------------------------------- | ---- |
| [Best Practices](./docs/best-practices/README.md)                     | Avoid Unity's hidden bugs & pitfalls          | FREE |
| [CSharpier](./docs/tooling/01-csharpier.md)                           | Stop debating code style, auto-format on save | FREE |
| [EditorConfig](./docs/tooling/02-editorconfig.md)                     | Enforce naming conventions across team        | FREE |
| [Heap Allocation Viewer](./docs/tooling/04-heap-allocation-viewer.md) | Catch GC allocations before they ship         | FREE |

### **Workflow & Speed**

| Tool                                                          | Problem It Solves                               | Cost   |
| ------------------------------------------------------------- | ----------------------------------------------- | ------ |
| [Hot Reload](./docs/hot-reload/README.md)                     | Stop waiting for recompiles (2-3 hrs/day saved) | $10/mo |
| [Assembly Definitions](./docs/assembly-definitions/README.md) | Cut compile time by 10-100x                     | FREE   |
| [NuGet For Unity](./docs/tooling/03-nuget-for-unity.md)       | Use .NET packages in Unity projects             | FREE   |
| [Unity Helpers](./docs/unity-helpers/README.md)               | Eliminate boilerplate (auto-wiring, pooling)    | FREE   |

### **Animation & Polish**

| Tool                                      | Problem It Solves                               | Cost |
| ----------------------------------------- | ----------------------------------------------- | ---- |
| [Animancer](./docs/animancer/README.md)   | Replace Animator Controller spaghetti with code | ~$75 |
| [PrimeTween](./docs/primetween/README.md) | Zero-allocation tweens & sequences              | FREE |
| [Feel](./docs/feel/README.md)             | Add screen shake, particles, juice fast         | €46  |

### **Performance & Debugging**

| Tool                                                        | Problem It Solves                         | Cost |
| ----------------------------------------------------------- | ----------------------------------------- | ---- |
| [Graphy](./docs/graphy/README.md)                           | Monitor FPS/memory/audio in real-time     | FREE |
| [Better Build Info PRO](./docs/better-build-info/README.md) | Find what's bloating your build size      | ~$30 |
| [Asset Usage Finder](./docs/asset-usage-finder/README.md)   | See where assets are used before deleting | ~$20 |

### **Architecture & Scale**

| Tool                                                                  | Problem It Solves                                            | Cost |
| --------------------------------------------------------------------- | ------------------------------------------------------------ | ---- |
| [Event Systems Comparison](./docs/best-practices/10-event-systems.md) | ScriptableObject events vs DxMessaging (DxMessaging wins)    | FREE |
| [DxMessaging](./docs/dxmessaging/README.md)                           | Type-safe messaging without memory leaks (superior approach) | FREE |
| [Odin Inspector](./docs/odin/README.md)                               | Serialize dictionaries, custom editors                       | ~$55 |
| [Input System](./docs/input-system/README.md)                         | Modern input with rebinding support                          | FREE |

## 🎯 Recommended Tool Stacks

Choose based on your target platform and team size:

| Use Case          | Essential Tools                              | Why                                         |
| ----------------- | -------------------------------------------- | ------------------------------------------- |
| **Learning/Solo** | Best Practices + CSharpier + Graphy          | Build solid fundamentals, catch bugs early  |
| **Mobile**        | Add: Heap Allocation Viewer + Object Pooling | Performance is critical on mobile           |
| **2D Game**       | Add: Animancer + Feel + PrimeTween           | Animation control + juice + smooth movement |
| **Large Team**    | Add: EditorConfig + Assembly Definitions     | Enforce standards, manage compile time      |
| **Production**    | Add: Hot Reload + Odin + DxMessaging         | Speed up iteration, scale architecture      |

## 📖 Learning Path

### **Week 1-2: Foundation** (4 hours)

Start here regardless of experience level:

1. [Lifecycle Methods](./docs/best-practices/01-lifecycle-methods.md) – When code runs (15 min)
2. [Null Checks](./docs/best-practices/02-null-checks.md) – Unity's "fake null" (10 min)
3. [Component Access](./docs/best-practices/03-component-access.md) – Cache, don't call repeatedly
   (15 min)
4. [CSharpier](./docs/tooling/01-csharpier.md) – Auto-format on save (10 min)
5. **Practice:** Build a character controller

### **Month 1: Core Patterns** (10 hours)

Add essential Unity patterns:

- [Coroutines](./docs/best-practices/05-coroutines.md) – Time-based operations (20 min)
- [Physics](./docs/best-practices/06-physics.md) – FixedUpdate and forces (18 min)
- [Serialization](./docs/best-practices/04-serialization.md) – Inspector fields (12 min)
- [Heap Allocation Viewer](./docs/tooling/04-heap-allocation-viewer.md) – Catch GC spikes (15 min)
- **Practice:** 2D platformer or top-down shooter

### **Month 2-3: Advanced** (20+ hours)

Master architecture and optimization:

- [Event Systems](./docs/best-practices/10-event-systems.md) – ScriptableObject events vs
  DxMessaging (30 min)
- [ScriptableObjects](./docs/best-practices/08-scriptable-objects.md) – Data-driven design (25 min)
- [Object Pooling](./docs/best-practices/09-object-pooling.md) – Eliminate spawn lag (18 min)
- [Assembly Definitions](./docs/assembly-definitions/README.md) – Slash compile times
- [Animancer](./docs/animancer/README.md) or [Odin](./docs/odin/README.md) – Based on needs
- **Practice:** Complete game with performance requirements

---

## 🤝 Contributing

Found a mistake or want to add a tool? Open an issue or PR. This is a living document that grows
with Unity's ecosystem.

---

**Ready to start?** → [Best Practices Guide](./docs/best-practices/README.md)

**Want automation?** → [Development Tooling](./docs/tooling/README.md)
