# Git Unmerged

A Python command-line tool to analyze git branches and find commits that haven't been merged into a base branch.

## Features

- Find all branches with recent commits (configurable time window)
- Identify branches not yet merged into a base branch (e.g., `dev`, `main`)
- Filter branches by ignore patterns
- Configurable base branch, time window, and ignore patterns
- **Show contributors** (authors) who committed in each branch
- **Verbose mode** to display detailed commit information (hash, author, date, subject)
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

### Verbose mode (show detailed commit information)

```bash
# Show all missing commits with details
git-unmerged --verbose

# Combine with other options
git-unmerged --repo /path/to/repo --verbose
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
| `--verbose` | `False` | Show detailed commit information for each branch |
| `--version` | - | Show version and exit |
| `--help` | - | Show help message and exit |

## Output Examples

### Default Mode

Shows a table with contributors for each branch:

```
Fetching latest changes from remote...

Finding branches with commits in the last 60 days...
Ignoring branches containing: '-eld'

Found 22 branches NOT merged into origin/dev:

Branch Name                                        Commits    Contributors                             Last Commit Date
--------------------------------------------------------------------------------------------------------------------------------------------
feat/timing-compliance                             15         John Doe, Jane Smith                     2025-11-21 23:25:02 +0500
feature/set_event_to_doc_activity                  1          Bob Johnson                              2025-11-21 21:49:45 +0500
hotfix/improve-split-sleep                         2          Alice Brown                              2025-11-21 20:27:51 +0500
...


Total unmerged branches: 22
```

### Verbose Mode

Shows detailed commit information for each branch:

```
Finding branches with commits in the last 60 days...

Found 3 branches NOT merged into origin/dev:


====================================================================================================
Branch: feature/user-auth
Unmerged commits: 3
Last commit date: 2025-11-21 23:25:02 +0500
Contributors: John Doe <john@example.com>, Test User <test@example.com>

Missing commits against origin/dev:
  Hash       Author                         Date                       Subject
  ---------- ------------------------------ -------------------------- ----------------------------------------
  348a291    John Doe <john@example.com>    2025-11-21 11:32:08 +0500  Implement JWT token support
  289ba81    John Doe <john@example.com>    2025-11-21 11:32:08 +0500  Add password validation
  be1f766    Test User <test@example.com>   2025-11-21 11:32:08 +0500  Add user authentication

====================================================================================================

Total unmerged branches: 3
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
