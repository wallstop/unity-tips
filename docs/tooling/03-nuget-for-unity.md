# NuGet For Unity | .NET Packages Inside Unity

NuGetForUnity brings the entire NuGet ecosystem into the Unity Editor. It runs natively inside
Unity, so you can install, update, and remove any NuGet package without leaving the project or
breaking Unity's compilation pipeline.

## Why teams use it

- **Full .NET reach** – Access thousands of libraries (JSON, testing, HTTP clients, and more) that
  are not on the Asset Store.
- **Unity-friendly** – Handles assembly definitions, .dll placement, and dependency graphs the way
  Unity expects, so imported packages show up instantly in your project.
- **One-click upgrades** – Manage direct and transitive dependencies from a single window with
  upgrade/downgrade helpers.
- **Offline cache** – Packages are stored locally, making future installs faster and reproducible.

## Install via Unity Package Manager (preferred)

Unity 2019.3+

1. Open `Window → Package Manager`.
2. Click the `+` button and choose **Add package from git URL...**.
3. Paste the Git URL and click **Add**:

   ```
   https://github.com/GlitchEnzo/NuGetForUnity.git?path=/src/NuGetForUnity
   ```

   To lock to a version append `#v{version}`, for example `#v2.0.0`.

Unity 2019.2 or earlier

Add the dependency directly to `Packages/manifest.json`:

```json
"com.glitchenzo.nugetforunity": "https://github.com/GlitchEnzo/NuGetForUnity.git?path=/src/NuGetForUnity"
```

### Alternative: OpenUPM registry

If you already use [OpenUPM](https://openupm.com/packages/com.github-glitchenzo.nugetforunity/), add
or reuse a scoped registry and then install the package ID `com.github-glitchenzo.nugetforunity` via
Package Manager (or run `openupm add com.github-glitchenzo.nugetforunity`).

## Getting started

1. Launch `NuGet → Manage NuGet Packages` inside Unity.
2. Use the **Online** tab to search the NuGet feed, enable **Show Prerelease** when needed, and
   click **Install** to pull packages and all required dependencies.
3. Review the **Installed** tab to see direct and transitive dependencies. Use **Add as explicit**
   to keep a dependency pinned even if no longer referenced.
4. Visit the **Updates** tab to batch upgrade or downgrade versions with one click.

NuGetForUnity writes assemblies and `.asmdef` files under `Packages/NuGet`, so additions are tracked
in source control and compile like any other UPM package. The plugin respects Unity's domain reloads
and rebuilds, keeping the workflow seamless.

## Tips for production projects

- Audit packages before shipping—NuGet makes it easy to pull advanced libraries, but ensure licenses
  align with your project.
- Check Unity's target framework: when using packages that require newer .NET APIs, set
  `PlayerSettings → Api Compatibility Level` to `.NET Standard 2.1` or above in supported versions.
- Pair with CI: include the `Packages/NuGet` folder in source control so build machines avoid
  re-downloading dependencies.
- Combine with [EditorConfig](./02-editorconfig.md) and [CSharpier](./01-csharpier.md) to enforce
  cross-team standards while consuming wider .NET tooling.
