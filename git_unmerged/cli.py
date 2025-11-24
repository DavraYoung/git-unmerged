#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path
from .analyzer import GitUnmerged


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze git branches to find unmerged commits",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze current directory
  git-unmerged

  # Analyze specific repository
  git-unmerged --repo /path/to/repo

  # Compare against main branch instead of dev
  git-unmerged --base-branch origin/main

  # Ignore branches with 'hotfix' pattern
  git-unmerged --ignore-pattern hotfix

  # Look back 90 days instead of 60
  git-unmerged --days 90

  # Don't ignore any branches
  git-unmerged --ignore-pattern ""
        """
    )

    parser.add_argument(
        '--repo',
        type=str,
        default='.',
        help='Path to the git repository (default: current directory)'
    )

    parser.add_argument(
        '--base-branch',
        type=str,
        default='origin/dev',
        help='Base branch to compare against (default: origin/dev)'
    )

    parser.add_argument(
        '--ignore-pattern',
        type=str,
        default='-eld',
        help='Pattern to ignore in branch names (default: -eld). Use empty string to disable.'
    )

    parser.add_argument(
        '--days',
        type=int,
        default=60,
        help='Number of days to look back for recent commits (default: 60)'
    )

    parser.add_argument(
        '--no-fetch',
        action='store_true',
        help='Skip fetching from remote'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )

    args = parser.parse_args()

    # Validate repository path
    repo_path = Path(args.repo).resolve()
    if not repo_path.exists():
        print(f"Error: Repository path does not exist: {repo_path}", file=sys.stderr)
        sys.exit(1)

    git_dir = repo_path / '.git'
    if not git_dir.exists():
        print(f"Error: Not a git repository: {repo_path}", file=sys.stderr)
        sys.exit(1)

    # Handle empty ignore pattern
    ignore_pattern = args.ignore_pattern if args.ignore_pattern else None

    # Create analyzer
    analyzer = GitUnmerged(
        repo_path=str(repo_path),
        base_branch=args.base_branch,
        ignore_pattern=ignore_pattern,
        days=args.days
    )

    # Run analysis
    if not args.no_fetch:
        print("Fetching latest changes from remote...")

    print(f"\nFinding branches with commits in the last {args.days} days...")
    if ignore_pattern:
        print(f"Ignoring branches containing: '{ignore_pattern}'")

    unmerged_branches = analyzer.analyze(fetch=not args.no_fetch)

    print(f"\nFound {len(unmerged_branches)} branches NOT merged into {args.base_branch}:\n")

    if unmerged_branches:
        # Print table header
        print(f"{'Branch Name':<60} {'Commits':<10} {'Last Commit Date'}")
        print("-" * 100)

        # Print branches
        for branch in unmerged_branches:
            print(f"{branch['name']:<60} {branch['unmerged_commits']:<10} {branch['date_str']}")

        print(f"\n\nTotal unmerged branches: {len(unmerged_branches)}")
    else:
        print("No unmerged branches found.")

    return 0


if __name__ == '__main__':
    sys.exit(main())
