# Unity Null Checks Best Practices

## The Problem

Unity overrides the `==` operator for `UnityEngine.Object` to check if the native C++ object still
exists. When you destroy a Unity object, the C# wrapper remains but the native object is gone -
creating a "fake null" state.

**The danger:** C#'s `is null`, `?.`, `??`, and `ReferenceEquals()` bypass Unity's override and only
check the C# wrapper, leading to false negatives on destroyed objects.

```csharp
GameObject obj = /* destroyed object */;

// These are DIFFERENT in Unity!
if (obj == null)        // ✓ Unity's null check - detects destroyed objects (SAFE)
if (obj is null)        // ❌ C# null check - doesn't detect destroyed objects (UNSAFE)
obj?.DoSomething();     // ❌ Null-conditional - bypasses Unity (UNSAFE)
obj = obj ?? fallback;  // ❌ Null-coalescing - bypasses Unity (UNSAFE)
```

**Real-world impact:** You check `if (enemy != null)` and it passes, but `enemy.transform` throws
NullReferenceException because the GameObject was destroyed.

## Table of Contents

- [When to Use Each Check](#when-to-use-each-check)
- [Best Practices](#best-practices)
- [Common Pitfalls](#common-pitfalls)
- [Performance Considerations](#performance-considerations)

## Why Unity Has "Fake Null"

Unity objects exist in two places: a C# wrapper and a native C++ object. When destroyed, the native
object is removed but the C# wrapper remains. Unity's `==` operator checks both sides; C#'s native
operators only check the wrapper.

```csharp
// Three scenarios that appear "null" in Unity:

// 1. TRUE NULL - Nothing assigned
GameObject obj1 = null;

// 2. FAKE NULL - Destroyed object (wrapper exists, native doesn't)
GameObject obj2 = new GameObject();
Destroy(obj2);

// 3. MISSING REFERENCE - Unassigned Inspector field
[SerializeField] private GameObject obj3;
```

## When to Use Each Check

### Never use `is null` or `is not null` for Unity objects

**Use for:** `GameObject`, `Component`, `Transform`, `MonoBehaviour`, `ScriptableObject`,
`Material`, `Texture`, and any `UnityEngine.Object` derived type.

```csharp
// ✓ SAFE - Unity's overloaded operator
if (gameObject == null) return;
if (myComponent != null) myComponent.DoSomething();
Transform target = primary != null ? primary : secondary;

// ❌ UNSAFE - These bypass Unity's null check
if (obj is null) return;              // Pattern matching
if (!ReferenceEquals(obj, null)) {}   // Reference check
rigidbody?.AddForce(Vector3.up);      // Null-conditional
Transform t = obj1 ?? obj2;           // Null-coalescing
```

### For Pure C# Objects: Use Modern Patterns

For objects **not** derived from `UnityEngine.Object`:

```csharp
MyDataClass data = GetData();

// ✓ Modern C# patterns are safe here
if (data is null) return;
if (data is { IsValid: true }) ProcessData(data);
data ??= new MyDataClass();
value = data?.GetValue() ?? defaultValue;
```

## Best Practices

### 1. Always Check After Delays

```csharp
// ✓ Check after every yield or async operation
private IEnumerator AttackSequence(Enemy enemy)
{
    if (enemy == null) yield break;
    enemy.TakeDamage(10);

    yield return new WaitForSeconds(1f);
    if (enemy == null) yield break;  // Might be destroyed during wait

    enemy.TakeDamage(10);
}
```

### 2. Use TryGetComponent

```csharp
// ✓ Single lookup + built-in null check
if (TryGetComponent<Rigidbody>(out var rb))
    rb.AddForce(Vector3.up * 10);

// Also valid but less efficient
Rigidbody rb = GetComponent<Rigidbody>();
if (rb != null)
    rb.AddForce(Vector3.up * 10);
```

### 3. Validate Inspector References Early

```csharp
[SerializeField] private Transform target;

private void Awake()
{
    // ✓ Validate in Awake/Start
    if (target == null)
        Debug.LogError($"Target not assigned on {gameObject.name}!", this);

    // Or use assertions (stripped in release builds)
    Assert.IsNotNull(target, "Target must be assigned!");
}

// ✓ Use RequireComponent to enforce dependencies
[RequireComponent(typeof(Rigidbody))]
public class PhysicsObject : MonoBehaviour
{
    private Rigidbody rb;

    private void Awake()
    {
        rb = GetComponent<Rigidbody>(); // Guaranteed by RequireComponent
    }
}
```

```csharp
// ❌ Repeated GetComponent calls
private void Update()
{
    if (GetComponent<Rigidbody>() != null)
        GetComponent<Rigidbody>().AddForce(Vector3.up);
}

// ✓ Cache in Awake/Start
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

## Common Pitfalls

### Pitfall 1: Not Checking After Delays

```csharp
// ❌ Object might be destroyed during delay
private IEnumerator DamageOverTime(Enemy enemy)
{
    for (int i = 0; i < 5; i++)
    {
        enemy.TakeDamage(10);
        yield return new WaitForSeconds(1f);
    }
}

// ✓ Check before each use
private IEnumerator DamageOverTime(Enemy enemy)
{
    for (int i = 0; i < 5; i++)
    {
        if (enemy == null) yield break;
        enemy.TakeDamage(10);
        yield return new WaitForSeconds(1f);
    }
}
```

### Pitfall 2: Not Validating Find Results

```csharp
// ❌ Doesn't check if found
GameManager manager = FindObjectOfType<GameManager>();
manager.RegisterPlayer(this);  // Crash if not found!

// ✓ Always check Find results
GameManager manager = FindObjectOfType<GameManager>();
if (manager != null)
    manager.RegisterPlayer(this);
else
    Debug.LogError("GameManager not found!");
```

### Pitfall 3: Not Checking Component Results

```csharp
// ❌ GetComponent can return null
if (enemy != null)
{
    enemy.GetComponent<Health>().TakeDamage(1);  // Crash if no Health component
}

// ✓ Check component result
if (enemy != null)
{
    Health health = enemy.GetComponent<Health>();
    if (health != null)
        health.TakeDamage(1);
}

// ✓ Better: Cache components
private Enemy enemy;
private Health enemyHealth;

private void SetEnemy(Enemy newEnemy)
{
    enemy = newEnemy;
    enemyHealth = enemy != null ? enemy.GetComponent<Health>() : null;
}
```

## Performance Considerations

Unity's `== null` is **~10-20x slower** than native C# null checks because it calls into C++ to
check the native object state. However, it's necessary for correctness with Unity objects.

**Optimization tips:**

```csharp
// ✓ Cache component references (avoids repeated GetComponent calls)
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

// ✓ Avoid unnecessary checks in hot paths
private Transform target;  // Validated in Awake, never destroyed in your game

private void Update()
{
    // Skip null check if you know it's safe
    transform.LookAt(target);
}

// ✓ Use TryGetComponent for single lookup
if (TryGetComponent<Rigidbody>(out var rb))
    rb.AddForce(Vector3.up);
```

## Quick Reference

**For Unity objects** (`GameObject`, `Component`, `MonoBehaviour`, etc.):

```csharp
// ✓ SAFE
if (obj == null) return;
if (obj != null) DoSomething();
Transform t = obj1 != null ? obj1 : obj2;

// ❌ UNSAFE - All bypass Unity's null check
if (obj is null) {}                // Pattern matching
if (ReferenceEquals(obj, null)) {} // Reference equality
obj?.DoSomething();                // Null-conditional
Transform t = obj1 ?? obj2;        // Null-coalescing
```

**For pure C# objects** (not derived from `UnityEngine.Object`):

```csharp
// ✓ Modern C# patterns are safe
if (data is null) return;
data ??= new MyClass();
value = data?.GetValue() ?? defaultValue;
```

## Summary

**The core rules:**

1. Use `== null` / `!= null` for Unity objects
2. Never use `is null`, `?.`, `??`, or `ReferenceEquals()` with Unity objects
3. Always check after delays (coroutines, async operations)
4. Validate Inspector references in Awake/Start
5. Cache component references to avoid repeated lookups
6. Use `TryGetComponent` for efficiency

Unity's null checking exists because destroyed objects leave C# wrappers alive. The convenient
operators (`?.`, `??`) bypass Unity's override and only check the wrapper, causing crashes on
destroyed objects. Always use explicit `== null` checks.
