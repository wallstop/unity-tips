# Unity Event Systems: Choosing the Right Pattern

## What Problem Does This Solve?

**The Problem:** Your game has systems that need to communicate (player dies → show game over UI, score changes → update HUD, enemy spawns → play sound). How should these systems talk to each other without creating tight coupling and memory leaks?

**Without Proper Event Systems (The Spaghetti Way):**

```csharp
// ❌ Tight coupling - every system knows about every other system
public class Player : MonoBehaviour {
    public UIManager uiManager;
    public SoundManager soundManager;
    public AchievementManager achievementManager;

    void Die() {
        uiManager.ShowGameOver();      // Direct references everywhere
        soundManager.PlayDeathSound(); // Hard to maintain
        achievementManager.CheckDeaths(); // Can't test in isolation
    }
}
```

**Problems:**
- Tight coupling between systems
- Memory leaks from forgotten event unsubscriptions
- Hard to test individual systems
- Adding new listeners requires modifying existing code

**The Solution:** Event systems decouple components. When player dies, emit one event. Any system can listen independently without the player knowing about them.

---

## Two Approaches: Designer-Driven vs Code-Driven Events

Unity developers typically use one of two patterns for event systems:

1. **ScriptableObject Events (Designer-Driven)** - Asset-based event channels wired through Inspector
2. **Event Bus/Messaging Systems (Code-Driven)** - Type-safe messaging systems managed through code

**Key Insight:** These patterns serve **different team workflows**, not competing technical solutions. Choose based on who creates and modifies events.

---

## Table of Contents

