# Unity Best Practices

A comprehensive, beginner-friendly guide to Unity best practices. This collection covers common
patterns, pitfalls, and solutions that every Unity developer should know.

## 📚 Table of Contents

1. [**Coroutines**](./01-coroutines.md) - Time-based operations and async workflows
2. [**Object Pooling**](./02-object-pooling.md) - Performance optimization for frequent spawning
3. [**Null Checks**](./03-null-checks.md) - Unity's "fake null" and safe comparison patterns
4. [**Component Access**](./04-component-access.md) - Efficient component lookup and caching
5. [**Physics**](./05-physics.md) - Proper physics update loops and force application
6. [**ScriptableObjects**](./06-scriptable-objects.md) - Data-driven design and shared configuration

## 🎯 Quick Start

**New to Unity?** Start here:

1. Read [Null Checks](./03-null-checks.md) first - This catches 50% of beginner bugs!
2. Then [Component Access](./04-component-access.md) - Learn to cache properly from the start
3. Finally [Physics](./05-physics.md) - Understand Update vs FixedUpdate

**Have some experience?** Jump to:

- [Coroutines](./01-coroutines.md) - Master async workflows
- [Object Pooling](./02-object-pooling.md) - Optimize your game
- [ScriptableObjects](./06-scriptable-objects.md) - Level up your architecture

## 🔥 Most Common Mistakes

### Mistake #1: Using `== null` Wrong

```csharp
// ❌ WRONG - Pattern matching bypasses Unity's null check
if (obj is null) return;

// ✓ CORRECT - Use Unity's operator
if (obj == null) return;
```

**Read more**: [Null Checks](./03-null-checks.md)

### Mistake #2: GetComponent in Update

```csharp
// ❌ TERRIBLE - Called 60+ times per second!
private void Update()
{
    GetComponent<Rigidbody>().AddForce(Vector3.up);
}

// ✓ CORRECT - Cache in Awake
private Rigidbody rb;
private void Awake() { rb = GetComponent<Rigidbody>(); }
private void Update() { rb.AddForce(Vector3.up); }
```

**Read more**: [Component Access](./04-component-access.md)

### Mistake #3: Physics in Update

```csharp
// ❌ WRONG - Variable timestep causes inconsistent physics
private void Update()
{
    rb.AddForce(Vector3.forward * 10f);
}

// ✓ CORRECT - Use FixedUpdate for physics
private void FixedUpdate()
{
    rb.AddForce(Vector3.forward * 10f);
}
```

**Read more**: [Physics](./05-physics.md)

### Mistake #4: Not Storing Coroutine References

```csharp
// ❌ BAD - No way to stop it later
StartCoroutine(FlashRed());

// ✓ GOOD - Store reference for control
Coroutine flashCoroutine = StartCoroutine(FlashRed());
```

**Read more**: [Coroutines](./01-coroutines.md)

### Mistake #5: Not Disposing Object Pools

```csharp
// ❌ BAD - Memory leak! Pooled objects never destroyed
public class BulletPool : MonoBehaviour
{
    private ObjectPool<Bullet> pool;
    // Missing OnDestroy!
}

// ✓ GOOD - Always clean up pools
private void OnDestroy()
{
    pool?.Dispose();
}
```

**Read more**: [Object Pooling](./02-object-pooling.md)

## 📖 Document Overview

### [01. Coroutines](./01-coroutines.md)

Learn how to properly manage time-based operations and asynchronous workflows.

**Key Topics:**

- When to use coroutines vs regular methods
- Storing and stopping coroutine references
- Preventing coroutine stacking
- Handling object destruction during coroutines
- Common pitfalls and solutions

**Critical Rules:**

1. Always store `Coroutine` references
2. Setting to null does NOT stop coroutines
3. Can't stop by calling the method again

### [02. Object Pooling](./02-object-pooling.md)

Master performance optimization through object reuse instead of instantiate/destroy.

**Key Topics:**

