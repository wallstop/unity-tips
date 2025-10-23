# Unity Physics Best Practices

> **Unity Version Note**: This guide uses Unity 6 property names. If you're using Unity 5.x or
> earlier versions:
>
> - Use `velocity` instead of `linearVelocity`
> - Use `angularVelocity` (unchanged across versions)
> - Note that `drag` (Inspector UI) is accessed as `linearDamping` in code (Unity 6+)

## What Problem Does This Solve?

**The Problem:** You move a Rigidbody in `Update()` and it jitters, tunnels through walls, or
behaves inconsistently on different frame rates.

**Why This Happens:** Unity's physics engine runs at a fixed 50 times per second (by default), but
`Update()` runs at your frame rate (30-300 FPS). If you modify physics in `Update()`, you're
changing physics 60 times per second while physics simulates 50 times per second—causing desynced,
jittery motion.

**Analogy:** Imagine a train (physics simulation) running on a fixed schedule (50 times/sec) but
passengers (your code) trying to board at random times (variable frame rate). Some passengers miss
the train, some board twice. Result: chaos.

**The Solution:** Always modify physics (velocity, forces, position) in `FixedUpdate()`, which runs
synchronized with physics simulation.

**Real-World Impact:**

- ✅ Eliminates jittery physics movement
- ✅ Consistent behavior across all frame rates
- ✅ Prevents tunneling through walls
- ✅ Makes multiplayer physics deterministic

---

## ⚠️ Critical Rules

**The most common physics mistakes:**

1. 🔴 **CRITICAL**: Modifying physics in `Update()` instead of `FixedUpdate()` - causes frame-rate
   dependent behavior
2. 🟡 **QUALITY**: Using legacy Input polling (`Input.GetKey`, `Input.GetAxis`) instead of Unity's
   Input System package
3. 🟡 **QUALITY**: Using `transform.position` instead of `Rigidbody.MovePosition()` - causes jitter
   and collision issues
4. 🟢 **NOTE**: Impulse forces CAN be called from Update (Unity queues them for next physics step)

### ⚠️ About Input Polling in Examples

> **IMPORTANT**: All code examples in this document use the **legacy Input Manager**
> (`Input.GetKey`, `Input.GetAxis`) for simplicity. However, **Unity now recommends the Input System
> package** for production projects.
>
> **Why the new Input System is better:**
>
> - **Event-driven** instead of polling (more efficient, no Update() checks needed)
> - **Automatic multi-platform** support (gamepad, keyboard, touch, VR all work with same code)
> - **Rebindable controls** without code changes (players can customize bindings in-game)
> - **Composites and modifiers** (e.g., "Sprint = Shift + Forward" is trivial)
> - **Better for multiplayer** and modern hardware support
>
> **Legacy Input limitations:**
>
> - Must poll every frame with `Input.GetKey()` (less efficient)
> - Hard-coded keybindings (changing keys requires code modifications)
> - Poor gamepad/VR/touch support (separate code paths needed)
> - Not receiving updates for new hardware
>
> **For production projects**, strongly consider migrating to the Input System package. The physics
> principles in this document apply to both—just replace `Input.GetKey()` polling with Input Action
> callbacks.

### Will These Mistakes "Still Work"?

**Short answer: Yes, but with significant quality issues.**

These aren't compile errors or crashes - they're **quality and consistency problems** that separate
amateur from professional Unity development:

| Practice                            | Will It Move? | What Actually Happens                                                     |
| ----------------------------------- | ------------- | ------------------------------------------------------------------------- |
| `transform.position` on Rigidbody   | ✅ Yes        | ❌ Jitters, breaks interpolation, ignores collisions, causes desync       |
| Continuous force in `Update()`      | ✅ Yes        | ❌ Frame-rate dependent (30fps ≠ 144fps), inconsistent, non-deterministic |
| Impulse force in `Update()`         | ✅ Yes        | ✅ Actually fine - Unity queues it for next physics step                  |
| Force in `FixedUpdate()`            | ✅ Yes        | ✅ Smooth, consistent, deterministic                                      |
| `MovePosition()` in `FixedUpdate()` | ✅ Yes        | ✅ Smooth, collision-aware, professional                                  |

**Reality Check:**

