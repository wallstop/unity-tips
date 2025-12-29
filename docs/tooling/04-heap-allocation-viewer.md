# Heap Allocation Viewer | Catch GC Hotspots

Heap Allocations Viewer (Rider/ReSharper plugin) highlights every managed allocation that your C#
code would trigger at runtime. For Unity projects, that means you can spot `new` allocations,
boxing, closures, and LINQ calls inside per-frame code before they ever hit players.

## Why Update-loop allocations hurt

`Update()` can execute 30–120 times per second on every active `MonoBehaviour`. Even a few bytes of
transient heap memory per frame per object snowball into megabytes each minute. The .NET/Mono GC
then has to pause the main thread to reclaim that memory:

- **Frame drops & stutter** – GC collections stop the Unity player thread, so frequent collections
  show up as hitching and input lag.
- **Mobile impact** – Mobile CPUs are slower and often thermally throttled, so GC spikes are longer
  and more noticeable.
- **Background systems** – Allocations in AI, pathfinding, combat logs, or UI updates all add up
  when they run every frame.

Catching allocations as you type is the cheapest way to avoid these problems.

## Install in JetBrains Rider (Unity Hub default)

1. Open `File → Settings…` (`Ctrl+,` / `Cmd+,`).
2. Navigate to `Plugins → Marketplace` and search for **Heap Allocations Viewer**.
3. Click **Install**, then restart Rider.

> ✅ The plugin ships with the Unity/Rider integration, but installing it explicitly guarantees you
> have the latest version.

## Install in Visual Studio + ReSharper

1. Open `Extensions → ReSharper → Extension Manager…`.
2. Search for **Heap Allocations Viewer** (ID: `com.jetbrains.resharper.heapview`).
3. Install and restart Visual Studio.

## Configure “yell-at-me” highlighting

### Rider / IntelliJ-based IDEs

1. `File → Settings… → Editor → Inspections → C# → Performance`.
2. Set **Heap allocation (from Heap Allocations Viewer)** to **Error** severity so it stands out.
3. While still focused on the inspection, use the gear icon → **Edit Highlighting in Editor** to:
   - Change the effect to **Solid underline** or **Wavy underline**.
   - Enable **Bold** and **Italic** font styles to make the offending call sites scream.
4. Apply and restart if prompted.

You can further adjust colors at `Settings → Editor → Color Scheme → Inspections → Heap allocation`.

### Visual Studio + ReSharper

1. `Extensions → ReSharper → Options… → Code Inspection → Inspection Severity`.
2. Locate **Heap allocation** and change severity to **Error**.
3. Open `Tools → Options → Environment → Fonts and Colors`.
4. Filter the display items list for **ReSharper Heap Allocation** entries and set:
   - **Font style:** Bold + Italic.
   - **Item foreground:** attention-grabbing color (e.g., red/orange).
   - **Display items effect:** Single underline.

## What gets flagged

- Object, array, and delegate creation via `new`.
- Boxing conversions (e.g., assigning a struct to `object`, `string.Format` with value types).
- Captures that allocate hidden closure classes (lambdas, local functions).
- LINQ queries and iterator blocks that generate enumerator objects.
- `foreach` loops over value types that trigger boxing.

Hovering the underline shows a tooltip describing the exact allocation so you can refactor (pool the
object, reuse a struct, move work out of `Update()`, etc.).

## Workflow tips

- Audit per-frame methods (`Update`, `FixedUpdate`, `LateUpdate`, UI `OnValueChanged`) regularly—the
  plugin highlights issues instantly.
- Pair with Unity's **Profile Analyzer** or **Timeline** to confirm GC spikes disappeared after
  refactors.
- Remember that some allocations are unavoidable; add a code comment when you intentionally keep one
  so future reviewers know it was a conscious trade-off.

Proactively catching allocations keeps your frame time flat and your players happy—especially on
mobile hardware with limited CPU headroom.

---

## 🎯 Before & After Examples

### Example 1: String Concatenation in Update

