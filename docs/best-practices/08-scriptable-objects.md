# Unity ScriptableObjects Best Practices

> **🛑 Looking for Event Systems?** Don't use ScriptableObjects for events!
>
> ScriptableObject events require **manual asset creation, manual Inspector wiring, custom editor
> tools to debug, and don't scale**. You can't trace who's listening or sending, "Find References"
> doesn't work on assets, and complex projects become unmaintainable.
>
> Use **[DxMessaging](./19-event-systems.md)** instead for automatic memory management, code-only
> events (no assets!), full debugging support, and scales to thousands of events. See the
> **[Event Systems Comparison](./19-event-systems.md)** for details.

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

**Simple Analogy**: Think of MonoBehaviours as "actors" (they do things in your scene), and
ScriptableObjects as "scripts" or "recipes" (they hold information that actors can read from).

## Table of Contents

- [When to Use ScriptableObjects](#when-to-use-scriptableobjects)
- [When NOT to Use ScriptableObjects](#when-not-to-use-scriptableobjects)
- [Creating ScriptableObjects](#creating-scriptableobjects)
- [Common Patterns](#common-patterns)
- [Best Practices](#best-practices)
- [Common Pitfalls](#common-pitfalls)

## When to Use ScriptableObjects

> **⚠️ Note:** This guide covers general ScriptableObject usage. For **event systems specifically**,
> see **[Event Systems: ScriptableObject vs DxMessaging](./19-event-systems.md)** - DxMessaging is
> the superior choice for events.

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

### 3. ~~Event Systems~~ **❌ DON'T USE ScriptableObjects for Events**

> **🛑 STOP: Don't use ScriptableObjects for event systems!**
>
> **Use [DxMessaging](./19-event-systems.md) instead.** ScriptableObject events are **extremely
> manual** (create assets, wire Inspector, track references), **impossible to debug** (can't see
> who's listening/sending, need custom editor tools), and **don't scale** (hundreds of assets,
> Inspector nightmare, unmaintainable in complex projects).
>
> **ScriptableObject event problems:**
>
> - ❌ **Manual everything** - Create assets, wire Inspector for every component, track all
>   references
> - ❌ **Can't debug** - No way to trace listeners/senders, must build custom editor tools
> - ❌ **Doesn't scale** - Hundreds of event assets, Inspector references break, new devs can't
>   understand flow
> - ❌ **Memory leaks** - Forget `OnDisable()` unregister = leak (happens constantly)
> - ❌ **No compile-time safety** - Wrong asset in Inspector = silent runtime failure
>
> **DxMessaging provides:**
>
> - ✅ **Zero manual work** - No assets, no Inspector wiring, just code
> - ✅ **Full debugging** - Inspector shows all message flow, handlers, and performance
> - ✅ **Scales to thousands** - Code-only, "Find References" works, refactoring works
> - ✅ **Zero memory leaks** - Automatic cleanup, impossible to forget
> - ✅ **Compile-time type safety** - Wrong message type = compiler error
>
> **Read the full comparison:** >
> **[Event Systems: ScriptableObject vs DxMessaging](./19-event-systems.md)**

<details>
<summary><b>Why is this pattern still documented?</b> (Click to expand)</summary>

This pattern is shown for **reference only** because you'll see it in older tutorials and legacy
codebases.

**Don't use it in new projects.** The code below demonstrates why ScriptableObject events are
error-prone:

```csharp
// ❌ BAD PATTERN - ScriptableObject events (shown for reference only)
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
        OnEventRaised -= listener;  // Easy to forget = memory leak!
    }
}

// Usage (requires manual cleanup)
public class ScoreUI : MonoBehaviour
{
    [SerializeField] private IntEvent onScoreChanged;

    private void OnEnable()
    {
        onScoreChanged.RegisterListener(UpdateDisplay);
    }

    private void OnDisable()
    {
        onScoreChanged.UnregisterListener(UpdateDisplay);  // Forget this = MEMORY LEAK!
    }

    private void UpdateDisplay(int newScore)
    {
        // Update UI
    }
}
```

**Problems with this approach:**

- ❌ Manual cleanup required (forget `OnDisable()` = memory leak)
- ❌ Must create asset for every event type (Project clutter)
- ❌ No compile-time safety (wrong asset in Inspector = runtime error)
- ❌ Allocates garbage for event parameters
- ❌ Listeners persist between Play Mode sessions (must clear in `OnEnable()`)

**Real-world scaling nightmare:**

Imagine you have 50 different events in your game (player death, enemy spawned, score changed, level
complete, etc.). With ScriptableObject events:

1. **Manual asset hell:** Create 50 event assets in Project window
2. **Inspector nightmare:** Wire 50 assets across hundreds of components
3. **Debugging impossible:** Event fired - who's listening? Search entire project, check every
   Inspector
4. **Refactoring disaster:** Rename "OnPlayerDeath" → "OnPlayerKilled"? Manually update 30 Inspector
   references
5. **New dev onboarding:** "How does player death trigger game over?" → Must search assets, check
   Inspectors, draw flow diagram
6. **Custom tools required:** Build editor window just to see which components listen to which
   events

With DxMessaging: Search for `RegisterUntargeted<PlayerDied>` - done. All listeners found in 2
seconds with "Find References".

**✅ Use DxMessaging instead:**

```csharp
// ✅ GOOD PATTERN - DxMessaging (automatic cleanup, zero allocations)
[DxUntargetedMessage]
[DxAutoConstructor]
public readonly partial struct ScoreChanged {
    public readonly int newScore;
}

// Usage (automatic cleanup!)
public class ScoreUI : MessageAwareComponent {
    protected override void RegisterMessageHandlers() {
        _ = Token.RegisterUntargeted<ScoreChanged>(UpdateDisplay);
    }  // Token automatically unsubscribes when destroyed - zero leaks!

    void UpdateDisplay(ref ScoreChanged msg) {
        // Update UI
    }
}
```

**See full comparison:** **[Event Systems Best Practices](./19-event-systems.md)**

</details>

### 4. Runtime Sets/Collections

```csharp
// Track all active enemies
[CreateAssetMenu(menuName = "Collections/Enemy Set")]
public class EnemySet : ScriptableObject
{
    private List<Enemy> enemies = new List<Enemy>();

    public IReadOnlyList<Enemy> Enemies => enemies;

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

public class WaveManager : MonoBehaviour
{
    [SerializeField] private EnemySet activeEnemies;

    public bool AllEnemiesDefeated()
    {
        return activeEnemies.Enemies.Count == 0;
    }
}
```

**Use for**: Active enemy lists, player inventory, quest tracking

### 5. Persistent Data Between Scenes

```csharp
// Survives scene loads
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

**Use for**: Player stats, game progression, unlocks (but be careful - see pitfalls!)

## When NOT to Use ScriptableObjects

Avoid ScriptableObjects when:

### 1. Event Systems

> **🛑 DON'T use ScriptableObjects for event systems!** Use [DxMessaging](./19-event-systems.md)
> instead.

ScriptableObject events are a common anti-pattern that causes memory leaks and requires manual
cleanup.

**Why ScriptableObject events are bad:**

**Manual & Error-Prone:**

- ❌ Memory leaks if you forget to unregister in `OnDisable()` (happens constantly)
- ❌ Must manually create asset for every event type (dozens of files in Project)
- ❌ Must manually wire assets in Inspector for every component (hundreds of references)
- ❌ Must manually track down and update every reference when refactoring
- ❌ No compile-time safety (wrong asset in Inspector = silent runtime failure)

**Debugging Nightmare:**

- ❌ **Can't see who's listening to an event** - No way to trace all subscribers
- ❌ **Can't see who's sending an event** - No way to find all raisers
- ❌ **Can't debug message flow** - Events fire with no stack trace or visibility
- ❌ **Must build custom editor tools** just to understand your own event system
- ❌ **Search fails** - Can't "Find References" on assets, only string search

**Scaling Disaster:**

- ❌ **Hundreds of event assets clutter Project window** - Finding the right one is painful
- ❌ **Inspector references break** when moving/renaming assets
- ❌ **No compile-time refactoring** - Rename event? Manually fix all Inspector references
- ❌ **New team members can't trace flow** without custom editor tools
- ❌ **Complex projects become unmaintainable** - Event chains are invisible

**Technical Issues:**

- ❌ Allocates garbage for event parameters
- ❌ Listeners persist between Play Mode sessions (must clear manually)
- ❌ Runtime modifications persist to disk (corrupt your assets)

**Why DxMessaging is better:**

- ✅ **Zero memory leaks** - Automatic cleanup, impossible to forget
- ✅ **Zero manual work** - No assets, no Inspector wiring, no manual tracking
- ✅ **Full debugging support** - Inspector shows all message types, handlers, and flow
- ✅ **Code-only** - "Find References" works, refactoring works, team members can trace flow
- ✅ **Compile-time type safety** - Wrong message type = compiler error
- ✅ **Zero allocations** - Readonly structs, no garbage
- ✅ **Scales to thousands of events** - No Project clutter, no Inspector nightmare

**See the full comparison:**
**[Event Systems: ScriptableObject vs DxMessaging](./19-event-systems.md)**

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

### 3. Frequently Changing Data

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

### 4. When MonoBehaviour is More Appropriate

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

### 2. ~~Event Channel Pattern~~ **❌ DON'T DO THIS - Use DxMessaging Instead**

> **🛑 STOP: Don't use the Event Channel Pattern!**
>
> This is a common anti-pattern from older Unity tutorials. It's **extremely manual** (create assets
> for every event, wire every component in Inspector), **impossible to debug** (can't trace who's
> listening/sending without custom editor tools), and **doesn't scale** (hundreds of event assets,
> unmaintainable in complex projects).
>
> **Use [DxMessaging](./19-event-systems.md) instead** for zero manual work, full debugging support,
> and scales to thousands of events.
>
> **See:** **[Event Systems: ScriptableObject vs DxMessaging Comparison](./19-event-systems.md)**

<details>
<summary><b>Why is this anti-pattern still documented?</b> (Click to expand)</summary>

You'll see this pattern in legacy code and older tutorials. Here's why it's problematic:

```csharp
// ❌ BAD: Event Channel anti-pattern (DO NOT USE)
[CreateAssetMenu(menuName = "Events/Game Event")]
public class GameEvent : ScriptableObject
{
    private readonly List<GameEventListener> listeners = new List<GameEventListener>();

    public void Raise()
    {
        for (int i = listeners.Count - 1; i >= 0; i--)
        {
            listeners[i].OnEventRaised();
        }
    }

    public void RegisterListener(GameEventListener listener)
    {
        if (!listeners.Contains(listener))
            listeners.Add(listener);
    }

    public void UnregisterListener(GameEventListener listener)
    {
        listeners.Remove(listener);  // Must remember to call this!
    }

    // Missing OnEnable() to clear listeners = accumulation between Play Mode sessions!
}

// Listener component
public class GameEventListener : MonoBehaviour
{
    [SerializeField] private GameEvent gameEvent;
    [SerializeField] private UnityEvent response;

    private void OnEnable()
    {
        gameEvent.RegisterListener(this);
    }

    private void OnDisable()
    {
        gameEvent.UnregisterListener(this);  // Forget this = memory leak!
    }

    public void OnEventRaised()
    {
        response?.Invoke();
    }
}
```

**Problems:**

- ❌ Memory leaks if you forget `OnDisable()` unregistration
- ❌ Listeners accumulate between Play Mode sessions
- ❌ Must create asset for every event type
- ❌ No type safety (all events are generic)
- ❌ UnityEvent allocates garbage

**The debugging and scaling nightmare:**

**Scenario:** Your game fires an `OnPlayerDeath` event, but game over screen doesn't appear.

**With ScriptableObject events (painful):**

1. Find `OnPlayerDeath.asset` in Project window (which folder?)
2. Click asset - Inspector shows nothing useful (just the ScriptableObject)
3. Search entire project for `onPlayerDeath` (string search, error-prone)
4. Check every result - which ones are listeners vs raisers?
5. Open each component in Inspector to see if the asset is wired
6. Realize UIManager has `onHealthChanged.asset` wired instead of `onPlayerDeath.asset` - silent
   bug!
7. Debug time: **30+ minutes**

**With DxMessaging (instant):**

1. Right-click `PlayerDied` message → "Find References"
2. See all `RegisterUntargeted<PlayerDied>` calls
3. UIManager not in list - found the bug!
4. Debug time: **30 seconds**

**Scaling gets worse:** At 100+ events, ScriptableObject approach requires custom editor tools just
to visualize event flow. DxMessaging's Inspector shows everything automatically.

**✅ Use DxMessaging instead:**

```csharp
// ✅ GOOD: DxMessaging (automatic cleanup, zero leaks)
[DxUntargetedMessage]
[DxAutoConstructor]
public readonly partial struct PlayerDied { }

public class UIManager : MessageAwareComponent {
    protected override void RegisterMessageHandlers() {
        _ = Token.RegisterUntargeted<PlayerDied>(OnPlayerDied);
    }  // Automatic cleanup when destroyed!

    void OnPlayerDied(ref PlayerDied msg) {
        ShowGameOverScreen();
    }
}

// Raise from anywhere
new PlayerDied().EmitUntargeted();
```

**Full comparison:** **[Event Systems Best Practices](./19-event-systems.md)**

</details>

### 3. Variable Reference Pattern

```csharp
// Shared variable that multiple objects can read/write
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

### 4. Typed Collection Pattern

```csharp
// Base class
public abstract class RuntimeSet<T> : ScriptableObject
{
    private readonly List<T> items = new List<T>();

    public IReadOnlyList<T> Items => items;

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

## Best Practices

### 1. Reset to Defaults on Play

ScriptableObjects persist between Play Mode sessions!

```csharp
[CreateAssetMenu]
public class PlayerData : ScriptableObject
{
    [Header("Default Values")]
    public int defaultHealth = 100;
    public int defaultGold = 0;

    [Header("Runtime Values")]
    public int currentHealth;
    public int currentGold;

    private void OnEnable()
    {
        #if UNITY_EDITOR
        // Reset to defaults when entering Play Mode
        if (!Application.isPlaying)
        {
            ResetToDefaults();
        }
        #endif
    }

    public void ResetToDefaults()
    {
        currentHealth = defaultHealth;
        currentGold = defaultGold;
    }
}
```

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

### 4. Clear Runtime Collections on Enable

```csharp
[CreateAssetMenu]
public class EnemySet : ScriptableObject
{
    private List<Enemy> enemies = new List<Enemy>();

    private void OnEnable()
    {
        // Clear leftovers from previous Play Mode
        enemies.Clear();
    }

    public void Add(Enemy enemy)
    {
        if (!enemies.Contains(enemy))
            enemies.Add(enemy);
    }
}
```

### 5. Use Editor-Only Reset for Development

```csharp
[CreateAssetMenu]
public class PlayerStats : ScriptableObject
{
    public int health;
    public int gold;

    #if UNITY_EDITOR
    // Add context menu in Inspector
    [ContextMenu("Reset to Defaults")]
    private void ResetToDefaults()
    {
        health = 100;
        gold = 0;
        UnityEditor.EditorUtility.SetDirty(this);
    }
    #endif
}
```

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

### Pitfall 1: Forgetting ScriptableObjects Persist in Editor

```csharp
// ❌ PROBLEM - Values persist between Play Mode sessions
[CreateAssetMenu]
public class GameState : ScriptableObject
{
    public int currentLevel = 1;
    public int score = 0;

    // You start Play Mode: score = 0
    // Gain 100 points: score = 100
    // Exit Play Mode: score still = 100!
    // Next Play Mode: starts at 100!
}

// ✓ SOLUTION - Reset in OnEnable
[CreateAssetMenu]
public class GameState : ScriptableObject
{
    public int defaultLevel = 1;
    public int currentLevel;
    public int score;

    private void OnEnable()
    {
        #if UNITY_EDITOR
        if (!Application.isPlaying)
        {
            ResetToDefaults();
        }
        #endif
    }

    public void ResetToDefaults()
    {
        currentLevel = defaultLevel;
        score = 0;
    }
}
```

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

### Pitfall 4: Modifying ScriptableObjects in Builds

```csharp
// ⚠️ WARNING - Changes persist in builds!
[CreateAssetMenu]
public class PlayerData : ScriptableObject
{
    public int highScore;

    public void SetHighScore(int score)
    {
        highScore = score;
        // In builds, this modifies the asset file!
        // Next time you run the build, it keeps the new value!
    }
}

// ✓ SOLUTION - Use PlayerPrefs or save files for persistent data
[CreateAssetMenu]
public class PlayerData : ScriptableObject
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

- ✓ Shared configuration data
- ✓ Item/enemy/ability databases
- ✓ Runtime collections
- ✓ Constants and enums
- ✓ Editor tools

### Don't Use ScriptableObjects For

- ❌ **Event systems** - Use [DxMessaging](./19-event-systems.md) instead (zero leaks, better
  performance)
- ❌ Per-instance runtime data
- ❌ Frequently changing data (every frame)
- ❌ Data that needs Update/FixedUpdate
- ❌ Scene references
- ❌ Persistent save data (use PlayerPrefs/save files)

### Always Remember To

- ✓ Reset to defaults in OnEnable (Editor only)
- ✓ Clear runtime collections on enable
- ✓ **DON'T use ScriptableObjects for events** - Use [DxMessaging](./19-event-systems.md) instead
- ✓ Avoid scene references
- ✓ Use CreateAssetMenu for easy creation

## Summary

**Golden Rules:**

1. **ScriptableObjects are for shared data**, not instance data
2. **Reset runtime values in OnEnable** for clean Play Mode sessions
3. **DON'T use ScriptableObjects for event systems** - Use [DxMessaging](./19-event-systems.md) for
   automatic cleanup, better performance, and type safety
4. **Don't store scene references** in ScriptableObjects
5. **Use for configuration**, not for data that changes every frame
6. **Clear collections** on enable to avoid stale references
7. **Use PlayerPrefs/save files** for actual persistent data, not ScriptableObjects

ScriptableObjects are incredibly powerful for organizing your game's data and creating decoupled,
maintainable systems. Use them wisely!
