# Getting Started

> Install the Hot Reload package, enable it in Unity, and make your first edit without entering the
> compile loop.

---

## Installation

Hot Reload is a commercial product available from [hotreload.net](https://hotreload.net/) or the
Unity Asset Store.

1. Purchase and download Hot Reload from the [Unity Asset Store](https://assetstore.unity.com/) or
   [hotreload.net](https://hotreload.net/).
2. Import the package into your Unity project.
3. Once imported, Unity adds the _Hot Reload_ menu and editor window.

> **Note:** Hot Reload is a paid tool. For open-source alternatives, see Unity's built-in
> "Edit and Continue" feature in Unity 2022.2+ or the experimental .NET Hot Reload support.

---

## Project Setup

- Hot Reload manages Unity's Auto Refresh setting automatically—**do not manually enable it**.
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
