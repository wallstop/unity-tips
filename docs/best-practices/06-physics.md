# Unity Physics Best Practices

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

1. Modifying physics in `Update()` instead of `FixedUpdate()`
2. Using `transform.position` instead of `Rigidbody.MovePosition()`
3. Not understanding the difference between variable and fixed timestep methods
4. Applying forces every frame without considering `Time.fixedDeltaTime`

## Table of Contents

- [Update vs FixedUpdate](#update-vs-fixedupdate)
- [Transform vs Rigidbody Methods](#transform-vs-rigidbody-methods)
- [Variable Timestep Physics Methods](#variable-timestep-physics-methods)
- [Force Application](#force-application)
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

    private void Awake()
    {
        rb = GetComponent<Rigidbody>();
    }

    // ✓ Use Update for input
    private void Update()
    {
        // Read input every frame for responsiveness
        if (Input.GetKeyDown(KeyCode.Space))
        {
            Jump();
        }
    }

    // ✓ Use FixedUpdate for physics
    private void FixedUpdate()
    {
        // Apply physics forces at fixed timestep
        float horizontal = Input.GetAxis("Horizontal");
        rb.AddForce(Vector3.right * horizontal * 10f);
    }

    private void Jump()
    {
        // Immediate physics response
        rb.AddForce(Vector3.up * 5f, ForceMode.Impulse);
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
}

// ✓ CORRECT - Works with physics system
private void FixedUpdate()
{
    rb.MovePosition(rb.position + Vector3.forward * speed * Time.fixedDeltaTime);
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

## Variable Timestep Physics Methods

### Understanding the Problem

```csharp
// ⚠️ IMPORTANT - This code is actually CORRECT in FixedUpdate!
private void FixedUpdate()
{
    // FixedUpdate runs at a FIXED timestep (50fps by default)
    // regardless of rendering frame rate!
    // At 144fps rendering: FixedUpdate still runs ~50 times/second
    // At 30fps rendering: FixedUpdate still runs ~50 times/second
    rb.AddForce(Vector3.up * 10f);
}

// ❌ WRONG - This WOULD vary with frame rate!
private void Update()
{
    // If running at 144fps: applies force 144 times per second
    // If running at 30fps: applies force 30 times per second
    // Same code, different results!
    rb.AddForce(Vector3.up * 10f);
}
```

### The Solution: Use Appropriate Force Modes

Unity provides different `ForceMode` options to handle this:

```csharp
public enum ForceMode
{
    Force,          // Continuous force (automatically scaled by Time.fixedDeltaTime)
    Acceleration,   // Continuous acceleration (mass-independent)
    Impulse,        // Instant force (one-time push)
    VelocityChange  // Instant velocity (mass-independent, one-time)
}
```

### ForceMode.Force (Default) - Continuous Force

```csharp
// ✓ CORRECT - Continuous force application
private void FixedUpdate()
{
    // Applies force accounting for mass and time
    // Automatically uses Time.fixedDeltaTime
    rb.AddForce(Vector3.forward * 10f, ForceMode.Force);

    // Same as:
    // rb.AddForce(Vector3.forward * 10f * rb.mass * Time.fixedDeltaTime);
}

// Use for: Continuous pushing (jet engines, thrusters, wind)
```

### ForceMode.Acceleration - Continuous Acceleration

```csharp
// ✓ CORRECT - Continuous acceleration (ignores mass)
private void FixedUpdate()
{
    // Applies acceleration regardless of mass
    // Useful when all objects should accelerate equally
    rb.AddForce(Vector3.forward * 10f, ForceMode.Acceleration);

    // Same as:
    // rb.AddForce(Vector3.forward * 10f * Time.fixedDeltaTime);
}

// Use for: Gravity-like effects, magnetic fields
```

### ForceMode.Impulse - Instant Force

```csharp
// ✓ CORRECT - One-time force application
private void OnJump()
{
    // Applies instant force accounting for mass
    // Call once, not every frame!
    rb.AddForce(Vector3.up * 5f, ForceMode.Impulse);

    // Same as:
    // rb.AddForce(Vector3.up * 5f * rb.mass);
}

// Use for: Jumping, explosions, kicks
```

### ForceMode.VelocityChange - Instant Velocity

```csharp
// ✓ CORRECT - Instant velocity change (ignores mass)
private void OnDash()
{
    // Changes velocity instantly, ignores mass
    // All objects get same velocity boost
    rb.AddForce(Vector3.forward * 10f, ForceMode.VelocityChange);

    // Almost same as:
    // rb.linearVelocity += Vector3.forward * 10f;
}

// Use for: Dashes, speed boosts (when mass shouldn't matter)
```

### Complete Example

```csharp
public class PhysicsCharacter : MonoBehaviour
{
    private Rigidbody rb;

    [Header("Movement")]
    public float moveForce = 10f;
    public float jumpForce = 5f;

    private void Awake()
    {
        rb = GetComponent<Rigidbody>();
    }

    private void Update()
    {
        // ✓ Read input in Update for responsiveness
        if (Input.GetKeyDown(KeyCode.Space))
        {
            Jump();
        }
    }

    private void FixedUpdate()
    {
        // ✓ Apply continuous movement force
        float horizontal = Input.GetAxis("Horizontal");

        // Continuous force - call every FixedUpdate
        rb.AddForce(Vector3.right * horizontal * moveForce, ForceMode.Force);
    }

    private void Jump()
    {
        // ✓ Apply instant impulse - call once
        rb.AddForce(Vector3.up * jumpForce, ForceMode.Impulse);
    }
}
```

## Force Application

### Continuous Forces (Apply in FixedUpdate)

```csharp
// ✓ CORRECT - Continuous forces
private void FixedUpdate()
{
    // Thrust / acceleration
    rb.AddForce(transform.forward * thrustPower, ForceMode.Force);

    // Gravity-like effect
    rb.AddForce(Vector3.down * customGravity, ForceMode.Acceleration);

    // Drag / air resistance
    rb.AddForce(-rb.linearVelocity * dragCoefficient, ForceMode.Force);
}
```

### Instant Forces (Apply Once)

```csharp
// ✓ CORRECT - One-time impacts
private void OnCollisionEnter(Collision collision)
{
    // Explosion force
    Vector3 direction = (transform.position - collision.contacts[0].point).normalized;
    rb.AddForce(direction * explosionForce, ForceMode.Impulse);
}

public void OnHit()
{
    // Knockback
    rb.AddForce(Vector3.back * knockbackForce, ForceMode.Impulse);
}
```

### Direct Velocity Manipulation

```csharp
// ⚠️ Use sparingly - bypasses physics simulation
private void FixedUpdate()
{
    // Clamp maximum speed
    if (rb.linearVelocity.magnitude > maxSpeed)
    {
        rb.linearVelocity = rb.linearVelocity.normalized * maxSpeed;
    }

    // Zero out vertical velocity (for 2D platformer feel)
    if (isGrounded)
    {
        rb.linearVelocity = new Vector3(rb.linearVelocity.x, 0, rb.linearVelocity.z);
    }
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

    private void Awake()
    {
        rb = GetComponent<Rigidbody>();
    }

    // Read input in Update (responsive)
    private void Update()
    {
        if (Input.GetKeyDown(KeyCode.Space))
            Jump();
    }

    // Apply physics in FixedUpdate (stable)
    private void FixedUpdate()
    {
        float move = Input.GetAxis("Horizontal");
        rb.AddForce(Vector3.right * move * 10f);
    }

    private void Jump()
    {
        rb.AddForce(Vector3.up * 5f, ForceMode.Impulse);
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

### 3. Use MovePosition for Kinematic Objects

```csharp
// ✓ CORRECT - Kinematic character movement
public class KinematicCharacter : MonoBehaviour
{
    private Rigidbody rb;
    public float speed = 5f;

    private void Awake()
    {
        rb = GetComponent<Rigidbody>();
        rb.isKinematic = true;  // Kinematic mode
    }

    private void FixedUpdate()
    {
        Vector3 movement = new Vector3(Input.GetAxis("Horizontal"), 0, Input.GetAxis("Vertical"));
        Vector3 newPosition = rb.position + movement * speed * Time.fixedDeltaTime;

        // MovePosition for smooth, collision-aware movement
        rb.MovePosition(newPosition);
    }
}
```

### 4. Clamp Velocities to Avoid Instability

```csharp
// ✓ GOOD - Prevent excessive speeds
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
// ❌ WRONG - Breaks physics
[RequireComponent(typeof(Rigidbody))]
public class BadPhysics : MonoBehaviour
{
    private void Update()
    {
        transform.position += Vector3.forward * Time.deltaTime;
        // Rigidbody and transform are now out of sync!
        // Physics will glitch!
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
}

// ✓ CORRECT - Fixed timestep ensures consistent physics
private void FixedUpdate()
{
    rb.AddForce(Vector3.forward * 10f);
    // Always applied 50 times per second (default)
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

### Pitfall 3: Wrong ForceMode for Continuous Forces

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

### Pitfall 4: Not Caching Input in Update

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

### Pitfall 5: Modifying linearVelocity Directly for Movement

```csharp
// ⚠️ PROBLEMATIC - Bypasses physics simulation
private void FixedUpdate()
{
    rb.linearVelocity = new Vector3(Input.GetAxis("Horizontal") * speed, rb.linearVelocity.y, 0);
    // Feels unnatural, no acceleration/deceleration
    // Ignores friction, drag, and other forces
}

// ✓ BETTER - Use forces for natural movement
private void FixedUpdate()
{
    float targetVelocity = Input.GetAxis("Horizontal") * speed;
    float velocityDifference = targetVelocity - rb.linearVelocity.x;

    rb.AddForce(Vector3.right * velocityDifference * acceleration, ForceMode.Force);
    // Smooth acceleration, works with physics system
}
```

### Pitfall 6: Not Checking Grounded State

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

## Summary

**Golden Rules:**

1. **Use FixedUpdate for all physics** - `Update()` is for rendering/input
2. **Use Rigidbody methods, not Transform** - `MovePosition()`, not `transform.position`
3. **Cache Rigidbody references** - In `Awake()` or `Start()`
4. **Use correct ForceMode** - `Force` for continuous, `Impulse` for one-shot
5. **Read input in Update** - Apply in FixedUpdate
6. **Use MovePosition for kinematic** - Smooth collision-aware movement
7. **Clamp velocities** - Prevent excessive speeds
8. **Check grounded state** - Before allowing jumps

Remember: Unity's physics system is deterministic when used correctly. Follow these practices for
consistent, stable physics!
