# Automated Testing & CI

Automated tests catch regressions before players do. Unity's Test Framework lets you run Edit Mode
and Play Mode tests headlessly, making it easy to add guardrails in continuous integration (CI).

## Testing matrix

- **Edit Mode tests** – Run in the editor without entering Play Mode; great for pure C# utilities
  and data pipelines.
- **Play Mode tests** – Spin up scenes, instantiate prefabs, and validate behaviours in a simulated
  runtime.
- **Integration smoke tests** – Use build scripts (Shell, C#) to launch the game, load key scenes,
  and assert there are no fatal errors in logs.

## Getting started

1. Install the **Test Framework** package if it is not already present.
2. Create `Tests/EditMode` and `Tests/PlayMode` folders (Unity auto-discovers them).
3. Write NUnit-style tests:

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
