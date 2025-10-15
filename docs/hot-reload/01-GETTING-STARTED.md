# Getting Started

> Install the Hot Reload package, enable it in Unity, and make your first edit without entering the
> compile loop.

---

## Installation

1. Open **Window → Package Manager**.
2. Click the **+** button → **Add package from git URL**.
3. Paste `https://github.com/dotnet/hotreload-unity.git` (or your private fork) and click **Add**.
4. Once imported, Unity adds the _Hot Reload_ menu and editor window.

> Already using a local clone? Use "Add package from disk" and select the package's `package.json`.

---

## Project Setup

- Enable **Auto Refresh** in Unity preferences so file saves trigger hot reload automatically.
- Open **Window → Hot Reload** and keep the window docked; it shows pending patches and log output.
- Decide if you want **Apply Changes Automatically** (recommended) or manual confirmation.

---

## Your First Hot Reload

1. Enter **Play Mode**.
2. Pick any MonoBehaviour method and change a literal or conditional.
3. Save the file.
4. Watch the change apply instantly—Unity stays in Play Mode and your state persists.

```csharp
void Update()
{
    if (Input.GetKeyDown(KeyCode.Space))
    {
        Debug.Log("Jump!"); // Change this string while in Play Mode
    }
}
```

You should see the new string printed without recompiling or losing scene state.

---

## How It Works (Crash Course)

- Hot Reload rewrites just the methods that changed, producing lightweight patches.
- Patched methods replace the originals in memory; Unity does not reload assemblies.
- Static fields, singletons, and scene objects keep their existing state.

---

## Opening the Window & Shortcut

- **Menu**: `Window → Hot Reload`.
- **Shortcut**: `Alt + Shift + H` on Windows/Linux, `⌥ + ⇧ + H` on macOS.

Use the window to apply queued patches manually or to trigger a full recompile when needed.

---

## Basic Workflow Checklist

- [ ] Hot Reload window is docked and visible.
- [ ] "Apply changes automatically" enabled.
- [ ] Domain reload disabled in **Enter Play Mode Options** if you want faster Play Mode restarts.
- [ ] Version control ignores the package cache (if using a local checkout).

---

## Next Steps

Move on to [Why Hot Reload?](02-WHY-HOT-RELOAD.md) to understand the productivity gains and
limitations before rolling it out to the whole team.
