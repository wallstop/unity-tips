# EditorConfig | Naming & Style Enforcement

**Website:** [Editorconfig](https://editorconfig.org/)

EditorConfig turns your style guide into automated IDE warnings. Pair it with CSharpier: the
formatter fixes whitespace, while EditorConfig keeps naming, braces, and other rules consistent
across the team.

## Starter `.editorconfig`

```ini
# Top-most EditorConfig file
root = true

[*]
charset = utf-8
indent_style = space
indent_size = 4
trim_trailing_whitespace = true
insert_final_newline = true

[*.cs]
# Always use braces for control flow
csharp_prefer_braces = true:warning

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

# Private fields: _health, _playerSpeed (_camelCase)
dotnet_naming_rule.private_fields_rule.severity = warning
dotnet_naming_rule.private_fields_rule.symbols = private_fields
dotnet_naming_rule.private_fields_rule.style = underscore_camel_case
dotnet_naming_symbols.private_fields.applicable_kinds = field
dotnet_naming_symbols.private_fields.applicable_accessibilities = private
dotnet_naming_style.underscore_camel_case.capitalization = camel_case
dotnet_naming_style.underscore_camel_case.required_prefix = _

# Public fields: health, playerSpeed (camelCase)
dotnet_naming_rule.public_fields_rule.severity = warning
dotnet_naming_rule.public_fields_rule.symbols = public_fields
dotnet_naming_rule.public_fields_rule.style = camel_case
dotnet_naming_symbols.public_fields.applicable_kinds = field
dotnet_naming_symbols.public_fields.applicable_accessibilities = public
dotnet_naming_style.camel_case.capitalization = camel_case

# Properties: Health, PlayerSpeed (PascalCase)
dotnet_naming_rule.properties_rule.severity = warning
dotnet_naming_rule.properties_rule.symbols = properties
dotnet_naming_rule.properties_rule.style = pascal_case
dotnet_naming_symbols.properties.applicable_kinds = property
dotnet_naming_style.pascal_case.capitalization = pascal_case
```

## Common Unity conventions to enforce

- Interfaces start with `I` (`IPlayer`, `IEnemy`).
- Events start with `On` (`OnClick`, `OnPlayerDied`).
- Type parameters start with `T` (`TComponent`, `TValue`).
- Private fields use `_camelCase` (`_health`, `_playerSpeed`), or `camelCase` (`health`,
  `playerSpeed`)
- Public fields use `camelCase` unless Unity's serializer requires otherwise.
- Properties use `PascalCase` (`Health`, `PlayerSpeed`).
- Always include braces for `if`, `for`, `while`, etc. The samples in this documentation omit braces
  for brevity.

---

## 🎯 What Gets Caught

### Before EditorConfig (No Warnings)

```csharp
// Inconsistent naming compiles fine but breaks conventions
public interface PlayerController { }  // Should be IPlayerController
public event Action Click;              // Should be OnClick
private int Health;                     // Should be _health or health
public int player_speed;                // Should be playerSpeed

if (health < 0)
    Die();                              // Missing braces
```

### After EditorConfig (IDE Warnings)

```csharp
// IDE shows warnings for all convention violations:
public interface PlayerController { }  // Warning: Interface must start with 'I'
public event Action Click;              // Warning: Event must start with 'On'
private int Health;                     // Warning: Private field must start with '_'
public int player_speed;                // Warning: Public field must be camelCase

if (health < 0)
    Die();                              // Warning: Add braces
```

### After Fix (Clean)

```csharp
// All conventions followed, no warnings
public interface IPlayerController { }
public event Action OnClick;
private int _health;
public int playerSpeed;

if (health < 0)
{
    Die();
}
```

---

## ✅ Dos and ❌ Don'ts

### ✅ DO

```csharp
// ✅ Follow the conventions, IDE stays quiet
public class Enemy : MonoBehaviour
{
    [SerializeField] private int _maxHealth = 100;
    public int currentHealth;

    public event Action OnDeath;

    public void TakeDamage(int amount)
    {
        currentHealth -= amount;
        if (currentHealth <= 0)
        {
            OnDeath?.Invoke();
        }
    }
}

// ✅ Interfaces start with I
public interface IDamageable
{
    void TakeDamage(int amount);
}

// ✅ Generics start with T
public class Pool<TItem> where TItem : Component { }
```

### ❌ DON'T

```csharp
// ❌ Wrong: Interface missing I prefix
public interface Damageable { }  // Should be IDamageable

// ❌ Wrong: Event missing On prefix
public event Action Death;       // Should be OnDeath

// ❌ Wrong: Private field not using _camelCase or camelCase
private int m_health;            // Unity's old style—use _health

// ❌ Wrong: No braces for single-line if
if (health <= 0) Die();          // Should use braces

// ❌ Wrong: Generic not using T prefix
public class Pool<Item> { }      // Should be TItem
```

---

## 🔧 Troubleshooting

### Problem: "EditorConfig warnings not showing in IDE"

**VS Code:**

1. Install the "EditorConfig for VS Code" extension
2. Install C# Dev Kit or Omnisharp extension
3. Reload window (`Ctrl+Shift+P` → "Reload Window")

**Rider:**

- EditorConfig is built-in, but you need to enable C# inspections:
  1. Settings → Editor → Code Style → C#
  2. Check "Enable EditorConfig support"
  3. Settings → Editor → Inspection Settings
  4. Ensure "Naming rules" severity is set to "Warning" or "Error"

**Visual Studio:**

- Built-in support since VS 2017. If not working:
  1. Tools → Options → Text Editor → C# → Code Style
  2. Ensure "Generate EditorConfig" is checked
  3. Restart Visual Studio

### Problem: "Warnings only show in some files"

**Cause:** EditorConfig only applies to files in subdirectories of where `.editorconfig` is located.

**Solution:** Place `.editorconfig` at repository root and ensure `root = true` is set:

```ini
# .editorconfig at repository root
root = true

[*]
# ... settings ...
```

### Problem: "Team members ignoring warnings"

**Solution:** Enforce in CI/CD pipeline:

```bash
# Install dotnet-format tool
dotnet tool install -g dotnet-format

# Check for style violations (fails build if found)
dotnet format --verify-no-changes --severity warn
```

**GitHub Actions example:**

```yaml
- name: Check code style
  run: |
    dotnet tool install -g dotnet-format
    dotnet format --verify-no-changes --severity warn
```

### Problem: "Conflicts between EditorConfig and CSharpier"

**Solution:** They work together! EditorConfig handles naming/style rules, CSharpier handles
formatting.

**Don't configure formatting in EditorConfig** (indent style, brace position, etc.) if using
CSharpier—it will override those settings anyway.

```ini
# ✅ GOOD: Let CSharpier handle formatting
[*.cs]
# Naming rules only
dotnet_naming_rule.interfaces_rule.severity = warning

# ❌ BAD: These conflict with CSharpier
# csharp_new_line_before_open_brace = all
# csharp_indent_size = 4
```

### Problem: "How do I find all violations at once?"

**Solution:**

```bash
# Install dotnet-format
dotnet tool install -g dotnet-format

# Show all violations without fixing
dotnet format --verify-no-changes --verbosity diagnostic

# Fix all violations automatically
dotnet format
```

---

## 🎯 Common Scenarios

### Scenario: Migrating from Unity's `m_` prefix

**Old Unity style:**

```csharp
private int m_health;
private float m_speed;
```

**Modern C# style:**

```csharp
private int _health;
private float _speed;
```

**Migration steps:**

1. Add EditorConfig with `_camelCase` rule
2. Use Rider's "Fix all in solution" or `dotnet format`
3. Review changes and commit

**Find-replace regex (VS Code/Rider):**

- Find: `\bm_([a-z])`
- Replace: `_$1`

### Scenario: Enforcing event naming

**Problem:** Some events use `On` prefix, some don't

**Before:**

```csharp
public event Action PlayerDied;      // Inconsistent
public event Action OnHealthChanged; // Inconsistent
```

**After EditorConfig:**

```csharp
public event Action OnPlayerDied;      // ✅ Consistent
public event Action OnHealthChanged;   // ✅ Consistent
```

**EditorConfig rule:**

```ini
# Events must start with On
dotnet_naming_rule.events_rule.severity = warning
dotnet_naming_rule.events_rule.symbols = event
dotnet_naming_rule.events_rule.style = begins_with_on
dotnet_naming_symbols.event.applicable_kinds = event
dotnet_naming_style.begins_with_on.capitalization = pascal_case
dotnet_naming_style.begins_with_on.required_prefix = On
```

### Scenario: Team members using different editors

**Problem:** VS Code, Rider, and Visual Studio users need consistent style

**Solution:** EditorConfig works in all three! Just ensure the file is at the repo root.

**Bonus:** Add to version control:

```bash
git add .editorconfig
git commit -m "Add EditorConfig for consistent style across editors"
```

Everyone who clones the repo gets the same warnings automatically.

---

## 📚 Advanced Rules

### Enforce braces for all control flow

```ini
# Always use braces, even for single-line if/for/while
csharp_prefer_braces = true:warning
```

**Before:**

```csharp
if (health <= 0) Die();  // Warning: Add braces
```

**After:**

```csharp
if (health <= 0)
{
    Die();
}
```

### Enforce explicit access modifiers

```ini
# Require explicit public/private/protected
dotnet_style_require_accessibility_modifiers = always:warning
```

**Before:**

```csharp
void Update() { }  // Warning: Add access modifier
```

**After:**

```csharp
private void Update() { }
```

### Enforce `this.` for clarity

```ini
# Require 'this.' when accessing instance members
dotnet_style_qualification_for_field = true:warning
dotnet_style_qualification_for_property = true:warning
```

**Before:**

```csharp
public void Heal()
{
    health += 10;  // Warning: Use this.health
}
```

**After:**

```csharp
public void Heal()
{
    this.health += 10;
}
```

**Note:** This is controversial—most Unity developers don't use `this.` unless disambiguating. Set
to `false` if your team prefers cleaner code.

---

## 📚 Learn More

- [EditorConfig Docs](https://editorconfig.org/)
- [C# EditorConfig Options](https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/code-style-rule-options)
- [EditorConfig Generator](https://editorconfig.org/#download) – Interactive config builder
