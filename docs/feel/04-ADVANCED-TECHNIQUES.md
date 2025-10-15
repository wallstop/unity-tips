# Advanced Techniques

> **For Power Users**: Master scripting, custom feedbacks, performance optimization, and advanced
> patterns to unlock Feel's full potential.

## Scripting with MMFeedbacks

While Feel's Inspector workflow is powerful, scripting unlocks dynamic, context-aware feedback.

### Basic Scripting API

```csharp
using MoreMountains.Feedbacks;
using UnityEngine;

public class FeedbackController : MonoBehaviour
{
    [Header("Feedback References")]
    public MMFeedbacks onHitFeedback;
    public MMFeedbacks onDeathFeedback;
    public MMFeedbacks onJumpFeedback;

    // Play feedback
    void OnCollisionEnter(Collision collision)
    {
        onHitFeedback.PlayFeedbacks();
    }

    // Play feedback at specific position (useful for VFX)
    void SpawnEffect(Vector3 position)
    {
        onHitFeedback.PlayFeedbacks(position);
    }

    // Stop feedback (if it's looping or long-running)
    void OnDisable()
    {
        onHitFeedback.StopFeedbacks();
    }

    // Reset feedback to initial state
    void ResetEffect()
    {
        onHitFeedback.ResetFeedbacks();
    }

    // Pause and resume
    void PauseEffect()
    {
        onHitFeedback.PauseFeedbacks();
    }

    void ResumeEffect()
    {
        onHitFeedback.ResumeFeedbacks();
    }
}
```

### Controlling Feedback Intensity

Dynamically adjust feedback strength based on game state:

```csharp
public class DynamicFeedback : MonoBehaviour
{
    public MMFeedbacks screenShakeFeedback;

    // Scale intensity based on damage
    void TakeDamage(float damageAmount)
    {
        // Normalize damage (0-100) to intensity (0-1)
        float intensity = Mathf.Clamp01(damageAmount / 100f);
        screenShakeFeedback.FeedbacksIntensity = intensity;
        screenShakeFeedback.PlayFeedbacks();
    }

    // Full intensity for critical hits
    void TakeCriticalHit()
    {
        screenShakeFeedback.FeedbacksIntensity = 1.0f;
        screenShakeFeedback.PlayFeedbacks();
    }
}
```

**Use Cases**:

- Scale screen shake by explosion proximity
- Adjust haptic intensity based on impact force
- Vary particle density based on effect tier (common/rare/legendary)

### Reversing Feedbacks

Some feedbacks support **Direction** control:

```csharp
public class ReversibleEffect : MonoBehaviour
{
    public MMFeedbacks doorFeedback; // Contains Position, Rotation, Sound

    void OpenDoor()
    {
        doorFeedback.Direction = MMFeedbacks.Directions.TopToBottom;
        doorFeedback.PlayFeedbacks();
    }

    void CloseDoor()
    {
        doorFeedback.Direction = MMFeedbacks.Directions.BottomToTop; // Reverses!
        doorFeedback.PlayFeedbacks();
    }
}
```

**Works with**: Transform feedbacks, UI animations, tween-based feedbacks.

**Doesn't work with**: Instantiate feedbacks (can't un-spawn objects), one-shot effects.

### Feedback Events

Hook into feedback lifecycle:

```csharp
public class FeedbackEventListener : MonoBehaviour
{
    public MMFeedbacks myFeedback;

    void Start()
    {
        // Subscribe to events
        myFeedback.Events.OnPlay.AddListener(OnFeedbackPlay);
        myFeedback.Events.OnPause.AddListener(OnFeedbackPause);
        myFeedback.Events.OnResume.AddListener(OnFeedbackResume);
        myFeedback.Events.OnRevert.AddListener(OnFeedbackRevert);
        myFeedback.Events.OnComplete.AddListener(OnFeedbackComplete);
    }

    void OnDestroy()
    {
        // Always unsubscribe to prevent memory leaks!
        myFeedback.Events.OnPlay.RemoveListener(OnFeedbackPlay);
        myFeedback.Events.OnPause.RemoveListener(OnFeedbackPause);
        myFeedback.Events.OnResume.RemoveListener(OnFeedbackResume);
        myFeedback.Events.OnRevert.RemoveListener(OnFeedbackRevert);
        myFeedback.Events.OnComplete.RemoveListener(OnFeedbackComplete);
    }

    void OnFeedbackPlay()
    {
        Debug.Log("Feedback started!");
    }

    void OnFeedbackComplete()
    {
        Debug.Log("Feedback finished!");
        // Chain another action, spawn next wave, etc.
    }

    void OnFeedbackPause()
    {
        Debug.Log("Feedback paused.");
    }

    void OnFeedbackResume()
    {
        Debug.Log("Feedback resumed.");
    }

    void OnFeedbackRevert()
    {
        Debug.Log("Feedback reverted.");
    }
}
```

