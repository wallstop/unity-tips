# Core Features: Odin Serializer & Inspector

> **TL;DR**: Odin Serializer lets you serialize anything (dictionaries, properties, interfaces).
> Odin Inspector gives you buttons, validation, conditional visibility, and beautiful UX—all with
> simple attributes.

This guide covers the two core systems: **Odin Serializer** (what you can serialize) and **Odin
Inspector** (how you enhance the Inspector).

---

## Table of Contents

1. [Odin Serializer](#odin-serializer)
2. [Odin Inspector](#odin-inspector)
3. [Common Attributes](#common-attributes)
4. [Attribute Combinations](#attribute-combinations)
5. [Performance Considerations](#performance-considerations)

---

## Odin Serializer

Odin Serializer removes Unity's serialization limitations. It's a complete replacement serialization
backend that supports **any C# type**.

### What Odin Can Serialize

| Type                         | Vanilla Unity | Odin | Example                                |
| ---------------------------- | ------------- | ---- | -------------------------------------- |
| **Dictionaries**             | ❌            | ✅   | `Dictionary<string, GameObject>`       |
| **Properties**               | ❌            | ✅   | `public int Health { get; set; }`      |
| **Interfaces**               | ❌            | ✅   | `IItem`, `IEnumerable<T>`              |
| **Nullable Types**           | ❌            | ✅   | `int?`, `float?`, `bool?`              |
| **Tuples**                   | ❌            | ✅   | `(int, string)`, `ValueTuple<T1, T2>`  |
| **Multi-dimensional Arrays** | ⚠️            | ✅   | `int[,]`, `float[,,]`                  |
| **Jagged Arrays**            | ⚠️            | ✅   | `int[][]`                              |
| **Generic Types**            | ⚠️            | ✅   | `List<Dictionary<int, T>>`             |
| **Circular References**      | ❌            | ✅   | Object A → Object B → Object A         |
| **Polymorphism**             | ⚠️            | ✅   | Serialize derived types via base class |

### 1. Dictionary Serialization

The #1 reason people use Odin.

#### Basic Dictionary

```csharp
using Sirenix.OdinInspector;
using System.Collections.Generic;

public class Example : SerializedMonoBehaviour
{
    // Just works!
    [SerializeField]
    private Dictionary<string, int> _stringToInt = new();

    [SerializeField]
    private Dictionary<int, GameObject> _idToPrefab = new();

    [SerializeField]
    private Dictionary<string, List<int>> _stringToList = new();
}
```

#### Custom Dictionary Labels

```csharp
[DictionaryDrawerSettings(
    KeyLabel = "Item ID",
    ValueLabel = "Item Prefab",
    DisplayMode = DictionaryDisplayOptions.ExpandedFoldout
)]
[SerializeField]
private Dictionary<string, GameObject> _items = new();
```

**DisplayMode options:**

- `OneLine` — Compact, one line per entry
- `Foldout` — Collapsible foldout (default)
- `ExpandedFoldout` — Starts expanded

#### Nested Dictionaries

```csharp
// Dictionary of dictionaries
[SerializeField]
private Dictionary<string, Dictionary<string, int>> _nestedDict = new();

// Dictionary with complex values
[System.Serializable]
public class ItemData
{
    public string name;
    public int cost;
    public Sprite icon;
}

[SerializeField]
private Dictionary<string, ItemData> _itemDatabase = new();
```

### 2. Property Serialization

Odin can serialize properties, not just fields!

#### Auto-Properties

```csharp
[ShowInInspector]  // Required for properties
public int Health { get; set; } = 100;

[ShowInInspector]
public string PlayerName { get; private set; } = "Player";

[ShowInInspector]
public List<int> Scores { get; set; } = new();
```

#### Computed Properties (Read-Only)

```csharp
[ShowInInspector]
public int TotalHealth => _health + _armor;

[ShowInInspector]
public bool IsAlive => _health > 0;

[ShowInInspector]
public string Status => IsAlive ? "Alive" : "Dead";
```

**Note:** `[ShowInInspector]` makes properties visible but they re-evaluate often. Don't put
expensive logic here!

### 3. Interface Serialization

Serialize interface references with full polymorphism support.

```csharp
public interface IItem
{
    string Name { get; }
    int Value { get; }
}

[System.Serializable]
public class Weapon : IItem
{
    public string Name => "Sword";
    public int Value => 100;
    public int Damage = 50;
}

[System.Serializable]
public class Potion : IItem
{
    public string Name => "Health Potion";
    public int Value => 25;
    public int HealAmount = 50;
}

public class Inventory : SerializedMonoBehaviour
{
    // Serialize list of interfaces!
    [SerializeField]
    private List<IItem> _items = new();

    // In Inspector, you can select which implementation to create
}
```

**In the Inspector:**

- Click "+" button
- Choose from dropdown: Weapon, Potion, or any class implementing IItem
- Edit derived class fields inline

### 4. Nullable Type Serialization

```csharp
[SerializeField]
private int? _optionalCount = null;

[SerializeField]
private float? _optionalMultiplier = null;

[SerializeField]
private bool? _useFeature = null;

void Start()
{
    if (_optionalCount.HasValue)
    {
        Debug.Log($"Count: {_optionalCount.Value}");
    }
}
```

### 5. Tuple Serialization

```csharp
[SerializeField]
private (int x, int y) _position = (0, 0);

[SerializeField]
private (string name, int level, float health) _playerData;

[SerializeField]
private List<(string id, GameObject prefab)> _prefabs = new();
```

### 6. Polymorphic Serialization

Serialize derived types through base class references.

```csharp
[System.Serializable]
public abstract class Enemy
{
    public int Health = 100;
}

[System.Serializable]
public class Goblin : Enemy
{
    public int Strength = 10;
}

[System.Serializable]
public class Dragon : Enemy
{
    public float FireDamage = 50f;
}

public class EnemyManager : SerializedMonoBehaviour
{
    // Can store any derived type!
    [SerializeField]
    private List<Enemy> _enemies = new();

    // Inspector lets you choose: Goblin or Dragon
}
```

---

## Odin Inspector

Odin Inspector enhances the Unity Inspector with powerful attributes. No custom editors required!

### Categories of Inspector Attributes

| Category        | Purpose                              | Key Attributes                                                    |
| --------------- | ------------------------------------ | ----------------------------------------------------------------- |
| **Actions**     | Add buttons and interactive elements | `[Button]`, `[OnValueChanged]`                                    |
| **Validation**  | Ensure data integrity                | `[Required]`, `[ValidateInput]`, `[AssetsOnly]`                   |
| **Conditional** | Show/hide fields dynamically         | `[ShowIf]`, `[HideIf]`, `[EnableIf]`, `[DisableIf]`               |
| **Grouping**    | Organize complex components          | `[FoldoutGroup]`, `[TabGroup]`, `[BoxGroup]`, `[HorizontalGroup]` |
| **Styling**     | Improve readability                  | `[Title]`, `[InfoBox]`, `[GUIColor]`, `[LabelText]`               |
| **References**  | Control object references            | `[AssetsOnly]`, `[SceneObjectsOnly]`, `[InlineEditor]`            |
| **Collections** | Better list/array editing            | `[TableList]`, `[ListDrawerSettings]`                             |
| **Value Input** | Custom value editors                 | `[ValueDropdown]`, `[FilePath]`, `[FolderPath]`                   |

---

## Common Attributes

### Buttons

Add clickable buttons to call methods from the Inspector.

#### Basic Button

```csharp
[Button]
private void SimpleMethod()
{
    Debug.Log("Button clicked!");
}
```

#### Styled Buttons

```csharp
// Custom label
[Button("Click Me!")]
private void CustomLabel() { }

// Size variants
[Button(ButtonSizes.Small)]
private void SmallButton() { }

[Button(ButtonSizes.Medium)]
private void MediumButton() { }

[Button(ButtonSizes.Large)]
private void LargeButton() { }

[Button(ButtonSizes.Gigantic)]
private void GiganticButton() { }

// Color tint
[Button, GUIColor(0, 1, 0)]  // Green
private void GreenButton() { }

[Button, GUIColor(1, 0.3f, 0.3f)]  // Red
private void DangerButton() { }
```

#### Button Groups

```csharp
[ButtonGroup]
private void Action1() { }

[ButtonGroup]
private void Action2() { }

[ButtonGroup]
private void Action3() { }

// Buttons appear side-by-side in a row
```

#### Conditional Buttons

```csharp
[Button]
[DisableInEditorMode]  // Only enabled in play mode
private void SpawnEnemy() { }

[Button]
[EnableIf(nameof(CanReset))]
private void ResetGame() { }

private bool CanReset => _gameStarted && !_gameOver;
```

#### Buttons with Parameters

```csharp
[Button]
private void DealDamage(int amount)
{
    _health -= amount;
    Debug.Log($"Dealt {amount} damage. Health: {_health}");
}

// In Inspector, a text field appears for the parameter!
```

### Validation Attributes

Ensure data integrity with automatic checks.

#### Required Fields

```csharp
[Required]  // Error if null
[SerializeField] private GameObject _playerPrefab;

[Required("You must assign a spawn point!")]
[SerializeField] private Transform _spawnPoint;
```

#### Asset/Scene Object Restrictions

```csharp
[AssetsOnly]  // Only accept prefabs, not scene objects
[SerializeField] private GameObject _prefab;

[SceneObjectsOnly]  // Only accept scene objects, not prefabs
[SerializeField] private Transform _sceneTransform;
```

#### Value Validation

```csharp
[MinValue(0)]
[SerializeField] private int _count;

[MaxValue(100)]
[SerializeField] private int _percentage;

[MinValue(0), MaxValue(100)]
[SerializeField] private float _normalizedValue;

[ValidateInput(nameof(ValidateHealth), "Health must be positive!")]
[SerializeField] private float _health;

private bool ValidateHealth(float value)
{
    return value > 0;
}
```

#### Child/Sibling Component Validation

```csharp
[ChildGameObjectsOnly]  // Only child objects
[SerializeField] private Transform _childTransform;

[RequireComponent(typeof(Rigidbody))]  // Component must exist
public class RequiresRigidbody : SerializedMonoBehaviour { }
```

### Conditional Visibility

Show or hide fields based on conditions.

#### Show/Hide Based on Boolean

```csharp
[SerializeField] private bool _useAdvancedMode;

[ShowIf(nameof(_useAdvancedMode))]
[SerializeField] private float _advancedSetting;

[HideIf(nameof(_useAdvancedMode))]
[SerializeField] private float _basicSetting;
```

#### Show/Hide Based on Enum

```csharp
public enum WeaponType { Melee, Ranged, Magic }

[SerializeField] private WeaponType _weaponType;

[ShowIf(nameof(_weaponType), WeaponType.Melee)]
[SerializeField] private float _meleeDamage;

[ShowIf(nameof(_weaponType), WeaponType.Ranged)]
[SerializeField] private int _ammoCount;

[ShowIf(nameof(_weaponType), WeaponType.Magic)]
[SerializeField] private float _manaCost;
```

#### Enable/Disable (Grayed Out)

```csharp
[EnableIf(nameof(_canEdit))]
[SerializeField] private string _editableField;

[DisableIf(nameof(_isLocked))]
[SerializeField] private int _value;

[DisableInEditorMode]  // Only enabled in play mode
[SerializeField] private float _runtimeOnlyValue;

[DisableInPlayMode]  // Only enabled in edit mode
[SerializeField] private GameObject _editorOnlyField;
```

#### Complex Conditions

```csharp
[ShowIf(nameof(ShowAdvanced))]
[SerializeField] private float _advancedSetting;

private bool ShowAdvanced()
{
    return _level > 10 && _hasUnlockedAdvanced && !_isLocked;
}
```

### Grouping Attributes

Organize complex Inspectors.

#### Foldout Groups

```csharp
[FoldoutGroup("Player Stats")]
[SerializeField] private int _health;

[FoldoutGroup("Player Stats")]
[SerializeField] private int _mana;

[FoldoutGroup("Player Stats")]
[SerializeField] private float _speed;

[FoldoutGroup("Audio Settings")]
[SerializeField] private AudioClip _jumpSound;
```

#### Tab Groups

```csharp
[TabGroup("Stats")]
[SerializeField] private int _health;

[TabGroup("Stats")]
[SerializeField] private int _mana;

[TabGroup("Visuals")]
[SerializeField] private Material _material;

[TabGroup("Visuals")]
[SerializeField] private Mesh _mesh;

[TabGroup("Audio")]
[SerializeField] private AudioClip _attackSound;
```

#### Box Groups

```csharp
[BoxGroup("Core Settings")]
[SerializeField] private float _moveSpeed;

[BoxGroup("Core Settings")]
[SerializeField] private float _jumpHeight;
```

#### Horizontal Groups

```csharp
[HorizontalGroup("Position")]
[SerializeField] private float _x;

[HorizontalGroup("Position")]
[SerializeField] private float _y;

[HorizontalGroup("Position")]
[SerializeField] private float _z;

// All three fields appear in a single row
```

#### Nested Groups

```csharp
[TabGroup("Gameplay")]
[FoldoutGroup("Gameplay/Movement")]
[SerializeField] private float _speed;

[TabGroup("Gameplay")]
[FoldoutGroup("Gameplay/Combat")]
[SerializeField] private int _damage;

[TabGroup("Debug")]
[BoxGroup("Debug/Tools")]
[Button]
private void DebugReset() { }
```

### Styling Attributes

Improve Inspector UX.

#### Titles and Headers

```csharp
[Title("Player Configuration")]
[SerializeField] private int _health;

[Title("Advanced Settings", "Be careful with these!", TitleAlignment.Centered)]
[SerializeField] private float _dangerValue;
```

#### Info Boxes

```csharp
[InfoBox("This is a helpful message!")]
[SerializeField] private int _value;

[InfoBox("Warning: This setting affects performance!", InfoMessageType.Warning)]
[SerializeField] private int _qualityLevel;

[InfoBox("Error: This will break things!", InfoMessageType.Error)]
[SerializeField] private bool _dangerMode;

[InfoBox("Success: Configuration validated!", InfoMessageType.Info)]
[SerializeField] private bool _validated;
```

#### Conditional Info Boxes

```csharp
[InfoBox("Health is too low!", InfoMessageType.Warning, nameof(_health), 20)]
[SerializeField] private int _health = 100;

// Shows warning only when _health < 20
```

#### GUI Colors

```csharp
[GUIColor(0, 1, 0)]  // Green
[SerializeField] private bool _isHealthy;

[GUIColor(1, 0.3f, 0.3f)]  // Red
[SerializeField] private bool _isDangerous;

[GUIColor(nameof(GetHealthColor))]
[SerializeField] private float _health;

private Color GetHealthColor()
{
    if (_health > 70) return Color.green;
    if (_health > 30) return Color.yellow;
    return Color.red;
}
```

#### Custom Labels

```csharp
[LabelText("Movement Speed (m/s)")]
[SerializeField] private float _moveSpeed;

[LabelText("HP")]
[SerializeField] private int _health;

[LabelText("$" + nameof(GetLabelText))]
[SerializeField] private int _dynamicValue;

private string GetLabelText()
{
    return $"Value (Max: {_maxValue})";
}
```

### Collection Attributes

Better list and array editing.

#### Table Lists

Display lists as tables for better readability.

```csharp
[System.Serializable]
public class EnemyData
{
    public string Name;
    public int Health;
    public float Speed;
    public GameObject Prefab;
}

[TableList(ShowIndexLabels = true)]
[SerializeField]
private List<EnemyData> _enemies = new();
```

**Result:** List displays as a table with columns for Name, Health, Speed, Prefab.

#### List Drawer Settings

```csharp
[ListDrawerSettings(
    ShowIndexLabels = true,
    ListElementLabelName = "Name",
    DraggableItems = true,
    ShowItemCount = true,
    NumberOfItemsPerPage = 10
)]
[SerializeField]
private List<ItemData> _items = new();
```

#### Inline Editors

Display referenced object's Inspector inline.

```csharp
[InlineEditor(InlineEditorModes.FullEditor)]
[SerializeField]
private ItemData _itemData;

[InlineEditor(InlineEditorModes.SmallPreview)]
[SerializeField]
private Texture2D _icon;

// Edit ItemData directly in this Inspector!
```

### Value Dropdown

Provide selectable value options.

```csharp
[ValueDropdown(nameof(GetItemIDs))]
[SerializeField]
private string _selectedItemID;

private IEnumerable<string> GetItemIDs()
{
    return new[] { "sword", "shield", "potion", "key" };
}

// Or with labels
[ValueDropdown(nameof(GetItemOptions))]
[SerializeField]
private string _selectedItem;

private IEnumerable<ValueDropdownItem<string>> GetItemOptions()
{
    return new ValueDropdownList<string>
    {
        { "Iron Sword", "sword_iron" },
        { "Steel Shield", "shield_steel" },
        { "Health Potion", "potion_health" }
    };
}
```

### File/Folder Paths

```csharp
[FilePath]
[SerializeField]
private string _configPath;

[FolderPath]
[SerializeField]
private string _dataFolder;

[FilePath(Extensions = "txt,json")]
[SerializeField]
private string _dataFilePath;
```

---

## Attribute Combinations

Attributes can be combined for powerful effects.

### Example 1: Validated Dictionary with Info

```csharp
[InfoBox("Item ID must be unique. Price must be positive.")]
[DictionaryDrawerSettings(KeyLabel = "Item ID", ValueLabel = "Price")]
[ValidateInput(nameof(ValidatePrices), "All prices must be positive!")]
[SerializeField]
private Dictionary<string, int> _itemPrices = new();

private bool ValidatePrices(Dictionary<string, int> dict)
{
    return dict.Values.All(price => price > 0);
}
```

### Example 2: Conditional Button Group

```csharp
[SerializeField] private bool _debugMode;

[ShowIf(nameof(_debugMode))]
[ButtonGroup("Debug Tools")]
[Button("Spawn Enemy")]
private void SpawnEnemy() { }

[ShowIf(nameof(_debugMode))]
[ButtonGroup("Debug Tools")]
[Button("Clear All")]
private void ClearAll() { }
```

### Example 3: Styled Tabs with Validation

```csharp
[TabGroup("Core")]
[Required]
[AssetsOnly]
[SerializeField] private GameObject _playerPrefab;

[TabGroup("Core")]
[MinValue(1), MaxValue(4)]
[SerializeField] private int _playerCount = 1;

[TabGroup("Advanced")]
[ShowIf(nameof(_debugMode))]
[InfoBox("Debug features enabled!", InfoMessageType.Warning)]
[GUIColor(1, 0.5f, 0.5f)]
[SerializeField] private bool _godMode;
```

---

## Performance Considerations

### Odin Serializer Performance

| Aspect                    | Impact                    | Notes                            |
| ------------------------- | ------------------------- | -------------------------------- |
| **Serialization Speed**   | ~10-20% slower than Unity | Only affects editor, not runtime |
| **Deserialization Speed** | Similar to Unity          | Minimal impact                   |
| **Build Size**            | +2-5MB                    | Includes Odin runtime library    |
| **Runtime Performance**   | Identical to Unity        | Zero performance difference      |

### Odin Inspector Performance

| Feature                   | Cost       | Recommendation                       |
| ------------------------- | ---------- | ------------------------------------ |
| `[ShowInInspector]`       | Medium     | Use sparingly; re-evaluates often    |
| `[Button]`                | Low        | No performance cost                  |
| `[ValueDropdown]`         | Low-Medium | Cache large lists                    |
| Complex validation        | Medium     | Avoid in Update-like methods         |
| Table lists (1000+ items) | High       | Paginate with `NumberOfItemsPerPage` |

### Best Practices

✅ **DO:**

- Use `SerializedMonoBehaviour` only when needed
- Cache expensive dropdown value providers
- Use `[OnValueChanged]` instead of polling
- Serialize dictionaries instead of parallel lists

❌ **DON'T:**

- Put expensive logic in `[ShowInInspector]` properties
- Serialize massive dictionaries (>10,000 items) without testing
- Use Odin for every script (vanilla Unity is faster for simple cases)

---

## Next Steps

- **[Advanced Techniques](03-ADVANCED-TECHNIQUES.md)** — Custom processors, editor workflows
- **[Common Patterns](04-COMMON-PATTERNS.md)** — Real-world recipes and examples
- **[Best Practices](05-BEST-PRACTICES.md)** — Optimization, pitfalls, team workflows

---

**Key Takeaways:**

- Odin Serializer: Serialize **anything** (dictionaries, properties, interfaces)
- Odin Inspector: Enhance Inspector with **buttons, validation, conditional visibility**
- Attributes can be **combined** for powerful effects
- Performance cost is **minimal** and only affects the editor
