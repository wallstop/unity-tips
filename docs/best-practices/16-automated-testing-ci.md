# Automated Testing & CI

Automated tests catch regressions before players do. Unity's Test Framework lets you run Edit Mode
and Play Mode tests headlessly, making it easy to add guardrails in continuous integration (CI).

## Unity Test Runner

Unity's built-in Test Runner (Window > General > Test Runner) provides a comprehensive testing
framework based on NUnit. Tests appear in two tabs:

- **EditMode** – Tests run in the editor context without entering Play Mode
- **PlayMode** – Tests run in the actual Unity runtime with full engine simulation

## Testing matrix

- **Edit Mode tests** – Run in the editor without entering Play Mode; great for pure C# utilities,
  data pipelines, and editor tools. No access to GameObject lifecycle or scene management.
- **Play Mode tests** – Full runtime environment where you can:
  - Load scenes with `SceneManager.LoadScene()`
  - Create GameObjects with `new GameObject()` or `GameObject.CreatePrimitive()`
  - Instantiate prefabs with `Object.Instantiate()`
  - Test physics, collisions, and Unity's frame-based systems
  - Validate MonoBehaviour lifecycle (Awake, Start, Update, etc.)
  - Simulate player input and interactions
- **Integration smoke tests** – Use build scripts (Shell, C#) to launch the game, load key scenes,
  and assert there are no fatal errors in logs.

## Getting started

1. Install the **Test Framework** package if it is not already present.
2. Create `Tests/EditMode` and `Tests/PlayMode` folders (Unity auto-discovers them).
3. Write NUnit-style tests using `[Test]` or `[UnityTest]`:

### [Test] vs [UnityTest]

- **[Test]** – Synchronous test that runs to completion immediately. Use for logic that doesn't
  depend on Unity's frame loop:

```csharp
[TestFixture]
public class CurrencyTests
{
    [Test]
    public void AddingGoldDoesNotOverflow()
    {
        var wallet = new CurrencyWallet();
        wallet.AddGold(1000);
        Assert.AreEqual(1000, wallet.Gold);
    }
}
```

- **[UnityTest]** – Returns `IEnumerator` and yields control back to Unity, allowing frame-based
  testing. Use when you need to:
  - Wait for multiple frames (`yield return null`)
  - Wait for specific conditions (`yield return new WaitForSeconds(2f)`)
  - Test animations, coroutines, or physics simulations
  - Validate behaviour over time

```csharp
public class FireDamageTests : TestBase
{
    [UnityTest]
    public IEnumerator PlayerTakesFireDamageOverTime()
    {
        var player = Track(new GameObject()).AddComponent<Player>();
        player.EnterFireZone();

        float initialHealth = player.Health;
        yield return new WaitForSeconds(2f);

        Assert.Less(player.Health, initialHealth);
        // No manual cleanup needed - TestBase.TearDown handles it
    }
}
```

### Test Base Class Pattern

Always use a base class that tracks and automatically cleans up Unity objects. This prevents leaks
even when assertions fail:

```csharp
using UnityEngine;
using UnityEngine.TestTools;
using NUnit.Framework;
using System.Collections.Generic;

public abstract class TestBase
{
    private readonly List<Object> _trackedObjects = new();

    protected T Track<T>(T obj) where T : Object
    {
        _trackedObjects.Add(obj);
        return obj;
    }

    protected GameObject TrackGameObject(string name = "TestObject")
    {
        return Track(new GameObject(name));
    }

    [TearDown]
    public void TearDown()
    {
        foreach (var obj in _trackedObjects)
        {
            if (obj != null)
            {
                Object.DestroyImmediate(obj);
            }
        }
        _trackedObjects.Clear();
    }
}
```

### Play Mode testing example

Play Mode tests have full access to Unity's runtime, making them ideal for integration testing:

```csharp
using UnityEngine;
using UnityEngine.TestTools;
using UnityEngine.SceneManagement;
using NUnit.Framework;
using System.Collections;

public class GameplayTests : TestBase
{
    [UnityTest]
    public IEnumerator PlayerCanCollectPowerup()
    {
        // Load the test scene
        SceneManager.LoadScene("TestArena");
        yield return null; // Wait one frame for scene to load

        // Instantiate player from prefab - Track() ensures cleanup
        var playerPrefab = Resources.Load<GameObject>("Player");
        var player = Track(Object.Instantiate(playerPrefab, Vector3.zero, Quaternion.identity));

        // Create powerup - Track() ensures cleanup even if assertion fails
        var powerup = Track(GameObject.CreatePrimitive(PrimitiveType.Sphere));
        powerup.transform.position = new Vector3(1, 0, 0);
        powerup.AddComponent<Powerup>();

        // Move player toward powerup
        player.transform.position = Vector3.zero;
        var movement = player.GetComponent<PlayerMovement>();
        movement.MoveToward(powerup.transform.position);

        // Wait for physics/collision
        yield return new WaitForSeconds(0.5f);
        yield return new WaitForFixedUpdate();

        // Assert powerup was collected
        Assert.IsTrue(player.GetComponent<Player>().HasPowerup);
        // No manual cleanup needed - TestBase.TearDown handles everything
    }
}
```

1. Hook the command-line runner into CI:

```bash
/Applications/Unity/Hub/Editor/2022.3.8f1/Unity \
  -batchmode -nographics -projectPath . \
  -runTests -testResults results.xml -testPlatform PlayMode \
  -quit
```

1. Parse `results.xml` (NUnit format) to fail the build when tests break.

## Best practices

- **Keep tests deterministic** – Seed random generators and avoid using real network calls without a
  stub.
- **Limit Play Mode duration** – Focus on short (under 10s) integration tests so CI stays fast.
- **Mock Unity APIs** – Use dependency injection or wrappers (e.g., for time, input, analytics) to
  isolate behaviours.
- **Protect against flaky tests** – Re-run failing tests automatically and quarantine persistent
  offenders until fixed.

## CI essentials

- Run `pre-commit run --all-files` before packaging builds.
- Add a dedicated CI job for tests, then gate merges/PRs on a green test suite.
- Cache Library/ package downloads between runs to keep pipelines under 15 minutes.
- Publish test and lint reports to your PR system for quick triage.

Teams that treat automated tests as mandatory can refactor dangerous systems without fear, ship hot
fixes confidently, and catch platform regressions long before QA or players feel them.
