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
        '--verbose',
        action='store_true',
        help='Show detailed commit information for each branch'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.1.0'
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

    unmerged_branches = analyzer.analyze(
        fetch=not args.no_fetch,
        include_contributors=True,
        include_commit_details=args.verbose
    )

    print(f"\nFound {len(unmerged_branches)} branches NOT merged into {args.base_branch}:\n")

    if unmerged_branches:
        if args.verbose:
            # Verbose mode: show detailed commit information
            for branch in unmerged_branches:
                print(f"\n{'='*100}")
                print(f"Branch: {branch['name']}")
                print(f"Unmerged commits: {branch['unmerged_commits']}")
                print(f"Last commit date: {branch['date_str']}")

                # Show contributors
                if 'contributors' in branch and branch['contributors']:
                    print(f"Contributors: {', '.join(branch['contributors'])}")

                # Show detailed commits
                if 'commit_details' in branch and branch['commit_details']:
                    print(f"\nMissing commits against {args.base_branch}:")
                    print(f"  {'Hash':<10} {'Author':<30} {'Date':<26} {'Subject'}")
                    print(f"  {'-'*10} {'-'*30} {'-'*26} {'-'*40}")
                    for commit in branch['commit_details']:
                        author = f"{commit['author_name']} <{commit['author_email']}>"
                        if len(author) > 30:
                            author = author[:27] + "..."
                        subject = commit['subject']
                        if len(subject) > 40:
                            subject = subject[:37] + "..."
                        print(f"  {commit['hash']:<10} {author:<30} {commit['date']:<26} {subject}")

            print(f"\n{'='*100}")
            print(f"\nTotal unmerged branches: {len(unmerged_branches)}")
        else:
            # Default mode: show table with contributors
            print(f"{'Branch Name':<50} {'Commits':<10} {'Contributors':<40} {'Last Commit Date'}")
            print("-" * 140)

            # Print branches
            for branch in unmerged_branches:
                # Format contributors list
                contributors = ""
                if 'contributors' in branch and branch['contributors']:
                    # Extract just names (without emails) for cleaner display
                    names = [c.split('<')[0].strip() for c in branch['contributors']]
                    contributors = ', '.join(names)
                    if len(contributors) > 38:
                        contributors = contributors[:35] + "..."

                print(f"{branch['name']:<50} {branch['unmerged_commits']:<10} {contributors:<40} {branch['date_str']}")

            print(f"\n\nTotal unmerged branches: {len(unmerged_branches)}")
    else:
        print("No unmerged branches found.")

    return 0


if __name__ == '__main__':
    sys.exit(main())