#### ❌ BEFORE (Allocates Every Frame)

```csharp
public class ScoreUI : MonoBehaviour
{
    public Text scoreText;
    private int score = 0;

    void Update()
    {
        // Heap Allocation Viewer highlights this line
        // "String concatenation allocates new string"
        scoreText.text = "Score: " + score.ToString();
        // ⚠️ At 60 FPS: 60 allocations/second = GC collection every few seconds
    }
}
```

**Problem:** Creates new string objects 60+ times per second, triggering GC pauses.

#### ✅ AFTER (Zero Allocations)

```csharp
public class ScoreUI : MonoBehaviour
{
    public Text scoreText;
    private int _score = 0;

    public int Score
    {
        get => _score;
        set
        {
            if (_score != value)
            {
                _score = value;
                // Only update when score changes
                scoreText.text = $"Score: {_score}";
            }
        }
    }

    // Update() removed entirely—no per-frame cost!
}
```

**Result:** No warnings from Heap Allocation Viewer, zero GC spikes.

---

### Example 2: LINQ in Hot Path

#### ❌ BEFORE (Major Allocations)

```csharp
public class EnemyManager : MonoBehaviour
{
    public List<Enemy> enemies = new List<Enemy>();

    void Update()
    {
        // Heap Allocation Viewer flags all of these:
        // 1. Lambda captures "this" → closure allocation
        // 2. LINQ creates enumerator → IEnumerable allocation
        // 3. ToList() → new List allocation
        var aliveEnemies = enemies.Where(e => e.Health > 0).ToList();

        // More LINQ allocations
        var nearbyEnemies = enemies.Where(e => Vector3.Distance(e.transform.position, player.position) < 10f);

        // ⚠️ At 60 FPS with 100 enemies: massive GC pressure
    }
}
```

**Problem:** LINQ creates iterators and captures closures, allocating multiple objects per frame.

#### ✅ AFTER (Zero Allocations)

```csharp
public class EnemyManager : MonoBehaviour
{
    public List<Enemy> enemies = new List<Enemy>();
    private List<Enemy> _aliveEnemies = new List<Enemy>(100);  // Pre-allocate
    private List<Enemy> _nearbyEnemies = new List<Enemy>(100);

    void Update()
    {
        // No warnings! Manual filtering reuses lists
        _aliveEnemies.Clear();  // Clear instead of new
        for (int i = 0; i < enemies.Count; i++)
        {
            if (enemies[i].Health > 0)
            {
                _aliveEnemies.Add(enemies[i]);
            }
        }

        _nearbyEnemies.Clear();
        for (int i = 0; i < _aliveEnemies.Count; i++)
        {
            float distance = Vector3.Distance(_aliveEnemies[i].transform.position, player.position);
            if (distance < 10f)
            {
                _nearbyEnemies.Add(_aliveEnemies[i]);
            }
        }

        // Use _aliveEnemies and _nearbyEnemies...
    }
}
```

**Result:** Zero allocations per frame. Lists are reused instead of recreated.

---

### Example 3: Boxing Value Types

#### ❌ BEFORE (Hidden Boxing)

```csharp
public class CombatLogger : MonoBehaviour
{
    void OnDamageDealt(int damage, float multiplier)
    {
        // Heap Allocation Viewer flags this:
        // "Boxing allocation: int → object"
        // "Boxing allocation: float → object"
        Debug.Log($"Dealt {damage} damage with {multiplier}x multiplier");

        // Worse: string.Format boxes everything
        string message = string.Format("Dealt {0} damage", damage);

        // Even worse: Unity's old string concatenation
        Debug.Log("Damage: " + damage);  // Boxing!
    }
}
```

**Problem:** String interpolation/format boxes value types into objects.

#### ✅ AFTER (No Boxing)

