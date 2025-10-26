# Unity Coroutine Best Practices

## What Problem Does This Solve?

**The Problem:** You need to wait 3 seconds before spawning an enemy, or fade out UI over 2 seconds.
Using `Update()` with timers is messy and error-prone.

**Without Coroutines (The Painful Way):**

```csharp
private float timer = 0f;
private bool isWaiting = false;

void Update() {
    if (isWaiting) {
        timer += Time.deltaTime;
        if (timer >= 3f) {
            SpawnEnemy();
            isWaiting = false;
            timer = 0f;
        }
    }
}

void StartSpawnSequence() {
    isWaiting = true;
    timer = 0f;
}
```

**With Coroutines (The Clean Way):**

```csharp
IEnumerator Start() {
    yield return new WaitForSeconds(3f);
    SpawnEnemy();
}
```

**The Solution:** Coroutines let you write time-based logic sequentially instead of managing timers
and state flags manually. This reduces code complexity by 70-80% for time-based operations.

---

## ⚠️ Critical Rules - Read This First!

**If you remember nothing else, remember these 3 rules:**

1. **ALWAYS store the Coroutine reference** when calling `StartCoroutine()`

   ```csharp
   Coroutine myCoroutine = StartCoroutine(MyCoroutine()); // ✓ CORRECT
   ```

1. **Setting to null does NOT stop a coroutine!** You MUST call `StopCoroutine()`:

   ```csharp
   myCoroutine = null; // ❌ Still running!
   StopCoroutine(myCoroutine); // ✓ Actually stops it
   myCoroutine = null; // ✓ Then null for tracking
   ```

1. **You CANNOT stop a coroutine by calling the method again:**

   ```csharp
   StartCoroutine(FlashRed());
   StopCoroutine(FlashRed()); // ❌ DOES NOT WORK!
   ```

**Read the full guide below to understand WHY these rules exist and avoid common mistakes!**

---

## Table of Contents

