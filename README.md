# Unity Tips & Tools - Complete Guide

> **Everything you need to build professional Unity games.** A comprehensive collection of best
> practices, tools, and documentation to accelerate your Unity development from beginner to expert.

---

## 🎯 What Is This?

This repository contains:

- **✅ Best practices guides** for Unity development (lifecycle methods, physics, serialization,
  etc.)
- **✅ In-depth documentation** for essential Unity tools and plugins
- **✅ Beginner-friendly explanations** of complex topics
- **✅ Real-world examples** from production games
- **✅ Quick reference cards** for common patterns

**Perfect for:** Unity developers of all skill levels who want to write better code, avoid common
pitfalls, and ship games faster.

---

## 🚀 Quick Start (5 Minutes)

### New to Unity?

Start here in order:

1. **[Best Practices](./docs/best-practices/README.md)** - Foundation concepts (lifecycle, null
   checks, components)
2. **[Unity Helpers](./docs/unity-helpers/README.md)** - Essential utilities to eliminate
   boilerplate
3. **[Hot Reload](./docs/hot-reload/README.md)** - Edit code without recompiling (save 2-3
   hours/day!)

### Building a 2D Game?

You need these tools:

1. **[Unity Helpers](./docs/unity-helpers/README.md)** - Component auto-wiring, object pooling, plus
   2D editor tools
2. **[Animancer](./docs/animancer/README.md)** - Code-driven animation control
3. **[Feel](./docs/feel/README.md)** - Game feel and juice (screen shake, particles, etc.)
4. **[PrimeTween](./docs/primetween/README.md)** - Zero-allocation animations and tweens

### Optimizing Performance?

Essential performance tools:

1. **[Graphy](./docs/graphy/README.md)** - Real-time FPS/memory monitor (FREE!)
2. **[Assembly Definitions](./docs/assembly-definitions/README.md)** - 10-100x faster compile times
3. **[Better Build Info PRO](./docs/better-build-info/README.md)** - Build size analysis
4. **[Object Pooling Best Practices](./docs/best-practices/09-object-pooling.md)** - Eliminate GC
   spikes

### Working on a Large Project?

Critical organization tools:

1. **[Assembly Definitions](./docs/assembly-definitions/README.md)** - Manage compile times and
   dependencies
2. **[Odin Inspector](./docs/odin/README.md)** - Serialize dictionaries, powerful Inspector tools
3. **[Asset Usage Finder](./docs/asset-usage-finder/README.md)** - Find where assets are used
4. **[DxMessaging](./docs/dxmessaging/README.md)** - Type-safe, zero-leak messaging

---

## 📚 Complete Tool Catalog

### Foundation & Best Practices

#### [Unity Best Practices](./docs/best-practices/README.md) ⭐ **START HERE**

**What it solves:** Common Unity mistakes that cause bugs, performance issues, and technical debt.

**Why it exists:** 80% of Unity bugs come from the same 10 mistakes. Learn them once, avoid them
forever.

**Key topics:**

- Lifecycle methods (Awake vs Start vs Update)
- Null checking in Unity (why `== null` works but `is null` doesn't)
- Component caching for performance
- Serialization patterns
- Coroutines, physics, memory management

**How to use:** Read in order. Each topic builds on previous ones.

**Time investment:** 2-3 hours reading | **Saves:** Weeks of debugging

---

### Core Utilities

#### [Unity Helpers](./docs/unity-helpers/README.md) 🔧 **HIGHLY RECOMMENDED**

**What it solves:** Eliminates repetitive boilerplate code that you write in every Unity project.

**Why it exists:** Stop writing the same component caching, serialization, and pooling code for
every project.

**Key features:**

- **Automatic Component Wiring** - `[SelfComponent]` instead of 10 lines of GetComponent boilerplate
- **Unity-Aware Serialization** - Serialize Vector3, Color, GameObjects seamlessly
- **Zero-Allocation Pooling** - Professional object pooling with zero GC
- **Data-Driven Effects System** - Buffs/debuffs as ScriptableObjects
- **🎮 2D Editor Tools** - Sprite automation, animation generation, and batch processing via Unity
  menus

**2D Game Development Tools:**

Unity Helpers provides powerful editor tools accessible through Unity's menu system:

- **Animation Creator** - `Tools → Wallstop Studios → Unity Helpers → Animation Creator` - Create
  animations from sprite sequences
- **Sprite Sheet Animation Creator** -
  `Tools → Wallstop Studios → Unity Helpers → Sprite Sheet Animation Creator` - Generate animations
  from sprite sheets
- **Sprite Cropper** - `Tools → Wallstop Studios → Unity Helpers → Sprite Cropper` - Remove
  transparent pixels from sprites
- **Sprite Atlas Generator** - `Tools → Wallstop Studios → Unity Helpers → Sprite Atlas Generator` -
  Generate optimized sprite atlases
- **Sprite Settings Applier** - `Tools → Wallstop Studios → Unity Helpers → Sprite Settings Applier`
  - Batch adjust sprite import settings
- **Prefab Checker** - `Tools → Wallstop Studios → Unity Helpers → Prefab Checker` - Validate
  prefabs have required components

These are editor GUI tools accessed through Unity's menu system (under
`Tools → Wallstop Studios → Unity Helpers`), similar to Unity's built-in Animation window or Sprite
Packer.

