# CSharpier | Automatic Code Formatting

**Website:** [Csharpier](https://csharpier.com/)

CSharpier keeps every C# file perfectly formatted. Write code however you want; the formatter makes
it consistent the moment you save. That means no style debates, fewer whitespace merge conflicts,
and zero time spent manually reformatting files.

## Why teams rely on it

- **Zero mental overhead** – stop thinking about indentation or spacing.
- **Deterministic output** – everyone sees the exact same formatting.
- **Integrates everywhere** – editor plug-ins, pre-commit hooks, CI pipelines.
- **Merge friendly** – consistent formatting keeps diffs small and readable.

```csharp
// Input: messy code you just typed
public class Player:MonoBehaviour{
private int health=100;public void TakeDamage(int amount){health-=amount;
if(health<=0)Die();}}

// Output: CSharpier's consistent formatting
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

## Setup checklist (≈5 minutes)

### 1. Install as a .NET local tool

```bash
# Ensure the .config directory exists
mkdir -p .config

cat > .config/dotnet-tools.json <<'JSON'
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
JSON

dotnet tool restore
```

### 2. Add a pre-commit hook

```bash
pip install pre-commit

cat > .pre-commit-config.yaml <<'YAML'
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
YAML

pre-commit install
```

### 3. Enforce formatting in CI/CD

```yaml
# GitHub Actions example
- name: Check code formatting
  run: |
    dotnet tool restore
    dotnet csharpier --check .
```

### 4. Enable format-on-save in your editor

- **VS Code:** Install the "CSharpier" extension and enable format-on-save.
- **JetBrains Rider:** Install the "CSharpier" plug-in and enable format-on-save in preferences.
- **Visual Studio:** Install the "CSharpier" extension and enable format-on-save.

**Cost:** Free (MIT license).

---

## ✅ Dos and ❌ Don'ts

### ✅ DO

```csharp
// ✅ Write code naturally, let CSharpier fix it
public void Attack(Enemy target){
int damage = baseDamage+critBonus;
target.TakeDamage(damage);
Debug.Log("Attacked "+target.name);}

// After save → CSharpier formats automatically:
public void Attack(Enemy target)
{
    int damage = baseDamage + critBonus;
    target.TakeDamage(damage);
    Debug.Log("Attacked " + target.name);
}
```

```csharp
// ✅ Let team members use their own brace style while typing
// Everyone gets the same output after save
public class PlayerController : MonoBehaviour
{
    void Update()
    {
        // Code here
    }
}

// ✅ Format entire project before merging
dotnet csharpier format .
```

### ❌ DON'T

```csharp
// ❌ Don't waste time manually formatting
public void Heal   (   int amount   )    // Stop adjusting spacing!
{
    health   +=   amount;                 // CSharpier does this
}

// ❌ Don't commit unformatted code
// Add pre-commit hook or CI check to catch this

// ❌ Don't try to preserve manual formatting
// CSharpier will overwrite it—embrace the consistency!
```

---

## 🔧 Troubleshooting

### Problem: "Command 'dotnet csharpier' not found"

**Cause:** .NET tools not restored or .NET SDK not in PATH

**Solution:**

```bash
# 1. Ensure .NET SDK is installed
dotnet --version  # Should show version 6.0 or higher

# 2. Restore tools
dotnet tool restore

# 3. Verify CSharpier is available
dotnet csharpier --version
```

### Problem: "CSharpier changed too much in my file!"

**Cause:** File had inconsistent formatting

**Solution:** This is expected on first format. Review the changes once, then commit.

```bash
# Format one file at a time if nervous
dotnet csharpier Assets/Scripts/Player/PlayerController.cs

# Review changes with git diff
git diff Assets/Scripts/Player/PlayerController.cs

# If good, format rest of project
dotnet csharpier .
```

**Pro tip:** Format the whole codebase in a dedicated "Add CSharpier formatting" commit so git blame
stays clean.

### Problem: "Format-on-save not working in my IDE"

**VS Code:**

```jsonc
// Check .vscode/settings.json
{
  "editor.formatOnSave": true,
  "[csharp]": {
    "editor.defaultFormatter": "csharpier.csharpier"
  }
}
```

**Rider:**

1. Settings → Tools → CSharpier
2. Enable "Run on Save"
3. Set "CSharpier location" to "Local Tool (.config/dotnet-tools.json)"

**Visual Studio:**

1. Tools → Options → CSharpier
2. Enable "Format on Save"

### Problem: "Pre-commit hook failing on fresh clone"

**Cause:** Team member hasn't run `dotnet tool restore`

**Solution:** Add to project setup docs or use a composite hook:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: dotnet-tool-restore
        name: Ensure .NET tools are installed
        entry: dotnet tool restore
        language: system
        always_run: true
        pass_filenames: false
      - id: csharpier
        name: Format C# files
        entry: dotnet csharpier
        language: system
        types: [c#]
```

### Problem: "Can I configure line width or brace style?"

**No.** CSharpier is opinionated by design—no configuration means no debates. If your team wants
different formatting, CSharpier isn't the right tool.

**Alternative:** Use a different formatter (like Roslyn formatters with `.editorconfig`), but you'll
lose the zero-config benefit.

---

## 🎯 Common Scenarios

### Scenario: Large legacy codebase

**Problem:** 10,000+ lines of inconsistent formatting

**Solution:**

```bash
# 1. Create a dedicated branch
git checkout -b formatting/add-csharpier

# 2. Format everything
dotnet csharpier .

# 3. Commit with descriptive message
git add .
git commit -m "chore: apply CSharpier formatting

This commit only changes formatting—no logic changes.
All future commits will have consistent formatting."

# 4. Merge to main
git push origin formatting/add-csharpier
```

**Pro tip:** Use `git blame --ignore-rev <commit-hash>` to skip formatting commits in blame history.

### Scenario: Mid-project adoption

**Problem:** Don't want to reformat files unrelated to current work

**Solution:** Format only changed files in pre-commit hook:

```yaml
# .pre-commit-config.yaml
- id: csharpier
  name: Format modified C# files
  entry: dotnet csharpier
  language: system
  types: [c#]
  # Only formats files being committed
```

Gradually, the whole codebase becomes formatted as files are touched.

---

## 📚 Learn More

- [CSharpier Docs](https://csharpier.com/)
- [CSharpier Playground](https://playground.csharpier.com/) – See formatting in real-time
- [Why CSharpier is opinionated](https://csharpier.com/docs/About) – Design philosophy
