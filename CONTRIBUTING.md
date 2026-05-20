# Contributing Guidelines

Thank you for your interest in contributing to **Damn Antigravity IDE Migrator**!

This project aims to safely and seamlessly migrate critical configurations, extensions, and valuable conversation histories from the legacy Antigravity editor to the new Antigravity IDE.

Any contributions (bug reports, documentation updates, code changes, etc.) are highly welcome.

## 1. Issue Reporting Guidelines

To help us understand and resolve issues efficiently, please follow these guidelines when opening an Issue:

### Bug Reports
When reporting a bug, please include the following details:
1. **Environment**: Your OS version (e.g., Windows 10/11) and legacy Antigravity version.
2. **Steps to Reproduce**: Provide step-by-step instructions on what actions cause the issue.
3. **Logs**: Attach the contents of the `migration.log` file generated in the project root directory, or paste the full console error output.

### Feature Requests
When suggesting new options or features:
1. **Motivation**: Explain why this feature is useful and what problem it solves.
2. **Proposed Solution**: Describe how the new feature should work.

---

## 2. Pull Request (PR) Process

If you would like to contribute code improvements or bug fixes:
1. **Fork** the repository and create a new working branch.
2. Run the [unit tests](#3-development-setup--testing) locally to ensure everything works and all tests pass.
3. Submit a **Pull Request (PR)**, summarizing your changes and explaining the reasoning behind them.

---

## 3. Development Setup & Testing

This tool is designed to be lightweight and zero-dependency, using only the **Python Standard Library**. No external pip installation is required.

* **Requirements**: Python 3.8+
* **Running Unit Tests**:
  Always verify that your changes do not break existing behaviors by running the tests:
  ```bash
  python -m unittest tests/test_migration.py
  ```

## 4. Coding Guidelines

* **Standard Library Only**: Do not add external package dependencies (no pip install requirements).
* **Safety First**: Ensure automatic backups and robust rollbacks are implemented before making any filesystem or database changes.
* **Code Style**: Adhere to PEP 8 standards and write clear, self-explanatory variable and function names.

## 5. License

By contributing to this project, you agree that your contributions will be licensed under the **MIT License**.
