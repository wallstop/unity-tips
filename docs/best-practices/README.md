# Unity Best Practices

A comprehensive, beginner-friendly guide to Unity best practices. This collection covers common
patterns, pitfalls, and solutions that every Unity developer should know - organized in **optimal
learning order** from beginner to advanced topics.

## 📚 Table of Contents (Learning Order)

### Foundation (Start Here!)

1. [**Lifecycle Methods**](./01-lifecycle-methods.md) - Awake vs Start, Update vs FixedUpdate
2. [**Null Checks**](./02-null-checks.md) - Unity's "fake null" and safe comparison patterns
3. [**Component Access**](./03-component-access.md) - Efficient component lookup and caching
4. [**Serialization**](./04-serialization.md) - SerializeField vs public, Inspector organization

### Core Patterns

1. [**Coroutines**](./05-coroutines.md) - Time-based operations and async workflows
2. [**Physics**](./06-physics.md) - Proper physics update loops and force application
3. [**Performance & Memory**](./07-performance-memory.md) - GC, allocations, and optimization

### Advanced Patterns

1. [**ScriptableObjects**](./08-scriptable-objects.md) - Data-driven design and shared configuration
2. [**Object Pooling**](./09-object-pooling.md) - Performance optimization for frequent spawning
3. [**Event Systems**](./10-event-systems.md) - ScriptableObject Events vs DxMessaging comparison

### Systems & Architecture

1. [**Addressables**](./11-addressables.md) - Memory-safe asset streaming and live content updates
2. [**Scene Organization**](./12-scene-loading.md) - Additive loading and collaboration-friendly
   layouts
3. [**Jobs & Burst**](./13-jobs-burst.md) - Parallelize CPU-heavy work with native performance
4. [**Async/Await**](./14-async-await.md) - Background tasks without breaking Unity's main thread

### Production Excellence

1. [**Profiling Workflow**](./15-profiling.md) - Instrument performance and catch regressions early
2. [**Automated Testing & CI**](./16-automated-testing-ci.md) - Keep builds stable with headless
   tests
3. [**Input Architecture**](./17-input-architecture.md) - Action-based controls, rebinding, and
   multiplayer
4. [**Save/Load & Versioning**](./18-save-load.md) - Durable data with Protobuf and Unity Helpers

## 🎯 Quick Start Guide

### Absolute Beginners

**Start with the Foundation section** - these are the core concepts you'll use every day:

1. **[Lifecycle Methods](./01-lifecycle-methods.md)** - When to use Awake vs Start vs Update

   - This is THE most fundamental Unity concept
   - Prevents 80% of initialization bugs

2. **[Null Checks](./02-null-checks.md)** - Why `== null` works but `is null` doesn't

   - Catches 50% of beginner NullReferenceExceptions
   - 5-minute read that saves hours of debugging

3. **[Component Access](./03-component-access.md)** - Cache in Awake, use TryGetComponent

   - Prevents performance issues from day one
   - Learn good habits early

4. **[Serialization](./04-serialization.md)** - Use `[SerializeField] private` not `public`
   - Keeps your code clean and maintainable
   - Proper encapsulation from the start

### Intermediate Developers

**After the Foundation**, learn these core patterns:

1. **[Coroutines](./05-coroutines.md)** - Handle time-based operations properly
2. **[Physics](./06-physics.md)** - Master the physics system
3. **[Performance](./07-performance-memory.md)** - Write efficient code

### Advanced Developers

**Finally**, master these architectural patterns:

1. **[ScriptableObjects](./08-scriptable-objects.md)** - Build flexible, data-driven systems
2. **[Object Pooling](./09-object-pooling.md)** - Eliminate GC spikes
3. **[Addressables](./11-addressables.md)** - Stream assets and manage memory proactively
4. **[Scene Organization](./12-scene-loading.md)** - Structure additive scenes for seamless loads
5. **[Jobs & Burst](./13-jobs-burst.md)** - Parallelize CPU-heavy work safely
6. **[Async/Await](./14-async-await.md)** - Keep async workflows responsive on the main thread

## 🔥 Top 10 Most Common Mistakes

### 1. Using `is null` Instead of `== null`

```csharp
// ❌ WRONG - Doesn't work for Unity objects!
if (obj is null) return;

// ✓ CORRECT - Unity's operator override
if (obj == null) return;
```