**Use Cases**:

- Chain multiple MMFeedbacks sequentially
- Track feedback completion for achievements
- Sync game logic with feedback timing
- Debug feedback execution

### Accessing Individual Feedbacks

Control specific feedbacks within an MMFeedbacks component:

```csharp
public class IndividualFeedbackControl : MonoBehaviour
{
    public MMFeedbacks multiEffectFeedback;

    void Start()
    {
        // Get specific feedback by type
        MMF_CameraShake shakeEffect = multiEffectFeedback.GetFeedbackOfType<MMF_CameraShake>();
        if (shakeEffect != null)
        {
            // Modify settings at runtime
            shakeEffect.ShakeAmplitude = 2.0f;
            shakeEffect.ShakeDuration = 0.5f;
        }

        // Disable a specific feedback
        MMF_Sound soundEffect = multiEffectFeedback.GetFeedbackOfType<MMF_Sound>();
        if (soundEffect != null)
        {
            soundEffect.Active = false; // Won't play when MMFeedbacks plays
        }
    }

    // Enable/disable feedback based on settings
    void UpdateSoundSettings(bool soundEnabled)
    {
        MMF_Sound soundEffect = multiEffectFeedback.GetFeedbackOfType<MMF_Sound>();
        if (soundEffect != null)
        {
            soundEffect.Active = soundEnabled;
        }
    }
}
```

**Use Cases**:

- Respect player settings (disable sound/haptics)
- Randomize effect parameters each play
- Enable/disable feedbacks based on game state

## Advanced Timing and Sequencing

### Timing Offset Pattern

Create staggered effects without multiple MMFeedbacks components:

```csharp
// In MMFeedbacks Inspector:
Feedback 1: Scale (UI Element 1)
  - Initial Delay: 0.0s
  - Duration: 0.3s

Feedback 2: Scale (UI Element 2)
  - Initial Delay: 0.1s ← starts 0.1s after Element 1
  - Duration: 0.3s

Feedback 3: Scale (UI Element 3)
  - Initial Delay: 0.2s ← starts 0.2s after Element 2
  - Duration: 0.3s

// Result: Cascading UI reveal!
```

**Use Cases**: Menu reveals, card flips, sequential damage numbers

### Chance-Based Feedbacks

Add randomness directly in Inspector:

```
Feedback: Particles (Critical Hit Sparkles)
  - Chance: 20% ← Only plays 20% of the time
```

**Scripted Version** (more control):

```csharp
public class RandomFeedback : MonoBehaviour
{
    public MMFeedbacks normalHitFeedback;
    public MMFeedbacks criticalHitFeedback; // Rarer, more dramatic

    void OnHit(bool isCritical)
    {
        if (isCritical)
        {
            criticalHitFeedback.PlayFeedbacks();
        }
        else
        {
            normalHitFeedback.PlayFeedbacks();
        }
    }

    // Random variation
    void OnHit()
    {
        if (Random.value < 0.2f) // 20% chance
        {
            criticalHitFeedback.PlayFeedbacks();
        }
        else
        {
            normalHitFeedback.PlayFeedbacks();
        }
    }
}
```

### Range-Based Feedbacks

Only play feedback if player is within range:

```
Feedback: Camera Shake
  - Use Range: True
  - Range: 10.0 ← Only shakes if MMFeedbacks is within 10 units of camera
```

**Perfect for**: Explosions, audio sources, localized effects.

### Looping Feedbacks

Create continuous effects:

```
Feedback: Light (Flickering Torch)
  - Duration: 0.2s
  - Loop: True
  - Number of Loops: -1 ← Infinite

// Stop via script when needed:
torchFeedback.StopFeedbacks();
```

**Use Cases**: Ambient effects, charging animations, auras

## Creating Custom Feedbacks

Extend Feel with your own feedback types!

### Step 1: Create Custom Feedback Class

