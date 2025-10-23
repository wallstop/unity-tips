# Unity ScriptableObjects Best Practices

> **Looking for Event Systems?** See [Event Systems Comparison](./10-event-systems.md) for details.

## What Problem Does This Solve?

**The Problem:** You have 50 enemy types. Each enemy MonoBehaviour stores its own stats (health,
damage, speed). To change goblin health from 50 to 60, you must update 50 prefabs in your project.
Designers can't balance the game without programmer help.

**Without ScriptableObjects (The Painful Way):**

```csharp
public class Enemy : MonoBehaviour {
    public int health = 50;      // Duplicated in every enemy prefab
    public int damage = 10;      // Change requires updating all prefabs
    public float speed = 5f;     // 50 prefabs = 50 places to edit
}
```

**Problems:**

- Change goblin health: Edit 50 prefabs
- Add new stat: Edit 50 prefabs
- Designer needs programmer to change values
- Merge conflicts in prefab files

**With ScriptableObjects (The Data-Driven Way):**

```csharp
[CreateAssetMenu]
public class EnemyData : ScriptableObject {
    public int health = 50;
    public int damage = 10;
    public float speed = 5f;
}

public class Enemy : MonoBehaviour {
    public EnemyData data;      // Reference ONE asset
    // All goblins reference "GoblinData" asset
}
```

**Benefits:**

- Change goblin health: Edit ONE asset, all goblins update
- Designer can edit assets directly
- Clean git diffs (data files, not binary prefabs)
- Decouple data from behavior

**The Solution:** ScriptableObjects centralize shared data. Change one asset, update all instances.
Designers can balance without touching prefabs.

---

## What are ScriptableObjects?

ScriptableObjects are data containers that exist independently of scenes and GameObjects. They're
like MonoBehaviours, but for data instead of behavior.

**Primary Use:** ScriptableObjects should primarily be used as **data containers** for shared configuration, databases, and runtime collections. While they can also be used for event systems, see the [Event Systems documentation](./10-event-systems.md) for a comprehensive comparison of different event approaches.

**Simple Analogy**: Think of MonoBehaviours as "actors" (they do things in your scene), and
ScriptableObjects as "recipes" (they hold information that actors can read from).

## Table of Contents

