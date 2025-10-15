# Best Practices & Pitfalls

> **What to do, what NOT to do, and why.** Learn from production experience to avoid common mistakes
> and optimize your Odin workflow.

---

## Table of Contents

1. [Serialization Best Practices](#serialization-best-practices)
2. [Performance Optimization](#performance-optimization)
3. [Common Mistakes & Solutions](#common-mistakes--solutions)
4. [Editor vs Runtime Considerations](#editor-vs-runtime-considerations)
5. [Version Control & Team Workflows](#version-control--team-workflows)
6. [Build Size Management](#build-size-management)
7. [Pre-Ship Checklist](#pre-ship-checklist)

---

## Serialization Best Practices

### ✅ DO: Use SerializedMonoBehaviour Only When Needed

**Good:**

```csharp
// Simple script with basic fields → use MonoBehaviour
public class HealthBar : MonoBehaviour
{
    [SerializeField] private Image _fillImage;
    [SerializeField] private float _maxHealth = 100f;
}

// Complex script with dictionaries → use SerializedMonoBehaviour
public class ItemDatabase : SerializedMonoBehaviour
{
    [SerializeField] private Dictionary<string, ItemData> _items = new();
}
```

**Why:** Vanilla Unity serialization is faster. Only use Odin when you need its features.

---

### ✅ DO: Initialize Dictionaries and Collections

**Good:**

```csharp
[SerializeField]
private Dictionary<string, int> _scores = new();  // ✅ Initialized

[SerializeField]
private List<Item> _items = new();  // ✅ Initialized
```

**Bad:**

```csharp
[SerializeField]
private Dictionary<string, int> _scores;  // ❌ null by default

void Start()
{
    _scores.Add("player", 100);  // ❌ NullReferenceException!
}
```

**Why:** Null dictionaries/lists cause runtime errors. Always initialize.

---

### ✅ DO: Use [NonSerialized] for Runtime-Only Data

**Good:**

```csharp
[SerializeField]
private Dictionary<string, GameObject> _prefabs = new();

[NonSerialized]
private Dictionary<string, GameObject> _spawnedInstances = new();  // Runtime cache
```

**Why:** Runtime caches don't need to be serialized. Reduces save file size and serialization time.

---

### ❌ DON'T: Serialize Unity Objects in Dictionaries Without Caution

**Problematic:**

```csharp
// This works but can cause issues with scene references
[SerializeField]
private Dictionary<string, Transform> _sceneObjects = new();
```

**Better:**

```csharp
// For prefabs (assets)
[SerializeField]
private Dictionary<string, GameObject> _prefabs = new();

// For scene objects, use direct references
[SerializeField]
private Transform _spawnPoint;

[SerializeField]
private Transform _exitPoint;
```

**Why:** Dictionary keys with UnityEngine.Object references can break if objects are destroyed or
references lost.

---

### ✅ DO: Validate Dictionary Keys

**Good:**

```csharp
[ValidateInput(nameof(ValidateKeys), "Dictionary keys must not be empty!")]
[SerializeField]
private Dictionary<string, ItemData> _items = new();

private bool ValidateKeys(Dictionary<string, ItemData> dict)
{
    return dict.Keys.All(key => !string.IsNullOrWhiteSpace(key));
}
```

**Why:** Empty or null keys cause hard-to-debug issues. Validate early!

---

## Performance Optimization

### ✅ DO: Cache Expensive Dropdown Providers

**Good:**

```csharp
private static List<string> _cachedItemIDs;

[ValueDropdown(nameof(GetItemIDs))]
[SerializeField]
private string _selectedItemID;

private IEnumerable<string> GetItemIDs()
{
    if (_cachedItemIDs == null)
    {
        _cachedItemIDs = LoadAllItemIDs();  // Expensive operation
    }
    return _cachedItemIDs;
}
```

**Bad:**

```csharp
[ValueDropdown(nameof(GetItemIDs))]
[SerializeField]
private string _selectedItemID;

private IEnumerable<string> GetItemIDs()
{
    return LoadAllItemIDs();  // ❌ Runs EVERY Inspector repaint!
}
```

**Why:** Dropdown providers run on every Inspector repaint. Cache results!

---

### ✅ DO: Avoid Heavy Logic in [ShowInInspector] Properties

**Good:**

```csharp
[ShowInInspector, ReadOnly]
private int TotalItems => _items.Count;  // ✅ Fast

[Button]
private void CalculateComplexStats()  // ✅ Only runs when clicked
{
    int result = ExpensiveCalculation();
    Debug.Log($"Result: {result}");
}
```

**Bad:**

```csharp
[ShowInInspector, ReadOnly]
private int ComplexCalculation
{
    get
    {
        // ❌ This runs CONSTANTLY while Inspector is open!
        return ExpensiveCalculation();
    }
}
```

**Why:** `[ShowInInspector]` properties re-evaluate continuously. Use buttons for expensive
operations.

---

### ✅ DO: Paginate Large Table Lists

**Good:**

```csharp
[TableList(ShowIndexLabels = true, NumberOfItemsPerPage = 25)]
[SerializeField]
private List<EnemyData> _enemies = new();  // Could have 1000+ items
```

**Why:** Large table lists without pagination slow down the Inspector.

---

### ❌ DON'T: Serialize Massive Dictionaries

**Problematic:**

```csharp
// 10,000+ entries
[SerializeField]
private Dictionary<int, Vector3> _allPositions = new();
```

**Better:**

```csharp
// Store in external file or database
[FilePath]
[SerializeField]
private string _positionsDataPath;

private Dictionary<int, Vector3> _positions;  // Load at runtime

void Start()
{
    _positions = LoadPositionsFromFile(_positionsDataPath);
}
```

**Why:** Very large dictionaries (>5,000 entries) slow down serialization. Use external storage.

---

## Common Mistakes & Solutions

### Mistake #1: Forgetting to Inherit SerializedMonoBehaviour

**Symptom:** Dictionary appears empty in Inspector, doesn't serialize.

**Bad:**

```csharp
using Sirenix.OdinInspector;

public class Example : MonoBehaviour  // ❌ Wrong base class!
{
    [SerializeField]
    private Dictionary<string, int> _data = new();
}
```

**Fixed:**

```csharp
using Sirenix.OdinInspector;

public class Example : SerializedMonoBehaviour  // ✅ Correct!
{
    [SerializeField]
    private Dictionary<string, int> _data = new();
}
```

---

### Mistake #2: Mixing [SerializeField] and [ShowInInspector]

**Problem:** Confusion about when to use which.

**Rule:**

- `[SerializeField]` — For fields that should **persist** (save to disk)
- `[ShowInInspector]` — For properties/fields that should **display** but may not persist

**Example:**

```csharp
// Persisted field
[SerializeField]
private int _health = 100;

// Display-only computed property
[ShowInInspector, ReadOnly]
public bool IsAlive => _health > 0;

// Non-serialized field shown for debugging
[ShowInInspector, NonSerialized]
private float _lastDamageTime;
```

---

### Mistake #3: Not Clearing OwnedEvents Equivalent

**Symptom:** Buttons or callbacks fire multiple times unexpectedly.

**Problem Pattern:**

```csharp
[Button]
private void SetupCallbacks()
{
    SomeEvent += OnSomeEvent;  // ❌ Adds another listener each click!
}
```

**Fixed:**

```csharp
[Button]
private void SetupCallbacks()
{
    SomeEvent -= OnSomeEvent;  // ✅ Remove first
    SomeEvent += OnSomeEvent;  // ✅ Then add
}
```

---

### Mistake #4: Using Buttons That Modify Scene in Edit Mode Without Undo

**Bad:**

```csharp
[Button]
private void SpawnEnemies()
{
    for (int i = 0; i < 10; i++)
    {
        Instantiate(_enemyPrefab);  // ❌ No undo support!
    }
}
```

**Good:**

```csharp
[Button]
private void SpawnEnemies()
{
    #if UNITY_EDITOR
    for (int i = 0; i < 10; i++)
    {
        var instance = (GameObject)UnityEditor.PrefabUtility.InstantiatePrefab(_enemyPrefab);
        UnityEditor.Undo.RegisterCreatedObjectUndo(instance, "Spawn Enemy");  // ✅ Undo support
    }
    #endif
}
```

**Why:** Edit-mode changes without undo are frustrating. Always support undo!

---

### Mistake #5: Forgetting Editor Conditionals

**Bad:**

```csharp
[Button]
private void EditorOnlyMethod()
{
    UnityEditor.AssetDatabase.Refresh();  // ❌ Compiler error in build!
}
```

**Good:**

```csharp
[Button]
private void EditorOnlyMethod()
{
    #if UNITY_EDITOR
    UnityEditor.AssetDatabase.Refresh();  // ✅ Compiles out of builds
    #endif
}
```

---

### Mistake #6: Serializing Properties Without Backing Fields

**Problematic:**

```csharp
[ShowInInspector]
public int Health { get; set; } = 100;  // ⚠️ May not serialize correctly
```

**Better:**

```csharp
[SerializeField]
private int _health = 100;

[ShowInInspector]
public int Health
{
    get => _health;
    set => _health = Mathf.Max(0, value);
}
```

**Why:** Auto-properties can be unreliable for serialization. Use backing fields for critical data.

---

## Editor vs Runtime Considerations

### ✅ DO: Wrap Editor-Only Code

```csharp
public class GameManager : SerializedMonoBehaviour
{
    [SerializeField] private int _lives = 3;

    // Always available
    public void LoseLife()
    {
        _lives--;
    }

    #if UNITY_EDITOR
    // Compiles out of builds
    [Title("Debug Tools")]
    [Button]
    private void ResetLives()
    {
        _lives = 3;
    }

    [ShowInInspector, ReadOnly]
    private string DebugInfo => $"Lives: {_lives}";
    #endif
}
```

---

### ✅ DO: Use [DisableInEditorMode] for Play-Only Buttons

```csharp
[Button, DisableInEditorMode]  // Grayed out in edit mode
private void SpawnEnemy()
{
    // This should only run during play mode
    Instantiate(_enemyPrefab, _spawnPoint.position, Quaternion.identity);
}
```

---

### ❌ DON'T: Modify Scene Objects from Edit Mode Without Care

**Bad:**

```csharp
[Button]
private void ModifyAllEnemies()
{
    var enemies = FindObjectsOfType<Enemy>();
    foreach (var enemy in enemies)
    {
        enemy.Health = 100;  // ❌ No undo, no dirty flag
    }
}
```

**Good:**

```csharp
[Button]
private void ModifyAllEnemies()
{
    #if UNITY_EDITOR
    var enemies = FindObjectsOfType<Enemy>();
    foreach (var enemy in enemies)
    {
        UnityEditor.Undo.RecordObject(enemy, "Set Enemy Health");
        enemy.Health = 100;
        UnityEditor.EditorUtility.SetDirty(enemy);
    }
    #endif
}
```

---

## Version Control & Team Workflows

### ✅ DO: Use Text Serialization

Ensure your project uses text-based scene/prefab serialization:

**Edit → Project Settings → Editor**

- Asset Serialization: **Force Text**
- Line Endings For New Scripts: **Unix**

**Why:** Odin serialization creates clean text diffs in Git. Binary mode loses this benefit.

---

### ✅ DO: Document Custom Attributes

```csharp
/// <summary>
/// Manages all game items. Use the Inspector to add/edit items.
/// Dictionary key = item ID (must be unique).
/// Dictionary value = item data (prefab, price, description).
/// </summary>
public class ItemDatabase : SerializedScriptableObject
{
    [DictionaryDrawerSettings(KeyLabel = "Item ID", ValueLabel = "Item Data")]
    [InfoBox("Item IDs must be unique! Use lowercase with underscores (e.g., 'health_potion').")]
    [SerializeField]
    private Dictionary<string, ItemData> _items = new();
}
```

**Why:** Teammates need context. Document complex dictionaries and workflows.

---

### ✅ DO: Create Validation Scripts

```csharp
#if UNITY_EDITOR
using UnityEditor;

public static class ProjectValidator
{
    [MenuItem("Tools/Validate All Odin Data")]
    public static void ValidateAllData()
    {
        var allDatabases = AssetDatabase.FindAssets("t:SerializedScriptableObject");
        int errors = 0;

        foreach (var guid in allDatabases)
        {
            string path = AssetDatabase.GUIDToAssetPath(guid);
            var asset = AssetDatabase.LoadAssetAtPath<SerializedScriptableObject>(path);

            // Validate asset...
            // (Custom validation logic here)
        }

        Debug.Log(errors == 0 ? "✓ All data validated!" : $"✗ {errors} error(s) found!");
    }
}
#endif
```

**Why:** Pre-commit validation catches errors before they reach version control.

---

### ❌ DON'T: Commit .meta Files Without Testing

Always test that:

1. Odin data serializes correctly
2. References aren't broken
3. Dictionary data persists

**Best Practice:** After pulling changes, open all Odin-heavy ScriptableObjects and verify data
integrity.

---

## Build Size Management

### Minimize Build Size Impact

| Technique                                | Size Reduction |
| ---------------------------------------- | -------------- |
| Wrap editor code in `#if UNITY_EDITOR`   | ~100-500KB     |
| Strip unused Odin features (Preferences) | ~500KB-1MB     |
| Don't serialize massive collections      | Varies         |
| Use `[NonSerialized]` for runtime data   | ~10-100KB      |

### ✅ DO: Profile Build Size

```csharp
#if UNITY_EDITOR
[MenuItem("Tools/Analyze Odin Build Size")]
public static void AnalyzeBuildSize()
{
    var report = BuildPipeline.BuildPlayer(
        EditorBuildSettings.scenes,
        "Builds/Test",
        EditorUserBuildSettings.activeBuildTarget,
        BuildOptions.None
    );

    Debug.Log($"Total Build Size: {report.summary.totalSize / (1024 * 1024):F2} MB");
    // Analyze report for Odin DLLs...
}
#endif
```

---

### ✅ DO: Remove Debug Tools from Builds

**Development Build:**

```csharp
public class DevTools : SerializedMonoBehaviour
{
    [Button] private void GodMode() { }
    [Button] private void SpawnItems() { }
}
```

**Production Build:**

```csharp
#if UNITY_EDITOR || DEVELOPMENT_BUILD
public class DevTools : SerializedMonoBehaviour
{
    [Button] private void GodMode() { }
    [Button] private void SpawnItems() { }
}
#endif
```

---

## Pre-Ship Checklist

### Before Shipping Your Game

#### ✅ Validate All Odin Data

- [ ] All `[Required]` fields are assigned
- [ ] No duplicate dictionary keys
- [ ] All prefab references are valid
- [ ] No missing ScriptableObject references

#### ✅ Performance Check

- [ ] No expensive logic in `[ShowInInspector]` properties
- [ ] Large collections use pagination
- [ ] Dropdown providers are cached
- [ ] No memory leaks from event subscriptions

#### ✅ Build Check

- [ ] All editor code wrapped in `#if UNITY_EDITOR`
- [ ] Debug tools removed or gated behind `DEVELOPMENT_BUILD`
- [ ] Build size is acceptable
- [ ] No Odin-related runtime errors in builds

#### ✅ Team Workflow

- [ ] Custom attributes documented
- [ ] Validation scripts created
- [ ] Data schemas documented
- [ ] Teammates trained on Odin workflows

---

## Performance Comparison

### Odin vs Vanilla Unity

| Metric                    | Vanilla Unity | Odin   | Notes                           |
| ------------------------- | ------------- | ------ | ------------------------------- |
| **Serialization Speed**   | 100%          | ~85%   | Editor-only, negligible impact  |
| **Deserialization Speed** | 100%          | ~95%   | Slightly slower                 |
| **Inspector Draw Time**   | 100%          | ~90%   | More features = slightly slower |
| **Runtime Performance**   | 100%          | 100%   | Identical!                      |
| **Build Size**            | Baseline      | +2-5MB | Odin runtime included           |

**Takeaway:** Odin's performance cost is minimal and limited to the editor. Runtime performance is
identical.

---

## Summary Checklist

### DO ✅

| Practice                                       | Benefit                               |
| ---------------------------------------------- | ------------------------------------- |
| Use `SerializedMonoBehaviour` only when needed | Better performance for simple scripts |
| Initialize collections                         | Avoid NullReferenceExceptions         |
| Use `[NonSerialized]` for runtime data         | Reduce serialization overhead         |
| Cache expensive dropdown providers             | Faster Inspector                      |
| Validate dictionary keys                       | Catch errors early                    |
| Paginate large lists                           | Better Inspector performance          |
| Wrap editor code in `#if UNITY_EDITOR`         | Reduce build size                     |
| Support undo for edit-mode changes             | Better UX                             |
| Document complex dictionaries                  | Team productivity                     |
| Create validation tools                        | Data integrity                        |

### DON'T ❌

| Mistake                                     | Consequence              |
| ------------------------------------------- | ------------------------ |
| Forget `SerializedMonoBehaviour`            | Data won't serialize     |
| Put expensive logic in `[ShowInInspector]`  | Inspector lag            |
| Serialize massive dictionaries (>10k items) | Slow editor              |
| Modify scene in edit mode without undo      | Frustrating workflow     |
| Forget `#if UNITY_EDITOR` for editor code   | Build errors             |
| Use auto-properties for critical data       | Unreliable serialization |
| Mix Unity Objects in dictionary keys        | Broken references        |
| Ignore validation                           | Runtime bugs             |

---

## Final Advice

**Start Simple:** Begin with dictionaries and buttons. Master the basics before diving into custom
processors.

**Validate Early:** Use `[Required]` and `[ValidateInput]` liberally. Catching errors in the editor
saves debugging time.

**Profile First:** Only optimize if you have actual performance issues. Odin is fast enough for most
projects.

**Document Everything:** Your future self (and teammates) will thank you.

**Embrace Iteration:** Odin makes iteration fast. Use it to empower designers and speed up
workflows.

---

**Key Takeaways:**

- Use Odin where it provides value, not everywhere
- Performance cost is minimal and editor-only
- Validation and documentation are critical for teams
- Wrap editor code in `#if UNITY_EDITOR`
- Test builds early and often

**Happy Serializing!** 🎉