```csharp
public class CombatLogger : MonoBehaviour
{
    // Option 1: Only log when needed (not every frame)
    void OnDamageDealt(int damage, float multiplier)
    {
        // Acceptable if not called 60 times/second
        Debug.Log($"Dealt {damage} damage with {multiplier}x multiplier");
    }

    // Option 2: Cache strings for common values
    private readonly Dictionary<int, string> _damageStrings = new Dictionary<int, string>
    {
        { 10, "10" },
        { 25, "25" },
        { 50, "50" },
        { 100, "100" }
    };

    void OnDamageDealtOptimized(int damage)
    {
        if (_damageStrings.TryGetValue(damage, out string cached))
        {
            Debug.Log("Damage: " + cached);  // No boxing, reuses string
        }
        else
        {
            Debug.Log($"Damage: {damage}");  // Rare case, acceptable
        }
    }

    // Option 3: Use StringBuilder for repeated operations
    private readonly StringBuilder _sb = new StringBuilder(128);

    void OnDamageDealtStringBuilder(int damage, float multiplier)
    {
        _sb.Clear();
        _sb.Append("Dealt ");
        _sb.Append(damage);
        _sb.Append(" damage with ");
        _sb.Append(multiplier);
        _sb.Append("x multiplier");

        Debug.Log(_sb.ToString());  // Single allocation for final string
    }
}
```

**Result:** Heap Allocation Viewer quiet, no boxing warnings.

---

### Example 4: Closure Allocations

#### ❌ BEFORE (Lambda Creates Closure)

```csharp
public class UIManager : MonoBehaviour
{
    public Button startButton;
    private int _level = 1;

    void Start()
    {
        // Heap Allocation Viewer warns:
        // "Lambda captures 'this' → allocates closure object"
        startButton.onClick.AddListener(() =>
        {
            LoadLevel(_level);  // Captures '_level' from 'this'
        });

        // Each button creates a new closure
        for (int i = 0; i < 5; i++)
        {
            // WARNING: Captures loop variable 'i' (and it's always 5 anyway!)
            CreateButton(i, () => Debug.Log($"Clicked button {i}"));
        }
    }

    void CreateButton(int index, Action onClick) { /* ... */ }
    void LoadLevel(int level) { /* ... */ }
}
```

**Problem:** Lambdas that capture variables allocate closure objects.

#### ✅ AFTER (No Closures)

```csharp
public class UIManager : MonoBehaviour
{
    public Button startButton;
    private int _level = 1;

    void Start()
    {
        // No warning! Method group doesn't capture anything
        startButton.onClick.AddListener(OnStartButtonClicked);

        // For parameterized callbacks, use a helper class
        for (int i = 0; i < 5; i++)
        {
            int buttonIndex = i;  // Capture loop variable correctly
            CreateButton(buttonIndex, new ButtonClickHandler(this, buttonIndex).OnClick);
        }
    }

    private void OnStartButtonClicked()
    {
        LoadLevel(_level);  // Direct method, no closure
    }

    void CreateButton(int index, Action onClick) { /* ... */ }
    void LoadLevel(int level) { /* ... */ }

    // Helper to avoid closure allocation
    private class ButtonClickHandler
    {
        private UIManager _manager;
        private int _index;

        public ButtonClickHandler(UIManager manager, int index)
        {
            _manager = manager;
            _index = index;
        }

        public void OnClick()
        {
            Debug.Log($"Clicked button {_index}");
            // Access _manager as needed
        }
    }
}
```

**Alternative (Simpler):** Use UnityEvents with parameters in Inspector instead of code.

---

## ✅ Dos and ❌ Don'ts

### ✅ DO

```csharp
// ✅ Cache strings used repeatedly
private const string PLAYER_TAG = "Player";  // No allocation
if (other.CompareTag(PLAYER_TAG)) { /* ... */ }

// ✅ Reuse collections instead of creating new ones
private List<Enemy> _tempList = new List<Enemy>(100);
void Update()
{
    _tempList.Clear();  // Reuse, don't allocate
    // Fill _tempList...
}

// ✅ Use object pooling for frequent spawns
private ObjectPool<Bullet> _bulletPool;  // See Unity Best Practices

// ✅ Use direct method references instead of lambdas
button.onClick.AddListener(OnButtonClicked);  // No closure

// ✅ Comment intentional allocations
void LoadLevel()
{
    // Intentional allocation: happens once per level, not per-frame
    var config = new LevelConfig { /* ... */ };
}
```

