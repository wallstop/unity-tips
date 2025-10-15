# Code Examples & Recipes

Ready-to-use code patterns for common animation scenarios in Animancer Pro 8.

> **📖 How to use this guide:** Each example is self-contained and ready to copy-paste. Jump to what
> you need—you don't have to read everything!

---

## Table of Contents

1. [Directional Animation Switching](#directional-animation-switching-seamless) ⭐ **Start here for
   seamless directional animations!**
2. [Basic Character Controller](#basic-character-controller)
3. [Attack System with Events](#attack-system-with-events)
4. [Multi-Sprite Character](#multi-sprite-character)
5. [Movement Mixer (Idle/Walk/Run)](#movement-mixer-idlewalkrun)
6. [State Machine Character](#state-machine-character)
7. [Combat System](#combat-system)
8. [Footstep System](#footstep-system)
9. [Hit Reaction System](#hit-reaction-system)
10. [Interactable NPC](#interactable-npc)
11. [Platformer Character](#platformer-character)
12. [Animation Chaining](#animation-chaining)
13. [Object Pooling with Animancer](#object-pooling-with-animancer)

---

## Directional Animation Switching (Seamless)

**The Pattern:** Switch between directional animations (walk_left, walk_right, walk_up, walk_down)
without restarting the cycle.

**Key Insight:** If all your directional animations are the same length, you can preserve the walk
cycle position when changing direction!

```csharp
using UnityEngine;
using Animancer;

public class DirectionalCharacter : MonoBehaviour
{
    [Header("Components")]
    [SerializeField] private AnimancerComponent _animancer;

    [Header("Directional Walk Clips (all same length!)")]
    [SerializeField] private AnimationClip _walkUp;
    [SerializeField] private AnimationClip _walkDown;
    [SerializeField] private AnimationClip _walkLeft;
    [SerializeField] private AnimationClip _walkRight;

    void Update()
    {
        Vector2 input = new Vector2(Input.GetAxis("Horizontal"), Input.GetAxis("Vertical"));

        if (input.magnitude > 0.1f)
        {
            // Determine which direction to face
            AnimationClip targetClip = GetDirectionalClip(input);
            PlayDirectional(targetClip);
        }
    }

    AnimationClip GetDirectionalClip(Vector2 direction)
    {
        // Simple 4-direction logic
        if (Mathf.Abs(direction.x) > Mathf.Abs(direction.y))
        {
            return direction.x > 0 ? _walkRight : _walkLeft;
        }
        else
        {
            return direction.y > 0 ? _walkUp : _walkDown;
        }
    }

    void PlayDirectional(AnimationClip newClip)
    {
        // 1. Check if we're already playing this clip
        if (_animancer.States.Current?.Clip == newClip)
            return;

        // 2. Grab current normalized time (where in the walk cycle are we?)
        float normalizedTime = _animancer.States.Current?.NormalizedTime % 1f ?? 0f;

        // 3. Play the new direction's animation
        AnimancerState newState = _animancer.Play(newClip);

        // 4. Continue from the same point in the cycle (THE MAGIC!)
        newState.NormalizedTime = normalizedTime;

        // Result: Seamless direction changes - no foot sliding or jarring restarts!
    }
}
```

**Why This Works:**

- All directional animations are the same length
- NormalizedTime (0-1) is clip-independent
- Setting the new clip's time to match the old preserves the cycle

**Official Documentation:**
[Animancer — Performance Tips](https://kybernetik.com.au/animancer/docs/manual/playing/states#performance)

---

## Basic Character Controller

A simple character with idle, walk, and run animations based on input.

```csharp
using UnityEngine;
using Animancer;

public class BasicCharacter : MonoBehaviour
{
    [Header("Components")]
    [SerializeField] private AnimancerComponent _animancer;
    [SerializeField] private Rigidbody2D _rigidbody;

    [Header("Animation Clips")]
    [SerializeField] private AnimationClip _idle;
    [SerializeField] private AnimationClip _walk;
    [SerializeField] private AnimationClip _run;

    [Header("Movement Settings")]
    [SerializeField] private float _walkSpeed = 3f;
    [SerializeField] private float _runSpeed = 6f;

    void Update()
    {
        // Get input
        float horizontal = Input.GetAxis("Horizontal");
        bool isRunning = Input.GetKey(KeyCode.LeftShift);

        // Determine animation
        if (Mathf.Abs(horizontal) < 0.1f)
        {
            PlayIdle();
        }
        else if (isRunning)
        {
            PlayRun();
            Move(horizontal, _runSpeed);
        }
        else
        {
            PlayWalk();
            Move(horizontal, _walkSpeed);
        }
    }

    void PlayIdle()
    {
        if (!_animancer.IsPlaying(_idle))
            _animancer.Play(_idle, fadeDuration: 0.2f);
    }

    void PlayWalk()
    {
        if (!_animancer.IsPlaying(_walk))
            _animancer.Play(_walk, fadeDuration: 0.25f);
    }

    void PlayRun()
    {
        if (!_animancer.IsPlaying(_run))
            _animancer.Play(_run, fadeDuration: 0.3f);
    }

    void Move(float direction, float speed)
    {
        _rigidbody.velocity = new Vector2(direction * speed, _rigidbody.velocity.y);

        // Flip sprite based on direction
        if (direction < 0)
            transform.localScale = new Vector3(-1, 1, 1);
        else if (direction > 0)
            transform.localScale = new Vector3(1, 1, 1);
    }
}
```

---

## Attack System with Events

A character that can attack with proper damage timing via animation events.

```csharp
using UnityEngine;
using Animancer;

public class AttackSystem : MonoBehaviour
{
    [Header("Components")]
    [SerializeField] private AnimancerComponent _animancer;
    [SerializeField] private Collider2D _damageCollider;

    [Header("Animation Clips")]
    [SerializeField] private AnimationClip _idle;
    [SerializeField] private AnimationClip _lightAttack;
    [SerializeField] private AnimationClip _heavyAttack;

    [Header("Settings")]
    [SerializeField] private int _lightDamage = 10;
    [SerializeField] private int _heavyDamage = 25;

    private bool _isAttacking = false;

    void Start()
    {
        _damageCollider.enabled = false;
        _animancer.Play(_idle);
    }

    void Update()
    {
        if (_isAttacking) return;

        if (Input.GetKeyDown(KeyCode.J))
        {
            LightAttack();
        }
        else if (Input.GetKeyDown(KeyCode.K))
        {
            HeavyAttack();
        }
    }

    void LightAttack()
    {
        _isAttacking = true;

        AnimancerState state = _animancer.Play(_lightAttack, fadeDuration: 0.05f);
        state.OwnedEvents.Clear();

        // Enable damage collider during swing
        state.OwnedEvents.Add(0.3f, () => {
            _damageCollider.enabled = true;
            Debug.Log($"Light attack! Damage: {_lightDamage}");
        });

        // Disable damage collider after swing
        state.OwnedEvents.Add(0.6f, () => {
            _damageCollider.enabled = false;
        });

        // Return to idle
        state.OwnedEvents.Add(1.0f, () => {
            _isAttacking = false;
            _animancer.Play(_idle);
        });
    }

    void HeavyAttack()
    {
        _isAttacking = true;

        AnimancerState state = _animancer.Play(_heavyAttack, fadeDuration: 0.05f);
        state.OwnedEvents.Clear();

        // Longer wind-up for heavy attack
        state.OwnedEvents.Add(0.5f, () => {
            _damageCollider.enabled = true;
            Debug.Log($"Heavy attack! Damage: {_heavyDamage}");
        });

        state.OwnedEvents.Add(0.8f, () => {
            _damageCollider.enabled = false;
        });

        state.OwnedEvents.Add(1.0f, () => {
            _isAttacking = false;
            _animancer.Play(_idle);
        });
    }

    void OnTriggerEnter2D(Collider2D collision)
    {
        if (collision.CompareTag("Enemy"))
        {
            // Apply damage to enemy
            var enemy = collision.GetComponent<Enemy>();
            if (enemy != null)
            {
                int damage = _animancer.IsPlaying(_heavyAttack) ? _heavyDamage : _lightDamage;
                enemy.TakeDamage(damage);
            }
        }
    }
}
```

---

## Multi-Sprite Character

Synchronizing separate sprite layers (body, arms, legs) without desync.

```csharp
using UnityEngine;
using Animancer;

public class MultiSpriteCharacter : MonoBehaviour
{
    [Header("Animancer Components")]
    [SerializeField] private AnimancerComponent _bodyAnimancer;
    [SerializeField] private AnimancerComponent _leftArmAnimancer;
    [SerializeField] private AnimancerComponent _rightArmAnimancer;

    [Header("Animation Clips")]
    [SerializeField] private AnimationClip _idle;
    [SerializeField] private AnimationClip _walk;

    void Start()
    {
        PlaySyncedAnimation(_idle, keepTime: false);
    }

    void Update()
    {
        if (Input.GetAxis("Horizontal") != 0)
        {
            PlaySyncedAnimation(_walk, keepTime: true);
        }
        else
        {
            PlaySyncedAnimation(_idle, keepTime: true);
        }
    }

    /// <summary>
    /// Plays an animation on all sprite layers in sync.
    /// </summary>
    /// <param name="clip">The animation clip to play</param>
    /// <param name="keepTime">If true, preserve normalized time (prevents popping)</param>
    void PlaySyncedAnimation(AnimationClip clip, bool keepTime)
    {
        if (clip == null) return;

        // Check if already playing on body
        if (_bodyAnimancer.IsPlaying(clip)) return;

        // Get current normalized time for sync
        float normalizedTime = 0f;
        if (keepTime && _bodyAnimancer.States.Current != null)
        {
            normalizedTime = _bodyAnimancer.States.Current.NormalizedTime % 1f;
        }

        // Play on all sprites at the same time
        AnimancerState bodyState = _bodyAnimancer.Play(clip);
        bodyState.NormalizedTime = normalizedTime;

        AnimancerState leftArmState = _leftArmAnimancer.Play(clip);
        leftArmState.NormalizedTime = normalizedTime;

        AnimancerState rightArmState = _rightArmAnimancer.Play(clip);
        rightArmState.NormalizedTime = normalizedTime;
    }
}
```

---

## Movement Mixer (Idle/Walk/Run)

Smooth blending between movement speeds using a Linear Mixer.

```csharp
using UnityEngine;
using Animancer;

public class MovementMixer : MonoBehaviour
{
    [Header("Components")]
    [SerializeField] private AnimancerComponent _animancer;
    [SerializeField] private Rigidbody2D _rigidbody;

    [Header("Movement Clips")]
    [SerializeField] private AnimationClip _idle;
    [SerializeField] private AnimationClip _walk;
    [SerializeField] private AnimationClip _run;

    [Header("Settings")]
    [SerializeField] private float _maxSpeed = 10f;

    private LinearMixerState _movementMixer;

    void Start()
    {
        // Create linear mixer
        _movementMixer = new LinearMixerState();

        // Add animations at speed thresholds
        _movementMixer.Add(_idle, threshold: 0f);
        _movementMixer.Add(_walk, threshold: 5f);
        _movementMixer.Add(_run,  threshold: 10f);

        // Play the mixer
        _animancer.Play(_movementMixer);
    }

    void Update()
    {
        // Get input
        float horizontal = Input.GetAxis("Horizontal");
        float targetSpeed = Mathf.Abs(horizontal) * _maxSpeed;

        // Update mixer parameter (automatically blends)
        _movementMixer.Parameter = targetSpeed;

        // Move character
        _rigidbody.velocity = new Vector2(horizontal * _maxSpeed, _rigidbody.velocity.y);

        // Flip sprite
        if (horizontal < 0)
            transform.localScale = new Vector3(-1, 1, 1);
        else if (horizontal > 0)
            transform.localScale = new Vector3(1, 1, 1);
    }
}
```

---

## State Machine Character

Using Animancer's FSM for clean state management.

```csharp
using UnityEngine;
using Animancer;
using Animancer.FSM;

public class StateMachineCharacter : MonoBehaviour
{
    [Header("Components")]
    [SerializeField] private AnimancerComponent _animancer;

    [Header("Animation Clips")]
    [SerializeField] private AnimationClip _idle;
    [SerializeField] private AnimationClip _walk;
    [SerializeField] private AnimationClip _jump;
    [SerializeField] private AnimationClip _attack;

    private StateMachine<CharacterState>.WithDefault _stateMachine;

    // State instances
    private IdleState _idleState;
    private WalkState _walkState;
    private JumpState _jumpState;
    private AttackState _attackState;

    void Awake()
    {
        // Create state machine
        _stateMachine = new StateMachine<CharacterState>.WithDefault();

        // Create states
        _idleState = new IdleState(this, _idle);
        _walkState = new WalkState(this, _walk);
        _jumpState = new JumpState(this, _jump);
        _attackState = new AttackState(this, _attack);

        // Set default state
        _stateMachine.DefaultState = _idleState;
    }

    void Update()
    {
        // Input handling
        if (Input.GetKeyDown(KeyCode.Space))
        {
            _stateMachine.TrySetState(_attackState);
        }
        else if (Input.GetKeyDown(KeyCode.W))
        {
            _stateMachine.TrySetState(_jumpState);
        }
        else if (Input.GetAxis("Horizontal") != 0)
        {
            _stateMachine.TrySetState(_walkState);
        }
        else
        {
            _stateMachine.TrySetState(_idleState);
        }
    }

    public AnimancerComponent Animancer => _animancer;
    public StateMachine<CharacterState> StateMachine => _stateMachine;
}

// Base state class
public abstract class CharacterState : IState
{
    protected StateMachineCharacter _character;
    protected AnimationClip _clip;

    public CharacterState(StateMachineCharacter character, AnimationClip clip)
    {
        _character = character;
        _clip = clip;
    }

    public virtual bool CanEnterState => true;
    public virtual bool CanExitState => true;

    public virtual void OnEnterState()
    {
        _character.Animancer.Play(_clip);
    }

    public virtual void OnExitState() { }
}

// Idle state
public class IdleState : CharacterState
{
    public IdleState(StateMachineCharacter character, AnimationClip clip)
        : base(character, clip) { }
}

// Walk state
public class WalkState : CharacterState
{
    public WalkState(StateMachineCharacter character, AnimationClip clip)
        : base(character, clip) { }
}

// Jump state
public class JumpState : CharacterState
{
    public JumpState(StateMachineCharacter character, AnimationClip clip)
        : base(character, clip) { }

    public override bool CanExitState => false;  // Can't interrupt jump

    public override void OnEnterState()
    {
        AnimancerState state = _character.Animancer.Play(_clip);
        state.OwnedEvents.Clear();

        // Return to idle when jump completes
        state.OwnedEvents.Add(1.0f, () => {
            _character.StateMachine.TrySetState(_character.StateMachine.DefaultState);
        });
    }
}

// Attack state
public class AttackState : CharacterState
{
    public AttackState(StateMachineCharacter character, AnimationClip clip)
        : base(character, clip) { }

    public override bool CanExitState => false;  // Can't interrupt attack

    public override void OnEnterState()
    {
        AnimancerState state = _character.Animancer.Play(_clip);
        state.OwnedEvents.Clear();

        // Return to idle when attack completes
        state.OwnedEvents.Add(1.0f, () => {
            _character.StateMachine.TrySetState(_character.StateMachine.DefaultState);
        });
    }
}
```

---

## Combat System

A complete combat system with combos and hit detection.

```csharp
using UnityEngine;
using Animancer;

public class CombatSystem : MonoBehaviour
{
    [Header("Components")]
    [SerializeField] private AnimancerComponent _animancer;
    [SerializeField] private Collider2D _hitCollider;

    [Header("Combo Clips")]
    [SerializeField] private AnimationClip _idle;
    [SerializeField] private AnimationClip _combo1;
    [SerializeField] private AnimationClip _combo2;
    [SerializeField] private AnimationClip _combo3;

    [Header("Settings")]
    [SerializeField] private float _comboWindow = 0.5f;

    private int _comboIndex = 0;
    private float _lastAttackTime;
    private bool _isAttacking = false;
    private bool _canContinueCombo = false;

    void Start()
    {
        _hitCollider.enabled = false;
        _animancer.Play(_idle);
    }

    void Update()
    {
        if (Input.GetKeyDown(KeyCode.Space))
        {
            if (_canContinueCombo)
            {
                ContinueCombo();
            }
            else if (!_isAttacking)
            {
                StartCombo();
            }
        }

        // Reset combo if window expired
        if (Time.time - _lastAttackTime > _comboWindow && !_isAttacking)
        {
            ResetCombo();
        }
    }

    void StartCombo()
    {
        _comboIndex = 0;
        PerformAttack(_combo1);
    }

    void ContinueCombo()
    {
        _comboIndex++;

        switch (_comboIndex)
        {
            case 1:
                PerformAttack(_combo2);
                break;
            case 2:
                PerformAttack(_combo3);
                break;
            default:
                ResetCombo();
                StartCombo();
                break;
        }

        _canContinueCombo = false;
    }

    void PerformAttack(AnimationClip attackClip)
    {
        _isAttacking = true;
        _lastAttackTime = Time.time;

        AnimancerState state = _animancer.Play(attackClip, fadeDuration: 0.05f);
        state.OwnedEvents.Clear();

        // Enable hitbox during attack
        state.OwnedEvents.Add(0.3f, () => {
            _hitCollider.enabled = true;
            Debug.Log($"Combo {_comboIndex + 1}!");
        });

        // Disable hitbox
        state.OwnedEvents.Add(0.6f, () => {
            _hitCollider.enabled = false;
        });

        // Combo window opens
        state.OwnedEvents.Add(0.7f, () => {
            _canContinueCombo = true;
        });

        // Attack ends
        state.OwnedEvents.Add(1.0f, () => {
            _isAttacking = false;
            if (!_canContinueCombo)
            {
                ResetCombo();
                _animancer.Play(_idle);
            }
        });
    }

    void ResetCombo()
    {
        _comboIndex = 0;
        _canContinueCombo = false;
    }
}
```

---

## Footstep System

Play footstep sounds at specific animation frames.

```csharp
using UnityEngine;
using Animancer;

public class FootstepSystem : MonoBehaviour
{
    [Header("Components")]
    [SerializeField] private AnimancerComponent _animancer;
    [SerializeField] private AudioSource _audioSource;

    [Header("Footstep Sounds")]
    [SerializeField] private AudioClip[] _footstepSounds;

    [Header("Animation Clips")]
    [SerializeField] private AnimationClip _walk;
    [SerializeField] private AnimationClip _run;

    void Start()
    {
        PlayWalk();
    }

    void PlayWalk()
    {
        AnimancerState state = _animancer.Play(_walk);

        // Use SharedEvents for consistent footsteps
        if (state.SharedEvents == null)
        {
            state.SharedEvents = new AnimancerEvent.Sequence();
        }

        state.SharedEvents.Clear();

        // Add footstep events (adjust times based on your animation)
        state.SharedEvents.Add(0.2f, PlayFootstep);  // Left foot
        state.SharedEvents.Add(0.7f, PlayFootstep);  // Right foot
    }

    void PlayRun()
    {
        AnimancerState state = _animancer.Play(_run);

        if (state.SharedEvents == null)
        {
            state.SharedEvents = new AnimancerEvent.Sequence();
        }

        state.SharedEvents.Clear();

        // Faster footsteps for running
        state.SharedEvents.Add(0.15f, PlayFootstep);
        state.SharedEvents.Add(0.4f, PlayFootstep);
        state.SharedEvents.Add(0.65f, PlayFootstep);
        state.SharedEvents.Add(0.9f, PlayFootstep);
    }

    void PlayFootstep()
    {
        if (_footstepSounds.Length == 0) return;

        // Play random footstep sound
        AudioClip clip = _footstepSounds[Random.Range(0, _footstepSounds.Length)];
        _audioSource.PlayOneShot(clip);
    }
}
```

---

## Hit Reaction System

Character reacts to damage with hit stun animation.

```csharp
using UnityEngine;
using Animancer;

public class HitReactionSystem : MonoBehaviour
{
    [Header("Components")]
    [SerializeField] private AnimancerComponent _animancer;

    [Header("Animation Clips")]
    [SerializeField] private AnimationClip _idle;
    [SerializeField] private AnimationClip _hitLight;
    [SerializeField] private AnimationClip _hitHeavy;
    [SerializeField] private AnimationClip _death;

    [Header("Health")]
    [SerializeField] private int _maxHealth = 100;
    private int _currentHealth;

    private bool _isInHitStun = false;

    void Start()
    {
        _currentHealth = _maxHealth;
        _animancer.Play(_idle);
    }

    public void TakeDamage(int damage, bool isHeavy = false)
    {
        _currentHealth -= damage;

        if (_currentHealth <= 0)
        {
            Die();
            return;
        }

        // Play appropriate hit reaction
        PlayHitReaction(isHeavy);
    }

    void PlayHitReaction(bool isHeavy)
    {
        if (_isInHitStun) return;

        _isInHitStun = true;

        AnimationClip hitClip = isHeavy ? _hitHeavy : _hitLight;
        AnimancerState state = _animancer.Play(hitClip, fadeDuration: 0.05f);
        state.OwnedEvents.Clear();

        // Return to idle after hit stun
        state.OwnedEvents.Add(1.0f, () => {
            _isInHitStun = false;
            _animancer.Play(_idle);
        });
    }

    void Die()
    {
        AnimancerState state = _animancer.Play(_death, fadeDuration: 0.1f);
        state.OwnedEvents.Clear();

        // Disable character after death animation
        state.OwnedEvents.Add(1.0f, () => {
            gameObject.SetActive(false);
        });
    }
}
```

---

## Interactable NPC

NPC that plays reaction animations when interacted with.

```csharp
using UnityEngine;
using Animancer;

public class InteractableNPC : MonoBehaviour
{
    [Header("Components")]
    [SerializeField] private AnimancerComponent _animancer;

    [Header("Animation Clips")]
    [SerializeField] private AnimationClip _idle;
    [SerializeField] private AnimationClip _greetingClip;
    [SerializeField] private AnimationClip _greetingLoopClip;
    [SerializeField] private AnimationClip _farewellClip;

    private bool _isInteracting = false;

    void Start()
    {
        _animancer.Play(_idle);
    }

    public void OnInteractionStart()
    {
        if (_isInteracting) return;

        _isInteracting = true;

        // Play greeting, then loop
        AnimancerState greeting = _animancer.Play(_greetingClip);
        greeting.OwnedEvents.Clear();

        greeting.OwnedEvents.Add(1.0f, () => {
            // Transition to looping stance
            if (_greetingLoopClip != null)
            {
                _animancer.Play(_greetingLoopClip);
            }
        });
    }

    public void OnInteractionEnd()
    {
        if (!_isInteracting) return;

        // Play farewell, return to idle
        AnimancerState farewell = _animancer.Play(_farewellClip);
        farewell.OwnedEvents.Clear();

        farewell.OwnedEvents.Add(1.0f, () => {
            _isInteracting = false;
            _animancer.Play(_idle);
        });
    }
}
```

---

## Platformer Character

Complete platformer with jump, land, and air animations.

```csharp
using UnityEngine;
using Animancer;

public class PlatformerCharacter : MonoBehaviour
{
    [Header("Components")]
    [SerializeField] private AnimancerComponent _animancer;
    [SerializeField] private Rigidbody2D _rigidbody;

    [Header("Animation Clips")]
    [SerializeField] private AnimationClip _idle;
    [SerializeField] private AnimationClip _run;
    [SerializeField] private AnimationClip _jump;
    [SerializeField] private AnimationClip _fall;
    [SerializeField] private AnimationClip _land;

    [Header("Settings")]
    [SerializeField] private float _moveSpeed = 5f;
    [SerializeField] private float _jumpForce = 10f;
    [SerializeField] private LayerMask _groundLayer;

    private bool _isGrounded;
    private bool _wasGrounded;

    void Update()
    {
        CheckGrounded();
        HandleInput();
        UpdateAnimation();
    }

    void CheckGrounded()
    {
        _wasGrounded = _isGrounded;

        // Simple ground check (improve with raycasts in production)
        _isGrounded = Physics2D.Raycast(transform.position, Vector2.down, 1.1f, _groundLayer);

        // Just landed
        if (_isGrounded && !_wasGrounded)
        {
            OnLand();
        }
    }

    void HandleInput()
    {
        // Movement
        float horizontal = Input.GetAxis("Horizontal");
        _rigidbody.velocity = new Vector2(horizontal * _moveSpeed, _rigidbody.velocity.y);

        // Jump
        if (Input.GetKeyDown(KeyCode.Space) && _isGrounded)
        {
            Jump();
        }

        // Flip sprite
        if (horizontal < 0)
            transform.localScale = new Vector3(-1, 1, 1);
        else if (horizontal > 0)
            transform.localScale = new Vector3(1, 1, 1);
    }

    void UpdateAnimation()
    {
        // Don't update if playing land animation
        if (_animancer.IsPlaying(_land))
            return;

        if (!_isGrounded)
        {
            // In air: jump or fall based on velocity
            if (_rigidbody.velocity.y > 0.1f)
            {
                if (!_animancer.IsPlaying(_jump))
                    _animancer.Play(_jump, fadeDuration: 0.1f);
            }
            else
            {
                if (!_animancer.IsPlaying(_fall))
                    _animancer.Play(_fall, fadeDuration: 0.2f);
            }
        }
        else
        {
            // On ground: idle or run
            float speed = Mathf.Abs(_rigidbody.velocity.x);

            if (speed > 0.1f)
            {
                if (!_animancer.IsPlaying(_run))
                    _animancer.Play(_run, fadeDuration: 0.2f);
            }
            else
            {
                if (!_animancer.IsPlaying(_idle))
                    _animancer.Play(_idle, fadeDuration: 0.2f);
            }
        }
    }

    void Jump()
    {
        _rigidbody.velocity = new Vector2(_rigidbody.velocity.x, _jumpForce);
        _animancer.Play(_jump, fadeDuration: 0.05f);
    }

    void OnLand()
    {
        AnimancerState land = _animancer.Play(_land, fadeDuration: 0.05f);
        land.OwnedEvents.Clear();

        // Return to movement after landing
        land.OwnedEvents.Add(1.0f, () => {
            // Animation will update naturally in UpdateAnimation()
        });
    }
}
```

---

## Animation Chaining

Chain multiple animations in sequence.

```csharp
using UnityEngine;
using Animancer;
using System.Collections.Generic;

public class AnimationChain : MonoBehaviour
{
    [Header("Components")]
    [SerializeField] private AnimancerComponent _animancer;

    [Header("Animation Sequence")]
    [SerializeField] private AnimationClip[] _animationSequence;

    private Queue<AnimationClip> _animationQueue = new Queue<AnimationClip>();

    void Start()
    {
        PlaySequence(_animationSequence);
    }

    /// <summary>
    /// Play a sequence of animations in order.
    /// </summary>
    public void PlaySequence(AnimationClip[] clips)
    {
        _animationQueue.Clear();

        foreach (var clip in clips)
        {
            _animationQueue.Enqueue(clip);
        }

        PlayNext();
    }

    void PlayNext()
    {
        if (_animationQueue.Count == 0)
        {
            Debug.Log("Animation sequence complete!");
            return;
        }

        AnimationClip nextClip = _animationQueue.Dequeue();
        AnimancerState state = _animancer.Play(nextClip);
        state.OwnedEvents.Clear();

        // Play next animation when current finishes
        state.OwnedEvents.Add(1.0f, PlayNext);
    }
}
```

---

## Object Pooling with Animancer

Properly reset animations for pooled objects.

```csharp
using UnityEngine;
using Animancer;

public class PooledEnemy : MonoBehaviour
{
    [Header("Components")]
    [SerializeField] private AnimancerComponent _animancer;

    [Header("Animation Clips")]
    [SerializeField] private AnimationClip _spawn;
    [SerializeField] private AnimationClip _idle;

    void Awake()
    {
        // Reset animations when object is disabled (pooled)
        _animancer.ActionOnDisable = AnimancerComponent.DisableAction.Reset;
    }

    void OnEnable()
    {
        // Play spawn animation
        AnimancerState spawn = _animancer.Play(_spawn);
        spawn.OwnedEvents.Clear();

        // Transition to idle after spawn
        spawn.OwnedEvents.Add(1.0f, () => {
            _animancer.Play(_idle);
        });
    }

    void OnDisable()
    {
        // Animancer automatically resets thanks to ActionOnDisable
    }

    public void ReturnToPool()
    {
        gameObject.SetActive(false);
        // When reactivated, OnEnable will play spawn from the beginning
    }
}
```

---

## Key Takeaways

✅ **Always check IsPlaying()** before replaying animations ✅ **Clear OwnedEvents** before adding
new ones ✅ **Use NormalizedTime** to sync multi-sprite characters ✅ **Leverage animation events**
for gameplay logic (damage windows, footsteps) ✅ **Set ActionOnDisable** for pooled objects ✅
**Separate animation from gameplay logic** (use dedicated components) ✅ **Cache AnimationClip
references** (don't load at runtime)

---

## Next Steps

- **[Getting Started](./01-GETTING-STARTED.md)** - Introduction to Animancer
- **[Core Concepts](./02-CORE-CONCEPTS.md)** - Understanding the fundamentals
- **[Advanced Techniques](./03-ADVANCED-TECHNIQUES.md)** - Layers, mixers, state machines
- **[Best Practices](./04-BEST-PRACTICES.md)** - Avoid common pitfalls

---

**Official Documentation:**
[kybernetik.com.au/animancer/docs/](https://kybernetik.com.au/animancer/docs/)
