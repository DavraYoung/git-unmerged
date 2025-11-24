# Quick Start Guide

## Installation

```bash
cd /c/tmp/git-unmerged
pip install -e .
```

## Basic Usage

### 1. Analyze current directory (default settings)

```bash
cd /path/to/your/repo
git-unmerged
```

### 2. Analyze specific repository

```bash
git-unmerged --repo C:/projects/logitex/eld-system-mobile
```

### 3. Change base branch (compare against main instead of dev)

```bash
git-unmerged --repo /path/to/repo --base-branch origin/main
```

### 4. Change ignore pattern

```bash
# Ignore branches with 'hotfix'
git-unmerged --ignore-pattern hotfix

# Don't ignore any branches
git-unmerged --ignore-pattern ""
```

### 5. Change time window (look back 90 days)

```bash
git-unmerged --days 90
```

### 6. Skip fetching (use existing local data)

```bash
git-unmerged --no-fetch
```

## Common Use Cases

### Find all unmerged feature branches in eld-system-mobile

```bash
git-unmerged \
  --repo C:/projects/logitex/eld-system-mobile \
  --base-branch origin/dev \
  --ignore-pattern "-eld"
```

### Find recent branches (last 30 days) not in main

```bash
git-unmerged \
  --repo /path/to/repo \
  --base-branch origin/main \
  --days 30
```

### Quick check without fetching

```bash
git-unmerged --repo /path/to/repo --no-fetch
```

## Using as Python Module

Create a Python script:

```python
from git_unmerged.analyzer import GitUnmerged

analyzer = GitUnmerged(
    repo_path='C:/projects/logitex/eld-system-mobile',
    base_branch='origin/dev',
    ignore_pattern='-eld',
    days=60
)

unmerged = analyzer.analyze(fetch=True)

for branch in unmerged:
    print(f"{branch['name']}: {branch['unmerged_commits']} commits")
```

## Output Format

The tool outputs a table with:
- **Branch Name**: Name of the branch (without `origin/` prefix)
- **Commits**: Number of commits not yet in the base branch
- **Last Commit Date**: Date of the most recent commit

Example:
```
Branch Name                                                  Commits    Last Commit Date
----------------------------------------------------------------------------------------------------
feat/timing-compliance                                       15         2025-11-21 23:25:02 +0500
feature/shift_duration                                       11         2025-11-18 22:06:03 +0500
```

## Tips

1. **Use `--no-fetch`** for faster results if you've recently fetched
2. **Adjust `--days`** to focus on recent or older branches
3. **Use empty `--ignore-pattern ""`** to see all branches
4. **Pipe output** to filter/sort: `git-unmerged | grep feature`
