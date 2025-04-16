# Contributing to Toronto Trendspotter

Thank you for your interest in contributing to the Toronto Trendspotter project! This document provides guidelines for contributions to ensure a smooth collaboration process.

## Development Setup

1. Fork the repository
2. Clone your fork to your local machine
3. Set up a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and fill in the required values
5. Create a new branch for your feature or bug fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Code Style Guidelines

This project follows these style guides:

- **Python**: [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- **JavaScript/React**: [Airbnb Style Guide](https://github.com/airbnb/javascript)

We use automatic code formatters to maintain consistent style:

- **Python**: Use `black` and `isort` to format Python code:
  ```bash
  black src/
  isort src/
  ```
- **JavaScript**: Use Prettier for frontend code:
  ```bash
  npm run format
  ```

## Testing

- All new features should include appropriate tests
- Run tests before submitting a pull request:
  ```bash
  pytest
  ```

## Pull Request Process

1. Update the README.md or documentation with details of changes if applicable
2. Run all tests and ensure they pass
3. Make sure your code follows the style guidelines
4. Submit your pull request with a clear description of the changes
5. Link any related issues in your pull request description

## Commit Message Guidelines

Follow these guidelines for commit messages:

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests after the first line

Example:
```
Add Toronto events integration with Eventbrite API

- Implement API client for Eventbrite
- Add data transformers for event format
- Create database models for events
- Write tests for API integration

Resolves #123
```

## Issue Reporting

When reporting issues, please include:

- A clear, descriptive title
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Screenshots if applicable
- Your environment information (OS, browser, Python version, etc.)

## Feature Requests

Feature requests are welcome! Please provide:

- A clear, descriptive title
- Detailed description of the proposed feature
- Explanation of why this feature would be useful
- Examples of how it would be used

## Questions?

If you have any questions about contributing, please open an issue with the "question" label.