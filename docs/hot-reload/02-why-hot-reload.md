# Why Hot Reload?

> Quantify the impact before you adopt it. Hot Reload shortens the code-test cycle so developers
> stay in creative flow.

---

## The Compile-Time Problem

- Even a tiny change in Unity can trigger a full C# recompile.
- Domain reload resets all static data, singletons, and the scene when entering Play Mode.
- Iteration time balloons from seconds to minutes on large projects.

---

## Time & Cost Savings

| Team Size | Avg. Time Saved per Dev/Day | Dollar Impact (at $60/hr) |
| --------- | --------------------------- | ------------------------- |
| Solo      | 45 minutes                  | $45                       |
| 5 devs    | 2.5 hours total             | $150                      |
| 15 devs   | 6.5 hours total             | $390                      |

> Multiply this by months and the investment pays for itself quickly.

---

## Workflow Comparison

| Step              | Traditional Compile  | Hot Reload               |
| ----------------- | -------------------- | ------------------------ |
| Save file         | Recompile assemblies | Diff method & emit patch |
| Domain reload     | Yes (scene resets)   | No                       |
| Play Mode restart | Yes                  | No                       |
| State preserved   | Rarely               | Always                   |

---

## Supported vs. Unsupported Changes

✅ Supported (apply instantly):

- Method body changes
- Conditional logic
- Serialized field defaults
- Local functions and lambdas

⚠️ Requires full compile (use the **Recompile** button):

- Adding new methods/classes
- Changing method signatures
- Editing attributes
- Modifying serialized field names (Unity needs a domain reload)

---

## Alternative Solutions

| Tool                  | Strengths                                 | Limitations                  |
| --------------------- | ----------------------------------------- | ---------------------------- |
| Unity Enter Play Mode | Skips domain reload, but still recompiles | No code hot swap             |
| Fast Script Reload    | Community plugin, good for prototypes     | Fewer features, less support |
| Live coding (custom)  | Flexible                                  | Maintenance burden           |

Pick Hot Reload when you want a supported, team-ready solution without writing tooling yourself.

---

## Rollout Strategy

1. Test in a feature branch with a few developers.
2. Document workflow differences (see [How to Use It](03-how-to-use.md)).
3. Add Hot Reload configuration to version control if using a custom server.
4. Track compile time saved to justify license cost.

---

## FAQ

**Does it affect build size?** No. Patches are editor-only.

**Will it break Play Mode tests?** Tests continue to run; hot reload only touches the editor
runtime.

**Can it run on build machines?** No. It is a development-time tool only.

---

Ready to apply it daily? Continue to [How to Use It](03-how-to-use.md).
