# Common PrimeTween Patterns

> **Battle-Tested Recipes from IshoBoy**: These patterns are actively used in production. Copy them
> freely!

## Table of Contents

- [UI Patterns](#ui-patterns)
- [Gameplay Patterns](#gameplay-patterns)
- [Camera Patterns](#camera-patterns)
- [Audio Patterns](#audio-patterns)
- [VFX Patterns](#vfx-patterns)
- [Utility Patterns](#utility-patterns)

---

## UI Patterns

### Button Pulse on Hover

**Problem**: Buttons need immediate visual feedback when hovered.

**Solution**: Scale up on mouse enter, scale back on exit.

```csharp
using UnityEngine;
using UnityEngine.EventSystems;
using PrimeTween;

public class ButtonHoverEffect : MonoBehaviour, IPointerEnterHandler, IPointerExitHandler
{
    [SerializeField] private float hoverScale = 1.2f;
    [SerializeField] private TweenSettings hoverSettings;

    private Tween currentTween;

    public void OnPointerEnter(PointerEventData eventData)
    {
        currentTween.Stop();
        currentTween = Tween.Scale(transform, hoverScale, hoverSettings);
    }

    public void OnPointerExit(PointerEventData eventData)
    {
        currentTween.Stop();
        currentTween = Tween.Scale(transform, 1f, hoverSettings);
    }
}
```

**IshoBoy Example**: `MainMenu.cs:401` uses this pattern for menu buttons:

```csharp
// From MainMenu.cs - Button pulse effect
private void OnEnter(Button button, BaseEventData _)
{
    if (_buttonTweens.TryGetValue(button, out Tween existingTween))
    {
        existingTween.Stop();
    }

    _buttonTweens[button] = Tween
        .Scale(button.transform, _maxScale, _pulseSettings)
        .OnComplete(ScaleIn);

    void ScaleIn()
    {
        if (button == null) return;

        _buttonTweens[button] = Tween
            .Scale(button.transform, _minScale, _pulseSettings)
            .OnComplete(ScaleOut);
    }
}
```

---

### Fade Panel In/Out

**Problem**: UI panels need smooth transitions when showing/hiding.

**Solution**: Animate `CanvasGroup.alpha` and enable/disable interactivity.

```csharp
using UnityEngine;
using PrimeTween;

public class UIPanel : MonoBehaviour
{
    [SerializeField] private CanvasGroup canvasGroup;
    [SerializeField] private float fadeDuration = 0.5f;

    private Tween fadeTween;

    public void Show()
    {
        gameObject.SetActive(true);
        canvasGroup.alpha = 0;
        canvasGroup.interactable = false;
        canvasGroup.blocksRaycasts = false;

        fadeTween = Tween.Alpha(canvasGroup, endValue: 1f, duration: fadeDuration)
            .OnComplete(target: this, (self, _) => {
                self.canvasGroup.interactable = true;
                self.canvasGroup.blocksRaycasts = true;
            });
    }

    public void Hide()
    {
        canvasGroup.interactable = false;
        canvasGroup.blocksRaycasts = false;

        fadeTween = Tween.Alpha(canvasGroup, endValue: 0f, duration: fadeDuration)
            .OnComplete(target: this, (self, _) => self.gameObject.SetActive(false));
    }

    private void OnDisable()
    {
        fadeTween.Stop();
    }
}
```

**Variants**:

- Slide + Fade: Add `Tween.Position` in a `Sequence.Group()`
- Scale + Fade: Add `Tween.Scale` for "pop-in" effect

---

### Staggered List Reveal

**Problem**: Revealing a list of items all at once looks jarring.

**Solution**: Use `Sequence.Insert()` with incremental delays.

```csharp
using UnityEngine;
using PrimeTween;
using System.Collections.Generic;

public class StaggeredListReveal : MonoBehaviour
{
    [SerializeField] private List<RectTransform> items;
    [SerializeField] private float staggerDelay = 0.1f;
    [SerializeField] private TweenSettings revealSettings;

    public void RevealAll()
    {
        Sequence sequence = Sequence.Create();

        for (int i = 0; i < items.Count; i++)
        {
            RectTransform item = items[i];
            item.localScale = Vector3.zero;

            // Insert each item's reveal at staggered time
            sequence.Insert(
                atTime: i * staggerDelay,
                Tween.Scale(item, endValue: 1f, revealSettings)
            );
        }
    }
}
```

**Alternative (Chain + Group)**:

```csharp
Sequence sequence = Sequence.Create();

foreach (RectTransform item in items)
{
    item.localScale = Vector3.zero;
    sequence.Chain(Tween.Delay(staggerDelay))
            .Group(Tween.Scale(item, 1f, revealSettings));
}
```

---

### Number Counter Animation

**Problem**: Score/currency changes need to count up smoothly.

**Solution**: Use `Tween.Custom` to interpolate numbers.

```csharp
using UnityEngine;
using PrimeTween;
using TMPro;

public class NumberCounter : MonoBehaviour
{
    [SerializeField] private TextMeshProUGUI text;
    [SerializeField] private float duration = 1f;

    private Tween counterTween;

    public void AnimateToValue(int targetValue)
    {
        int currentValue = int.TryParse(text.text, out int parsed) ? parsed : 0;

        counterTween.Stop();
        counterTween = Tween.Custom(
            startValue: currentValue,
            endValue: targetValue,
            duration: duration,
            ease: Ease.OutQuad,
            onValueChange: value => text.text = Mathf.RoundToInt(value).ToString()
        );
    }

    private void OnDisable()
    {
        counterTween.Stop();
    }
}
```

**Variants**:

- Add commas: `value.ToString("N0")`
- Show decimals: `value.ToString("F2")`
- Punch scale on complete for emphasis

---

## Gameplay Patterns

### Item Drop with Squash & Stretch

**Problem**: Dropping items needs to feel weighty and satisfying.

**Solution**: Combine horizontal/vertical motion with squash/stretch, fire events mid-flight.

```csharp
using UnityEngine;
using PrimeTween;

public class ItemDrop : MonoBehaviour
{
    [Header("Drop Settings")]
    [SerializeField] private TweenSettings horizontalSettings;
    [SerializeField] private TweenSettings verticalSettings;

    [Header("Squash Settings")]
    [SerializeField] private float squashScaleY = 0.7f;
    [SerializeField] private float stretchScaleX = 1.3f;
    [SerializeField] private float squashDuration = 0.1f;

    private Sequence dropSequence;

    public void DropToPosition(Transform visual, Vector3 dropPoint)
    {
        Vector3 startPos = visual.position;

        dropSequence = Sequence.Create()
            // Parallel horizontal and vertical motion
            .Group(Tween.PositionX(visual, dropPoint.x, horizontalSettings))
            .Group(Tween.Custom(
                startValue: startPos.y,
                endValue: dropPoint.y,
                verticalSettings,
                value => {
                    Vector3 pos = visual.position;
                    pos.y = value;
                    visual.position = pos;
                }
            ))
            // Squash on impact
            .Chain(Tween.ScaleY(visual, squashScaleY, squashDuration))
            .Group(Tween.ScaleX(visual, stretchScaleX, squashDuration))
            // Bounce back
            .Chain(Tween.ScaleY(visual, 1f, squashDuration, ease: Ease.OutBack))
            .Group(Tween.ScaleX(visual, 1f, squashDuration, ease: Ease.OutBack))
            // Cleanup
            .OnComplete(target: this, (self, _) => self.OnDropComplete());
    }

    private void OnDropComplete()
    {
        Debug.Log("Item landed!");
    }

    private void OnDisable()
    {
        dropSequence.Stop();
    }
}
```

**IshoBoy Example**: `CarryComponent.cs:730-782` implements this pattern:

```csharp
// From CarryComponent.cs - Complex drop with squash/stretch
Sequence.Create()
    .Group(Tween.Delay(
        movementDuration * _onCompleteTriggerPercent,
        () => {
            // Fire landed event mid-flight
            PropLandedMessage landed = new(...);
            landed.EmitGameObjectBroadcast(propOwner.gameObject);
        }
    ))
    .Group(Tween.Custom(
        initial.y,
        dropPoint.y,
        yMovementSettings,
        value => {
            Vector3 targetPosition = visual.transform.position;
            targetPosition.y = value;
            visual.transform.position = targetPosition;
        }
    ))
    .Group(Tween.ScaleY(visual.transform, squash.yMax, yMovementSettings))
    .Chain(Sequence.Create(
        Tween.ScaleY(visual.transform, squash.yMin, squash.overTime)
    )
    .Group(Tween.ScaleX(visual.transform, squash.xMax, squash.overTime))
    .OnComplete(() => visual.transform.localScale = Vector3.one));
```

---

### Damage Flash Effect

**Problem**: Player needs immediate visual feedback when taking damage.

**Solution**: Flash color to red and back, optionally shake.

```csharp
using UnityEngine;
using PrimeTween;

public class DamageFlash : MonoBehaviour
{
    [SerializeField] private SpriteRenderer spriteRenderer;
    [SerializeField] private float flashDuration = 0.2f;
    [SerializeField] private Color flashColor = Color.red;
    [SerializeField] private ShakeSettings shakeSettings;

    private Color originalColor;
    private Sequence flashSequence;

    private void Awake()
    {
        originalColor = spriteRenderer.color;
    }

    public void Flash()
    {
        flashSequence.Stop();

        flashSequence = Sequence.Create()
            .Group(Tween.Color(spriteRenderer, flashColor, flashDuration / 2))
            .Group(Tween.ShakeLocalPosition(transform, shakeSettings))
            .Chain(Tween.Color(spriteRenderer, originalColor, flashDuration / 2));
    }

    private void OnDisable()
    {
        flashSequence.Stop();
        spriteRenderer.color = originalColor;
    }
}
```

**Variants**:

- Punch scale instead of shake
- Flash multiple times in sequence
- Add invulnerability flicker (cycle alpha)

---

### Pickup Magnet Effect

**Problem**: Items need to smoothly fly toward the player when collected.

**Solution**: Animate position toward moving target, destroy on complete.

```csharp
using UnityEngine;
using PrimeTween;

public class PickupMagnet : MonoBehaviour
{
    [SerializeField] private float magnetDuration = 0.5f;
    [SerializeField] private Ease magnetEase = Ease.InQuad;

    private Tween magnetTween;

    public void MagnetToPlayer(Transform player, System.Action onCollected)
    {
        magnetTween = Tween.Position(
            transform,
            player.position,
            duration: magnetDuration,
            ease: magnetEase
        ).OnComplete(() => {
            onCollected?.Invoke();
            Destroy(gameObject);
        });
    }

    private void OnDisable()
    {
        magnetTween.Stop();
    }
}
```

**Advanced**: For a moving target, chain short tweens instead of updating every frame:

```csharp
public class PickupMagnetFollowing : MonoBehaviour
{
    [SerializeField] private float tweenDuration = 0.15f;
    [SerializeField] private Ease magnetEase = Ease.InQuad;

    private Transform player;
    private Tween magnetTween;

    public void StartMagnet(Transform target, System.Action onCollected)
    {
        player = target;
        ChainNextTween(onCollected);
    }

    private void ChainNextTween(System.Action onCollected)
    {
        float distance = Vector3.Distance(transform.position, player.position);

        // Close enough - collect it
        if (distance < 0.1f)
        {
            onCollected?.Invoke();
            Destroy(gameObject);
            return;
        }

        // Chain to next position, then re-evaluate
        magnetTween = Tween.Position(
            transform,
            player.position,
            duration: tweenDuration,
            ease: magnetEase
        ).OnComplete(() => ChainNextTween(onCollected));
    }

    private void OnDisable()
    {
        magnetTween.Stop();
    }
}
```

---

## Camera Patterns

### Smooth Camera Follow

**Problem**: Camera needs to follow player smoothly without jittering.

**Solution**: Use `Tween.Position` each frame with short duration (damping effect).

```csharp
using UnityEngine;
using PrimeTween;

public class SmoothCameraFollow : MonoBehaviour
{
    [SerializeField] private Transform target;
    [SerializeField] private Vector3 offset = new Vector3(0, 2, -10);
    [SerializeField] private float smoothSpeed = 5f;

    private void LateUpdate()
    {
        if (target == null) return;

        Vector3 targetPosition = target.position + offset;

        Tween.Position(
            transform,
            targetPosition,
            duration: Time.deltaTime * smoothSpeed
        );
    }
}
```

**Pro Tip**: This creates frame-rate independent smoothing. Higher `smoothSpeed` = faster follow.

---

### Camera Shake on Impact

**Problem**: Explosions/hits need camera shake feedback.

**Solution**: Use `Tween.ShakeCamera` with strength based on impact force.

```csharp
using UnityEngine;
using PrimeTween;

public class CameraShake : MonoBehaviour
{
    [SerializeField] private ShakeSettings lightShake;
    [SerializeField] private ShakeSettings mediumShake;
    [SerializeField] private ShakeSettings heavyShake;

    public void ShakeOnImpact(float impactForce)
    {
        ShakeSettings settings = impactForce switch
        {
            < 5f => lightShake,
            < 15f => mediumShake,
            _ => heavyShake
        };

        Tween.ShakeCamera(Camera.main, settings);
    }

    // Simpler version: dynamic strength
    public void ShakeSimple(float strength, float duration)
    {
        Tween.ShakeCamera(
            Camera.main,
            strength: strength,
            duration: duration,
            frequency: 10
        );
    }
}
```

---

### Camera Zoom In/Out

**Problem**: Dramatic moments need camera zoom transitions.

**Solution**: Animate `Camera.orthographicSize` (2D) or FOV (3D).

```csharp
using UnityEngine;
using PrimeTween;

public class CameraZoom : MonoBehaviour
{
    [SerializeField] private Camera cam;
    [SerializeField] private float defaultSize = 5f;
    [SerializeField] private float zoomDuration = 1f;

    private Tween zoomTween;

    // For 2D (orthographic)
    public void ZoomTo(float targetSize)
    {
        zoomTween.Stop();
        zoomTween = Tween.Custom(
            cam.orthographicSize,
            targetSize,
            zoomDuration,
            value => cam.orthographicSize = value
        );
    }

    // For 3D (perspective)
    public void ZoomFOV(float targetFOV)
    {
        zoomTween.Stop();
        zoomTween = Tween.Custom(
            cam.fieldOfView,
            targetFOV,
            zoomDuration,
            value => cam.fieldOfView = value
        );
    }

    public void ResetZoom()
    {
        ZoomTo(defaultSize);
    }

    private void OnDisable()
    {
        zoomTween.Stop();
    }
}
```

---

## Audio Patterns

### Audio Fade In/Out

**Problem**: Audio transitions need to be smooth, not jarring cuts.

**Solution**: Animate `AudioSource.volume`.

```csharp
using UnityEngine;
using PrimeTween;

public class AudioFader : MonoBehaviour
{
    [SerializeField] private AudioSource audioSource;
    [SerializeField] private float fadeDuration = 1f;

    private Tween fadeTween;

    public void FadeIn(float targetVolume = 1f)
    {
        if (!audioSource.isPlaying)
        {
            audioSource.volume = 0;
            audioSource.Play();
        }

        fadeTween.Stop();
        fadeTween = Tween.Custom(
            audioSource.volume,
            targetVolume,
            fadeDuration,
            value => audioSource.volume = value
        );
    }

    public void FadeOut(bool stopOnComplete = true)
    {
        fadeTween.Stop();
        fadeTween = Tween.Custom(
            audioSource.volume,
            0f,
            fadeDuration,
            value => audioSource.volume = value
        ).OnComplete(target: this, (self, _) => {
            if (stopOnComplete)
            {
                self.audioSource.Stop();
            }
        });
    }

    public void Crossfade(AudioSource otherSource, float duration)
    {
        Sequence.Create()
            .Group(Tween.Custom(audioSource.volume, 0f, duration, v => audioSource.volume = v))
            .Group(Tween.Custom(0f, 1f, duration, v => otherSource.volume = v))
            .OnComplete(() => audioSource.Stop());

        if (!otherSource.isPlaying)
        {
            otherSource.volume = 0;
            otherSource.Play();
        }
    }

    private void OnDisable()
    {
        fadeTween.Stop();
    }
}
```

---

### Audio Pitch Shift

**Problem**: Slow-motion/time effects need audio pitch changes.

**Solution**: Animate `AudioSource.pitch` synchronized with `Time.timeScale`.

```csharp
using UnityEngine;
using PrimeTween;

public class TimeEffect : MonoBehaviour
{
    [SerializeField] private AudioSource musicSource;
    [SerializeField] private float slowMoDuration = 2f;
    [SerializeField] private float slowMoScale = 0.5f;

    private Sequence slowMoSequence;

    public void TriggerSlowMotion()
    {
        slowMoSequence.Stop();

        slowMoSequence = Sequence.Create()
            // Slow down time and pitch together
            .Group(Tween.Custom(Time.timeScale, slowMoScale, 0.5f, v => Time.timeScale = v))
            .Group(Tween.Custom(musicSource.pitch, slowMoScale, 0.5f, v => musicSource.pitch = v))
            // Hold for duration (use unscaled time!)
            .Chain(Tween.Delay(slowMoDuration, useUnscaledTime: true))
            // Speed back up
            .Chain(Tween.Custom(Time.timeScale, 1f, 0.5f, v => Time.timeScale = v))
            .Group(Tween.Custom(musicSource.pitch, 1f, 0.5f, v => musicSource.pitch = v));
    }
}
```

---

## VFX Patterns

### Particle System Burst

**Problem**: VFX needs to spawn and self-destruct after playing.

**Solution**: Spawn particle system, delay destroy based on lifetime.

```csharp
using UnityEngine;
using PrimeTween;

public class VFXSpawner : MonoBehaviour
{
    [SerializeField] private ParticleSystem vfxPrefab;

    public void SpawnVFX(Vector3 position, Quaternion rotation)
    {
        ParticleSystem instance = Instantiate(vfxPrefab, position, rotation);
        instance.Play();

        float lifetime = instance.main.duration + instance.main.startLifetime.constantMax;

        Tween.Delay(lifetime, () => Destroy(instance.gameObject));
    }
}
```

---

### Dissolve Effect

**Problem**: Objects need to dissolve away smoothly.

**Solution**: Animate material's dissolve property (requires shader with `_Cutoff` or similar).

```csharp
using UnityEngine;
using PrimeTween;

public class DissolveEffect : MonoBehaviour
{
    [SerializeField] private Renderer targetRenderer;
    [SerializeField] private float dissolveDuration = 1f;
    [SerializeField] private string dissolveProperty = "_Cutoff";

    private Material material;
    private Tween dissolveTween;

    private void Awake()
    {
        material = targetRenderer.material; // Creates instance
    }

    public void Dissolve()
    {
        dissolveTween = Tween.Custom(
            startValue: 0f,
            endValue: 1f,
            duration: dissolveDuration,
            onValueChange: value => material.SetFloat(dissolveProperty, value)
        ).OnComplete(() => Destroy(gameObject));
    }

    private void OnDestroy()
    {
        Destroy(material); // Clean up material instance
    }
}
```

---

## Utility Patterns

### Object Pool with Tween Reset

**Problem**: Pooled objects may have active tweens when returned.

**Solution**: Always stop tweens before returning to pool.

```csharp
using UnityEngine;
using PrimeTween;
using System.Collections.Generic;

public class PooledObject : MonoBehaviour
{
    private List<Tween> activeTweens = new();

    public void AnimateSomething()
    {
        Tween t = Tween.Position(transform, Vector3.up * 5, 1f);
        activeTweens.Add(t);
    }

    public void ReturnToPool()
    {
        // Stop all active tweens
        foreach (Tween tween in activeTweens)
        {
            if (tween.isAlive)
            {
                tween.Stop();
            }
        }
        activeTweens.Clear();

        // Or use IshoBoy extension:
        // activeTweens.ClearTweens();

        // Reset transform
        transform.localPosition = Vector3.zero;
        transform.localRotation = Quaternion.identity;
        transform.localScale = Vector3.one;

        // Return to pool...
        ObjectPool.Return(this);
    }
}
```

**IshoBoy Extension** (`TweenExtensions.cs`):

```csharp
public static void ClearTweens(this List<Tween> tweens)
{
    foreach (Tween tween in tweens.ToArray())
    {
        if (tween.isAlive)
        {
            tween.Stop();
        }
    }
    tweens.Clear();
}
```

---

### Conditional Animation Chain

**Problem**: Animation steps depend on runtime conditions.

**Solution**: Build sequence dynamically based on state.

```csharp
using UnityEngine;
using PrimeTween;

public class ConditionalAnimation : MonoBehaviour
{
    [SerializeField] private bool shouldRotate;
    [SerializeField] private bool shouldScale;

    public void Animate()
    {
        Sequence sequence = Sequence.Create()
            .Chain(Tween.Position(transform, Vector3.up * 5, 1f));

        if (shouldRotate)
        {
            sequence.Chain(Tween.Rotation(transform, new Vector3(0, 180, 0), 1f));
        }

        if (shouldScale)
        {
            sequence.Chain(Tween.Scale(transform, 2f, 0.5f));
        }

        sequence.OnComplete(() => Debug.Log("Animation complete"));
    }
}
```

---

### Delayed Event System

**Problem**: Need to schedule multiple events at specific times.

**Solution**: Use `Sequence.ChainCallback` instead of `Invoke` or coroutines.

```csharp
using UnityEngine;
using PrimeTween;

public class EventScheduler : MonoBehaviour
{
    private Sequence eventSequence;

    public void ScheduleEvents()
    {
        eventSequence = Sequence.Create()
            .Chain(Tween.Delay(1f))
            .ChainCallback(() => Debug.Log("Event at 1 second"))
            .Chain(Tween.Delay(2f))
            .ChainCallback(() => Debug.Log("Event at 3 seconds"))
            .Chain(Tween.Delay(5f))
            .ChainCallback(() => Debug.Log("Event at 8 seconds"));
    }

    public void CancelEvents()
    {
        eventSequence.Stop();
    }
}
```

**Advantages over `Invoke`**:

- Can be stopped/paused
- Part of animation flow
- Respects `Time.timeScale` (unless using `useUnscaledTime`)

---

## Performance Patterns

### Batch Multiple Tweens

**Problem**: Creating 100 tweens in one frame may spike CPU.

**Solution**: Stagger tween creation across multiple frames.

```csharp
using UnityEngine;
using PrimeTween;
using System.Collections;
using System.Collections.Generic;

public class BatchedTweenSpawner : MonoBehaviour
{
    [SerializeField] private List<Transform> targets;
    [SerializeField] private int tweensPerFrame = 10;

    public IEnumerator AnimateAllBatched()
    {
        for (int i = 0; i < targets.Count; i += tweensPerFrame)
        {
            int batchEnd = Mathf.Min(i + tweensPerFrame, targets.Count);

            for (int j = i; j < batchEnd; j++)
            {
                Tween.Position(targets[j], Vector3.up * 5, 1f);
            }

            yield return null; // Wait one frame
        }
    }
}
```

---

### Reuse Sequence Patterns

**Problem**: Creating similar sequences repeatedly is inefficient.

**Solution**: Serialize `TweenSettings` and reuse across objects.

```csharp
[CreateAssetMenu]
public class TweenPreset : ScriptableObject
{
    public TweenSettings moveSettings;
    public TweenSettings scaleSettings;
    public TweenSettings rotateSettings;

    public Sequence CreateSequence(Transform target, Vector3 targetPos)
    {
        return Sequence.Create()
            .Chain(Tween.Position(target, targetPos, moveSettings))
            .Chain(Tween.Scale(target, 1.5f, scaleSettings))
            .Chain(Tween.Rotation(target, new Vector3(0, 180, 0), rotateSettings));
    }
}
```

---

## Next Steps

- **[Anti-Patterns](05-anti-patterns.md)** — Learn what NOT to do
- **[API Reference](03-api-reference.md)** — Complete method documentation
- **[Getting Started](01-getting-started.md)** — Refresh the basics

---

**Pro Tip**: The IshoBoy codebase has many more examples. Search for `using PrimeTween;` to find
real-world usage:

- `CarryComponent.cs` — Complex item drop sequences
- `MainMenu.cs` — Button animations with Inspector settings
- `CircularFadePostProcess.cs` — Custom tween for post-processing
- `AudioManager.cs` — Audio fading patterns