- [When to Use ScriptableObjects](#when-to-use-scriptableobjects)
- [When NOT to Use ScriptableObjects](#when-not-to-use-scriptableobjects)
- [Creating ScriptableObjects](#creating-scriptableobjects)
- [Common Patterns](#common-patterns)
- [Best Practices](#best-practices)
- [Common Pitfalls](#common-pitfalls)

## When to Use ScriptableObjects

ScriptableObjects are perfect for:

### 1. Shared Configuration Data

```csharp
// Instead of this: Settings on every enemy prefab
public class Enemy : MonoBehaviour
{
    public float maxHealth = 100;
    public float moveSpeed = 5f;
    public int damag = 10;
    // If you want to change these, edit EVERY prefab!
}

// Do this: Shared settings asset
[CreateAssetMenu(fileName = "EnemySettings", menuName = "Game/Enemy Settings")]
public class EnemySettings : ScriptableObject
{
    public float maxHealth = 100;
    public float moveSpeed = 5f;
    public int damage = 10;
}

public class Enemy : MonoBehaviour
{
    [SerializeField] private EnemySettings settings;
    // Now all enemies can share one settings asset!
    // Change once, affects all!
}
```

**Use for**: Enemy stats, weapon configurations, game rules, difficulty settings

### 2. Data Tables and Databases

```csharp
// Create a database of items, enemies, spells, etc.
[CreateAssetMenu(menuName = "Game/Item")]
public class ItemData : ScriptableObject
{
    public string itemName;
    public Sprite icon;
    public int value;
    public string description;
}

// Then create one asset for each item
// SwordData, ShieldData, PotionData, etc.
```

**Use for**: Item databases, enemy types, ability definitions, dialogue trees

### 3. Event Systems (Consider Alternatives)

ScriptableObjects can be used for event systems, allowing components to communicate through shared event assets.

> **Note:** While ScriptableObject events are a valid pattern (especially for designer-driven workflows), there are multiple approaches to event systems in Unity, each with different trade-offs. For a comprehensive comparison of ScriptableObject events vs code-driven event buses, see the **[Event Systems documentation](./10-event-systems.md)**.

**Quick Example:**

```csharp
// Basic event ScriptableObject
[CreateAssetMenu(menuName = "Events/Int Event")]
public class IntEvent : ScriptableObject
{
    private event System.Action<int> OnEventRaised;

    public void Raise(int value)
    {
        OnEventRaised?.Invoke(value);
    }

    public void RegisterListener(System.Action<int> listener)
    {
        OnEventRaised += listener;
    }

    public void UnregisterListener(System.Action<int> listener)
    {
        OnEventRaised -= listener;
    }

    private void OnEnable()
    {
        // Clear stale listeners from previous Play Mode
        OnEventRaised = null;
    }
}
```

**When to consider this approach:**
- Designer-driven workflows where non-programmers create game flow
- Animation events triggering prefab logic
- Smaller projects with < 50 event types

### 4. Runtime Sets/Collections ⚠️ (Not Recommended)

> **⚠️ Warning: Using ScriptableObjects for mutable runtime state is generally not recommended.**
>
> ScriptableObjects were designed as **immutable data containers**, not runtime state managers. Using them for mutable data causes several problems:
>
> - **Editor vs Build inconsistency**: Changes persist in Editor between play sessions but reset in builds[^1]
> - **Domain reload issues**: Disabling domain/scene reload causes unpredictable state persistence[^2]
> - **Debugging difficulties**: Hard to trace which scripts modify which ScriptableObjects[^2]
> - **Scalability problems**: Managing many runtime variables as assets becomes unwieldy[^2]
> - **Inspector limitations**: Can't serialize scene objects, causing "Type mismatch" errors[^3]
>
> **Better alternatives:**
> - Use regular C# classes/structs for runtime state
> - Use static classes or dependency injection for shared state
> - Use proper save/load systems for persistent data
>
> If you must use this pattern, understand the limitations and always clear state in `OnEnable()`.

<details>
<summary><b>Example for reference (not recommended)</b></summary>

```csharp
// ⚠️ NOT RECOMMENDED - Runtime sets with ScriptableObjects
[CreateAssetMenu(menuName = "Collections/Enemy Set")]
public class EnemySet : ScriptableObject
{
    private List<Enemy> enemies = new List<Enemy>();

    public IReadOnlyList<Enemy> Enemies => enemies;

    private void OnEnable()
    {
        // CRITICAL: Clear stale state from previous sessions
        enemies.Clear();
    }

    public void Add(Enemy enemy)
    {
        if (!enemies.Contains(enemy))
            enemies.Add(enemy);
    }

    public void Remove(Enemy enemy)
    {
        enemies.Remove(enemy);
    }

    public void Clear()
    {
        enemies.Clear();
    }
}

public class Enemy : MonoBehaviour
{
    [SerializeField] private EnemySet activeEnemies;

    private void OnEnable()
    {
        activeEnemies.Add(this);
    }

    private void OnDisable()
    {
        activeEnemies.Remove(this);
    }
}
```

**Problems with this approach:**
- State persists between Editor play sessions (confusing)
- Can't inspect scene objects in ScriptableObject Inspector
- Hard to debug which enemies are in the set
- Doesn't scale well to multiple instance types

</details>

### 5. Persistent Data Between Scenes ⚠️ (Not Recommended)

> **⚠️ Warning: ScriptableObjects are not suitable for persistent save data.**
>
> While ScriptableObjects survive scene loads, they have critical limitations for persistent data:
>
> - **Build behavior**: Changes only persist within a single game session, not between sessions[^1]
> - **Editor confusion**: Data persists in Editor but resets in builds, causing unexpected behavior[^1]
> - **Not designed for saves**: ScriptableObjects were designed for immutable configuration data[^2]
> - **Asset corruption risk**: Runtime modifications can accidentally be saved to the asset file in Editor
>
> **Use proper save systems instead:**
> - PlayerPrefs for simple key-value data
> - JSON/Binary serialization to persistent data paths
> - Dedicated save/load systems (e.g., SaveSystem packages)

<details>
<summary><b>Why this doesn't work (click to expand)</b></summary>

```csharp
// ❌ NOT RECOMMENDED - ScriptableObjects for persistent data
[CreateAssetMenu(menuName = "Game/Player Data")]
public class PlayerData : ScriptableObject
{
    public int currentHealth;
    public int maxHealth;
    public int gold;
    public List<string> unlockedAbilities;

    public void ResetToDefaults()
    {
        currentHealth = maxHealth;
        gold = 0;
        unlockedAbilities.Clear();
    }
}
```

**What actually happens:**

**In Editor:**
1. Player plays, gains 100 gold
2. Exit play mode → gold = 100 (persisted!)
3. Enter play mode again → gold = 100 (still there!)
4. This seems to work... but it's misleading

**In Build:**
1. Player plays, gains 100 gold
2. Exit game → gold data lost
3. Restart game → gold = 0 (back to default!)
4. Players lose all progress

**The solution:** Use PlayerPrefs or a proper save system that writes to persistent storage.

</details>

## When NOT to Use ScriptableObjects

Avoid ScriptableObjects when:

### 1. Mutable Runtime State

**ScriptableObjects are designed for immutable data, not runtime state management.**

```csharp
// ❌ DON'T - Runtime variables that change during gameplay
[CreateAssetMenu]
public class FloatVariable : ScriptableObject
{
    public float value;  // Bad! Mutable runtime state
}

// ✓ DO - Use regular C# classes for runtime state
public class GameState
{
    public float currentValue;  // Simple, clear, no persistence issues
}
```

**Why this is problematic:**
- Changes persist between Editor play sessions but not in builds[^1]
- Hard to debug which systems are modifying the values[^2]
- Causes confusion about game state during development
- Not how ScriptableObjects were designed to be used[^2]

### 2. Instance-Specific Runtime Data

```csharp
// ❌ DON'T - This data is unique per enemy instance
[CreateAssetMenu]
public class EnemyState : ScriptableObject
{
    public Vector3 position;      // Bad! Position is per-instance
    public int currentHealth;     // Bad! Health is per-instance
    public Transform target;      // Bad! Target is per-instance
}

// ✓ DO - Use regular class for instance data
public class Enemy : MonoBehaviour
{
    [SerializeField] private EnemySettings settings;  // Shared data from SO

    // Instance data
    private Vector3 position;
    private int currentHealth;
    private Transform target;
}
```

### 3. Persistent Save Data

```csharp
// ❌ DON'T - ScriptableObjects for save games
[CreateAssetMenu]
public class SaveData : ScriptableObject
{
    public int playerLevel;
    public int score;
    // This won't persist between game sessions in builds!
}

// ✓ DO - Use proper save systems
public class SaveSystem
{
    public void SaveGame(SaveData data)
    {
        string json = JsonUtility.ToJson(data);
        File.WriteAllText(Application.persistentDataPath + "/save.json", json);
    }
}
```

### 4. Frequently Changing Data

```csharp
// ❌ DON'T - Updated every frame
[CreateAssetMenu]
public class PlayerPosition : ScriptableObject
{
    public Vector3 position;  // Bad! Changes every frame
}

// ✓ DO - Use regular variables or events
public class Player : MonoBehaviour
{
    public Vector3 Position => transform.position;
}
```

### 5. When MonoBehaviour is More Appropriate

```csharp
// ❌ DON'T - Needs Update loop
[CreateAssetMenu]
public class Timer : ScriptableObject
{
    public float currentTime;

    // Can't use Update()!
    // ScriptableObjects don't have Update/FixedUpdate/etc.
}

// ✓ DO - Use MonoBehaviour
public class Timer : MonoBehaviour
{
    public float currentTime;

    private void Update()
    {
        currentTime += Time.deltaTime;
    }
}
```

## Creating ScriptableObjects

### Basic ScriptableObject

```csharp
using UnityEngine;

[CreateAssetMenu(fileName = "NewWeaponData", menuName = "Game/Weapon Data")]
public class WeaponData : ScriptableObject
{
    [Header("Display")]
    public string weaponName;
    public Sprite icon;
    public GameObject prefab;

    [Header("Stats")]
    public int damage;
    public float fireRate;
    public float range;

    [Header("Ammo")]
    public int magazineSize;
    public int maxAmmo;
}
```

### Creating Assets in Editor

1. Right-click in Project window
2. Navigate to "Create" → your menu path (e.g., "Game/Weapon Data")
3. Name your asset (e.g., "Rifle_Data")
4. Fill in the Inspector values

### Creating Assets in Code

```csharp
#if UNITY_EDITOR
using UnityEditor;

public class WeaponDataGenerator
{
    [MenuItem("Tools/Create Weapon Data")]
    public static void CreateWeaponData()
    {
        WeaponData data = ScriptableObject.CreateInstance<WeaponData>();

        data.weaponName = "New Weapon";
        data.damage = 10;
        data.fireRate = 1f;

        AssetDatabase.CreateAsset(data, "Assets/Data/Weapons/NewWeapon.asset");
        AssetDatabase.SaveAssets();
    }
}
#endif
```

## Common Patterns

### 1. Shared Configuration Pattern

```csharp
// Define settings once
[CreateAssetMenu(menuName = "Game/Game Settings")]
public class GameSettings : ScriptableObject
{
    [Header("Difficulty")]
    public float enemyHealthMultiplier = 1f;
    public float enemyDamageMultiplier = 1f;

    [Header("Audio")]
    public float masterVolume = 1f;
    public float musicVolume = 0.7f;
    public float sfxVolume = 1f;
}

// Use everywhere
public class Enemy : MonoBehaviour
{
    [SerializeField] private GameSettings settings;
    [SerializeField] private float baseHealth = 100;

    private void Start()
    {
        float actualHealth = baseHealth * settings.enemyHealthMultiplier;
    }
}
```

### 2. Variable Reference Pattern ⚠️ (Not Recommended)

> **⚠️ Warning: This is a mutable runtime state pattern - not recommended for the same reasons as Runtime Sets.**
>
> This pattern suffers from the same issues:
> - State persists between Editor play sessions but not in builds
> - Hard to debug which systems are modifying values
> - Doesn't scale well when you need many variables[^2]
>
> **Better alternative:** Use regular C# classes with events or a reactive framework like UniRx.

<details>
<summary><b>Example for reference (not recommended)</b></summary>

```csharp
// ⚠️ NOT RECOMMENDED - Mutable variable ScriptableObjects
[CreateAssetMenu(menuName = "Variables/Float Variable")]
public class FloatVariable : ScriptableObject
{
    [SerializeField] private float value;

    public float Value
    {
        get => value;
        set
        {
            this.value = value;
            OnValueChanged?.Invoke(value);
        }
    }

    public event System.Action<float> OnValueChanged;

    private void OnEnable()
    {
        // Must clear event listeners to prevent accumulation
        OnValueChanged = null;
    }

    public void Add(float amount)
    {
        Value += amount;
    }

    public void Subtract(float amount)
    {
        Value -= amount;
    }
}

// Usage
public class HealthBar : MonoBehaviour
{
    [SerializeField] private FloatVariable playerHealth;
    [SerializeField] private Image healthBar;

    private void OnEnable()
    {
        playerHealth.OnValueChanged += UpdateDisplay;
        UpdateDisplay(playerHealth.Value);
    }

    private void OnDisable()
    {
        playerHealth.OnValueChanged -= UpdateDisplay;
    }

    private void UpdateDisplay(float health)
    {
        healthBar.fillAmount = health / 100f;
    }
}
```

**Problems:**
- Need to create an asset for every variable (PlayerHealth, EnemyHealth, Score, etc.)
- State persistence issues between Editor/Build
- Hard to manage at scale

</details>

### 3. Typed Collection Pattern ⚠️ (Not Recommended)

> **⚠️ Warning: This is another form of mutable runtime state - not recommended.**
>
> This pattern (also called "Runtime Sets") suffers from the same issues as other mutable ScriptableObject patterns:
> - Editor/Build behavior inconsistency[^1]
> - Can't serialize scene objects properly[^3]
> - Hard to debug and doesn't scale[^2]
>
> **Better alternative:** Use static managers with regular C# collections, or dependency injection frameworks.

<details>
<summary><b>Example for reference (not recommended)</b></summary>

```csharp
// ⚠️ NOT RECOMMENDED - Runtime collections with ScriptableObjects
public abstract class RuntimeSet<T> : ScriptableObject
{
    private readonly List<T> items = new List<T>();

    public IReadOnlyList<T> Items => items;

    private void OnEnable()
    {
        // CRITICAL: Must clear to prevent stale data
        items.Clear();
    }

    public void Add(T item)
    {
        if (!items.Contains(item))
            items.Add(item);
    }

    public void Remove(T item)
    {
        items.Remove(item);
    }

    public void Clear()
    {
        items.Clear();
    }
}

// Concrete implementations
[CreateAssetMenu(menuName = "Collections/Enemy Set")]
public class EnemySet : RuntimeSet<Enemy> { }

[CreateAssetMenu(menuName = "Collections/Collectible Set")]
public class CollectibleSet : RuntimeSet<Collectible> { }
```

**Better approach - Static Manager:**

```csharp
// ✅ RECOMMENDED - Regular C# collection with single source of truth. Static classes are not recommended for production code, this is just here as an example.
public class EnemyManager : MonoBehavior
{
    // Note: There are better, safer singleton implementations
    public static EnemyManagerInstance
    {
        get
        {
            if (instance == null) 
            {
                GameObject singleton = new("EnemeyManager-Singleton", typeof(EnemyManager));
                // instance should be auto-populated
            }
            return instance;
        }
    }

    private static EnemyManager instance;

    private void Awake()
    {
        instance = this;
    }

    private readonly List<Enemy> activeEnemies = new List<Enemy>();

    public IReadOnlyList<Enemy> ActiveEnemies => activeEnemies;

    public void Register(Enemy enemy) => activeEnemies.Add(enemy);
    public void Unregister(Enemy enemy) => activeEnemies.Remove(enemy);
}

public class Enemy : MonoBehaviour
{
    private void OnEnable() => EnemyManager.Instance.Register(this);
    private void OnDisable() => EnemyManager.Instance.Unregister(this);
}
```

</details>

## Best Practices

### 1. Keep ScriptableObjects Immutable

**The most important best practice: Use ScriptableObjects for immutable data only.**[^2]

```csharp
// ✅ GOOD - Immutable configuration data
[CreateAssetMenu]
public class EnemyData : ScriptableObject
{
    [Header("Design Data - Set once, never changes at runtime")]
    public int maxHealth = 100;
    public int damage = 10;
    public float moveSpeed = 5f;
    public GameObject prefab;

    // No runtime state here!
}

// ❌ BAD - Mutable runtime state in ScriptableObject
[CreateAssetMenu]
public class PlayerData : ScriptableObject
{
    public int currentHealth;  // Don't do this!
    public int currentGold;    // Use regular C# classes instead!
}
```

**Why immutability matters:**
- Avoids Editor/Build persistence inconsistencies[^1]
- Makes code easier to debug and understand[^2]
- Prevents unexpected state carryover between play sessions
- Follows the original design intent of ScriptableObjects[^2]

### 2. Use CreateAssetMenu Properly

```csharp
// ✓ GOOD - Clear, organized menu
[CreateAssetMenu(
    fileName = "New Enemy Data",
    menuName = "Game/Characters/Enemy Data",
    order = 1
)]
public class EnemyData : ScriptableObject
{
    // ...
}

// ❌ BAD - Generic, unclear
[CreateAssetMenu]
public class Data : ScriptableObject
{
    // What kind of data?
}
```

### 3. Make Fields ReadOnly Where Appropriate

```csharp
public class GameSettings : ScriptableObject
{
    [SerializeField] private float masterVolume = 1f;

    // Readonly property - can't be changed arbitrarily
    public float MasterVolume => masterVolume;

    // Controlled setter with validation
    public void SetMasterVolume(float volume)
    {
        masterVolume = Mathf.Clamp01(volume);
    }
}
```

### 4. Avoid Runtime Collections in ScriptableObjects

> **⚠️ Don't use ScriptableObjects for runtime collections.** See warnings in sections above.

If you inherited a codebase using this pattern and must maintain it temporarily, always clear collections in `OnEnable()`:

```csharp
// ⚠️ Legacy pattern - avoid in new code
[CreateAssetMenu]
public class EnemySet : ScriptableObject
{
    private List<Enemy> enemies = new List<Enemy>();

    private void OnEnable()
    {
        // CRITICAL: Clear leftovers from previous Play Mode
        enemies.Clear();
    }

    public void Add(Enemy enemy)
    {
        if (!enemies.Contains(enemy))
            enemies.Add(enemy);
    }
}
```

**Better approach:** Use static managers / single source of truth (see Typed Collection Pattern example above).

### 5. Use Context Menus for Design Data Editing

```csharp
[CreateAssetMenu]
public class EnemyData : ScriptableObject
{
    public int maxHealth = 100;
    public int damage = 10;

    #if UNITY_EDITOR
    // Add context menu in Inspector for quick edits
    [ContextMenu("Apply Difficulty Scaling")]
    private void ApplyHardMode()
    {
        maxHealth = (int)(maxHealth * 1.5f);
        damage = (int)(damage * 1.5f);
        UnityEditor.EditorUtility.SetDirty(this);
    }

    [ContextMenu("Reset to Defaults")]
    private void ResetToDefaults()
    {
        maxHealth = 100;
        damage = 10;
        UnityEditor.EditorUtility.SetDirty(this);
    }
    #endif
}
```

**Note:** This is for **design-time editing** of immutable data, not for runtime state management.

### 6. Don't Store Scene References

```csharp
// ❌ BAD - Scene references in ScriptableObject
[CreateAssetMenu]
public class PlayerData : ScriptableObject
{
    public Transform playerTransform;  // Bad! Scene reference!
    public GameObject playerObject;    // Bad! Scene reference!
}

// ✓ GOOD - Store data, not references
[CreateAssetMenu]
public class PlayerData : ScriptableObject
{
    public float moveSpeed;
    public int maxHealth;
    // Just data, no scene references
}
```

## Common Pitfalls

### Pitfall 1: Using ScriptableObjects for Mutable Runtime State

**This is the #1 most common misuse of ScriptableObjects.**[^1][^2]

```csharp
// ❌ PROBLEM - Mutable runtime state in ScriptableObject
[CreateAssetMenu]
public class GameState : ScriptableObject
{
    public int currentLevel = 1;
    public int score = 0;

    // Problems:
    // 1. Values persist in Editor between play sessions (confusing!)
    // 2. Values reset in Build between game sessions (broken!)
    // 3. Hard to debug which systems modify these values
}

// ✓ SOLUTION - Use regular C# classes for runtime state
public class GameState // No ScriptableObject!
{
    public int currentLevel = 1;
    public int score = 0;

    // Clear, predictable behavior
    // Easy to debug
    // Works same in Editor and Build
}

// Access via singleton, static, or dependency injection
public class GameManager : MonoBehaviour
{
    private static GameManager instance;
    public static GameState State { get; private set; } = new GameState();

    private void Awake()
    {
        if (instance == null)
        {
            instance = this;
            DontDestroyOnLoad(gameObject);
        }
    }
}
```

**Key takeaway:** Don't try to "fix" mutable ScriptableObject state with `OnEnable()` resets. Just don't use ScriptableObjects for mutable state at all.[^2]

### Pitfall 2: Using ScriptableObjects for Per-Instance Data

```csharp
// ❌ WRONG - All enemies share same data!
[CreateAssetMenu]
public class EnemyState : ScriptableObject
{
    public int currentHealth;
    public Vector3 position;
}

public class Enemy : MonoBehaviour
{
    [SerializeField] private EnemyState state;

    private void TakeDamage(int damage)
    {
        state.currentHealth -= damage;
        // All enemies using this asset take damage!
    }
}

// ✓ CORRECT - Instance data on MonoBehaviour
[CreateAssetMenu]
public class EnemyData : ScriptableObject
{
    public int maxHealth;  // Shared configuration
    public float moveSpeed;
}

public class Enemy : MonoBehaviour
{
    [SerializeField] private EnemyData data;

    private int currentHealth;  // Instance data
    private Vector3 currentPosition;

    private void Start()
    {
        currentHealth = data.maxHealth;
    }
}
```

### Pitfall 3: Not Unregistering Event Listeners

```csharp
// ❌ BAD - Memory leak!
public class EventListener : MonoBehaviour
{
    [SerializeField] private GameEvent gameEvent;

    private void Start()
    {
        gameEvent.OnEventRaised += HandleEvent;
    }

    // Forgot to unregister!
    // Reference persists even after object is destroyed
}

// ✓ GOOD - Proper cleanup
public class EventListener : MonoBehaviour
{
    [SerializeField] private GameEvent gameEvent;

    private void OnEnable()
    {
        gameEvent.OnEventRaised += HandleEvent;
    }

    private void OnDisable()
    {
        gameEvent.OnEventRaised -= HandleEvent;
    }

    private void HandleEvent()
    {
        // Handle event
    }
}
```

### Pitfall 4: Trying to Use ScriptableObjects for Save Data

**ScriptableObjects don't work for persistent save data.**[^1]

**See [Save/Load System](./18-save-load.md) for a full save/load implementation.**

```csharp
// ❌ WRONG - This doesn't work as expected
[CreateAssetMenu]
public class PlayerData : ScriptableObject
{
    public int highScore;

    public void SetHighScore(int score)
    {
        highScore = score;
        // In Editor: Persists (misleading!)
        // In Build: Resets on game restart (broken!)
    }
}

// ✓ CORRECT - Use proper save system
public class SaveSystem
{
    private const string SAVE_PATH = "/save.json";

    [System.Serializable]
    public class PlayerData
    {
        public int highScore;
    }

    public static void SaveData(PlayerData data)
    {
        string json = JsonUtility.ToJson(data);
        File.WriteAllText(Application.persistentDataPath + SAVE_PATH, json);
    }

    public static PlayerData LoadData()
    {
        string path = Application.persistentDataPath + SAVE_PATH;
        if (File.Exists(path))
        {
            string json = File.ReadAllText(path);
            return JsonUtility.FromJson<PlayerData>(json);
        }
        return new PlayerData();
    }
}
```

**Or use PlayerPrefs for simple data:**

```csharp
// ✅ SIMPLE SOLUTION - PlayerPrefs
public class ScoreManager : MonoBehaviour
{
    public int defaultHighScore;

    public int GetHighScore()
    {
        return PlayerPrefs.GetInt("HighScore", defaultHighScore);
    }

    public void SetHighScore(int score)
    {
        PlayerPrefs.SetInt("HighScore", score);
        PlayerPrefs.Save();
    }
}
```

### Pitfall 5: Circular References

```csharp
// ❌ BAD - Circular reference!
[CreateAssetMenu]
public class WeaponData : ScriptableObject
{
    public CharacterData owner;  // Weapon references character
}

[CreateAssetMenu]
public class CharacterData : ScriptableObject
{
    public WeaponData weapon;  // Character references weapon
}
// Can cause issues with serialization and loading

// ✓ BETTER - One-way references
[CreateAssetMenu]
public class WeaponData : ScriptableObject
{
    public int damage;
    public float range;
    // No reference to CharacterData
}

[CreateAssetMenu]
public class CharacterData : ScriptableObject
{
    public WeaponData startingWeapon;  // Only character references weapon
}
```

## Quick Reference

### Use ScriptableObjects For

- ✓ **Shared configuration data** (immutable design data)
- ✓ **Item/enemy/ability databases** (static data tables)
- ✓ **Constants and enums** (game rules, formulas)
- ✓ **Editor tools** (custom asset types)
- ⚠️ **Event systems** (see [Event Systems Comparison](./10-event-systems.md) for trade-offs)

### Don't Use ScriptableObjects For

- ❌ **Mutable runtime state** (use regular C# classes)[^1][^2]
- ❌ **Runtime collections** (use regular lists/dictionaries)[^1][^2]
- ❌ **Persistent save data** (use PlayerPrefs/save systems)[^1]
- ❌ **Per-instance runtime data** (use MonoBehaviour fields)
- ❌ **Frequently changing data** (every frame updates)
- ❌ **Data that needs Update/FixedUpdate** (use MonoBehaviour)
- ❌ **Scene references** (ScriptableObjects can't serialize scene objects)[^3]

### Always Remember To

- ✓ Reset to defaults in OnEnable (Editor only)
- ✓ Clear runtime collections on enable
- ✓ Clear event listeners in OnEnable (if using ScriptableObject events)
- ✓ Avoid scene references
- ✓ Use CreateAssetMenu for easy creation

## Summary

**Golden Rules:**

1. **ScriptableObjects are for immutable data**, not runtime state[^2]
2. **Use for configuration and design data** (enemy stats, item definitions, game rules)
3. **Don't use for mutable runtime state** (player health, scores, active object lists)[^1][^2]
4. **Don't use for persistent save data** (use proper save systems instead)[^1]
5. **Reset runtime values in OnEnable** if you must store runtime data (Editor only)
6. **Don't store scene references** in ScriptableObjects[^3]
7. **For event systems**, see the [Event Systems Comparison](./10-event-systems.md) to understand trade-offs

ScriptableObjects are incredibly powerful for organizing your game's **immutable configuration data** and creating decoupled, maintainable systems. Use them for what they were designed for: data containers, not state managers.

---

## References

[^1]: Unity Forums: [ScriptableObject changes persist between editor but not game sessions](https://forum.unity.com/threads/scriptable-object-changes-persist-between-editor-but-not-game-sessions.525392/). Changes to ScriptableObjects persist in Editor play sessions but reset in builds, causing confusion and bugs.

[^2]: GitHub: [AntiScriptableObjectArchitecture](https://github.com/cathei/AntiScriptableObjectArchitecture). Documents problems with using ScriptableObjects for runtime state: design mismatch, debugging difficulties, scalability issues, and domain reload complications.

[^3]: Unity Documentation: [Using ScriptableObject-based Runtime Sets](https://unity.com/how-to/scriptableobject-based-runtime-set). ScriptableObjects can't serialize scene objects by design, causing "Type mismatch" errors in Inspector.
