# Changelog

All notable changes to Collider will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- pyproject.toml for modern Python packaging
- Makefile for standard development commands
- tox.ini for multi-Python version testing
- dependabot.yml for automated dependency updates
- Issue and PR templates
- CODEOWNERS file
- Coverage configuration (.coveragerc)
- Deterministic JSON output (sort_keys=True)
- pytest job in CI with multi-Python matrix
- Security scanning with pip-audit

### Changed
- CI workflow now includes pytest with coverage
- CI workflow now includes security scanning

### Fixed
- JSON output now deterministic across Python sessions

## [2.3.0] - 2026-01-16

### Added
- Brain Download feature (output.md generation)
- Topology reasoning for shape classification
- Semantic cortex for domain inference
- HTML visualization improvements

### Changed
- Improved atom classification accuracy
- Enhanced edge resolution

## [2.2.0] - 2026-01-10

### Added
- Theory coverage CI job
- Docstring linting

### Fixed
- Import resolution edge cases

## [2.1.0] - 2026-01-04

### Added
- React T2 detection improvements
- Purpose field extraction

[Unreleased]: https://github.com/leonardo-lech/collider/compare/v2.3.0...HEAD
[2.3.0]: https://github.com/leonardo-lech/collider/compare/v2.2.0...v2.3.0
[2.2.0]: https://github.com/leonardo-lech/collider/compare/v2.1.0...v2.2.0
[2.1.0]: https://github.com/leonardo-lech/collider/releases/tag/v2.1.0
