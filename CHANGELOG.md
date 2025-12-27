# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Added

- **GitHub Pages Documentation Site** - Beautiful, searchable documentation at
  `https://wallstop.github.io/unity-tips` using MkDocs Material theme
- **Spell Checking** - Added cspell with Unity/C# dictionaries to catch typos in documentation
- **Stale Management** - Automated workflow to mark and close inactive issues/PRs after 60 days
- **Security Scanning** - CodeQL analysis for Python scripts and dependency review on PRs
- **PR Quality Checks** - Automatic size labeling (XS/S/M/L/XL) and category labels (documentation,
  scripts, ci/cd, config)
- Warning comments on large PRs (500+ lines) encouraging smaller, focused changes

### Changed

- Reorganized all documentation files to use kebab-case naming convention
- Renamed 35 documentation files across 7 folders (animancer, assembly-definitions, feel,
  hot-reload, input-system, odin, primetween)
- Updated 315+ internal links to reflect new file names
- CI workflow now explicitly triggers re-runs after auto-fix commits

## 0.1.0 - 2025-12-27

### Added

- **Documentation Audit System**

  - Added C# syntax validation script (`scripts/check_csharp_syntax.py`)
  - Added orphaned documentation checker (`scripts/check_orphaned_docs.py`)
  - Enhanced pre-commit workflow with documentation validation

- **Best Practices Documentation** (18 guides)

  - Lifecycle methods guide
  - Null checks and Unity's "fake null" handling
  - Component access and caching patterns
  - Serialization best practices
  - Coroutines guide
  - Physics and FixedUpdate patterns
  - Performance and memory optimization
  - ScriptableObjects usage patterns
  - Object pooling implementation
  - Event systems comparison (ScriptableObject events vs DxMessaging)
  - Addressables guide
  - Scene loading patterns
  - Jobs and Burst compiler guide
  - Async/await in Unity
  - Profiling techniques
  - Automated testing and CI/CD
  - Input architecture patterns
  - Save/load system patterns

- **Tool Documentation**

  - [Animancer](docs/animancer/README.md) - Code-driven animation system (~$75)
  - [Assembly Definitions](docs/assembly-definitions/README.md) - Compile time optimization (FREE)
  - [Asset Usage Finder](docs/asset-usage-finder/README.md) - Asset dependency tracking (~$20)
  - [Better Build Info PRO](docs/better-build-info/README.md) - Build size analysis (~$30)
  - [DxMessaging](docs/dxmessaging/README.md) - Type-safe messaging system (FREE)
  - [Feel](docs/feel/README.md) - Game juice and feedback system (€46)
  - [Graphy](docs/graphy/README.md) - Runtime performance monitoring (FREE)
  - [Hot Reload](docs/hot-reload/README.md) - Live code reloading ($10/mo)
  - [Input System](docs/input-system/README.md) - Modern input handling (FREE)
  - [Odin Inspector](docs/odin/README.md) - Advanced serialization and editors (~$55)
  - [PrimeTween](docs/primetween/README.md) - Zero-allocation tweening (FREE)
  - [Unity Helpers](docs/unity-helpers/README.md) - Utility library (FREE)

- **Development Tooling Documentation**

  - CSharpier auto-formatting guide
  - EditorConfig conventions guide
  - NuGet for Unity integration guide
  - Heap Allocation Viewer guide

- **Project Infrastructure**
  - Pre-commit hooks with markdownlint, prettier, and yamllint
  - GitHub Actions workflow for documentation validation
  - Dependabot configuration for dependency updates
  - AGENTS.md for AI assistant guidance
  - CONTRIBUTING.md with contribution guidelines

### Changed

- Improved code examples across all documentation with syntax validation
- Enhanced Object Pooling documentation with clearer patterns
- Updated Better Build Info docs with free alternatives
- Refined event systems documentation to recommend DxMessaging over ScriptableObject events

### Fixed

- Fixed C# code syntax errors in documentation examples
- Fixed coroutine formatting issues
- Fixed markdown ordered list numbering
- Resolved pre-commit validation errors
