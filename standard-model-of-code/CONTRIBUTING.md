# Contributing to Collider

Thank you for your interest in contributing to Collider!

## Development Setup

```bash
# Clone the repository
git clone <repo-url>
cd standard-model-of-code

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install in development mode
make install-dev

# Verify installation
./collider --help
```

## Running Tests

```bash
# Run all tests
make test

# Run specific test file
PYTHONPATH=src pytest tests/test_contract_output.py -v

# Run with coverage report
PYTHONPATH=src pytest tests/ --cov=src/core --cov-report=html
```

## Code Style

We use:
- **black** for code formatting
- **isort** for import sorting
- **flake8** for linting

```bash
# Check style
make lint

# Auto-format
make format
```

## Making Changes

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Make your changes
3. Run tests: `make test`
4. Run self-analysis: `./collider full . --output /tmp/check`
5. Commit with clear message
6. Push and create PR

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation only
- `test:` - Adding tests
- `refactor:` - Code change that neither fixes a bug nor adds a feature
- `ci:` - CI/CD changes
- `build:` - Build system changes

## Questions?

Open an issue or contact the maintainers.
