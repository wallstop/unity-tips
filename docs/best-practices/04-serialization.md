# Unity Serialization Best Practices

## The Problem

Unity's serialization determines what appears in the Inspector and what gets saved. Common issues:

- Fields marked `[SerializeField]` don't appear in Inspector
- Values reset after saving
- Public fields break encapsulation

**Why:** Unity only serializes specific types and structures for performance. Understanding these
rules prevents debugging "why isn't this saving?" and helps you write maintainable, encapsulated
code.

**Key mistakes:**

1. Using `public` fields instead of `[SerializeField] private`
2. Forgetting `[Serializable]` on custom classes
3. Trying to serialize dictionaries directly
4. Not organizing the Inspector with headers/tooltips

## Table of Contents

- [SerializeField vs Public](#serializefield-vs-public)
- [What Unity Can Serialize](#what-unity-can-serialize)
- [Inspector Organization](#inspector-organization)
- [Best Practices](#best-practices)
- [Common Pitfalls](#common-pitfalls)

## SerializeField vs Public

**Always prefer `[SerializeField] private` over `public`** - it keeps encapsulation while still
showing in the Inspector.

```csharp
// ❌ Public fields - other scripts can bypass your logic
public class BadPlayer : MonoBehaviour
{
    public int currentHealth = 100;

    public void TakeDamage(int damage) { currentHealth -= damage; }
}
// Problem: otherScript can do badPlayer.currentHealth = 0 and bypass TakeDamage()

// ✓ SerializeField - Inspector-editable but encapsulated
public class GoodPlayer : MonoBehaviour
{
    [SerializeField] private int maxHealth = 100;  // Config (in Inspector)
    private int currentHealth;                      // State (not in Inspector)

    public int CurrentHealth => currentHealth;      // Read - only access

    public void TakeDamage(int damage)              // Controlled modification
    {
        currentHealth = Mathf.Max(0, currentHealth - damage);
        if (currentHealth == 0) Die();
    }
}

// Exception: Public fields OK for simple data containers with no behavior
[System.Serializable]
public class ItemData
{
    public string itemName;
    public Sprite icon;
    public int value;
}
```

## What Unity Can Serialize

**Unity CAN serialize:**

- Basic types: `int`, `float`, `bool`, `string`
- Unity types: `Vector3`, `Color`, `LayerMask`
- Unity object references: `GameObject`, `Transform`, `Material`, `AudioClip`
- Enums
- Arrays and `List<T>` of serializable types
- Custom classes marked `[Serializable]`
- Auto-properties with `[field: SerializeField]`
- Concrete generic types (Unity 2020.1+)

**Unity CANNOT serialize:**

- Dictionaries (use wrapper - see below)
- HashSets/Queues/complex collections
- Properties without `[field:]` attribute
- Static fields, const fields
- Delegates/Events
- Classes without `[Serializable]`
- Polymorphic fields without `[SerializeReference]` (Unity 2019.3+)

### Common Patterns

**Auto-properties:**

```csharp
// ❌ Won't serialize
[SerializeField] private int Health { get; set; }

// ✓ Will serialize (Unity 2017+)
[field: SerializeField] private int Health { get; set; } = 100;

// ✓ With other attributes
[field: SerializeField]
[field: Range(0, 10)]
private float Speed { get; set; } = 5f;
```

**Polymorphic types (Unity 2019.3+):**

```csharp
[System.Serializable]
public abstract class PowerUp { public string name; }

[System.Serializable]
public class HealthPowerUp : PowerUp { public int healAmount; }

public class PowerUpManager : MonoBehaviour
{
    // ❌ Won't serialize derived class fields
    [SerializeField] private PowerUp powerUp;

    // ✓ Will serialize derived class fields (Unity 2019.3+)
    [SerializeReference] private PowerUp polymorphicPowerUp;
    [SerializeReference] private List<PowerUp> allPowerUps;
}
```

**Dictionary workaround:**

```csharp
[System.Serializable]
public class StringIntPair
{
    public string key;
    public int value;
}

public class InventorySystem : MonoBehaviour
{
    [SerializeField] private List<StringIntPair> inventoryData;
    private Dictionary<string, int> inventory;

    private void Awake()
    {
        inventory = new Dictionary<string, int>();
        foreach (var pair in inventoryData)
            inventory[pair.key] = pair.value;
    }
}
```

## Inspector Organization

Use these attributes to make the Inspector clean and understandable:

```csharp
public class OrganizedComponent : MonoBehaviour
{
    [Header("Movement")]
    [Tooltip("Speed in units per second")]
    [Range(0f, 20f)]
    [SerializeField] private float moveSpeed = 5f;

    [Space(10)]
    [Header("Combat")]
    [Tooltip("Maximum health points")]
    [SerializeField] private int maxHealth = 100;

    [Header("References")]
    [SerializeField] private Transform target;

    // Hidden from Inspector but still serialized
    [HideInInspector]
    public int cachedValue;
}
```

**Common attributes:**

- `[Header("Text")]` - Section label
- `[Tooltip("Text")]` - Hover description
- `[Space(pixels)]` - Vertical spacing
- `[Range(min, max)]` - Slider constraint
- `[Min(value)]` - Minimum value
- `[TextArea(minLines, maxLines)]` - Multi-line text
- `[HideInInspector]` - Hide but still serialize
- `[RequireComponent(typeof(T))]` - Force component dependency

**Nested classes:**

```csharp
[System.Serializable]
public class WeaponStats
{
    [Range(1, 100)] public int damage = 10;
    [Range(0.1f, 5f)] public float fireRate = 1f;
}

public class Weapon : MonoBehaviour
{
    [SerializeField] private WeaponStats stats;  // Shows as foldout
}
```

## Best Practices

### 1. Validate Inspector Values

Use `OnValidate()` to enforce constraints and auto-find components:

```csharp
public class ValidatedComponent : MonoBehaviour
{
    [SerializeField] private int maxHealth = 100;
    [SerializeField] private float moveSpeed = 5f;

    private void OnValidate()
    {
        // Enforce constraints
        maxHealth = Mathf.Max(1, maxHealth);
        moveSpeed = Mathf.Max(0f, moveSpeed);

        // Auto-find components if missing (editor only)
        #if UNITY_EDITOR
        if (!Application.isPlaying && rigidbody == null)
            rigidbody = GetComponent<Rigidbody>();
        #endif
    }
}
```

### 2. Use Serializable Data Classes

Group related fields into reusable data classes:

```csharp
[System.Serializable]
public class EnemyStats
{
    [Range(10, 1000)] public int maxHealth = 100;
    [Range(1f, 20f)] public float moveSpeed = 5f;
    [Range(1, 100)] public int damage = 10;
}

public class Enemy : MonoBehaviour
{
    [SerializeField] private EnemyStats stats;
}
```

### 3. Set Meaningful Defaults

```csharp
// ✓ Good defaults save setup time
[SerializeField] private float moveSpeed = 5f;
[SerializeField] private int maxHealth = 100;
[SerializeField] private Color teamColor = Color.blue;
```

## Common Pitfalls

### Pitfall 1: Forgetting [Serializable]

```csharp
// ❌ Won't show in Inspector
public class ItemData
{
    public string itemName;
    public int value;
}

// ✓ Add [Serializable]
[System.Serializable]
public class ItemData
{
    public string itemName;
    public int value;
}
```

### Pitfall 2: Forgetting [field:] for Auto-Properties

```csharp
// ❌ Won't serialize
[SerializeField] private int Health { get; set; } = 100;

// ✓ Use [field: SerializeField]
[field: SerializeField] private int Health { get; set; } = 100;
```

### Pitfall 3: Exposing Same-GameObject References

```csharp
// ❌ Requires manual assignment every time
[SerializeField] private Rigidbody rb;

// ✓ Auto-find in Awake
[RequireComponent(typeof(Rigidbody))]
public class AutoReferences : MonoBehaviour
{
    private Rigidbody rb;

    private void Awake()
    {
        rb = GetComponent<Rigidbody>();
    }
}
```

## Quick Reference

**Always use:**

- `[SerializeField] private` instead of `public`
- `[Serializable]` on custom classes
- `[Header]` and `[Tooltip]` for organization
- `[Range]` for bounded numeric values
- `[RequireComponent]` for dependencies
- `[field: SerializeField]` for auto-properties

**Never:**

- Public fields for internal state
- Serialize properties without `[field:]`
- Serialize static fields or dictionaries directly
- Forget `[Serializable]` on custom classes
- Forget `[SerializeReference]` for polymorphic types (Unity 2019.3+)

## Summary

**Core principles:**

1. Use `[SerializeField] private` instead of `public` for encapsulation
2. Expose read-only access via properties, modifications via methods
3. Mark custom classes `[Serializable]`
4. Use `[field: SerializeField]` for auto-properties
5. Use `[SerializeReference]` for polymorphic types (Unity 2019.3+)
6. Organize Inspector with `[Header]`, `[Tooltip]`, `[Range]`
7. Validate values in `OnValidate()`
8. Auto-find same-GameObject components in `Awake()`

**Pattern:**

```csharp
public class ProperComponent : MonoBehaviour
{
    // Inspector config
    [Header("Settings")]
    [Tooltip("Movement speed in units/sec")]
    [Range(0f, 20f)]
    [SerializeField] private float moveSpeed = 5f;

    // Runtime state
    private int currentHealth;

    // Controlled access
    public int CurrentHealth => currentHealth;

    public void TakeDamage(int damage)
    {
        currentHealth = Mathf.Max(0, currentHealth - damage);
    }
}
```
