# Unity Object Pool Best Practices

## What Problem Does This Solve?

**The Problem:** Your game spawns 100 bullets per second. Each `Instantiate()` allocates, taking real wallclock time. [Reference](https://discussions.unity.com/t/gameobject-pool-to-avoid-performance-issues-in-instantiating-many-objects/33256/5).

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
void Shoot() {
    Instantiate(bulletPrefab, position, rotation);
    // 10 bullets/sec × 0.5ms = 5ms/sec minimum
    // After 1000 bullets: GC spike = 50-100ms freeze
}

// ✅ With pooling
void Shoot() {
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

### 1. Objects Must Be Ready-to-Use When Retrieved

**THE GOLDEN RULE**: When you return an object to the pool, it must be in a state where it can be
immediately retrieved and used.

```csharp
// GOOD: Immediate, synchronous cleanup
public void ReturnToPool()
{
    // Reset state immediately
    velocity = Vector3.zero;
    health = maxHealth;
    isActive = false;

    // Disable immediately
    gameObject.SetActive(false);

    // Return to pool
    pool.Release(this);
}

// BAD: Delayed cleanup via coroutine
public void ReturnToPool()
{
    StartCoroutine(FadeOutAndReturn()); // DANGER!
}

private IEnumerator FadeOutAndReturn()
{
    // If object is retrieved during this coroutine,
    // it's in an invalid state!
    yield return new WaitForSeconds(1.0f);
    pool.Release(this);
}
```

**Why this matters**: If an object is retrieved from the pool while a coroutine is running, it could
be:

- Partially reset
- In the middle of an animation
- Have conflicting state from the previous use

### 2. Release Functions Should NEVER Be Async

Release/return operations must be **immediate and synchronous**.

```csharp
// GOOD: Synchronous release
public void Release()
{
    ResetState();
    pool.Release(this);
}

// BAD: Coroutine release
public void Release()
{
    StartCoroutine(AsyncCleanupCoroutine());
    pool.Release(this);
}
```

**If you need visual effects before returning to pool**:

- Handle the effect separately from the pooled object
- Use a different pooled object for the effect
- Complete the effect before returning to pool

### 3. Don't Cap Pools Unless Absolutely Necessary

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

### 4. Stop All Coroutines on Release

Any coroutines running on a pooled object must be stopped before returning to pool.

```csharp
// GOOD: Stop coroutines before release
public void ReturnToPool()
{
    StopAllCoroutines();
    ResetState();
    pool.Release(this);
}

// BAD: Coroutines keep running
public void ReturnToPool()
{
    // Coroutine from previous use still running!
    pool.Release(this);
}
```

### 5. Clear References and Reset State

```csharp
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
    isActive = false;

    // Unsubscribe from events
    Listener -= OnDeath;
}
```

### 6. ALWAYS Clear or Dispose Pools in OnDestroy

**CRITICAL**: If your MonoBehaviour owns an object pool, you **MUST** clean it up when the
MonoBehaviour is destroyed.

Unity's `ObjectPool` provides two cleanup methods:

- **`Clear()`** - Destroys all objects currently in the pool (both active and inactive)
- **`Dispose()`** - Calls `Clear()` and then marks the pool as disposed (prevents further use)

**Why this matters**:

- Pooled objects are real GameObjects in your scene
- If you don't clean up the pool, those GameObjects will remain in the scene as "orphans"
- This causes memory leaks and clutters your hierarchy
- In Play Mode, you'll see objects persist between play sessions
- In builds, memory usage will continuously grow

```csharp
// GOOD: Use Dispose() for complete cleanup
public class BulletPool : MonoBehaviour
{
    private ObjectPool<Bullet> pool;

    private void Awake()
    {
        pool = new ObjectPool<Bullet>(
            createFunc: CreateBullet,
            actionOnGet: OnGetBullet,
            actionOnRelease: OnReleaseBullet,
            actionOnDestroy: OnDestroyBullet
        );
    }

    private void OnDestroy()
    {
        // Dispose() is preferred - it calls Clear() and prevents further pool use
        pool?.Dispose();
    }

    private void OnDestroyBullet(Bullet bullet)
    {
        // This gets called for each pooled object when Dispose()/Clear() is called
        if (bullet != null)
        {
            Destroy(bullet.gameObject);
        }
    }
}

// ALSO GOOD: Use Clear() if you need to reuse the pool
public class ReusablePool : MonoBehaviour
{
    private ObjectPool<Effect> effectPool;

    public void ClearPool()
    {
        // Clear() destroys all pooled objects but pool remains usable
        effectPool?.Clear();
        // Can still call effectPool.Get() after this
    }

    private void OnDestroy()
    {
        // Dispose() when the pool owner is being destroyed
        effectPool?.Dispose();
    }
}

// BAD: No cleanup - leaves orphaned objects!
public class BulletPool : MonoBehaviour
{
    private ObjectPool<Bullet> pool;

    private void Awake()
    {
        pool = new ObjectPool<Bullet>(/* ... */);
    }

    // Missing OnDestroy! Pooled bullets will never be cleaned up!
}
```

**Clear() vs Dispose() - When to use which**:

| Method      | What it does                                     | When to use                                                 |
| ----------- | ------------------------------------------------ | ----------------------------------------------------------- |
| `Clear()`   | Destroys all pooled objects, pool remains usable | Resetting a level, clearing between waves, reusing the pool |
| `Dispose()` | Calls `Clear()` + marks pool as disposed         | `OnDestroy()`, final cleanup, pool won't be used again      |

```csharp
// Example: Using both Clear() and Dispose()
public class WaveManager : MonoBehaviour
{
    private ObjectPool<Enemy> enemyPool;

    public void OnWaveComplete()
    {
        // Clear between waves - pool is reused for next wave
        enemyPool?.Clear();
    }

    private void OnDestroy()
    {
        // Dispose when done forever - pool won't be used again
        enemyPool?.Dispose();
    }
}
```

**What happens without cleanup**:

1. **In Editor**: After exiting Play Mode, pooled objects remain in your hierarchy (look for
   DontDestroyOnLoad or inactive objects)
2. **In Builds**: Memory is never freed, leading to memory leaks
3. **Scene Transitions**: Objects from previous scenes can leak into new scenes

**Easy way to check if you have this problem**:

- Enter Play Mode
- Spawn some pooled objects
- Exit Play Mode
- Look in your hierarchy - if you see leftover objects, you forgot to clean up your pool!

**Different cleanup scenarios**:

```csharp
// If your pool manager is a singleton/DontDestroyOnLoad
public class GlobalPoolManager : MonoBehaviour
{
    private ObjectPool<Effect> effectPool;

    private void OnDestroy()
    {
        // Use Dispose() for final cleanup
        effectPool?.Dispose();
    }

    private void OnApplicationQuit()
    {
        // Extra safety: dispose on application quit
        effectPool?.Dispose();
    }
}

// If your pool is tied to a scene/level
public class LevelEnemyPool : MonoBehaviour
{
    private ObjectPool<Enemy> enemyPool;

    private void OnDestroy()
    {
        // Use Dispose() for scene transitions - pool won't be used again
        enemyPool?.Dispose();
    }

    public void RestartLevel()
    {
        // Use Clear() when restarting - pool will be reused
        enemyPool?.Clear();
    }
}

// If you're using multiple pools
public class MultiPoolManager : MonoBehaviour
{
    private ObjectPool<Bullet> bulletPool;
    private ObjectPool<Enemy> enemyPool;
    private ObjectPool<Particle> particlePool;

    private void OnDestroy()
    {
        // Dispose ALL your pools
        bulletPool?.Dispose();
        enemyPool?.Dispose();
        particlePool?.Dispose();
    }
}

// If you're using a dictionary of pools
public class DynamicPoolManager : MonoBehaviour
{
    private Dictionary<string, ObjectPool<GameObject>> pools = new();

    private void OnDestroy()
    {
        // Dispose all pools in the dictionary
        foreach (var pool in pools.Values)
        {
            pool?.Dispose();
        }
        pools.Clear();
    }
}
```

**Pro tip**: If you forget this, you might not notice immediately because:

- Your game seems to work fine
- Performance might even be good at first
- But over time (especially with scene transitions), memory usage grows
- Eventually you'll run out of memory or have thousands of hidden objects

**Testing your cleanup**:

```csharp
private void OnDestroy()
{
    #if UNITY_EDITOR
    Debug.Log($"Disposing {pool.CountAll} pooled objects");
    #endif

    pool?.Dispose();
}
```

This helps you verify in the console that cleanup actually happened!

**Quick reference**:

```csharp
// Use Clear() when you want to destroy all pooled objects but keep using the pool
pool.Clear();  // Destroys all objects, pool still usable

// Use Dispose() when you're completely done with the pool
pool.Dispose(); // Destroys all objects AND marks pool as disposed (no further use)
```

## Common Pitfalls and How to Avoid Them

### Pitfall #1: Double-Release

Returning the same object to the pool twice causes corruption.

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

### Pitfall #3: Children with Active Coroutines

```csharp
// BAD: Child components running coroutines
public class Bullet : MonoBehaviour
{
    private TrailRenderer trail;

    public void ReturnToPool()
    {
        // TrailRenderer might have a fade coroutine running!
        pool.Release(this);
    }
}

// GOOD: Stop all coroutines on entire hierarchy
public void ReturnToPool()
{
    // Stop coroutines on all children
    foreach (var coroutineRunner in GetComponentsInChildren<MonoBehaviour>())
    {
        coroutineRunner.StopAllCoroutines();
    }

    pool.Release(this);
}
```

### Pitfall #4: Destroying Instead of Releasing

```csharp
// BAD: Defeats the purpose of pooling
public void Die()
{
    Destroy(gameObject); // Don't do this with pooled objects!
}

// GOOD: Always return to pool
public void Die()
{
    ReturnToPool();
}
```

### Pitfall #5: Pooling Objects with Scene References

```csharp
// PROBLEMATIC: References to scene objects
public class Enemy : MonoBehaviour
{
    public Transform patrolRoute; // Scene reference!

    // If scene unloads, this reference becomes invalid
    // when object is retrieved from pool
}

// BETTER: Find references when retrieved
public class Enemy : MonoBehaviour
{
    private Transform patrolRoute;

    public void OnGet()
    {
        GameObject routeObj = GameObject.FindWithTag("PatrolRoute");
        if (routeObj != null)
            patrolRoute = routeObj.transform;
    }

    public void OnRelease()
    {
        patrolRoute = null;
    }
}
```

### Pitfall #6: Forgetting to Clean Up the Pool Itself

**THIS IS THE #1 MEMORY LEAK CAUSE WITH OBJECT POOLS!**

```csharp
// BAD: Pool owner has no cleanup
public class WeaponSystem : MonoBehaviour
{
    private ObjectPool<Projectile> projectilePool;

    private void Awake()
    {
        projectilePool = new ObjectPool<Projectile>(
            createFunc: () => Instantiate(projectilePrefab),
            actionOnGet: (p) => p.gameObject.SetActive(true),
            actionOnRelease: (p) => p.gameObject.SetActive(false),
            actionOnDestroy: (p) => Destroy(p.gameObject)
        );
    }

    // NO OnDestroy! When this WeaponSystem is destroyed,
    // all the pooled projectiles become orphans in the scene!
}

// GOOD: Always clean up your pools
public class WeaponSystem : MonoBehaviour
{
    private ObjectPool<Projectile> projectilePool;

    private void Awake()
    {
        projectilePool = new ObjectPool<Projectile>(
            createFunc: () => Instantiate(projectilePrefab),
            actionOnGet: (p) => p.gameObject.SetActive(true),
            actionOnRelease: (p) => p.gameObject.SetActive(false),
            actionOnDestroy: (p) => Destroy(p.gameObject) // This is called by Clear()
        );
    }

    private void OnDestroy()
    {
        // ALWAYS call Dispose() to destroy all pooled objects and mark pool as done
        projectilePool?.Dispose();
    }
}
```

**How to spot this bug**:

1. Run your game in the Editor
2. Spawn some pooled objects
3. Stop Play Mode
4. Check your Hierarchy - do you see inactive GameObjects that shouldn't be there?
5. If yes, you forgot to clear your pool!

**Memory leak symptoms**:

- Scene transitions leave objects behind
- Memory usage grows over time
- Hierarchy fills with inactive objects
- "DontDestroyOnLoad" objects accumulating

## Code Examples

### Basic Pool Setup (Unity's ObjectPool)

```csharp
using UnityEngine;
using UnityEngine.Pool;

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
            collectionCheck: true, // Detect double-release in debug
            defaultCapacity: 20
        );
    }

    private Bullet CreateBullet()
    {
        Bullet bullet = Instantiate(bulletPrefab, transform);
        bullet.SetPool(pool);
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

    private void OnDestroyBullet(Bullet bullet)
    {
        Destroy(bullet.gameObject);
    }

    public Bullet Get()
    {
        return pool.Get();
    }

    private void OnDestroy()
    {
        // CRITICAL: Clean up all pooled objects when this manager is destroyed
        pool?.Dispose();
    }
}
```

### Pooled Object Implementation

```csharp
using UnityEngine;
using UnityEngine.Pool;

public class Bullet : MonoBehaviour
{
    private IObjectPool<Bullet> pool;
    private Rigidbody rb;
    private float lifetime;
    private const float MaxLifetime = 5f;

    private void Awake()
    {
        rb = GetComponent<Rigidbody>();
    }

    public void SetPool(IObjectPool<Bullet> objectPool)
    {
        pool = objectPool;
    }

    public void OnGet()
    {
        lifetime = 0f;
        // Initialize any state needed for a fresh bullet
    }

    public void OnRelease()
    {
        // Stop any running coroutines
        StopAllCoroutines();

        // Reset physics
        rb.linearVelocity = Vector3.zero;
        rb.angularVelocity = Vector3.zero;

        // Reset state
        lifetime = 0f;
    }

    private void Update()
    {
        lifetime += Time.deltaTime;

        if (lifetime >= MaxLifetime)
        {
            ReturnToPool();
        }
    }

    private void OnCollisionEnter(Collision collision)
    {
        // Handle collision
        ReturnToPool();
    }

    public void ReturnToPool()
    {
        pool.Release(this);
    }
}
```

### Prewarming a Pool

```csharp
public void PrewarmPool(int count)
{
    List<Bullet> bullets = new List<Bullet>(count);

    // Get objects to create them
    for (int i = 0; i < count; i++)
    {
        bullets.Add(pool.Get());
    }

    // Return them all
    foreach (var bullet in bullets)
    {
        pool.Release(bullet);
    }
}
```

## Summary Checklist

When implementing object pooling, ensure:

- [ ] **Pool cleanup implemented** - OnDestroy() calls pool.Clear()
- [ ] **actionOnDestroy defined** - Specified when creating the pool
- [ ] Release functions are synchronous (no async/coroutines)
- [ ] Objects are fully reset when returned to pool
- [ ] All coroutines are stopped before release
- [ ] Event subscriptions are cleared on release
- [ ] Guard against double-release
- [ ] Don't cap pool size unless memory is a proven issue
- [ ] SetActive(false) is called on release
- [ ] References are cleared to prevent memory leaks
- [ ] Children components are also properly reset
- [ ] Scene references are handled appropriately

**The #1 Mistake**: Forgetting to call `pool?.Dispose()` in `OnDestroy()`. This causes memory leaks
and orphaned GameObjects. **Always clean up your pools!**

**Remember the difference**:

- **`Dispose()`** = Final cleanup (use in `OnDestroy()`)
- **`Clear()`** = Reset pool but keep using it (use for level resets, wave clears, etc.)

**Remember**: Object pools are an optimization tool. Profile first, optimize second. When in doubt,
keep it simple and follow these practices to avoid subtle bugs.