- Your game won't crash, but players will notice the jank
- "Works on my machine" but behaves differently on faster/slower hardware
- Single-player might seem fine, but multiplayer will be a nightmare
- Professional studios follow these practices for good reason

## Table of Contents

- [Update vs FixedUpdate](#update-vs-fixedupdate)
- [Transform vs Rigidbody Methods](#transform-vs-rigidbody-methods)
- [Force Modes Explained](#force-modes-explained)
- [Collision and Triggers](#collision-and-triggers)
- [Best Practices](#best-practices)
- [Common Pitfalls](#common-pitfalls)

## Update vs FixedUpdate

### Understanding the Difference

```csharp
// Update() - Called every frame
// - Variable timestep (depends on frame rate)
// - Use for: Input, UI, animations, rendering
private void Update()
{
    // Runs at variable rate: 30fps, 60fps, 144fps, etc.
    // Time.deltaTime varies each frame
}

// FixedUpdate() - Called at fixed intervals
// - Fixed timestep (default 0.02s = 50 times per second)
// - Use for: Physics, Rigidbody movement
private void FixedUpdate()
{
    // Runs at fixed rate: 50fps by default
    // Time.deltaTime is constant here as well (0.02s)
    // Time.fixedDeltaTime is constant (0.02s)
}
```

### Visual Explanation

```
Frame Rate = 60 FPS (16.67ms per frame)
Physics Rate = 50 FPS (20ms per physics step)

Timeline:
0ms    16.67ms   33.33ms   40ms      50ms      60ms
|------|---------|---------|---------|---------|
Update  Update    Update   FixedUp   Update   FixedUp
                           |                  |
                           Physics            Physics

Update happens more often than FixedUpdate in this scenario!
```

### When to Use Each

```csharp
public class PhysicsObject : MonoBehaviour
{
    private Rigidbody rb;
    private bool jumpRequested;
    private float horizontalInput;

    private void Awake()
    {
        rb = GetComponent<Rigidbody>();
    }

    // ✓ Use Update for input - cache it for FixedUpdate
    private void Update()
    {
        // Cache input every frame for responsiveness
        if (Input.GetKeyDown(KeyCode.Space))
        {
            jumpRequested = true;
        }

        horizontalInput = Input.GetAxis("Horizontal");
    }

    // ✓ Use FixedUpdate for physics - apply cached input
    private void FixedUpdate()
    {
        // Apply cached horizontal input
        rb.AddForce(Vector3.right * horizontalInput * 10f);

        // Apply jump if requested
        if (jumpRequested)
        {
            rb.AddForce(Vector3.up * 5f, ForceMode.Impulse);
            jumpRequested = false;
        }
    }
}
```

## Transform vs Rigidbody Methods

### The Golden Rule

**If an object has a Rigidbody, NEVER use `transform` to move it!**

```csharp
// ❌ WRONG - Breaks physics simulation
private void FixedUpdate()
{
    transform.position += Vector3.forward * speed * Time.fixedDeltaTime;
    // Object will move, but:
    // - Disables interpolation (causes stuttering)
    // - Ignores collisions (teleports through walls)
    // - Physics engine fights with your code (jitter)
    // - Rigidbody gets out of sync with transform
}

// ✓ CORRECT - Works with physics system
private void FixedUpdate()
{
    rb.MovePosition(rb.position + Vector3.forward * speed * Time.fixedDeltaTime);
    // Smooth, collision-aware, properly integrated with physics
}
```

### Transform Methods (No Rigidbody)

```csharp
// ✓ Use for non-physics objects (UI, cameras, static objects)
public class NonPhysicsMovement : MonoBehaviour
{
    public float speed = 5f;

    private void Update()  // Note: Update, not FixedUpdate
    {
        // OK - No Rigidbody on this object
        transform.position += Vector3.forward * speed * Time.deltaTime;

        // OK - Rotating a camera or UI element
        transform.Rotate(Vector3.up * 50f * Time.deltaTime);
    }
}
```

### Rigidbody Methods (With Rigidbody)

```csharp
// ✓ Use for physics objects
public class PhysicsMovement : MonoBehaviour
{
    private Rigidbody rb;
    public float speed = 5f;

    private void Awake()
    {
        rb = GetComponent<Rigidbody>();
    }

    private void FixedUpdate()  // Note: FixedUpdate for physics!
    {
        // Position-based movement
        Vector3 newPosition = rb.position + Vector3.forward * speed * Time.fixedDeltaTime;
        rb.MovePosition(newPosition);

        // Rotation-based movement
        Quaternion deltaRotation = Quaternion.Euler(Vector3.up * 50f * Time.fixedDeltaTime);
        rb.MoveRotation(rb.rotation * deltaRotation);
    }
}
```

### Method Comparison Table

| Method               | Use When           | Updates       | Notes                               |
| -------------------- | ------------------ | ------------- | ----------------------------------- |
| `transform.position` | No Rigidbody       | Update()      | Teleports, breaks physics           |
| `rb.position`        | Read position      | Any           | Reading only, don't assign directly |
| `rb.MovePosition()`  | Kinematic movement | FixedUpdate() | Smooth, collision-aware             |
| `rb.AddForce()`      | Dynamic movement   | FixedUpdate() | Realistic physics                   |
| `rb.linearVelocity`  | Direct velocity    | FixedUpdate() | Instant velocity change             |

## Force Modes Explained

Unity provides different `ForceMode` options for different physics scenarios:

```csharp
public enum ForceMode
{
    Force,          // Continuous force (scaled by mass and time)
    Acceleration,   // Continuous acceleration (mass-independent)
    Impulse,        // Instant force (one-time push)
    VelocityChange  // Instant velocity (mass-independent, one-time)
}
```

### When to Use Each ForceMode

```csharp
public class PhysicsCharacter : MonoBehaviour
{
    private Rigidbody rb;
    private bool jumpRequested;
    private float horizontalInput;

    [Header("Movement")]
    public float moveForce = 10f;
    public float jumpForce = 5f;

    private void Awake()
    {
        rb = GetComponent<Rigidbody>();
    }

    private void Update()
    {
        // Cache input in Update for responsiveness
        if (Input.GetKeyDown(KeyCode.Space))
            jumpRequested = true;

        horizontalInput = Input.GetAxis("Horizontal");
    }

    private void FixedUpdate()
    {
        // ForceMode.Force - Continuous push (call every FixedUpdate)
        // Use for: Jet engines, thrusters, wind, player movement
        rb.AddForce(Vector3.right * horizontalInput * moveForce, ForceMode.Force);

        // ForceMode.Acceleration - Continuous acceleration (ignores mass)
        // Use for: Gravity-like effects, magnetic fields
        rb.AddForce(Vector3.down * customGravity, ForceMode.Acceleration);

        // ForceMode.Impulse - Instant force (call once)
        // Use for: Jumping, explosions, kicks
        if (jumpRequested)
        {
            rb.AddForce(Vector3.up * jumpForce, ForceMode.Impulse);
            jumpRequested = false;
        }

        // ForceMode.VelocityChange - Instant velocity (ignores mass)
        // Use for: Dashes, speed boosts (when mass shouldn't matter)
        // Example: rb.AddForce(Vector3.forward * dashSpeed, ForceMode.VelocityChange);
    }
}
```

### Important: Continuous vs One-Time Forces

```csharp
// ❌ WRONG - Impulse is for one-time forces!
private void FixedUpdate()
{
    rb.AddForce(Vector3.up * 10f, ForceMode.Impulse);
    // Applied 50 times per second = way too much force!
}

// ✓ CORRECT - Use Force for continuous application
private void FixedUpdate()
{
    rb.AddForce(Vector3.up * 10f, ForceMode.Force);
    // Properly scaled for continuous application
}
```

## Collision and Triggers

### Collision Methods (Called on Colliders)

```csharp
// ✓ Use for physics objects that should collide
private void OnCollisionEnter(Collision collision)
{
    // Called once when collision starts
    Debug.Log($"Hit {collision.gameObject.name}");

    // Access collision details
    ContactPoint contact = collision.contacts[0];
    Vector3 hitPoint = contact.point;
    Vector3 hitNormal = contact.normal;
}

private void OnCollisionStay(Collision collision)
{
    // Called every frame while colliding
    // Use sparingly - can be expensive
}

private void OnCollisionExit(Collision collision)
{
    // Called once when collision ends
}
```

### Trigger Methods (Called on Trigger Colliders)

```csharp
// ✓ Use for detection zones (no physics collision)
private void OnTriggerEnter(Collider other)
{
    // Called once when entering trigger
    if (other.CompareTag("Player"))
    {
        ActivateTrap();
    }
}

private void OnTriggerStay(Collider other)
{
    // Called every frame while inside trigger
    if (other.CompareTag("Player"))
    {
        DamagePlayer();
    }
}

private void OnTriggerExit(Collider other)
{
    // Called once when leaving trigger
}
```

### Collision Matrix

Both objects need specific components for collision/trigger to work:

| Object A                       | Object B | Collision Event | Trigger Event |
| ------------------------------ | -------- | --------------- | ------------- |
| Rigidbody + Collider           | Collider | ✓ Yes           | -             |
| Rigidbody + Collider           | Trigger  | -               | ✓ Yes         |
| Kinematic Rigidbody + Collider | Collider | -               | -             |
| Kinematic Rigidbody + Collider | Trigger  | -               | ✓ Yes         |

**Key Point**: At least one object needs a non-kinematic Rigidbody for events to fire!

## Best Practices

### 1. Always Use FixedUpdate for Physics

```csharp
// ✓ CORRECT
[RequireComponent(typeof(Rigidbody))]
public class PhysicsController : MonoBehaviour
{
    private Rigidbody rb;
    private bool jumpRequested;
    private float horizontalInput;

    private void Awake()
    {
        rb = GetComponent<Rigidbody>();
    }

    // Cache input in Update (responsive)
    private void Update()
    {
        if (Input.GetKeyDown(KeyCode.Space))
            jumpRequested = true;

        horizontalInput = Input.GetAxis("Horizontal");
    }

    // Apply physics in FixedUpdate (stable)
    private void FixedUpdate()
    {
        rb.AddForce(Vector3.right * horizontalInput * 10f);

        if (jumpRequested)
        {
            rb.AddForce(Vector3.up * 5f, ForceMode.Impulse);
            jumpRequested = false;
        }
    }
}
```

### 2. Cache Rigidbody References

```csharp
// ✓ CORRECT - Cache in Awake
private Rigidbody rb;

private void Awake()
{
    rb = GetComponent<Rigidbody>();
}

// ❌ WRONG - GetComponent every frame
private void FixedUpdate()
{
    GetComponent<Rigidbody>().AddForce(Vector3.up);
}
```

### 3. Use Drag/Damping to Control Speed

```csharp
// ✓ GOOD - Use drag to naturally limit speed
private void Awake()
{
    rb = GetComponent<Rigidbody>();

    // Linear Drag - resists forward motion (0 = no resistance)
    rb.linearDamping = 2f;  // Inspector shows this as "Linear Drag"
    // Formula: velocity *= (1 - linearDamping * Time.fixedDeltaTime)

    // Angular Drag - resists rotation (0 = no resistance)
    rb.angularDamping = 0.5f;  // Inspector shows this as "Angular Drag"
}

// Example: Parachute increases drag when deployed
// Note: Modifying physics PROPERTIES (linearDamping, mass, etc.) in Update() is fine
// Only physics FORCES/VELOCITY must be in FixedUpdate()
private void Update()
{
    if (Input.GetKeyDown(KeyCode.Space))
    {
        parachuteOpen = !parachuteOpen;
        rb.linearDamping = parachuteOpen ? 20f : 2f;  // Toggle parachute
    }
}
```

### 4. Clamp Velocities to Avoid Instability

```csharp
// ✓ GOOD - Prevent excessive speeds (alternative to drag)
private void FixedUpdate()
{
    // Apply movement forces
    rb.AddForce(inputDirection * moveForce);

    // Clamp to maximum speed
    if (rb.linearVelocity.magnitude > maxSpeed)
    {
        rb.linearVelocity = rb.linearVelocity.normalized * maxSpeed;
    }
}
```

### 5. Use Appropriate Collision Detection Mode

```csharp
private void Awake()
{
    rb = GetComponent<Rigidbody>();

    // For fast-moving objects (bullets, projectiles)
    rb.collisionDetectionMode = CollisionDetectionMode.ContinuousDynamic;

    // For normal objects (default)
    rb.collisionDetectionMode = CollisionDetectionMode.Discrete;

    // For static objects that fast objects collide with
    rb.collisionDetectionMode = CollisionDetectionMode.Continuous;
}
```

### 6. Freeze Constraints for 2D Physics in 3D

```csharp
// ✓ GOOD - Lock unnecessary axes for 2D gameplay
private void Awake()
{
    rb = GetComponent<Rigidbody>();

    // Lock Z position and X/Y rotation for 2D platformer
    rb.constraints = RigidbodyConstraints.FreezePositionZ |
                     RigidbodyConstraints.FreezeRotationX |
                     RigidbodyConstraints.FreezeRotationY;
}
```

## Common Pitfalls

### Pitfall 1: Using Transform with Rigidbody

```csharp
// ❌ WRONG - "Works" but with severe quality issues
[RequireComponent(typeof(Rigidbody))]
public class BadPhysics : MonoBehaviour
{
    private void Update()
    {
        transform.position += Vector3.forward * Time.deltaTime;
        // Object WILL move forward, but:
        // - Rigidbody and transform are now out of sync
        // - Interpolation disabled = visible stuttering
        // - Collision detection unreliable = can phase through walls
        // - Physics engine tries to correct = fighting/jitter
        // Result: Looks unprofessional, unreliable collision detection
    }
}

// ✓ CORRECT - Use Rigidbody methods
public class GoodPhysics : MonoBehaviour
{
    private Rigidbody rb;

    private void Awake()
    {
        rb = GetComponent<Rigidbody>();
    }

    private void FixedUpdate()
    {
        rb.MovePosition(rb.position + Vector3.forward * Time.fixedDeltaTime);
        // Smooth, collision-aware, synchronized with physics
    }
}
```

### Pitfall 2: Physics in Update

```csharp
// ❌ WRONG - Variable timestep causes inconsistent physics
private void Update()
{
    rb.AddForce(Vector3.forward * 10f);
    // At 30fps: Force applied 30 times per second
    // At 144fps: Force applied 144 times per second
    // Same code, wildly different results!
    // Object WILL move, but ~5x faster on high-end PCs vs low-end
    // "Works on my machine" syndrome - breaks on different hardware
}

// ✓ CORRECT - Fixed timestep ensures consistent physics
private void FixedUpdate()
{
    rb.AddForce(Vector3.forward * 10f);
    // Always applied 50 times per second (default)
    // Consistent behavior on ALL hardware
}

// ⚠️ EXCEPTION - One-time Impulse forces CAN be called from Update
private void Update()
{
    if (Input.GetKeyDown(KeyCode.Space))
    {
        // This is acceptable - Impulse is a one-time force
        // Unity queues it for the next physics step
        rb.AddForce(Vector3.up * 5f, ForceMode.Impulse);
    }
}

// ✓ BETTER - Cache input and apply in FixedUpdate for consistency
private bool jumpRequested;

private void Update()
{
    if (Input.GetKeyDown(KeyCode.Space))
    {
        jumpRequested = true;
    }
}

private void FixedUpdate()
{
    if (jumpRequested)
    {
        rb.AddForce(Vector3.up * 5f, ForceMode.Impulse);
        jumpRequested = false;
    }
}
```

### Pitfall 3: Not Caching Input in Update

```csharp
// ⚠️ PROBLEMATIC - May miss input
private void FixedUpdate()
{
    // FixedUpdate runs 50 times per second
    // If player presses button between FixedUpdate calls, input is missed!
    if (Input.GetKeyDown(KeyCode.Space))
    {
        Jump();
    }
}

// ✓ CORRECT - Cache input in Update
private bool jumpRequested;

private void Update()
{
    // Update runs every frame - catches all input
    if (Input.GetKeyDown(KeyCode.Space))
    {
        jumpRequested = true;
    }
}

private void FixedUpdate()
{
    if (jumpRequested)
    {
        Jump();
        jumpRequested = false;
    }
}
```

### Pitfall 4: Modifying linearVelocity Directly for Movement

```csharp
// ⚠️ PROBLEMATIC - Works but bypasses physics simulation
private void FixedUpdate()
{
    rb.linearVelocity = new Vector3(Input.GetAxis("Horizontal") * speed, rb.linearVelocity.y, 0);
    // Object WILL move, but:
    // - Instant velocity change = feels arcade-y/unnatural
    // - Ignores friction, drag, and other physics forces
    // - No acceleration/deceleration = robotic feel
    // Sometimes acceptable for arcade-style games, but usually not ideal
}

// ✓ BETTER - Use forces for natural movement
private void FixedUpdate()
{
    float targetVelocity = Input.GetAxis("Horizontal") * speed;
    float velocityDifference = targetVelocity - rb.linearVelocity.x;

    rb.AddForce(Vector3.right * velocityDifference * acceleration, ForceMode.Force);
    // Smooth acceleration, works with physics system, feels natural
}
```

### Pitfall 5: Not Checking Grounded State

```csharp
// ❌ WRONG - Can jump mid-air
private bool isGrounded;

private void Update()
{
    if (Input.GetKeyDown(KeyCode.Space))
    {
        jumpRequested = true;
    }
}

private void FixedUpdate()
{
    if (jumpRequested)
    {
        // Player can jump infinitely without grounded check!
        rb.AddForce(Vector3.up * jumpForce, ForceMode.Impulse);
        jumpRequested = false;
    }
}

// ✓ CORRECT - Check if grounded before jumping
private bool isGrounded;
private bool jumpRequested;

private void Update()
{
    // Capture input every frame for responsiveness
    if (Input.GetKeyDown(KeyCode.Space) && isGrounded)
    {
        jumpRequested = true;
    }
}

private void FixedUpdate()
{
    // Apply physics in FixedUpdate
    if (jumpRequested)
    {
        rb.AddForce(Vector3.up * jumpForce, ForceMode.Impulse);
        jumpRequested = false;
    }
}

private void OnCollisionStay(Collision collision)
{
    // Check if colliding with ground
    isGrounded = collision.contacts[0].normal.y > 0.7f;
}

private void OnCollisionExit(Collision collision)
{
    isGrounded = false;
}
```

## Quick Reference

### Use FixedUpdate For

- Rigidbody movement
- AddForce calls
- Physics calculations
- MovePosition/MoveRotation
- linearVelocity modifications

### Use Update For

- Input reading
- Non-physics movement
- Animations
- UI updates
- Camera movement (unless following physics objects)

### ForceMode Quick Guide

- **Force**: Continuous push (call every FixedUpdate)
- **Acceleration**: Continuous push, ignore mass
- **Impulse**: One-time push (call once)
- **VelocityChange**: One-time velocity change, ignore mass

### Rigidbody Methods

- `MovePosition()`: Smooth position change with collision detection
- `MoveRotation()`: Smooth rotation change with collision detection
- `AddForce()`: Apply force (natural physics)
- `AddTorque()`: Apply rotational force
- `linearVelocity`: Direct velocity (use sparingly)
- `angularVelocity`: Direct angular velocity (use sparingly)

### Rigidbody Properties

- `linearDamping`: Linear drag/air resistance (called "Linear Drag" in Inspector)
- `angularDamping`: Rotational drag (called "Angular Drag" in Inspector)
- `mass`: Object mass (affects force calculations)
- `useGravity`: Enable/disable gravity
- `isKinematic`: Disable physics forces (use for manually controlled objects)

## Summary

**Golden Rules:**

1. **Use FixedUpdate for all physics** - `Update()` is for input caching only
2. **Cache input in Update, apply in FixedUpdate** - Responsive + consistent
3. **Use Rigidbody methods, not Transform** - `MovePosition()`, not `transform.position`
4. **Cache Rigidbody references** - In `Awake()` or `Start()`
5. **Use correct ForceMode** - `Force` for continuous, `Impulse` for one-shot
6. **Consider migrating to Unity's Input System** - Better than legacy polling
7. **Use drag/damping or clamp velocities** - Prevent excessive speeds
8. **Check grounded state** - Before allowing jumps

**Important Reality Check:**

Breaking these rules won't crash your game or prevent compilation. Your objects will still move.
However, you'll get:

- Visible jitter and stuttering (unprofessional feel)
- Inconsistent behavior across different frame rates and hardware
- Collision detection issues (tunneling, phasing through walls)
- Non-deterministic physics (nightmare for multiplayer)
- "Works on my machine" problems that break for players

The difference between following these practices and ignoring them is the difference between:

- ❌ "My character controller works but feels janky"
- ✅ "My character controller feels smooth and professional"

Remember: Unity's physics system is deterministic when used correctly. Follow these practices for
consistent, stable, professional-quality physics!