**How to use:** Install via Package Manager, use the provided attributes and utilities in your
scripts.

**Time saved:** 30-40% of development time on infrastructure

**Installation:** [Quick Start Guide](./docs/unity-helpers/README.md#quick-start)

---

#### [Hot Reload](./docs/hot-reload/README.md) ⚡ **GAME CHANGER**

**What it solves:** Waiting 5-60+ seconds every time you change code to see the result.

**Why it exists:** Unity's compile-wait-test loop kills productivity. Hot Reload lets you edit code
and see changes in ~100ms while the game keeps running.

**Key features:**

- Edit code without stopping play mode
- Changes apply in milliseconds
- Game state preserved
- Works in Editor, Play Mode, and on-device

**Real-world impact:**

- **Before:** Change code → Wait 30s → Test → Repeat (8-75 seconds per iteration)
- **After:** Change code → Wait 0.1s → Test → Repeat (<1 second per iteration)
- **Time saved:** 2-3 hours per day for active development

**How to use:** Install, press Alt+Shift+H to open window, start coding. Changes apply automatically
on save.

**Cost:** Free tier available | Indie ~$10-15/month | **ROI:** Pays for itself in 1-2 days

**Limitations:** Can't add new methods/fields (requires recompile button click), but method body
changes work instantly.

---

#### [Odin Inspector & Serializer](./docs/odin/README.md) 🎨 **DESIGNER FAVORITE**

**What it solves:** Unity can't serialize dictionaries. Unity's Inspector is inflexible. You can't
run code from Inspector.

**Why it exists:** Unity's serialization and Inspector were designed in 2005. Odin brings them into
the modern era.

**Key features:**

- **Serialize dictionaries** - `Dictionary<string, GameObject>` just works
- **Inspector buttons** - `[Button]` to run code without entering play mode
- **Validation** - `[Required]`, `[ValidateInput]` catch errors before runtime
- **Conditional visibility** - `[ShowIf]`, `[HideIf]` for context-sensitive UI
- **Organization** - `[TabGroup]`, `[FoldoutGroup]` for complex components

```csharp
// Unity's limitation: Can't serialize dictionaries
Dictionary<string, int> items; // ❌ Doesn't work in vanilla Unity

// Odin's solution: Just works!
[SerializeField] private Dictionary<string, int> items = new(); // ✅

// Run code from Inspector
[Button("Generate Level")]
private void GenerateLevel() { /* Runs when clicked! */ }

// Smart validation
[Required("Must assign!")]
[AssetsOnly] // Only prefabs, not scene objects
private GameObject enemyPrefab;
```

**How to use:** Change `MonoBehaviour` to `SerializedMonoBehaviour`, use attributes.

**Cost:** ~$55 (one-time) | **Worth it if:** You need dictionaries or better Inspector UX

---

### Animation & Visual Polish

#### [Animancer Pro 8](./docs/animancer/README.md) 🎬 **CODE-FIRST ANIMATION**

**What it solves:** Unity's Animator Controller is a visual spaghetti mess that's hard to debug and
version control.

**Why it exists:** For programmers who prefer `animancer.Play(walkClip)` over visual state machine
graphs.

**Key features:**

- **Direct code control** - `animancer.Play(clip)` instead of setting bool parameters
- **No state machines** - Your code IS the state machine
- **Easy debugging** - Breakpoints and stack traces work
- **Clean diffs** - C# files, not binary assets
- **Seamless directional switching** - Preserve normalized time across animations

```csharp
// Traditional Animator Controller
animator.SetBool("IsWalking", true);
animator.SetFloat("Speed", 5f);
animator.SetTrigger("Attack");
// Hope the state machine is configured correctly...

// Animancer - Direct control
animancer.Play(walkClip);
animancer.Play(attackClip).Speed = 2f; // Double speed
```

**Perfect for:** Programmers, complex character controllers, 2D games with many animations

**How to use:** Add `AnimancerComponent`, reference clips, call `Play()`.

**Cost:** ~$50-100 | **Worth it if:** You have 10+ animations or hate visual state machines

---

#### [Feel](./docs/feel/README.md) ✨ **GAME FEEL LIBRARY**

**What it solves:** Adding screen shake, particles, sound effects, and visual polish takes 100+
lines of code per effect.

**Why it exists:** Game feel is what makes games satisfying. Feel makes it accessible to everyone,
not just graphics programmers.

**Key features:**

- **150+ ready-to-use feedbacks** - Screen shake, camera zoom, particle bursts, etc.
- **Designer-friendly** - Configure everything in Inspector
- **Composable** - Stack multiple feedbacks for complex effects
- **Zero code needed** - `PlayFeedbacks()` is the only code you write

```csharp
// Without Feel: 100+ lines for a satisfying sword slash
// - Screen shake code
// - Particle instantiation
// - Camera zoom animation
// - Slow-motion code
// - Sound effect triggering
// - Post-processing burst

// With Feel: Add MMFeedbacks component, configure in Inspector, done!
public MMFeedbacks swordSlashFeedback;
void Attack() { swordSlashFeedback.PlayFeedbacks(); }
```

**Perfect for:** Adding juice to your game without coding VFX systems

**How to use:** Add `MMFeedbacks` component, click "Add Feedback", configure, call
`PlayFeedbacks()`.

**Cost:** €46 | Free version (MMFeedbacks) with ~80 feedbacks available

---

#### [PrimeTween](./docs/primetween/README.md) 🎯 **ZERO-ALLOCATION ANIMATIONS**

**What it solves:** DOTween allocates memory causing garbage collection stutters. LeanTween is slow.

**Why it exists:** Smooth animations shouldn't cause frame drops. PrimeTween is **2.6x faster** and
allocates **0 bytes**.

**Key features:**

- **Zero garbage collection** - Literally 0 allocations
- **2.6x faster** than DOTween
- **Inspector-friendly** - Serialize `TweenSettings` for designer control
- **Simple API** - One method per animation type

```csharp
// Animate anything in one line
Tween.Position(transform, targetPos, duration: 1f);
Tween.Scale(transform, 1.5f, 0.5f, ease: Ease.OutBack);

// Chain animations
Sequence.Create()
    .Chain(Tween.Position(transform, Vector3.up * 5, 1f))
    .Chain(Tween.Scale(transform, 2f, 0.5f));

// Performance: 0 bytes allocated vs DOTween's 734-2846 bytes per tween
```

**Perfect for:** UI animations, gameplay tweens, anything that moves/scales/rotates

**How to use:** Call `Tween.*(...)` methods. That's it.

**Cost:** FREE (open source)

---

### Development Workflow

#### CSharpier | Automatic Code Formatting | FREE

**Website:** [Csharpier](https://csharpier.com/)

**What it solves:** Inconsistent code formatting, merge conflicts from whitespace changes, and time
wasted on style debates.

**Why it exists:** Stop thinking about formatting. Type code however you want, hit save, and
CSharpier instantly makes it beautiful and consistent. No configuration, no debates, just pretty
code.

**The magic:** CSharpier is like having an automatic car wash for your code. Drive in messy, drive
out sparkling clean. Write your code any way you want - sloppy indentation, inconsistent spacing,
whatever - and when you save, it's instantly formatted perfectly. Every single time.

**Key benefits:**

- **Zero mental overhead** - Never think about formatting again
- **Automatic everywhere** - Format-on-save in editor, pre-commit hooks, CI/CD
- **No merge conflicts** - Everyone's code looks identical
- **No style debates** - One deterministic format, no options to argue about
- **Works with your editor** - Plugins for VS Code, Rider, Visual Studio

```csharp
// You type this mess:
public class Player:MonoBehaviour{
private int health=100;public void TakeDamage(int amount){health-=amount;
if(health<=0)Die();}}

// CSharpier auto-formats to:
public class Player : MonoBehaviour
{
    private int health = 100;

    public void TakeDamage(int amount)
    {
        health -= amount;
        if (health <= 0)
            Die();
    }
}
```

**How to set up (5 minutes):**

1. **Install as .NET tool** (project-wide consistency):

   ```bash
   # Create .config directory if it doesn't exist
   mkdir -p .config

   # Create dotnet-tools.json
   cat > .config/dotnet-tools.json << 'EOF'
   {
     "version": 1,
     "isRoot": true,
     "tools": {
       "CSharpier": {
         "version": "1.1.2",
         "commands": ["csharpier"]
       }
     }
   }
   EOF

   # Install the tool
   dotnet tool restore
   ```

1. **Add pre-commit hook** (auto-format before commits):

   ```bash
   # Install pre-commit framework (if not installed)
   pip install pre-commit

   # Create .pre-commit-config.yaml
   cat > .pre-commit-config.yaml << 'EOF'
   repos:
     - repo: local
       hooks:
         - id: dotnet-tool-restore
           name: Install .NET tools
           entry: dotnet tool restore
           language: system
           always_run: true
           pass_filenames: false
           stages: [pre-commit]
         - id: csharpier
           name: Run CSharpier on C# files
           entry: dotnet csharpier
           language: system
           types: [c#]
   EOF

   # Install the hooks
   pre-commit install
   ```

1. **Add to CI/CD** (enforce formatting in builds):

   ```yaml
   # In your GitHub Actions workflow:
   - name: Check code formatting
     run: |
       dotnet tool restore
       dotnet csharpier --check .
   ```

1. **Editor plugin** (format-on-save):
   - **VS Code:** Install "CSharpier" extension → Enable format-on-save
   - **Rider:** Install "CSharpier" plugin → Enable format-on-save in settings
   - **Visual Studio:** Install "CSharpier" extension → Enable format-on-save

**Cost:** FREE (MIT license)

---

#### EditorConfig | Style Enforcement | FREE

**Website:** [Editorconfig](https://editorconfig.org/)

**What it solves:** Inconsistent naming (camelCase vs PascalCase), style violations, and "which
convention should we use?" debates.

**Why it exists:** CSharpier formats your code's structure (braces, spacing), but EditorConfig
enforces naming conventions and style rules. It's your team's style guide, automatically enforced by
every IDE.

**Key benefits:**

- **Enforced naming conventions** - Interfaces start with `I`, private fields are `camelCase`, etc.
- **Always use braces** - Enforce `if (x) { }` instead of `if (x) statement;`
- **IDE integration** - Works in VS Code, Rider, Visual Studio automatically
- **Prevents bugs** - Deterministic rules (always do X) are safer than flexible ones (sometimes do
  X)
- **Team consistency** - Everyone's code follows the same rules automatically

```csharp
// Without EditorConfig: Inconsistent naming causes confusion
public interface player { }  // ❌ Should be IPlayer
private int HealthValue;      // ❌ Should be healthValue (camelCase)
public event Action click;    // ❌ Should be OnClick

// With EditorConfig: IDE shows warnings/errors for violations
public interface IPlayer { }  // ✅ Correct!
private int healthValue;      // ✅ Correct!
public event Action OnClick;  // ✅ Correct!

// Enforces braces for safety:
if (health <= 0)              // ❌ Warning: Missing braces
    Die();

if (health <= 0)              // ✅ Correct!
{
    Die();
}
```

**Why deterministic rules matter:**

```csharp
// "Sometimes use braces" rule (BAD):
if (health <= 0) Die();  // Works fine

// Later, someone adds logging:
if (health <= 0)
    Debug.Log("Player died");
    Die();  // 🐛 BUG! This ALWAYS runs, not just when health <= 0!

// "Always use braces" rule (GOOD):
if (health <= 0)
{
    Die();
}

// Adding logging is safe:
if (health <= 0)
{
    Debug.Log("Player died");
    Die();  // ✅ Correct! Always runs when health <= 0
}
```

**How to set up (2 minutes):**

1. **Create `.editorconfig` at project root:**

   ```ini
   # Example Unity .editorconfig (simplified for clarity)

   # Top-most EditorConfig file
   root = true

   # All files
   [*]
   charset = utf-8-bom
   indent_style = space
   indent_size = 4
   trim_trailing_whitespace = true
   insert_final_newline = true

   # C# files
   [*.cs]

   # Always use braces for control flow (CRITICAL!)
   csharp_prefer_braces = true:warning

   # Naming conventions
   # Interfaces: IPlayer, IEnemy
   dotnet_naming_rule.interfaces_rule.severity = warning
   dotnet_naming_rule.interfaces_rule.symbols = interface
   dotnet_naming_rule.interfaces_rule.style = begins_with_i
   dotnet_naming_symbols.interface.applicable_kinds = interface
   dotnet_naming_style.begins_with_i.capitalization = pascal_case
   dotnet_naming_style.begins_with_i.required_prefix = I

   # Events: OnClick, OnPlayerDied
   dotnet_naming_rule.events_rule.severity = warning
   dotnet_naming_rule.events_rule.symbols = event
   dotnet_naming_rule.events_rule.style = begins_with_on
   dotnet_naming_symbols.event.applicable_kinds = event
   dotnet_naming_style.begins_with_on.capitalization = pascal_case
   dotnet_naming_style.begins_with_on.required_prefix = On

   # Private fields: health, playerSpeed (camelCase)
   dotnet_naming_rule.private_fields_rule.severity = warning
   dotnet_naming_rule.private_fields_rule.symbols = private_fields
   dotnet_naming_rule.private_fields_rule.style = camel_case
   dotnet_naming_symbols.private_fields.applicable_kinds = field
   dotnet_naming_symbols.private_fields.applicable_accessibilities = private
   dotnet_naming_style.camel_case.capitalization = camel_case

   # Public fields: Health, PlayerSpeed (PascalCase)
   dotnet_naming_rule.public_fields_rule.severity = warning
   dotnet_naming_rule.public_fields_rule.symbols = public_fields
   dotnet_naming_rule.public_fields_rule.style = pascal_case
   dotnet_naming_symbols.public_fields.applicable_kinds = field
   dotnet_naming_symbols.public_fields.applicable_accessibilities = public
   dotnet_naming_style.pascal_case.capitalization = pascal_case
   ```

1. **For a comprehensive production-ready config**, search for "Unity .editorconfig" examples with
   160+ lines of rules covering all edge cases

**Common Unity naming conventions to enforce:**

- ✅ Interfaces must start with `I` (IPlayer, IEnemy)
- ✅ Events must start with `On` (OnClick, OnPlayerDied)
- ✅ Type parameters must start with `T` (TComponent, TValue)
- ✅ Private fields use camelCase (health, playerSpeed)
- ✅ Public fields use PascalCase (Health, PlayerSpeed)
- ✅ Always use braces for `if`, `for`, `while`, etc.

**How CSharpier and EditorConfig work together:**

1. **CSharpier** (Format Structure):

   - Handles spacing, indentation, line breaks
   - "How does the code look?"
   - Runs: On save, pre-commit, CI/CD

2. **EditorConfig** (Enforce Rules):
   - Handles naming, conventions, style rules
   - "What are the code's rules?"
   - Runs: Continuously in IDE (live warnings/errors)

Together, they mean: **Write code however you want → Save → Perfect, consistent, rule-compliant code
automatically**

**Cost:** FREE (built into most IDEs)

---

**⚠️ CRITICAL UNITY GOTCHA: Null-Conditional Operators on Unity Objects**

Unity's null handling is broken with C#'s null-conditional (`?.`) and null-coalescing (`??`)
operators. This causes **silent bugs** that are hard to track down.

**The Problem:**

Unity overrides `== null` to detect destroyed objects, but C# operators like `?.` and `??` use the
built-in C# null check, which **doesn't know about destroyed Unity objects**.

```csharp
// ❌ DANGEROUS: Null-conditional operator on Unity objects
GameObject player = destroyedGameObject; // Destroyed but not null!
int? health = player?.GetComponent<Health>()?.currentHealth;
// 🐛 BUG! This throws NullReferenceException instead of returning null!
// Unity thinks it's destroyed, but C# thinks it's not null

// ❌ DANGEROUS: Null-coalescing operator
Transform target = destroyedTransform ?? fallbackTransform;
// 🐛 BUG! Uses destroyedTransform instead of fallback!
// C# doesn't see it as null even though it's destroyed

// ✅ SAFE: Explicit Unity null check
if (player != null) // Unity's overridden == operator
{
    Health health = player.GetComponent<Health>();
    if (health != null)
    {
        int currentHealth = health.currentHealth;
    }
}

// ✅ SAFE: Null-coalescing with explicit check
Transform target = (destroyedTransform != null) ? destroyedTransform : fallbackTransform;
```

**Real-world example of the bug:**

```csharp
public class PlayerController : MonoBehaviour
{
    private GameObject target;

    void Update()
    {
        // Enemy gets destroyed during gameplay
        // target is destroyed but not "null" in C#

        // ❌ DANGEROUS: Looks safe, but throws NullReferenceException!
        Vector3? position = target?.transform.position;

        // ❌ DANGEROUS: Uses destroyed object instead of fallback!
        Transform finalTarget = target?.transform ?? defaultTarget;

        // ✅ SAFE: Unity's null check works correctly
        if (target != null)
        {
            Vector3 position = target.transform.position;
        }

        // ✅ SAFE: Explicit check before coalescing
        Transform finalTarget = (target != null) ? target.transform : defaultTarget;
    }
}
```

**Why this happens:**

- Unity objects are C# wrappers around native C++ objects
- When `Destroy()` is called, the C++ object is destroyed, but the C# wrapper still exists
- Unity overrides `==` and `!=` to check if the native object exists
- C#'s `?.` and `??` operators **don't use overloaded operators**, they use the built-in null check
- Result: Destroyed Unity objects fail the built-in null check → crashes and bugs

**The Rule: NEVER use `?.` or `??` with Unity object types**

**Unity object types include:**

- `GameObject`, `Transform`, `Component`
- Any class inheriting from `MonoBehaviour`
- Any class inheriting from `ScriptableObject`
- Any class inheriting from `UnityEngine.Object`

**Safe to use `?.` and `??` with:**

- Plain C# classes (`class Foo { }`)
- Structs (`Vector3`, `Quaternion`, your own structs)
- Interfaces (but be careful if they're implemented by Unity objects!)
- C# primitives (`int?`, `string`, etc.)

**EditorConfig can help prevent this:**

```ini
# Add to your .editorconfig to warn about this pattern
[*.cs]
# Unfortunately, there's no built-in rule for this specific issue
# Best practice: Code review + team education
# Consider using a custom analyzer or Roslyn rule
```

**Bottom line:** When working with Unity objects (GameObject, Component, MonoBehaviour, etc.),
**always use explicit `!= null` checks**. Never use `?.` or `??` operators. This is one of Unity's
most dangerous quirks.

---

#### [Assembly Definitions](./docs/assembly-definitions/README.md) ⚡ **COMPILE TIME SAVER**

**What it solves:** Changing one script recompiles your entire project (30-120+ seconds).

**Why it exists:** Unity's default setup compiles everything as one giant assembly. Assembly
Definitions split your code so only changed parts recompile.

**Real-world impact:**

- **Small projects (500 scripts):** 5-10s → 2-3s (2-3x faster)
- **Medium projects (2000 scripts):** 15-30s → 2-5s (5-10x faster)
- **Large projects (8000+ scripts):** 60-120s → 3-8s (10-20x faster)

**Key benefits:**

- **10-100x faster** incremental compiles
- **Explicit dependencies** - Prevents spaghetti architecture
- **Platform-specific code** - Auto-exclude code from certain platforms

**How to use:** Right-click folder → Create → Assembly Definition. Done!

**When to use:** Projects with 500+ scripts or compile times > 10 seconds

**Cost:** FREE (built into Unity)

---

#### [Unity Input System](./docs/input-system/README.md) 🎮 **MODERN INPUT HANDLING**

**What it solves:** Old Input Manager is hardcoded, doesn't support rebinding, and is a mess for
multi-device support.

**Why it exists:** Modern games need gamepad support, rebindable controls, and multi-device
handling. Old system can't do this.

**Key features:**

- **Event-driven** - Subscribe to actions, don't poll in Update()
- **Device agnostic** - One action works on keyboard, gamepad, touch
- **Runtime rebinding** - Let players customize controls
- **Native multiplayer** - Each player gets their own input instance

```csharp
// Old Input Manager
void Update() {
    if (Input.GetKeyDown(KeyCode.Space)) Jump(); // Hardcoded!
}

// New Input System
void Awake() {
    jumpAction.performed += ctx => Jump(); // Event-driven!
    // Works with keyboard Space, gamepad A, or touch tap
}
```

**Perfect for:** Any game that needs gamepad support, rebindable controls, or multiplayer

**How to use:** Create Input Actions asset, generate C# class, subscribe to events.

**Cost:** FREE (official Unity package)

---

### Performance & Debugging

#### [Graphy](./docs/graphy/README.md) 📊 **PERFORMANCE MONITOR** ⭐ FREE!

**What it solves:** "Is my game running smoothly? When do frame drops happen? Why did it stutter?"

**Why it exists:** You can't optimize what you can't see. Graphy makes performance visible in
real-time.

**Key features:**

- **Real-time FPS/memory/audio graphs** - Always visible overlay
- **Works everywhere** - Editor, builds, mobile devices
- **Zero config** - Add to scene, done
- **FREE and open-source**
- **Unity Awards 2018 Winner** - Best Development Asset

```csharp
// No code needed! Just add to scene:
GameObject → Graphy → Graphy (Complete)

// Or control via code:
GraphyManager.Instance.Enable();

// Optional: React to performance
graphy.FpsMonitor.FpsBelowThreshold += (fps) => {
    Debug.LogWarning($"FPS dropped to {fps}!");
};
```

**Perfect for:** Every Unity project. Seriously, just use it.

**How to use:** Add to scene, play. That's it.

**Cost:** FREE (MIT license)

---

#### [Better Build Info PRO](./docs/better-build-info/README.md) 📦 **BUILD ANALYZER**

**What it solves:** "Why is my build 250MB? What are the largest files? What changed between
builds?"

**Why it exists:** Unity's build log is a text dump. Better Build Info shows visual tree maps and
lets you drill into every asset.

**Key features:**

- **Visual tree map** - See build size at a glance (huge rectangles = huge files)
- **Asset usage tracking** - Click any asset to see where it's used
- **Build comparison** - "What changed between v1.0 and v1.1?"
- **Sprite atlas breakdown** - See which sprites bloat your atlases

**Real-world results:**

- Find and fix 30MB of accidental debug textures in 5 minutes
- Reduce mobile APK from 230MB → 110MB in 3 hours
- Identify which features contribute most to build size

**How to use:** Build project → Window → Better Build Info → Explore

**Cost:** Standard ~$15 | PRO ~$30-40 | **Worth it for:** Mobile/console games with size limits

---

#### [Asset Usage Finder](./docs/asset-usage-finder/README.md) 🔍 **REFERENCE FINDER**

**What it solves:** "Where is this texture used? Can I safely delete this asset?"

**Why it exists:** Unity's built-in tools can't find project-wide references. You'd spend hours
searching manually.

**Key features:**

- **Find references instantly** - Right-click → Find References in Project
- **Works across everything** - Scenes, prefabs, materials, ScriptableObjects
- **Safe deletion** - Know exactly what uses an asset before deleting

```
Problem: Want to delete unused assets
Unity built-in: ❌ Can't tell what uses what
Manual search: ⏱️ 20-60 minutes per asset

Asset Usage Finder: ✅ Right-click → 5 seconds → Complete list
```

**Perfect for:** Cleaning projects, refactoring, build size optimization

**How to use:** Right-click any asset → Find References in Project

**Cost:** FREE version available (Asset Usage Detector) | Paid ~$10-30 (faster, better UI)

---

### Architecture & Messaging

#### [DxMessaging](./docs/dxmessaging/README.md) 📡 **TYPE-SAFE MESSAGING**

**What it solves:** C# events cause memory leaks when you forget to unsubscribe. Direct references
create tight coupling.

**Why it exists:** Game systems need to communicate without creating dependency hell. DxMessaging
provides safe, observable messaging.

**Key features:**

- **Zero memory leaks** - Automatic cleanup when components are destroyed
- **Type-safe** - Compile-time checking of message types
- **Observable** - Inspect message flow in Unity Inspector
- **Three message types** - Targeted, Untargeted, Broadcast

```csharp
// Define a message
[DxTargetedMessage]
[DxAutoConstructor]
public readonly partial struct TakeDamage { public readonly int amount; }

// Listen (auto-cleanup!)
public class Player : MessageAwareComponent {
    protected override void RegisterMessageHandlers() {
        _ = Token.RegisterComponentTargeted<TakeDamage>(this, OnDamage);
    } // Automatically unsubscribes when destroyed!

    void OnDamage(ref TakeDamage msg) => health -= msg.amount;
}

// Send
new TakeDamage(50).EmitComponentTargeted(player);
```

**Perfect for:** Large projects with many interconnected systems

**How to use:** Inherit `MessageAwareComponent`, define message structs, register handlers.

**Cost:** FREE (open source)

---

## 🎯 Quick Decision Guide

### "Which tools do I need for my project?"

#### 🎮 2D Platformer / Action Game

**Essential:**

- [Best Practices](./docs/best-practices/README.md) - Foundation
- [Unity Helpers](./docs/unity-helpers/README.md) - Boilerplate elimination + 2D editor tools
- [CSharpier](#csharpier--automatic-code-formatting--free) - Automatic formatting (FREE!)
- [EditorConfig](#editorconfig--style-enforcement--free) - Enforce naming conventions (FREE!)
- [Animancer](./docs/animancer/README.md) - Character animation control
- [PrimeTween](./docs/primetween/README.md) - UI and gameplay tweens
- [Feel](./docs/feel/README.md) - Game feel and juice
- [Input System](./docs/input-system/README.md) - Gamepad support

**Recommended:**

- [Hot Reload](./docs/hot-reload/README.md) - Save 2-3 hours/day
- [Graphy](./docs/graphy/README.md) - Performance monitoring (FREE!)

**If needed:**

- [Assembly Definitions](./docs/assembly-definitions/README.md) - If project has 500+ scripts

---

#### 📱 Mobile Game

**Essential:**

- [Best Practices](./docs/best-practices/README.md) - Performance critical
- [Unity Helpers](./docs/unity-helpers/README.md) - Object pooling, serialization
- [CSharpier](#csharpier--automatic-code-formatting--free) - Automatic formatting (FREE!)
- [EditorConfig](#editorconfig--style-enforcement--free) - Enforce naming conventions (FREE!)
- [Graphy](./docs/graphy/README.md) - On-device performance testing
- [Better Build Info PRO](./docs/better-build-info/README.md) - Build size optimization
- [PrimeTween](./docs/primetween/README.md) - Zero-allocation animations

**Highly Recommended:**

- [Hot Reload](./docs/hot-reload/README.md) - Test on device faster
- [Assembly Definitions](./docs/assembly-definitions/README.md) - Faster iteration
- [Asset Usage Finder](./docs/asset-usage-finder/README.md) - Clean unused assets

---

#### 🏢 Large Team Project

**Essential:**

- [Best Practices](./docs/best-practices/README.md) - Team standards
- [CSharpier](#csharpier--automatic-code-formatting--free) - Consistent formatting (FREE!)
- [EditorConfig](#editorconfig--style-enforcement--free) - Team style rules (FREE!)
- [Assembly Definitions](./docs/assembly-definitions/README.md) - Manage dependencies
- [Odin Inspector](./docs/odin/README.md) - Designer empowerment
- [DxMessaging](./docs/dxmessaging/README.md) - Decouple systems
- [Input System](./docs/input-system/README.md) - Professional input handling

**Highly Recommended:**

- [Hot Reload](./docs/hot-reload/README.md) - Team-wide productivity
- [Unity Helpers](./docs/unity-helpers/README.md) - Standardized utilities
- [Asset Usage Finder](./docs/asset-usage-finder/README.md) - Manage large asset base
- [Better Build Info PRO](./docs/better-build-info/README.md) - Track build bloat

---

#### 🎓 Learning / Solo Developer

**Start Here:**

- [Best Practices](./docs/best-practices/README.md) - Build solid foundation
- [CSharpier](#csharpier--automatic-code-formatting--free) - Never think about formatting (FREE!)
- [EditorConfig](#editorconfig--style-enforcement--free) - Learn good naming conventions (FREE!)
- [Unity Helpers](./docs/unity-helpers/README.md) - Learn good patterns
- [Graphy](./docs/graphy/README.md) - Understand performance (FREE!)

**Add Gradually:**

- [Hot Reload](./docs/hot-reload/README.md) - When compile times annoy you
- [Animancer](./docs/animancer/README.md) - When Animator Controllers frustrate you
- [Feel](./docs/feel/README.md) - When you want your game to feel better

**Skip for Now:**

- Assembly Definitions - Until you have 500+ scripts
- Odin - Until you need dictionaries or complex data
- DxMessaging - Until you have 10+ interconnected systems

---

## 📖 Learning Paths

### Beginner Path (10-15 hours total)

**Week 1: Foundation**

1. [Best Practices - Lifecycle Methods](./docs/best-practices/01-lifecycle-methods.md) (15 min)
2. [Best Practices - Null Checks](./docs/best-practices/02-null-checks.md) (10 min)
3. [Best Practices - Component Access](./docs/best-practices/03-component-access.md) (15 min)
4. **Practice:** Build simple character controller

**Week 2: Core Tools**

1. [Unity Helpers - Quick Start](./docs/unity-helpers/README.md#quick-start) (30 min)
2. [PrimeTween - Getting Started](./docs/primetween/README.md) (30 min)
3. [Graphy - Setup](./docs/graphy/README.md) (5 min)
4. **Practice:** Add health system with animations

**Week 3: Advanced Concepts**

1. [Best Practices - Coroutines](./docs/best-practices/05-coroutines.md) (20 min)
2. [Best Practices - Physics](./docs/best-practices/06-physics.md) (18 min)
3. [Feel - Getting Started](./docs/feel/README.md) (30 min)
4. **Practice:** Add game feel to your project

---

### Intermediate Path (20-30 hours total)

**Prerequisites:** Complete Beginner Path

**Focus Areas:**

1. **Animation** - [Animancer complete guide](./docs/animancer/README.md) (2-3 hours)
2. **Input** - [Input System](./docs/input-system/README.md) (2-3 hours)
3. **Performance** - [Best Practices - Performance](./docs/best-practices/07-performance-memory.md)
   (1 hour)
4. **Architecture** - [ScriptableObjects](./docs/best-practices/08-scriptable-objects.md) (1 hour)
5. **Optimization** - [Object Pooling](./docs/best-practices/09-object-pooling.md) (1 hour)

**Practice Project:** Complete 2D platformer or top-down shooter

---

### Advanced Path (40+ hours total)

**Prerequisites:** Complete Intermediate Path

**Focus Areas:**

1. **Architecture** - [DxMessaging](./docs/dxmessaging/README.md) (2 hours)
2. **Workflow** - [Assembly Definitions](./docs/assembly-definitions/README.md) (2 hours)
3. **Data** - [Odin Inspector](./docs/odin/README.md) (3 hours)
4. **Optimization** - [Better Build Info PRO](./docs/better-build-info/README.md) (2 hours)
5. **Professional Polish** - Deep dive all tools' advanced sections

**Practice Project:** Mobile game with performance requirements or multi-system game

---

## 🎓 Recommended Free Tools (Start Here!)

If you're on a budget, these FREE tools will take you 80% of the way:

1. ✅ **[Best Practices](./docs/best-practices/README.md)** - FREE knowledge that prevents bugs
2. ✅ **[CSharpier](#csharpier--automatic-code-formatting--free)** - FREE automatic code formatting
3. ✅ **[EditorConfig](#editorconfig--style-enforcement--free)** - FREE style enforcement
4. ✅ **[Graphy](./docs/graphy/README.md)** - FREE performance monitor (Unity Awards winner!)
5. ✅ **[PrimeTween](./docs/primetween/README.md)** - FREE zero-allocation animations
6. ✅ **[Input System](./docs/input-system/README.md)** - FREE official Unity package
7. ✅ **[Assembly Definitions](./docs/assembly-definitions/README.md)** - FREE built-in Unity
   feature
8. ✅ **[DxMessaging](./docs/dxmessaging/README.md)** - FREE open-source messaging
9. ✅ **[Asset Usage Detector](https://github.com/yasirkula/UnityAssetUsageDetector)** - FREE
   alternative to Asset Usage Finder

**Add when budget allows:**

- [Hot Reload](./docs/hot-reload/README.md) - $10-15/month (Free tier available) - Pays for itself
  in 1-2 days
- [Unity Helpers](./docs/unity-helpers/README.md) - FREE! (Open source)
- [Feel](./docs/feel/README.md) - €46 (Free MMFeedbacks version available)
- [Animancer](./docs/animancer/README.md) - ~$50-100
- [Odin](./docs/odin/README.md) - ~$55

---

## 🤝 Contributing

Found an issue or want to suggest improvements? Please open an issue or pull request!

This documentation is a living resource that grows with Unity's ecosystem.

---

## 📄 License

Documentation and examples are provided for educational purposes. Individual tools have their own
licenses - check each tool's documentation for details.

---

## 🌟 Credits

This collection is built from:

- Official Unity documentation
- Community best practices
- Real-world production experience
- Tool developer documentation
- Years of Unity development knowledge

Special thanks to all tool developers who make Unity development better!

---

**Ready to level up your Unity development?**

👉 Start with [Best Practices](./docs/best-practices/README.md) to build a solid foundation!

---

_Last updated: 2025-10-15_
