# Getting Started with PrimeTween

> **Quick Start**: Add `using PrimeTween;` to your script, then call
> `Tween.Position(transform, endValue: new Vector3(10, 0, 0), duration: 1f);` — that's it!

## What is PrimeTween?

PrimeTween is a **zero-allocation, high-performance animation library** for Unity. It lets you
animate transforms, UI elements, materials, audio, cameras, and custom data with simple, one-line
calls while keeping every animation configurable in the Inspector.

```csharp
using PrimeTween;

// Animate anything in one line
Tween.Position(transform, endValue: targetPosition, duration: 1f);
Tween.Scale(transform, endValue: 1.5f, duration: 0.5f, ease: Ease.OutBack);
Tween.Color(spriteRenderer, endValue: Color.red, duration: 0.3f);
```

## Installation

PrimeTween is already installed in this project via Unity Package Manager. You can verify by
checking:

- `Assets/Plugins/PrimeTween/` directory
- Package Manager window → PrimeTween package

For new projects, install via:

1. Unity Package Manager → Add package from git URL
2. Use: `https://github.com/KyryloKuzyk/PrimeTween.git`
3. Or download from Unity Asset Store (FREE)

## Your First Animation

Let's animate a UI button that pulses when hovered:

```csharp
using UnityEngine;
using PrimeTween;

public class PulsingButton : MonoBehaviour
{
    [SerializeField] private float hoverScale = 1.2f;
    [SerializeField] private float duration = 0.3f;

    private Tween currentTween;

    private void OnMouseEnter()
    {
        // Stop any existing animation
        currentTween.Stop();

        // Scale up smoothly
        currentTween = Tween.Scale(
            transform,
            endValue: hoverScale,
            duration: duration,
            ease: Ease.OutBack  // Adds a nice "bounce" effect
        );
    }

    private void OnMouseExit()
    {
        currentTween.Stop();
        currentTween = Tween.Scale(transform, endValue: 1f, duration: duration);
    }
}
```

### What Just Happened?

1. **`Tween.Scale(transform, ...)`** returns a lightweight `Tween` struct
2. **Storing it** lets you stop/modify the animation later
3. **`.Stop()`** is safe to call even if the tween is dead
4. **`ease: Ease.OutBack`** creates a pleasant overshoot effect

## Core Concepts (8 Total)

PrimeTween has only **8 top-level concepts** — you can learn the entire API without reading
extensive docs:

### 1. **Tween Methods**

Static methods on the `Tween` class for animating everything:

```csharp
Tween.Position()      // Move transforms
Tween.Scale()         // Scale transforms
Tween.Rotation()      // Rotate transforms
Tween.Color()         // Animate colors (SpriteRenderer, Image, Material)
Tween.Alpha()         // Fade transparency
Tween.Custom()        // Animate anything custom
Tween.Delay()         // Wait before executing callback
```

### 2. **Tween Struct**

Returned by every `Tween.*` call. It's a lightweight handle for controlling animations:

```csharp
Tween myTween = Tween.Position(transform, targetPos, 1f);

if (myTween.isAlive) myTween.Stop();     // Cancel animation
myTween.Complete();                       // Jump to end instantly
myTween.isPaused = true;                  // Pause/resume
```

### 3. **Duration & Easing**

```csharp
Tween.Scale(
    transform,
    endValue: 2f,
    duration: 1.5f,              // Time in seconds
    ease: Ease.InOutQuad         // See full list at Ease enum
);
```

**Common Easing Curves:**

- `Ease.Linear` — constant speed
- `Ease.InOutSine` — smooth start and end
- `Ease.OutBack` — overshoot effect (UI buttons!)
- `Ease.InOutElastic` — bouncy spring effect

