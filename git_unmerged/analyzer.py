#!/usr/bin/env python3

import subprocess
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Optional


class GitUnmerged:
    """Analyze git branches to find unmerged commits."""

    def __init__(self, repo_path: str, base_branch: str = "origin/dev",
                 ignore_pattern: Optional[str] = "-eld", days: int = 60):
        """
        Initialize the analyzer.

        Args:
            repo_path: Path to the git repository
            base_branch: Base branch to compare against (default: origin/dev)
            ignore_pattern: Pattern to ignore in branch names (default: -eld)
            days: Number of days to look back for recent commits (default: 60)
        """
        self.repo_path = repo_path
        self.base_branch = base_branch
        self.ignore_pattern = ignore_pattern
        self.days = days

    def run_git_command(self, cmd: str) -> str:
        """Run a git command and return the output."""
        try:
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                shell=True
            )
            return result.stdout.strip()
        except Exception as e:
            print(f"Error running command: {e}", file=sys.stderr)
            return ""

    def get_recent_branches(self) -> List[Dict]:
        """Get all branches with commits in the last N days."""
        cutoff_date = datetime.now() - timedelta(days=self.days)

        # Get all remote branches with their last commit dates
        cmd = 'git branch -r --format="%(refname:short)|%(committerdate:iso8601)"'
        output = self.run_git_command(cmd)

        branches = []
        for line in output.split('\n'):
            if not line:
                continue

            # Apply ignore pattern
            if self.ignore_pattern and self.ignore_pattern in line:
                continue

            parts = line.split('|')
            if len(parts) != 2:
                continue

            branch_name = parts[0].strip()
            date_str = parts[1].strip()

            # Skip origin itself and non-branch refs
            if branch_name == 'origin' or 'HEAD' in branch_name:
                continue

            # Parse date
            try:
                # Handle timezone more flexibly - just parse the date/time part
                date_part = date_str.split(' ')[0] + ' ' + date_str.split(' ')[1]
                commit_date = datetime.fromisoformat(date_part)
                if commit_date >= cutoff_date:
                    # Remove 'origin/' prefix
                    clean_name = branch_name.replace('origin/', '')
                    branches.append({
                        'name': clean_name,
                        'full_name': branch_name,
                        'date': commit_date,
                        'date_str': date_str
                    })
            except Exception:
                continue

        return branches

    def get_unmerged_commits(self, branch_name: str) -> int:
        """Get the number of commits in branch that are not in base_branch."""
        # Handle both origin/ prefixed and non-prefixed branch names
        remote_branch = f"origin/{branch_name}" if not branch_name.startswith('origin/') else branch_name
        cmd = f"git log {self.base_branch}..{remote_branch} --oneline"
        output = self.run_git_command(cmd)

        if not output:
            return 0

        return len(output.split('\n'))

    def fetch_remote(self, quiet: bool = True) -> None:
        """Fetch latest changes from remote."""
        cmd = "git fetch --all" + (" --quiet" if quiet else "")
        self.run_git_command(cmd)

    def analyze(self, fetch: bool = True) -> List[Dict]:
        """
        Analyze branches and return unmerged ones.

        Args:
            fetch: Whether to fetch from remote first (default: True)

        Returns:
            List of dictionaries containing branch information
        """
        if fetch:
            self.fetch_remote()

        recent_branches = self.get_recent_branches()

        # Extract base branch name without origin/ prefix
        base_branch_name = self.base_branch.replace('origin/', '')

        unmerged_branches = []
        for branch in recent_branches:
            # Skip the base branch itself
            if branch['name'] == base_branch_name:
                continue

            unmerged_count = self.get_unmerged_commits(branch['name'])
            if unmerged_count > 0:
                branch['unmerged_commits'] = unmerged_count
                unmerged_branches.append(branch)

        # Sort by date (most recent first)
        unmerged_branches.sort(key=lambda x: x['date'], reverse=True)

        return unmerged_branches
