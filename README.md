# Git Unmerged

A Python command-line tool to analyze git branches and find commits that haven't been merged into a base branch.

## Features

- Find all branches with recent commits (configurable time window)
- Identify branches not yet merged into a base branch (e.g., `dev`, `main`)
- Filter branches by ignore patterns
- Configurable base branch, time window, and ignore patterns
- Clean, tabular output showing unmerged commit counts

## Installation

### From source

```bash
cd /c/tmp/git-unmerged
pip install .
```

### Development installation

```bash
cd /c/tmp/git-unmerged
pip install -e .
```

## Usage

### Basic usage (analyze current directory)

```bash
git-unmerged
```

### Analyze a specific repository

```bash
git-unmerged --repo /path/to/repo
```

### Compare against a different base branch

```bash
git-unmerged --base-branch origin/main
```

### Change the ignore pattern

```bash
# Ignore branches containing 'hotfix'
git-unmerged --ignore-pattern hotfix

# Don't ignore any branches
git-unmerged --ignore-pattern ""
```

### Look back a different number of days

```bash
# Look back 90 days instead of the default 60
git-unmerged --days 90
```

### Skip fetching from remote

```bash
git-unmerged --no-fetch
```

### Combined example

```bash
git-unmerged \
  --repo /path/to/eld-system-mobile \
  --base-branch origin/dev \
  --ignore-pattern "-eld" \
  --days 60
```

## Command-line Options

| Option | Default | Description |
|--------|---------|-------------|
| `--repo` | `.` (current directory) | Path to the git repository |
| `--base-branch` | `origin/dev` | Base branch to compare against |
| `--ignore-pattern` | `-eld` | Pattern to ignore in branch names (use `""` to disable) |
| `--days` | `60` | Number of days to look back for recent commits |
| `--no-fetch` | `False` | Skip fetching from remote |
| `--version` | - | Show version and exit |
| `--help` | - | Show help message and exit |

## Output Example

```
Fetching latest changes from remote...

Finding branches with commits in the last 60 days...
Ignoring branches containing: '-eld'

Found 22 branches NOT merged into origin/dev:

Branch Name                                                  Commits    Last Commit Date
----------------------------------------------------------------------------------------------------
feat/timing-compliance                                       15         2025-11-21 23:25:02 +0500
feature/set_event_to_doc_activity                            1          2025-11-21 21:49:45 +0500
hotfix/improve-split-sleep                                   2          2025-11-21 20:27:51 +0500
...


Total unmerged branches: 22
```

## Use as a Python Module

You can also use the analyzer programmatically:

```python
from git_unmerged.analyzer import GitUnmerged

analyzer = GitUnmerged(
    repo_path='/path/to/repo',
    base_branch='origin/dev',
    ignore_pattern='-eld',
    days=60
)

unmerged_branches = analyzer.analyze(fetch=True)

for branch in unmerged_branches:
    print(f"{branch['name']}: {branch['unmerged_commits']} commits")
```

## Requirements

- Python 3.7 or higher
- Git installed and available in PATH

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
