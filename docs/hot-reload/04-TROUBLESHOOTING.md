# Troubleshooting

> Things not updating? Use this reference to get back on track quickly.

---

## Changes Not Applying

- Check the Hot Reload window for compile errors.
- Confirm **Apply Automatically** is enabled.
- Ensure the script file is part of the Unity project (not excluded via asmdef or platform filters).

---

## Auto Refresh Conflicts

- Unity's **Auto Refresh** must be on so file saves trigger a refresh.
- If using source control tools that lock files, unlock before editing.

---

## When to Use Manual Recompile

Use **Recompile** after structural changes (new methods, fields, classes) or assembly definition
updates. Hot Reload reports "Manual recompile required" when it detects a change it cannot patch.

---

## IDE-Specific Issues

- **Rider**: Disable _Run Configurations → External Console_ when debugging; it can block patching.
- **Visual Studio**: Install the Unity workload so the solution stays in sync with generated C#
  projects.
- **VS Code**: Ensure the
  [C# Dev Kit](https://marketplace.visualstudio.com/items?itemName=ms-dotnettools.csdevkit) is up to
  date.

---

## Performance Problems

- Too many rapid saves can queue many patches—slow down auto save or increase the debounce.
- If the editor feels sluggish, clear logs and restart the Hot Reload server (button in the window).

---

## Network & Firewall Issues

- On-device hot reload requires the player and editor to share a network and port access.
- Add firewall exceptions for `HotReloadServer.exe` (Windows) or allow connections (macOS).

---

## Troubleshooting Checklist

- [ ] Hot Reload window open, no pending errors
- [ ] Auto Refresh enabled in Unity preferences
- [ ] Project compiled successfully at least once after installation
- [ ] Domain reload not disabled if editor scripts rely on it
- [ ] Package version verified in `Packages/manifest.json`

---

If problems persist, consult the [official documentation](https://hotreload.net/docs/unity) or email
support with Unity Editor version, package version, and reproduction steps.
