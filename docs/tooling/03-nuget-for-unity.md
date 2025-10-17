# NuGet For Unity | .NET Packages Inside Unity

NuGetForUnity brings the entire NuGet ecosystem into the Unity Editor. It runs natively inside
Unity, so you can install, update, and remove any NuGet package without leaving the project or
breaking Unity's compilation pipeline.

## Why teams use it

- **Full .NET reach** – Access thousands of libraries (JSON, testing, HTTP clients, and more) that
  are not on the Asset Store.
- **Unity-friendly** – Handles assembly definitions, .dll placement, and dependency graphs the way
  Unity expects, so imported packages show up instantly in your project.
- **One-click upgrades** – Manage direct and transitive dependencies from a single window with
  upgrade/downgrade helpers.
- **Offline cache** – Packages are stored locally, making future installs faster and reproducible.

## Install via Unity Package Manager (preferred)

Unity 2019.3+

1. Open `Window → Package Manager`.
2. Click the `+` button and choose **Add package from git URL...**.
3. Paste the Git URL and click **Add**:

   ```
   https://github.com/GlitchEnzo/NuGetForUnity.git?path=/src/NuGetForUnity
   ```

   To lock to a version append `#v{version}`, for example `#v2.0.0`.

Unity 2019.2 or earlier

Add the dependency directly to `Packages/manifest.json`:

```json
"com.glitchenzo.nugetforunity": "https://github.com/GlitchEnzo/NuGetForUnity.git?path=/src/NuGetForUnity"
```

### Alternative: OpenUPM registry

