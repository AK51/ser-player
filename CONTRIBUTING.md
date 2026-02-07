# Contributing to SER File Viewer

Thank you for your interest in contributing to SER File Viewer! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Create a new branch for your feature or bugfix
4. Make your changes
5. Test your changes thoroughly
6. Submit a pull request

## Development Setup

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Git

### Installation

```bash
# Clone your fork
git clone https://github.com/yourusername/ser-file-viewer.git
cd ser-file-viewer

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov hypothesis
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m property      # Property-based tests only
pytest -m integration   # Integration tests only
```

## Code Style

- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions focused and concise
- Comment complex logic

## Pull Request Process

1. **Update Documentation**: Ensure README.md and USER_MANUAL.md are updated if needed
2. **Add Tests**: Include tests for new features or bug fixes
3. **Test Thoroughly**: Run the full test suite before submitting
4. **Write Clear Commit Messages**: Use descriptive commit messages
5. **One Feature Per PR**: Keep pull requests focused on a single feature or fix

### Commit Message Format

```
<type>: <short summary>

<detailed description if needed>

<issue reference if applicable>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Adding or updating tests
- `refactor`: Code refactoring
- `style`: Code style changes (formatting, etc.)
- `perf`: Performance improvements

Example:
```
feat: Add support for AVI file format

Implemented AVI file parsing and frame extraction.
Added tests for AVI format support.

Closes #42
```

## Reporting Bugs

When reporting bugs, please include:

1. **Description**: Clear description of the bug
2. **Steps to Reproduce**: Detailed steps to reproduce the issue
3. **Expected Behavior**: What you expected to happen
4. **Actual Behavior**: What actually happened
5. **Environment**: OS, Python version, package versions
6. **Log Files**: Include relevant log output from `ser_viewer.log`
7. **Sample Files**: If possible, provide a sample SER file that triggers the bug

## Feature Requests

When requesting features, please include:

1. **Use Case**: Describe the problem you're trying to solve
2. **Proposed Solution**: Your idea for how to solve it
3. **Alternatives**: Other solutions you've considered
4. **Additional Context**: Any other relevant information

## Code Review Process

All submissions require review. We use GitHub pull requests for this purpose. The review process includes:

1. **Automated Tests**: All tests must pass
2. **Code Review**: At least one maintainer will review your code
3. **Documentation**: Ensure documentation is updated
4. **Discussion**: Be prepared to discuss and iterate on your changes

## Areas for Contribution

Here are some areas where contributions are especially welcome:

### Features
- Additional file format support (AVI, MP4, FITS)
- Advanced image processing algorithms
- Batch processing capabilities
- Export to additional formats
- Performance optimizations

### Testing
- Additional unit tests
- Property-based tests
- Integration tests
- Performance benchmarks

### Documentation
- Tutorial videos
- Example workflows
- API documentation
- Translation to other languages

### Bug Fixes
- Check the issue tracker for open bugs
- Fix any bugs you encounter while using the software

## Questions?

If you have questions about contributing, feel free to:
- Open an issue with the "question" label
- Contact the maintainers

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors.

### Our Standards

- Be respectful and considerate
- Welcome newcomers and help them get started
- Focus on what is best for the community
- Show empathy towards other community members

### Unacceptable Behavior

- Harassment or discrimination of any kind
- Trolling or insulting comments
- Publishing others' private information
- Other conduct which could reasonably be considered inappropriate

## License

By contributing to SER File Viewer, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to SER File Viewer!
