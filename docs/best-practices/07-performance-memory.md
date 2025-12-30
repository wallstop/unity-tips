# Unity Performance & Memory Best Practices

## What Problem Does This Solve?

**The Problem:** Your game runs smoothly at 60 FPS most of the time, but every few seconds it
freezes for 50-100ms. Players notice. Reviews mention "stuttering."

**Why This Happens:** C#'s garbage collector (GC) periodically stops your game to clean up unused
memory. Every `new` allocation in `Update()` creates garbage. With 60 FPS, that's 60 allocations per
second, 3,600 per minute. Eventually, GC kicks in and freezes your game.

**Performance Impact:**

- Small GC collection: 5-20ms freeze
- Large GC collection: 50-200ms freeze
- On mobile: 100-500ms freeze
- **Result:** Visible stuttering, bad reviews, frustrated players

**Example:**

```csharp
// ❌ This innocent-looking code creates 3600 allocations per minute
void Update()
{
    string message = "Score: " + score;  // 60 allocations/sec
    healthText.text = message;
}
```

**The Solution:** Eliminate allocations in frequently-called code (Update, FixedUpdate) through
object pooling, caching, and avoiding string operations.

---

## ⚠️ Critical Rules

**The biggest performance killers:**

1. String concatenation in Update/FixedUpdate
2. Camera.main or FindObjectOfType in loops
3. Instantiate/Destroy instead of object pooling
4. Boxing allocations from foreach on Unity collections
5. Not using StringBuilder for repeated string operations

## Table of Contents

