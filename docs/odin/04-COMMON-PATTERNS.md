# Common Patterns

> **Cookbook**: Copy-paste solutions for the most common Odin use cases. These are battle-tested
> patterns from real production codebases.

---

## Table of Contents

1. [Dictionary Patterns](#dictionary-patterns)
2. [Button Patterns](#button-patterns)
3. [Validation Patterns](#validation-patterns)
4. [Editor Workflow Patterns](#editor-workflow-patterns)
5. [UI/UX Patterns](#uiux-patterns)
6. [Architecture Patterns](#architecture-patterns)

---

## Dictionary Patterns

### Pattern 1: Item Database

**Problem:** Managing game items with IDs, prefabs, and metadata.

```csharp
using Sirenix.OdinInspector;
using System.Collections.Generic;
using UnityEngine;

[CreateAssetMenu(fileName = "ItemDatabase", menuName = "Game/Item Database")]
public class ItemDatabase : SerializedScriptableObject
{
    [System.Serializable]
    public class ItemData
    {
        [PreviewField(50)]
        public Sprite Icon;

        [Required]
        public GameObject Prefab;

        [TextArea(2, 4)]
        public string Description;

        [MinValue(0)]
        public int BasePrice;

        [MinValue(0)]
        public int MaxStackSize = 1;
    }

    [DictionaryDrawerSettings(
        KeyLabel = "Item ID",
        ValueLabel = "Item Data",
        DisplayMode = DictionaryDisplayOptions.Foldout
    )]
    [OdinSerialize]
    private Dictionary<string, ItemData> _items = new();

    public ItemData GetItem(string itemId)
    {
        _items.TryGetValue(itemId, out var item);
        return item;
    }

    [Button("Add Example Items"), PropertyOrder(-1)]
    private void AddExampleItems()
    {
        if (!_items.ContainsKey("health_potion"))
        {
            _items["health_potion"] = new ItemData
            {
                Description = "Restores 50 HP",
                BasePrice = 50,
                MaxStackSize = 10
            };
        }
    }

    [Button("Validate Database")]
    private void ValidateDatabase()
    {
        int errors = 0;

        foreach (var kvp in _items)
        {
            if (string.IsNullOrWhiteSpace(kvp.Key))
            {
                Debug.LogError("Empty item ID found!", this);
                errors++;
            }

            if (kvp.Value.Prefab == null)
            {
                Debug.LogError($"Missing prefab for item: {kvp.Key}", this);
                errors++;
            }
        }

        if (errors == 0)
        {
            Debug.Log($"✓ Database validated! {_items.Count} items, 0 errors.", this);
        }
        else
        {
            Debug.LogError($"✗ Validation failed with {errors} error(s)!", this);
        }
    }
}
```

### Pattern 2: State-Based Configuration

**Problem:** Different settings for different game states.

```csharp
public class GameStateConfig : SerializedScriptableObject
{
    public enum GameState
    {
        MainMenu,
        Playing,
        Paused,
        GameOver
    }

    [System.Serializable]
    public class StateSettings
    {
        [Range(0, 1)] public float TimeScale = 1f;
        public bool ShowUI = true;
        public bool AllowInput = true;
        [AssetsOnly] public AudioClip BackgroundMusic;
    }

    [DictionaryDrawerSettings(KeyLabel = "Game State", ValueLabel = "Settings")]
    [OdinSerialize]
    private Dictionary<GameState, StateSettings> _stateSettings = new();

    public StateSettings GetSettings(GameState state)
    {
        return _stateSettings.TryGetValue(state, out var settings) ? settings : null;
    }
}
```

### Pattern 3: Localization Dictionary

**Problem:** Multi-language text management.

```csharp
public class LocalizationData : SerializedScriptableObject
{
    [DictionaryDrawerSettings(KeyLabel = "Text ID", ValueLabel = "Localized Text")]
    [OdinSerialize]
    private Dictionary<string, string> _englishText = new();

    [DictionaryDrawerSettings(KeyLabel = "Text ID", ValueLabel = "Localized Text")]
    [OdinSerialize]
    private Dictionary<string, string> _spanishText = new();

    public string GetText(string textId, SystemLanguage language)
    {
        var dict = language == SystemLanguage.Spanish ? _spanishText : _englishText;
        return dict.TryGetValue(textId, out var text) ? text : $"[MISSING: {textId}]";
    }

    [Button("Find Missing Translations")]
    private void FindMissingTranslations()
    {
        var englishKeys = new HashSet<string>(_englishText.Keys);
        var spanishKeys = new HashSet<string>(_spanishText.Keys);

        var missingInSpanish = englishKeys.Except(spanishKeys).ToList();
        var extraInSpanish = spanishKeys.Except(englishKeys).ToList();

        if (missingInSpanish.Count > 0)
        {
            Debug.LogWarning($"Missing Spanish translations: {string.Join(", ", missingInSpanish)}");
        }

        if (extraInSpanish.Count > 0)
        {
            Debug.LogWarning($"Extra Spanish translations: {string.Join(", ", extraInSpanish)}");
        }

        if (missingInSpanish.Count == 0 && extraInSpanish.Count == 0)
        {
            Debug.Log("✓ All translations match!");
        }
    }
}
```

### Pattern 4: Enemy Wave Configuration

**Problem:** Defining waves of enemies with counts.

```csharp
public class WaveManager : SerializedMonoBehaviour
{
    [System.Serializable]
    public class WaveData
    {
        [DictionaryDrawerSettings(KeyLabel = "Enemy Type", ValueLabel = "Count")]
        public Dictionary<GameObject, int> EnemyComposition = new();

        [MinValue(1)]
        public float SpawnInterval = 1f;
    }

    [ListDrawerSettings(ShowIndexLabels = true, ListElementLabelName = "Wave")]
    [SerializeField]
    private List<WaveData> _waves = new();

    [ShowInInspector, ReadOnly]
    private int _currentWave = 0;

    [Button(ButtonSizes.Large), DisableInEditorMode]
    private void StartNextWave()
    {
        if (_currentWave >= _waves.Count)
        {
            Debug.Log("All waves complete!");
            return;
        }

        SpawnWave(_waves[_currentWave]);
        _currentWave++;
    }

    private void SpawnWave(WaveData wave)
    {
        foreach (var kvp in wave.EnemyComposition)
        {
            for (int i = 0; i < kvp.Value; i++)
            {
                // Spawn logic here
                Debug.Log($"Spawning {kvp.Key.name}");
            }
        }
    }
}
```

---

## Button Patterns

### Pattern 1: Development Tools Panel

**Problem:** Quick access to common dev functions.

```csharp
public class DevTools : SerializedMonoBehaviour
{
    [Title("Player Tools", "Quick player manipulation")]
    [HorizontalGroup("Player")]
    [Button(ButtonSizes.Large), GUIColor(0.4f, 1f, 0.4f)]
    private void FullHeal()
    {
        var player = FindObjectOfType<PlayerController>();
        if (player != null)
        {
            player.Health = player.MaxHealth;
            Debug.Log("Player healed!");
        }
    }

    [HorizontalGroup("Player")]
    [Button(ButtonSizes.Large), GUIColor(1f, 0.8f, 0.4f)]
    private void AddGold()
    {
        var player = FindObjectOfType<PlayerController>();
        if (player != null)
        {
            player.Gold += 1000;
            Debug.Log("Added 1000 gold!");
        }
    }

    [HorizontalGroup("Player")]
    [Button(ButtonSizes.Large), GUIColor(0.4f, 0.8f, 1f)]
    private void ResetPosition()
    {
        var player = FindObjectOfType<PlayerController>();
        if (player != null)
        {
            player.transform.position = Vector3.zero;
            Debug.Log("Player reset to origin!");
        }
    }

    [Title("Scene Tools")]
    [Button("Clear All Enemies"), GUIColor(1f, 0.3f, 0.3f)]
    private void ClearEnemies()
    {
        var enemies = FindObjectsOfType<Enemy>();
        foreach (var enemy in enemies)
        {
            DestroyImmediate(enemy.gameObject);
        }
        Debug.Log($"Cleared {enemies.Length} enemies!");
    }

    [Button("Spawn Test Enemies")]
    private void SpawnTestEnemies()
    {
        // Spawn logic...
        Debug.Log("Test enemies spawned!");
    }
}
```

### Pattern 2: Asset Generation

**Problem:** Generate ScriptableObject assets from code.

```csharp
#if UNITY_EDITOR
using UnityEditor;
#endif

public class EnemyGenerator : SerializedMonoBehaviour
{
    [SerializeField] private string _enemyName = "Goblin";
    [SerializeField] private int _baseHealth = 100;
    [SerializeField] private float _baseSpeed = 3f;

    [Button(ButtonSizes.Large), GUIColor(0.4f, 1f, 0.4f)]
    private void GenerateEnemyAsset()
    {
        #if UNITY_EDITOR
        var enemyData = ScriptableObject.CreateInstance<EnemyData>();
        enemyData.Name = _enemyName;
        enemyData.Health = _baseHealth;
        enemyData.Speed = _baseSpeed;

        string path = EditorUtility.SaveFilePanelInProject(
            "Save Enemy Data",
            _enemyName,
            "asset",
            "Save generated enemy data"
        );

        if (!string.IsNullOrEmpty(path))
        {
            AssetDatabase.CreateAsset(enemyData, path);
            AssetDatabase.SaveAssets();
            EditorUtility.FocusProjectWindow();
            Selection.activeObject = enemyData;
            Debug.Log($"Enemy asset created: {path}");
        }
        #endif
    }
}
```

### Pattern 3: Scene Validation

**Problem:** Validate scene setup before testing.

```csharp
public class SceneValidator : SerializedMonoBehaviour
{
    [Button(ButtonSizes.Gigantic, "Validate Scene Setup"), PropertyOrder(-1)]
    [GUIColor(0.4f, 0.8f, 1f)]
    private void ValidateScene()
    {
        var errors = new List<string>();

        // Check for required managers
        if (FindObjectOfType<GameManager>() == null)
            errors.Add("Missing GameManager in scene!");

        if (FindObjectOfType<AudioManager>() == null)
            errors.Add("Missing AudioManager in scene!");

        // Check for player spawn point
        var spawnPoint = GameObject.FindGameObjectWithTag("SpawnPoint");
        if (spawnPoint == null)
            errors.Add("No GameObject with tag 'SpawnPoint' found!");

        // Check for main camera
        if (Camera.main == null)
            errors.Add("No main camera found!");

        // Report results
        if (errors.Count == 0)
        {
            Debug.Log("✓ Scene validation passed! All required objects found.");
        }
        else
        {
            Debug.LogError($"✗ Scene validation failed with {errors.Count} error(s):");
            foreach (var error in errors)
            {
                Debug.LogError($"  - {error}");
            }
        }
    }
}
```

---

## Validation Patterns

### Pattern 1: Prefab Reference Validator

**Problem:** Ensure prefabs have required components.

```csharp
public class EnemySpawner : SerializedMonoBehaviour
{
    [Required]
    [AssetsOnly]
    [ValidateInput(nameof(ValidateEnemyPrefab), "Prefab must have Enemy component!")]
    [SerializeField]
    private GameObject _enemyPrefab;

    [Required]
    [SceneObjectsOnly]
    [SerializeField]
    private Transform _spawnPoint;

    private bool ValidateEnemyPrefab(GameObject prefab)
    {
        if (prefab == null) return true;  // [Required] handles null
        return prefab.GetComponent<Enemy>() != null;
    }
}
```

### Pattern 2: Range Validator

**Problem:** Ensure min/max values are properly ordered.

```csharp
public class DamageDealer : SerializedMonoBehaviour
{
    [HorizontalGroup("Damage")]
    [MinValue(0)]
    [SerializeField]
    private int _minDamage = 10;

    [HorizontalGroup("Damage")]
    [MinValue(0)]
    [ValidateInput(nameof(ValidateMaxDamage), "Max must be >= Min!")]
    [SerializeField]
    private int _maxDamage = 20;

    [InfoBox("$" + nameof(GetDamageInfo))]
    [Button("Deal Random Damage")]
    private void DealDamage()
    {
        int damage = Random.Range(_minDamage, _maxDamage + 1);
        Debug.Log($"Dealt {damage} damage!");
    }

    private bool ValidateMaxDamage(int max)
    {
        return max >= _minDamage;
    }

    private string GetDamageInfo()
    {
        return $"Will deal between {_minDamage} and {_maxDamage} damage.";
    }
}
```

### Pattern 3: Collection Integrity Validator

**Problem:** Ensure lists/dictionaries have valid data.

```csharp
public class QuestManager : SerializedMonoBehaviour
{
    [System.Serializable]
    public class Quest
    {
        [Required]
        public string QuestID;

        [Required, TextArea(2, 4)]
        public string Description;

        [MinValue(0)]
        public int RewardGold;
    }

    [ValidateInput(nameof(ValidateQuests), "Duplicate quest IDs or invalid data detected!")]
    [TableList(ShowIndexLabels = true)]
    [OdinSerialize]
    private List<Quest> _quests = new();

    private bool ValidateQuests(List<Quest> quests)
    {
        // Check for duplicates
        var ids = quests.Where(q => q != null).Select(q => q.QuestID).ToList();
        if (ids.Count != ids.Distinct().Count())
            return false;

        // Check for empty IDs
        if (quests.Any(q => q != null && string.IsNullOrWhiteSpace(q.QuestID)))
            return false;

        return true;
    }

    [Button("Find Duplicate Quest IDs")]
    private void FindDuplicates()
    {
        var ids = _quests.Where(q => q != null).Select(q => q.QuestID).ToList();
        var duplicates = ids.GroupBy(id => id).Where(g => g.Count() > 1).Select(g => g.Key).ToList();

        if (duplicates.Count > 0)
        {
            Debug.LogError($"Duplicate quest IDs: {string.Join(", ", duplicates)}");
        }
        else
        {
            Debug.Log("✓ No duplicate quest IDs found!");
        }
    }
}
```

---

## Editor Workflow Patterns

### Pattern 1: Batch Operations

**Problem:** Modify multiple objects at once.

```csharp
#if UNITY_EDITOR
using UnityEditor;
#endif

public class BatchProcessor : SerializedMonoBehaviour
{
    [SerializeField]
    private List<GameObject> _targets = new();

    [Title("Batch Operations")]
    [HorizontalGroup("Batch")]
    [Button("Set Layer")]
    private void SetLayerForAll()
    {
        #if UNITY_EDITOR
        int layer = EditorUtility.DisplayDialogComplex(
            "Set Layer",
            "Choose layer to set for all targets",
            "Default",
            "UI",
            "Cancel"
        );

        if (layer == 2) return;  // Cancel

        string layerName = layer == 0 ? "Default" : "UI";
        int layerIndex = LayerMask.NameToLayer(layerName);

        foreach (var target in _targets)
        {
            if (target != null)
            {
                Undo.RecordObject(target, "Set Layer");
                target.layer = layerIndex;
            }
        }

        Debug.Log($"Set {_targets.Count} objects to layer '{layerName}'");
        #endif
    }

    [HorizontalGroup("Batch")]
    [Button("Set Tag")]
    private void SetTagForAll()
    {
        #if UNITY_EDITOR
        // Similar logic for tags...
        #endif
    }

    [Button("Enable All")]
    private void EnableAll()
    {
        foreach (var target in _targets)
        {
            if (target != null)
            {
                #if UNITY_EDITOR
                Undo.RecordObject(target, "Enable GameObject");
                #endif
                target.SetActive(true);
            }
        }
    }
}
```

### Pattern 2: Prefab Variant Generator

**Problem:** Create multiple prefab variants with different settings.

```csharp
public class PrefabVariantGenerator : SerializedMonoBehaviour
{
    [Required, AssetsOnly]
    [SerializeField] private GameObject _basePrefab;

    [SerializeField] private List<string> _variantNames = new() { "Red", "Blue", "Green" };

    [SerializeField] private List<Material> _variantMaterials = new();

    [Button(ButtonSizes.Large, "Generate Prefab Variants")]
    private void GeneratePrefabVariants()
    {
        #if UNITY_EDITOR
        if (_basePrefab == null)
        {
            Debug.LogError("Base prefab not assigned!");
            return;
        }

        string basePath = AssetDatabase.GetAssetPath(_basePrefab);
        string directory = System.IO.Path.GetDirectoryName(basePath);

        for (int i = 0; i < _variantNames.Count && i < _variantMaterials.Count; i++)
        {
            string variantPath = $"{directory}/{_basePrefab.name}_{_variantNames[i]}.prefab";
            var variant = (GameObject)PrefabUtility.InstantiatePrefab(_basePrefab);

            // Apply material
            var renderer = variant.GetComponent<Renderer>();
            if (renderer != null)
            {
                renderer.sharedMaterial = _variantMaterials[i];
            }

            // Save as prefab
            PrefabUtility.SaveAsPrefabAsset(variant, variantPath);
            DestroyImmediate(variant);

            Debug.Log($"Created variant: {variantPath}");
        }

        AssetDatabase.SaveAssets();
        AssetDatabase.Refresh();
        #endif
    }
}
```

---

## UI/UX Patterns

### Pattern 1: Organized Inspector with Tabs

**Problem:** Too many fields cluttering the Inspector.

```csharp
public class ComplexCharacter : SerializedMonoBehaviour
{
    [TabGroup("Stats")]
    [MinValue(0)] public int Health = 100;

    [TabGroup("Stats")]
    [MinValue(0)] public int Mana = 50;

    [TabGroup("Stats")]
    [Range(0, 10)] public float Speed = 5f;

    [TabGroup("Combat")]
    [MinValue(0)] public int AttackDamage = 10;

    [TabGroup("Combat")]
    [Range(0, 1)] public float CritChance = 0.1f;

    [TabGroup("Combat")]
    [Required, AssetsOnly] public GameObject AttackEffect;

    [TabGroup("Visuals")]
    [Required] public Renderer CharacterRenderer;

    [TabGroup("Visuals")]
    [InlineEditor] public Material CharacterMaterial;

    [TabGroup("Audio")]
    public AudioClip AttackSound;

    [TabGroup("Audio")]
    public AudioClip HurtSound;

    [TabGroup("Audio")]
    [Range(0, 1)] public float SoundVolume = 1f;
}
```

### Pattern 2: Conditional Complexity

**Problem:** Advanced settings clutter simple workflows.

```csharp
public class FlexibleSpawner : SerializedMonoBehaviour
{
    [ToggleGroup("_enabled", "Enable Spawner")]
    [SerializeField] private bool _enabled = true;

    [ToggleGroup("_enabled")]
    [Required, AssetsOnly]
    [SerializeField] private GameObject _prefab;

    [ToggleGroup("_enabled")]
    [MinValue(0.1f)]
    [SerializeField] private float _spawnInterval = 1f;

    [ToggleGroup("_enabled")]
    [SerializeField] private bool _useAdvancedSettings;

    [ToggleGroup("_enabled")]
    [ShowIf(nameof(_useAdvancedSettings))]
    [MinValue(1)]
    [SerializeField] private int _maxSpawns = 10;

    [ToggleGroup("_enabled")]
    [ShowIf(nameof(_useAdvancedSettings))]
    [SerializeField] private AnimationCurve _spawnRateCurve = AnimationCurve.Linear(0, 1, 1, 1);
}
```

---

## Architecture Patterns

### Pattern 1: ScriptableObject Configuration System

**Problem:** Game configuration scattered across scenes.

```csharp
[CreateAssetMenu(fileName = "GameConfig", menuName = "Game/Game Configuration")]
public class GameConfig : SerializedScriptableObject
{
    [TabGroup("Player")]
    [DictionaryDrawerSettings(KeyLabel = "Stat Name", ValueLabel = "Base Value")]
    public Dictionary<string, float> PlayerBaseStats = new()
    {
        { "Health", 100f },
        { "Speed", 5f },
        { "JumpHeight", 2f }
    };

    [TabGroup("Economy")]
    [DictionaryDrawerSettings(KeyLabel = "Currency", ValueLabel = "Starting Amount")]
    public Dictionary<string, int> StartingCurrency = new()
    {
        { "Gold", 100 },
        { "Gems", 0 }
    };

    [TabGroup("Gameplay")]
    public int LivesPerGame = 3;

    [TabGroup("Gameplay")]
    public float RespawnDelay = 2f;

    [Button("Apply to Current Scene")]
    private void ApplyConfiguration()
    {
        var gameManager = FindObjectOfType<GameManager>();
        if (gameManager != null)
        {
            gameManager.LoadConfig(this);
            Debug.Log("Configuration applied!");
        }
    }
}
```

### Pattern 2: Event System with Inspector Debugging

**Problem:** Hard to debug event subscriptions.

```csharp
public class GameEventSystem : SerializedMonoBehaviour
{
    public delegate void GameEvent(string eventName, object data);
    private Dictionary<string, GameEvent> _events = new();

    #if UNITY_EDITOR
    [ShowInInspector, ReadOnly]
    [DictionaryDrawerSettings(KeyLabel = "Event Name", ValueLabel = "Subscriber Count")]
    private Dictionary<string, int> DebugEventCounts
    {
        get
        {
            var counts = new Dictionary<string, int>();
            foreach (var kvp in _events)
            {
                counts[kvp.Key] = kvp.Value?.GetInvocationList().Length ?? 0;
            }
            return counts;
        }
    }

    [Button("Clear All Events"), GUIColor(1, 0.3f, 0.3f)]
    private void ClearAllEvents()
    {
        _events.Clear();
        Debug.Log("All events cleared!");
    }
    #endif

    public void Subscribe(string eventName, GameEvent callback)
    {
        if (!_events.ContainsKey(eventName))
        {
            _events[eventName] = null;
        }
        _events[eventName] += callback;
    }

    public void Trigger(string eventName, object data = null)
    {
        if (_events.TryGetValue(eventName, out var eventDelegate))
        {
            eventDelegate?.Invoke(eventName, data);
        }
    }
}
```

---

**Key Takeaways:**

- Dictionaries excel at key-value data (items, configs, localization)
- Buttons streamline dev tools and asset generation
- Validation ensures data integrity before runtime
- Editor workflows automate repetitive tasks
- Good UX patterns (tabs, groups, conditional visibility) keep complex Inspectors manageable
- ScriptableObjects + Odin = powerful, designer-friendly configuration systems
