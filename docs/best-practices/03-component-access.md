# Unity Component Access Best Practices

## What Problem Does This Solve?

**The Problem:** Calling `GetComponent<Rigidbody>()` every frame is slow. In a game with 100 enemies
calling GetComponent in Update, this can cost 5-10ms per frame—causing visible stuttering at 60 FPS.

**Why This Happens:** `GetComponent()` searches through all components on a GameObject every time
you call it. This search takes time, especially with many components.

**The Solution:** Cache component references once in `Awake()` or `Start()`, then reuse them. This
turns a 1-5ms operation into a 0.001ms memory lookup.

**Performance Gain:** Caching components can improve frame time by 30-50% in component-heavy scenes.

**Real Numbers:**

- `GetComponent()` in Update: 0.05ms per call × 100 enemies × 60 FPS = **300ms per second** (18
  frames lost!)
- Cached reference: 0.0001ms per access × 100 enemies × 60 FPS = **0.6ms per second** (negligible)
- **Performance improvement: 500x faster**

---

## ⚠️ Critical Rules

**The most common mistakes:**

1. Using `GetComponent` in `Update()` - Cache in `Awake()` instead!
2. Not checking if `GetComponent` returns null
3. Using `Find` methods in performance-critical code
4. Not using `TryGetComponent` when available

## Table of Contents