[View all 30+ easing functions](https://easings.net/)

### 4. **Callbacks**

Execute code when animations complete or update:

```csharp
Tween.Position(transform, targetPos, 1f)
    .OnComplete(() => Debug.Log("Animation finished!"));

// Zero-allocation version (recommended for hot paths)
Tween.Position(transform, targetPos, 1f)
    .OnComplete(target: this, (self, _) => self.OnAnimationFinished());
```

### 5. **Sequences**

Chain or group multiple animations:

```csharp
Sequence.Create()
    .Chain(Tween.Position(transform, Vector3.up * 5, 1f))   // First
    .Chain(Tween.Scale(transform, 1.5f, 0.5f))              // Then this
    .Group(Tween.Color(spriteRenderer, Color.red, 0.5f));   // At the same time as scale
```

### 6. **TweenSettings**

Serialize animation parameters in the Inspector:

```csharp
[SerializeField] private TweenSettings hoverSettings;

private void Start()
{
    // Designers can now tweak duration/easing without code changes!
    Tween.Scale(transform, 1.2f, hoverSettings);
}
```

In the Inspector, you'll see fields for:

- Duration
- Ease type
- Start delay
- Cycles (loops)
- Update type (Normal/Late/Fixed)

### 7. **Shake & Punch**

Add impact effects:

```csharp
// Camera shake on explosion
Tween.ShakeCamera(Camera.main, strength: 0.5f, duration: 0.3f);

// Punch scale on hit
Tween.PunchScale(transform, strength: 0.3f, duration: 0.5f);
```

### 8. **Custom Tweens**

Animate anything that's not a transform/color:

```csharp
// Animate audio volume
Tween.Custom(
    startValue: 0f,
    endValue: 1f,
    duration: 2f,
    onValueChange: value => audioSource.volume = value
);

// Animate material property
Tween.Custom(0f, 1f, 1f, v => material.SetFloat("_Cutoff", v));
```

## Common Use Cases

### UI Button Feedback

```csharp
void OnButtonClick()
{
    // Quick scale down + up gives tactile feedback
    Sequence.Create()
        .Chain(Tween.Scale(transform, 0.9f, 0.1f))
        .Chain(Tween.Scale(transform, 1.0f, 0.1f, ease: Ease.OutBack));
}
```

### Fade In UI Panel

```csharp
void ShowPanel()
{
    CanvasGroup canvasGroup = GetComponent<CanvasGroup>();
    canvasGroup.alpha = 0;

    Tween.Alpha(canvasGroup, endValue: 1f, duration: 0.5f);
}
```

### Smooth Camera Follow

```csharp
void Update()
{
    Vector3 targetPos = player.position + offset;
    Tween.Position(
        Camera.main.transform,
        targetPos,
        duration: Time.deltaTime * 5f  // Smooth damping
    );
}
```

### Object Drop with Bounce

```csharp
void DropItem(Vector3 dropPosition)
{
    Sequence.Create()
        .Chain(Tween.Position(transform, dropPosition, 0.5f, ease: Ease.InQuad))
        .Chain(Tween.ScaleY(transform, 0.7f, 0.1f))  // Squash on impact
        .Chain(Tween.ScaleY(transform, 1.0f, 0.1f, ease: Ease.OutBack));  // Bounce back
}
```

## Performance Best Practices

### ✅ DO: Store Tweens You Need to Control

```csharp
Tween moveTween = Tween.Position(transform, targetPos, 1f);
// Later...
if (moveTween.isAlive) moveTween.Stop();
```

### ✅ DO: Use `target:` Parameter for Zero Allocations

```csharp
// ❌ Allocates (captures 'this')
Tween.Position(transform, targetPos, 1f)
    .OnComplete(() => OnMoveComplete());

// ✅ Zero allocations
Tween.Position(transform, targetPos, 1f)
    .OnComplete(target: this, (self, _) => self.OnMoveComplete());
```

### ✅ DO: Serialize TweenSettings for Designer Control

```csharp
[SerializeField] private TweenSettings jumpSettings;

void Jump()
{
    Tween.PositionY(transform, jumpHeight, jumpSettings);
}
```

### ❌ DON'T: Forget to Stop Tweens on Disable

```csharp
private Tween activeTween;

void OnDisable()
{
    activeTween.Stop();  // Always clean up!
}

// Or stop all tweens on this object:
void OnDisable()
{
    Tween.StopAll(target: gameObject);
}
```

### ❌ DON'T: Chain Callbacks for Sequences

```csharp
// ❌ Hard to read and maintain
Tween.Position(transform, pos1, 1f)
    .OnComplete(() => {
        Tween.Scale(transform, 1.5f, 0.5f)
            .OnComplete(() => {
                Tween.Color(sprite, Color.red, 0.3f);
            });
    });

// ✅ Use Sequence instead
Sequence.Create()
    .Chain(Tween.Position(transform, pos1, 1f))
    .Chain(Tween.Scale(transform, 1.5f, 0.5f))
    .Chain(Tween.Color(sprite, Color.red, 0.3f));
```

## Debugging

### Inspect Active Tweens

1. Enter Play Mode
2. Find `PrimeTweenManager` under DontDestroyOnLoad in Hierarchy
3. View inspector to see:
   - **Alive tweens count**
   - **Max alive tweens** (use this to set capacity)
   - **Pooled tweens capacity**

### Set Capacity Early

```csharp
// In your game bootstrap/initializer
void Awake()
{
    // If max alive tweens reaches 1000 during gameplay, set this to 1200
    PrimeTweenConfig.SetTweensCapacity(1200);

    // Optional: disable warnings for tweens on disabled objects
    PrimeTweenConfig.warnTweenOnDisabledTarget = false;
}
```

_In IshoBoy: See `Assets/Scripts/Utils/Initializers.cs` for global PrimeTween configuration._

### Enable Animation Curve Visualization

```csharp
[SerializeField] private TweenSettings settings;

void Start()
{
    // In Inspector, TweenSettings shows an AnimationCurve preview!
    // You can visually see the easing function
    Tween.Position(transform, targetPos, settings);
}
```

## Next Steps

Now that you understand the basics:

1. **[Why PrimeTween?](02-WHY-PRIMETWEEN.md)** — Performance comparisons with DOTween/LeanTween
2. **[API Reference](03-API-REFERENCE.md)** — Complete method documentation with examples
3. **[Common Patterns](04-COMMON-PATTERNS.md)** — Real-world recipes from IshoBoy codebase
4. **[Anti-Patterns](05-ANTI-PATTERNS.md)** — What NOT to do and why

## Quick Reference Card

```csharp
using PrimeTween;

// Basic animations
Tween.Position(transform, endValue, duration);
Tween.Scale(transform, endValue, duration);
Tween.Rotation(transform, endValue, duration);
Tween.Color(renderer, endValue, duration);

// Control
Tween t = Tween.Position(...);
t.Stop();         // Cancel
t.Complete();     // Jump to end
t.isPaused = true; // Pause/resume

// Callbacks (zero-alloc)
Tween.Position(transform, endValue, duration)
    .OnComplete(target: this, (self, _) => self.OnDone());

// Sequences
Sequence.Create()
    .Chain(Tween.Position(...))  // Play after previous
    .Group(Tween.Scale(...))      // Play with previous
    .ChainCallback(() => Debug.Log("Done"));

// Inspector-driven
[SerializeField] TweenSettings settings;
Tween.Position(transform, endValue, settings);

// Shake
Tween.ShakeCamera(Camera.main, strength: 0.5f, duration: 0.3f);

// Custom
Tween.Custom(0f, 1f, 1f, value => DoSomething(value));
```

---

**Pro Tip**: Look at `Assets/Scripts/Gameplay/Player/Actions/CarryComponent.cs` and
`Assets/Scripts/Production/Gameplay/MainMenu/MainMenu.cs` for battle-tested patterns from IshoBoy.
