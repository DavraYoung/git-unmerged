#!/usr/bin/env python3

"""Example usage of git-unmerged as a Python module."""

from git_unmerged.analyzer import GitUnmerged


def main():
    # Create analyzer instance
    analyzer = GitUnmerged(
        repo_path='C:/projects/logitex/eld-system-mobile',
        base_branch='origin/dev',
        ignore_pattern='-eld',
        days=60
    )

    # Get unmerged branches
    print("Analyzing repository...")
    unmerged_branches = analyzer.analyze(fetch=True)

    # Print results
    print(f"\nFound {len(unmerged_branches)} unmerged branches:\n")

    for branch in unmerged_branches:
        print(f"Branch: {branch['name']}")
        print(f"  Unmerged commits: {branch['unmerged_commits']}")
        print(f"  Last commit: {branch['date_str']}")
        print()

    # Example: Get only branches with more than 5 unmerged commits
    large_branches = [b for b in unmerged_branches if b['unmerged_commits'] > 5]
    print(f"\nBranches with more than 5 unmerged commits: {len(large_branches)}")
    for branch in large_branches:
        print(f"  - {branch['name']}: {branch['unmerged_commits']} commits")


if __name__ == '__main__':
    main()