- [Component Access Methods](#component-access-methods)
- [When to Use Each Method](#when-to-use-each-method)
- [Caching Strategies](#caching-strategies)
- [Performance Comparison](#performance-comparison)
- [Best Practices](#best-practices)
- [Common Pitfalls](#common-pitfalls)

## Component Access Methods

### GetComponent (Instance Method)

```csharp
// Get component on same GameObject
Rigidbody rb = GetComponent<Rigidbody>();

// Always check for null!
if (rb != null)
{
    rb.AddForce(Vector3.up * 10);
}
```

**Performance**: Fast (but still has overhead - cache when possible) **When to use**: Getting
components on the same GameObject

### TryGetComponent (Recommended)

```csharp
// Modern approach - more efficient
if (TryGetComponent<Rigidbody>(out var rb))
{
    rb.AddForce(Vector3.up * 10);
}

// Equivalent to:
Rigidbody rb = GetComponent<Rigidbody>();
if (rb != null)
{
    rb.AddForce(Vector3.up * 10);
}
```

**Performance**: Faster than `GetComponent` + null check **When to use**: Always prefer this over
`GetComponent` when you need to check existence **Why it's better**: Single lookup instead of
lookup + separate null check

### GetComponentInChildren

```csharp
// Finds component on this GameObject or any child
Health health = GetComponentInChildren<Health>();

// Include inactive children
Health health = GetComponentInChildren<Health>(includeInactive: true);
```

**Performance**: SLOW - Searches entire hierarchy recursively **When to use**: Sparingly, never in
Update/FixedUpdate

### GetComponentInParent

```csharp
// Finds component on this GameObject or any parent
PlayerController player = GetComponentInParent<PlayerController>();

// Include inactive parents
PlayerController player = GetComponentInParent<PlayerController>(includeInactive: true);
```

**Performance**: SLOW - Searches up the hierarchy **When to use**: Initialization only, never in
Update/FixedUpdate

### GetComponents (Multiple Components)

```csharp
// Get all components of type on this GameObject
Collider[] colliders = GetComponents<Collider>();

// Better: Use List overload to avoid allocations
private List<Collider> colliders = new List<Collider>();

void CacheColliders()
{
    GetComponents<Collider>(colliders);
    // colliders list now contains all Collider components
}
```

**Performance**: Slow, allocates array (unless using List overload) **When to use**: Initialization,
use List overload for reuse

### GetComponentsInChildren (Multiple in Hierarchy)

```csharp
// ❌ BAD - Allocates new array every call
void Update()
{
    Renderer[] renderers = GetComponentsInChildren<Renderer>();
}

// ✓ GOOD - Cache and reuse list
private List<Renderer> renderers = new List<Renderer>();

void Start()
{
    GetComponentsInChildren<Renderer>(renderers);
}

void Update()
{
    // Use cached renderers list
    foreach (var renderer in renderers)
    {
        renderer.enabled = true;
    }
}
```

**Performance**: VERY SLOW - Searches entire hierarchy **When to use**: Initialization only, always
use List overload

## When to Use Each Method

### TryGetComponent - Preferred for Conditional Access

```csharp
// ✓ Use when you're not sure if component exists
if (TryGetComponent<Rigidbody>(out var rb))
{
    rb.AddForce(Vector3.up);
}

// ✓ Use in collision/trigger handlers
private void OnCollisionEnter(Collision collision)
{
    if (collision.gameObject.TryGetComponent<Breakable>(out var breakable))
    {
        breakable.Break();
    }
}

// ✓ Use for optional components
if (TryGetComponent<AudioSource>(out var audio))
{
    audio.Play();
}
```

### GetComponent - Use When Caching or Component Guaranteed

```csharp
// ✓ Use when caching in Awake/Start
private Rigidbody rb;

private void Awake()
{
    rb = GetComponent<Rigidbody>();
    Debug.Assert(rb != null, "Rigidbody required!");
}

// ✓ Use with RequireComponent (component guaranteed to exist)
[RequireComponent(typeof(Rigidbody))]
public class PhysicsController : MonoBehaviour
{
    private Rigidbody rb;

    private void Awake()
    {
        // Safe - RequireComponent ensures it exists
        rb = GetComponent<Rigidbody>();
    }
}
```

### GetComponentInChildren - Use Sparingly

```csharp
// ✓ ACCEPTABLE - Called once in Start
private void Start()
{
    Animator animator = GetComponentInChildren<Animator>();
    if (animator != null)
    {
        animator.SetTrigger("Spawn");
    }
}

// ❌ NEVER - Don't call repeatedly
private void Update()
{
    // TERRIBLE for performance!
    Animator anim = GetComponentInChildren<Animator>();
    if (anim != null)
        anim.SetTrigger("Walk");
}
```

### RequireComponent - Best for Mandatory Components

```csharp
// ✓ BEST PRACTICE - Enforces component at edit time
[RequireComponent(typeof(Rigidbody))]
[RequireComponent(typeof(Collider))]
public class PhysicsObject : MonoBehaviour
{
    private Rigidbody rb;
    private Collider col;

    private void Awake()
    {
        // Safe - RequireComponent guarantees these exist
        rb = GetComponent<Rigidbody>();
        col = GetComponent<Collider>();
    }
}
```

## Caching Strategies

### Cache in Awake/Start

```csharp
// ✓ BEST PRACTICE - Cache in Awake/Start
public class CachedComponents : MonoBehaviour
{
    // Cached references
    private Rigidbody rb;
    private Transform tf;
    private Renderer rend;

    private void Awake()
    {
        // Cache components once
        rb = GetComponent<Rigidbody>();
        tf = transform;  // transform is already cached by Unity, but this shows the pattern
        rend = GetComponent<Renderer>();

        // Validate required components
        Debug.Assert(rb != null, "Rigidbody required!");
        Debug.Assert(rend != null, "Renderer required!");
    }

    private void Update()
    {
        // Use cached references - no GetComponent calls!
        rb.AddForce(Vector3.up);
        rend.material.color = Color.red;
    }
}
```

### Cache Child/Parent Components

```csharp
// ✓ GOOD - Cache hierarchy searches
public class HierarchyCache : MonoBehaviour
{
    [Header("Cached Child Components")]
    private Animator animator;
    private ParticleSystem particles;

    [Header("Cached Parent Components")]
    private PlayerController controller;

    private void Awake()
    {
        // Cache once at initialization
        animator = GetComponentInChildren<Animator>();
        particles = GetComponentInChildren<ParticleSystem>();
        controller = GetComponentInParent<PlayerController>();

        // Validate
        if (animator == null)
            Debug.LogWarning("Animator not found in children!");
    }

    public void PlayAnimation()
    {
        // Use cached reference
        if (animator != null)
            animator.SetTrigger("Play");
    }
}
```

### Use SerializeField for Editor Assignment

```csharp
// ✓ BEST - Assign in Inspector when possible
public class EditorAssigned : MonoBehaviour
{
    [SerializeField] private Rigidbody rb;
    [SerializeField] private Transform target;
    [SerializeField] private AudioSource audioSource;

    private void Awake()
    {
        // Validate Inspector assignments
        if (rb == null)
            Debug.LogError("Rigidbody not assigned!", this);

        if (target == null)
            Debug.LogError("Target not assigned!", this);
    }

    private void Update()
    {
        // Use references - no runtime searching
        if (rb != null && target != null)
        {
            rb.MovePosition(target.position);
        }
    }
}
```

### Lazy Caching Pattern

```csharp
// ✓ GOOD - Lazy cache for optional components
public class LazyCache : MonoBehaviour
{
    private Rigidbody _rb;
    public Rigidbody Rb
    {
        get
        {
            if (_rb == null)
                _rb = GetComponent<Rigidbody>();
            return _rb;
        }
    }

    private void Update()
    {
        // Automatically caches on first access
        if (Rb != null)
            Rb.AddForce(Vector3.up);
    }
}

// ✓ MODERN - Using null-coalescing assignment (C# 8.0+)
public class ModernLazyCache : MonoBehaviour
{
    private Rigidbody rb;

    private void Update()
    {
        // Cache on first use
        rb ??= GetComponent<Rigidbody>();

        if (rb != null)
            rb.AddForce(Vector3.up);
    }
}
```

## Performance Comparison

```
Performance ranking (fastest to slowest):

1. Cached reference                     // Virtually free
2. transform, gameObject properties     // Already cached by Unity
3. TryGetComponent                      // ~0.02ms
4. GetComponent                         // ~0.025ms
5. GetComponents (with List reuse)      // ~0.05ms
6. GetComponentInChildren               // ~0.1-1ms (depends on hierarchy depth)
7. GetComponentsInChildren (List)       // ~0.5-5ms (depends on hierarchy depth)
8. FindObjectOfType                     // ~1-10ms (depends on scene size)
9. FindObjectsOfType                    // ~5-50ms (depends on scene size)
10. GetComponentInChildren (no cache)   // Allocates garbage
11. Find with string                    // VERY SLOW + fragile
```

### Performance Test Example

```csharp
// Performance comparison
private void PerformanceTest()
{
    var stopwatch = System.Diagnostics.Stopwatch.StartNew();

    // Test 1: Cached reference (FASTEST)
    for (int i = 0; i < 10000; i++)
    {
        var rb = cachedRigidbody;
    }
    Debug.Log($"Cached: {stopwatch.ElapsedMilliseconds}ms");  // ~0ms

    stopwatch.Restart();

    // Test 2: TryGetComponent
    for (int i = 0; i < 10000; i++)
    {
        TryGetComponent<Rigidbody>(out var rb);
    }
    Debug.Log($"TryGetComponent: {stopwatch.ElapsedMilliseconds}ms");  // ~200ms

    stopwatch.Restart();

    // Test 3: GetComponent
    for (int i = 0; i < 10000; i++)
    {
        var rb = GetComponent<Rigidbody>();
    }
    Debug.Log($"GetComponent: {stopwatch.ElapsedMilliseconds}ms");  // ~250ms

    stopwatch.Restart();

    // Test 4: GetComponentInChildren (SLOWEST)
    for (int i = 0; i < 1000; i++)  // Only 1000 iterations!
    {
        var rb = GetComponentInChildren<Rigidbody>();
    }
    Debug.Log($"GetComponentInChildren: {stopwatch.ElapsedMilliseconds}ms");  // ~1000ms
}
```

## Best Practices

### 1. Cache Everything in Awake/Start

```csharp
// ✓ EXCELLENT - All components cached at start
public class OptimalComponent : MonoBehaviour
{
    // Components on this GameObject
    private Rigidbody rb;
    private Collider col;
    private Renderer rend;

    // Components in hierarchy
    private Animator animator;
    private Transform targetBone;

    // External references
    [SerializeField] private Transform target;

    private void Awake()
    {
        // Cache all components at initialization
        rb = GetComponent<Rigidbody>();
        col = GetComponent<Collider>();
        rend = GetComponent<Renderer>();

        animator = GetComponentInChildren<Animator>();
        targetBone = animator.GetBoneTransform(HumanBodyBones.RightHand);

        ValidateReferences();
    }

    private void ValidateReferences()
    {
        Debug.Assert(rb != null, "Rigidbody missing!");
        Debug.Assert(col != null, "Collider missing!");
        Debug.Assert(target != null, "Target not assigned!");
    }

    private void Update()
    {
        // Use cached references - optimal performance
        rb.AddForce(Vector3.up);
        rend.material.color = Color.red;
    }
}
```

### 2. Use RequireComponent for Dependencies

```csharp
// ✓ BEST - Enforces dependencies at edit time
[RequireComponent(typeof(Rigidbody))]
[RequireComponent(typeof(Collider))]
[RequireComponent(typeof(AudioSource))]
public class RequiredComponents : MonoBehaviour
{
    private Rigidbody rb;
    private Collider col;
    private AudioSource audio;

    private void Awake()
    {
        // Safe - RequireComponent guarantees existence
        rb = GetComponent<Rigidbody>();
        col = GetComponent<Collider>();
        audio = GetComponent<AudioSource>();
    }
}
```

### 3. Use List Overloads to Avoid Allocations

```csharp
// ✓ EXCELLENT - Reuse List to avoid garbage
public class ListOverloadExample : MonoBehaviour
{
    // Reusable list - no allocations after first use
    private List<Collider> colliders = new List<Collider>();
    private List<Renderer> renderers = new List<Renderer>();

    private void Start()
    {
        // Populate lists once
        GetComponents<Collider>(colliders);
        GetComponentsInChildren<Renderer>(renderers);
    }

    public void DisableAllRenderers()
    {
        // Use cached list - no allocations
        foreach (var renderer in renderers)
        {
            renderer.enabled = false;
        }
    }

    public void RefreshColliders()
    {
        // Reuse same list - clears and repopulates
        GetComponents<Collider>(colliders);
    }
}
```

### 4. Validate in Development, Trust in Production

```csharp
public class DevelopmentValidation : MonoBehaviour
{
    private Rigidbody rb;

    private void Awake()
    {
        rb = GetComponent<Rigidbody>();

        // Validation only runs in editor and development builds
        #if UNITY_EDITOR || DEVELOPMENT_BUILD
        if (rb == null)
        {
            Debug.LogError($"Rigidbody missing on {gameObject.name}!", this);
        }
        #endif
    }

    private void Update()
    {
        // No null check needed in production builds
        #if UNITY_EDITOR || DEVELOPMENT_BUILD
        if (rb != null)
        #endif
        {
            rb.AddForce(Vector3.up);
        }
    }
}
```

### 5. Use TryGetComponent for Optional Components

```csharp
// ✓ GOOD - Clean optional component pattern
public class OptionalComponents : MonoBehaviour
{
    private void OnCollisionEnter(Collision collision)
    {
        // Check if object has Health component
        if (collision.gameObject.TryGetComponent<Health>(out var health))
        {
            health.TakeDamage(10);
        }

        // Check if object has Rigidbody
        if (collision.gameObject.TryGetComponent<Rigidbody>(out var rb))
        {
            rb.AddForce(Vector3.up * 100);
        }

        // No errors if components don't exist
    }
}
```

## Common Pitfalls

### Pitfall 1: GetComponent in Update

```csharp
// ❌ TERRIBLE - GetComponent called every frame!
private void Update()
{
    Rigidbody rb = GetComponent<Rigidbody>();
    rb.AddForce(Vector3.up);
}

// ✓ CORRECT - Cache in Awake
private Rigidbody rb;

private void Awake()
{
    rb = GetComponent<Rigidbody>();
}

private void Update()
{
    rb.AddForce(Vector3.up);
}
```

**Why it's bad**: `GetComponent` is slow relative to cached access. Called 60+ times per second,
this adds up quickly!

### Pitfall 2: Not Checking GetComponent Results

```csharp
// ❌ BAD - Assumes component exists
private void Start()
{
    Rigidbody rb = GetComponent<Rigidbody>();
    rb.AddForce(Vector3.up);  // ☠️ NullReferenceException if no Rigidbody!
}

// ✓ GOOD - Always check
private void Start()
{
    if (TryGetComponent<Rigidbody>(out var rb))
    {
        rb.AddForce(Vector3.up);
    }
    else
    {
        Debug.LogError("Rigidbody required!", this);
    }
}

// ✓ BEST - Use RequireComponent
[RequireComponent(typeof(Rigidbody))]
public class SafeComponent : MonoBehaviour
{
    private void Start()
    {
        // Safe - component guaranteed to exist
        Rigidbody rb = GetComponent<Rigidbody>();
        rb.AddForce(Vector3.up);
    }
}
```

### Pitfall 3: Using GetComponentInChildren in Update

```csharp
// ❌ CATASTROPHIC - Searches entire hierarchy every frame!
private void Update()
{
    Animator anim = GetComponentInChildren<Animator>();
    if (anim != null)
        anim.SetFloat("Speed", 5f);
}

// ✓ CORRECT - Cache in Awake
private Animator anim;

private void Awake()
{
    anim = GetComponentInChildren<Animator>();
}

private void Update()
{
    if (anim != null)
        anim.SetFloat("Speed", 5f);
}
```

**Why it's catastrophic**: With a deep hierarchy, this can take milliseconds per frame!

### Pitfall 4: Not Using List Overloads

```csharp
// ❌ BAD - Creates garbage every call
public void DisableAllRenderers()
{
    Renderer[] renderers = GetComponentsInChildren<Renderer>();
    foreach (var renderer in renderers)
    {
        renderer.enabled = false;
    }
    // Array is garbage collected
}

// ✓ GOOD - Reuse List
private List<Renderer> renderers = new List<Renderer>();

public void DisableAllRenderers()
{
    renderers.Clear();  // Clear previous contents
    GetComponentsInChildren<Renderer>(renderers);

    foreach (var renderer in renderers)
    {
        renderer.enabled = false;
    }
    // No garbage created!
}
```

### Pitfall 5: Using Find Methods in Performance Code

```csharp
// ❌ TERRIBLE - Searches entire scene every frame!
private void Update()
{
    GameObject player = GameObject.Find("Player");
    transform.LookAt(player.transform);
}

// ✓ CORRECT - Find once, cache forever
private Transform player;

private void Start()
{
    GameObject playerObj = GameObject.Find("Player");
    if (playerObj != null)
        player = playerObj.transform;
}

private void Update()
{
    if (player != null)
        transform.LookAt(player);
}

// ✓ BETTER - Use tags (faster than Find)
private Transform player;

private void Start()
{
    GameObject playerObj = GameObject.FindGameObjectWithTag("Player");
    if (playerObj != null)
        player = playerObj.transform;
}

// ✓ BEST - Assign in Inspector
[SerializeField] private Transform player;

private void Update()
{
    if (player != null)
        transform.LookAt(player);
}
```

### Pitfall 6: Repeated GetComponent Calls

```csharp
// ❌ BAD - Multiple GetComponent calls for same component
private void ProcessEnemy(GameObject enemy)
{
    if (enemy.GetComponent<Health>() != null)
    {
        enemy.GetComponent<Health>().TakeDamage(10);

        if (enemy.GetComponent<Health>().IsDead())
        {
            enemy.GetComponent<Health>().PlayDeathAnimation();
        }
    }
}

// ✓ GOOD - Cache component result
private void ProcessEnemy(GameObject enemy)
{
    if (enemy.TryGetComponent<Health>(out var health))
    {
        health.TakeDamage(10);

        if (health.IsDead())
        {
            health.PlayDeathAnimation();
        }
    }
}
```

## Quick Reference

### Component Access Speed (Fast → Slow)

1. ✓ Cached reference (Awake/Start)
2. ✓ `TryGetComponent`
3. ✓ `GetComponent`
4. ⚠️ `GetComponentInChildren` (use once in Start)
5. ⚠️ `GetComponentInParent` (use once in Start)
6. ❌ `FindObjectOfType` (avoid in Update)
7. ❌ `Find` with string (avoid always)

### Always Cache These

- `GetComponent` results
- `GetComponentInChildren` results
- `GetComponentInParent` results
- `FindObjectOfType` results
- Transform references
- Rigidbody, Collider, Renderer, etc.

### Use List Overloads For

- `GetComponents<T>(List<T>)`
- `GetComponentsInChildren<T>(List<T>)`
- `GetComponentsInParent<T>(List<T>)`

### Prefer TryGetComponent When

- Component might not exist
- Checking colliding objects
- Optional functionality
- Avoiding null checks

## Summary

**Golden Rules:**

1. **Cache everything** in Awake/Start
2. **Never call GetComponent** in Update/FixedUpdate/LateUpdate
3. **Use TryGetComponent** when component might not exist
4. **Use RequireComponent** for mandatory components
5. **Use List overloads** to avoid garbage collection
6. **Avoid Find methods** except at initialization
7. **Assign in Inspector** when possible
8. **Always null-check** GetComponent results

Remember: Every GetComponent call has overhead. Cache aggressively for best performance!
