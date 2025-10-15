# Contributing to Unity Tips

Thanks for helping make this knowledge base better! These guidelines keep the docs consistent and
make reviews smoother.

## Before You Start

- Make sure you have **Python 3.8+** available. Pre-commit installs the tooling it needs, including
  Node-based linters such as Prettier and markdownlint.
- Install [pre-commit](https://pre-commit.com/) once: `pip install pre-commit`.
- Run `pre-commit install` inside your clone so the checks run automatically before each commit.

## Formatting & Linting

- Run `pre-commit run --all-files` before you open a pull request. This formats Markdown, YAML, and
  JSON files and enforces lint rules.
- The **Lint Docs** GitHub Action will auto-apply any fixable pre-commit changes on pull requests
  opened from this repository. Fork-based PRs still need to push the fixes manually.
- Fix any remaining markdownlint warnings by following the message in the output (e.g., add
  languages to fenced code blocks).
- Follow the existing tone of the docs and prefer American English spelling for new content.

## Making Changes

- Work on a feature branch and keep changes scoped to a single topic when possible.
- Include context for screenshots or code snippets (Unity versions, packages, settings, etc.).
- Use descriptive headings and add anchor links if you reference sections from other pages.

## Pull Requests

- Link related issues when available and describe reader-facing changes in the PR body.
- Ensure the **Lint Docs** GitHub Action passes; it runs the same pre-commit hooks used locally.
- Dependabot PRs will auto-assign `@wallstop`; feel free to mention them directly if you need
  guidance.

Thanks again for contributing—every improvement helps Unity developers learn faster!