- [Understanding the Two Paradigms](#understanding-the-two-paradigms)
- [ScriptableObject Events (Designer-Driven)](#scriptableobject-events-designer-driven)
- [Event Bus/Messaging (Code-Driven)](#event-busmessaging-code-driven)
- [Feature Comparison](#feature-comparison)
- [Side-by-Side Examples](#side-by-side-examples)
- [When to Use Each](#when-to-use-each)
- [Hybrid Approaches](#hybrid-approaches)
- [Common Pitfalls](#common-pitfalls)

---

<a id="understanding-the-two-paradigms"></a>
## Understanding the Two Paradigms

### Designer-Driven (ScriptableObject Events)

**Philosophy:** Non-programmers create and wire events through Unity Inspector.

**Workflow:**
1. Designer creates event asset in Project window
2. Designer drags asset to prefabs/components
3. Designer wires UnityEvent callbacks in Inspector
4. Events fire, callbacks execute
5. No code changes required

**Best For:** Teams where designers/artists need autonomy to create game flow without programmer intervention.

### Code-Driven (Event Bus/Messaging)

**Philosophy:** Programmers define and wire events through code.

**Workflow:**
1. Programmer defines message struct/class
2. Programmer writes handler methods
3. Programmer registers handlers in code
4. Events fire, handlers execute
5. Designer can adjust *data*, not *flow*

**Best For:** Teams prioritizing type safety, refactoring support, and programmer-controlled architecture.

---

<a id="scriptableobject-events-designer-driven"></a>
## ScriptableObject Events (Designer-Driven)

### Origin and Intent

Popularized by Ryan Hipple's Unite Austin 2017 talk "Game Architecture with Scriptable Objects" ([video](https://www.youtube.com/watch?v=raQ3iHhE_Kk), [source](https://github.com/roboryantron/Unite2017)), this pattern was designed to enable non-programmers to create game flow independently.

**Original Design Goals:**
- Designers create events without writing code
- Animation events trigger prefab responses
- Eliminate cross-scene references that break on despawn
- Enable rapid iteration by non-technical staff

### Proper Implementation

The pattern uses generic base classes with Inspector-driven listener components:

```csharp
// 1. Define generic base class (write once, reuse forever)
public abstract class ScriptableEvent<T> : ScriptableObject {
    private event System.Action<T> OnEventRaised;

    public void Raise(T value) {
        OnEventRaised?.Invoke(value);
    }

    public void Register(System.Action<T> listener) {
        OnEventRaised += listener;
    }

    public void Unregister(System.Action<T> listener) {
        OnEventRaised -= listener;
    }

    private void OnEnable() {
        // Clear stale listeners from previous Play Mode session
        OnEventRaised = null;
    }
}

// 2. Create concrete event types (one line each)
[CreateAssetMenu(menuName = "Events/Int Event")]
public class IntEvent : ScriptableEvent<int> { }

[CreateAssetMenu(menuName = "Events/Float Event")]
public class FloatEvent : ScriptableEvent<float> { }

[CreateAssetMenu(menuName = "Events/Void Event")]
public class VoidEvent : ScriptableEvent<System.Object> { }

// 3. Define listener component base class
public abstract class ScriptableEventListener<T, E> : MonoBehaviour
    where E : ScriptableEvent<T> {

    [SerializeField] private E eventAsset;
    [SerializeField] private UnityEvent<T> response;

    private void OnEnable() {
        eventAsset?.Register(OnEventRaised);
    }

    private void OnDisable() {
        eventAsset?.Unregister(OnEventRaised);
    }

    private void OnEventRaised(T value) {
        response?.Invoke(value);
    }
}

// 4. Create concrete listener components
public class IntEventListener : ScriptableEventListener<int, IntEvent> { }
public class FloatEventListener : ScriptableEventListener<float, FloatEvent> { }
```

### Designer Workflow Example

**Scenario:** Designer wants health changes to update UI and trigger low-health warning.

**Steps (no code required):**
1. Right-click Project → Create → Events → Int Event → name it "OnPlayerHealthChanged"
2. Add `IntEventListener` component to HealthBar prefab
3. Drag "OnPlayerHealthChanged" asset to listener's Event Asset field
4. Wire UnityEvent to `HealthBar.UpdateDisplay()` method in Inspector
5. Add another `IntEventListener` to WarningUI prefab
6. Drag same "OnPlayerHealthChanged" asset
7. Wire UnityEvent to `WarningUI.CheckLowHealth()` method

**Result:** Designer created event chain with zero code changes, zero programmer involvement.

**Important Note on Asset Proliferation:** If the game also needs to track enemy health, boss health, or shield values, the designer must create separate asset instances for each: `OnEnemyHealthChanged`, `OnBossHealthChanged`, `OnPlayerShieldChanged`, etc. Each conceptually similar event (health tracking, damage tracking, score tracking) requires its own asset instance per usage context. This is by design—ScriptableObject events use assets as communication channels, so each distinct channel needs its own asset.

### Raising Events from Code

```csharp
public class Player : MonoBehaviour {
    [SerializeField] private IntEvent onHealthChanged;
    [SerializeField] private VoidEvent onPlayerDied;

    private int health = 100;

    public void TakeDamage(int amount) {
        health -= amount;
        onHealthChanged.Raise(health);

        if (health <= 0) {
            onPlayerDied.Raise(null);
        }
    }
}
```

### Advantages

**Designer Empowerment:**
- ✅ Non-programmers create game flow independently
- ✅ Rapid iteration without code review cycle
- ✅ Visual workflow (drag-drop assets, wire callbacks)
- ✅ Animation events can trigger prefab logic without scripting
- ✅ No code compilation required for event chain changes

**Collaboration Benefits:**
- ✅ Reduces merge conflicts (designers modify assets, programmers modify scripts)
- ✅ Clear separation: programmers build systems, designers orchestrate flow
- ✅ Designers can test event chains without programmer availability

**Technical Benefits:**
- ✅ No external dependencies
- ✅ Simple conceptual model (assets are event channels)
- ✅ Automatic cleanup with proper base class implementation
- ✅ Built into Unity (ScriptableObjects are first-class citizens)

### Disadvantages

**Debugging Challenges:**
- ❌ Cannot trace all listeners to an event without custom editor tools
- ❌ Cannot find all raisers of an event through code search alone
- ❌ Asset references don't appear in "Find References" (IDE limitation)
- ❌ Must check Inspector on every component to verify wiring
- ❌ Event flow invisible without visualizer tools

**Scalability Concerns:**
- ❌ 50+ events require folder organization and naming conventions
- ❌ 100+ events typically need custom editor visualization tools
- ❌ Asset count grows linearly with event types
- ❌ Inspector references can break when moving/renaming assets

**Manual Overhead:**
- ❌ Must define each event type as a concrete class (e.g., `IntEvent`, `FloatEvent`, `HealthChangedEvent`)
- ❌ Must create a separate asset instance for each distinct use case (e.g., `PlayerHealth_SO`, `Enemy1Health_SO`, `Enemy2Health_SO`, `BossHealth_SO`)
- ❌ Asset proliferation: A "health changed" event needs separate instances for player health, each enemy type's health, boss health, etc.
- ❌ Both code churn (defining event types) and asset churn (creating instances for each usage context)
- ❌ Must wire assets in Inspector for every component (manual labor)
- ❌ Must manually update references when refactoring event names (if an in-place rename doesn't work)
- ❌ Problematic Inspector wiring (wrong/no asset = runtime bug)

**Performance Considerations:**
- ⚠️ UnityEvent allocates 136 bytes on first invocation (subsequent invocations don't allocate)[^1]
- ⚠️ UnityEvent is slower than C# events (8-13x in benchmarks, varies by listener count)[^1]
- ⚠️ Passing complex data requires class/struct instances (possible heap allocation) or tuples
- ⚠️ May not be suitable for high-frequency events in performance-critical scenarios

**Missing Advanced Features:**
- ⚠️ Concept is very simple - essentially just actions. Most event busses have advanced features like ordering, global listeners, message mutation, message prevention.

### Best Practices

1. **Always use generic base classes** - Don't create separate event classes manually
2. **Always implement OnEnable() clearing** - Prevents listener accumulation between Play Mode sessions
3. **Use listener components, not code registration** - Embraces designer-driven workflow
4. **Organize assets in folders** - Create Events/ folder with subfolders by category
5. **Naming convention** - Prefix with "On" (OnHealthChanged, OnEnemySpawned)
6. **Document event purpose** - Add [Tooltip] or comment in asset

---

<a id="event-busmessaging-code-driven"></a>
## Event Bus/Messaging (Code-Driven)

### Philosophy and Design

Event buses provide centralized message routing with type-safe, code-driven subscription management. Messages are defined as types (structs/classes) rather than assets.

**Design Goals:**
- Compile-time type safety
- Zero-allocation messaging (struct-based)
- Automatic memory management
- Full IDE support (Find References, Rename, etc.)
- Scalable to thousands of message types

### Comparisons of Modern Event Systems

See a breakdown of modern solutions like UniRx, MessagePipe, Zenject Signals, and DxMessaging [here](https://github.com/wallstop/DxMessaging/blob/master/Docs/Comparisons.md).

### Example: DxMessaging

DxMessaging is a modern Unity messaging system with automatic lifecycle management. [GitHub](https://github.com/wallstop/DxMessaging)

```csharp
// 1. Define message (no asset needed!)
[DxUntargetedMessage]  // Global broadcast
[DxAutoConstructor]    // Generates constructor
public readonly partial struct HealthChanged {
    public readonly int currentHealth;
    public readonly int maxHealth;
}

// 2. Emit message from anywhere
public class Player : MessageAwareComponent {
    private int health = 100;
    private int maxHealth = 100;

    public void TakeDamage(int amount) {
        health -= amount;
        var healthChanged = new HealthChanged(health, maxHealth)
        healthChanged.EmitUntargeted();
    }
}

// 3. Listen for message (automatic cleanup!)
public class HealthBar : MessageAwareComponent {
    [SerializeField] private Image fillImage;

    protected override void RegisterMessageHandlers() {
        _ = Token.RegisterUntargeted<HealthChanged>(OnHealthChanged);
        // Token automatically unsubscribes when destroyed - zero leaks!
    }

    private void OnHealthChanged(ref HealthChanged msg) {
        fillImage.fillAmount = (float)msg.currentHealth / msg.maxHealth;
    }
}

public class WarningUI : MessageAwareComponent {
    protected override void RegisterMessageHandlers() {
        _ = Token.RegisterUntargeted<HealthChanged>(OnHealthChanged);
    }

    private void OnHealthChanged(ref HealthChanged msg) {
        if (msg.currentHealth < msg.maxHealth * 0.3f) {
            ShowLowHealthWarning();
        }
    }
}
```

### Advantages

**Developer Productivity:**
- ✅ Zero memory leaks (automatic cleanup via Token/IDisposable pattern)
- ✅ IDE "Find References" works (find all listeners instantly)
- ✅ IDE "Rename" works (refactor message types automatically)
- ✅ Compile-time type safety (wrong message type = compiler error)
- ✅ No asset creation overhead (pure code)
- ✅ No Inspector wiring required

**Performance:**
- ✅ Zero/Low-allocation design possible with readonly structs (when passed by ref)
- ✅ Can be suitable for high-frequency events (with proper implementation)
- ✅ Avoids UnityEvent overhead
- ✅ Can use cache-friendly struct layouts

**Debugging & Observability:**
- ✅ Full stack traces on message emission
- ✅ Can set breakpoints on message handler registration
- ✅ Built-in Inspector shows all message flow (DxMessaging)
- ✅ Can trace all listeners through "Find References"

**Scalability:**
- ✅ Scales to thousands of message types (no asset overhead)
- ✅ Namespace organization for large projects
- ✅ No Inspector reference breakage on refactors
- ✅ New developers use "Find References" to understand flow

### Disadvantages

**Programmer-Required:**
- ⚠️ Designers cannot create new messages without code
- ⚠️ Designers cannot wire event chains through Inspector
- ⚠️ Requires programming knowledge to modify flow
- ⚠️ Less visual feedback (no asset graph, unless custom tools built)

**External Dependency:**
- ⚠️ Requires package installation (not built into Unity)
- ⚠️ Team must learn specific library's patterns
- ⚠️ Package maintenance risk (though many are well-maintained)

**Learning Curve:**
- ⚠️ More complex than ScriptableObject concept
- ⚠️ Multiple message types (Untargeted, Targeted, Broadcast) to understand
- ⚠️ Requires understanding of memory management patterns

### Best Practices

1. **Use readonly structs with ref parameters** - Minimizes allocations and prevents accidental mutations
2. **Namespace organization** - Group related messages (Gameplay.Combat.*, UI.Dialogs.*)
3. **Descriptive message names** - Past tense for events (PlayerDied), present for state (HealthChanged)
4. **Minimal message data** - Only include essential information
5. **Unregister in OnDisable** - Or use lifecycle-aware base classes
6. **Document message contracts** - XML comments explaining when/why message fires

### Performance Reality Check

While event buses **can** be more performant than UnityEvents, claiming "zero allocations" oversimplifies reality:

**What Actually Happens:**
- ✅ Readonly structs passed by `ref` avoid copying
- ✅ Avoids UnityEvent's reflection overhead
- ⚠️ Listener storage still requires memory (lists, dictionaries, etc.)
- ⚠️ Delegate creation/caching affects allocations
- ⚠️ Boxing occurs if structs are cast to interfaces or stored in object fields
- ⚠️ Large structs (>16 bytes) passed by value cause expensive copying

**Actual Allocation Sources in Message Buses:**
1. Listener registration (dictionary/list growth)
2. Delegate allocation (unless pre-cached)
3. Message routing data structures
4. Boxing if implementation uses object/interface storage

**The Truth:** Well-implemented event buses have **lower** allocations than UnityEvents, not necessarily **zero** allocations. Always profile your specific implementation.

---

<a id="feature-comparison"></a>
## Feature Comparison

| Feature | ScriptableObject Events | Event Bus/Messaging |
|---------|------------------------|---------------------|
| **Workflow** |
| Designer creates events | ✅ Yes (Inspector only) | ❌ No (code required) |
| Programmer creates events | ⚠️ Verbose (type definition + asset instances) | ✅ Simple (message struct) |
| Asset/instance overhead | ❌ Separate asset per use case | ✅ Single type for all uses |
| Visual event wiring | ✅ Inspector drag-drop | ❌ Code-only |
| Animation event integration | ✅ Excellent | ⚠️ Requires wrapper |
| **Technical** |
| Memory management | ⚠️ Manual (proper base class helps) | ✅ Automatic |
| Memory leak risk | ⚠️ Moderate (if base classes not used) | ✅ Zero/Minimal (with lifecycle management) |
| Compile-time type safety | ❌ Inspector wiring | ✅ Full |
| Performance (allocations) | ⚠️ UnityEvent overhead | ✅ Low-allocation (with structs) |
| High-frequency events | ⚠️ May be problematic | ✅ Can handle well |
| **Debugging** |
| Find all listeners | ❌ Custom tools needed | ✅ "Find References" |
| Find all emitters | ⚠️ String search | ✅ "Find References" |
| Stack traces | ✅ Yes | ✅ Yes |
| Runtime inspection | ⚠️ UnityEvent list | ✅ Built-in (DxMessaging) |
| **Refactoring** |
| Rename event | ❌ Manual Inspector updates | ✅ IDE rename |
| Find usages | ❌ Asset search | ✅ IDE search |
| Break-on-change | ❌ Runtime errors | ✅ Compile errors |
| **Scalability** |
| 1-20 event instances | ✅ Simple | ✅ Simple |
| 20-100 event instances | ⚠️ Needs organization | ✅ Simple |
| 100+ event instances | ❌ Custom tools required | ✅ Scales naturally |
| Asset/type count growth | ❌ O(n) per usage context | ✅ O(1) per semantic type |
| **Dependencies** |
| External packages | ✅ None | ⚠️ Required |
| Unity version | ✅ Any | ⚠️ Package dependent |
| **Team Dynamics** |
| Non-programmer autonomy | ✅ Full | ❌ None |
| Merge conflicts | ✅ Reduced | ⚠️ Code conflicts |
| Onboarding time | ✅ Low (visual) | ⚠️ Moderate (code concepts) |

**Summary:** ScriptableObject events excel at designer empowerment and visual workflows. Event buses excel at programmer productivity, performance, and scalability.

---

<a id="side-by-side-examples"></a>
## Side-by-Side Examples

### Example 1: Player Death Event

#### ScriptableObject Approach (Designer-Driven)

```csharp
// === Programmer creates base classes (once) ===
public abstract class ScriptableEvent<T> : ScriptableObject {
    private event System.Action<T> OnEventRaised;
    public void Raise(T value) => OnEventRaised?.Invoke(value);
    public void Register(System.Action<T> listener) => OnEventRaised += listener;
    public void Unregister(System.Action<T> listener) => OnEventRaised -= listener;
    private void OnEnable() => OnEventRaised = null;
}

[CreateAssetMenu(menuName = "Events/Void Event")]
public class VoidEvent : ScriptableEvent<System.Object> { }

public class VoidEventListener : ScriptableEventListener<System.Object, VoidEvent> { }

// === Programmer creates raiser ===
public class Player : MonoBehaviour {
    [SerializeField] private VoidEvent onPlayerDied;

    void Die() {
        onPlayerDied.Raise(null);
    }
}

// === Designer workflow (no code!) ===
// 1. Right-click → Create → Events → Void Event → "OnPlayerDied"
// 2. Add VoidEventListener to UIManager
// 3. Drag OnPlayerDied asset to listener
// 4. Wire UnityEvent to UIManager.ShowGameOver()
// 5. Add VoidEventListener to AchievementManager
// 6. Drag OnPlayerDied asset to listener
// 7. Wire UnityEvent to AchievementManager.CheckDeathAchievements()
```

**Designer Outcome:** Two listeners wired with zero code changes, no programmer involvement needed.

#### Event Bus Approach (Code-Driven)

```csharp
// === Programmer defines message ===
[DxUntargetedMessage]
[DxAutoConstructor]
public readonly partial struct PlayerDied { }

// === Programmer creates raiser ===
public class Player : MonoBehaviour {
    void Die() {
        var playerDied = new PlayerDied();
        playerDied.EmitUntargeted();
    }
}

// === Programmer creates listeners ===
public class UIManager : MessageAwareComponent {
    protected override void RegisterMessageHandlers() {
        _ = Token.RegisterUntargeted<PlayerDied>(OnPlayerDied);
    }

    void OnPlayerDied(ref PlayerDied msg) {
        ShowGameOver();
    }
}

public class AchievementManager : MessageAwareComponent {
    protected override void RegisterMessageHandlers() {
        _ = Token.RegisterUntargeted<PlayerDied>(OnPlayerDied);
    }

    void OnPlayerDied(ref PlayerDied msg) {
        CheckDeathAchievements();
    }
}
```

**Programmer Outcome:** Compile-time safety, automatic cleanup, "Find References" shows all listeners instantly.

---

### Example 2: Health System with UI Updates

#### ScriptableObject Approach

```csharp
// === Programmer setup ===
[CreateAssetMenu(menuName = "Events/Int Event")]
public class IntEvent : ScriptableEvent<int> { }

public class IntEventListener : ScriptableEventListener<int, IntEvent> { }

public class Player : MonoBehaviour {
    [SerializeField] private IntEvent onHealthChanged;
    private int health = 100;

    public void TakeDamage(int damage) {
        health -= damage;
        onHealthChanged.Raise(health);
    }
}

// === Designer workflow ===
// 1. Create IntEvent asset "OnHealthChanged"
// 2. Add IntEventListener to HealthBar
// 3. Wire to HealthBar.UpdateDisplay(int)
// 4. Add IntEventListener to WarningUI
// 5. Wire to WarningUI.CheckLowHealth(int)
```

**Challenge:** Designer can wire callbacks, but callbacks must accept `int`. If HealthBar needs current + max health, requires more complex event type or multiple events.

#### Event Bus Approach

```csharp
// === Programmer implementation ===
[DxUntargetedMessage]
[DxAutoConstructor]
public readonly partial struct HealthChanged {
    public readonly int current;
    public readonly int max;
}

public class Player : MessageAwareComponent {
    private int health = 100;
    private int maxHealth = 100;

    public void TakeDamage(int damage) {
        health -= damage;
        var healthChanged = new HealthChanged(health, maxHealth);
        healthChanged.EmitUntargeted();
    }
}

public class HealthBar : MessageAwareComponent {
    [SerializeField] private Image fillImage;

    protected override void RegisterMessageHandlers() {
        _ = Token.RegisterUntargeted<HealthChanged>(OnHealthChanged);
    }

    void OnHealthChanged(ref HealthChanged msg) {
        fillImage.fillAmount = (float)msg.current / msg.max;
    }
}

public class WarningUI : MessageAwareComponent {
    protected override void RegisterMessageHandlers() {
        _ = Token.RegisterUntargeted<HealthChanged>(OnHealthChanged);
    }

    void OnHealthChanged(ref HealthChanged msg) {
        if (msg.current < msg.max * 0.3f) {
            ShowWarning();
        }
    }
}
```

**Benefit:** Message includes both current and max health. Type-safe access. Minimal allocations when using structs passed by ref.

---

### Example 3: Complex Multi-Parameter Event

#### ScriptableObject Approach

```csharp
// === Programmer creates event with tuple ===
[CreateAssetMenu(menuName = "Events/Damage Event")]
public class DamageEvent : ScriptableEvent<(int amount, GameObject attacker, DamageType type)> { }

public class DamageEventListener :
    ScriptableEventListener<(int, GameObject, DamageType), DamageEvent> { }

// === Usage ===
public class Weapon : MonoBehaviour {
    [SerializeField] private DamageEvent onDamageDealt;

    void DealDamage(GameObject target, int amount, DamageType type) {
        onDamageDealt.Raise((amount, this.gameObject, type));
    }
}

// === Designer workflow ===
// Must wire UnityEvent<(int, GameObject, DamageType)> in Inspector
// UnityEvent doesn't natively support tuples well - requires wrapper method
```

**Challenge:** Tuples work in code but awkward with UnityEvents. Designers may need programmer to create wrapper methods.

#### Event Bus Approach

```csharp
// === Programmer implementation ===
[DxTargetedMessage]
[DxAutoConstructor]
public readonly partial struct TakeDamage {
    public readonly int amount;
    public readonly GameObject attacker;
    public readonly DamageType type;
}

public class Weapon : MonoBehaviour {
    void DealDamage(GameObject target, int amount, DamageType type) {
        if (target.TryGetComponent<HealthComponent>(out var health)) {
            var takeDamage = new TakeDamage(amount, gameObject, type);
            takeDamage.EmitComponentTargeted(health);
        }
    }
}

public class HealthComponent : MessageAwareComponent {
    protected override void RegisterMessageHandlers() {
        _ = Token.RegisterComponentTargeted<TakeDamage>(this, OnTakeDamage);
    }

    void OnTakeDamage(ref TakeDamage msg) {
        // Handle damage with full type-safe access
        ApplyDamage(msg.amount, msg.type);
        LogAttacker(msg.attacker);
    }
}
```

**Benefit:** Clean struct with named fields. Minimal allocations with ref parameters. Targeted delivery (only damaged component receives).

---

### Example 4: Multiple Entities with Same Event Type (Asset Proliferation)

#### ScriptableObject Approach

```csharp
// === Programmer defines base event type (once) ===
[CreateAssetMenu(menuName = "Events/Int Event")]
public class IntEvent : ScriptableEvent<int> { }

// === Designer must create separate asset instances for each usage ===
// Project Assets:
//   Events/
//     OnPlayerHealthChanged (IntEvent asset)
//     OnEnemy1HealthChanged (IntEvent asset)
//     OnEnemy2HealthChanged (IntEvent asset)
//     OnBossHealthChanged (IntEvent asset)
//     OnPlayerShieldChanged (IntEvent asset)
//     OnPlayerManaChanged (IntEvent asset)
//     ... (more assets as game grows)

public class Player : MonoBehaviour {
    [SerializeField] private IntEvent onPlayerHealthChanged;
    [SerializeField] private IntEvent onPlayerShieldChanged;
    [SerializeField] private IntEvent onPlayerManaChanged;
    // Designer must wire three different asset instances in Inspector
}

public class Enemy : MonoBehaviour {
    [SerializeField] private IntEvent onEnemyHealthChanged;
    // Each enemy prefab needs its own dedicated asset instance
    // Enemy1 can't share the same asset as Enemy2 if they need independent tracking
}
```

**Reality Check:** For a game with:
- 1 player (health, shield, mana) = 3 IntEvent assets
- 5 enemy types (health each) = 5 IntEvent assets
- 3 bosses (health, shield each) = 6 IntEvent assets
- 10 UI elements (score, timer, etc.) = 10+ more assets

**Total: 24+ IntEvent asset instances**, all from one `IntEvent` type definition. Each asset must be created, named, organized in folders, and manually wired in Inspector.

#### Event Bus Approach

```csharp
// === Programmer defines message types (once per semantic concept) ===
[DxBroadcastMessage]
[DxAutoConstructor]
public readonly partial struct HealthChanged {
    public readonly int current;
    public readonly int max;
}

[DxBroadcastMessage]
[DxAutoConstructor]
public readonly partial struct ShieldChanged {
    public readonly int current;
    public readonly int max;
}

// === All entities use the same message type ===
public class Player : MessageAwareComponent {
    private int health = 100;

    public void TakeDamage(int damage) {
        health -= damage;
        var healthChanged = new HealthChanged(health, 100);
        healthChanged.EmitGameObjectBroadcast(gameObject);
        // Same type for player, no asset needed
    }
}

public class Enemy : MessageAwareComponent {
    private int health = 50;

    public void TakeDamage(int damage) {
        health -= damage;
        var healthChanged = new HealthChanged(health, 50);
        healthChanged.EmitGameObjectBraodcast(gameObject);
        // Same HealthChanged type, works for all enemies
    }
}

public class HealthBar : MessageAwareComponent {

    protected override void RegisterMessageHandlers() {
        _ = Token.RegisterGameObjectBroadcast<HealthChanged>(gameObject, OnHealthChanged);
    }

    void OnHealthChanged(ref HealthChanged msg) {
        UpdateDisplay(msg.current, msg.max);
    }
}
```

**Reality Check:** For the same game:
- 2 message type definitions (`HealthChanged`, `ShieldChanged`)
- 0 asset instances
- All entities share the same message types
- Filtering by entity happens in code, not asset wiring

**Summary:** ScriptableObject events require **O(n) assets per usage context**. Event buses require **O(1) message type definitions per semantic concept**. This is the core scalability difference.

---

<a id="when-to-use-each"></a>
## When to Use Each

### Use ScriptableObject Events When:

| Scenario | Why |
|----------|-----|
| **Non-programmers create game flow** | Designers/artists need autonomy without code review |
| **Animation-driven events** | Animator needs to trigger prefab logic without code |
| **Rapid prototyping by mixed teams** | Game jams, quick prototypes with non-technical staff |
| **Low event count (< 50)** | Simple games where asset overhead is minimal |
| **Inspector-centric workflow** | Team prefers visual wiring over code |
| **Zero external dependencies** | Cannot use packages, Unity-only |
| **Event frequency < 10000/second** | Performance overhead acceptable |

**Example Use Cases:**
- Cutscene system where designers wire animation events to game responses
- Educational project where students learn Unity through visual scripting
- Mobile puzzle game with 10 simple events (LevelComplete, ScoreChanged, etc.)
- Prefab-based game where designers assemble levels from pre-built pieces

### Use Event Bus/Messaging When:

| Scenario | Why |
|----------|-----|
| **Programmer-centric team** | Developers prefer code over Inspector wiring |
| **High event count (> 50)** | Scalability matters, asset overhead unacceptable |
| **Performance critical** | Mobile/VR where GC spikes cause frame drops |
| **High-frequency events** | Damage ticks, input polling, collision checks |
| **Complex message data** | Multi-parameter messages with type safety |
| **Long-term maintainability** | Need refactoring support, "Find References" |
| **Large team** | Need traceability, code review, compile errors vs runtime errors |

**Example Use Cases:**
- Multiplayer game with hundreds of network messages
- Action RPG with damage system firing 60+ times/second
- Large project with 20+ programmers needing clear code contracts
- Systems programming (AI, physics, state machines) with complex data flow

### Hybrid Approaches

Many successful projects use **both patterns** for different purposes:

**Example Architecture:**
- **ScriptableObject Events** for designer-facing game events (UI triggers, level progression, cutscenes)
- **Event Bus** for system-level communication (combat, networking, state machines)

```csharp
// Designer-driven: Level designer triggers victory sequence
[CreateAssetMenu(menuName = "Events/Void Event")]
public class VoidEvent : ScriptableEvent<System.Object> { }

// Code-driven: Combat system with high-frequency damage
[DxTargetedMessage]
public readonly partial struct TakeDamage {
    public readonly int amount;
    public readonly DamageType type;
}
```

**Benefits of Hybrid:**
- ✅ Designers work independently on game flow
- ✅ Programmers maintain performance-critical systems
- ✅ Clear separation: gameplay events vs system events

**Challenges of Hybrid:**
- ⚠️ Team must learn both patterns
- ⚠️ Inconsistent architecture can confuse new developers
- ⚠️ Must establish clear conventions for which pattern when

---

<a id="common-pitfalls"></a>
## Common Pitfalls

### Pitfall 1: ScriptableObject Memory Leaks (Code-Driven Pattern)

**The Problem:** Many developers use ScriptableObjects with code-based registration (OnEnable/OnDisable), conflating code-driven and designer-driven patterns.

```csharp
// ❌ WRONG: Using ScriptableObjects in code-driven pattern
[CreateAssetMenu]
public class GameEvent : ScriptableObject {
    private event System.Action OnEventRaised;
    public void Raise() => OnEventRaised?.Invoke();
    public void Register(System.Action listener) => OnEventRaised += listener;
    public void Unregister(System.Action listener) => OnEventRaised -= listener;
}

public class Listener : MonoBehaviour {
    [SerializeField] private GameEvent gameEvent;

    void OnEnable() {
        gameEvent.Register(HandleEvent);  // Code registration
    }

    void OnDisable() {
        gameEvent.Unregister(HandleEvent);  // Easy to forget!
    }
}
```

**Why This Is Wrong:**
- Combines worst of both worlds: asset creation overhead + manual code management
- No designer autonomy (requires code changes)
- Memory leak risk if OnDisable forgotten
- Asset overhead with no designer benefit

**Solution A:** Use proper designer-driven pattern with listener components
**Solution B:** Switch to event bus for code-driven pattern

### Pitfall 2: Not Clearing ScriptableObject Listeners in OnEnable

```csharp
// ❌ PROBLEM: Listeners can accumulate between Play Mode sessions within Editor
[CreateAssetMenu]
public class GameEvent : ScriptableObject {
    private readonly List<GameEventListener> listeners = new List<GameEventListener>();

    // Missing OnEnable() clear!
}

// ✅ SOLUTION: Always clear in OnEnable
[CreateAssetMenu]
public class GameEvent : ScriptableObject {
    private readonly List<GameEventListener> listeners = new List<GameEventListener>();

    private void OnEnable() {
        listeners.Clear();  // Clear stale references
    }
}
```

**References:**
- Unity Issue Tracker: "Memory leak when subscribing to C# event in referenced serialized ScriptableObject" ([Stack Overflow](https://stackoverflow.com/questions/58334248/how-do-i-avoid-memory-leak-in-unity-when-subscribing-to-c-sharp-event-in-referen))
- Unity Memory Profiler documentation on managed shell objects ([Unity Docs](https://docs.unity3d.com/Packages/com.unity.memoryprofiler@1.1/manual/managed-shell-objects.html))

### Pitfall 3: Wrong Event Asset in Inspector (Runtime Bug)

```csharp
// ❌ PROBLEM: No compile-time safety
public class ScoreUI : MonoBehaviour {
    [SerializeField] private IntEvent onScoreChanged;  // IntEvent

    void OnEnable() {
        onScoreChanged.Register(UpdateDisplay);
    }

    void UpdateDisplay(int newScore) {
        scoreText.text = newScore.ToString();
    }
}
// If designer accidentally wires "onHealthChanged" asset instead of "onScoreChanged",
// you get wrong events at runtime with no warning!
```

**Solution:** Use event bus with compile-time type safety:

```csharp
// ✅ SOLUTION: Compiler enforces correct type
public class ScoreUI : MessageAwareComponent {
    protected override void RegisterMessageHandlers() {
        _ = Token.RegisterUntargeted<ScoreChanged>(UpdateDisplay);
        // Compiler error if ScoreChanged doesn't exist or is wrong type
    }
}
```

### Pitfall 4: Using ScriptableObjects for High-Frequency Events

```csharp
// ❌ BAD: 60 damage events per second
[CreateAssetMenu]
public class IntEvent : ScriptableObject {
    private event System.Action<int> OnEventRaised;
    public void Raise(int value) {
        OnEventRaised?.Invoke(value);  // UnityEvent allocates garbage
    }
}

void Update() {
    // Fire damage every frame
    onDamageEvent.Raise(10);  // GC pressure!
}
```

**Performance Impact:** UnityEvent is slower than C# events (8-13x in benchmarks)[^1] and allocates 136 bytes on first dispatch. For high-frequency events (60+ per second), this overhead can accumulate. However, frequent AddListener/RemoveListener calls allocate new listener arrays each time, causing additional GC pressure with dynamic subscriptions.

**Solution:** For high-frequency events, use event bus with struct messages:

```csharp
// ✅ BETTER: Lower allocations with structs
[DxUntargetedMessage]
public readonly partial struct DamageDealt {
    public readonly int amount;
}

void Update() {
    var damageDealt = new DamageDealt(10);
    damageDealt.EmitUntargeted();  // Minimal allocations (depends on implementation)
}
```

**Note:** Actual allocation behavior depends on the specific message bus implementation and how it manages listener storage and invocation.

### Pitfall 5: Event Bus Without Proper Cleanup

```csharp
// ❌ WRONG: Manual registration without automatic cleanup
public class Listener : MonoBehaviour {
    void OnEnable() {
        MessageBus.Subscribe<PlayerDied>(HandleEvent);
    }

    // Forgot OnDisable! Memory leak!
}

// ✅ CORRECT: Use lifecycle-aware base class
public class Listener : MessageAwareComponent {
    protected override void RegisterMessageHandlers() {
        _ = Token.RegisterUntargeted<PlayerDied>(HandleEvent);
        // Token automatically unsubscribes when destroyed
    }
}
```

### Pitfall 6: Overusing Global Events

```csharp
// ❌ BAD: Everything is global broadcast
[DxUntargetedMessage]
public readonly partial struct DamageDealt { }

// 100 enemies, 100 damage events/second = 10,000 broadcast checks

// ✅ GOOD: Use targeted messages
[DxTargetedMessage]
public readonly partial struct TakeDamage {
    public readonly int amount;
}

// Only the damaged component receives message
var takeDamage = new TakeDamage(50);
takeDamage.EmitComponentTargeted(targetHealth);
```

---

## Performance Comparison

### Allocation Test: 10,000 Events with Multiple Parameters

**Test Setup:**
```csharp
// Fire 10,000 events with 3 parameters (int, Vector3, GameObject)
```

**ScriptableObject Events (UnityEvent):**
```csharp
[System.Serializable]
public class DamageData {
    public int amount;
    public Vector3 hitPoint;
    public GameObject attacker;
}

[CreateAssetMenu]
public class DamageEvent : ScriptableObject {
    private UnityEvent<DamageData> OnEventRaised;
    public void Raise(DamageData data) {
        OnEventRaised?.Invoke(data);
    }
}

// Test
for (int i = 0; i < 10000; i++) {
    var data = new DamageData {
        amount = i,
        hitPoint = Vector3.zero,
        attacker = gameObject
    };
    damageEvent.Raise(data);
}
```

**Result:**
- **~400 KB allocations** (DamageData class instances: 10,000 × ~40 bytes)
- **~50-100ms total execution time** (UnityEvent is 6-40x slower than C# events[^1])
- **1-2 GC collections**

**Event Bus (DxMessaging with Readonly Struct):**
```csharp
[DxUntargetedMessage]
[DxAutoConstructor]
public readonly partial struct DamageDealt {
    public readonly int amount;
    public readonly Vector3 hitPoint;
    public readonly GameObject attacker;
}

// Test
for (int i = 0; i < 10000; i++) {
    var damageDealt= new DamageDealt(i, Vector3.zero, gameObject);
    damageDealt.EmitUntargeted();
}
```

**Result (varies by implementation):**
- **Minimal allocations** (readonly struct passed by ref reduces copies)
- **Note:** Actual allocation depends on the message bus implementation details (listener storage, delegate allocation, etc.)
- **Faster than UnityEvent** (avoids reflection overhead)

**Conclusion:** For performance-critical high-frequency events, code-driven event systems can be optimized for lower allocations and faster execution. For low-frequency events (UI, progression), UnityEvent's overhead is usually acceptable. Always profile your specific use case.

**Important Caveats:**
- "Zero allocation" claims depend on implementation details (how listeners are stored, whether delegates are cached, etc.)
- Structs can still cause allocations if boxed (cast to interface, stored in object, etc.)
- Passing large structs by value causes copying overhead; use `ref` or `in` parameters
- The actual performance difference varies significantly based on Unity version, platform, and usage patterns

[^1]: Jackson Dunstan, ["Event Performance: C# vs. UnityEvent"](https://www.jacksondunstan.com/articles/3335) - Benchmarks show UnityEvent is 8-13x slower than C# events (tested on Unity 5.3.1f1, 10M iterations with 2 listeners). UnityEvent allocates 136 bytes on first dispatch, zero on subsequent dispatches. These benchmarks are from 2015 and may not reflect current Unity versions.

---

## Quick Decision Guide

```
Do non-programmers need to create/modify event flow?
│
├─ YES → ScriptableObject Events
│   │
│   ├─ Will you have > 50 event types?
│   │   ├─ YES → Consider event bus (scaling issues)
│   │   └─ NO → ScriptableObject Events are good fit
│   │
│   └─ High-frequency events (>10000/second)?
│       ├─ YES → Hybrid: event bus for these, ScriptableObjects for others
│       └─ NO → ScriptableObject Events are good fit
│
└─ NO → Event Bus/Messaging
    │
    ├─ Team comfortable with external packages?
    │   ├─ YES → Use DxMessaging or similar
    │   └─ NO → Implement simple event bus or reconsider ScriptableObjects
    │
    └─ Need compile-time safety and refactoring support?
        ├─ YES → Event Bus is best choice
        └─ NO → Either pattern works
```

---

## Summary

### Key Insights

1. **ScriptableObject Events and Event Buses serve different workflows**, not competing technical solutions
2. **ScriptableObject Events** excel when **designers need autonomy** to create game flow without programmer bottlenecks
3. **Event Buses** excel when **programmers prioritize type safety**, performance, and refactoring support
4. **Hybrid approaches** are valid: designer-driven for gameplay, code-driven for systems
5. **Neither pattern is universally superior** - choose based on team composition and project needs

### Recommendations by Project Type

**Small Prototype (< 1 month, < 20 events):**
- ScriptableObject Events if mixed team
- Event Bus if programmer-only

**Medium Game (3-12 months, 20-100 events):**
- Hybrid approach (both patterns for different purposes)
- Pure event bus if programmer-centric team

**Large Game (> 12 months, 100+ events):**
- Event bus for system architecture
- ScriptableObjects for designer-facing game events (if needed)

**Live Service Game:**
- Event bus (refactoring support critical for ongoing development)

### Golden Rules

**For ScriptableObject Events:**
1. Use generic base classes, not hand-written event classes
2. Always clear listeners in `OnEnable()` on ScriptableObject
3. Use listener components for designer-driven workflow, not code registration
4. Organize assets in folders with clear naming conventions
5. Profile performance for high-frequency events to ensure acceptable overhead

**For Event Bus:**
1. Use readonly structs (passed by ref) to minimize allocations and copying
2. Use lifecycle-aware base classes (MessageAwareComponent) for automatic cleanup
3. Choose appropriate message type (Untargeted, Targeted, Broadcast)
4. Namespace organization for large projects
5. Document message contracts with XML comments
6. Avoid boxing structs (casting to interfaces, storing in object fields)

**Universal:**
1. **Don't mix patterns haphazardly** - establish clear conventions
2. **Measure before optimizing** - profile to confirm performance needs
3. **Consider team composition** - designer empowerment vs programmer control
4. **Plan for scale** - 100+ events require different strategy than 10

---

## Additional Resources

### ScriptableObject Events
- **[Ryan Hipple's Unite 2017 Talk](https://www.youtube.com/watch?v=raQ3iHhE_Kk)** - Original "Game Architecture with Scriptable Objects" presentation
- **[Unite 2017 Sample Project](https://github.com/roboryantron/Unite2017)** - Official sample code from Ryan Hipple's talk
- **[Unity Official Guide](https://unity.com/how-to/architect-game-code-scriptable-objects)** - Architect your code for efficient changes with ScriptableObjects

### Event Bus/Messaging Systems
- **[DxMessaging GitHub](https://github.com/wallstop/DxMessaging)** - Modern Unity messaging system with automatic lifecycle management
- **[MessageBus Article](https://www.gamedeveloper.com/programming/fixing-unity-s-tendency-to-object-coupling-the-messagebus)** - Fixing Unity's tendency to object coupling

### Memory Management
- **[Unity Memory Profiler](https://docs.unity3d.com/Packages/com.unity.memoryprofiler@1.1/manual/managed-shell-objects.html)** - Analyzing memory leaks
- **[Stack Overflow: ScriptableObject Event Memory Leaks](https://stackoverflow.com/questions/58334248/how-do-i-avoid-memory-leak-in-unity-when-subscribing-to-c-sharp-event-in-referen)** - Common leak patterns

### Architecture
- **[ScriptableObjects Best Practices](./08-scriptable-objects.md)** - General ScriptableObject patterns
- **[Performance & Memory](./07-performance-memory.md)** - GC optimization strategies

---

**Choose thoughtfully, implement consistently, and measure results.** Both patterns are legitimate architectural choices when applied to their intended use cases.