```csharp
using MoreMountains.Feedbacks;
using UnityEngine;

/// <summary>
/// Custom feedback that rotates an object back and forth (oscillation)
/// </summary>
[AddComponentMenu("")]
[FeedbackHelp("Oscillates a transform's rotation back and forth around a specified axis.")]
[FeedbackPath("Transform/Oscillate Rotation")]
public class MMF_OscillateRotation : MMF_Feedback
{
    [Header("Oscillation Settings")]
    [Tooltip("The transform to oscillate")]
    public Transform TargetTransform;

    [Tooltip("Rotation axis (X, Y, or Z)")]
    public Vector3 RotationAxis = Vector3.forward;

    [Tooltip("Maximum rotation angle in degrees")]
    public float MaxAngle = 45f;

    [Tooltip("Oscillation speed (cycles per second)")]
    public float Speed = 1f;

    [Tooltip("How long to oscillate")]
    public float OscillationDuration = 2f;

    // Internal state
    private float _elapsedTime = 0f;
    private Quaternion _initialRotation;

    /// <summary>
    /// On init, store the initial rotation
    /// </summary>
    protected override void CustomInitialization(MMF_Player owner)
    {
        base.CustomInitialization(owner);
        if (TargetTransform != null)
        {
            _initialRotation = TargetTransform.localRotation;
        }
    }

    /// <summary>
    /// On Play, start oscillating
    /// </summary>
    protected override void CustomPlayFeedback(Vector3 position, float feedbacksIntensity = 1.0f)
    {
        if (!Active || TargetTransform == null)
        {
            return;
        }

        _elapsedTime = 0f;
        StartCoroutine(OscillateCoroutine(feedbacksIntensity));
    }

    private System.Collections.IEnumerator OscillateCoroutine(float intensity)
    {
        while (_elapsedTime < OscillationDuration)
        {
            _elapsedTime += Time.deltaTime;

            // Calculate oscillation angle using sine wave
            float angle = Mathf.Sin(_elapsedTime * Speed * Mathf.PI * 2f) * MaxAngle * intensity;

            // Apply rotation
            TargetTransform.localRotation = _initialRotation * Quaternion.AngleAxis(angle, RotationAxis);

            yield return null;
        }

        // Reset to initial rotation
        TargetTransform.localRotation = _initialRotation;
    }

    /// <summary>
    /// On Stop, reset rotation immediately
    /// </summary>
    protected override void CustomStopFeedback(Vector3 position, float feedbacksIntensity = 1.0f)
    {
        base.CustomStopFeedback(position, feedbacksIntensity);
        if (TargetTransform != null)
        {
            TargetTransform.localRotation = _initialRotation;
        }
        StopAllCoroutines();
    }

    /// <summary>
    /// On Reset, return to initial state
    /// </summary>
    protected override void CustomReset()
    {
        base.CustomReset();
        if (TargetTransform != null)
        {
            TargetTransform.localRotation = _initialRotation;
        }
    }
}
```

### Step 2: Use Your Custom Feedback

1. Add MMFeedbacks component to GameObject
2. Click "Add new feedback" → Transform → **Oscillate Rotation** (your custom feedback!)
3. Assign Target Transform, adjust settings
4. Play!

### Custom Feedback Template

```csharp
using MoreMountains.Feedbacks;
using UnityEngine;

[AddComponentMenu("")]
[FeedbackHelp("Brief description of what this feedback does.")]
[FeedbackPath("Category/YourFeedbackName")] // Where it appears in the menu
public class MMF_YourCustomFeedback : MMF_Feedback
{
    [Header("Your Settings")]
    public float YourParameter = 1.0f;

    protected override void CustomInitialization(MMF_Player owner)
    {
        base.CustomInitialization(owner);
        // Initialize your feedback (store references, etc.)
    }

    protected override void CustomPlayFeedback(Vector3 position, float feedbacksIntensity = 1.0f)
    {
        if (!Active)
        {
            return;
        }

        // Your feedback logic here!
        // Use feedbacksIntensity to scale effects (0-1 multiplier)
    }

    protected override void CustomStopFeedback(Vector3 position, float feedbacksIntensity = 1.0f)
    {
        base.CustomStopFeedback(position, feedbacksIntensity);
        // Stop your feedback (stop coroutines, reset state)
    }

    protected override void CustomReset()
    {
        base.CustomReset();
        // Reset to initial state
    }
}
```

**Key Methods**:

- `CustomInitialization`: Setup (called once)
- `CustomPlayFeedback`: Execute feedback logic
- `CustomStopFeedback`: Interrupt feedback early
- `CustomReset`: Return to initial state

## Performance Optimization

### Pooling and Reuse

Feel handles pooling internally, but you can optimize your usage:

**❌ BAD: Creating MMFeedbacks at Runtime**

```csharp
void OnHit()
{
    // Don't do this! Creates garbage and initialization overhead.
    GameObject feedbackObject = new GameObject("TempFeedback");
    MMFeedbacks feedback = feedbackObject.AddComponent<MMFeedbacks>();
    // Add feedbacks dynamically...
    feedback.PlayFeedbacks();
    Destroy(feedbackObject, 2f);
}
```

