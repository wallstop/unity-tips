# PrimeTween API Reference

> **Quick Navigation**: [Transform](#transform-animations) • [Color](#color-animations) •
> [UI](#ui-animations) • [Custom](#custom-tweens) • [Sequences](#sequences) • [Shake](#shake--punch)
> • [Control](#tween-control) • [Settings](#tween-settings)

## Transform Animations

### Position

#### `Tween.Position`

Animate a transform's position over time.

```csharp
// World position
Tween.Position(transform, endValue: new Vector3(10, 5, 0), duration: 1f);

// Local position
Tween.Position(transform, endValue: new Vector3(10, 5, 0), duration: 1f, useLocalValue: true);

// With easing
Tween.Position(transform, endValue: targetPos, duration: 2f, ease: Ease.OutQuad);

// From startValue to endValue
Tween.Position(
    transform,
    startValue: Vector3.zero,
    endValue: Vector3.up * 10,
    duration: 1.5f
);
```

#### `Tween.PositionX / Y / Z`

Animate individual axes (more performant than full `Position`).

```csharp
// Jump up
Tween.PositionY(transform, endValue: 5f, duration: 0.5f, ease: Ease.OutQuad);

// Slide left
Tween.PositionX(transform, endValue: -10f, duration: 1f);

// Move forward (local Z)
Tween.PositionZ(transform, endValue: 20f, duration: 2f, useLocalValue: true);
```

**Use Case**: UI elements sliding in from off-screen, platformer jumps.

---

### Rotation

#### `Tween.Rotation`

Animate rotation using either Euler angles or Quaternions.

```csharp
// Euler angles (Vector3)
Tween.Rotation(transform, endValue: new Vector3(0, 180, 0), duration: 1f);

// Quaternion
Tween.Rotation(transform, endValue: Quaternion.Euler(45, 90, 0), duration: 1f);

// Local rotation
Tween.Rotation(transform, endValue: new Vector3(0, 90, 0), duration: 1f, useLocalValue: true);

// Spin continuously (use cycles: -1)
Tween.Rotation(
    transform,
    startValue: Vector3.zero,
    endValue: new Vector3(0, 360, 0),
    new TweenSettings { duration = 2f, cycles = -1, ease = Ease.Linear }
);
```

**Pro Tip**: For continuous rotation (propellers, wheels), use `Ease.Linear` with `cycles: -1`.

---

### Scale

#### `Tween.Scale`

Animate uniform or non-uniform scale.

```csharp
// Uniform scale (float)
Tween.Scale(transform, endValue: 2f, duration: 0.5f);

// Non-uniform scale (Vector3)
Tween.Scale(transform, endValue: new Vector3(2, 0.5f, 1), duration: 1f);

// Pulse effect (cycle back and forth)
Tween.Scale(
    transform,
    startValue: 1f,
    endValue: 1.2f,
    new TweenSettings { duration = 0.5f, cycles = -1, cycleMode = CycleMode.Yoyo }
);
```

#### `Tween.ScaleX / Y / Z`

Animate individual scale axes.

```csharp
// Squash effect on landing
Tween.ScaleY(transform, endValue: 0.7f, duration: 0.1f);

// Stretch horizontally
Tween.ScaleX(transform, endValue: 1.5f, duration: 0.3f);
```

**Use Case**: Button press feedback, squash-and-stretch animations, size transitions.

---

## Color Animations

### `Tween.Color`

Animate color on `SpriteRenderer`, `Image`, `Material`, `CanvasGroup`, etc.

```csharp
// SpriteRenderer
Tween.Color(spriteRenderer, endValue: Color.red, duration: 1f);

// UI Image
Tween.Color(image, endValue: new Color(1, 0, 0, 0.5f), duration: 0.5f);

// Material (requires Renderer component)
Tween.Color(renderer, endValue: Color.blue, duration: 1f);

// Gradient effect using Custom
Color startColor = Color.red;
Color endColor = Color.blue;
Tween.Custom(0f, 1f, 1f, t => spriteRenderer.color = Color.Lerp(startColor, endColor, t));
```

### `Tween.Alpha`

Fade transparency (more performant than full `Color`).

```csharp
// Fade out SpriteRenderer
Tween.Alpha(spriteRenderer, endValue: 0f, duration: 1f);

// Fade in CanvasGroup
CanvasGroup canvasGroup = GetComponent<CanvasGroup>();
Tween.Alpha(canvasGroup, endValue: 1f, duration: 0.5f);

// Fade UI Image
Tween.Alpha(image, endValue: 0.5f, duration: 0.3f);
```

**Use Case**: UI panel fades, sprite fades, damage flash effects.

---

## UI Animations

### Canvas Group

```csharp
// Fade entire UI panel
CanvasGroup panel = GetComponent<CanvasGroup>();

// Fade in
Tween.Alpha(panel, endValue: 1f, duration: 0.5f)
    .OnComplete(() => panel.interactable = true);

// Fade out
Tween.Alpha(panel, endValue: 0f, duration: 0.3f)
    .OnComplete(() => panel.blocksRaycasts = false);
```

### RectTransform

```csharp
// Slide UI from off-screen
RectTransform rectTransform = GetComponent<RectTransform>();

// Anchor position
Tween.Position(rectTransform, endValue: Vector3.zero, duration: 0.5f, useLocalValue: true);

// Specific anchor (slide from right)
Tween.Custom(
    startValue: 1000f,
    endValue: 0f,
    duration: 0.5f,
    onValueChange: x => rectTransform.anchoredPosition = new Vector2(x, 0)
);
```

### UI Button Feedback

```csharp
public class ButtonFeedback : MonoBehaviour, IPointerDownHandler, IPointerUpHandler
{
    [SerializeField] private TweenSettings pressSettings;
    [SerializeField] private TweenSettings releaseSettings;

    public void OnPointerDown(PointerEventData eventData)
    {
        Tween.Scale(transform, 0.9f, pressSettings);
    }

    public void OnPointerUp(PointerEventData eventData)
    {
        Tween.Scale(transform, 1f, releaseSettings);
    }
}
```

**Use Case**: Button press feedback, menu transitions, tooltip animations.

---

## Custom Tweens

### `Tween.Custom`

Animate anything not covered by built-in methods.

```csharp
// Animate float
float value = 0f;
Tween.Custom(
    startValue: 0f,
    endValue: 100f,
    duration: 2f,
    onValueChange: v => value = v
);

// Animate audio volume
Tween.Custom(
    startValue: audioSource.volume,
    endValue: 0f,
    duration: 1f,
    onValueChange: v => audioSource.volume = v
);

// Animate material property
Tween.Custom(
    startValue: 0f,
    endValue: 1f,
    duration: 1f,
    onValueChange: v => material.SetFloat("_Cutoff", v)
);

// Animate TextMeshProUGUI number counter
int score = 0;
Tween.Custom(
    startValue: 0f,
    endValue: 1000f,
    duration: 2f,
    onValueChange: v => scoreText.text = Mathf.RoundToInt(v).ToString()
);
```

### Strongly-Typed Custom Tweens

Use `TweenSettings<T>` for better type safety:

```csharp
[SerializeField] private TweenSettings<float> volumeSettings;

void FadeOutAudio()
{
    Tween.Custom(
        startValue: audioSource.volume,
        endValue: 0f,
        volumeSettings,
        onValueChange: v => audioSource.volume = v
    );
}
```

**Use Case**: Audio fading, material properties, camera FOV, text counters, post-processing volumes.

---

## Sequences

### Creating Sequences

```csharp
// Basic sequence (one animation after another)
Sequence.Create()
    .Chain(Tween.Position(transform, Vector3.up * 5, 1f))
    .Chain(Tween.Scale(transform, 2f, 0.5f))
    .Chain(Tween.Color(spriteRenderer, Color.red, 0.3f));
```

### `.Chain()` — Sequential

Play animations one after another.

```csharp
Sequence.Create()
    .Chain(Tween.PositionY(transform, 10f, 1f))     // Happens first
    .Chain(Tween.PositionY(transform, 0f, 1f));     // Then this
```

### `.Group()` — Parallel

Play animations at the same time as the previous.

```csharp
Sequence.Create()
    .Chain(Tween.Position(transform, Vector3.right * 10, 2f))  // Move right
    .Group(Tween.Scale(transform, 2f, 2f))                     // Scale up at the same time
    .Group(Tween.Rotation(transform, new Vector3(0, 180, 0), 2f)); // Rotate at the same time
```

### `.ChainCallback()` / `.GroupCallback()`

Execute code at specific points.

```csharp
Sequence.Create()
    .Chain(Tween.Position(transform, targetPos, 1f))
    .ChainCallback(() => Debug.Log("Position reached!"))
    .Chain(Tween.Scale(transform, 2f, 0.5f))
    .ChainCallback(() => AudioManager.PlaySound("scale_up"));
```

### `.Insert()` — Absolute Timing

Insert animation at specific time offset.

```csharp
Sequence sequence = Sequence.Create()
    .Chain(Tween.Position(transform, Vector3.up * 5, 2f));

// Insert scale at 1 second (halfway through position tween)
sequence.Insert(atTime: 1f, Tween.Scale(transform, 1.5f, 0.5f));
```

### Sequence Control

```csharp
Sequence mySequence = Sequence.Create()
    .Chain(Tween.Position(transform, targetPos, 1f))
    .Chain(Tween.Scale(transform, 2f, 0.5f));

// Control the sequence
mySequence.isPaused = true;      // Pause entire sequence
mySequence.Stop();                // Stop and reset
mySequence.Complete();            // Jump to end
```

### Nested Sequences

```csharp
// Create sub-sequence for squash effect
Sequence squashSequence = Sequence.Create()
    .Chain(Tween.ScaleY(transform, 0.7f, 0.1f))
    .Chain(Tween.ScaleY(transform, 1.0f, 0.1f, ease: Ease.OutBack));

// Use in main sequence
Sequence.Create()
    .Chain(Tween.Position(transform, dropPoint, 1f))
    .Chain(squashSequence);  // Insert entire sub-sequence
```

### Loops & Yoyo

```csharp
// Loop entire sequence 3 times
Sequence.Create(cycles: 3)
    .Chain(Tween.Position(transform, Vector3.right * 10, 1f))
    .Chain(Tween.Position(transform, Vector3.zero, 1f));

// Yoyo (play forward then backward)
Sequence.Create(cycles: -1, cycleMode: CycleMode.Yoyo)
    .Chain(Tween.Scale(transform, 1.5f, 1f));
```

### Real-World Example: Item Drop with Squash

```csharp
void DropItem(Vector3 dropPosition)
{
    Sequence.Create()
        // Parallel horizontal and vertical motion
        .Group(Tween.PositionX(transform, dropPosition.x, 1f))
        .Group(Tween.Custom(
            startValue: transform.position.y,
            endValue: dropPosition.y,
            duration: 1f,
            ease: Ease.InQuad,  // Gravity-like fall
            onValueChange: y => {
                Vector3 pos = transform.position;
                pos.y = y;
                transform.position = pos;
            }
        ))
        // Squash on impact
        .Chain(Tween.ScaleY(transform, 0.7f, 0.1f))
        // Bounce back
        .Chain(Tween.ScaleY(transform, 1.0f, 0.15f, ease: Ease.OutBack))
        // Cleanup
        .OnComplete(target: this, (self, _) => self.OnDropComplete());
}
```

**Use Case**: Complex multi-step animations, cutscenes, UI transitions, character actions.

---

## Shake & Punch

### `Tween.ShakeCamera`

Add impact to camera movement.

```csharp
// Camera shake on explosion
Tween.ShakeCamera(
    camera: Camera.main,
    strength: 0.5f,
    duration: 0.3f,
    frequency: 10  // Higher = more jittery
);

// Subtle shake
Tween.ShakeCamera(Camera.main, 0.1f, 0.2f);
```

### `Tween.ShakeLocalPosition`

Shake a transform's position.

```csharp
// Shake UI element on error
Tween.ShakeLocalPosition(
    transform,
    strength: 10f,
    duration: 0.3f
);

// Shake with settings
[SerializeField] private ShakeSettings errorShake;

void ShowError()
{
    Tween.ShakeLocalPosition(transform, errorShake);
}
```

### `Tween.PunchScale`

Quick scale up and back down.

```csharp
// Hit effect
Tween.PunchScale(
    transform,
    strength: 0.3f,  // Scale up by 30%
    duration: 0.3f
);

// Combine with color
Sequence.Create()
    .Group(Tween.PunchScale(transform, 0.5f, 0.3f))
    .Group(Tween.Color(spriteRenderer, Color.red, 0.15f))
    .Chain(Tween.Color(spriteRenderer, Color.white, 0.15f));
```

### `Tween.PunchRotation`

Quick rotation shake.

```csharp
// Damage wobble
Tween.PunchRotation(
    transform,
    strength: new Vector3(0, 0, 15),  // Z-axis wobble
    duration: 0.4f
);
```

**Use Case**: Camera shake on explosions, UI error feedback, hit reactions, impact effects.

---

## Tween Control

### Storing & Controlling Tweens

```csharp
private Tween activeTween;

void StartAnimation()
{
    activeTween = Tween.Position(transform, targetPos, 1f);
}

void StopAnimation()
{
    if (activeTween.isAlive)
    {
        activeTween.Stop();
    }
}

void PauseAnimation()
{
    activeTween.isPaused = true;
}

void CompleteImmediately()
{
    activeTween.Complete();  // Jump to end value
}
```

### Tween Properties

```csharp
Tween myTween = Tween.Position(transform, targetPos, 1f);

// Read-only properties
bool isRunning = myTween.isAlive;        // Is tween still running?
float progress = myTween.progress;        // 0.0 to 1.0
float elapsed = myTween.elapsedTime;      // Seconds elapsed
float remaining = myTween.duration - myTween.elapsedTime;

// Writable properties
myTween.isPaused = true;                  // Pause/resume
myTween.timeScale = 0.5f;                 // Slow motion (0.5x speed)
```

### Stopping Multiple Tweens

```csharp
// Stop all tweens on a GameObject
Tween.StopAll(target: gameObject);

// Stop all tweens on a Transform
Tween.StopAll(target: transform);

// Using extension from IshoBoy (TweenExtensions.cs)
List<Tween> activeTweens = new();
activeTweens.Add(Tween.Position(...));
activeTweens.Add(Tween.Scale(...));

// Stop and clear all
activeTweens.ClearTweens();  // Custom extension

// Complete and clear all
activeTweens.CompleteTweens();  // Custom extension
```

### Chaining Multiple Controls

```csharp
Tween.Position(transform, targetPos, 1f)
    .OnUpdate(target: this, (self, tween) => {
        // Called every frame
        Debug.Log($"Progress: {tween.progress:P0}");
    })
    .OnComplete(target: this, (self, _) => {
        // Called when done
        self.OnAnimationComplete();
    });
```

---

## Tween Settings

### TweenSettings (Untyped)

```csharp
[SerializeField] private TweenSettings jumpSettings = new TweenSettings
{
    duration = 1f,
    ease = Ease.OutQuad,
    startDelay = 0.5f,
    cycles = 1,
    cycleMode = CycleMode.Restart
};

void Jump()
{
    Tween.PositionY(transform, jumpHeight, jumpSettings);
}
```

### TweenSettings\<T\> (Strongly-Typed)

```csharp
[SerializeField] private TweenSettings<float> volumeFadeSettings;
[SerializeField] private TweenSettings<Color> colorFadeSettings;

void FadeAudio()
{
    Tween.Custom(1f, 0f, volumeFadeSettings, v => audioSource.volume = v);
}

void FadeColor()
{
    Tween.Color(spriteRenderer, Color.red, colorFadeSettings);
}
```

### ShakeSettings

```csharp
[SerializeField] private ShakeSettings damageShake = new ShakeSettings
{
    duration = 0.3f,
    strength = 0.5f,
    vibrato = 10,  // Frequency of shakes
    randomness = 0.5f
};

void TakeDamage()
{
    Tween.ShakeCamera(Camera.main, damageShake);
}
```

### Settings Properties

All settings support:

```csharp
new TweenSettings
{
    duration = 1f,              // Animation length
    ease = Ease.OutQuad,        // Easing curve
    startDelay = 0f,            // Wait before starting
    endDelay = 0f,              // Wait after completing
    cycles = 1,                 // How many times to repeat (-1 = infinite)
    cycleMode = CycleMode.Restart,  // Restart, Yoyo, Incremental, Rewind
    useUnscaledTime = false     // Ignore Time.timeScale
};
```

### Inspector Benefits

When you serialize `TweenSettings`, designers can:

- ✅ Tweak duration/easing without code changes
- ✅ Visualize easing curves in Inspector
- ✅ Share settings across multiple scripts
- ✅ Create reusable animation profiles

---

## Callbacks

### OnComplete

```csharp
// Simple lambda (allocates closure)
Tween.Position(transform, targetPos, 1f)
    .OnComplete(() => Debug.Log("Done"));

// Zero-allocation (pass target explicitly)
Tween.Position(transform, targetPos, 1f)
    .OnComplete(target: this, (self, _) => self.OnMoveComplete());

// With Tween parameter
Tween.Scale(transform, 2f, 1f)
    .OnComplete(target: this, (self, tween) => {
        Debug.Log($"Final scale: {self.transform.localScale}");
    });
```

### OnUpdate

```csharp
// Called every frame
Tween.Custom(0f, 100f, 5f, v => Debug.Log(v))
    .OnUpdate(target: this, (self, tween) => {
        float progress = tween.progress;  // 0.0 to 1.0
        self.progressBar.fillAmount = progress;
    });
```

### Sequence Callbacks

```csharp
Sequence.Create()
    .Chain(Tween.Position(transform, pos1, 1f))
    .ChainCallback(target: this, self => self.OnFirstMoveComplete())
    .Chain(Tween.Scale(transform, 2f, 0.5f))
    .OnComplete(target: this, (self, _) => self.OnSequenceComplete());
```

---

## Delays

### Simple Delay

```csharp
// Execute callback after delay
Tween.Delay(duration: 2f, callback: () => Debug.Log("2 seconds passed"));

// Zero-allocation delay
Tween.Delay(2f, target: this, self => self.OnDelayComplete());
```

### Delay in Sequences

```csharp
Sequence.Create()
    .Chain(Tween.Position(transform, pos1, 1f))
    .Chain(Tween.Delay(0.5f))  // Wait 0.5 seconds
    .Chain(Tween.Scale(transform, 2f, 0.5f));

// Or use startDelay in settings
[SerializeField] private TweenSettings delayedSettings = new TweenSettings
{
    duration = 1f,
    startDelay = 2f  // Wait 2 seconds before animating
};
```

---

## Advanced Techniques

### Await Tweens in Coroutines

```csharp
IEnumerator AnimateCoroutine()
{
    yield return Tween.Position(transform, Vector3.up * 5, 1f).ToYieldInstruction();
    Debug.Log("Position complete");

    yield return Tween.Scale(transform, 2f, 0.5f).ToYieldInstruction();
    Debug.Log("Scale complete");
}
```

**Tip**: `ToYieldInstruction()` bridges tweens to Unity coroutines without creating `Task` state
machines, keeping GC pressure low.

> Need `async/await` semantics? Pair PrimeTween with [UniTask](https://github.com/Cysharp/UniTask)
> to await tweens without relying on `System.Threading.Tasks`.

### Dynamic Targets

```csharp
// Animate toward moving target
void Update()
{
    Vector3 targetPos = player.position + offset;
    Tween.Position(
        Camera.main.transform,
        targetPos,
        duration: Time.deltaTime * 5f  // Smooth follow
    );
}
```

### Easing Customization

```csharp
// Use AnimationCurve for custom easing
[SerializeField] private AnimationCurve customCurve;

Tween.Position(
    transform,
    targetPos,
    new TweenSettings { duration = 1f, ease = customCurve }
);
```

---

## Quick Reference Table

| Method              | Animates                      | Common Use                    |
| ------------------- | ----------------------------- | ----------------------------- |
| `Tween.Position`    | Transform position            | Move objects                  |
| `Tween.Scale`       | Transform scale               | Size transitions              |
| `Tween.Rotation`    | Transform rotation            | Spin objects                  |
| `Tween.Color`       | SpriteRenderer/Image/Material | Color transitions             |
| `Tween.Alpha`       | Transparency                  | Fade in/out                   |
| `Tween.Custom`      | Anything                      | Audio, FOV, custom properties |
| `Tween.Delay`       | Nothing (callback only)       | Timed events                  |
| `Tween.ShakeCamera` | Camera position               | Impact effects                |
| `Tween.PunchScale`  | Scale (temporary)             | Hit reactions                 |
| `Sequence.Create`   | Multiple tweens               | Complex animations            |

---

## Next Steps

- **[Common Patterns](04-common-patterns.md)** — Battle-tested recipes from IshoBoy
- **[Anti-Patterns](05-anti-patterns.md)** — Common mistakes and how to avoid them
- **[Getting Started](01-getting-started.md)** — If you haven't read this yet

---

**Pro Tip**: The PrimeTween API is designed to be discoverable. Just type `Tween.` in your IDE and
explore the autocomplete suggestions!
