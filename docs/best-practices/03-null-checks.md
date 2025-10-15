# Unity Null Checks Best Practices

## ⚠️ Unity's Fake Null - The Hidden Trap!

**The most important thing to understand**: Unity overrides the `==` operator for
`UnityEngine.Object`, which means `== null` doesn't work the same way as regular C# null checks!

```csharp
GameObject obj = /* destroyed object */;

// These are DIFFERENT in Unity!
if (obj == null)        // ✓ Unity's fake null check (SAFE)
if (obj is null)        // ❌ C# native check (UNSAFE for Unity objects!)
if (ReferenceEquals(obj, null))  // ❌ Native check (UNSAFE!)
```

## Table of Contents

- [The Unity Null Problem](#the-unity-null-problem)
- [When to Use Each Null Check](#when-to-use-each-null-check)
- [Best Practices](#best-practices)
- [Common Pitfalls](#common-pitfalls)
- [Performance Considerations](#performance-considerations)

## The Unity Null Problem

### Why Unity Has "Fake Null"

Unity has a custom null check because:

1. **Unity objects exist in two places**: C# wrapper + native C++ engine
2. **Destroyed objects** aren't immediately collected by C# garbage collector
3. **Scene transitions** can leave "dangling" C# references
4. **Missing references** (like unassigned Inspector fields) need special handling

```mermaid
graph LR
    A[C# GameObject Reference] -->|Points to| B[C# Wrapper]
    B -->|Points to| C[Native C++ Object]
    C -->|Destroyed| D[null]
    B -.->|Still exists!| B
    A -.->|Still points to| B

    style D fill:#f66
    style B fill:#ff6
```

When you destroy a Unity object, the native C++ object is destroyed, but the C# wrapper still
exists! Unity's `==` operator checks **both** the wrapper and the native object.

### The Three Types of Null

```csharp
// 1. TRUE NULL - Nothing assigned
GameObject obj1 = null;

// 2. FAKE NULL - Destroyed Unity object
GameObject obj2 = new GameObject();
Destroy(obj2);
// obj2 is now "fake null" - C# wrapper exists, native object doesn't

// 3. MISSING REFERENCE - Unassigned in Inspector
[SerializeField] private GameObject obj3;
// If not assigned in Inspector, obj3 is "fake null"
```

## When to Use Each Null Check

### Use `== null` or `!= null` (Unity's Overloaded Operator)

**Always use this for Unity objects!** This is the **ONLY** safe way.

```csharp
// ✓ CORRECT for Unity objects
if (gameObject == null)
    return;

if (myComponent != null)
    myComponent.DoSomething();

// ✓ CORRECT - null-coalescing
Transform target = primaryTarget != null ? primaryTarget : secondaryTarget;

// ✓ CORRECT - null-conditional
rigidbody?.AddForce(Vector3.up);
```

**Use for**: `GameObject`, `Component`, `Transform`, `MonoBehaviour`, `ScriptableObject`,
`Material`, `Texture`, and any other `UnityEngine.Object` derived type.

### Never Use `is null` or `is not null` for Unity Objects

**Pattern matching null checks bypass Unity's operator overload!**

```csharp
GameObject destroyedObj = new GameObject();
Destroy(destroyedObj);

// DANGEROUS - Pattern matching
if (destroyedObj is null)        // ❌ FALSE! (C# wrapper still exists)
if (destroyedObj is not null)    // ❌ TRUE! (But object is destroyed!)

// SAFE - Unity's operator
if (destroyedObj == null)        // ✓ TRUE! (Unity knows it's destroyed)
if (destroyedObj != null)        // ✓ FALSE! (Unity knows it's destroyed)
```

### Never Use `ReferenceEquals` for Unity Objects

```csharp
GameObject obj = someDestroyedObject;

// ❌ UNSAFE - Checks only C# reference
if (ReferenceEquals(obj, null))
    Debug.Log("This might not print even if the object is destroyed!");

// ✓ SAFE - Unity's check
if (obj == null)
    Debug.Log("This correctly detects destroyed objects");
```

### Use Regular C# Checks for Non-Unity Objects

For pure C# objects (not derived from `UnityEngine.Object`), use modern C# patterns:

```csharp
// Pure C# classes
MyDataClass data = GetData();

// ✓ Use modern C# patterns
if (data is null) return;
if (data is not null) DoSomething();

// ✓ Pattern matching
if (data is { IsValid: true })
    ProcessData(data);

// ✓ Null-coalescing assignment
data ??= new MyDataClass();
```

## Best Practices

### 1. Explicit Unity Null Checks

```csharp
// ✓ GOOD - Clear and explicit
if (enemy != null)
{
    enemy.TakeDamage(10);
}

// ✓ GOOD - Guard clause
if (enemy == null)
    return;

enemy.TakeDamage(10);

// ✓ GOOD - Null-conditional operator
enemy?.TakeDamage(10);
```

### 2. Check Before Every Use After Delays

```csharp
// ✓ GOOD - Check after coroutine yield
private IEnumerator AttackSequence(Enemy enemy)
{
    if (enemy == null) yield break;

    enemy.TakeDamage(10);
    yield return new WaitForSeconds(1f);

    // ⚠️ Enemy might be destroyed during wait!
    if (enemy == null) yield break;  // Check again!

    enemy.TakeDamage(10);
}

// ✓ GOOD - Check after async operation
private async Task ProcessTarget(GameObject target)
{
    if (target == null) return;

    await Task.Delay(1000);

    // ⚠️ Target might be destroyed during delay!
    if (target == null) return;  // Check again!

    target.transform.position = Vector3.zero;
}
```

### 3. Use Null-Conditional Operators

```csharp
// ✓ GOOD - Null-conditional operator
rigidbody?.AddForce(Vector3.up);

// ✓ GOOD - Chain null-conditional
enemy?.GetComponent<Health>()?.TakeDamage(10);

// ✓ GOOD - Null-coalescing
Transform target = primaryTarget ?? secondaryTarget ?? transform;

// Equivalent verbose version:
Transform target;
if (primaryTarget != null)
    target = primaryTarget;
else if (secondaryTarget != null)
    target = secondaryTarget;
else
    target = transform;
```

### 4. Check Components After GetComponent

```csharp
// ✓ GOOD - Always check GetComponent results
Rigidbody rb = GetComponent<Rigidbody>();
if (rb != null)
{
    rb.AddForce(Vector3.up * 10);
}

// ✓ BETTER - Use TryGetComponent
if (TryGetComponent<Rigidbody>(out var rb))
{
    rb.AddForce(Vector3.up * 10);
}

// ✓ GOOD - Null-conditional (no error if missing)
GetComponent<Rigidbody>()?.AddForce(Vector3.up * 10);
```

### 5. Validate Inspector References in Awake/Start

```csharp
[SerializeField] private Transform target;
[SerializeField] private AudioSource audioSource;

private void Awake()
{
    // ✓ GOOD - Validate required references
    if (target == null)
    {
        Debug.LogError($"Target not assigned on {gameObject.name}!", this);
    }

    if (audioSource == null)
    {
        Debug.LogError($"AudioSource not assigned on {gameObject.name}!", this);
    }
}

// ✓ BETTER - Use RequireComponent for components
[RequireComponent(typeof(Rigidbody))]
public class PhysicsObject : MonoBehaviour
{
    private Rigidbody rb;

    private void Awake()
    {
        // Guaranteed to exist thanks to RequireComponent
        rb = GetComponent<Rigidbody>();
    }
}
```

### 6. Use Assertions in Development

```csharp
using UnityEngine.Assertions;

private void Start()
{
    // ✓ GOOD - Assertions for development
    Assert.IsNotNull(target, "Target must be assigned!");
    Assert.IsNotNull(audioSource, "AudioSource must be assigned!");

    // These only run in development builds
    // Stripped from release builds
}
```

## Common Pitfalls

### Pitfall 1: Using `is null` Pattern Matching

```csharp
GameObject obj = someDestroyedObject;

// ❌ WRONG - Pattern matching bypasses Unity's null check
if (obj is null)
    return;

if (obj is not null)
    obj.SetActive(true);

// ✓ CORRECT - Use Unity's operator
if (obj == null)
    return;

if (obj != null)
    obj.SetActive(true);
```

### Pitfall 2: Not Checking After Delays

```csharp
// ❌ BAD - No check after delay
private IEnumerator DamageOverTime(Enemy enemy)
{
    for (int i = 0; i < 5; i++)
    {
        enemy.TakeDamage(10);  // ☠️ Might be null after first iteration!
        yield return new WaitForSeconds(1f);
    }
}

// ✓ GOOD - Check every iteration
private IEnumerator DamageOverTime(Enemy enemy)
{
    for (int i = 0; i < 5; i++)
    {
        if (enemy == null)  // ✓ Check before use
            yield break;

        enemy.TakeDamage(10);
        yield return new WaitForSeconds(1f);
    }
}
```

### Pitfall 3: Caching Without Null Checks

```csharp
// ❌ BAD - Cached reference might become invalid
public class CachedReference : MonoBehaviour
{
    private Transform target;

    private void Start()
    {
        target = GameObject.FindGameObjectWithTag("Player").transform;
    }

    private void Update()
    {
        // ☠️ Player might have been destroyed!
        transform.LookAt(target);
    }
}

// ✓ GOOD - Validate cached references
public class SafeCachedReference : MonoBehaviour
{
    private Transform target;

    private void Start()
    {
        GameObject player = GameObject.FindGameObjectWithTag("Player");
        if (player != null)
            target = player.transform;
    }

    private void Update()
    {
        // ✓ Check before use
        if (target != null)
            transform.LookAt(target);
    }
}

// ✓ BETTER - Re-find if missing
public class ResilientReference : MonoBehaviour
{
    private Transform target;

    private void Update()
    {
        // ✓ Auto-recover if target is destroyed and recreated
        if (target == null)
        {
            GameObject player = GameObject.FindGameObjectWithTag("Player");
            if (player != null)
                target = player.transform;
        }

        if (target != null)
            transform.LookAt(target);
    }
}
```

### Pitfall 4: Comparing Unity Objects with ReferenceEquals

```csharp
GameObject a = GetGameObject();
GameObject b = GetGameObject();

// ❌ WRONG - ReferenceEquals doesn't use Unity's override
if (ReferenceEquals(a, b))
    Debug.Log("Same");

// ❌ WRONG - Doesn't detect destroyed objects
if (!ReferenceEquals(a, null))
    a.SetActive(true);

// ✓ CORRECT - Use Unity's operator
if (a == b)
    Debug.Log("Same");

// ✓ CORRECT - Detects destroyed objects
if (a != null)
    a.SetActive(true);
```

### Pitfall 5: Not Checking FindObjectOfType Results

```csharp
// ❌ BAD - Doesn't check if found
private void Start()
{
    GameManager manager = FindObjectOfType<GameManager>();
    manager.RegisterPlayer(this);  // ☠️ NullReferenceException if not found!
}

// ✓ GOOD - Always check Find results
private void Start()
{
    GameManager manager = FindObjectOfType<GameManager>();
    if (manager != null)
    {
        manager.RegisterPlayer(this);
    }
    else
    {
        Debug.LogError("GameManager not found in scene!");
    }
}

// ✓ BETTER - Use null-conditional
private void Start()
{
    FindObjectOfType<GameManager>()?.RegisterPlayer(this);
}
```

### Pitfall 6: Accessing Components on Destroyed GameObjects

```csharp
// ❌ BAD - GameObject might be destroyed
public class BadComponentAccess : MonoBehaviour
{
    private Enemy enemy;

    private void Update()
    {
        if (enemy != null)
        {
            // ☠️ Even if enemy isn't null, its components might be!
            enemy.GetComponent<Health>().TakeDamage(1);
        }
    }
}

// ✓ GOOD - Check the component too
public class SafeComponentAccess : MonoBehaviour
{
    private Enemy enemy;

    private void Update()
    {
        if (enemy != null)
        {
            Health health = enemy.GetComponent<Health>();
            if (health != null)
            {
                health.TakeDamage(1);
            }
        }
    }
}

// ✓ BETTER - Use null-conditional chaining
public class BetterComponentAccess : MonoBehaviour
{
    private Enemy enemy;

    private void Update()
    {
        enemy?.GetComponent<Health>()?.TakeDamage(1);
    }
}
```

## Performance Considerations

### Unity's Null Check Has Overhead

Unity's `==` operator is **slower** than native C# null checks because it:

1. Calls into native C++ code
2. Checks both the C# wrapper and native object
3. Handles special cases (destroyed objects, missing references)

```csharp
// Slower (but NECESSARY for Unity objects)
if (transform != null)  // ~10-20x slower than native check
    DoSomething();

// Faster (but ONLY safe for pure C# objects)
if (myDataClass != null)  // Native C# speed
    DoSomething();
```

### Cache References When Possible

```csharp
// ❌ BAD - Repeated GetComponent calls
private void Update()
{
    if (GetComponent<Rigidbody>() != null)
        GetComponent<Rigidbody>().AddForce(Vector3.up);
}

// ✓ GOOD - Cache component references
private Rigidbody rb;

private void Awake()
{
    rb = GetComponent<Rigidbody>();
}

private void Update()
{
    if (rb != null)
        rb.AddForce(Vector3.up);
}
```

### Avoid Null Checks in Hot Paths

```csharp
// ❌ BAD - Unnecessary null check every frame
private Transform target;  // Assigned in Awake, never null

private void Update()
{
    if (target != null)  // Wasteful check
        transform.LookAt(target);
}

// ✓ GOOD - Only check when necessary
private Transform target;

private void Awake()
{
    target = GameObject.FindGameObjectWithTag("Player").transform;

    if (target == null)
    {
        Debug.LogError("Player not found!");
        enabled = false;  // Disable this component
    }
}

private void Update()
{
    // No null check needed - validated in Awake
    transform.LookAt(target);
}
```

### Use TryGetComponent to Avoid Double Lookups

```csharp
// ❌ LESS EFFICIENT - GetComponent called twice
Rigidbody rb = GetComponent<Rigidbody>();
if (rb != null)
    rb.AddForce(Vector3.up);

// ✓ MORE EFFICIENT - Single lookup + null check
if (TryGetComponent<Rigidbody>(out var rb))
    rb.AddForce(Vector3.up);
```

## Quick Reference

### Safe Null Checks for Unity Objects

```csharp
// ✓ Use these:
if (obj == null) return;
if (obj != null) DoSomething();
obj?.DoSomething();
Transform t = obj1 ?? obj2 ?? obj3;
```

### Unsafe Null Checks for Unity Objects

```csharp
// ❌ DON'T use these:
if (obj is null) return;           // Pattern matching
if (obj is not null) DoSomething(); // Pattern matching
if (ReferenceEquals(obj, null))    // Reference check
```

### Safe for Pure C# Objects

```csharp
// ✓ Use modern C# for non-Unity objects:
if (data is null) return;
if (data is not null) DoSomething();
if (data is { IsValid: true }) Process();
data ??= new MyClass();
```

## Summary

**Golden Rules for Unity Null Checks:**

1. **Always use `== null` or `!= null`** for Unity objects
2. **Never use `is null` or `is not null`** for Unity objects
3. **Never use `ReferenceEquals`** for Unity objects
4. **Always check after delays** (coroutines, async, animations)
5. **Validate Inspector references** in Awake/Start
6. **Use TryGetComponent** for efficiency
7. **Cache component references** in Awake/Start
8. **Use null-conditional operators** (`?.`) for cleaner code

**Remember**: Unity's null checking is weird, but it exists for good reason. Embrace it and use
`== null` everywhere for Unity objects!