- When pooling helps (and when it doesn't)
- Synchronous release requirements
- Using Unity's ObjectPool API
- List overloads to avoid garbage
- Pool cleanup and disposal

**Critical Rules:**

1. Objects must be ready-to-use when retrieved
2. Release functions must be synchronous
3. Always call `Dispose()` in OnDestroy

### [03. Null Checks](./03-null-checks.md)

Understand Unity's "fake null" system and avoid the #1 source of NullReferenceExceptions.

**Key Topics:**

- Why Unity overrides `==` operator
- True null vs fake null vs missing references
- Pattern matching pitfalls (`is null`)
- When to check for null
- Performance considerations

**Critical Rules:**

1. Always use `== null` for Unity objects
2. Never use `is null` for Unity objects
3. Check after every delay/yield
4. `ReferenceEquals` doesn't work correctly

### [04. Component Access](./04-component-access.md)

Learn efficient component lookup patterns and caching strategies.

**Key Topics:**

- GetComponent vs TryGetComponent
- Caching strategies for performance
- List overloads to avoid allocations
- GetComponentInChildren performance
- RequireComponent attribute

**Critical Rules:**

1. Cache everything in Awake/Start
2. Never call GetComponent in Update
3. Use TryGetComponent when unsure
4. Use List overloads to avoid garbage

### [05. Physics](./05-physics.md)

Master Unity's physics system for stable, performant, and realistic simulations.

**Key Topics:**

- Update vs FixedUpdate
- Transform vs Rigidbody methods
- ForceMode options explained
- Variable timestep solutions
- Collision and trigger events

**Critical Rules:**

1. Use FixedUpdate for all physics
2. Use Rigidbody methods, not Transform
3. Cache Rigidbody references
4. Use correct ForceMode

### [06. ScriptableObjects](./06-scriptable-objects.md)

Create data-driven, maintainable architectures with Unity's data container system.

**Key Topics:**

- When to use ScriptableObjects
- Event systems and decoupling
- Runtime collections
- Configuration management
- Persistence pitfalls

**Critical Rules:**

1. ScriptableObjects are for shared data, not instance data
2. Reset runtime values in OnEnable
3. Never store scene references
4. Use PlayerPrefs for actual save data

## 🎓 Learning Path

### Beginner (Essential Foundation)

Start here if you're new to Unity:

1. **[Null Checks](./03-null-checks.md)** - Avoid the most common Unity bug
2. **[Component Access](./04-component-access.md)** - Learn proper caching early
3. **[Physics](./05-physics.md)** - Understand the update loop

### Intermediate (Common Patterns)

Once you're comfortable with basics:

1. **[Coroutines](./01-coroutines.md)** - Handle time-based operations
2. **[ScriptableObjects](./06-scriptable-objects.md)** - Improve your architecture

### Advanced (Performance)

When optimizing your game:

1. **[Object Pooling](./02-object-pooling.md)** - Eliminate garbage collection spikes

## 🔧 Common Workflows

### Setting Up a New Character Controller

1. ✓ Add Rigidbody component
2. ✓ Use `[RequireComponent(typeof(Rigidbody))]`
3. ✓ Cache Rigidbody in Awake ([Component Access](./04-component-access.md))
4. ✓ Read input in Update
5. ✓ Apply forces in FixedUpdate ([Physics](./05-physics.md))
6. ✓ Use MovePosition for kinematic movement

### Creating a Reusable Enemy System

1. ✓ Create EnemyData ScriptableObject ([ScriptableObjects](./06-scriptable-objects.md))
2. ✓ Cache components in Awake ([Component Access](./04-component-access.md))
3. ✓ Use ObjectPool for spawning ([Object Pooling](./02-object-pooling.md))
4. ✓ Store coroutine references for effects ([Coroutines](./01-coroutines.md))
5. ✓ Check null after yields ([Null Checks](./03-null-checks.md))

### Implementing a Damage Flash Effect

1. ✓ Create coroutine for flash ([Coroutines](./01-coroutines.md))
2. ✓ Store coroutine reference
3. ✓ Check and stop existing coroutine before starting new one
4. ✓ Clean up reference when done
5. ✓ Stop coroutine in OnDisable

## 🚫 Anti-Patterns to Avoid

### Performance Killers

- ❌ GetComponent in Update/FixedUpdate
- ❌ GetComponentInChildren in performance-critical code
- ❌ FindObjectOfType every frame
- ❌ Using string-based Find methods
- ❌ Not using object pools for frequent spawning
- ❌ Instantiate/Destroy in tight loops

### Common Bugs

- ❌ Using `is null` for Unity objects
- ❌ Forgetting to cache Rigidbody references
- ❌ Physics in Update instead of FixedUpdate
- ❌ Transform.position on objects with Rigidbody
- ❌ Not stopping coroutines before starting new ones
- ❌ Using ForceMode.Impulse in FixedUpdate

### Architecture Issues

- ❌ ScriptableObjects for instance data
- ❌ Scene references in ScriptableObjects
- ❌ Not disposing object pools
- ❌ Not unregistering event listeners
- ❌ Circular references between ScriptableObjects

## 🎯 Quick Reference Cheat Sheet

### Null Checks

```csharp
// ✓ DO
if (obj == null) return;
obj?.DoSomething();

// ❌ DON'T
if (obj is null) return;
if (ReferenceEquals(obj, null)) return;
```

### Component Access

```csharp
// ✓ DO
private Rigidbody rb;
void Awake() { rb = GetComponent<Rigidbody>(); }

if (TryGetComponent<Health>(out var health))
    health.TakeDamage(10);

// ❌ DON'T
void Update() { GetComponent<Rigidbody>().AddForce(...); }
```

### Physics

```csharp
// ✓ DO
void FixedUpdate() { rb.AddForce(Vector3.up, ForceMode.Force); }
void OnJump() { rb.AddForce(Vector3.up * 5, ForceMode.Impulse); }

// ❌ DON'T
void Update() { rb.AddForce(Vector3.up); }
void Update() { transform.position += Vector3.up; }
```

### Coroutines

```csharp
// ✓ DO
Coroutine myCoroutine = StartCoroutine(MyCoroutine());
if (myCoroutine != null) StopCoroutine(myCoroutine);

// ❌ DON'T
StartCoroutine(MyCoroutine());
myCoroutine = null; // Doesn't stop it!
```

### Object Pooling

```csharp
// ✓ DO
void OnDestroy() { pool?.Dispose(); }
void ReturnToPool() { ResetState(); pool.Release(this); }

// ❌ DON'T
IEnumerator DelayedReturn() { yield return wait; pool.Release(this); }
```

## 🤝 Contributing

Found an error or have a suggestion? This is a living document that should evolve with Unity's best
practices.

## 📄 License

These best practices are collected from Unity documentation, community knowledge, and real-world
experience. Use freely for learning and development!

---

## 💡 Philosophy

These best practices are designed to be:

- **Beginner-friendly**: Clear explanations and simple analogies
- **Practical**: Real code examples you can use immediately
- **Comprehensive**: Covers the "why" not just the "what"
- **Opinionated**: Clear guidance on what to do and what to avoid

**Remember**: These are guidelines, not laws. Understand the principles, then adapt to your
project's needs!

---

**Happy Unity development! 🎮**
