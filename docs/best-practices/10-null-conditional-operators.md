# Null-Conditional Operators with Unity Objects

Unity's `Destroy()` tears down the native object but leaves the managed wrapper alive. C#'s
null-conditional (`?.`) and null-coalescing (`??`) operators check the managed wrapper only, so they
silently bypass Unity's overloaded equality operators. The result: code that looks safe still throws
exceptions or chooses destroyed objects.

## Why it fails

- Unity objects are managed wrappers around native C++ instances.
- `Destroy()` removes the native side, leaving the managed wrapper orphaned.
- Unity overrides `==`/`!=` to report destroyed objects as `null`.
- `?.` and `??` ignore operator overloads; they use raw reference null checks.

## Bug examples

```csharp
// Destroyed GameObject still passes the C# null-conditional check
GameObject player = destroyedGameObject;
Vector3? position = player?.transform.position; // Throws NullReferenceException

Transform target = destroyedTransform ?? fallback; // Returns destroyedTransform
```

```csharp
public class PlayerController : MonoBehaviour
{
    [SerializeField] private GameObject target;
    [SerializeField] private Transform defaultTarget;

    private void Update()
    {
        // Looks safe, but target?.transform throws when the enemy was destroyed
        Transform finalTarget = target?.transform ?? defaultTarget;

        // ✅ Safe version: rely on Unity's operator overload instead
        if (target != null)
        {
            Transform safeTarget = target.transform;
        }

        Transform resolved = target != null ? target.transform : defaultTarget;
    }
}
```

## Safe patterns

- Use explicit `!= null` checks on any type derived from `UnityEngine.Object`.
- Cache references after a null check if you need to reuse them.
- Replace `foo?.Bar ?? fallback` with `foo != null ? foo.Bar : fallback` when `foo` might be a Unity
  object.

## What counts as a Unity object?

- `GameObject`, `Transform`, `Component`
- Anything inheriting from `MonoBehaviour`, `ScriptableObject`, or `UnityEngine.Object`

Safe to use `?.`/`??` with plain C# classes, structs, and primitives—just avoid Unity engine types.

## Prevention tips

- Document the rule in your team style guide and code reviews.
- Consider an analyzer that flags `?.` or `??` when the receiver derives from `UnityEngine.Object`.
- Add unit tests around systems where destroyed objects are common (object pooling, combat, async
  callbacks).

**Bottom line:** When Unity objects are in play, prefer explicit null checks. It is the only way to
get the engine's overloaded behavior and avoid hard-to-debug crashes.
