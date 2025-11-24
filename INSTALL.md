# Installation Guide

## Installation Options

### Option 1: Install from source (recommended for development)

```bash
cd /c/tmp/git-unmerged
pip install -e .
```

The `-e` flag installs the package in "editable" mode, so changes to the source code are immediately reflected without reinstalling.

### Option 2: Install from source (regular)

```bash
cd /c/tmp/git-unmerged
pip install .
```

### Option 3: Build and install as wheel

```bash
cd /c/tmp/git-unmerged
python -m build
pip install dist/git_unmerged-1.0.0-py3-none-any.whl
```

### Option 4: Install from PyPI (when published)

```bash
pip install git-unmerged
```

## Verify Installation

After installation, verify it works:

```bash
git-unmerged --version
git-unmerged --help
```

## Uninstallation

```bash
pip uninstall git-unmerged
```

## Requirements

- Python 3.7 or higher
- pip
- Git (installed and available in PATH)

## Troubleshooting

### Command not found

If you get "command not found" after installation, make sure your Python scripts directory is in your PATH:

**Windows:**
```
C:\Users\<YourUsername>\AppData\Local\Programs\Python\Python3XX\Scripts
```

**Linux/Mac:**
```
~/.local/bin
```

### Permission errors

If you get permission errors during installation, try:

```bash
pip install --user .
```

Or use a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install .
```
