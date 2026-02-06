# Contributing to TFC/TFE Practice Evaluator

Thank you for your interest in contributing! This document provides guidelines for contributing to the TFC/TFE Practice Evaluator skill.

## How to Contribute

### Reporting Issues

- Use the [Bug Report](https://github.com/songlining/tfc-practice-evaluator/issues/new?template=bug_report.md) template for bugs
- Use the [Feature Request](https://github.com/songlining/tfc-practice-evaluator/issues/new?template=feature_request.md) template for enhancements
- Search existing issues before creating a new one

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following the code style below
3. **Test your changes** against a TFC/TFE organization
4. **Update documentation** if needed
5. **Submit a pull request** with a clear description

### Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/tfc-practice-evaluator.git
cd tfc-practice-evaluator

# Create a feature branch
git checkout -b feature/my-improvement

# Test the scripts
export TFC_TOKEN="your-token"
export TFC_ORG="your-org"
python3 scripts/collect_tfc_data.py
```

## Code Style

### SKILL.md
- Follow the existing frontmatter format
- Keep instructions clear and actionable
- Include examples where helpful

### Python Scripts
- Python 3.6+ compatible
- Use only standard library (no external dependencies)
- Include docstrings for functions
- Handle errors gracefully with informative messages

### Bash Scripts
- Bash 4.0+ compatible
- Use shellcheck for linting
- Quote variables properly
- Include helpful comments

## Areas for Contribution

### High Priority
- New evaluation categories aligned with HVD
- Improved scoring algorithms
- Better policy gap detection
- Support for additional TFC/TFE API endpoints

### Documentation
- Usage examples and tutorials
- Tips for different organization sizes
- Integration guides

### Testing
- Test data fixtures
- Validation scripts
- Edge case coverage

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow

## Questions?

Open a [Discussion](https://github.com/songlining/tfc-practice-evaluator/discussions) for questions or ideas that aren't bugs or feature requests.

---

Thank you for helping improve TFC/TFE Practice Evaluator! 🎉
