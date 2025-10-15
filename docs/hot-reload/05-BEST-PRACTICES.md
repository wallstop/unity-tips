# Best Practices & Examples

> Optimise your workflow with repeatable patterns, team policies, and automation ideas.

---

## When to Hot Reload vs. Recompile

- Use Hot Reload for logic tweaks, UI text, and gameplay balancing.
- Recompile when adding scripts, changing public API surface, or touching attributes.
- Schedule periodic clean recompiles (e.g., daily) to ensure the project still builds fresh.

---

## Team Workflow Patterns

- Agree on when to click **Recompile** (typically before committing).
- Document the workflow in your team wiki and link to this guide.
- Pair with feature flags: toggle behaviours via hot reload to test quickly.

---

## Working with Unit Tests

- Hot reload supports Play Mode and Edit Mode tests—rerun failed tests after patching.
- If a test references a newly added method, do a full recompile first.

---

## Excluding from Builds

- Keep editor-only scripts (e.g., dev tools) inside an `Editor` folder or wrap with
  `#if UNITY_EDITOR` so they stay out of player builds.
- For enterprise setups, consider a custom build check that verifies no hot reload patches are
  pending before releasing.

---

## State Management Tips

- Persist debug values in ScriptableObjects so they survive hot reload and domain reload.
- When working with static fields, expose reset buttons in the editor to clear state manually.

---

## Example Workflow

```csharp
public class EnemySpawner : MonoBehaviour
{
    [SerializeField] private float _spawnInterval = 5f;
    [SerializeField] private GameObject _enemyPrefab;

    private float _timer;

    void Update()
    {
        _timer += Time.deltaTime;
        if (_timer >= _spawnInterval)
        {
            _timer = 0f;
            Spawn();
        }
    }

    private void Spawn()
    {
        Instantiate(_enemyPrefab, transform.position, Quaternion.identity);
    }
}
```

Change `_spawnInterval` or the behaviour inside `Spawn()` during Play Mode to tune pacing instantly.

---

## Next Steps

1. Read [Getting Started](01-GETTING-STARTED.md) if you skipped the setup.
2. Share [How to Use It](03-HOW-TO-USE.md) with the rest of your team.
3. Log recurring issues in your project wiki so the whole team benefits.

---

Keep iterating quickly, and combine Hot Reload with profiling tools to spot performance regressions
as soon as they appear.
