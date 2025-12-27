# Getting Started with Odin Inspector & Serializer

> **Quick Start**: Change `MonoBehaviour` to `SerializedMonoBehaviour`, then serialize a
> `Dictionary<string, int>` — that's it!

## What is Odin?

Odin Inspector & Serializer is a Unity plugin that **solves two critical problems**:

1. **Odin Serializer**: Serialize types that Unity can't handle (dictionaries, properties,
   interfaces, nullable types, etc.)
2. **Odin Inspector**: Add powerful Inspector features (buttons, validation, conditional visibility,
   custom drawers) with simple attributes

```csharp
using Sirenix.OdinInspector;
using System.Collections.Generic;

public class Example : SerializedMonoBehaviour
{
    // ✨ Odin Serializer: Unity can't serialize this!
    [OdinSerialize]
    private Dictionary<string, int> _scores = new();

    // ✨ Odin Inspector: Run code directly from Inspector!
    [Button]
    private void AddScore()
    {
        _scores["Player"] = 100;
    }
}
```

---

## The Two Core Problems Odin Solves

### Problem #1: Unity's Serialization is Limited

Unity's built-in serialization system has strict limitations:

#### What Unity CAN Serialize

✅ Primitive types (int, float, bool, string) ✅ UnityEngine objects (GameObject, Transform,
Material) ✅ Simple classes marked with `[System.Serializable]` ✅ Arrays and Lists of supported
types

#### What Unity CANNOT Serialize

❌ **Dictionaries** (Dictionary<TKey, TValue>) ❌ **Properties** (auto-properties or properties with
custom get/set) ❌ **Interfaces** (IEnumerable, IItem, etc.) ❌ **Nullable types** (int?, float?,
bool?) ❌ **Tuples** ((int, string) or ValueTuple) ❌ **Generic classes** (beyond List<T>) ❌
**Multi-dimensional arrays** (int[,]) ❌ **Circular references** (objects referencing each other)

**Odin Serializer removes ALL these limitations.**

### Problem #2: Unity's Inspector is Inflexible

Unity's Inspector is purely data-driven. You can't: ❌ Add buttons to call methods ❌ Add validation
warnings ❌ Show/hide fields conditionally ❌ Group fields into tabs or foldouts easily ❌ Display
read-only computed properties

**Odin Inspector adds ALL these features with simple attributes.**

---

## Installation

### Prerequisites

- Unity 2020.3 or newer (2021.3+ recommended)
- Odin Inspector & Serializer asset (purchased from Unity Asset Store)

### Steps

1. **Import Odin**

   - Window → Package Manager
   - Click "Packages: In Project"
   - Find "Odin Inspector and Serializer"
   - Click "Import"

2. **Verify Installation**

   - Check for `Assets/Plugins/Sirenix/` directory
   - Open any script and add `using Sirenix.OdinInspector;`
   - If no errors, installation succeeded!