- [Garbage Collection Basics](#garbage-collection-basics)
- [Common Allocation Sources](#common-allocation-sources)
- [String Operations](#string-operations)
- [Unity-Specific Optimizations](#unity-specific-optimizations)
- [Best Practices](#best-practices)
- [Common Pitfalls](#common-pitfalls)

## Garbage Collection Basics

### What is Garbage Collection?

When you create objects in C#, they allocate memory. Garbage Collection (GC) is when Unity pauses
your game to clean up unused memory.

```
Normal gameplay:  ████████████████████
GC happens:       ████▓▓████████▓▓████
                       ↑ Stutter  ↑ Stutter

▓▓ = Garbage collection pause (can cause frame drops!)
```

### Why It Matters

```csharp
// ❌ Creates garbage every frame!
private void Update()
{
    string message = "Health: " + health; // Allocates memory
    // After enough allocations, GC runs = frame stutter
}

// After 1000 frames:
// - 1000 string allocations
// - GC kicks in
// - Game stutters for 10-50ms
// - Players notice lag spike
```

**Goal**: Minimize allocations, especially in frequently-called code!

## Common Allocation Sources

### 1. String Concatenation

```csharp
// ❌ TERRIBLE - Allocates every frame
private void Update()
{
    string text = "Score: " + score; // Allocation!
    uiText.text = "Health: " + health + "/" + maxHealth; // Multiple allocations!
}

// ✓ GOOD - Use StringBuilder for repeated operations
private StringBuilder sb = new StringBuilder();

private void UpdateUI()
{
    sb.Clear();
    sb.Append("Health: ");
    sb.Append(health);
    sb.Append("/");
    sb.Append(maxHealth);
    uiText.text = sb.ToString(); // Only one allocation
}

// ✓ BETTER - Only update when values change
private int lastHealth = -1;

private void Update()
{
    if (health != lastHealth)
    {
        uiText.text = $"Health: {health}/{maxHealth}"; // Infrequent allocation OK
        lastHealth = health;
    }
}

// ✓ BEST - Cache formatted strings
private readonly Dictionary<int, string> _healthText = new();

private void OnHealthChanged(int newHealth)
{
    if (!_healthText.TryGetValue(newHealth, out string cachedString))
    {
        cachedString = $"Health: {newHealth}/{maxHealth}";
        _healthText[newHealth] = cachedString;
    }
    uiText.text = cachedString;
}
```

### 2. Boxing Allocations

```csharp
// ❌ BAD - Boxing allocates!
private void PrintValue(object value) // object = boxing
{
    Debug.Log(value);
}

private void Update()
{
    PrintValue(42); // int boxed to object = allocation!
}

// ✓ GOOD - Use generics (no boxing)
private void PrintValue<T>(T value)
{
    Debug.Log(value);
}

private void Update()
{
    PrintValue(42); // No boxing, no allocation!
}
```

### 3. LINQ Allocations

```csharp
// ❌ TERRIBLE - LINQ allocates on every call!
private void Update()
{
    var activeEnemies = enemies.Where(e => e.isActive).ToList(); // Allocation!
    var closestEnemy = enemies.OrderBy(e => Vector3.Distance(transform.position, e.transform.position)).First(); // Multiple allocations!
}

// ✓ GOOD - Manual loops (no allocations)
private void Update()
{
    // Count active enemies
    int activeCount = 0;
    foreach (var enemy in enemies)
    {
        if (enemy.isActive)
            activeCount++;
    }

    // Find closest enemy
    Enemy closest = null;
    float minDistance = float.MaxValue;

    foreach (var enemy in enemies)
    {
        float dist = Vector3.Distance(transform.position, enemy.transform.position);
        if (dist < minDistance)
        {
            minDistance = dist;
            closest = enemy;
        }
    }
}
```

### 4. Array/List Allocations

```csharp
// ❌ BAD - Creates new array every frame
private void Update()
{
    Collider[] hits = Physics.OverlapSphere(transform.position, radius); // Allocation!
}

// ✓ GOOD - Reuse array with NonAlloc variant
private Collider[] hitResults = new Collider[50];

private void Update()
{
    int hitCount = Physics.OverlapSphereNonAlloc(transform.position, radius, hitResults);

    for (int i = 0; i < hitCount; i++)
    {
        ProcessHit(hitResults[i]);
    }
}

// ✓ ALSO GOOD - Use List and Clear()
private List<Collider> reusableList = new List<Collider>(50);

private void GatherNearbyObjects()
{
    reusableList.Clear(); // Clears list but keeps capacity

    foreach (var obj in allObjects)
    {
        if (IsNearby(obj))
            reusableList.Add(obj);
    }
}
```

### 5. Unity GetComponents

```csharp
// ❌ BAD - Allocates array
private void Update()
{
    Collider[] colliders = GetComponents<Collider>(); // Allocation every frame!
}

// ✓ GOOD - Use List overload (reusable)
private List<Collider> colliderList = new List<Collider>();

private void Start()
{
    GetComponents<Collider>(colliderList); // Populate once
}

// If list content changes, refresh it:
private void RefreshColliders()
{
    colliderList.Clear();
    GetComponents<Collider>(colliderList); // Reuses list, no new allocation
}
```

## String Operations

### The String Problem

```csharp
// Why strings are expensive:
string a = "Hello";
string b = "World";
string c = a + b; // Creates NEW string, old strings become garbage

// Every concatenation = new allocation!
string result = "";
for (int i = 0; i < 100; i++)
{
    result += i.ToString(); // 100 allocations!
}
```

### String Builder Solution

```csharp
// ✓ CORRECT - StringBuilder for repeated operations
private StringBuilder sb = new StringBuilder(256); // Pre-allocate capacity

private string BuildMessage()
{
    sb.Clear(); // Reuse same StringBuilder

    sb.Append("Player: ");
    sb.Append(playerName);
    sb.Append(" | Level: ");
    sb.Append(level);
    sb.Append(" | XP: ");
    sb.Append(currentXP);
    sb.Append("/");
    sb.Append(maxXP);

    return sb.ToString(); // One allocation for final string
}
```

### String Caching

```csharp
// ✓ Cache common strings
private class StringCache
{
    public static readonly string Empty = string.Empty;
    public static readonly string NewLine = "\n";
    public static readonly string Space = " ";

    // Cache formatted strings
    private static Dictionary<int, string> numberStrings = new Dictionary<int, string>();

    public static string GetNumber(int num)
    {
        if (!numberStrings.ContainsKey(num))
            numberStrings[num] = num.ToString();

        return numberStrings[num];
    }
}

// Usage
text.text = StringCache.GetNumber(score); // Cached!
```

### String Comparison

```csharp
// ❌ SLOW - Creates garbage and slow
if (tagName == "Player") { }

// ✓ FAST - No allocation, optimized
if (CompareTag("Player")) { }
```

## Unity-Specific Optimizations

### 1. Camera.main

```csharp
// ❌ VERY SLOW - FindGameObjectWithTag every call!
private void Update()
{
    Vector3 toCamera = Camera.main.transform.position - transform.position;
}

// ✓ FAST - Cache it
private Camera mainCamera;

private void Start()
{
    mainCamera = Camera.main; // Find once
}

private void Update()
{
    Vector3 toCamera = mainCamera.transform.position - transform.position;
}
```

### 2. Transform Access

```csharp
// ⚠️ INEFFICIENT - Property call overhead (calls out to Unity C++ engine)
private void Update()
{
    transform.position = Vector3.zero;
    transform.rotation = Quaternion.identity;
    transform.localScale = Vector3.one;
}

// ✓ BETTER - Cache transform reference
private Transform tr;

private void Awake()
{
    tr = transform;
}

private void Update()
{
    tr.position = Vector3.zero;
    tr.rotation = Quaternion.identity;
    tr.localScale = Vector3.one;
}

// Note: Modern Unity caches transform internally, but explicit caching
// still helps with readability and avoiding repeated property access
```

### 3. Find Operations

```csharp
// ❌ CATASTROPHIC - Searches entire scene every frame!
private void Update()
{
    GameObject player = GameObject.Find("Player");
    GameObject enemy = GameObject.FindGameObjectWithTag("Enemy");
    GameManager gm = FindObjectOfType<GameManager>();
}

// ✓ CORRECT - Find once, cache forever
private GameObject player;
private GameObject enemy;
private GameManager gm;

private void Start()
{
    player = GameObject.Find("Player");
    enemy = GameObject.FindGameObjectWithTag("Enemy");
    gm = FindObjectOfType<GameManager>();
}

// ✓ BEST - Assign in Inspector (no runtime searching)
[SerializeField] private GameObject player;
[SerializeField] private GameObject enemy;
[SerializeField] private GameManager gm;
```

### 4. Physics Queries

```csharp
// ❌ BAD - Allocates array
Collider[] hits = Physics.OverlapSphere(pos, radius);

// ✓ GOOD - Reuse array
private Collider[] hitBuffer = new Collider[10];

private void CheckNearby()
{
    int hitCount = Physics.OverlapSphereNonAlloc(pos, radius, hitBuffer);

    for (int i = 0; i < hitCount; i++)
    {
        ProcessHit(hitBuffer[i]);
    }
}
```

### 5. SendMessage vs Direct Calls

```csharp
// ❌ VERY SLOW - Boxing, allocations
gameObject.SendMessage("TakeDamage", 10);

// ✓ FAST - Direct call
Health health = GetComponent<Health>();
if (health != null)
    health.TakeDamage(10);

// ✓ FASTER - Cached component
private Health cachedHealth;

private void Awake()
{
    cachedHealth = GetComponent<Health>();
}

private void DealDamage()
{
    if (cachedHealth != null)
        cachedHealth.TakeDamage(10);
}
```

## Best Practices

### 1. Cache Everything

```csharp
public class CachedReferences : MonoBehaviour
{
    // Cache components
    private Transform tr;
    private Rigidbody rb;
    private Renderer rend;

    // Cache references
    private Camera mainCam;
    private GameObject player;
    private GameManager gm;

    // Cache LayerMasks
    private LayerMask enemyLayer;

    private void Awake()
    {
        // Cache once
        tr = transform;
        rb = GetComponent<Rigidbody>();
        rend = GetComponent<Renderer>();

        mainCam = Camera.main;
        player = GameObject.FindGameObjectWithTag("Player");
        gm = FindObjectOfType<GameManager>();

        enemyLayer = LayerMask.GetMask("Enemy");
    }

    private void Update()
    {
        // Use cached references - fast!
        tr.position += Vector3.forward * Time.deltaTime;

        if (Physics.Raycast(mainCam.transform.position, mainCam.transform.forward, 100f, enemyLayer))
        {
            // Hit enemy
        }
    }
}
```

### 2. Use Object Pooling

```csharp
// See best-practices/09-object-pooling.md for full details

// Instead of:
Instantiate(bulletPrefab);
Destroy(bullet, 5f);

// Use:
Bullet bullet = bulletPool.Get();
bulletPool.Release(bullet); // when done
```

### 3. Avoid Update When Possible

```csharp
// ❌ WASTEFUL - Runs every frame even when nothing changes
private void Update()
{
    if (Input.GetKeyDown(KeyCode.Space))
        Jump();
}

// ✓ BETTER - Use events/coroutines when appropriate
private void OnEnable()
{
    InputManager.OnJumpPressed += Jump;
}

private void OnDisable()
{
    InputManager.OnJumpPressed -= Jump;
}
```

### 4. Batch Operations

```csharp
// ❌ INEFFICIENT - Multiple iterations
foreach (var enemy in enemies)
    enemy.UpdateAI();

foreach (var enemy in enemies)
    enemy.UpdateMovement();

foreach (var enemy in enemies)
    enemy.UpdateAnimation();

// ✓ EFFICIENT - Single iteration
foreach (var enemy in enemies)
{
    enemy.UpdateAI();
    enemy.UpdateMovement();
    enemy.UpdateAnimation();
}
```

### 5. Use Structs for Small Data

```csharp
// ✓ GOOD - Value type, no allocation
public struct Damage
{
    public int amount;
    public DamageType type;
    public Vector3 hitPoint;
}

// Passing struct = copy, no allocation
public void TakeDamage(Damage damage) { }

// ⚠️ Classes allocate when created
public class DamageInfo
{
    public int amount;
    public DamageType type;
}

// This allocates:
TakeDamage(new DamageInfo { amount = 10, type = DamageType.Fire });
```

## Common Pitfalls

### Pitfall 1: String Concatenation in Update

```csharp
// ❌ TERRIBLE - 60 allocations per second at 60fps!
private void Update()
{
    debugText.text = "FPS: " + (1f / Time.deltaTime).ToString("F1");
}

// ✓ BETTER - Update less frequently
private float updateInterval = 0.2f;
private float updateTimer = 0f;

private void Update()
{
    updateTimer += Time.deltaTime;

    if (updateTimer >= updateInterval)
    {
        updateTimer = 0f;
        debugText.text = $"FPS: {(1f / Time.deltaTime):F1}";
    }
}

// ✓ BEST - Use StringBuilder + update only when needed
private StringBuilder sb = new StringBuilder();
private float lastFPS = 0f;

private void Update()
{
    float currentFPS = 1f / Time.deltaTime;

    if (Mathf.Abs(currentFPS - lastFPS) > 1f) // Only update if changed significantly
    {
        sb.Clear();
        sb.Append("FPS: ");
        sb.Append(currentFPS.ToString("F1"));
        debugText.text = sb.ToString();
        lastFPS = currentFPS;
    }
}
```

### Pitfall 2: Foreach on Unity Collections

```csharp
// ⚠️ ALLOCATES - Unity's Transform.GetEnumerator allocates!
foreach (Transform child in transform)
{
    child.gameObject.SetActive(false);
}

// ✓ NO ALLOCATION - Use for loop
for (int i = 0; i < transform.childCount; i++)
{
    transform.GetChild(i).gameObject.SetActive(false);
}
```

### Pitfall 3: Closure Allocations

```csharp
// ❌ ALLOCATES - Captures local variable
private void Update()
{
    int value = 42;
    button.onClick.AddListener(() => Debug.Log(value)); // Allocation!
}

// ✓ NO ALLOCATION - Use cached delegate
private UnityAction cachedDelegate;

private void Start()
{
    cachedDelegate = OnButtonClick;
    button.onClick.AddListener(cachedDelegate);
}

private void OnButtonClick()
{
    Debug.Log("Clicked!");
}
```

### Pitfall 4: GetComponent in Update

```csharp
// ❌ EXTREMELY SLOW
private void Update()
{
    GetComponent<Rigidbody>().AddForce(Vector3.up);
}

// ✓ CACHE IT
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

### Pitfall 5: Unnecessary Null Checks

```csharp
// ❌ WASTEFUL - Repeated null checks
private void Update()
{
    if (player != null && player.IsAlive)
    {
        // Check every frame even though player never changes
    }
}

// ✓ BETTER - Cache result when it changes
private bool shouldUpdate = false;

private void OnPlayerStateChanged()
{
    shouldUpdate = player != null && player.IsAlive;
}

private void Update()
{
    if (shouldUpdate)
    {
        // Faster!
    }
}
```

### Pitfall 6: LINQ in Hot Paths

```csharp
// ❌ TERRIBLE - LINQ + boxing + allocations
private void Update()
{
    var average = enemies.Average(e => e.health); // Multiple allocations!
    var sorted = enemies.OrderBy(e => e.distance).ToList(); // Even more!
}

// ✓ GOOD - Manual calculation
private void Update()
{
    float sum = 0f;
    foreach (var enemy in enemies)
        sum += enemy.health;

    float average = sum / enemies.Count;
}
```

## Quick Reference

### Always Avoid in Update/FixedUpdate

- ❌ String concatenation (`+` operator)
- ❌ `Camera.main`
- ❌ `Find` / `FindObjectOfType`
- ❌ `GetComponent` (cache instead)
- ❌ LINQ queries
- ❌ Boxing (use generics)
- ❌ `new` for objects (use pooling)
- ❌ Physics queries without NonAlloc

### Always Do

- ✓ Cache references in Awake/Start
- ✓ Use StringBuilder for repeated string operations
- ✓ Use object pooling for frequent Instantiate/Destroy
- ✓ Use NonAlloc variants of Physics methods
- ✓ Use `for` instead of `foreach` on Unity collections
- ✓ Update only when values change
- ✓ Use CompareTag instead of `==` for tags

### Profiling

**Always profile before optimizing!**

- Unity Profiler (Window → Analysis → Profiler)
- Look for "GC.Alloc" in profiler
- Check frame time and GC spikes
- Profile on target platform (mobile is different from PC!)

## Summary

**Golden Rules:**

1. **Cache everything** - Components, references, cameras
2. **Avoid allocations in hot paths** - Update, FixedUpdate, coroutines
3. **Use StringBuilder** for repeated string operations
4. **Use object pooling** for frequently created objects
5. **Use NonAlloc variants** for Physics queries
6. **Avoid LINQ** in performance-critical code
7. **Profile before optimizing** - Don't guess!

**Performance Priority:**

```
1. Make it work
2. Make it clean
3. Profile it
4. Make it fast (if needed)
```

**Remember**: Premature optimization is the root of all evil. Profile first, optimize what matters!