**✅ GOOD: Pre-Create and Reuse**

```csharp
public class FeedbackPool : MonoBehaviour
{
    public MMFeedbacks hitFeedbackPrefab;
    private List<MMFeedbacks> _feedbackPool = new List<MMFeedbacks>();
    private int _nextIndex = 0;

    void Start()
    {
        // Pre-instantiate a pool of feedback objects
        for (int i = 0; i < 10; i++)
        {
            MMFeedbacks instance = Instantiate(hitFeedbackPrefab, transform);
            instance.Initialization(gameObject);
            instance.gameObject.SetActive(false);
            _feedbackPool.Add(instance);
        }
    }

    public void PlayPooledFeedback(Vector3 position)
    {
        MMFeedbacks feedback = _feedbackPool[_nextIndex];
        feedback.transform.position = position;
        feedback.gameObject.SetActive(true);
        feedback.PlayFeedbacks();

        _nextIndex = (_nextIndex + 1) % _feedbackPool.Count;

        // Disable after playing (optional)
        StartCoroutine(DisableAfterDelay(feedback, 2f));
    }

    private System.Collections.IEnumerator DisableAfterDelay(MMFeedbacks feedback, float delay)
    {
        yield return new WaitForSeconds(delay);
        feedback.gameObject.SetActive(false);
    }
}
```

### Conditional Execution

Skip feedbacks based on settings or performance:

```csharp
public class AdaptiveFeedback : MonoBehaviour
{
    public MMFeedbacks highQualityFeedback; // Particles, post-processing, etc.
    public MMFeedbacks lowQualityFeedback;  // Just sound and basic effects

    void PlayAdaptiveFeedback()
    {
        if (QualitySettings.GetQualityLevel() >= 3) // High/Ultra quality
        {
            highQualityFeedback.PlayFeedbacks();
        }
        else
        {
            lowQualityFeedback.PlayFeedbacks();
        }
    }
}
```

### Respecting Player Settings

Disable specific feedback types based on user preferences:

```csharp
public class SettingsManager : MonoBehaviour
{
    public static bool ScreenShakeEnabled = true;
    public static bool HapticsEnabled = true;

    public MMFeedbacks myFeedback;

    void Start()
    {
        // Disable feedbacks based on settings
        if (!ScreenShakeEnabled)
        {
            MMF_CameraShake shake = myFeedback.GetFeedbackOfType<MMF_CameraShake>();
            if (shake != null) shake.Active = false;
        }

        if (!HapticsEnabled)
        {
            MMF_Haptics haptics = myFeedback.GetFeedbackOfType<MMF_Haptics>();
            if (haptics != null) haptics.Active = false;
        }
    }
}
```

### Avoiding Feedback Spam

Prevent rapid-fire feedback calls that overwhelm players:

```csharp
public class ThrottledFeedback : MonoBehaviour
{
    public MMFeedbacks screenShakeFeedback;
    private float _lastShakeTime = 0f;
    private float _shakeCooldown = 0.2f; // Minimum time between shakes

    void OnHit()
    {
        if (Time.time - _lastShakeTime > _shakeCooldown)
        {
            screenShakeFeedback.PlayFeedbacks();
            _lastShakeTime = Time.time;
        }
    }
}
```

## Advanced Patterns

### Health-Based Dynamic Feedback

Intensify effects as player health drops:

```csharp
public class HealthFeedback : MonoBehaviour
{
    public MMFeedbacks lowHealthVignetteFeedback;
    private float _currentHealth = 100f;
    private float _maxHealth = 100f;

    void Update()
    {
        float healthPercent = _currentHealth / _maxHealth;

        if (healthPercent < 0.3f) // Below 30% health
        {
            // Increase vignette intensity as health drops
            float intensity = 1f - (healthPercent / 0.3f); // 0.3 -> 0.0 maps to 0.0 -> 1.0
            lowHealthVignetteFeedback.FeedbacksIntensity = intensity;

            if (!lowHealthVignetteFeedback.IsPlaying)
            {
                lowHealthVignetteFeedback.PlayFeedbacks();
            }
        }
        else
        {
            if (lowHealthVignetteFeedback.IsPlaying)
            {
                lowHealthVignetteFeedback.StopFeedbacks();
            }
        }
    }
}
```

### Context-Aware Feedback Selection

Choose feedback based on environment:

