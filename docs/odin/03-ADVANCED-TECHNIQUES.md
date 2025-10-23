# Advanced Techniques

> **TL;DR**: Custom processors, editor-only workflows, complex validation, custom drawers, build
> pipeline considerations, and integration patterns.

This guide covers advanced Odin usage for power users and teams building complex editor tools.

---

## Table of Contents

1. [Custom Attribute Processors](#custom-attribute-processors)
2. [Editor-Only Fields and Workflows](#editor-only-fields-and-workflows)
3. [Complex Validation Systems](#complex-validation-systems)
4. [Custom Type Drawers](#custom-type-drawers)
5. [Integration with External Systems](#integration-with-external-systems)
6. [Build Pipeline Considerations](#build-pipeline-considerations)
7. [Advanced Serialization](#advanced-serialization)

---

## Custom Attribute Processors

Create your own Odin-style attributes.

### Creating a Custom Attribute

```csharp
using System;
using Sirenix.OdinInspector;

/// <summary>
/// Highlights fields in a custom color.
/// </summary>
[AttributeUsage(AttributeTargets.Field | AttributeTargets.Property)]
public class HighlightAttribute : Attribute
{
    public float R { get; set; }
    public float G { get; set; }
    public float B { get; set; }

    public HighlightAttribute(float r, float g, float b)
    {
        R = r;
        G = g;
        B = b;
    }
}
```

### Creating a Custom Drawer

```csharp
#if UNITY_EDITOR
using Sirenix.OdinInspector.Editor;
using UnityEditor;
using UnityEngine;

public class HighlightAttributeDrawer : OdinAttributeDrawer<HighlightAttribute>
{
    protected override void DrawPropertyLayout(GUIContent label)
    {
        var attribute = this.Attribute;
        var previousColor = GUI.backgroundColor;

        GUI.backgroundColor = new Color(attribute.R, attribute.G, attribute.B);
        EditorGUILayout.BeginVertical(GUI.skin.box);

        CallNextDrawer(label);

        EditorGUILayout.EndVertical();
        GUI.backgroundColor = previousColor;
    }
}
#endif
```

### Usage

```csharp
public class Example : SerializedMonoBehaviour
{
    [Highlight(1f, 0.8f, 0.8f)]  // Light red background
    [SerializeField] private int _health;

    [Highlight(0.8f, 1f, 0.8f)]  // Light green background
    [SerializeField] private int _mana;
}
```

---

## Editor-Only Fields and Workflows

Create fields and methods that only exist in the editor.

### Editor-Only Debug Fields

```csharp
public class PlayerController : SerializedMonoBehaviour
{
    [SerializeField] private float _speed = 5f;

    #if UNITY_EDITOR
    [Title("Editor-Only Debug Info", "These don't exist in builds")]
    [ShowInInspector, ReadOnly]
    private string DebugInfo => $"Speed: {_speed}, Position: {transform.position}";

    [ShowInInspector, ReadOnly]
    private float CurrentVelocity
    {
        get
        {
            Rigidbody rb = GetComponent<Rigidbody>();
            return rb != null ? rb.velocity.magnitude : 0f;
        }
    }

    [Button("Teleport to Origin"), GUIColor(0.4f, 0.8f, 1f)]
    private void TeleportToOrigin()
    {
        transform.position = Vector3.zero;
        UnityEditor.EditorUtility.SetDirty(this);
    }
    #endif
}
```

**Result:** Debug fields and buttons compile out of release builds, saving space.

### Editor-Only Validation

```csharp
public class SpawnManager : SerializedMonoBehaviour
{
    [SerializeField] private GameObject _enemyPrefab;
    [SerializeField] private Transform _spawnPoint;

    #if UNITY_EDITOR
    [Button("Validate Setup"), PropertyOrder(-1)]
    private void ValidateSetup()
    {
        if (_enemyPrefab == null)
        {
            Debug.LogError("Enemy prefab is not assigned!", this);
            return;
        }

        if (_spawnPoint == null)
        {
            Debug.LogError("Spawn point is not assigned!", this);
            return;
        }

        if (UnityEditor.PrefabUtility.IsPartOfPrefabAsset(_spawnPoint.gameObject))
        {
            Debug.LogError("Spawn point must be a scene object, not a prefab!", this);
            return;
        }

        Debug.Log("✓ Setup validated successfully!", this);
    }
    #endif
}
```

### Editor-Only Asset Generation

```csharp
public class LevelGenerator : SerializedMonoBehaviour
{
    [SerializeField] private int _width = 10;
    [SerializeField] private int _height = 10;

    #if UNITY_EDITOR
    [Button(ButtonSizes.Large), GUIColor(0.4f, 1f, 0.4f)]
    private void GenerateLevelAsset()
    {
        var levelData = GenerateLevelData();
        SaveLevelAsset(levelData);
    }

    private LevelData GenerateLevelData()
    {
        // Complex generation logic...
        return new LevelData();
    }

    private void SaveLevelAsset(LevelData data)
    {
        string path = UnityEditor.EditorUtility.SaveFilePanelInProject(
            "Save Level Data",
            "LevelData",
            "asset",
            "Save generated level data"
        );

        if (!string.IsNullOrEmpty(path))
        {
            UnityEditor.AssetDatabase.CreateAsset(data, path);
            UnityEditor.AssetDatabase.SaveAssets();
            Debug.Log($"Level asset saved: {path}");
        }
    }
    #endif
}
```

---

## Complex Validation Systems

Build robust data validation.

### Cross-Field Validation

```csharp
public class CharacterStats : SerializedMonoBehaviour
{
    [MinValue(0)]
    [SerializeField] private int _health = 100;

    [MinValue(0)]
    [SerializeField] private int _maxHealth = 100;

    [ValidateInput(nameof(ValidateHealth), "Health cannot exceed Max Health!")]
    [SerializeField] private bool _validateHealthCheck;

    private bool ValidateHealth()
    {
        return _health <= _maxHealth;
    }

    [InfoBox("$" + nameof(GetValidationMessage), InfoMessageType.Error, VisibleIf = nameof(ShowValidationError))]
    [Button("Fix Health")]
    private void FixHealth()
    {
        if (_health > _maxHealth)
        {
            _health = _maxHealth;
        }
    }

    private bool ShowValidationError() => _health > _maxHealth;

    private string GetValidationMessage()
    {
        return $"Health ({_health}) exceeds Max Health ({_maxHealth})!";
    }
}
```

### Collection Validation

```csharp
public class ItemDatabase : SerializedMonoBehaviour
{
    [ValidateInput(nameof(ValidateNoDuplicateIDs), "Duplicate item IDs detected!")]
    [DictionaryDrawerSettings(KeyLabel = "Item ID", ValueLabel = "Item Data")]
    [OdinSerialize]
    private Dictionary<string, ItemData> _items = new();

    [ValidateInput(nameof(ValidateAllPricesPositive), "All prices must be positive!")]
    [DictionaryDrawerSettings(KeyLabel = "Item ID", ValueLabel = "Price")]
    [OdinSerialize]
    private Dictionary<string, int> _prices = new();

    private bool ValidateNoDuplicateIDs(Dictionary<string, ItemData> dict)
    {
        // Dictionary keys are inherently unique, but we can validate values
        var names = dict.Values.Select(item => item.Name).ToList();
        return names.Count == names.Distinct().Count();
    }

    private bool ValidateAllPricesPositive(Dictionary<string, int> dict)
    {
        return dict.Values.All(price => price > 0);
    }

    [Button("Validate All Data"), PropertyOrder(-1)]
    private void ValidateAll()
    {
        int errors = 0;

        foreach (var kvp in _items)
        {
            if (!_prices.ContainsKey(kvp.Key))
            {
                Debug.LogError($"Missing price for item: {kvp.Key}");
                errors++;
            }
        }

        foreach (var kvp in _prices)
        {
            if (!_items.ContainsKey(kvp.Key))
            {
                Debug.LogError($"Price defined for non-existent item: {kvp.Key}");
                errors++;
            }
        }

        if (errors == 0)
        {
            Debug.Log("✓ All data validated successfully!");
        }
        else
        {
            Debug.LogError($"Validation failed with {errors} error(s)!");
        }
    }
}
```

### Reference Validation

```csharp
public class PrefabSpawner : SerializedMonoBehaviour
{
    [Required]
    [AssetsOnly]
    [ValidateInput(nameof(ValidatePrefabHasComponent), "Prefab must have Enemy component!")]
    [SerializeField]
    private GameObject _enemyPrefab;

    private bool ValidatePrefabHasComponent(GameObject prefab)
    {
        if (prefab == null) return true;  // [Required] handles null check
        return prefab.GetComponent<Enemy>() != null;
    }
}
```

---

## Custom Type Drawers

Create custom Inspector views for complex types.

### Custom Drawer for Range2D

```csharp
[System.Serializable]
public struct Range2D
{
    public float Min;
    public float Max;
}

#if UNITY_EDITOR
using Sirenix.OdinInspector.Editor;
using UnityEditor;
using UnityEngine;

public class Range2DDrawer : OdinValueDrawer<Range2D>
{
    protected override void DrawPropertyLayout(GUIContent label)
    {
        var rect = EditorGUILayout.GetControlRect(label != null);

        if (label != null)
        {
            rect = EditorGUI.PrefixLabel(rect, label);
        }

        var value = this.ValueEntry.SmartValue;

        var minRect = new Rect(rect.x, rect.y, rect.width * 0.45f, rect.height);
        var maxRect = new Rect(rect.x + rect.width * 0.55f, rect.y, rect.width * 0.45f, rect.height);

        value.Min = EditorGUI.FloatField(minRect, value.Min);
        EditorGUI.LabelField(new Rect(rect.x + rect.width * 0.45f, rect.y, rect.width * 0.1f, rect.height), "-", EditorStyles.centeredGreyMiniLabel);
        value.Max = EditorGUI.FloatField(maxRect, value.Max);

        // Clamp min/max
        if (value.Min > value.Max)
        {
            value.Min = value.Max;
        }

        this.ValueEntry.SmartValue = value;
    }
}
#endif

// Usage:
public class Example : SerializedMonoBehaviour
{
    [SerializeField] private Range2D _damageRange = new Range2D { Min = 10, Max = 20 };
}
```

---

## Integration with External Systems

### JSON Export/Import

```csharp
using Sirenix.OdinInspector;
using System.Collections.Generic;
using UnityEngine;

public class ConfigManager : SerializedMonoBehaviour
{
    [DictionaryDrawerSettings(KeyLabel = "Setting Name", ValueLabel = "Value")]
    [OdinSerialize]
    private Dictionary<string, string> _settings = new();

    [FoldoutGroup("Import/Export")]
    [Button("Export to JSON")]
    private void ExportToJSON()
    {
        #if UNITY_EDITOR
        string json = JsonUtility.ToJson(new SerializableDict(_settings), prettyPrint: true);
        string path = UnityEditor.EditorUtility.SaveFilePanel("Export Settings", "", "settings.json", "json");

        if (!string.IsNullOrEmpty(path))
        {
            System.IO.File.WriteAllText(path, json);
            Debug.Log($"Exported to: {path}");
        }
        #endif
    }

    [FoldoutGroup("Import/Export")]
    [Button("Import from JSON")]
    private void ImportFromJSON()
    {
        #if UNITY_EDITOR
        string path = UnityEditor.EditorUtility.OpenFilePanel("Import Settings", "", "json");

        if (!string.IsNullOrEmpty(path))
        {
            string json = System.IO.File.ReadAllText(path);
            var data = JsonUtility.FromJson<SerializableDict>(json);
            _settings = data.ToDictionary();
            Debug.Log($"Imported from: {path}");
        }
        #endif
    }

    [System.Serializable]
    private class SerializableDict
    {
        public List<string> keys = new();
        public List<string> values = new();

        public SerializableDict(Dictionary<string, string> dict)
        {
            keys = dict.Keys.ToList();
            values = dict.Values.ToList();
        }

        public Dictionary<string, string> ToDictionary()
        {
            var dict = new Dictionary<string, string>();
            for (int i = 0; i < keys.Count && i < values.Count; i++)
            {
                dict[keys[i]] = values[i];
            }
            return dict;
        }
    }
}
```

### CSV Export for Game Design

```csharp
public class EnemyDatabase : SerializedMonoBehaviour
{
    [System.Serializable]
    public class EnemyData
    {
        public string ID;
        public string Name;
        public int Health;
        public float Speed;
        public int Damage;
    }

    [TableList]
    [SerializeField]
    private List<EnemyData> _enemies = new();

    [Button("Export to CSV for Game Design")]
    private void ExportToCSV()
    {
        #if UNITY_EDITOR
        var csv = new System.Text.StringBuilder();
        csv.AppendLine("ID,Name,Health,Speed,Damage");

        foreach (var enemy in _enemies)
        {
            csv.AppendLine($"{enemy.ID},{enemy.Name},{enemy.Health},{enemy.Speed},{enemy.Damage}");
        }

        string path = UnityEditor.EditorUtility.SaveFilePanel("Export Enemies", "", "enemies.csv", "csv");
        if (!string.IsNullOrEmpty(path))
        {
            System.IO.File.WriteAllText(path, csv.ToString());
            Debug.Log($"Exported {_enemies.Count} enemies to: {path}");
        }
        #endif
    }
}
```

---

## Build Pipeline Considerations

### Stripping Editor-Only Code

Always wrap editor code in `#if UNITY_EDITOR`:

```csharp
public class GameManager : SerializedMonoBehaviour
{
    [SerializeField] private int _lives = 3;

    #if UNITY_EDITOR
    // This entire section compiles out of builds
    [Title("Debug Tools")]
    [Button]
    private void AddLife()
    {
        _lives++;
    }
    #endif

    // This always exists
    public void LoseLife()
    {
        _lives--;
    }
}
```

### Build Size Management

| Technique                                               | Build Size Reduction |
| ------------------------------------------------------- | -------------------- |
| Use `#if UNITY_EDITOR` for debug tools                  | ~100-500KB           |
| Don't serialize huge dictionaries                       | Varies               |
| Use `[NonSerialized]` for runtime-only data             | ~10-100KB            |
| Strip unused Odin features (Tools → Odin → Preferences) | ~500KB-1MB           |

### Build Validation

```csharp
#if UNITY_EDITOR
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.Build.Reporting;
using UnityEngine;

public class OdinBuildValidator : IPreprocessBuildWithReport
{
    public int callbackOrder => 0;

    public void OnPreprocessBuild(BuildReport report)
    {
        Debug.Log("Validating Odin serialized data before build...");

        var allComponents = GameObject.FindObjectsOfType<SerializedMonoBehaviour>();
        int errors = 0;

        foreach (var component in allComponents)
        {
            // Example: Check for null required fields
            var type = component.GetType();
            var fields = type.GetFields(System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Public);

            foreach (var field in fields)
            {
                var requiredAttr = field.GetCustomAttribute<Sirenix.OdinInspector.RequiredAttribute>();
                if (requiredAttr != null)
                {
                    var value = field.GetValue(component);
                    if (value == null || value.Equals(null))
                    {
                        Debug.LogError($"[Build Validation] Required field '{field.Name}' is null on {component.name}", component);
                        errors++;
                    }
                }
            }
        }

        if (errors > 0)
        {
            throw new BuildFailedException($"Build validation failed with {errors} error(s). Check console for details.");
        }

        Debug.Log("✓ Odin validation passed!");
    }
}
#endif
```

---

## Advanced Serialization

### Polymorphic Serialization with UI

```csharp
public interface IAbility
{
    string Name { get; }
    void Execute();
}

[System.Serializable]
public class FireballAbility : IAbility
{
    public string Name => "Fireball";
    public float Damage = 50f;
    public float Range = 10f;

    public void Execute()
    {
        Debug.Log($"Cast Fireball! Damage: {Damage}, Range: {Range}");
    }
}

[System.Serializable]
public class HealAbility : IAbility
{
    public string Name => "Heal";
    public float HealAmount = 30f;

    public void Execute()
    {
        Debug.Log($"Cast Heal! Amount: {HealAmount}");
    }
}

public class AbilityManager : SerializedMonoBehaviour
{
    [ListDrawerSettings(ShowIndexLabels = true, ListElementLabelName = "Name")]
    [OdinSerialize]
    private List<IAbility> _abilities = new();

    [Button("Execute All Abilities")]
    private void ExecuteAll()
    {
        foreach (var ability in _abilities)
        {
            ability.Execute();
        }
    }
}
```

### Circular Reference Handling

Odin handles circular references automatically:

```csharp
[System.Serializable]
public class Node
{
    public string Name;
    public List<Node> Children = new();
    public Node Parent;  // Circular reference!
}

public class Graph : SerializedMonoBehaviour
{
    [OdinSerialize]
    private Node _rootNode;

    [Button]
    private void CreateCircularGraph()
    {
        var root = new Node { Name = "Root" };
        var child = new Node { Name = "Child", Parent = root };
        root.Children.Add(child);

        _rootNode = root;
        // Odin handles this without errors!
    }
}
```

### Generic Class Serialization

```csharp
[System.Serializable]
public class Container<T>
{
    public T Value;
}

public class GenericExample : SerializedMonoBehaviour
{
    [OdinSerialize]
    private Container<int> _intContainer;

    [OdinSerialize]
    private Container<GameObject> _prefabContainer;

    [OdinSerialize]
    private List<Container<string>> _stringContainers;

    // Odin serializes these perfectly!
}
```

---

## Next Steps

- **[Common Patterns](04-COMMON-PATTERNS.md)** — Real-world recipes and cookbook
- **[Best Practices](05-BEST-PRACTICES.md)** — Optimization, team workflows, pitfalls

---

**Key Takeaways:**

- Custom attributes and drawers extend Odin's functionality
- Editor-only workflows reduce build size and enable powerful tools
- Complex validation ensures data integrity
- Odin handles advanced serialization scenarios (polymorphism, circular refs, generics)
- Always wrap editor code in `#if UNITY_EDITOR`