- [What are Coroutines?](#what-are-coroutines)
- [When to Use Coroutines](#when-to-use-coroutines)
- [When NOT to Use Coroutines](#when-not-to-use-coroutines)
- [Critical Best Practices](#critical-best-practices)
- [Common Pitfalls and How to Avoid Them](#common-pitfalls-and-how-to-avoid-them)
- [Code Examples](#code-examples)

## What are Coroutines?

Coroutines are a way to spread work across multiple frames in Unity. Think of them as functions that
can pause execution, wait for something (like time passing or another operation), and then resume
where they left off.

**Simple Analogy**: Imagine you're cooking and you put something in the oven. Instead of standing
there staring at it for 30 minutes, you go do other things and come back when the timer beeps.
Coroutines work the same way - they can "pause" and let other code run, then "resume" when ready.

### How They Differ from Normal Functions

```csharp
// Normal function - runs completely in one frame
void DoSomething()
{
    Debug.Log("Start");
    // These both happen in the same frame
    Debug.Log("Middle");
    Debug.Log("End");
}

// Coroutine - can spread across multiple frames
IEnumerator DoSomethingOverTime()
{
    Debug.Log("Start");
    yield return new WaitForSeconds(1f); // Pause here for 1 second
    Debug.Log("Middle"); // This happens 1 second later
    yield return new WaitForSeconds(1f); // Pause again
    Debug.Log("End"); // This happens 2 seconds after we started
}
```

## When to Use Coroutines

Coroutines are perfect for:

- **Time-based effects** - Fading UI, timed buffs, cooldown timers
- **Sequences of actions** - Play animation, wait, spawn enemy, wait, close door
- **Gradual changes** - Moving objects smoothly, interpolating values over time
- **Waiting for conditions** - Wait until player is close, wait until animation finishes
- **Periodic checks** - Check every 0.5 seconds if something is true
- **Asynchronous operations** - Loading assets, waiting for network responses

**Examples**:

- Fade a UI element in over 2 seconds
- Flash a damaged enemy red for 0.2 seconds
- Wait 3 seconds then spawn the next wave
- Gradually heal the player 5 HP per second for 10 seconds

## When NOT to Use Coroutines

Avoid coroutines when:

- **Every frame logic** - Use `Update()` instead; it's clearer and more efficient
- **Instant operations** - If nothing needs to wait, just use a regular function
- **Complex state management** - Consider state machines or behavior trees instead
- **Performance-critical loops** - Coroutines have overhead; tight loops should be in regular
  functions
- **When you need precise timing** - Coroutines can be affected by frame rate and time scale

**Wrong Uses**:

```csharp
// DON'T - This should just be in Update()
IEnumerator CheckInput()
{
    while (true)
    {
        if (Input.GetKeyDown(KeyCode.Space))
            Jump();
        yield return null; // Every frame
    }
}
```

## Critical Best Practices

### 1. **ALWAYS Store the Coroutine Reference**

**THE GOLDEN RULE**: When you start a coroutine, store the `Coroutine` object that
`StartCoroutine()` returns. This lets you control the coroutine's lifetime.

#### Why This Matters

```csharp
// BAD - No way to stop it later!
StartCoroutine(FlashRed());

// GOOD - You can control it
Coroutine flashCoroutine = StartCoroutine(FlashRed());
```

Without storing the reference, you:

- Can't cancel the coroutine
- Can't check if it's running
- Risk stacking multiple copies if the code runs again
- Lose control over the effect

### 2. **Prevent Stacking Coroutines**

When the same code can be called multiple times, you MUST prevent multiple coroutines from running
simultaneously.

```csharp
// BAD - Calling DealDamage() 5 times = 5 simultaneous flash effects!
public void DealDamage()
{
    StartCoroutine(FlashRed());
    health -= 10;
}

// GOOD - Always check and stop existing coroutines first
private Coroutine flashCoroutine;

public void DealDamage()
{
    // Stop any existing flash effect
    if (flashCoroutine != null)
    {
        StopCoroutine(flashCoroutine);
    }

    // Start a new one
    flashCoroutine = StartCoroutine(FlashRed());
    health -= 10;
}

private IEnumerator FlashRed()
{
    spriteRenderer.color = Color.red;
    yield return new WaitForSeconds(0.2f);
    spriteRenderer.color = Color.white;

    // Clean up the reference when done
    flashCoroutine = null;
}
```

### 3. **Clean Up Coroutine References**

Set the coroutine reference to `null` at the end of your coroutine. This indicates it's no longer
running.

```csharp
private IEnumerator MyCoroutine()
{
    // Do work...
    yield return new WaitForSeconds(1f);
    // More work...

    // Always do this at the end
    myCoroutineReference = null;
}
```

**Why?** So you can check `if (myCoroutineReference != null)` to see if it's running.

**CRITICAL DISTINCTION**: Setting a coroutine to `null` does **NOT** stop it! This is just
bookkeeping.

```csharp
// This does NOT stop the coroutine - it keeps running!
myCoroutine = null;

// This DOES stop the coroutine
StopCoroutine(myCoroutine);
myCoroutine = null; // Then null it for bookkeeping
```

The coroutine will continue running until:

- It finishes naturally (reaches the end or `yield break`)
- You explicitly call `StopCoroutine()`
- The MonoBehaviour it started on is disabled/destroyed

### 4. **Stop Coroutines on Disable/Destroy**

If your MonoBehaviour is disabled or destroyed, coroutines started on it automatically stop.
However, you should still clean up references and handle any necessary state changes.

```csharp
private Coroutine healingCoroutine;

private void OnDisable()
{
    // Stop the coroutine if it's running
    if (healingCoroutine != null)
    {
        StopCoroutine(healingCoroutine);
        healingCoroutine = null;
    }

    // Clean up any state
    isHealing = false;
}

private void OnDestroy()
{
    // Same cleanup
    if (healingCoroutine != null)
    {
        StopCoroutine(healingCoroutine);
        healingCoroutine = null;
    }
}
```

## Common Pitfalls and How to Avoid Them

### Pitfall 1: Not Storing Coroutine References

```csharp
// BAD
void StartEffect()
{
    StartCoroutine(EffectCoroutine());
}

// GOOD
private Coroutine effectCoroutine;

void StartEffect()
{
    if (effectCoroutine != null)
        StopCoroutine(effectCoroutine);

    effectCoroutine = StartCoroutine(EffectCoroutine());
}
```

### Pitfall 2: Stacking Coroutines

```csharp
// BAD - Each button click stacks another coroutine
public void OnButtonClick()
{
    StartCoroutine(AnimateButton());
}

// GOOD - Always stop the previous one
private Coroutine buttonAnimation;

public void OnButtonClick()
{
    if (buttonAnimation != null)
        StopCoroutine(buttonAnimation);

    buttonAnimation = StartCoroutine(AnimateButton());
}

private IEnumerator AnimateButton()
{
    // Animation logic...
    yield return new WaitForSeconds(0.3f);
    buttonAnimation = null;
}
```

### Pitfall 3: Forgetting to Null References

```csharp
// BAD - Can't tell if coroutine is still running
private Coroutine myCoroutine;

private IEnumerator MyCoroutine()
{
    yield return new WaitForSeconds(1f);
    // Forgot to set myCoroutine = null
}

// Now this check doesn't work correctly
if (myCoroutine != null)
{
    // This might be true even after coroutine finished!
}

// GOOD - Always null at the end
private IEnumerator MyCoroutine()
{
    yield return new WaitForSeconds(1f);
    myCoroutine = null; // ✓
}
```

**Important**: Setting to `null` doesn't stop the coroutine - it's just for tracking! If you need to
cancel early, use `StopCoroutine()` first.

### Pitfall 4: Thinking Setting to Null Stops the Coroutine

**This is a VERY common misconception!**

```csharp
// BAD - Coroutine keeps running!
private Coroutine healCoroutine;

public void StartHealing()
{
    healCoroutine = StartCoroutine(HealOverTime());
}

public void StopHealing()
{
    // ⚠️ THIS DOES NOT STOP THE COROUTINE!
    healCoroutine = null;
    // The coroutine is still running and healing the player!
}

// GOOD - Actually stop it
public void StopHealing()
{
    if (healCoroutine != null)
    {
        StopCoroutine(healCoroutine); // ✓ Actually stops it
        healCoroutine = null; // ✓ Then bookkeeping
    }
}
```

**Remember**: `myCoroutine = null` only removes YOUR reference to the coroutine. Unity is still
running it in the background. You must explicitly call `StopCoroutine()` to cancel execution.

### Pitfall 5: Using Wrong Stop Method

```csharp
// BAD - Stops ALL coroutines on this object!
StopAllCoroutines();

// GOOD - Stop specific ones
if (coroutine1 != null)
    StopCoroutine(coroutine1);
if (coroutine2 != null)
    StopCoroutine(coroutine2);

// BAD - Only works if you pass the exact same IEnumerator instance
IEnumerator routine = MyRoutine();
StartCoroutine(routine);
StopCoroutine(routine); // Works, but awkward

// GOOD - Use the Coroutine reference
Coroutine myCoroutine = StartCoroutine(MyRoutine());
StopCoroutine(myCoroutine); // ✓ Clean and clear
```

### Pitfall 6: Trying to Stop by Calling the Method Again

**CRITICAL MISUNDERSTANDING:** Calling `StopCoroutine()` with a method call does NOT work!

```csharp
// BAD - THIS DOES NOT WORK!
StartCoroutine(FlashRed());

// Later, trying to stop it...
StopCoroutine(FlashRed()); // ⚠️ DOES NOT STOP THE COROUTINE!
// This creates a NEW IEnumerator and tries to stop THAT (which was never started)
// The original coroutine keeps running!

// GOOD - Store and stop the reference
Coroutine flashCoroutine = StartCoroutine(FlashRed());

// Later...
if (flashCoroutine != null)
{
    StopCoroutine(flashCoroutine); // ✓ Stops the actual running coroutine
    flashCoroutine = null;
}
```

**Why this fails**: Each time you call `FlashRed()`, it creates a **new, different** IEnumerator
object. `StopCoroutine(FlashRed())` tries to stop that new one, not the original running one.
They're completely unrelated!

**Think of it like**: If you start driving a car, you can't stop it by getting into a different car
and hitting the brakes. You need a reference to the **specific car you started**.

### Pitfall 7: Waiting in Infinite Loops Without Yielding

```csharp
// BAD - This FREEZES Unity!
private IEnumerator WaitForCondition()
{
    while (!conditionMet)
    {
        // Nothing here - infinite loop in one frame!
    }
    DoSomething();
}

// GOOD - Yield every loop iteration
private IEnumerator WaitForCondition()
{
    while (!conditionMet)
    {
        yield return null; // Wait one frame
    }
    DoSomething();
}

// BETTER - Add a timeout safety
private IEnumerator WaitForCondition()
{
    float timeout = 5f;
    float elapsed = 0f;

    while (!conditionMet && elapsed < timeout)
    {
        yield return null;
        elapsed += Time.deltaTime;
    }

    if (conditionMet)
        DoSomething();
    else
        Debug.LogWarning("Coroutine timed out!");
}
```

### Pitfall 8: Not Returning the IEnumerator Result

```csharp
// BAD - Returns void, not a coroutine!
IEnumerator MyCoroutine()
{
    yield return new WaitForSeconds(1f);
    DoSomething();
    // No return statement!
}

// GOOD - Explicitly shows it returns
IEnumerator MyCoroutine()
{
    yield return new WaitForSeconds(1f);
    DoSomething();
    yield break; // Explicit exit (optional but clear)
}
```

**Note**: While C# allows omitting the explicit return, `yield break` makes intent clearer,
especially for beginners.

### Pitfall 9: Trying to Get a Return Value Immediately

```csharp
// BAD - This doesn't work how you think!
IEnumerator CalculateValue()
{
    yield return new WaitForSeconds(1f);
    return 42; // ⚠️ This doesn't return 42 to the caller!
}

// Later...
int result = CalculateValue(); // ❌ COMPILER ERROR - can't convert IEnumerator to int
```

**Coroutines can't return values directly!** If you need a result, use callbacks or set a field:

```csharp
// GOOD - Use a callback
private void StartCalculation()
{
    StartCoroutine(CalculateValue(result => {
        Debug.Log($"Got result: {result}");
    }));
}

private IEnumerator CalculateValue(System.Action<int> callback)
{
    yield return new WaitForSeconds(1f);
    callback(42); // Pass result to callback
}

// ALSO GOOD - Set a field
private int calculatedValue;

private IEnumerator CalculateValue()
{
    yield return new WaitForSeconds(1f);
    calculatedValue = 42; // Store in field
}
```

### Pitfall 10: Forgetting to Actually Start the Coroutine

```csharp
// BAD - Coroutine never runs!
void DoSomethingDelayed()
{
    DelayedAction(); // ❌ Just calls the method, doesn't start the coroutine!
    // Nothing happens!
}

IEnumerator DelayedAction()
{
    yield return new WaitForSeconds(1f);
    Debug.Log("This never prints!");
}

// GOOD - Actually start it
void DoSomethingDelayed()
{
    StartCoroutine(DelayedAction()); // ✓ Starts the coroutine
}
```

**Why this happens**: Calling an `IEnumerator` method without `StartCoroutine()` just creates the
IEnumerator object but doesn't run it. It's like writing down instructions but never following them.

### Pitfall 11: Accessing Destroyed Objects After Yield

```csharp
// BAD - Can crash after yield!
private IEnumerator AttackSequence(Enemy enemy)
{
    enemy.TakeDamage(10);

    yield return new WaitForSeconds(0.5f);

    // ⚠️ Enemy might be dead/destroyed now!
    enemy.TakeDamage(10); // ☠️ NullReferenceException
}

// GOOD - Check validity after yield
private IEnumerator AttackSequence(Enemy enemy)
{
    if (enemy == null) yield break;

    enemy.TakeDamage(10);

    yield return new WaitForSeconds(0.5f);

    // Check if still valid
    if (enemy == null) yield break;

    enemy.TakeDamage(10); // Safe
}
```

**Rule of thumb**: After ANY `yield` statement, assume the world might have changed. Check that
objects still exist before using them.

### Pitfall 12: Using StartCoroutine on a Disabled GameObject

````csharp
// BAD - Coroutine won't run!
void Start()
{
    gameObject.SetActive(false);
    StartCoroutine(MyCoroutine()); // ⚠️ Won't run - object is disabled!
}

// GOOD - Start before disabling
void Start()
{
    StartCoroutine(MyCoroutine()); // Start first
    // Disable later if needed
}
````
**Important**: Coroutines on a GameObject only run while that GameObject is active. Disabling it stops all its coroutines.

### Pitfall 13: Reusing the Same WaitForSeconds Object Incorrectly

```csharp
// CONFUSING - Don't do this as a beginner
private WaitForSeconds wait = new WaitForSeconds(1f);

IEnumerator MyCoroutine()
{
    yield return wait; // Reusing is OK but can be confusing
}
````

**For beginners**: Just create new `WaitForSeconds` each time. It's clearer and the performance
difference is negligible until you profile:

```csharp
// CLEARER - Do this when learning
IEnumerator MyCoroutine()
{
    yield return new WaitForSeconds(1f); // Clear and simple
}
```

**Advanced note**: Caching `WaitForSeconds` reduces garbage, but only optimize after profiling shows
it's needed.

### Pitfall 14: Forgetting Time.timeScale Affects WaitForSeconds

```csharp
// Can be surprising for beginners!
IEnumerator DelayedAction()
{
    // If Time.timeScale = 0 (paused), this NEVER completes!
    yield return new WaitForSeconds(2f);
    Debug.Log("This prints after 2 seconds of game time");
}

// If you need real-time (ignoring pause/slow-mo)
IEnumerator DelayedActionRealtime()
{
    yield return new WaitForSecondsRealtime(2f); // Unaffected by timeScale
    Debug.Log("This prints after 2 real seconds");
}
```

**Important distinction**:

- `WaitForSeconds` - Affected by `Time.timeScale` (pauses when game pauses)
- `WaitForSecondsRealtime` - Real-world time (continues even when paused)

### Pitfall 15: Modifying Collections While Iterating in Coroutines

```csharp
// BAD - Can cause errors!
private List<Enemy> enemies = new List<Enemy>();

IEnumerator DamageAllEnemies()
{
    foreach (Enemy enemy in enemies)
    {
        enemy.TakeDamage(10);

        // ⚠️ If TakeDamage() kills enemy and removes it from the list...
        yield return new WaitForSeconds(0.5f);
        // ☠️ Collection was modified; enumeration operation may not execute
    }
}

// GOOD - Iterate backwards or copy the list
IEnumerator DamageAllEnemies()
{
    // Option 1: Iterate backwards (safe if removing)
    for (int i = enemies.Count - 1; i >= 0; i--)
    {
        if (i >= enemies.Count) continue; // Safety check

        enemies[i].TakeDamage(10);
        yield return new WaitForSeconds(0.5f);
    }
}

// ALSO GOOD - Copy the list
IEnumerator DamageAllEnemies()
{
    List<Enemy> enemiesCopy = new List<Enemy>(enemies);

    foreach (Enemy enemy in enemiesCopy)
    {
        if (enemy == null) continue; // Check validity

        enemy.TakeDamage(10);
        yield return new WaitForSeconds(0.5f);
    }
}
```

## Code Examples

### Example 1: Simple Fade Effect

```csharp
using UnityEngine;
using System.Collections;

public class FadeEffect : MonoBehaviour
{
    [SerializeField] private CanvasGroup canvasGroup;
    private Coroutine fadeCoroutine;

    public void FadeIn(float duration)
    {
        // Stop any existing fade
        if (fadeCoroutine != null)
            StopCoroutine(fadeCoroutine);

        fadeCoroutine = StartCoroutine(FadeToAlpha(1f, duration));
    }

    public void FadeOut(float duration)
    {
        if (fadeCoroutine != null)
            StopCoroutine(fadeCoroutine);

        fadeCoroutine = StartCoroutine(FadeToAlpha(0f, duration));
    }

    private IEnumerator FadeToAlpha(float targetAlpha, float duration)
    {
        float startAlpha = canvasGroup.alpha;
        float elapsed = 0f;

        while (elapsed < duration)
        {
            elapsed += Time.deltaTime;
            float t = elapsed / duration;
            canvasGroup.alpha = Mathf.Lerp(startAlpha, targetAlpha, t);
            yield return null; // Wait one frame
        }

        // Ensure we hit exact target
        canvasGroup.alpha = targetAlpha;

        // Clean up reference
        fadeCoroutine = null;
    }

    private void OnDisable()
    {
        // Stop fade if disabled
        if (fadeCoroutine != null)
        {
            StopCoroutine(fadeCoroutine);
            fadeCoroutine = null;
        }
    }
}
```

### Example 2: Damage Flash with Proper Stacking Prevention

```csharp
using UnityEngine;
using System.Collections;

public class DamageFlash : MonoBehaviour
{
    [SerializeField] private SpriteRenderer spriteRenderer;
    [SerializeField] private Color flashColor = Color.red;
    [SerializeField] private float flashDuration = 0.15f;

    private Color originalColor;
    private Coroutine flashCoroutine;

    private void Awake()
    {
        originalColor = spriteRenderer.color;
    }

    public void Flash()
    {
        // CRITICAL: Stop existing flash before starting new one
        if (flashCoroutine != null)
        {
            StopCoroutine(flashCoroutine);
            // Reset to original color in case we interrupted mid-flash
            spriteRenderer.color = originalColor;
        }

        flashCoroutine = StartCoroutine(FlashCoroutine());
    }

    private IEnumerator FlashCoroutine()
    {
        // Flash to damage color
        spriteRenderer.color = flashColor;

        // Wait
        yield return new WaitForSeconds(flashDuration);

        // Return to original
        spriteRenderer.color = originalColor;

        // Clean up reference
        flashCoroutine = null;
    }

    private void OnDisable()
    {
        if (flashCoroutine != null)
        {
            StopCoroutine(flashCoroutine);
            flashCoroutine = null;
            spriteRenderer.color = originalColor; // Reset appearance
        }
    }
}
```

### Example 3: Complex Sequence with Multiple Steps

```csharp
using UnityEngine;
using System.Collections;

public class SpawnSequence : MonoBehaviour
{
    [SerializeField] private GameObject enemyPrefab;
    [SerializeField] private Transform spawnPoint;
    [SerializeField] private GameObject doorObject;

    private Coroutine sequenceCoroutine;

    public void StartSpawnSequence()
    {
        // Prevent multiple sequences running
        if (sequenceCoroutine != null)
        {
            Debug.LogWarning("Sequence already running!");
            return;
        }

        sequenceCoroutine = StartCoroutine(SpawnSequenceCoroutine());
    }

    private IEnumerator SpawnSequenceCoroutine()
    {
        // Step 1: Close door
        doorObject.SetActive(true);

        // Step 2: Wait before spawning
        yield return new WaitForSeconds(1f);


        List<Enemy> enemies = new();
        // Step 3: Spawn 3 enemies with delays
        for (int i = 0; i < 3; i++)
        {
            Enemey enemy = Instantiate(enemyPrefab, spawnPoint.position, Quaternion.identity);
            enemies.Add(enemies);
            yield return new WaitForSeconds(0.5f);
        }

        // Step 4: Wait for all enemies to be defeated
        yield return new WaitUntil(() => enemies.All(spawned => spawned == null));

        // Step 5: Open door
        yield return new WaitForSeconds(0.5f);
        doorObject.SetActive(false);

        // Clean up
        sequenceCoroutine = null;
    }

    public void CancelSequence()
    {
        if (sequenceCoroutine != null)
        {
            StopCoroutine(sequenceCoroutine);
            sequenceCoroutine = null;

            // Clean up any partial state
            doorObject.SetActive(false);
        }
    }

    private void OnDisable()
    {
        CancelSequence();
    }
}
```

## Quick Reference Checklist

When writing a coroutine, ask yourself:

- [ ] Am I storing the `Coroutine` reference returned by `StartCoroutine()`?
- [ ] Am I checking and stopping existing coroutines before starting new ones?
- [ ] Am I setting the reference to `null` at the end of the coroutine?
- [ ] Am I stopping coroutines in `OnDisable()` and `OnDestroy()`?
- [ ] Do I have a `yield` statement in my while loops?
- [ ] Am I avoiding `StopAllCoroutines()` unless I really mean it?
- [ ] Am I checking object validity after `yield` statements when objects might be destroyed?

## Summary

**The Core Principles:**

1. **Always track coroutines** - Store the `Coroutine` reference
2. **Prevent stacking** - Stop existing coroutines before starting new ones
3. **Clean up references** - Set to `null` when done
4. **Manage lifecycle** - Stop in `OnDisable`/`OnDestroy`

Coroutines are powerful tools for time-based and sequential logic, but they require careful lifetime
management. Follow these practices and you'll avoid the most common pitfalls!
