# Contributing

## Quick start

- **Bugs:** Open an issue using the bug-report template.
- **Features:** Open an issue using the feature-request template.
- **PRs:** Fork, branch from `develop`, keep the change focused, open against `develop`.

## Conventions

The pinned test environment requires Python 3.14.2 or later.

```bash
python -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python -m pytest
```

- Prefix commits semantically (`feat:`, `fix:`, `docs:`, `ci:`, `deps:`).
- One logical change per PR.
- Make sure CI is green before requesting review.

## License

By contributing, you agree that your contributions will be licensed under the project's MIT license.
