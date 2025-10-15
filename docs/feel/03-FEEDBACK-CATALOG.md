# Feedback Catalog

> **Quick Reference**: Feel includes 150+ feedbacks across 15 categories. Use this guide to find the
> perfect feedback for your needs.

## How to Use This Catalog

Each feedback listing includes:

- **What it does**: Brief description
- **Common uses**: Typical scenarios
- **Key settings**: Important Inspector parameters
- **Example**: Quick setup guide

**Navigation**: Jump to any category:

- [Audio](#audio) | [Camera](#camera) | [Events](#events) | [GameObject](#gameobject)
- [Haptics](#haptics-nice-vibrations) | [Light](#light) | [Materials](#materials--renderer) |
  [Particles](#particles)
- [Physics](#physics) | [Post Processing](#post-processing) | [Text](#text) | [Time](#time)
- [Transform](#transform) | [UI](#ui) | [Debug](#debug)

---

## Audio

Audio feedbacks control sound playback, mixing, and effects.

### MMF_Sound ⭐ Most Used

**What it does**: Plays an audio clip with extensive control options.

**Common uses**: SFX for jumps, hits, UI clicks, pickups

**Key settings**:

- **Sfx**: AudioClip to play
- **Volume**: 0-1 loudness
- **Pitch**: 0.5-2.0 (affects speed/tone)
- **Random Volume/Pitch**: Add variation to avoid repetition

**Example: Jump Sound**

```
Add Feedback → Audio → Sound
  - Sfx: Jump.wav
  - Volume: 0.7
  - Random Pitch: Min 0.95, Max 1.05 ← slight variation
```

**Pro Tip**: Use Random Pitch on repeated sounds (footsteps, gunshots) to avoid robotic repetition.

---

### MMF_AudioSource

**What it does**: Controls an existing AudioSource component (play, pause, stop).

**Common uses**: Background music control, ambient loops

**Key settings**:

- **Target AudioSource**: The AudioSource to control
- **Mode**: Play, Pause, Stop, Resume

**Example: Stop Music on Boss Death**

```
Add Feedback → Audio → AudioSource
  - Target AudioSource: BackgroundMusicSource
  - Mode: Stop
  - Fade Duration: 0.5s ← smooth fadeout
```

---

### MMF_AudioSource_Pitch / Volume

**What it does**: Animates AudioSource pitch or volume over time.

**Common uses**: Tension building, slow-motion effects, fade-ins/outs

**Example: Slow Motion Audio Effect**

```
Add Feedback → Audio → AudioSource Pitch
  - Target: All AudioSources
  - Destination Pitch: 0.5 ← half-speed, deeper sound
  - Duration: 0.2s
```

---

### MMF_AudioMixer

**What it does**: Changes Audio Mixer exposed parameters (like master volume, effect wet mix).

**Common uses**: Dynamic audio mixing, setting changes, focus modes

**Example: Lower Music During Dialogue**

```
Add Feedback → Audio → Audio Mixer
  - Target Mixer: MainAudioMixer
  - Exposed Parameter: "MusicVolume"
  - Target Value: -20 dB ← quieter
  - Duration: 0.5s
```

---

## Camera

Camera feedbacks add impact and focus through camera manipulation.

### MMF_CameraShake ⭐ Most Used

**What it does**: Shakes the camera using MMCinemachineShake or custom shake.

**Common uses**: Explosions, hits, earthquakes, heavy footsteps

**Key settings**:

- **Duration**: How long the shake lasts
- **Amplitude**: Shake intensity (distance)
- **Frequency**: How fast it shakes (lower = smooth, higher = jittery)

**Example: Explosion Shake**

```
Add Feedback → Camera → Camera Shake
  - Duration: 0.5s
  - Amplitude: 2.0 ← strong shake
  - Frequency: 30 ← rapid
```

**Pro Tip**: Use lower Amplitude (0.1-0.3) for subtle effects like UI feedback. Use higher (1.0+)
for explosions.

---

### MMF_CameraZoom

**What it does**: Smoothly zooms camera in/out (changes field of view or orthographic size).

**Common uses**: Focus on important moments, dramatic reveals

**Key settings**:

- **Target FOV/Size**: Destination zoom level
- **Duration**: Zoom speed
- **Transition Mode**: Instant, Relative, Absolute

**Example: Zoom on Boss Appear**

```
Add Feedback → Camera → Camera Zoom
  - Target Field of View: 50 ← narrower (zoomed in)
  - Duration: 1.0s
  - Curve: Ease In-Out
```

---

### MMF_Flash

**What it does**: Flashes the screen with a color overlay.

**Common uses**: Hit feedback, teleportation, lightning strikes

**Key settings**:

- **Flash Color**: Color and alpha of flash
- **Duration**: How long flash lasts
- **Alpha Curve**: Controls fade-in/out shape

**Example: Red Damage Flash**

```
Add Feedback → Camera → Flash
  - Flash Color: Red with 50% alpha
  - Duration: 0.15s
  - Alpha Curve: Sharp spike (up fast, down fast)
```

---

### MMF_Fade

**What it does**: Fades the screen to/from black (or any color).

**Common uses**: Scene transitions, death screens, level loading

**Key settings**:

- **Fade Type**: Fade In, Fade Out, Fade In Then Out
- **Duration**: Fade speed
- **Fade Color**: Usually black, but can be white/custom

**Example: Death Fade to Black**

```
Add Feedback → Camera → Fade
  - Fade Type: Fade Out (to black)
  - Duration: 1.5s
  - Fade Color: Black
```

---

### MMF_Cinemachine_Impulse / Transition

**What it does**: Integrates with Cinemachine for advanced camera effects.

**Common uses**: When using Cinemachine virtual cameras, impulse sources

**Example: Switch Virtual Camera on Enter Room**

```
Add Feedback → Camera → Cinemachine Transition
  - Target Virtual Camera: RoomCamera02
  - Blend Duration: 1.0s
```

---

## Events

Event feedbacks trigger Unity Events or custom game events.

### MMF_Events ⭐ Most Used

**What it does**: Invokes a Unity Event when feedback plays.

**Common uses**: Triggering custom game logic, door opens, spawn enemies

**Example: Open Door**

```
Add Feedback → Events → Events
  - Unity Event: DoorController.Open()
```

**Pro Tip**: Use this to integrate Feel with your existing systems without writing code.

---

### MMF_MMGameEvent

**What it does**: Raises a MoreMountains GameEvent (event channel pattern).

**Common uses**: Decoupled communication, global events

**Example: Notify UI of Score Change**

```
Add Feedback → Events → MM Game Event
  - Target Event: OnScoreChanged (ScriptableObject)
```

---

## GameObject

GameObject feedbacks control object lifecycle and behavior.

### MMF_Enable / Disable

**What it does**: Enables or disables a GameObject or component.

**Common uses**: Showing/hiding UI, activating traps, spawning objects

**Example: Show Victory Screen**

```
Add Feedback → GameObject → Enable
  - Target GameObject: VictoryPanel
```

---

### MMF_Instantiate

**What it does**: Spawns a prefab at a position.

**Common uses**: Spawning pickups, VFX prefabs, projectiles

**Key settings**:

- **Prefab**: What to spawn
- **Position/Rotation**: Where and how to spawn it
- **Parent**: Optional transform parent

**Example: Spawn Coin Pickup**

```
Add Feedback → GameObject → Instantiate
  - Prefab: CoinPrefab
  - Position: Transform (this GameObject's position)
  - Auto Destroy: After 5 seconds
```

---

### MMF_Destroy

**What it does**: Destroys a GameObject.

**Common uses**: Removing objects, cleaning up effects

**Example: Destroy Enemy on Death**

```
Add Feedback → GameObject → Destroy
  - Target: this.gameObject
  - Delay: 2.0s ← wait for death animation
```

---

### MMF_Rigidbody

**What it does**: Applies force, velocity, or torque to a Rigidbody.

**Common uses**: Knockback, explosions, physics reactions

**Example: Knockback on Hit**

```
Add Feedback → GameObject → Rigidbody
  - Target: Player Rigidbody
  - Mode: Add Force
  - Force: (-5, 2, 0) ← back and up
  - Force Mode: Impulse
```

---

## Haptics (Nice Vibrations)

Haptic feedbacks provide tactile feedback on mobile and controllers.

### MMF_Haptics ⭐ Most Used

**What it does**: Triggers device vibration (iOS, Android, console controllers).

**Common uses**: Button presses, hits, collisions, UI feedback

**Key settings**:

- **Haptic Type**: Light, Medium, Heavy, Success, Warning, Failure
- **Platform**: Automatically uses correct API per platform

**Example: Button Press Feedback**

```
Add Feedback → Haptics → Haptics
  - Haptic Type: Light
```

**Platform Support**:

- **iOS**: Uses UIImpactFeedbackGenerator (Taptic Engine)
- **Android**: Uses Vibrator API
- **Console**: Uses controller rumble
- **PC**: Ignored (no effect)

---

### MMF_NVClip

**What it does**: Plays a pre-authored haptic clip (advanced timing control).

**Common uses**: Complex vibration patterns, weapon firing

---

## Light

Light feedbacks control Unity Light components.

### MMF_Light

**What it does**: Animates Light intensity and color.

**Common uses**: Flickering lights, lightning, pulsing, damage indicators

**Example: Flickering Torch**

```
Add Feedback → Light → Light
  - Target Light: TorchLight
  - Animate Intensity: From-To
  - From: 0.5, To: 1.0
  - Duration: 0.1s
  - Loop: Ping-Pong (back and forth)
```

---

## Materials & Renderer

Material/Renderer feedbacks control visual appearance.

### MMF_Material

**What it does**: Changes material properties (color, float, vector).

**Common uses**: Damage flashes, dissolve effects, shader animations

**Example: Damage Red Flash**

```
Add Feedback → Renderer → Material
  - Target Renderer: Enemy Sprite Renderer
  - Property: _Color
  - Destination Color: Red
  - Duration: 0.2s
  - Curve: Spike (quick flash then revert)
```

---

### MMF_SpriteRenderer

**What it does**: Controls SpriteRenderer (color, alpha, flip).

**Common uses**: 2D character flashes, fading, sprite swaps

**Example: Fade Out Sprite**

```
Add Feedback → Renderer → Sprite Renderer
  - Target: Character SpriteRenderer
  - Animate Alpha: To Destination
  - Destination Alpha: 0 (invisible)
  - Duration: 0.5s
```

---

### MMF_Flicker

**What it does**: Flickers a renderer on/off rapidly.

**Common uses**: Invincibility frames, damage feedback, glitches

**Example: Invincibility Flicker**

```
Add Feedback → Renderer → Flicker
  - Target Renderer: Player Sprite Renderer
  - Duration: 1.0s ← flickers for 1 second
  - Flicker Speed: 0.05s ← very fast on/off
```

---

## Particles

Particle feedbacks control Unity ParticleSystems.

### MMF_Particles_Instantiate ⭐ Most Used

**What it does**: Spawns a particle system prefab at a position.

**Common uses**: Explosions, dust, sparks, magic effects

**Example: Dust on Landing**

```
Add Feedback → Particles → Instantiate
  - Particle Prefab: DustPuffPrefab
  - Position: At Transform (player's feet)
  - Auto Destroy: When particle system finishes
```

---

### MMF_Particles_Play / Stop

**What it does**: Controls an existing ParticleSystem (play, pause, stop).

**Common uses**: Jetpack flames, auras, continuous effects

**Example: Start Jetpack Flames**

```
Add Feedback → Particles → Play
  - Target Particle System: JetpackFlames
  - Mode: Play
```

---

## Physics

Physics feedbacks interact with Rigidbodies and physics systems.

### MMF_Rigidbody (see GameObject section)

---

## Post Processing

Post-processing feedbacks require URP/HDRP Volume components.

### MMF_Bloom

**What it does**: Animates bloom intensity (glow effect).

**Common uses**: Magical moments, powerups, explosions

**Example: Powerup Bloom Burst**

```
Add Feedback → Post Processing → Bloom
  - Intensity: From 0 to 5 (strong glow)
  - Duration: 0.3s
  - Curve: Spike (quick burst then fade)
```

**Setup Required**: Add Volume component to scene with Bloom override enabled.

---

### MMF_Vignette

**What it does**: Animates vignette (darkened screen edges).

**Common uses**: Low health, focus, dramatic moments

**Example: Low Health Vignette**

```
Add Feedback → Post Processing → Vignette
  - Intensity: 0.5 (darker edges)
  - Duration: 0.5s
```

---

### MMF_ChromaticAberration

**What it does**: Animates chromatic aberration (color fringing, glitch effect).

**Common uses**: Hits, glitches, portal effects, impacts

**Example: Hit Glitch**

```
Add Feedback → Post Processing → Chromatic Aberration
  - Intensity: 1.0 (strong aberration)
  - Duration: 0.1s
  - Curve: Spike
```

---

### MMF_ColorGrading / DepthOfField / LensDistortion / MotionBlur

**What it does**: Animates respective post-processing effects.

**Common uses**: Cinematic moments, drunken effects, speed boosts

---

## Text

Text feedbacks animate TextMeshPro or Unity UI Text components.

### MMF_TMPText

**What it does**: Changes TextMeshPro text content, color, or alpha.

**Common uses**: Score updates, damage numbers, notifications

**Example: Show Damage Number**

```
Add Feedback → Text → TMP Text
  - Target Text: FloatingDamageText
  - New Text: "50" ← damage amount
  - Animate Color: To Destination (Red)
  - Duration: 0.5s
```

---

### MMF_TMPDilate / Outline / FontSize

**What it does**: Animates TextMeshPro shader properties.

**Common uses**: Pulsing UI, emphasis, hover effects

**Example: Button Hover Pulse**

```
Add Feedback → Text → TMP Font Size
  - Target Text: Button Text
  - Font Size: From 24 to 28
  - Duration: 0.2s
```

---

## Time

Time feedbacks control game time scale (slow motion, freeze frames).

### MMF_TimescaleModifier ⭐ Most Used

**What it does**: Changes Time.timeScale to slow or speed up the game.

**Common uses**: Bullet time, dramatic hits, freeze frames

**Key settings**:

- **Target Time Scale**: 0 = frozen, 0.5 = half speed, 2.0 = double speed
- **Duration**: How long the time change lasts
- **Unscaled**: Whether the feedback itself is affected by time scale

**Example: Slow Motion on Critical Hit**

```
Add Feedback → Time → Timescale Modifier
  - Target Time Scale: 0.3 (70% slower)
  - Duration: 0.2s
  - Lerp Speed: 5 ← smooth transition
```

**Pro Tip**: Always return time scale to 1.0! Add a second feedback with delay or use "Restore Time
Scale" mode.

**Complete Example: Freeze Frame then Slow-Mo**

```
Feedback 1: Timescale Modifier
  - Target: 0.0 (freeze)
  - Duration: 0.1s

Feedback 2: Timescale Modifier
  - Initial Delay: 0.1s
  - Target: 0.5 (slow)
  - Duration: 0.3s

Feedback 3: Timescale Modifier
  - Initial Delay: 0.4s
  - Target: 1.0 (normal)
  - Duration: 0.2s
```

---

### MMF_FreezeFrame

**What it does**: Freezes the game for a brief moment (wrapper around time scale).

**Common uses**: Impactful hits, critical damage

**Example: Freeze on Boss Death**

```
Add Feedback → Time → Freeze Frame
  - Duration: 0.2s
```

---

## Transform

Transform feedbacks animate position, rotation, and scale.

### MMF_Position / Rotation / Scale ⭐ Most Used

**What it does**: Animates a Transform's position, rotation, or scale over time.

**Common uses**: Movement, spinning, growing/shrinking, UI animations

**Key settings**:

- **Animate Mode**: To Destination, From-To, By Amount, ToDestinationThenBack
- **Destination**: Target position/rotation/scale
- **Duration**: Animation speed
- **Curve**: Easing curve (Linear, EaseOut, EaseInOut, etc.)

**Example: Coin Bounce Up Then Down**

```
Add Feedback → Transform → Position
  - Target: Coin Transform
  - Animate Position Y: To Destination Then Back
  - Destination Y: 2.0 (bounce up 2 units)
  - Duration: 0.5s
  - Curve: Ease Out (slow down at peak)
```

**Example: Spin Pickup Item**

```
Add Feedback → Transform → Rotation
  - Target: Item Transform
  - Animate Rotation Y: By Amount
  - Amount: 360 (one full rotation)
  - Duration: 0.5s
  - Curve: Linear
```

**Example: Squash and Stretch on Landing**

```
Feedback 1: Scale
  - Animate Scale: To Destination
  - Destination: (1.3, 0.7, 1) ← wider, flatter
  - Duration: 0.1s

Feedback 2: Scale
  - Initial Delay: 0.1s
  - Destination: (1, 1, 1) ← back to normal
  - Duration: 0.2s
  - Curve: Ease Out Back (overshoot)
```

---

### MMF_Wiggle (Position/Rotation/Scale)

**What it does**: Randomly wiggles position, rotation, or scale over time.

**Common uses**: Shaking objects, jittery effects, nervous animations

**Example: Shaking Chest Before Opening**

```
Add Feedback → Transform → Wiggle Position
  - Target: Chest Transform
  - Amplitude: (0.1, 0.1, 0) ← small shake
  - Frequency: 20 ← fast jitter
  - Duration: 0.5s
```

---

### MMF_SquashAndStretch

**What it does**: Applies squash-and-stretch animation automatically.

**Common uses**: Cartoon-style impacts, bouncing

**Example: Ball Bounce**

```
Add Feedback → Transform → Squash And Stretch
  - Target: Ball Transform
  - Intensity: 0.5
  - Duration: 0.3s
```

---

### MMF_Spring (Position/Rotation/Scale)

**What it does**: Physics-based spring animation (bouncy, realistic).

**Common uses**: UI popups, satisfying button presses

**Example: Popup Menu Bounce**

```
Add Feedback → Transform → Spring Scale
  - Target: Menu Panel
  - Spring Strength: 100
  - Damping: 10 ← controls bounciness
  - Target Scale: (1, 1, 1)
```

---

## UI

UI feedbacks control Unity UI (Canvas, RectTransform, Image, etc.).

### MMF_CanvasGroup ⭐ Most Used

**What it does**: Fades UI in/out by animating CanvasGroup alpha.

**Common uses**: Menu transitions, tooltips, notifications

**Example: Fade In Menu**

```
Add Feedback → UI → Canvas Group
  - Target Canvas Group: Main Menu Canvas Group
  - Destination Alpha: 1.0 (visible)
  - Duration: 0.3s
  - Also Block Raycasts: True ← makes it interactive when visible
```

---

### MMF_Image

**What it does**: Animates UI Image color, fill amount, or sprite.

**Common uses**: Health bars, progress bars, button feedback

**Example: Deplete Health Bar**

```
Add Feedback → UI → Image
  - Target Image: HealthBarFill
  - Animate Fill Amount: To Destination
  - Destination Fill: 0.3 (30% health)
  - Duration: 0.2s
```

**Example: Button Color Change on Hover**

```
Add Feedback → UI → Image
  - Target Image: Button Background
  - Animate Color: To Destination
  - Destination Color: Light Blue
  - Duration: 0.15s
```

---

### MMF_RectTransform

**What it does**: Animates RectTransform properties (anchored position, size, pivot).

**Common uses**: Sliding menus, expanding panels, UI animations

**Example: Slide Menu In From Left**

```
Add Feedback → UI → RectTransform
  - Target: Side Menu RectTransform
  - Animate Anchored Position: To Destination
  - Destination Position: (0, 0) ← screen center
  - Duration: 0.4s
  - Curve: Ease Out
```

---

### MMF_FloatingText

**What it does**: Spawns floating text (like damage numbers) that animates and fades.

**Common uses**: Damage numbers, +XP notifications, loot pickups

**Example: Damage Number on Hit**

```
Add Feedback → UI → Floating Text
  - Text: "50"
  - Color: Red
  - Spawn Position: Above enemy
  - Movement: Up and fade out
  - Duration: 1.0s
```

---

## Debug

Debug feedbacks help with testing and visualization.

### MMF_DebugLog

**What it does**: Logs a message to the console.

**Common uses**: Tracking feedback execution, debugging timing

**Example: Log When Feedback Plays**

```
Add Feedback → Debug → Debug Log
  - Message: "Boss attack feedback triggered!"
```

---

### MMF_Pause

**What it does**: Pauses MMFeedbacks execution for debugging.

**Common uses**: Inspecting feedback state mid-execution

---

## Quick Selection Guide

**Need instant impact?** → Camera Shake, Flash, Haptics, Time Freeze

**Need smooth transitions?** → Position, Rotation, Scale, Canvas Group

**Need audio?** → Sound, AudioSource

**Need visual effects?** → Particles, Material, Flicker

**Need UI feedback?** → Canvas Group, Image, RectTransform, Floating Text

**Need time effects?** → Timescale Modifier, Freeze Frame

**Need physics reactions?** → Rigidbody

**Need text updates?** → TMP Text, Floating Text

**Need dramatic moments?** → Post Processing (Bloom, Vignette, Chromatic Aberration), Camera Zoom,
Slow Motion

## Combining Feedbacks for Maximum Impact

Great game feel comes from **layering multiple feedbacks**:

### Example: Powerful Punch

```
MMFeedbacks (PowerfulPunch):
  ├─ Audio → Sound (heavy impact sound)
  ├─ Camera → Shake (0.3s, high intensity)
  ├─ Time → Freeze Frame (0.1s)
  ├─ Particles → Instantiate (impact sparks)
  ├─ Haptics → Heavy
  ├─ Transform → Wiggle (enemy shakes)
  └─ Post Processing → Chromatic Aberration (0.1s burst)
```

### Example: Magical Spell Cast

```
MMFeedbacks (SpellCast):
  ├─ Particles → Instantiate (magic circle)
  ├─ Audio → Sound (charging sound)
  ├─ Light → Pulse (0.5s)
  ├─ Post Processing → Bloom (0.5s glow)
  ├─ Transform → Scale (spell circle grows)
  └─ Camera → Zoom In (focus on caster)
```

## Next Steps

Now that you know what feedbacks exist:

1. **[Advanced Techniques](04-ADVANCED-TECHNIQUES.md)** — Scripting, sequences, custom feedbacks
2. **[Troubleshooting](05-TROUBLESHOOTING.md)** — When feedbacks don't work as expected

**Pro Tip**: Don't try to memorize all feedbacks — use the Inspector's search bar! Type "shake" to
find all shake-related feedbacks instantly.
