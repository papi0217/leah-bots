# Contributing to LEAH Bots

Guidelines for contributing to the LEAH Bots project.

## Code Standards

- **Python 3.8+** — All code must be Python 3.8 compatible
- **PEP 8** — Follow Python style guide
- **Type Hints** — Use type hints for all functions
- **Docstrings** — Document all classes and functions
- **Error Handling** — Comprehensive try/except blocks
- **Logging** — Log important events

## Development Setup

```bash
# Clone repository
git clone https://github.com/papi0217/leah-bots.git
cd leah-bots

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Add your credentials
```

## Making Changes

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make changes and test locally
3. Commit with clear messages: `git commit -m "Add: description"`
4. Push to branch: `git push origin feature/your-feature`
5. Create Pull Request

## Testing

### Local Testing

```bash
python app.py
```

Test both bots on Telegram:
- Send `/start` to both bots
- Test all commands
- Check error handling

### Code Quality

```bash
# Check syntax
python -m py_compile *.py

# Check imports
python -c "import app"
```

## Commit Messages

Use clear, descriptive commit messages:

- `Add: new feature description`
- `Fix: bug description`
- `Update: change description`
- `Refactor: code improvement description`
- `Docs: documentation update`

## Pull Request Process

1. Update README.md if needed
2. Add tests for new features
3. Ensure all tests pass
4. Provide clear description of changes
5. Link related issues

## Code Review

All pull requests require review before merging.

## Reporting Issues

Include:
- Clear description of issue
- Steps to reproduce
- Expected vs actual behavior
- Logs/error messages
- Environment (OS, Python version, etc.)

## Questions?

Open an issue or contact the maintainers.

---

**Thank you for contributing to LEAH!** ❤️
