# PrimeTween Anti-Patterns & Pitfalls

> **Learn from Mistakes**: These are real issues developers encounter. Avoid them!

## Table of Contents
- [Memory & Performance](#memory--performance)
- [Tween Management](#tween-management)
- [Sequences](#sequences)
- [Callbacks](#callbacks)
- [Inspector & Serialization](#inspector--serialization)
- [Common Bugs](#common-bugs)

---

## Memory & Performance

### ❌ DON'T: Capture `this` in Lambda Callbacks

**Problem**: Implicitly capturing `this` in lambdas allocates closures, defeating PrimeTween's zero-allocation promise.

```csharp
// ❌ BAD: Allocates closure
Tween.Position(transform, targetPos, 1f)
    .OnComplete(() => OnMoveComplete());

// ❌ BAD: Captures 'this' and 'score'
int score = 100;
Tween.Scale(transform, 2f, 1f)
    .OnComplete(() => {
        this.score = score;  // Allocation!
        UpdateUI();
    });
```

**Solution**: Pass `target` explicitly for zero allocations.

```csharp
// ✅ GOOD: Zero allocations
Tween.Position(transform, targetPos, 1f)
    .OnComplete(target: this, (self, _) => self.OnMoveComplete());

// ✅ GOOD: Pass data via target parameter
Tween.Scale(transform, 2f, 1f)
    .OnComplete(target: this, (self, tween) => {
        self.score = 100;
        self.UpdateUI();
    });
```

**Impact**: On hot paths (e.g., 100 tweens per second), this can save 10-50KB of GC allocations per second.

---

### ❌ DON'T: Use `await` in Hot Paths

**Problem**: `await tween` allocates a `Task`. It's fine for one-off cutscenes, but not for frequent gameplay animations.

```csharp
// ❌ BAD: Allocates Task every frame
async void Update()
{
    await Tween.Position(transform, targetPos, Time.deltaTime);
}

// ❌ BAD: Allocates in gameplay loop
async void OnButtonClick()
{
    await Tween.Scale(transform, 1.2f, 0.2f);
    await Tween.Scale(transform, 1.0f, 0.2f);
}
```

**Solution**: Use `Sequence` for chained animations, or callbacks for single tweens.

```csharp
// ✅ GOOD: Zero allocations with Sequence
void OnButtonClick()
{
    Sequence.Create()
        .Chain(Tween.Scale(transform, 1.2f, 0.2f))
        .Chain(Tween.Scale(transform, 1.0f, 0.2f));
}

// ✅ GOOD: Use callback if you need to execute code after
Tween.Position(transform, targetPos, 1f)
    .OnComplete(target: this, (self, _) => self.DoNextThing());
```

**When `await` is OK**:
- One-time cutscenes or menu transitions
- Editor tools or non-gameplay code
- Prototyping (optimize later)

---

### ❌ DON'T: Forget to Set Tween Capacity

**Problem**: If you exceed PrimeTween's internal capacity, it allocates new arrays mid-game, causing GC spikes.

```csharp
// ❌ BAD: Using default capacity (might be 100-200)
// If you spawn 500 tweens, PrimeTween will allocate!
```

**Solution**: Monitor max alive tweens in `PrimeTweenManager` inspector during stressful scenes, then set capacity in bootstrap.

```csharp
// ✅ GOOD: In game startup/initializer
void Awake()
{
    // If max alive tweens reaches 800 during gameplay, set to 1000
    PrimeTweenConfig.SetTweensCapacity(1000);
}
```

**IshoBoy Example**: `Assets/Scripts/Utils/Initializers.cs`
```csharp
PrimeTweenConfig.SetTweensCapacity(1_000);
```

**How to Check**:
1. Enter Play Mode
2. Find `PrimeTweenManager` in Hierarchy (under DontDestroyOnLoad)
3. Observe "Max alive tweens" during intense scenes
4. Set capacity to 20-30% higher than max observed

---

### ❌ DON'T: Create Tweens Every Frame Without Control

**Problem**: Creating a new tween every `Update()` without stopping previous ones leaks tweens.

```csharp
// ❌ BAD: Creates 60+ tweens per second (camera has 60 overlapping tweens!)
void Update()
{
    Tween.Position(Camera.main.transform, player.position, 1f);
}
```

**Solution**: Store the tween and replace it, or use short durations.

```csharp
// ✅ GOOD: Short duration creates smooth follow
void LateUpdate()
{
    Tween.Position(
        Camera.main.transform,
        player.position + offset,
        duration: Time.deltaTime * 5f  // Completes in ~5 frames
    );
}

// ✅ ALSO GOOD: Store and replace
private Tween cameraTween;

void Update()
{
    cameraTween.Stop();
    cameraTween = Tween.Position(Camera.main.transform, player.position, 1f);
}
```

---

## Tween Management

### ❌ DON'T: Forget to Stop Tweens on Disable/Destroy

**Problem**: Tweens continue running even after `GameObject` is disabled or destroyed, causing null references or unexpected behavior.

```csharp
// ❌ BAD: Tween keeps running after disable
public class Enemy : MonoBehaviour
{
    void Start()
    {
        Tween.Position(transform, targetPos, 5f)
            .OnComplete(() => Debug.Log("Reached target")); // May fire after enemy is destroyed!
    }

    // No OnDisable cleanup
}
```

**Solution**: Always clean up tweens in `OnDisable` or `OnDestroy`.

```csharp
// ✅ GOOD: Cleanup on disable
public class Enemy : MonoBehaviour
{
    private Tween moveTween;

    void Start()
    {
        moveTween = Tween.Position(transform, targetPos, 5f);
    }

    void OnDisable()
    {
        moveTween.Stop();
    }
}

// ✅ ALSO GOOD: Stop all tweens on this GameObject
void OnDisable()
{
    Tween.StopAll(target: gameObject);
}
```

**IshoBoy Pattern**: Use `List<Tween>` with custom extensions.
```csharp
private List<Tween> activeTweens = new();

void AnimateSomething()
{
    activeTweens.Add(Tween.Position(transform, targetPos, 1f));
    activeTweens.Add(Tween.Scale(transform, 2f, 1f));
}

void OnDisable()
{
    activeTweens.ClearTweens(); // Extension from TweenExtensions.cs
}
```

---

### ❌ DON'T: Reuse Tween Structs

**Problem**: PrimeTween's `Tween` is single-use. You can't "replay" a tween by storing it.

```csharp
// ❌ BAD: This doesn't work as expected
private Tween jumpTween;

void Start()
{
    jumpTween = Tween.PositionY(transform, 5f, 1f);
}

void Jump()
{
    // This does nothing if the tween already completed!
    jumpTween.isPaused = false; // ❌ Won't restart
}
```

**Solution**: Create a new tween each time.

```csharp
// ✅ GOOD: Create new tween on each call
[SerializeField] private TweenSettings jumpSettings;

void Jump()
{
    Tween.PositionY(transform, 5f, jumpSettings);
}
```

**Why**: Tweens are lightweight handles, not reusable animation clips. Creating a new tween is cheap (microseconds).

---

### ❌ DON'T: Mix Tweens on Same Property

**Problem**: Starting a new tween on the same property (e.g., position) while another is running causes conflicts.

```csharp
// ❌ BAD: Two tweens fighting over position
void Start()
{
    Tween.Position(transform, Vector3.up * 5, 2f);
    Tween.Position(transform, Vector3.right * 5, 2f); // Conflicts!
}
```

**What Happens**: Both tweens run simultaneously, creating unpredictable movement.

**Solution 1**: Stop the previous tween before starting a new one.
```csharp
// ✅ GOOD: Replace previous tween
private Tween moveTween;

void MoveTo(Vector3 target)
{
    moveTween.Stop();
    moveTween = Tween.Position(transform, target, 1f);
}
```

**Solution 2**: Use a sequence if both movements are intentional.
```csharp
// ✅ GOOD: Sequential movement
Sequence.Create()
    .Chain(Tween.Position(transform, Vector3.up * 5, 2f))
    .Chain(Tween.Position(transform, Vector3.right * 5, 2f));
```

**Solution 3**: Animate different axes separately.
```csharp
// ✅ GOOD: Independent axes
Tween.PositionY(transform, 5f, 2f);   // Vertical
Tween.PositionX(transform, 5f, 2f);   // Horizontal
```

---

## Sequences

### ❌ DON'T: Chain Callbacks Instead of Using Sequences

**Problem**: Nesting `.OnComplete` callbacks creates "callback hell" — hard to read, hard to maintain.

```csharp
// ❌ BAD: Callback pyramid of doom
Tween.Position(transform, pos1, 1f)
    .OnComplete(() => {
        Tween.Scale(transform, 2f, 0.5f)
            .OnComplete(() => {
                Tween.Color(renderer, Color.red, 0.3f)
                    .OnComplete(() => {
                        Tween.Position(transform, pos2, 1f)
                            .OnComplete(() => {
                                Debug.Log("Finally done!");
                            });
                    });
            });
    });
```

**Solution**: Use `Sequence.Chain()` for linear flows.

```csharp
// ✅ GOOD: Readable sequence
Sequence.Create()
    .Chain(Tween.Position(transform, pos1, 1f))
    .Chain(Tween.Scale(transform, 2f, 0.5f))
    .Chain(Tween.Color(renderer, Color.red, 0.3f))
    .Chain(Tween.Position(transform, pos2, 1f))
    .OnComplete(() => Debug.Log("Done!"));
```

**Benefits**:
- Easier to read/modify
- Can pause/stop entire sequence
- Can adjust timing with `.Insert()`

---

### ❌ DON'T: Forget `.Chain()` Before Adding to Sequence

**Problem**: Forgetting `.Chain()` or `.Group()` causes tweens to not be added to the sequence.

```csharp
// ❌ BAD: Second tween isn't part of sequence
Sequence seq = Sequence.Create()
    .Chain(Tween.Position(transform, pos1, 1f));

Tween.Scale(transform, 2f, 1f); // ❌ Not added! Runs independently
```

**Solution**: Always use `.Chain()` or `.Group()`.

```csharp
// ✅ GOOD: Explicit chaining
Sequence.Create()
    .Chain(Tween.Position(transform, pos1, 1f))
    .Chain(Tween.Scale(transform, 2f, 1f));
```

---

### ❌ DON'T: Ignore Sequence Return Value

**Problem**: Not storing the `Sequence` means you can't control it later.

```csharp
// ❌ BAD: Can't stop or check status
void PlayAnimation()
{
    Sequence.Create()
        .Chain(Tween.Position(transform, pos1, 1f))
        .Chain(Tween.Scale(transform, 2f, 1f));
}

// Later: How do I stop it?
```

**Solution**: Store sequence if you need control.

```csharp
// ✅ GOOD: Can control sequence
private Sequence animationSequence;

void PlayAnimation()
{
    animationSequence = Sequence.Create()
        .Chain(Tween.Position(transform, pos1, 1f))
        .Chain(Tween.Scale(transform, 2f, 1f));
}

void StopAnimation()
{
    animationSequence.Stop();
}
```

---

## Callbacks

### ❌ DON'T: Access Destroyed Objects in Callbacks

**Problem**: Callbacks may fire after `GameObject` is destroyed, causing null reference exceptions.

```csharp
// ❌ BAD: May throw NullReferenceException
void Start()
{
    Tween.Position(transform, targetPos, 5f)
        .OnComplete(() => {
            // If this GameObject was destroyed during the tween...
            Debug.Log(gameObject.name); // NullReferenceException!
        });
}
```

**Solution 1**: Always null-check in callbacks.
```csharp
// ✅ GOOD: Safe null check
Tween.Position(transform, targetPos, 5f)
    .OnComplete(() => {
        if (this == null) return;
        Debug.Log(gameObject.name);
    });
```

**Solution 2**: Stop tweens on disable (preferred).
```csharp
// ✅ BETTER: Prevent callback from firing
private Tween moveTween;

void Start()
{
    moveTween = Tween.Position(transform, targetPos, 5f)
        .OnComplete(() => Debug.Log("Done"));
}

void OnDisable()
{
    moveTween.Stop(); // Cancels callback
}
```

---

### ❌ DON'T: Use Callbacks for Timing (Use Delays Instead)

**Problem**: Using `.OnComplete()` to schedule future events is clunky.

```csharp
// ❌ BAD: Abusing OnComplete for timing
Tween.Position(transform, pos1, 1f)
    .OnComplete(() => {
        // Wait 2 seconds before next action
        StartCoroutine(WaitAndAct());
    });

IEnumerator WaitAndAct()
{
    yield return new WaitForSeconds(2f);
    DoSomething();
}
```

**Solution**: Use `Tween.Delay()` or `Sequence.Chain()`.

```csharp
// ✅ GOOD: Use Tween.Delay
Sequence.Create()
    .Chain(Tween.Position(transform, pos1, 1f))
    .Chain(Tween.Delay(2f))
    .ChainCallback(() => DoSomething());

// ✅ ALSO GOOD: Direct delay
Tween.Delay(2f, target: this, self => self.DoSomething());
```

---

## Inspector & Serialization

### ❌ DON'T: Hardcode Animation Values

**Problem**: Hardcoded durations/easing force recompilation for every tweak.

```csharp
// ❌ BAD: Requires code changes for tweaking
void Jump()
{
    Tween.PositionY(transform, 5f, duration: 0.8f, ease: Ease.OutQuad);
}
```

**Solution**: Serialize `TweenSettings` for designer control.

```csharp
// ✅ GOOD: Designer can tweak in Inspector
[SerializeField] private TweenSettings jumpSettings;

void Jump()
{
    Tween.PositionY(transform, 5f, jumpSettings);
}
```

**Benefits**:
- No recompilation needed
- Designers can iterate independently
- Easy A/B testing of animation feel

---

### ❌ DON'T: Create TweenSettings at Runtime

**Problem**: `new TweenSettings { ... }` in hot paths can allocate (though PrimeTween tries to optimize this).

```csharp
// ❌ AVOID: Creating settings at runtime
void Update()
{
    Tween.Position(
        transform,
        targetPos,
        new TweenSettings { duration = 1f, ease = Ease.Linear } // Potential allocation
    );
}
```

**Solution**: Serialize settings or reuse static instances.

```csharp
// ✅ GOOD: Serialize once
[SerializeField] private TweenSettings moveSettings;

void Update()
{
    Tween.Position(transform, targetPos, moveSettings);
}

// ✅ ALSO GOOD: Static/cached settings
private static readonly TweenSettings cachedSettings = new() { duration = 1f, ease = Ease.Linear };

void Update()
{
    Tween.Position(transform, targetPos, cachedSettings);
}
```

---

## Common Bugs

### ❌ DON'T: Animate Destroyed Transforms

**Problem**: Tweening a transform after its `GameObject` is destroyed causes errors.

```csharp
// ❌ BAD: Tween runs after Destroy()
void DestroyEnemy()
{
    Tween.Scale(transform, 0f, 1f); // Starts tween
    Destroy(gameObject); // Destroys immediately!
    // Tween tries to access destroyed transform → Error
}
```

**Solution**: Use `.OnComplete()` to destroy after animation.

```csharp
// ✅ GOOD: Destroy after tween completes
void DestroyEnemy()
{
    Tween.Scale(transform, 0f, 1f)
        .OnComplete(() => Destroy(gameObject));
}
```

---

### ❌ DON'T: Use Wrong Ease for Effect

**Problem**: Easing curves drastically change animation feel. Wrong curve = wrong feel.

```csharp
// ❌ BAD: Linear ease makes jump feel robotic
Tween.PositionY(transform, jumpHeight, duration: 1f, ease: Ease.Linear);

// ❌ BAD: InOut ease makes drop feel floaty
Tween.PositionY(transform, groundY, duration: 1f, ease: Ease.InOutSine);
```

**Solution**: Match easing to physical behavior.

```csharp
// ✅ GOOD: OutQuad makes jump feel natural (decelerates at peak)
Tween.PositionY(transform, jumpHeight, duration: 1f, ease: Ease.OutQuad);

// ✅ GOOD: InQuad makes drop feel gravity-like (accelerates)
Tween.PositionY(transform, groundY, duration: 1f, ease: Ease.InQuad);
```

**Easing Cheat Sheet**:
- **UI buttons**: `Ease.OutBack` (overshoot)
- **Jumps (up)**: `Ease.OutQuad` (decelerate at peak)
- **Drops (down)**: `Ease.InQuad` (accelerate like gravity)
- **Smooth in/out**: `Ease.InOutSine`
- **Bouncy**: `Ease.OutBounce` or `Ease.OutElastic`
- **Constant speed**: `Ease.Linear`

[See all easing functions at easings.net](https://easings.net/)

---

### ❌ DON'T: Tween to Current Value

**Problem**: Tweening to the current value wastes resources and may cause confusion.

```csharp
// ❌ BAD: Already at Vector3.zero
transform.position = Vector3.zero;
Tween.Position(transform, Vector3.zero, 1f); // Does nothing useful
```

**Solution**: Check before tweening, or always tween to different value.

```csharp
// ✅ GOOD: Only tween if needed
if (transform.position != targetPos)
{
    Tween.Position(transform, targetPos, 1f);
}

// ✅ ALSO GOOD: Set start value explicitly
Tween.Position(
    transform,
    startValue: Vector3.zero,
    endValue: Vector3.up * 5,
    duration: 1f
);
```

---

### ❌ DON'T: Ignore `useLocalValue` for Child Transforms

**Problem**: Forgetting `useLocalValue: true` when animating children causes world-space confusion.

```csharp
// ❌ BAD: Animating child in world space (probably not what you want)
Transform child = transform.GetChild(0);
Tween.Position(child, new Vector3(5, 0, 0), 1f); // World position!
```

**Solution**: Use `useLocalValue: true` for local-space animations.

```csharp
// ✅ GOOD: Animate in local space
Transform child = transform.GetChild(0);
Tween.Position(child, new Vector3(5, 0, 0), duration: 1f, useLocalValue: true);
```

**Rule of Thumb**: If the transform has a parent, use `useLocalValue: true`.

---

### ❌ DON'T: Forget `Time.timeScale` Considerations

**Problem**: Tweens pause when `Time.timeScale = 0` (e.g., game paused), unless using `useUnscaledTime`.

```csharp
// ❌ BAD: UI animation pauses when game is paused
void ShowPauseMenu()
{
    Time.timeScale = 0; // Pause game
    Tween.Alpha(pausePanel, 1f, 0.5f); // ❌ Won't animate! (Time.timeScale = 0)
}
```

**Solution**: Use `useUnscaledTime: true` for UI that should animate during pause.

```csharp
// ✅ GOOD: UI animates even when game is paused
void ShowPauseMenu()
{
    Time.timeScale = 0;
    Tween.Alpha(
        pausePanel,
        endValue: 1f,
        duration: 0.5f,
        useUnscaledTime: true // Ignores Time.timeScale
    );
}

// ✅ ALSO GOOD: Use TweenSettings
[SerializeField] private TweenSettings uiSettings = new()
{
    duration = 0.5f,
    useUnscaledTime = true
};
```

---

### ❌ DON'T: Spam Shake Effects

**Problem**: Overlapping shakes feel chaotic and can make players nauseous.

```csharp
// ❌ BAD: Every hit triggers camera shake (can stack dozens)
void OnEnemyHit()
{
    Tween.ShakeCamera(Camera.main, strength: 0.5f, duration: 0.5f);
    // If player hits 10 enemies in 0.5 seconds → 10 overlapping shakes!
}
```

**Solution**: Limit shake frequency with cooldown or stop previous shake.

```csharp
// ✅ GOOD: Cooldown prevents spam
private float lastShakeTime;
private const float shakeCooldown = 0.2f;

void OnEnemyHit()
{
    if (Time.time - lastShakeTime < shakeCooldown) return;

    Tween.ShakeCamera(Camera.main, strength: 0.5f, duration: 0.3f);
    lastShakeTime = Time.time;
}

// ✅ ALSO GOOD: Stop previous shake
private Tween currentShake;

void OnEnemyHit()
{
    currentShake.Stop();
    currentShake = Tween.ShakeCamera(Camera.main, strength: 0.5f, duration: 0.3f);
}
```

---

## Summary Checklist

**Before you ship, verify:**

✅ All hot-path callbacks use `target:` parameter (zero allocations)
✅ Tween capacity set based on "Max alive tweens" from `PrimeTweenManager`
✅ All scripts clean up tweens in `OnDisable()`
✅ No `await tween` in gameplay loops
✅ Complex animations use `Sequence`, not nested callbacks
✅ `TweenSettings` serialized for designer control
✅ Camera shakes have cooldowns or stop previous shake
✅ UI animations use `useUnscaledTime: true` during pause
✅ Pooled objects stop tweens before returning to pool
✅ No tweens started every frame without control

---

## Next Steps

- **[Common Patterns](04-COMMON-PATTERNS.md)** — See the RIGHT way to do things
- **[API Reference](03-API-REFERENCE.md)** — Complete method documentation
- **[Getting Started](01-GETTING-STARTED.md)** — Refresh the basics

---

**Remember**: PrimeTween's power comes from zero allocations. Don't throw that away with sloppy callback usage!