### ❌ DON'T

```csharp
// ❌ Don't use LINQ in Update()
void Update()
{
    var alive = enemies.Where(e => e.Health > 0).ToList();  // Allocates!
}

// ❌ Don't concatenate strings in hot paths
void Update()
{
    text.text = "Score: " + score;  // 60 allocations/second!
}

// ❌ Don't call GetComponent every frame
void Update()
{
    GetComponent<Rigidbody>().AddForce(Vector3.up);  // Allocates AND slow!
}

// ❌ Don't create closures in frequent callbacks
for (int i = 0; i < 100; i++)
{
    buttons[i].onClick.AddListener(() => OnClick(i));  // 100 closures!
}

// ❌ Don't ignore warnings in Update/FixedUpdate
void Update()
{
    // "I'll optimize later" = technical debt
    DoThingWithAllocations();  // Fix now!
}
```

---

## 🔧 Troubleshooting

### Problem: "Warnings everywhere, overwhelming!"

**Solution:** Focus on high-impact areas first:

1. **Start with per-frame methods:**

   - `Update()`, `FixedUpdate()`, `LateUpdate()`
   - UI callbacks that fire repeatedly (`OnValueChanged`, `OnPointerEnter`)

2. **Ignore initialization code:**

   - `Awake()`, `Start()` allocations are usually fine
   - Level loading, one-time setup

3. **Use "Find Usages" to prioritize:**
   - Fix allocations in methods called 100+ times
   - Ignore allocations in rarely-called methods

**Configure Rider to show only errors:**

```
Settings → Inspections → Heap allocation
Change severity to "Error" only for:
- "Closure allocation"
- "Object allocation (foreach loop)"
- "Delegate allocation"
```

### Problem: "False positives on async/await"

**Cause:** Async methods always allocate state machines—this is expected.

**Solution:**

```csharp
// This will always warn, it's unavoidable
private async Task LoadDataAsync()
{
    // State machine allocation is necessary
    await Task.Delay(1000);
}

// If in hot path, use coroutines instead
private IEnumerator LoadDataCoroutine()
{
    yield return new WaitForSeconds(1f);
    // Better for Unity, less allocations if managed properly
}
```

**Rule:** Async is fine for one-time operations (level load, network). Use coroutines for frequent
operations (animations, timers).

### Problem: "Warning on foreach with List<T>"

**Cause:** Old Rider versions warned about `foreach` allocations.

**Solution:**

```csharp
// Rider warns about foreach enumerator allocation
foreach (var enemy in enemies) { }  // Old C# versions allocate

// Modern C# (.NET Core 2.1+) doesn't allocate for List<T>
// Unity 2021+ supports this optimization

// If on older Unity, use for loop:
for (int i = 0; i < enemies.Count; i++)
{
    var enemy = enemies[i];
    // No allocation
}
```

**Check Unity version:**

- Unity 2021+: `foreach` on `List<T>` is allocation-free
- Unity 2020 and earlier: Use `for` loops

### Problem: "How do I confirm allocations are gone?"

**Solution:** Use Unity Profiler:

1. **Before fix:**

   ```csharp
   void Update()
   {
       var list = enemies.Where(e => e.Health > 0).ToList();
   }
   ```

   - Open Unity Profiler (Window → Analysis → Profiler)
   - Record while playing
   - Check "GC.Alloc" samples—should see spikes

1. **After fix:**

   ```csharp
   private List<Enemy> _alive = new List<Enemy>();
   void Update()
   {
       _alive.Clear();
       for (int i = 0; i < enemies.Count; i++)
       {
           if (enemies[i].Health > 0) _alive.Add(enemies[i]);
       }
   }
   ```

   - Profiler shows zero "GC.Alloc" in Update()

