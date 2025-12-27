# How to Use It

> Learn the day-to-day workflow: patching, manual recompiles, on-device usage, and IDE integration.

---

## Opening the Hot Reload Window

- Menu: **Window → Hot Reload**
- Shortcut: `Alt + Shift + H` (Windows/Linux) or `⌥ + ⇧ + H` (macOS)

Pin the window in a dock so you can see patch status while coding.

---

## Making Hot Reload Changes

1. Enter Play Mode (or stay in Edit Mode if you only need editor-time hot reload).
2. Edit a method body, constant, or lambda.
3. Save the file.
4. The change applies automatically if auto-apply is enabled. Otherwise, click **Apply Patches**.

If a change fails, the console displays the compile error but Unity remains in Play Mode. Fix the
code and save again.

---

## Manual Recompile Button

Use **Recompile** when you:

- Add new methods, classes, or namespaces.
- Change serialized field declarations that Unity must recognise.
- Update attributes or reflection-heavy code.

Manual recompile performs a regular Unity build but keeps the workflow in one place.

---

## Using Different IDEs

| IDE               | Setup Tips                                                                                                        |
| ----------------- | ----------------------------------------------------------------------------------------------------------------- |
| **Rider**         | Enable _External Tools → JetBrains Rider_ and keep the Hot Reload window visible; Rider auto-saves on focus loss. |
| **Visual Studio** | Turn on _Tools → Options → Text Editor → All Languages → Auto Save_ to push patches quickly.                      |
| **VS Code**       | Install _Auto Save_ or enable File → Auto Save (after delay).                                                     |

---

## On-Device Hot Reload

1. Build a Development Player with the Hot Reload runtime enabled.
2. Launch the player and enter the same local network as the editor.
3. Use the Hot Reload window to connect to the player and push patches.

> Tip: Keep a small scriptable object with credentials if you ship builds to QA frequently.

---

## Edit Mode vs. Play Mode

- **Play Mode**: Fastest feedback; state is preserved.
- **Edit Mode**: Useful for editor tooling, scriptable object processors, or runtime initialisation
  code that runs in edit scripts.

You can toggle _Apply in Edit Mode_ within the Hot Reload window.

---

## Integrating with Your Workflow

- Combine with **Enter Play Mode Options** (skip domain reload) for even faster iteration.
- Use version control hooks (pre-commit) to ensure patches are cleared before commits.
- Educate the team about changes that still require a full compile (see
  [Troubleshooting](04-troubleshooting.md)).

---

## Quick Reference

| Task                  | Action                                           |
| --------------------- | ------------------------------------------------ |
| See recent patches    | Check Hot Reload window log                      |
| Apply pending patches | Click **Apply** or enable auto-apply             |
| Force full recompile  | Click **Recompile**                              |
| Toggle device target  | Use the device dropdown in the Hot Reload window |
| Clear patch history   | Use **Clear Logs** to keep the console readable  |

---

Ready to diagnose issues? Move on to [Troubleshooting](04-troubleshooting.md).
