# Repository Guidelines

## Project Structure & Module Organization

- Source material lives under `docs/`, grouped by topic (e.g.,
  `docs/best-practices/01-coroutines.md`). Each directory holds a `README.md` that introduces the
  section and numbered guides for deep dives.
- Automation lives in `scripts/`, currently `fix_markdown_ordered_lists.py`, which keeps ordered
  lists sequential.
- Repo metadata sits at the root (`CONTRIBUTING.md`, `.pre-commit-config.yaml`,
  `.markdownlint-cli2.yaml`); update these when adding new automation or lint rules.

## Build, Test, and Development Commands

- Install tooling once: `pip install pre-commit`.
- Enable hooks after cloning: `pre-commit install` (runs formatters on staged files).
- Validate everything before opening a PR: `pre-commit run --all-files`.
- For spot fixes to numbering, run
  `python scripts/fix_markdown_ordered_lists.py docs/best-practices/01-coroutines.md`.

## Coding Style & Naming Conventions

- Write Markdown in American English, using sentence-style paragraphs and descriptive headings.
- Keep ordered lists simple and let the fixer renumber them; never hard-code skipped numbers.
- Prefer fenced code blocks with language tags (` ```csharp `, ` ```yaml `) and add commentary lines
  when Unity context is unclear.
- File names stay lowercase with hyphens; numbered articles use the existing `NN-topic.md` pattern.

## Testing Guidelines

- Pre-commit hooks run Prettier, markdownlint-cli2, yamllint, and the local list fixer—treat a clean
  run as the acceptance test.
- GitHub Actions (`Lint Docs`) mirrors the local hooks and will auto-commit fixes on in-repo
  branches; forked PRs must push their own corrections.
- When adding snippets, execute them in Unity or C# beforehand when feasible, and note the Unity
  version if behavior is version-specific.

## Commit & Pull Request Guidelines

- Follow the short, descriptive subjects used in history (`Best practices`, `Pre-commit hooks`). Aim
  for 50 characters or less and use imperative or noun-phrase tone.
- Commit related changes together—one topic per commit keeps reviews focused.
- Pull requests should link issues when relevant, summarize reader-facing changes, and mention
  required follow-up (screenshots, Unity version, package IDs).
- Confirm `pre-commit run --all-files` passes before requesting review; note any intentional lint
  suppressions in the PR body.
