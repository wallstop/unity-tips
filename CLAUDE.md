# Claude Code Guidelines

This file provides context and guidelines for Claude Code when working on this repository.

## Project Overview

Unity Tips & Tools is a documentation repository containing best practices, tool recommendations,
and architectural patterns for Unity game development. The documentation is built with MkDocs
Material and deployed to GitHub Pages.

## Code Style

### Python Scripts

All Python scripts in `scripts/` must be formatted with **black**:

- Black is configured in `.pre-commit-config.yaml`
- Use Python 3.11+ features (type hints, `|` union syntax, `removesuffix`, etc.)
- Use `raise SystemExit(main())` instead of `sys.exit(main())` for consistency
- Import shared utilities from `link_utils.py` for markdown link processing

Example formatting check:

```bash
black scripts/*.py --check
```

### Pre-commit Hooks

This repository uses pre-commit for automated checks. Key hooks include:

- **black** - Python code formatting
- **prettier** - Markdown, YAML, JSON formatting
- **markdownlint-cli2** - Markdown linting with auto-fix
- **cspell** - Spell checking for documentation
- **actionlint** - GitHub Actions workflow validation
- **yamllint** - YAML linting

Custom Python hooks in `scripts/`:

- `check_links.py` - Validate markdown links resolve correctly
- `fix_link_text.py` - Ensure human-readable link text
- `check_orphaned_docs.py` - Find unreferenced documentation
- `check_csharp_syntax.py` - Validate C# code blocks
- `fix_markdown_ordered_lists.py` - Auto-fix list numbering
- `sync-wiki.py` - Sync docs to GitHub Wiki

### Markdown

- Use kebab-case for file names with numeric prefixes (e.g., `01-getting-started.md`)
- Links should have human-readable text, not raw URLs or file paths
- Code blocks should specify the language for syntax highlighting
- C# code blocks are validated for basic syntax correctness

## Repository Structure

```
unity-tips/
├── docs/                    # Documentation source files
│   ├── best-practices/      # Unity best practices guides
│   ├── animancer/           # Tool-specific documentation
│   └── ...
├── scripts/                 # Python utility scripts
├── .github/
│   └── workflows/           # CI/CD workflows
├── mkdocs.yml               # MkDocs configuration
└── .pre-commit-config.yaml  # Pre-commit hooks
```

## CI/CD Workflows

- **docs.yml** - Build and deploy to GitHub Pages
- **wiki.yml** - Sync documentation to GitHub Wiki
- **pre-commit.yml** - Run linting and formatting checks
- **security.yml** - CodeQL analysis and dependency review
- **stale.yml** - Close inactive issues/PRs

## Common Tasks

### Adding New Documentation

1. Create markdown file in appropriate `docs/` subdirectory
2. Add entry to `mkdocs.yml` navigation
3. If wiki sync is needed, add mapping to `scripts/sync-wiki.py` `WIKI_STRUCTURE`

### Running Pre-commit Locally

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

### Formatting Python Scripts

```bash
pip install black
black scripts/*.py
```

## Git Conventions

- Commit messages should be clear and descriptive
- Use present tense ("Add feature" not "Added feature")
- Reference issues/PRs when applicable
