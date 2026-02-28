# Contributing to x402 Bazaar Auto-GPT Plugin

Thank you for your interest in contributing to the x402 Bazaar Auto-GPT Plugin! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to:
- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

### 1. Fork the Repository

Fork the repository on GitHub and clone your fork locally:

```bash
git clone https://github.com/YOUR_USERNAME/x402-autogpt-plugin.git
cd x402-autogpt-plugin
```

### 2. Set Up Development Environment

Create a virtual environment and install dependencies:

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install development dependencies
pip install -r requirements-dev.txt

# Install package in editable mode
pip install -e .
```

### 3. Create a Branch

Create a branch for your changes:

```bash
git checkout -b feature/your-feature-name
```

Use prefixes:
- `feature/` for new features
- `fix/` for bug fixes
- `docs/` for documentation
- `test/` for test improvements
- `refactor/` for code refactoring

## Development Workflow

### Code Style

We follow PEP 8 with some modifications. Use these tools:

```bash
# Format code with black
black src/ tests/

# Lint with flake8
flake8 src/ tests/

# Type check with mypy
mypy src/

# Lint with pylint
pylint src/x402_bazaar/
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=x402_bazaar --cov-report=term-missing

# Run specific test file
pytest tests/test_client.py
pytest tests/test_standalone_usage.py

# Run specific test class or test
pytest tests/test_client.py::TestX402Client::test_discover_services
pytest tests/test_standalone_usage.py::TestSection8ConvenienceMethods::test_all_four_methods_called
```

### Writing Tests

- Add tests for all new features
- Maintain or improve code coverage
- Use descriptive test names
- Follow the Arrange-Act-Assert pattern

Examples:

```python
# Simple AAA pattern
def test_new_feature(client):
    """Test description."""
    # Arrange
    input_data = {"key": "value"}

    # Act
    result = client.new_feature(input_data)

    # Assert
    assert result["success"] is True


# Integration-style pattern (used in test_standalone_usage.py)
# Group tests by section/feature in a class, use a _run() helper to
# avoid repeating mock boilerplate, and test stdout with redirect_stdout.
import io
from contextlib import redirect_stdout
from unittest.mock import MagicMock, patch

class TestMyFeature:
    def _run(self, my_method_return=None):
        mock_client = MagicMock()
        mock_client.my_method.return_value = my_method_return or {"success": False}
        buf = io.StringIO()
        with patch("my_module.MyClient", return_value=mock_client):
            with redirect_stdout(buf):
                main()
        return buf.getvalue()

    def test_success_shows_result(self):
        output = self._run(my_method_return={"success": True, "data": "ok"})
        assert "ok" in output

    def test_error_handled_gracefully(self):
        output = self._run(my_method_return={"success": False, "error": "oops"})
        assert "oops" in output
```

### Documentation

Update documentation when:
- Adding new features
- Changing API behavior
- Fixing bugs that affect usage
- Adding new configuration options

Documentation locations:
- `README.md` - Main documentation
- Docstrings - All public functions/classes
- `examples/` - Usage examples

### Commit Messages

Use clear, descriptive commit messages:

```bash
# Good
git commit -m "Add support for batch API calls"
git commit -m "Fix payment verification timeout"
git commit -m "Update README with new examples"

# Bad
git commit -m "fix"
git commit -m "update"
git commit -m "changes"
```

Format:
```
<type>: <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `test`: Testing
- `refactor`: Code refactoring
- `style`: Code style (formatting)
- `chore`: Maintenance

Example:
```
feat: Add batch API call support

Implement batch_call_api method that allows calling multiple
APIs in a single request, improving performance for agents
that need data from multiple sources.

Closes #42
```

## Pull Request Process

### 1. Update Your Fork

Before creating a PR, sync with upstream:

```bash
git remote add upstream https://github.com/x402-bazaar/x402-autogpt-plugin.git
git fetch upstream
git merge upstream/main
```

### 2. Run Pre-PR Checklist

- [ ] All tests pass: `pytest`
- [ ] Code is formatted: `black src/ tests/`
- [ ] No linting errors: `flake8 src/ tests/`
- [ ] Type checking passes: `mypy src/`
- [ ] Documentation updated
- [ ] CHANGELOG.md updated (if applicable)
- [ ] Tests added for new features

### 3. Create Pull Request

Push your branch and create a PR on GitHub:

```bash
git push origin feature/your-feature-name
```

In your PR description:
- Describe what the PR does
- Reference related issues
- List breaking changes (if any)
- Add screenshots (if UI changes)

Template:
```markdown
## Description
Brief description of changes

## Motivation
Why is this change needed?

## Changes
- Change 1
- Change 2

## Testing
How was this tested?

## Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Code formatted and linted
- [ ] CHANGELOG.md updated

## Related Issues
Closes #123
```

### 4. Review Process

- Maintainers will review your PR
- Address feedback and requested changes
- Keep PR focused (one feature/fix per PR)
- Be patient and respectful

## Types of Contributions

### Bug Reports

Create an issue with:
- Clear title
- Steps to reproduce
- Expected vs actual behavior
- Environment (Python version, OS)
- Code samples/screenshots

### Feature Requests

Create an issue with:
- Clear use case
- Proposed solution
- Alternative solutions considered
- Impact on existing features

### Code Contributions

Focus areas:
- New API integrations
- Performance improvements
- Bug fixes
- Documentation
- Test coverage
- Examples

### Documentation

- Fix typos
- Improve clarity
- Add examples
- Translate docs

## Development Tips

### Testing Against Live API

The plugin connects to the live x402 Bazaar API. For local testing:

```python
# Use production API (default)
client = X402Client()

# Use local API for development
client = X402Client(base_url="http://localhost:3000")
```

### Debugging

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from x402_bazaar import X402Client
client = X402Client()
```

### Running Examples

```bash
python examples/standalone_usage.py
```

### Building Package

```bash
# Build distribution
python -m build

# Check package
twine check dist/*

# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Upload to PyPI (maintainers only)
twine upload dist/*
```

## Release Process (Maintainers)

1. Update version in:
   - `pyproject.toml`
   - `setup.py`
   - `src/x402_bazaar/__init__.py`

2. Update `CHANGELOG.md`

3. Create release commit:
   ```bash
   git commit -m "chore: Release v0.2.0"
   git tag v0.2.0
   git push origin main --tags
   ```

4. Build and publish:
   ```bash
   python -m build
   twine upload dist/*
   ```

5. Create GitHub release with notes

## Questions?

- Create an issue for questions
- Join our Telegram: @x402_monitoradmin_bot
- Email: support@x402-bazaar.com

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to x402 Bazaar!