3. **Configure Odin (Optional)**
   - Tools → Odin Inspector → Preferences
   - Configure global settings (we'll cover this later)

---

## Your First Serialized Dictionary

Let's solve Unity's biggest serialization limitation: **dictionaries**.

### Without Odin (Doesn't Work)

```csharp
using UnityEngine;
using System.Collections.Generic;

public class ItemManager : MonoBehaviour
{
    // ❌ This doesn't serialize in Unity!
    [OdinSerialize]
    private Dictionary<string, int> _itemPrices = new();
    // Inspector shows: "Type is not supported"

    void Start()
    {
        // Dictionary is always empty, even if you populate it in editor
        Debug.Log(_itemPrices.Count);  // Always prints 0
    }
}
```

### With Odin (Just Works!)

```csharp
using UnityEngine;
using Sirenix.OdinInspector;
using System.Collections.Generic;

public class ItemManager : SerializedMonoBehaviour  // ← Changed!
{
    // ✅ This works perfectly with Odin!
    [OdinSerialize]
    private Dictionary<string, int> _itemPrices = new();

    void Start()
    {
        Debug.Log(_itemPrices.Count);  // Prints actual count!
    }
}
```

**What changed?**

1. Added `using Sirenix.OdinInspector;`
2. Changed `MonoBehaviour` to `SerializedMonoBehaviour`
3. **That's it!** Dictionary now serializes perfectly.

**In the Inspector, you'll see:**

- ✅ Add/remove entries with buttons
- ✅ Edit keys and values inline
- ✅ Drag & drop support for GameObject values
- ✅ Full undo/redo support
- ✅ Data persists across sessions

---

## Your First Inspector Button

Now let's add functionality that vanilla Unity simply **cannot do**: run code from the Inspector.

### Without Odin (Requires Play Mode)

```csharp
using UnityEngine;

public class LevelGenerator : MonoBehaviour
{
    public void GenerateLevel()
    {
        // Complex level generation logic...
        Debug.Log("Level generated!");
    }

    // ❌ To test this, you MUST:
    // 1. Enter play mode (slow!)
    // 2. Call this from Update() or another event
    // 3. Exit play mode
    // 4. Make changes
    // 5. Repeat entire cycle...
}
```

### With Odin (One-Click Testing!)

```csharp
using UnityEngine;
using Sirenix.OdinInspector;

public class LevelGenerator : SerializedMonoBehaviour
{
    [Button(ButtonSizes.Large)]  // ← Added attribute!
    public void GenerateLevel()
    {
        // Complex level generation logic...
        Debug.Log("Level generated!");

        // You can even modify the scene!
        #if UNITY_EDITOR
        UnityEditor.EditorUtility.SetDirty(this);
        #endif
    }

    [Button("Reset Level"), GUIColor(1, 0.3f, 0.3f)]
    public void ResetLevel()
    {
        // Clear level data...
        Debug.Log("Level reset!");
    }
}
```

**In the Inspector, you'll see:**

- ✅ Clickable "Generate Level" button (large, blue)
- ✅ Clickable "Reset Level" button (red tint)
- ✅ Works in **Edit Mode** and **Play Mode**
- ✅ No need to enter play mode to test!

**This changes development forever.** Test methods instantly, generate assets in edit mode, run
validation checks—all with zero setup.

---

## Core Concept: SerializedMonoBehaviour

The key to Odin's power is **SerializedMonoBehaviour**.

### When to Use SerializedMonoBehaviour

| Your Script Uses...                                  | Use...                           |
| ---------------------------------------------------- | -------------------------------- |
| Only simple fields (int, float, GameObject, etc.)    | `MonoBehaviour` (vanilla Unity)  |
| Dictionaries, properties, interfaces, nullable types | `SerializedMonoBehaviour` (Odin) |
| Any Odin Inspector attribute                         | `SerializedMonoBehaviour` (Odin) |
| Both Odin features and Unity's serialization         | `SerializedMonoBehaviour` (Odin) |

**Rule of thumb:** If you're importing `Sirenix.OdinInspector`, use `SerializedMonoBehaviour`.

### What About ScriptableObjects?

Use `SerializedScriptableObject` for ScriptableObjects:

```csharp
using Sirenix.OdinInspector;
using UnityEngine;
using System.Collections.Generic;

// ✅ For ScriptableObjects
[CreateAssetMenu(fileName = "ItemData", menuName = "Game/Item Data")]
public class ItemData : SerializedScriptableObject
{
    [OdinSerialize]
    private Dictionary<string, int> _baseStats = new();

    [Button]
    private void ValidateStats()
    {
        Debug.Log("Stats validated!");
    }
}
```

---

## Essential Attributes Quick Reference

Here are the **10 most important attributes** to learn first:

### 1. Dictionary Serialization

```csharp
[OdinSerialize]
private Dictionary<string, int> _scores = new();

// Custom labels for better UX
[OdinSerialize]
[DictionaryDrawerSettings(KeyLabel = "Player Name", ValueLabel = "Score")]
private Dictionary<string, int> _scoresPretty = new();
```

### 2. Buttons

```csharp
[Button]
private void SimpleButton() { }

[Button("Custom Label")]
private void CustomLabelButton() { }

[Button(ButtonSizes.Large), GUIColor(0, 1, 0)]
private void StyledButton() { }
```

### 3. Validation

```csharp
[Required]  // Shows error if null
[SerializeField] private GameObject _prefab;

[AssetsOnly]  // Only accept prefabs, not scene objects
[SerializeField] private GameObject _prefabOnly;

[SceneObjectsOnly]  // Only accept scene objects, not prefabs
[SerializeField] private Transform _sceneObject;
```

### 4. Value Constraints

```csharp
[MinValue(0), MaxValue(100)]
[SerializeField] private float _percentage;

[MinValue(1)]
[SerializeField] private int _count;
```

### 5. Conditional Visibility

```csharp
[SerializeField] private bool _useAdvancedMode;

[ShowIf(nameof(_useAdvancedMode))]
[SerializeField] private float _advancedSetting;

[HideIf(nameof(_useAdvancedMode))]
[SerializeField] private float _basicSetting;
```

### 6. Info Boxes

```csharp
[InfoBox("This is a helpful message!")]
[SerializeField] private int _value;

[InfoBox("Warning: This is experimental!", InfoMessageType.Warning)]
[SerializeField] private bool _experimentalFeature;

[InfoBox("Error: This will break things!", InfoMessageType.Error)]
[SerializeField] private bool _dangerousOption;
```

### 7. Groups and Organization

```csharp
[FoldoutGroup("Player Stats")]
[SerializeField] private int _health;

[FoldoutGroup("Player Stats")]
[SerializeField] private int _mana;

[BoxGroup("Enemy Settings")]
[SerializeField] private float _spawnRate;
```

### 8. Show Properties

```csharp
// Show computed properties in Inspector (read-only)
[ShowInInspector]
public int TotalScore => _scores.Values.Sum();

[ShowInInspector]
public string Status => _isAlive ? "Alive" : "Dead";
```

### 9. Inline Editors

```csharp
[InlineEditor]  // Shows referenced object's Inspector inline
[SerializeField] private ItemData _itemData;
```

### 10. Table Lists

```csharp
[TableList]  // Display list as a table
[SerializeField] private List<EnemyData> _enemies;

[System.Serializable]
public class EnemyData
{
    public string Name;
    public int Health;
    public float Speed;
}
```

---

## Complete Beginner Example

Here's a complete, practical example combining multiple features:

```csharp
using UnityEngine;
using Sirenix.OdinInspector;
using System.Collections.Generic;

/// <summary>
/// Manages player inventory with item counts and prices.
/// </summary>
public class PlayerInventory : SerializedMonoBehaviour
{
    [Title("Inventory Data")]
    [InfoBox("Add items and set their quantities. Dictionary keys are item names.")]
    [DictionaryDrawerSettings(KeyLabel = "Item Name", ValueLabel = "Quantity")]
    [OdinSerialize]
    private Dictionary<string, int> _itemQuantities = new();

    [Space(10)]
    [DictionaryDrawerSettings(KeyLabel = "Item Name", ValueLabel = "Price")]
    [OdinSerialize]
    private Dictionary<string, int> _itemPrices = new();

    [Title("Computed Values", "These update automatically")]
    [ShowInInspector, ReadOnly]
    public int TotalItems => _itemQuantities.Values.Sum();

    [ShowInInspector, ReadOnly]
    public int TotalValue
    {
        get
        {
            int total = 0;
            foreach (var kvp in _itemQuantities)
            {
                if (_itemPrices.TryGetValue(kvp.Key, out int price))
                {
                    total += price * kvp.Value;
                }
            }
            return total;
        }
    }

    [Title("Actions", "Dev tools for testing")]
    [Button(ButtonSizes.Large), GUIColor(0.4f, 0.8f, 1f)]
    private void AddSampleItems()
    {
        _itemQuantities["Health Potion"] = 5;
        _itemQuantities["Mana Potion"] = 3;
        _itemQuantities["Iron Sword"] = 1;

        _itemPrices["Health Potion"] = 50;
        _itemPrices["Mana Potion"] = 75;
        _itemPrices["Iron Sword"] = 200;

        Debug.Log("Sample items added!");
    }

    [Button("Clear All Items"), GUIColor(1, 0.3f, 0.3f)]
    private void ClearInventory()
    {
        _itemQuantities.Clear();
        _itemPrices.Clear();
        Debug.Log("Inventory cleared!");
    }

    [Button("Validate Inventory")]
    private void ValidateInventory()
    {
        foreach (var item in _itemQuantities.Keys)
        {
            if (!_itemPrices.ContainsKey(item))
            {
                Debug.LogWarning($"Missing price for item: {item}");
            }
        }
        Debug.Log("Validation complete!");
    }
}
```

**In the Inspector, you'll see:**

- 📦 Editable dictionary of item quantities
- 💰 Editable dictionary of item prices
- 📊 Read-only display of total items and total value
- 🎛️ Three buttons: Add Sample Items, Clear All Items, Validate Inventory
- 🎨 Color-coded buttons (blue = safe, red = destructive)
- 📝 Info boxes explaining each section

**This single script demonstrates:** ✅ Dictionary serialization (two dictionaries!) ✅ Inspector
buttons (three buttons!) ✅ Read-only computed properties (two properties!) ✅ Validation logic ✅
Custom labels and organization ✅ Color-coded UX

---

## Migration from Vanilla Unity

### Simple Migration (No Dictionaries)

If you just want Inspector buttons and validation:

**Before:**

```csharp
using UnityEngine;

public class Enemy : MonoBehaviour
{
    [SerializeField] private int _health = 100;
}
```

**After:**

```csharp
using UnityEngine;
using Sirenix.OdinInspector;  // ← Add this

public class Enemy : SerializedMonoBehaviour  // ← Change this
{
    [Required]  // ← Add validation
    [SerializeField] private int _health = 100;

    [Button]  // ← Add button
    private void ResetHealth()
    {
        _health = 100;
    }
}
```

### Advanced Migration (With Dictionaries)

If you're currently using parallel lists to fake dictionaries:

**Before (Painful):**

```csharp
using UnityEngine;
using System.Collections.Generic;
using System.Linq;

public class ItemManager : MonoBehaviour
{
    [System.Serializable]
    public class ItemPricePair
    {
        public string itemId;
        public int price;
    }

    [SerializeField]
    private List<ItemPricePair> _priceList = new();

    private Dictionary<string, int> _priceDict;

    void Awake()
    {
        // Convert list to dictionary at runtime
        _priceDict = _priceList.ToDictionary(x => x.itemId, x => x.price);
    }

    public int GetPrice(string itemId)
    {
        if (_priceDict.TryGetValue(itemId, out int price))
            return price;
        return 0;
    }
}
```

**After (Clean):**

```csharp
using UnityEngine;
using Sirenix.OdinInspector;
using System.Collections.Generic;

public class ItemManager : SerializedMonoBehaviour
{
    [OdinSerialize]
    private Dictionary<string, int> _prices = new();

    public int GetPrice(string itemId)
    {
        if (_prices.TryGetValue(itemId, out int price))
            return price;
        return 0;
    }
}
```

**Result:**

- ❌ Removed 15+ lines of boilerplate
- ❌ Removed custom serializable class
- ❌ Removed runtime conversion logic
- ✅ Direct dictionary serialization
- ✅ Cleaner, more maintainable code

---

## Common Questions

### Q: Do I need to replace ALL MonoBehaviours with SerializedMonoBehaviour?

**A: No!** Only use `SerializedMonoBehaviour` when you need:

- Dictionaries or other complex types
- Odin Inspector attributes

For simple scripts with basic fields, stick with vanilla `MonoBehaviour`.

### Q: Does Odin work with prefabs?

**A: Yes!** Odin fully supports:

- ✅ Prefab variants
- ✅ Prefab overrides
- ✅ Nested prefabs
- ✅ Prefab serialization

### Q: What about performance?

**A:** Odin Serializer is slightly slower than Unity's serializer (~10-20%), but:

- Serialization only happens in the editor (not runtime)
- The productivity gains far outweigh the negligible performance cost
- Runtime performance is identical to vanilla Unity

### Q: Can I use Odin with source control (Git, Perforce)?

**A: Yes!** Odin generates clean text-based scene and prefab files that work perfectly with version
control.

### Q: Do I need Odin on build machines?

**A:** Odin is **required** in the project for builds. The compiled game includes Odin's runtime
serializer (adds ~2-5MB to build size).

### Q: What if my team doesn't have Odin licenses?

**A:** Odin requires a license **per seat**. Every developer needs their own license. However:

- One license works across unlimited projects
- Builds don't require additional licenses
- Very cost-effective for the productivity gains

---

## Next Steps

Now that you understand the basics:

1. **[Core Features](02-core-features.md)** — Deep dive into Odin Serializer and Inspector
   attributes
2. **[Common Patterns](04-common-patterns.md)** — Real-world recipes for dictionaries, buttons,
   validation
3. **[Best Practices](05-best-practices.md)** — Avoid pitfalls and optimize performance
4. **[Advanced Techniques](03-advanced-techniques.md)** — Custom processors and advanced workflows

---

## Quick Reference Card

```csharp
using Sirenix.OdinInspector;
using System.Collections.Generic;

// Use SerializedMonoBehaviour (not MonoBehaviour)
public class Example : SerializedMonoBehaviour
{
    // Serialize dictionaries
    [OdinSerialize]
    private Dictionary<string, int> _dict = new();

    // Inspector buttons
    [Button]
    private void DoSomething() { }

    // Validation
    [Required]
    [SerializeField] private GameObject _prefab;

    // Conditional visibility
    [ShowIf(nameof(_showAdvanced))]
    [SerializeField] private float _advancedSetting;

    // Show properties (read-only)
    [ShowInInspector]
    public int Total => _dict.Values.Sum();

    // Value constraints
    [MinValue(0), MaxValue(100)]
    [SerializeField] private float _percentage;

    // Info boxes
    [InfoBox("This is helpful info!")]
    [SerializeField] private int _value;

    // Groups
    [FoldoutGroup("Settings")]
    [SerializeField] private bool _setting1;
}
```

---

**Pro Tip**: Create a new test script with `SerializedMonoBehaviour`, add a dictionary and a button,
and see the magic for yourself. Once you experience Odin's workflow, you'll never want to go back!