If you already use [OpenUPM](https://openupm.com/packages/com.github-glitchenzo.nugetforunity/), add
or reuse a scoped registry and then install the package ID `com.github-glitchenzo.nugetforunity` via
Package Manager (or run `openupm add com.github-glitchenzo.nugetforunity`).

## Getting started

1. Launch `NuGet → Manage NuGet Packages` inside Unity.
2. Use the **Online** tab to search the NuGet feed, enable **Show Prerelease** when needed, and
   click **Install** to pull packages and all required dependencies.
3. Review the **Installed** tab to see direct and transitive dependencies. Use **Add as explicit**
   to keep a dependency pinned even if no longer referenced.
4. Visit the **Updates** tab to batch upgrade or downgrade versions with one click.

NuGetForUnity writes assemblies and `.asmdef` files under `Packages/NuGet`, so additions are tracked
in source control and compile like any other UPM package. The plugin respects Unity's domain reloads
and rebuilds, keeping the workflow seamless.

## Tips for production projects

- Audit packages before shipping—NuGet makes it easy to pull advanced libraries, but ensure licenses
  align with your project.
- Check Unity's target framework: when using packages that require newer .NET APIs, set
  `PlayerSettings → Api Compatibility Level` to `.NET Standard 2.1` or above in supported versions.
- Pair with CI: include the `Packages/NuGet` folder in source control so build machines avoid
  re-downloading dependencies.
- Combine with [EditorConfig](./02-editorconfig.md) and [CSharpier](./01-csharpier.md) to enforce
  cross-team standards while consuming wider .NET tooling.

---

## 🎯 Real-World Examples

### Example 1: Using Newtonsoft.Json for Flexible Serialization

**Problem:** Unity's JsonUtility can't serialize dictionaries or complex types.

**Solution:**

```csharp
using Newtonsoft.Json;
using System.Collections.Generic;
using UnityEngine;

public class SaveManager : MonoBehaviour
{
    // Unity can't serialize Dictionary, but Newtonsoft.Json can
    public class SaveData
    {
        public Dictionary<string, int> ItemQuantities { get; set; }
        public DateTime LastSaved { get; set; }
    }

    public void SaveGame()
    {
        var data = new SaveData
        {
            ItemQuantities = new Dictionary<string, int>
            {
                { "HealthPotion", 5 },
                { "ManaPotion", 3 }
            },
            LastSaved = DateTime.Now
        };

        // Newtonsoft.Json handles dictionaries, dates, and complex types
        string json = JsonConvert.SerializeObject(data, Formatting.Indented);
        File.WriteAllText(Application.persistentDataPath + "/save.json", json);
    }

    public SaveData LoadGame()
    {
        string path = Application.persistentDataPath + "/save.json";
        if (!File.Exists(path)) return null;

        string json = File.ReadAllText(path);
        return JsonConvert.DeserializeObject<SaveData>(json);
    }
}
```

**Install:**

```bash
# In Unity: NuGet → Manage NuGet Packages → Search "Newtonsoft.Json"
# Or via command line:
# Not directly supported, use Unity's UI
```

### Example 2: Using Serilog for Advanced Logging

**Problem:** Unity's Debug.Log is basic—no log levels, no file output, no structured logging.

**Solution:**

```csharp
using Serilog;
using Serilog.Core;
using UnityEngine;

public class GameLogger : MonoBehaviour
{
    private static Logger _logger;

    void Awake()
    {
        // Configure Serilog to write to file and Unity console
        _logger = new LoggerConfiguration()
            .MinimumLevel.Debug()
            .WriteTo.File(Application.persistentDataPath + "/logs/game-.log",
                          rollingInterval: RollingInterval.Day)
            .WriteTo.Console()
            .CreateLogger();

        Log.Logger = _logger;
        Log.Information("Game started at {Time}", System.DateTime.Now);
    }

    void OnApplicationQuit()
    {
        Log.Information("Game closed");
        _logger?.Dispose();
    }

    // Usage in other scripts:
    // Log.Information("Player took {Damage} damage", damageAmount);
    // Log.Warning("Low health: {Health}", currentHealth);
    // Log.Error("Failed to load level {LevelName}", levelName);
}
```

**Benefits:**

- Automatic log rotation by day/size
- Structured logging (searchable, parseable)
- Multiple outputs (file + console)
- Log levels (Debug, Info, Warning, Error)

### Example 3: Using FluentValidation for Input Validation

**Problem:** Validating player input or config files is tedious and error-prone.

**Solution:**

```csharp
using FluentValidation;
using UnityEngine;

public class PlayerNameValidator : AbstractValidator<string>
{
    public PlayerNameValidator()
    {
        RuleFor(name => name)
            .NotEmpty().WithMessage("Name cannot be empty")
            .Length(3, 20).WithMessage("Name must be 3-20 characters")
            .Matches("^[a-zA-Z0-9_]+$").WithMessage("Only letters, numbers, and underscores allowed");
    }
}

public class NameInputUI : MonoBehaviour
{
    private PlayerNameValidator _validator = new PlayerNameValidator();

    public void OnNameSubmitted(string playerName)
    {
        var result = _validator.Validate(playerName);

        if (!result.IsValid)
        {
            foreach (var error in result.Errors)
            {
                Debug.LogWarning(error.ErrorMessage);
                // Show error in UI
            }
            return;
        }

        // Name is valid, proceed
        AcceptPlayerName(playerName);
    }
}
```

---

## ✅ Dos and ❌ Don'ts

### ✅ DO

```csharp
// ✅ Check API compatibility level before installing
// Project Settings → Player → Configuration → Api Compatibility Level
// Should be .NET Standard 2.1 or .NET Framework 4.x

// ✅ Test on target platform after adding packages
// Some NuGet packages are desktop-only and won't work on mobile/console

// ✅ Version lock critical packages
// In NuGet UI: right-click package → "Add as explicit"
// Prevents accidental upgrades

// ✅ Commit Packages/NuGet to source control
git add Packages/NuGet
git commit -m "Add Newtonsoft.Json via NuGet"
```

### ❌ DON'T

```csharp
// ❌ Don't install packages requiring .NET 5+ APIs
// Unity only supports .NET Standard 2.1 / .NET Framework 4.x

// ❌ Don't ignore licensing
// Check package license before shipping:
// NuGet UI → Package details → License URL

// ❌ Don't install packages with native dependencies without testing
// Packages with .dll/.so files may not work on all Unity platforms

// ❌ Don't use NuGet packages that conflict with Unity's built-in libraries
// Example: Don't install System.Drawing—Unity has its own Texture2D
```

---

## 🔧 Troubleshooting

### Problem: "Package X requires .NET 5 or higher"

**Cause:** Package uses APIs not available in Unity's .NET Standard 2.1

**Solution:**

1. Check if there's an older version that supports .NET Standard 2.1
2. Search for a Unity-compatible alternative
3. Use OpenUPM or Unity Asset Store instead

**Example:**

```bash
# Bad: Latest version requires .NET 6
NuGet: System.Text.Json 8.0.0 ❌

# Good: Use older version
NuGet: System.Text.Json 6.0.0 ✅ (supports .NET Standard 2.1)

# Better: Use Unity's built-in JsonUtility or Newtonsoft.Json
```

### Problem: "Installed package but Unity shows compilation errors"

**Cause:** Missing dependencies or API compatibility level mismatch

**Solution:**

```bash
# 1. Check API compatibility level
# Unity → Edit → Project Settings → Player → Other Settings
# Set to: .NET Standard 2.1 (or .NET Framework 4.x if needed)

# 2. Check NuGet → Installed tab for missing dependencies
# NuGet usually auto-installs them, but verify

# 3. Restart Unity Editor
# Sometimes Unity needs a domain reload after package install
```

### Problem: "Package works in Editor but crashes on build"

**Cause:** Package uses APIs not available on target platform (mobile, WebGL, console)

**Solution:**

```csharp
// Use conditional compilation to exclude platform-specific code
#if UNITY_EDITOR || UNITY_STANDALONE
    using Serilog;
    Log.Information("This only runs on PC");
#else
    Debug.Log("Fallback for other platforms");
#endif

// Or check at runtime
if (Application.platform == RuntimePlatform.WindowsPlayer)
{
    // Use NuGet package feature
}
else
{
    // Fallback implementation
}
```

**Testing:**

1. Build for target platform early
2. Test on device, not just in Editor
3. Check Unity console for "DllNotFoundException" or "PlatformNotSupportedException"

### Problem: "NuGet window not showing in Unity"

**Cause:** Package not installed or Unity needs restart

**Solution:**

```bash
# 1. Verify installation
# Unity → Window → Package Manager
# Look for "NuGet For Unity" in package list

# 2. If missing, reinstall
# Packages/manifest.json should have:
"com.glitchenzo.nugetforunity": "https://github.com/GlitchEnzo/NuGetForUnity.git?path=/src/NuGetForUnity"

# 3. Restart Unity Editor

# 4. Window → NuGet → Manage NuGet Packages should appear
```

### Problem: "Build size exploded after adding package"

**Cause:** Package includes large dependencies or unused code

**Solution:**

```bash
# 1. Check package size
# Window → Package Manager → Select package → See "Size on Disk"

# 2. Use Unity's Code Stripping
# Project Settings → Player → Other Settings → Managed Stripping Level
# Set to "High" (removes unused code)

# 3. Use IL2CPP instead of Mono
# Smaller builds, better performance
# Project Settings → Player → Scripting Backend → IL2CPP

# 4. Consider alternatives
# Search for lightweight Unity-specific versions on GitHub
```

---

## 🎯 Common Scenarios

### Scenario: Need to use Protobuf for networking

**Problem:** Unity doesn't include protobuf serialization

**Solution:**

```csharp
// 1. Install protobuf-net via NuGet
// NuGet → Search "protobuf-net" → Install

// 2. Define message classes
using ProtoBuf;

[ProtoContract]
public class NetworkMessage
{
    [ProtoMember(1)]
    public int PlayerId { get; set; }

    [ProtoMember(2)]
    public Vector3Data Position { get; set; }
}

[ProtoContract]
public class Vector3Data
{
    [ProtoMember(1)] public float X { get; set; }
    [ProtoMember(2)] public float Y { get; set; }
    [ProtoMember(3)] public float Z { get; set; }
}

// 3. Serialize/deserialize
public byte[] SerializeMessage(NetworkMessage msg)
{
    using var stream = new MemoryStream();
    Serializer.Serialize(stream, msg);
    return stream.ToArray();
}

public NetworkMessage DeserializeMessage(byte[] data)
{
    using var stream = new MemoryStream(data);
    return Serializer.Deserialize<NetworkMessage>(stream);
}
```

### Scenario: Team needs unit testing with xUnit

**Problem:** Unity's built-in test framework is limited

**Solution:**

```bash
# 1. Install xUnit via NuGet
# NuGet → Search "xunit" → Install xunit + xunit.runner.visualstudio

# 2. Create Tests folder outside Assets/
# Unity-Tests/
#   PlayerTests.cs
#   EnemyTests.cs

# 3. Write tests
using Xunit;

public class PlayerTests
{
    [Fact]
    public void TakeDamage_ReducesHealth()
    {
        var player = new Player { Health = 100 };
        player.TakeDamage(20);
        Assert.Equal(80, player.Health);
    }

    [Theory]
    [InlineData(100, 50, 50)]
    [InlineData(100, 100, 0)]
    [InlineData(100, 150, 0)]
    public void TakeDamage_MultipleScenarios(int initial, int damage, int expected)
    {
        var player = new Player { Health = initial };
        player.TakeDamage(damage);
        Assert.Equal(expected, player.Health);
    }
}
```

**Run tests:**

```bash
dotnet test Unity-Tests/
```

---

## 📚 Recommended Packages for Unity

| Package              | Use Case                                      | Installation              |
| -------------------- | --------------------------------------------- | ------------------------- |
| **Newtonsoft.Json**  | Serialize complex types (dictionaries, dates) | Search "Newtonsoft.Json"  |
| **Serilog**          | Advanced logging to files                     | Search "Serilog"          |
| **FluentValidation** | Validate input/config                         | Search "FluentValidation" |
| **protobuf-net**     | Fast binary serialization                     | Search "protobuf-net"     |
| **NSubstitute**      | Mocking for unit tests                        | Search "NSubstitute"      |
| **Polly**            | Retry/timeout policies                        | Search "Polly"            |
| **Humanizer**        | Format strings (pluralization, dates)         | Search "Humanizer"        |

---

## 📚 Learn More

- [NuGet For Unity GitHub](https://github.com/GlitchEnzo/NuGetForUnity)
- [Unity API Compatibility](https://docs.unity3d.com/Manual/dotnetProfileSupport.html)
- [NuGet Package Search](https://www.nuget.org/)
