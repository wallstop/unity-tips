# Unity Serialization Best Practices

## What Problem Does This Solve?

**The Problem:** You mark a field `[SerializeField]` but it doesn't appear in the Inspector. Or it
shows in Inspector but resets to default after saving. Unity's serialization system has strict rules
that aren't obvious.

**Why This Happens:** Unity's serialization system is designed for performance and editor
integration, not flexibility. It only supports specific types and structures to ensure fast scene
loading and reliable Inspector editing.

**Common Frustrations:**

- Dictionaries don't serialize (most requested feature for 10+ years)
- Properties don't serialize (only fields do)
- Polymorphic fields don't serialize correctly
- Using `public` fields everywhere breaks encapsulation

**The Solution:** Understanding Unity's serialization rules prevents hours of debugging "Why isn't
this saving?" problems and helps you write maintainable code with proper encapsulation.

---

## ⚠️ Critical Rules

**The most common serialization mistakes:**

1. Using `public` fields instead of `[SerializeField] private`
2. Not understanding what Unity can/can't serialize
3. Exposing implementation details unnecessarily
4. Not using `[HideInInspector]` or `[Header]` for organization

## Table of Contents

- [SerializeField vs Public](#serializefield-vs-public)
- [What Unity Can Serialize](#what-unity-can-serialize)
- [Inspector Organization](#inspector-organization)
- [Common Attributes](#common-attributes)
- [Best Practices](#best-practices)
- [Common Pitfalls](#common-pitfalls)

## SerializeField vs Public

### The Golden Rule

**Always prefer `[SerializeField] private` over `public`!**

```csharp
// ❌ BAD - Public exposes internal implementation
public float moveSpeed = 5f;
public Transform target;
public int currentHealth;

// ✓ GOOD - SerializeField keeps encapsulation
[SerializeField] private float moveSpeed = 5f;
[SerializeField] private Transform target;

// Current health shouldn't be editable
private int currentHealth;
```

### Why SerializeField is Better

```csharp
public class Player : MonoBehaviour
{
    // ❌ PUBLIC FIELDS - Accessible from anywhere!
    public int maxHealth = 100;
    public int currentHealth = 100;

    public void TakeDamage(int damage)
    {
        currentHealth -= damage;
    }
}

// Problem: Other scripts can break your logic
public class BadCode : MonoBehaviour
{
    public Player player;

    private void Start()
    {
        // Whoops! Bypassed TakeDamage logic
        player.currentHealth = 0;
    }
}
```

```csharp
// ✓ CORRECT - Proper encapsulation
public class Player : MonoBehaviour
{
    // Visible in Inspector, but not accessible from other scripts
    [SerializeField] private int maxHealth = 100;

    // Not visible in Inspector or other scripts
    private int currentHealth;

    private void Awake()
    {
        currentHealth = maxHealth;
    }

    // Controlled access through methods
    public void TakeDamage(int damage)
    {
        currentHealth = Mathf.Max(0, currentHealth - damage);

        if (currentHealth == 0)
        {
            Die();
        }
    }

    public int GetCurrentHealth() => currentHealth;
}

// Now other scripts can't break our logic
public class GoodCode : MonoBehaviour
{
    [SerializeField] private Player player;

    private void Start()
    {
        // Must use proper method - can't bypass logic
        player.TakeDamage(50);
    }
}
```

### When to Use Each

```csharp
public class ComponentExamples : MonoBehaviour
{
    // ✓ SerializeField: Inspector-editable, private to other scripts
    [SerializeField] private float moveSpeed = 5f;
    [SerializeField] private GameObject prefab;
    [SerializeField] private Transform target;

    // ✓ Private: Internal state, not in Inspector
    private int currentScore;
    private bool isAlive;
    private List<Enemy> activeEnemies = new List<Enemy>();

    // ✓ Public Property: Controlled access
    public int CurrentScore => currentScore;
    public bool IsAlive => isAlive;

    // ✓ Public Method: Controlled modification
    public void AddScore(int points)
    {
        currentScore += points;
        OnScoreChanged?.Invoke(currentScore);
    }

    // ⚠️ Rare: Public field only for simple data containers
    // Generally avoid this!
}

// Example of when public fields are OK:
[System.Serializable]
public class ItemData
{
    public string itemName;
    public Sprite icon;
    public int value;
    // Simple data container - no behavior to protect
}
```

## What Unity Can Serialize

### Unity CAN Serialize

```csharp
// ✓ Basic types
[SerializeField] private int health;
[SerializeField] private float speed;
[SerializeField] private bool isActive;
[SerializeField] private string playerName;

// ✓ Unity types
[SerializeField] private Vector3 position;
[SerializeField] private Color tintColor;
[SerializeField] private LayerMask targetLayers;

// ✓ Unity Object references
[SerializeField] private GameObject prefab;
[SerializeField] private Transform target;
[SerializeField] private Material material;
[SerializeField] private AudioClip sound;

// ✓ Enums
public enum EnemyType { Normal, Fast, Tank }
[SerializeField] private EnemyType enemyType;

// ✓ Arrays and Lists (of serializable types)
[SerializeField] private int[] scores;
[SerializeField] private List<Transform> waypoints;
[SerializeField] private GameObject[] spawnPoints;

// ✓ Custom classes marked [Serializable]
[System.Serializable]
public class PlayerStats
{
    public int maxHealth;
    public float moveSpeed;
    public int level;
}

[SerializeField] private PlayerStats stats;
```

### Unity CANNOT Serialize

```csharp
// ❌ Dictionaries (use custom wrapper)
private Dictionary<string, int> inventory; // Won't save!

// ❌ Properties
[SerializeField] private int Health { get; set; } // Won't work!

// ❌ Static fields
[SerializeField] private static int globalScore; // Won't serialize!

// ❌ const fields
[SerializeField] private const int MAX_LEVEL = 100; // Won't serialize!

// ❌ Delegates/Events
[SerializeField] private System.Action onComplete; // Won't serialize!

// ❌ Classes without [Serializable]
public class CustomClass { } // Won't serialize
[SerializeField] private CustomClass data; // Won't work!

// ❌ Generic classes (mostly)
[System.Serializable]
public class GenericClass<T> { public T value; }
[SerializeField] private GenericClass<int> data; // Won't work!
```

### Serializing Complex Data

```csharp
// ✓ CORRECT - Wrapper for Dictionary
[System.Serializable]
public class StringIntPair
{
    public string key;
    public int value;
}

public class InventorySystem : MonoBehaviour
{
    // Serialize as list, convert to dictionary at runtime
    [SerializeField] private List<StringIntPair> inventoryData;

    private Dictionary<string, int> inventory;

    private void Awake()
    {
        // Build dictionary from serialized list
        inventory = new Dictionary<string, int>();
        foreach (var pair in inventoryData)
        {
            inventory[pair.key] = pair.value;
        }
    }
}

// ✓ ALTERNATIVE - Use existing solutions
// Unity 2020+: SerializableDictionary from Unity packages
// Or: Odin Inspector (paid asset with great serialization)
```

## Inspector Organization

### Using Headers and Tooltips

```csharp
public class OrganizedComponent : MonoBehaviour
{
    [Header("Movement Settings")]
    [SerializeField] private float moveSpeed = 5f;
    [SerializeField] private float jumpForce = 10f;
    [SerializeField] private float gravity = -9.81f;

    [Header("Combat")]
    [Tooltip("Maximum health points")]
    [SerializeField] private int maxHealth = 100;

    [Tooltip("Damage dealt per hit")]
    [SerializeField] private int attackDamage = 10;

    [Header("References")]
    [SerializeField] private Transform groundCheck;
    [SerializeField] private LayerMask groundLayer;

    [Header("Visual Effects")]
    [SerializeField] private ParticleSystem hitEffect;
    [SerializeField] private AudioClip hitSound;
}
```

### Using Space and Range

```csharp
public class AttributeExamples : MonoBehaviour
{
    [Header("Player Stats")]
    [Range(1, 100)]
    [SerializeField] private int level = 1;

    [Range(0f, 1f)]
    [SerializeField] private float volume = 0.5f;

    [Space(20)]
    [Header("Debug Options")]
    [SerializeField] private bool showDebugInfo;
}
```

### Hiding Fields

```csharp
public class VisibilityExamples : MonoBehaviour
{
    // Visible in Inspector
    [SerializeField] private float moveSpeed = 5f;

    // Hidden from Inspector but still serialized
    [HideInInspector]
    public int cachedValue; // Still saved with the scene

    // Private and not serialized
    private int temporaryValue;

    // Public but hidden
    [HideInInspector]
    public bool internalFlag;
}
```

## Common Attributes

### Essential Attributes

```csharp
public class AttributeReference : MonoBehaviour
{
    // ═══════════════════════════════════════════
    // INSPECTOR VISIBILITY
    // ═══════════════════════════════════════════

    // Make private field visible in Inspector
    [SerializeField]
    private float speed;

    // Hide public field from Inspector
    [HideInInspector]
    public int internalValue;

    // ═══════════════════════════════════════════
    // INSPECTOR ORGANIZATION
    // ═══════════════════════════════════════════

    // Add header above field
    [Header("Movement Settings")]
    [SerializeField] private float moveSpeed;

    // Add space above field
    [Space(10)]
    [SerializeField] private float jumpHeight;

    // Add tooltip (hover for description)
    [Tooltip("Speed in units per second")]
    [SerializeField] private float velocity;

    // ═══════════════════════════════════════════
    // VALUE CONSTRAINTS
    // ═══════════════════════════════════════════

    // Slider in Inspector (min, max)
    [Range(0f, 100f)]
    [SerializeField] private float health;

    // Ensure value is not null
    [RequireComponent(typeof(Rigidbody))]

    // Require minimum value
    [Min(0)]
    [SerializeField] private int minScore;

    // ═══════════════════════════════════════════
    // COMPONENT REQUIREMENTS
    // ═══════════════════════════════════════════

    // Automatically add required component
    [RequireComponent(typeof(Rigidbody))]
    [RequireComponent(typeof(Collider))]
    public class PhysicsObject : MonoBehaviour { }

    // ═══════════════════════════════════════════
    // ADVANCED
    // ═══════════════════════════════════════════

    // Custom label in Inspector
    [SerializeField, Rename("Player Speed")]
    private float m_speed;

    // Multi-line text field
    [TextArea(3, 10)] // min 3 lines, max 10 lines
    [SerializeField] private string description;

    // Color picker
    [ColorUsage(true, true)] // HDR, show alpha
    [SerializeField] private Color effectColor;

    // Scene field
    [Scene]
    [SerializeField] private string mainMenuScene;
}

// Note: [Rename] and [Scene] require custom PropertyDrawers
```

### Nested Classes

```csharp
// Must mark as [Serializable] to show in Inspector
[System.Serializable]
public class WeaponStats
{
    [Header("Damage")]
    [Range(1, 100)]
    public int damage = 10;

    [Range(0.1f, 5f)]
    public float fireRate = 1f;

    [Header("Ammo")]
    public int magazineSize = 30;
    public int maxAmmo = 300;
}

public class WeaponSystem : MonoBehaviour
{
    [SerializeField] private WeaponStats stats;

    // Shows nice foldout in Inspector with all WeaponStats fields
}
```

## Best Practices

### 1. Use Properties for Public Access

```csharp
public class EncapsulatedPlayer : MonoBehaviour
{
    // ✓ Inspector-editable, private to other scripts
    [SerializeField] private int maxHealth = 100;
    [SerializeField] private float moveSpeed = 5f;

    // Runtime state (not in Inspector)
    private int currentHealth;
    private bool isAlive = true;

    // ✓ Public properties for read access
    public int MaxHealth => maxHealth;
    public int CurrentHealth => currentHealth;
    public bool IsAlive => isAlive;

    // ✓ Public methods for controlled modification
    public void TakeDamage(int damage)
    {
        if (!isAlive) return;

        currentHealth = Mathf.Max(0, currentHealth - damage);

        if (currentHealth == 0)
        {
            Die();
        }
    }

    public void Heal(int amount)
    {
        if (!isAlive) return;

        currentHealth = Mathf.Min(maxHealth, currentHealth + amount);
    }

    private void Die()
    {
        isAlive = false;
        // Death logic
    }
}
```

### 2. Organize Inspector Logically

```csharp
public class WellOrganizedComponent : MonoBehaviour
{
    [Header("Core Settings")]
    [Tooltip("Speed of movement in units/second")]
    [SerializeField] private float moveSpeed = 5f;

    [Tooltip("Maximum health points")]
    [SerializeField] private int maxHealth = 100;

    [Space(10)]
    [Header("References")]
    [Tooltip("Transform to follow")]
    [SerializeField] private Transform target;

    [Tooltip("Ground detection point")]
    [SerializeField] private Transform groundCheck;

    [Space(10)]
    [Header("Effects")]
    [SerializeField] private ParticleSystem deathEffect;
    [SerializeField] private AudioClip deathSound;

    [Space(10)]
    [Header("Debug")]
    [SerializeField] private bool showDebugGizmos;
}
```

### 3. Use Meaningful Default Values

```csharp
public class GoodDefaults : MonoBehaviour
{
    // ✓ Sensible defaults save time
    [SerializeField] private float moveSpeed = 5f; // Common speed
    [SerializeField] private int maxHealth = 100; // Round number
    [SerializeField] private Color teamColor = Color.blue; // Visual feedback

    // ✓ Defaults that make sense for the object
    [SerializeField] private LayerMask groundLayer = 1 << LayerMask.NameToLayer("Ground");
}
```

### 4. Validate in OnValidate

```csharp
public class ValidatedComponent : MonoBehaviour
{
    [SerializeField] private int maxHealth = 100;
    [SerializeField] private float moveSpeed = 5f;

    // Called when values change in Inspector
    private void OnValidate()
    {
        // Enforce constraints
        maxHealth = Mathf.Max(1, maxHealth);
        moveSpeed = Mathf.Max(0f, moveSpeed);

        // Auto-find components if missing
        #if UNITY_EDITOR
        if (Application.isPlaying == false)
        {
            if (rigidbody == null)
                rigidbody = GetComponent<Rigidbody>();
        }
        #endif
    }
}
```

### 5. Use Serializable Data Classes

```csharp
// ✓ GOOD - Reusable, organized data
[System.Serializable]
public class EnemyStats
{
    [Header("Health")]
    [Range(10, 1000)]
    public int maxHealth = 100;

    [Header("Movement")]
    [Range(1f, 20f)]
    public float moveSpeed = 5f;

    [Header("Combat")]
    [Range(1, 100)]
    public int damage = 10;

    [Range(0.5f, 5f)]
    public float attackCooldown = 1f;
}

public class Enemy : MonoBehaviour
{
    [SerializeField] private EnemyStats stats;

    // Easy to create multiple enemy types with different stats
}
```

## Common Pitfalls

### Pitfall 1: Public Fields Everywhere

```csharp
// ❌ TERRIBLE - Everything is public!
public class BadEncapsulation : MonoBehaviour
{
    public int health = 100;
    public int maxHealth = 100;
    public float moveSpeed = 5f;
    public bool isAlive = true;
    public Transform target;

    // Anyone can break your logic!
}

// Other script can do this:
badScript.isAlive = true;
badScript.health = 999999;

// ✓ CORRECT - Proper encapsulation
public class GoodEncapsulation : MonoBehaviour
{
    [SerializeField] private int maxHealth = 100;
    private int currentHealth;
    [SerializeField] private float moveSpeed = 5f;
    private bool isAlive = true;

    // Controlled access only
    public int CurrentHealth => currentHealth;
    public bool IsAlive => isAlive;

    public void TakeDamage(int damage)
    {
        // Can add logic, validation, etc.
        currentHealth -= damage;
        if (currentHealth <= 0)
            Die();
    }
}
```

### Pitfall 2: Forgetting [Serializable] on Custom Classes

```csharp
// ❌ WRONG - Won't show in Inspector!
public class ItemData
{
    public string itemName;
    public int value;
}

public class Inventory : MonoBehaviour
{
    [SerializeField] private ItemData data; // Won't work!
}

// ✓ CORRECT - Add [Serializable]
[System.Serializable]
public class ItemData
{
    public string itemName;
    public int value;
}

public class Inventory : MonoBehaviour
{
    [SerializeField] private ItemData data; // Works!
}
```

### Pitfall 3: Trying to Serialize Properties

```csharp
// ❌ WRONG - Properties don't serialize!
public class BadSerialization : MonoBehaviour
{
    [SerializeField]
    private int Health { get; set; } = 100; // Won't work!
}

// ✓ CORRECT - Use field + property
public class GoodSerialization : MonoBehaviour
{
    [SerializeField] private int maxHealth = 100;

    public int MaxHealth => maxHealth; // Property for access
}
```

### Pitfall 4: Not Using Headers/Tooltips

```csharp
// ❌ MESSY - Hard to understand in Inspector
public class MessyInspector : MonoBehaviour
{
    [SerializeField] private float moveSpeed;
    [SerializeField] private float jumpForce;
    [SerializeField] private float gravity;
    [SerializeField] private int maxHealth;
    [SerializeField] private int attackDamage;
    [SerializeField] private Transform target;
    [SerializeField] private AudioClip sound;
}

// ✓ CLEAN - Well organized
public class CleanInspector : MonoBehaviour
{
    [Header("Movement")]
    [Tooltip("Speed in units per second")]
    [SerializeField] private float moveSpeed;

    [Tooltip("Upward force when jumping")]
    [SerializeField] private float jumpForce;

    [Header("Combat")]
    [SerializeField] private int maxHealth;
    [SerializeField] private int attackDamage;

    [Header("References")]
    [SerializeField] private Transform target;
    [SerializeField] private AudioClip sound;
}
```

### Pitfall 5: Exposing References That Should Be Found

```csharp
// ⚠️ PROBLEMATIC - Manual assignment required
public class ManualReferences : MonoBehaviour
{
    [SerializeField] private Rigidbody rb; // On same GameObject
    [SerializeField] private Animator animator; // On same GameObject

    // Developer must assign these every time!
}

// ✓ BETTER - Auto-find in Awake
public class AutoReferences : MonoBehaviour
{
    private Rigidbody rb;
    private Animator animator;

    private void Awake()
    {
        rb = GetComponent<Rigidbody>();
        animator = GetComponent<Animator>();
    }
}

// ✓ BEST - RequireComponent + auto-find
[RequireComponent(typeof(Rigidbody))]
[RequireComponent(typeof(Animator))]
public class SafeAutoReferences : MonoBehaviour
{
    private Rigidbody rb;
    private Animator animator;

    private void Awake()
    {
        rb = GetComponent<Rigidbody>();
        animator = GetComponent<Animator>();
    }
}
```

### Pitfall 6: Not Validating Inspector Values

```csharp
// ⚠️ RISKY - Can be set to invalid values in Inspector
public class NoValidation : MonoBehaviour
{
    [SerializeField] private int maxHealth; // Could be 0 or negative!
    [SerializeField] private float moveSpeed; // Could be negative!
}

// ✓ SAFE - Use Range or OnValidate
public class WithValidation : MonoBehaviour
{
    [Range(1, 1000)]
    [SerializeField] private int maxHealth = 100;

    [Range(0f, 20f)]
    [SerializeField] private float moveSpeed = 5f;

    private void OnValidate()
    {
        // Additional validation
        maxHealth = Mathf.Max(1, maxHealth);
        moveSpeed = Mathf.Max(0f, moveSpeed);
    }
}
```

## Quick Reference

### Always Use

- `[SerializeField] private` instead of `public`
- `[Header]` to organize sections
- `[Tooltip]` to document fields
- `[Range]` for numeric values with limits
- `[RequireComponent]` for dependencies

### Never Do

- Public fields for internal state
- Serialize properties
- Serialize static fields
- Serialize dictionaries directly
- Forget `[Serializable]` on custom classes

### Inspector Organization Pattern

```csharp
[Header("Category 1")]
[Tooltip("Description")]
[SerializeField] private float value1;

[Space(10)]
[Header("Category 2")]
[SerializeField] private int value2;
```

## Summary

**Golden Rules:**

1. **Use `[SerializeField] private`** instead of `public`
2. **Expose through properties** for read-only access
3. **Expose through methods** for controlled modification
4. **Mark custom classes `[Serializable]`** to serialize them
5. **Use `[Header]` and `[Tooltip]`** for organization
6. **Use `[Range]`** for bounded values
7. **Validate in `OnValidate()`** for complex constraints
8. **Don't serialize** what doesn't need to persist

**Encapsulation Example:**

```csharp
public class ProperEncapsulation : MonoBehaviour
{
    // Inspector-editable configuration
    [Header("Settings")]
    [SerializeField] private int maxHealth = 100;
    [SerializeField] private float moveSpeed = 5f;

    // Runtime state (private)
    private int currentHealth;

    // Public read-only access
    public int CurrentHealth => currentHealth;

    // Public controlled modification
    public void TakeDamage(int damage)
    {
        currentHealth = Mathf.Max(0, currentHealth - damage);
    }
}
```

Proper serialization keeps your code maintainable, your Inspector clean, and your logic protected!