```csharp
public class EnvironmentalFeedback : MonoBehaviour
{
    public MMFeedbacks grassFootstepFeedback;
    public MMFeedbacks waterFootstepFeedback;
    public MMFeedbacks metalFootstepFeedback;

    public enum SurfaceType { Grass, Water, Metal }
    private SurfaceType _currentSurface = SurfaceType.Grass;

    void OnFootstep()
    {
        switch (_currentSurface)
        {
            case SurfaceType.Grass:
                grassFootstepFeedback.PlayFeedbacks();
                break;
            case SurfaceType.Water:
                waterFootstepFeedback.PlayFeedbacks();
                break;
            case SurfaceType.Metal:
                metalFootstepFeedback.PlayFeedbacks();
                break;
        }
    }

    void OnTriggerEnter(Collider other)
    {
        // Detect surface type from collision layers/tags
        if (other.CompareTag("Water"))
        {
            _currentSurface = SurfaceType.Water;
        }
        else if (other.CompareTag("Metal"))
        {
            _currentSurface = SurfaceType.Metal;
        }
        else
        {
            _currentSurface = SurfaceType.Grass;
        }
    }
}
```

### Feedback Chains (Sequential Execution)

Execute multiple MMFeedbacks in sequence:

```csharp
public class FeedbackChain : MonoBehaviour
{
    public MMFeedbacks feedback1;
    public MMFeedbacks feedback2;
    public MMFeedbacks feedback3;

    void PlayChain()
    {
        feedback1.Events.OnComplete.AddListener(OnFeedback1Complete);
        feedback1.PlayFeedbacks();
    }

    void OnFeedback1Complete()
    {
        feedback1.Events.OnComplete.RemoveListener(OnFeedback1Complete);
        feedback2.Events.OnComplete.AddListener(OnFeedback2Complete);
        feedback2.PlayFeedbacks();
    }

    void OnFeedback2Complete()
    {
        feedback2.Events.OnComplete.RemoveListener(OnFeedback2Complete);
        feedback3.PlayFeedbacks();
    }
}
```

**Alternative: Use MMF_Events Feedback**

```
MMFeedbacks (Chain):
  Feedback 1: Scale (Duration: 0.5s)
  Feedback 2: Events (Unity Event → trigger next MMFeedbacks)
  Feedback 3: (next MMFeedbacks plays)
```

### Data-Driven Feedback Selection

Load feedback parameters from ScriptableObjects:

```csharp
[CreateAssetMenu(menuName = "Game/Feedback Profile")]
public class FeedbackProfile : ScriptableObject
{
    public float screenShakeIntensity = 1.0f;
    public float hapticIntensity = 1.0f;
    public bool particlesEnabled = true;
}

public class ProfiledFeedback : MonoBehaviour
{
    public FeedbackProfile profile;
    public MMFeedbacks myFeedback;

    void Start()
    {
        // Apply profile settings
        myFeedback.FeedbacksIntensity = profile.screenShakeIntensity;

        if (!profile.particlesEnabled)
        {
            MMF_Particles particles = myFeedback.GetFeedbackOfType<MMF_Particles>();
            if (particles != null) particles.Active = false;
        }
    }
}
```

**Use Cases**: Difficulty modes (easy = gentle feedback, hard = intense), accessibility profiles,
per-character feedback styles.

## Debugging and Troubleshooting

### Enable Feedback Debugging

In MMFeedbacks Inspector:

- **Debug Active**: Shows green indicator when playing
- **Feedback Label**: Rename feedbacks for clarity ("PlayerDamage_Shake" instead of "Camera Shake")

### Inspector Play Button

Use the **"▶ Play"** button in MMFeedbacks Inspector to test in Edit Mode (many feedbacks work
outside Play Mode!).

### Performance Profiler

Check feedback performance:

1. Open Profiler (Window → Analysis → Profiler)
2. Play your game
3. Look for "MMFeedbacks.PlayFeedbacks" calls in CPU Usage
4. Identify expensive feedbacks (usually Post Processing or complex particles)

### Common Pitfalls

**Issue**: Feedback plays once then never again. **Solution**: Check "Cooldown" settings — you may
have a long cooldown preventing replays.

**Issue**: Transform feedback doesn't reset between plays. **Solution**: Use "ToDestinationThenBack"
or add a second feedback to return to original state.

**Issue**: Feedback feels delayed. **Solution**: Check "Initial Delay" on individual feedbacks.

**Issue**: Post-processing feedback doesn't work. **Solution**: Ensure Volume component exists in
scene with the relevant override enabled.

## Next Steps

You're now a Feel power user! For final reference:

1. **[Troubleshooting](05-TROUBLESHOOTING.md)** — Detailed solutions to edge cases

**Pro Tip**: Share your custom feedbacks with the community! Feel has an active Discord and forum
where users exchange scripts and techniques.
