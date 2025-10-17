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
