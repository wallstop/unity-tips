# Unity Object Pool Best Practices

## What Problem Does This Solve?

**The Problem:** Your game spawns 100 bullets per second. Each `Instantiate()` allocates, taking
real wallclock time.
[Reference](https://discussions.unity.com/t/gameobject-pool-to-avoid-performance-issues-in-instantiating-many-objects/33256/5).

**Why Instantiate is Slow:**

- Allocates memory for new GameObject
- Calls Awake() on all components
- Calls OnEnable() on all components
- Registers with Unity's scene hierarchy
- Triggers garbage collection when destroyed

**Performance Comparison:**

- `Instantiate()`: 0.1-0.5ms per object + GC spikes every few seconds
- `Pool.Get()`: 0.001-0.01ms per object + zero GC
- **Speed improvement: 50-2000x faster**

**Real-World Example:**

```csharp
// ❌ Without pooling - Player shoots 10 bullets/sec
void Shoot()
{
    Instantiate(bulletPrefab, position, rotation);
    // 10 bullets/sec × 0.5ms = 5ms/sec minimum
    // After 1000 bullets: GC spike = 50-100ms freeze
}

// ✅ With pooling
void Shoot()
{
    var bullet = bulletPool.Get();
    bullet.transform.SetPositionAndRotation(position, rotation);
    // 10 bullets/sec × 0.01ms = 0.1ms/sec
    // Zero GC spikes = smooth gameplay
}
```

**The Solution:** Object pooling reuses GameObjects instead of creating/destroying them. Pre-create
100 bullets at game start, recycle them as needed. Zero runtime allocations, 50-2000x faster.

---

## Table of Contents

- [What are Object Pools?](#what-are-object-pools)
- [When to Use Object Pools](#when-to-use-object-pools)
- [When NOT to Use Object Pools](#when-not-to-use-object-pools)
- [Critical Best Practices](#critical-best-practices)
- [Common Pitfalls and How to Avoid Them](#common-pitfalls-and-how-to-avoid-them)
- [Code Examples](#code-examples)

## What are Object Pools?

Object pools are a design pattern that manages a reusable collection of objects. Instead of
constantly creating and destroying objects (which triggers garbage collection and hurts
performance), you:

1. Create objects once
2. Return them to a pool when done
3. Retrieve and reuse them when needed

Think of it like a library: books are checked out, returned, and checked out again by different
people rather than being printed new each time.

## When to Use Object Pools

Object pools are beneficial when:

- **Frequent spawning/destroying** - Bullets, particles, enemies in a wave shooter
- **Consistent object types** - Same prefab being instantiated repeatedly
- **Performance-critical scenarios** - Mobile games, VR, scenarios with tight frame budgets
- **Predictable usage patterns** - You can estimate roughly how many objects you'll need

**Examples**: Projectiles, visual effects, enemies, collectibles, audio sources, UI notifications

## When NOT to Use Object Pools

Avoid object pools when:

- **Rare instantiation** - Objects created once or very infrequently (player character, level
  geometry)
- **Highly variable objects** - Each instance is significantly different
- **Complex initialization** - Objects require extensive per-use setup that negates pooling benefits
- **Memory constraints** - Limited memory where holding inactive objects is problematic
- **Premature optimization** - You haven't profiled and confirmed it's a bottleneck

**Remember**: Profile first. Don't assume you need pooling without evidence.

## Critical Best Practices

### 1. Release Must Be Immediate and Synchronous

**THE GOLDEN RULE**: Objects must be ready-to-use immediately when retrieved. Release operations
must be **synchronous** - no coroutines, no async operations.

```csharp
// GOOD: Immediate, synchronous cleanup
public void ReturnToPool()
{
    StopAllCoroutines();  // Stop any running coroutines
    velocity = Vector3.zero;
    health = maxHealth;
    gameObject.SetActive(false);
    pool.Release(this);
}

// BAD: Delayed/async cleanup
public void ReturnToPool()
{
    StartCoroutine(FadeOutAndReturn());
    // DANGER! Object in invalid state if reused
    pool.Release(this);
}
```

**Why this matters**: Retrieved objects could be partially reset, mid-animation, or have conflicting
state from previous use.

**If you need visual effects**: Handle separately, use a different pooled effect object, or complete
the effect before returning to pool.

### 2. Don't Cap Pools Unless Absolutely Necessary

```csharp
// GOOD: Unlimited pool (for most cases)
var pool = new ObjectPool<Bullet>(
    createFunc: () => Instantiate(bulletPrefab),
    actionOnGet: (obj) => obj.SetActive(true),
    actionOnRelease: (obj) => obj.SetActive(false)
);

// ONLY IF REQUIRED: Capped pool with throw on limit
var pool = new ObjectPool<Bullet>(
    createFunc: () => Instantiate(bulletPrefab),
    actionOnGet: (obj) => obj.SetActive(true),
    actionOnRelease: (obj) => obj.SetActive(false),
    actionOnDestroy: (obj) => Destroy(obj),
    maxSize: 1000 // Only if memory is genuinely constrained
);
```

**Why uncapped is usually better**:

- Memory is typically abundant enough for reasonable object counts
- Capping can cause unexpected behavior when limit is reached
- Pool naturally stabilizes at the peak usage level
- No performance benefit to capping unless memory is actually a problem

**When to cap**:

- Confirmed memory constraints (mobile, VR)
- Runaway spawning bugs need safeguards
- Objects are very memory-heavy

### 3. Always Reset State Completely

Stop all coroutines, clear references, reset physics, and unsubscribe from events.

```csharp
public void ReturnToPool()
{
    StopAllCoroutines();  // Stop any running coroutines
    ResetState();
    pool.Release(this);
}

public void ResetState()
{
    // Clear references to prevent memory leaks
    target = null;
    owner = null;

    // Reset physics
    if (rigidbody != null)
    {
        rigidbody.linearVelocity = Vector3.zero;
        rigidbody.angularVelocity = Vector3.zero;
    }

    // Reset transform
    transform.localScale = Vector3.one;
    transform.rotation = Quaternion.identity;

    // Reset component state
    health = maxHealth;

    // Unsubscribe from events
    GameManager.OnGameOver -= HandleGameOver;
}
```

### 4. ALWAYS Clear or Dispose Pools in OnDestroy

**CRITICAL**: If your MonoBehaviour owns an object pool, you **MUST** clean it up when destroyed.

Unity's `ObjectPool` provides two cleanup methods:

- **`Clear()`** - Destroys all objects, pool remains usable
- **`Dispose()`** - Calls `Clear()` + marks pool as disposed (prevents further use)

**Why this matters**: Pooled GameObjects remain in your scene as "orphans" without cleanup, causing
memory leaks and hierarchy clutter.

```csharp
// GOOD: Cleanup with Dispose()
public class BulletPool : MonoBehaviour
{
    private ObjectPool<Bullet> pool;

    private void Awake()
    {
        pool = new ObjectPool<Bullet>(
            createFunc: CreateBullet,
            actionOnGet: OnGetBullet,
            actionOnRelease: OnReleaseBullet,
            actionOnDestroy: OnDestroyBullet // Called by Clear()/Dispose()
        );
    }

    private void OnDestroy()
    {
        pool?.Dispose(); // CRITICAL: Always clean up
    }

    private void OnDestroyBullet(Bullet bullet)
    {
        if (bullet != null) Destroy(bullet.gameObject);
    }
}

// BAD: No cleanup - memory leak!
public class BadPool : MonoBehaviour
{
    private ObjectPool<Bullet> pool;
    // Missing OnDestroy! Objects never cleaned up!
}
```

**Clear() vs Dispose()**:

| Method      | What it does                       | When to use                                      |
| ----------- | ---------------------------------- | ------------------------------------------------ |
| `Clear()`   | Destroys objects, pool still works | Level resets, wave clears, reusing pool          |
| `Dispose()` | `Clear()` + marks disposed         | `OnDestroy()`, final cleanup, no more pool usage |

```csharp
// Common scenarios
public class PoolManager : MonoBehaviour
{
    private ObjectPool<Enemy> enemyPool;
    private ObjectPool<Bullet> bulletPool;

    // Multiple pools? Dispose all
    private void OnDestroy()
    {
        enemyPool?.Dispose();
        bulletPool?.Dispose();
    }

    // Reusing pool? Use Clear()
    public void OnWaveComplete()
    {
        enemyPool?.Clear(); // Pool reused for next wave
    }
}

// Dictionary of pools
public class DynamicPoolManager : MonoBehaviour
{
    private Dictionary<string, ObjectPool<GameObject>> pools = new();

    private void OnDestroy()
    {
        foreach (var pool in pools.Values)
            pool?.Dispose();
        pools.Clear();
    }
}
```

**How to verify cleanup works**:

- Enter Play Mode → Spawn pooled objects → Exit Play Mode
- Check hierarchy for leftover objects
- If you see them, you forgot cleanup!

**Debug tip**:

```csharp
private void OnDestroy()
{
    #if UNITY_EDITOR
    Debug.Log($"Disposing {pool.CountAll} pooled objects");
    #endif
    pool?.Dispose();
}
```

## Common Pitfalls and How to Avoid Them

### Pitfall #1: Double-Release

Returning the same object to the pool twice causes corruption. This is only needed if pool
entrance/exit state is complex and under many call paths. This should be unnecessary for simple pool
setup.

```csharp
// BAD: Could release twice
public void TakeDamage(int damage)
{
    health -= damage;
    if (health <= 0)
    {
        ReturnToPool(); // First release
    }
}

public void OnCollision()
{
    ReturnToPool(); // Might release again!
}

// GOOD: Guard against double-release
private bool isPooled = false;

public void ReturnToPool()
{
    if (isPooled) return;

    isPooled = true;
    ResetState();
    pool.Release(this);
}

public void OnGet()
{
    isPooled = false;
    Initialize();
}
```

### Pitfall #2: Forgetting to Unsubscribe from Events

```csharp
// BAD: Event subscription survives pooling
public void OnGet()
{
    GameManager.OnGameOver += HandleGameOver; // Memory leak!
}

// GOOD: Unsubscribe on release
public void OnRelease()
{
    GameManager.OnGameOver -= HandleGameOver;
}
```

### Pitfall #3: Not Stopping Child Coroutines

Child components may have running coroutines. Stop them all or iterate through children:
`GetComponentsInChildren<MonoBehaviour>().ForEach(c => c.StopAllCoroutines())`

### Pitfall #4: Destroying Instead of Releasing

Never call `Destroy(gameObject)` on pooled objects - always call `ReturnToPool()` instead.

### Pitfall #5: Scene References

Scene references become invalid when scenes unload. Clear them in `OnRelease()` and re-find them in
`OnGet()` using tags or managers.

### Pitfall #6: Forgetting to Clean Up the Pool Itself

**THE #1 MEMORY LEAK CAUSE!** See [Best Practice #4](#4-always-clear-or-dispose-pools-in-ondestroy)
for detailed guidance. Always call `pool?.Dispose()` in `OnDestroy()`.

## Code Examples

### Decoupling Pooled Objects from the Pool

**Anti-Pattern Warning**: Having pooled objects directly reference the pool (e.g.,
`pool.Release(this)`) creates tight coupling and makes objects less reusable. Objects become
dependent on the pooling system, making them harder to test and reuse in non-pooled contexts.

**Better Approach**: Use dependency injection (action delegates), centralized management, or events
to decouple objects from the pool. This follows the Dependency Inversion Principle and makes your
code more maintainable.

### Pattern 1: Action Delegate / Interface

This pattern uses an interface and action delegate to decouple pooled objects from the pool.

```csharp
// Interface for poolable objects
public interface IPoolable
{
    void Initialize(System.Action returnAction);
    void OnGet();
    void OnRelease();
}

// Pool manager
public class BulletPool : MonoBehaviour
{
    [SerializeField] private Bullet bulletPrefab;
    private ObjectPool<Bullet> pool;

    private void Awake()
    {
        pool = new ObjectPool<Bullet>(
            createFunc: CreateBullet,
            actionOnGet: OnGetBullet,
            actionOnRelease: OnReleaseBullet,
            actionOnDestroy: OnDestroyBullet,
            collectionCheck: true,
            defaultCapacity: 20
        );
    }

    private Bullet CreateBullet()
    {
        Bullet bullet = Instantiate(bulletPrefab, transform);
        // Pass the return function as a delegate
        bullet.Initialize(() => pool.Release(bullet));
        return bullet;
    }

    private void OnGetBullet(Bullet bullet)
    {
        bullet.gameObject.SetActive(true);
        bullet.OnGet();
    }

    private void OnReleaseBullet(Bullet bullet)
    {
        bullet.OnRelease();
        bullet.gameObject.SetActive(false);
    }

    private void OnDestroyBullet(Bullet bullet) => Destroy(bullet.gameObject);

    public Bullet Get() => pool.Get();

    private void OnDestroy() => pool?.Dispose();
}

// Pooled object - no knowledge of pool (kinda)
public class Bullet : MonoBehaviour, IPoolable
{
    private System.Action lifeEnded;
    private Rigidbody rb;
    private float lifetime;
    private const float MaxLifetime = 5f;

    private void Awake() => rb = GetComponent<Rigidbody>();

    public void Initialize(System.Action lifeEndedAction)
    {
        lifeEnded = lifeEndedAction;
    }

    public void OnGet()
    {
        lifetime = 0f;
    }

    public void OnRelease()
    {
        StopAllCoroutines();
        rb.linearVelocity = Vector3.zero;
        rb.angularVelocity = Vector3.zero;
        lifetime = 0f;
    }

    private void Update()
    {
        lifetime += Time.deltaTime;
        if (lifetime >= MaxLifetime)
            LifeEnded();
    }

    private void LifeEnded()
    {
        lifeEnded?.Invoke();
    }
}
```

### Pattern 2: Centralized Pool Manager (Simplest)

The pool manager handles all lifecycle management - pooled objects remain completely ignorant of
pooling.

```csharp
public class BulletPool : MonoBehaviour
{
    [SerializeField] private Bullet bulletPrefab;
    private ObjectPool<Bullet> pool;

    private void Awake()
    {
        pool = new ObjectPool<Bullet>(
            createFunc: () => Instantiate(bulletPrefab, transform),
            actionOnGet: (b) => b.gameObject.SetActive(true),
            actionOnRelease: (b) => { b.ResetState(); b.gameObject.SetActive(false); },
            actionOnDestroy: (b) => Destroy(b.gameObject),
            defaultCapacity: 20
        );
    }

    public Bullet Spawn(Vector3 position, Quaternion rotation)
    {
        Bullet bullet = pool.Get();
        bullet.transform.SetPositionAndRotation(position, rotation);
        StartCoroutine(ReturnAfterLifetime(bullet));
        return bullet;
    }

    private IEnumerator ReturnAfterLifetime(Bullet bullet)
    {
        yield return new WaitForSeconds(5f);
        if (bullet.gameObject.activeInHierarchy)
            pool.Release(bullet);
    }

    private void OnDestroy() => pool?.Dispose();
}

// Bullet knows nothing about pooling
public class Bullet : MonoBehaviour
{
    private Rigidbody rb;

    private void Awake() => rb = GetComponent<Rigidbody>();

    public void ResetState()
    {
        StopAllCoroutines();
        rb.linearVelocity = Vector3.zero;
        rb.angularVelocity = Vector3.zero;
    }
}
```

### Pattern 3: Event-Based (Unity-Friendly)

Use Unity events for loose coupling.

```csharp
public class Bullet : MonoBehaviour
{
    public UnityEvent<Bullet> OnBulletExpired = new();
    private Rigidbody rb;
    private float lifetime;

    private void Awake() => rb = GetComponent<Rigidbody>();

    private void Update()
    {
        lifetime += Time.deltaTime;
        if (lifetime >= 5f)
            OnBulletExpired?.Invoke(this); // Notify listeners
    }

    public void ResetState()
    {
        StopAllCoroutines();
        rb.linearVelocity = Vector3.zero;
        rb.angularVelocity = Vector3.zero;
        lifetime = 0f;
    }
}

public class BulletPool : MonoBehaviour
{
    [SerializeField] private Bullet bulletPrefab;
    private ObjectPool<Bullet> pool;

    private void Awake()
    {
        pool = new ObjectPool<Bullet>(
            createFunc: CreateBullet,
            actionOnGet: (b) => b.gameObject.SetActive(true),
            actionOnRelease: (b) => { b.ResetState(); b.gameObject.SetActive(false); },
            actionOnDestroy: (b) => Destroy(b.gameObject),
            defaultCapacity: 20
        );
    }

    private Bullet CreateBullet()
    {
        Bullet bullet = Instantiate(bulletPrefab, transform);
        bullet.OnBulletExpired.AddListener(HandleBulletExpired);
        return bullet;
    }

    private void HandleBulletExpired(Bullet bullet) => pool.Release(bullet);

    public Bullet Get() => pool.Get();

    private void OnDestroy() => pool?.Dispose();
}
```

**Pattern Comparison:**

| Pattern             | Decoupling | Complexity | Best For                           |
| ------------------- | ---------- | ---------- | ---------------------------------- |
| Action Delegate     | ⭐⭐⭐     | Medium     | Reusable, testable systems         |
| Centralized Manager | ⭐⭐⭐     | Low        | Simple, fixed-lifetime objects     |
| Event-Based         | ⭐⭐       | Medium     | Unity-native, inspector-friendly   |
| Direct Pool Ref     | ⭐         | Low        | Quick prototypes (not recommended) |

### Prewarming a Pool

Unity's ObjectPool supports prewarming via the `defaultCapacity` parameter, which creates objects at
initialization:

```csharp
private void Awake()
{
    pool = new ObjectPool<Bullet>(
        createFunc: CreateBullet,
        actionOnGet: OnGetBullet,
        actionOnRelease: OnReleaseBullet,
        actionOnDestroy: OnDestroyBullet,
        collectionCheck: true,
        defaultCapacity: 50  // Pre-creates 50 bullets at initialization
    );
}
```

## Summary Checklist

When implementing object pooling, ensure:

- [ ] **Pool cleanup** - `OnDestroy()` calls `pool?.Dispose()` (THE #1 MISTAKE!)
- [ ] **actionOnDestroy defined** - Specified when creating pool
- [ ] **Synchronous release** - No async/coroutines in release functions
- [ ] **Complete reset** - Stop coroutines, clear references, reset physics, unsubscribe events
- [ ] **Double-release guard** - Use flag to prevent releasing twice
- [ ] **Uncapped pools** - Don't cap unless memory is proven issue
- [ ] **SetActive(false)** - Called on release

**Key reminder**: `Dispose()` = final cleanup in `OnDestroy()`, `Clear()` = reset but keep pool
usable.

**Remember**: Profile first, optimize second. Object pools are an optimization tool - use them when
proven beneficial.