**📖 Read**: [Null Checks](./02-null-checks.md#never-use-is-null-or-is-not-null-for-unity-objects)

### 2. GetComponent in Update

```csharp
// ❌ TERRIBLE - Called 60+ times per second!
void Update() { GetComponent<Rigidbody>().AddForce(...); }

// ✓ CORRECT - Cache in Awake
Rigidbody rb;
void Awake() { rb = GetComponent<Rigidbody>(); }
void Update() { rb.AddForce(...); }
```

**📖 Read**: [Component Access](./03-component-access.md#pitfall-1-getcomponent-in-update)

### 3. Physics in Update

```csharp
// ❌ WRONG - Inconsistent physics
void Update() { rb.AddForce(Vector3.forward); }

// ✓ CORRECT - Use FixedUpdate
void FixedUpdate() { rb.AddForce(Vector3.forward); }
```

**📖 Read**: [Physics](./06-physics.md#update-vs-fixedupdate)

### 4. Public Fields Everywhere

```csharp
// ❌ BAD - Breaks encapsulation
public int health = 100;

// ✓ GOOD - Proper encapsulation
[SerializeField] private int maxHealth = 100;
public int MaxHealth => maxHealth;
```

**📖 Read**: [Serialization](./04-serialization.md#serializefield-vs-public)

### 5. Not Storing Coroutine References

```csharp
// ❌ BAD - Can't stop it later
StartCoroutine(FlashRed());

// ✓ GOOD - Store reference
Coroutine flashCo = StartCoroutine(FlashRed());
if (flashCo != null) StopCoroutine(flashCo);
```

**📖 Read**: [Coroutines](./05-coroutines.md#1-always-store-the-coroutine-reference)

### 6. Accessing Other Objects in Awake

```csharp
// ❌ WRONG - Other object might not exist yet!
void Awake() { GameManager.Instance.Register(this); }

// ✓ CORRECT - Use Start for cross-object refs
void Start() { GameManager.Instance.Register(this); }
```

**📖 Read**: [Lifecycle Methods](./01-lifecycle-methods.md#awake-vs-start)

### 7. String Concatenation in Update

```csharp
// ❌ TERRIBLE - 60 allocations/sec!
void Update() { text = "Score: " + score; }

// ✓ CORRECT - Update only when changed
void OnScoreChanged() { text = $"Score: {score}"; }
```

**📖 Read**: [Performance](./07-performance-memory.md#1-string-concatenation)

### 8. Not Unsubscribing from Events

```csharp
// ❌ MEMORY LEAK!
void Start() { GameEvents.OnDeath += HandleDeath; }

// ✓ CORRECT - Unsubscribe in OnDisable
void OnEnable() { GameEvents.OnDeath += HandleDeath; }
void OnDisable() { GameEvents.OnDeath -= HandleDeath; }
```

**📖 Read**: [Lifecycle Methods](./01-lifecycle-methods.md#enabledisable-methods)

### 9. ScriptableObjects for Instance Data

```csharp
// ❌ WRONG - All enemies share same health!
[CreateAssetMenu]
public class EnemyState : ScriptableObject {
    public int currentHealth; // BAD!
}

// ✓ CORRECT - Instance data in MonoBehaviour
public class Enemy : MonoBehaviour {
    [SerializeField] private EnemyData data; // Shared config
    private int currentHealth; // Instance state
}
```

**📖 Read**: [ScriptableObjects](./08-scriptable-objects.md#when-not-to-use-scriptableobjects)

### 10. Not Disposing Object Pools

```csharp
// ❌ MEMORY LEAK!
private ObjectPool<Bullet> pool;
// Missing OnDestroy!

// ✓ CORRECT - Always dispose
void OnDestroy() { pool?.Dispose(); }
```

**📖 Read**: [Object Pooling](./09-object-pooling.md#4-always-clear-or-dispose-pools-in-ondestroy)

## 📖 Document Summaries

### [01. Lifecycle Methods](./01-lifecycle-methods.md) ⭐ **START HERE**

The absolute foundation of Unity development. Understanding when methods run is critical.

**You'll Learn:**

- Awake vs Start (and when to use each)
- Update vs FixedUpdate vs LateUpdate
- OnEnable/OnDisable for event subscriptions
- Why constructors don't work for MonoBehaviours
- Execution order between scripts

**Critical Concept**: All `Awake()` methods complete before any `Start()` method begins.

**Time to Read**: 15 minutes | **Impact**: ⭐⭐⭐⭐⭐

---

### [02. Null Checks](./02-null-checks.md) ⭐ **MUST READ**

Unity's null checking is different from C#. This catches 50% of beginner bugs.

**You'll Learn:**

- Why Unity overrides the `==` operator
- True null vs fake null vs missing references
- Why `is null` doesn't work for Unity objects
- When to check for null after delays/yields
- Performance implications

**Critical Concept**: Unity objects have two parts (C# wrapper + native C++ object), so `== null`
checks both!

**Time to Read**: 10 minutes | **Impact**: ⭐⭐⭐⭐⭐

---

### [03. Component Access](./03-component-access.md)

Learn to write performant code from day one by caching properly.

**You'll Learn:**

- GetComponent vs TryGetComponent
- Caching strategies for optimal performance
- List overloads to avoid garbage collection
- RequireComponent attribute
- Performance comparison table

**Critical Rule**: Cache in `Awake()`, never call `GetComponent()` in `Update()`.

**Time to Read**: 15 minutes | **Impact**: ⭐⭐⭐⭐⭐

---

### [04. Serialization](./04-serialization.md)

Keep your code clean and maintainable with proper encapsulation.

**You'll Learn:**

- `[SerializeField] private` vs `public` fields
- What Unity can/can't serialize
- Inspector organization with Headers and Tooltips
- Property vs field access patterns
- OnValidate for validation

**Critical Rule**: Use `[SerializeField] private` instead of `public` for Inspector-editable fields.

**Time to Read**: 12 minutes | **Impact**: ⭐⭐⭐⭐

---

### [05. Coroutines](./05-coroutines.md)

Master time-based operations and asynchronous workflows.

**You'll Learn:**

- When to use coroutines vs regular methods
- Storing and stopping coroutine references
- Preventing coroutine stacking
- Handling object destruction during coroutines
- 15 common pitfalls with solutions

**Critical Rule**: Always store `Coroutine` references, setting to `null` does NOT stop them!

**Time to Read**: 20 minutes | **Impact**: ⭐⭐⭐⭐

---

### [06. Physics](./06-physics.md)

Write stable, performant physics simulations.

**You'll Learn:**

- Update vs FixedUpdate (with timeline diagrams)
- Transform vs Rigidbody methods
- ForceMode options (Force, Acceleration, Impulse, VelocityChange)
- Variable timestep solutions
- Collision and trigger event matrix

**Critical Rule**: Use `FixedUpdate()` for ALL physics operations, `rb.MovePosition()` instead of
`transform.position`.

**Time to Read**: 18 minutes | **Impact**: ⭐⭐⭐⭐⭐

---

### [07. Performance & Memory](./07-performance-memory.md)

Write efficient code that doesn't cause frame stutters.

**You'll Learn:**

- Garbage collection basics
- String operations and StringBuilder
- Boxing allocations and how to avoid them
- LINQ allocations in hot paths
- NonAlloc variants of Physics methods

**Critical Rule**: Avoid allocations in `Update()`/`FixedUpdate()` - they cause GC stutters.

**Time to Read**: 20 minutes | **Impact**: ⭐⭐⭐⭐

---

### [08. ScriptableObjects](./08-scriptable-objects.md)

Build flexible, data-driven architectures.

**You'll Learn:**

- When to use ScriptableObjects (and when NOT to)
- Event systems and decoupling
- Runtime collections
- Configuration management
- Persistence pitfalls

**Critical Rule**: ScriptableObjects are for _shared data_, not _instance data_.

**Time to Read**: 25 minutes | **Impact**: ⭐⭐⭐⭐

---

### [09. Object Pooling](./09-object-pooling.md)

Eliminate garbage collection spikes with object reuse.

**You'll Learn:**

- When pooling helps (and when it doesn't)
- Synchronous release requirements
- Using Unity's ObjectPool API
- List overloads to avoid garbage
- Pool cleanup and disposal

**Critical Rule**: Always call `pool.Dispose()` in `OnDestroy()` - #1 memory leak cause!

**Time to Read**: 18 minutes | **Impact**: ⭐⭐⭐⭐

---

### [10. Event Systems](./10-event-systems.md) ⭐ **HIGHLY RECOMMENDED**

Comprehensive comparison of ScriptableObject events vs DxMessaging for decoupled communication.

**You'll Learn:**

- ScriptableObject event pattern (traditional approach)
- DxMessaging pattern (modern, zero-leak approach)
- Side-by-side code examples
- Performance comparison (allocations, GC pressure)
- Migration guide from ScriptableObject → DxMessaging
- Complete feature comparison table

**Critical Concept**: DxMessaging is superior for most projects due to automatic memory management,
zero allocations, and compile-time type safety.

**Time to Read**: 30 minutes | **Impact**: ⭐⭐⭐⭐⭐

## 🎓 Learning Paths

### Path 1: Beginner (2-3 hours)

**Goal**: Build solid fundamentals

1. [Lifecycle Methods](./01-lifecycle-methods.md) - 15 min
2. [Null Checks](./02-null-checks.md) - 10 min
3. [Component Access](./03-component-access.md) - 15 min
4. [Serialization](./04-serialization.md) - 12 min
5. [Coroutines](./05-coroutines.md) - 20 min (basics)
6. [Physics](./06-physics.md) - 18 min (basics)

**Practice Project**: Simple character controller with health system

---

### Path 2: Intermediate (4-5 hours)

**Goal**: Master common patterns

- Complete Beginner path
- Deep dive: [Coroutines](./05-coroutines.md) - All sections
- Deep dive: [Physics](./06-physics.md) - All sections
- Start: [Performance](./07-performance-memory.md) - String operations
- Start: [ScriptableObjects](./08-scriptable-objects.md) - Basic patterns

**Practice Project**: 2D platformer or top-down shooter

---

### Path 3: Advanced (8-10 hours)

**Goal**: Professional-grade code

- Complete all previous paths
- Master: [Performance](./07-performance-memory.md) - All optimizations
- Master: [ScriptableObjects](./08-scriptable-objects.md) - Event systems, runtime sets
- Master: [Object Pooling](./09-object-pooling.md) - Full implementation

**Practice Project**: Mobile game or VR experience with performance requirements

## 🔧 Common Workflows

### Setting Up a Character Controller

1. ✓ Add `[RequireComponent(typeof(Rigidbody))]` ([Serialization](./04-serialization.md))
2. ✓ Cache Rigidbody in `Awake()` ([Lifecycle](./01-lifecycle-methods.md),
   [Component Access](./03-component-access.md))
3. ✓ Read input in `Update()` ([Lifecycle](./01-lifecycle-methods.md))
4. ✓ Apply forces in `FixedUpdate()` ([Physics](./06-physics.md))
5. ✓ Use `MovePosition()` for kinematic movement ([Physics](./06-physics.md))
6. ✓ Null-check ground detection ([Null Checks](./02-null-checks.md))

### Creating a Reusable Enemy System

1. ✓ Create EnemyData ScriptableObject ([ScriptableObjects](./08-scriptable-objects.md))
2. ✓ Use `[SerializeField] private` for config ([Serialization](./04-serialization.md))
3. ✓ Cache components in `Awake()` ([Lifecycle](./01-lifecycle-methods.md),
   [Component Access](./03-component-access.md))
4. ✓ Use ObjectPool for spawning ([Object Pooling](./09-object-pooling.md))
5. ✓ Store coroutine references ([Coroutines](./05-coroutines.md))
6. ✓ Check null after yields ([Null Checks](./02-null-checks.md))
7. ✓ Unsubscribe events in `OnDisable()` ([Lifecycle](./01-lifecycle-methods.md))

### Optimizing Performance

1. ✓ Profile first with Unity Profiler ([Performance](./07-performance-memory.md))
2. ✓ Cache all `GetComponent()` calls ([Component Access](./03-component-access.md))
3. ✓ Use object pooling for frequently spawned objects ([Object Pooling](./09-object-pooling.md))
4. ✓ Avoid string concatenation in loops ([Performance](./07-performance-memory.md))
5. ✓ Use NonAlloc Physics methods ([Performance](./07-performance-memory.md))
6. ✓ Update UI only when values change ([Performance](./07-performance-memory.md))

## 🚫 Anti-Patterns Quick Reference

| ❌ Anti-Pattern                          | ✓ Correct Pattern                         | Document                                     |
| ---------------------------------------- | ----------------------------------------- | -------------------------------------------- |
| `public int health;`                     | `[SerializeField] private int maxHealth;` | [Serialization](./04-serialization.md)       |
| `if (obj is null)`                       | `if (obj == null)`                        | [Null Checks](./02-null-checks.md)           |
| `void Update() { GetComponent<>()... }`  | Cache in `Awake()`                        | [Component Access](./03-component-access.md) |
| `void Update() { rb.AddForce()... }`     | `void FixedUpdate()`                      | [Physics](./06-physics.md)                   |
| `void Awake() { FindOtherObject()... }`  | `void Start()`                            | [Lifecycle](./01-lifecycle-methods.md)       |
| `StartCoroutine(Flash());`               | `flashCo = StartCoroutine(Flash());`      | [Coroutines](./05-coroutines.md)             |
| `void Update() { text = "Score:" + s; }` | Update only when changed                  | [Performance](./07-performance-memory.md)    |
| `transform.position = newPos;` (with RB) | `rb.MovePosition(newPos);`                | [Physics](./06-physics.md)                   |

## 💡 Philosophy

These best practices are designed to be:

- **Beginner-friendly**: Clear explanations with simple analogies
- **Practical**: Real code examples you can use immediately
- **Comprehensive**: Covers the "why" not just the "what"
- **Progressive**: Ordered from foundation to advanced topics
- **Opinionated**: Clear guidance on what to do and what to avoid

**Remember**: These are guidelines, not laws. Understand the principles, then adapt to your
project's needs!

## 🤝 Contributing

Found an error or have a suggestion? This is a living document that should evolve with Unity's best
practices.

## 📄 License

These best practices are collected from Unity documentation, community knowledge, and real-world
experience. Use freely for learning and development!

---

**Happy Unity development! 🎮**

**Pro tip**: Bookmark this page and revisit sections as you encounter related problems in your
projects!