1. **Measure GC frequency:**
   - Tools → Profile Analyzer
   - Compare before/after
   - GC collections should drop from multiple per second to rare

---

## 🎯 Common Scenarios

### Scenario: Optimizing inventory UI

**Problem:** Updating 100 item slots causes frame drops

```csharp
// BEFORE: Allocates 100+ strings per frame
public class InventoryUI : MonoBehaviour
{
    public Text[] itemTexts;

    void Update()
    {
        for (int i = 0; i < itemTexts.Length; i++)
        {
            itemTexts[i].text = "Qty: " + inventory.GetQuantity(i);  // Allocates!
        }
    }
}
```

**Solution:**

```csharp
// AFTER: Zero allocations, only update on change
public class InventoryUI : MonoBehaviour
{
    public Text[] itemTexts;
    private int[] _cachedQuantities;

    void Awake()
    {
        _cachedQuantities = new int[itemTexts.Length];
    }

    void Update()
    {
        for (int i = 0; i < itemTexts.Length; i++)
        {
            int quantity = inventory.GetQuantity(i);
            if (_cachedQuantities[i] != quantity)
            {
                _cachedQuantities[i] = quantity;
                itemTexts[i].text = $"Qty: {quantity}";  // Only when changed
            }
        }
    }
}
```

**Better:** Use events instead of polling:

```csharp
public class InventoryUI : MonoBehaviour
{
    void Start()
    {
        inventory.OnItemChanged += OnInventoryChanged;
    }

    void OnInventoryChanged(int slotIndex, int newQuantity)
    {
        // Only update the specific slot that changed
        itemTexts[slotIndex].text = $"Qty: {newQuantity}";
    }

    void OnDestroy()
    {
        inventory.OnItemChanged -= OnInventoryChanged;
    }
}
```

### Scenario: Particle system with dynamic text

**Problem:** Damage numbers create GC spikes

```csharp
// BEFORE: Each damage number allocates
void ShowDamage(int amount, Vector3 position)
{
    var obj = Instantiate(damageTextPrefab, position, Quaternion.identity);
    obj.GetComponent<Text>().text = amount.ToString();  // Boxing + string allocation
    Destroy(obj, 1f);  // Creates 100s of objects
}
```

**Solution:**

```csharp
// AFTER: Object pool + cached strings
private ObjectPool<DamageText> _damagePool;
private readonly string[] _cachedNumbers = new string[1000];  // Cache 0-999

void Awake()
{
    // Pre-cache common damage values
    for (int i = 0; i < _cachedNumbers.Length; i++)
    {
        _cachedNumbers[i] = i.ToString();
    }

    _damagePool = new ObjectPool<DamageText>(
        createFunc: () => Instantiate(damageTextPrefab),
        actionOnGet: (obj) => obj.gameObject.SetActive(true),
        actionOnRelease: (obj) => obj.gameObject.SetActive(false),
        defaultCapacity: 50
    );
}

void ShowDamage(int amount, Vector3 position)
{
    var damageText = _damagePool.Get();
    damageText.transform.position = position;

    // Use cached string if available, else format
    damageText.text = (amount < _cachedNumbers.Length)
        ? _cachedNumbers[amount]
        : amount.ToString();

    StartCoroutine(ReturnToPoolAfterDelay(damageText, 1f));
}

IEnumerator ReturnToPoolAfterDelay(DamageText obj, float delay)
{
    yield return new WaitForSeconds(delay);
    _damagePool.Release(obj);
}
```

**Result:** Zero allocations for common damage values, smooth particle effects.

---

## 📚 Learn More

- [Unity Manual: Memory Management](https://docs.unity3d.com/Manual/performance-memory-overview.html)
- [Heap Allocations Viewer Plugin](https://plugins.jetbrains.com/plugin/9223-heap-allocations-viewer)
- [Unity Best Practices: Performance & Memory](../best-practices/07-performance-memory.md)
- [Unity Best Practices: Object Pooling](../best-practices/09-object-pooling.md)
