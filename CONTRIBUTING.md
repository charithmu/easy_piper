# Contributing to EasyPiper

Thank you for your interest in contributing to EasyPiper! This document provides guidelines and instructions for contributing.

## Development Setup

1. Fork the repository
2. Clone your fork with submodules:
   ```bash
   git clone --recursive https://github.com/<YOUR_USERNAME>/easy_piper.git
   cd easy_piper
   ```

3. Install development dependencies:
   ```bash
   pip install -e .[dev]
   ```

4. Create a new branch for your feature:
   ```bash
   git checkout -b feature/my-new-feature
   ```

## Code Style

- Follow PEP 8 guidelines
- Use `black` for code formatting:
  ```bash
  black .
  ```
- Use `flake8` for linting:
  ```bash
  flake8 .
  ```
- Write clear docstrings for all public functions and classes
- Add type hints where appropriate

## Testing

- Write tests for new features
- Ensure all tests pass before submitting:
  ```bash
  pytest tests/
  ```
- Test with actual hardware if possible

## Documentation

- Update relevant documentation in the `docs/` folder
- Add examples for new features
- Update README.md if adding major features
- Keep docstrings up to date

## Commit Messages

Write clear, concise commit messages:
- Use present tense ("Add feature" not "Added feature")
- Start with a capital letter
- Keep the first line under 72 characters
- Add detailed description if needed

Example:
```
Add gripper force control method

- Implement set_gripper_force() method
- Add safety checks for force limits
- Update documentation and examples
```

## Pull Request Process

1. Update documentation and tests
2. Run all tests and linting
3. Push to your fork:
   ```bash
   git push origin feature/my-new-feature
   ```
4. Create a Pull Request with:
   - Clear description of changes
   - Reference to any related issues
   - Screenshots/videos for UI changes
   - Test results

## Working with Submodules

If your contribution requires changes to submodules (piper_sdk or piper_sdk_ui):

1. Make changes in the submodule's repository first
2. Create a PR in the submodule's repository
3. Wait for the submodule PR to be merged
4. Update the submodule reference in easy_piper
5. Create a PR in easy_piper with the updated submodule

## Reporting Bugs

When reporting bugs, include:
- Python version
- Operating system
- Hardware configuration (CAN device, robot model)
- Minimal reproducible example
- Error messages and stack traces
- Expected vs actual behavior

## Feature Requests

When requesting features:
- Describe the use case clearly
- Explain why the feature would be useful
- Provide examples if possible
- Consider submitting a PR!

## Questions?

- Check existing documentation in `docs/`
- Search existing issues
- Create a new issue with the "question" label

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Help others learn

Thank you for contributing to EasyPiper! 🤖
