#!/usr/bin/env python3
"""
Test suite for git-unmerged tool.
Tests both the analyzer module and CLI functionality.
"""

import os
import subprocess
import tempfile
import unittest
from pathlib import Path
import shutil

from git_unmerged.analyzer import GitUnmerged


class TestGitUnmergedSetup(unittest.TestCase):
    """Test the setup of the test repository."""

    @classmethod
    def setUpClass(cls):
        """Set up test repository once for all tests."""
        cls.test_repo_path = tempfile.mkdtemp(prefix='git-unmerged-test-')

        # Run the setup script
        script_path = os.path.join(Path(__file__).parent.parent, 'test_setup.sh')
        if not os.path.exists(script_path):
            raise FileNotFoundError(f"Setup script not found: {script_path}")

        print(f"\nSetting up test repository at: {cls.test_repo_path}")

        # Convert Windows path to Unix-style path for Git Bash if on Windows
        def to_unix_path(path):
            """Convert Windows path to Unix-style path for Git Bash."""
            unix_path = path.replace('\\', '/')
            # Handle Windows drive letters (C:/ -> /c/)
            if len(unix_path) > 1 and unix_path[1] == ':':
                unix_path = '/' + unix_path[0].lower() + unix_path[2:]
            return unix_path

        script_path_unix = to_unix_path(script_path) if os.name == 'nt' else script_path
        test_repo_path_unix = to_unix_path(cls.test_repo_path) if os.name == 'nt' else cls.test_repo_path

        # Try to find bash executable
        bash_cmd = shutil.which('bash')
        if not bash_cmd:
            # Try common locations
            for bash_path in ['/usr/bin/bash', '/bin/bash', 'C:\\Program Files\\Git\\bin\\bash.exe']:
                if os.path.exists(bash_path):
                    bash_cmd = bash_path
                    break

        if not bash_cmd:
            raise RuntimeError("bash executable not found")

        result = subprocess.run(
            [bash_cmd, script_path_unix, test_repo_path_unix],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"Setup script stdout: {result.stdout}")
            print(f"Setup script stderr: {result.stderr}")
            raise RuntimeError(f"Failed to set up test repository: {result.stderr}")

        print(f"Test repository created successfully")

    @classmethod
    def tearDownClass(cls):
        """Clean up test repository after all tests."""
        if hasattr(cls, 'test_repo_path') and os.path.exists(cls.test_repo_path):
            print(f"\nCleaning up test repository: {cls.test_repo_path}")
            # On Windows, git files may be read-only, so we need to handle permissions
            def handle_remove_readonly(func, path, exc):
                """Error handler for Windows readonly files."""
                if os.name == 'nt':
                    os.chmod(path, 0o777)
                    func(path)
                else:
                    raise

            shutil.rmtree(cls.test_repo_path, onerror=handle_remove_readonly)


class TestGitUnmergedAnalyzer(TestGitUnmergedSetup):
    """Test the GitUnmerged analyzer class."""

    def setUp(self):
        """Set up analyzer for each test."""
        self.analyzer = GitUnmerged(
            repo_path=self.test_repo_path,
            base_branch='origin/dev',
            ignore_pattern=None,
            days=365
        )

    def test_get_recent_branches(self):
        """Test that we can get recent branches."""
        branches = self.analyzer.get_recent_branches()
        self.assertIsInstance(branches, list)
        self.assertGreater(len(branches), 0, "Should find at least one branch")

        # Check branch structure
        for branch in branches:
            self.assertIn('name', branch)
            self.assertIn('full_name', branch)
            self.assertIn('date', branch)

    def test_analyze_without_fetch(self):
        """Test basic analysis without fetching."""
        unmerged_branches = self.analyzer.analyze(fetch=False)

        self.assertIsInstance(unmerged_branches, list)
        # Should have 3 unmerged branches: user-auth, database, api-endpoints
        # hotfix/bug-123 is already merged
        self.assertGreaterEqual(len(unmerged_branches), 3,
                               "Should find at least 3 unmerged branches")

        # Check that each branch has required fields
        for branch in unmerged_branches:
            self.assertIn('name', branch)
            self.assertIn('unmerged_commits', branch)
            self.assertGreater(branch['unmerged_commits'], 0)

    def test_contributors_included(self):
        """Test that contributors are included in analysis."""
        unmerged_branches = self.analyzer.analyze(
            fetch=False,
            include_contributors=True
        )

        self.assertGreater(len(unmerged_branches), 0, "Should find unmerged branches")

        # Check that contributors are included
        for branch in unmerged_branches:
            self.assertIn('contributors', branch)
            self.assertIsInstance(branch['contributors'], list)

            # At least one contributor per branch
            if branch['unmerged_commits'] > 0:
                self.assertGreater(len(branch['contributors']), 0,
                                 f"Branch {branch['name']} should have contributors")

    def test_commit_details_included(self):
        """Test that detailed commit information is included when requested."""
        unmerged_branches = self.analyzer.analyze(
            fetch=False,
            include_commit_details=True
        )

        self.assertGreater(len(unmerged_branches), 0, "Should find unmerged branches")

        # Check that commit details are included
        for branch in unmerged_branches:
            self.assertIn('commit_details', branch)
            self.assertIsInstance(branch['commit_details'], list)

            # Number of commit details should match unmerged count
            self.assertEqual(len(branch['commit_details']),
                           branch['unmerged_commits'],
                           f"Branch {branch['name']} commit count mismatch")

            # Verify commit detail structure
            for commit in branch['commit_details']:
                self.assertIn('hash', commit)
                self.assertIn('author_name', commit)
                self.assertIn('author_email', commit)
                self.assertIn('subject', commit)
                self.assertIn('date', commit)

    def test_specific_branches(self):
        """Test that specific expected branches are found."""
        unmerged_branches = self.analyzer.analyze(
            fetch=False,
            include_contributors=True
        )

        branch_names = [b['name'] for b in unmerged_branches]

        # These branches should be unmerged
        self.assertIn('feature/user-auth', branch_names)
        self.assertIn('feature/database', branch_names)
        self.assertIn('feature/api-endpoints', branch_names)

        # hotfix/bug-123 is merged, so it should NOT appear
        self.assertNotIn('hotfix/bug-123', branch_names)

    def test_user_auth_branch_details(self):
        """Test specific details of the feature/user-auth branch."""
        unmerged_branches = self.analyzer.analyze(
            fetch=False,
            include_contributors=True,
            include_commit_details=True
        )

        # Find the user-auth branch
        user_auth = next(
            (b for b in unmerged_branches if b['name'] == 'feature/user-auth'),
            None
        )

        self.assertIsNotNone(user_auth, "feature/user-auth branch should exist")
        self.assertEqual(user_auth['unmerged_commits'], 3,
                        "feature/user-auth should have 3 unmerged commits")

        # Should have 2 contributors: Test User and John Doe
        self.assertEqual(len(user_auth['contributors']), 2,
                        "feature/user-auth should have 2 contributors")

        contributor_names = [c.split('<')[0].strip() for c in user_auth['contributors']]
        self.assertIn('Test User', contributor_names)
        self.assertIn('John Doe', contributor_names)


class TestGitUnmergedCLI(TestGitUnmergedSetup):
    """Test the CLI functionality."""

    def run_cli(self, *args):
        """Helper method to run the CLI and capture output."""
        cmd = ['git-unmerged', '--repo', self.test_repo_path] + list(args)
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        return result

    def test_cli_basic_run(self):
        """Test basic CLI execution."""
        result = self.run_cli(
            '--base-branch', 'origin/dev',
            '--ignore-pattern', '',
            '--no-fetch',
            '--days', '365'
        )

        self.assertEqual(result.returncode, 0,
                        f"CLI should exit successfully. Error: {result.stderr}")
        self.assertIn('Found', result.stdout)
        self.assertIn('branches NOT merged', result.stdout)

    def test_cli_default_mode_shows_contributors(self):
        """Test that default mode shows contributors in output."""
        result = self.run_cli(
            '--base-branch', 'origin/dev',
            '--ignore-pattern', '',
            '--no-fetch',
            '--days', '365'
        )

        self.assertEqual(result.returncode, 0)

        # Check for contributors column header
        self.assertIn('Contributors', result.stdout,
                     "Default mode should show Contributors column")

        # Check for specific contributors
        self.assertIn('John Doe', result.stdout)
        self.assertIn('Jane Smith', result.stdout)
        self.assertIn('Bob Johnson', result.stdout)

    def test_cli_verbose_mode(self):
        """Test that verbose mode shows detailed commit information."""
        result = self.run_cli(
            '--base-branch', 'origin/dev',
            '--ignore-pattern', '',
            '--no-fetch',
            '--days', '365',
            '--verbose'
        )

        self.assertEqual(result.returncode, 0)

        # Check for verbose mode indicators
        self.assertIn('Missing commits against', result.stdout,
                     "Verbose mode should show 'Missing commits against'")
        self.assertIn('Hash', result.stdout,
                     "Verbose mode should show commit hash column")
        self.assertIn('Author', result.stdout,
                     "Verbose mode should show author column")
        self.assertIn('Subject', result.stdout,
                     "Verbose mode should show subject column")

        # Check for specific commit messages
        self.assertIn('Add user authentication', result.stdout)
        self.assertIn('Add database schema', result.stdout)
        self.assertIn('Add REST API endpoints', result.stdout)

    def test_cli_help(self):
        """Test that help flag works."""
        result = subprocess.run(
            ['git-unmerged', '--help'],
            capture_output=True,
            text=True
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn('--verbose', result.stdout,
                     "Help should mention --verbose flag")
        self.assertIn('Show detailed commit information', result.stdout)

    def test_cli_ignores_merged_branches(self):
        """Test that merged branches are not shown."""
        result = self.run_cli(
            '--base-branch', 'origin/dev',
            '--ignore-pattern', '',
            '--no-fetch',
            '--days', '365'
        )

        self.assertEqual(result.returncode, 0)

        # hotfix/bug-123 was merged, should not appear
        self.assertNotIn('hotfix/bug-123', result.stdout,
                        "Merged branch should not appear in output")


class TestGitUnmergedEdgeCases(TestGitUnmergedSetup):
    """Test edge cases and error handling."""

    def test_invalid_repo_path(self):
        """Test handling of invalid repository path."""
        result = subprocess.run(
            ['git-unmerged', '--repo', '/nonexistent/path', '--no-fetch'],
            capture_output=True,
            text=True
        )

        self.assertNotEqual(result.returncode, 0,
                          "Should fail with invalid repo path")
        self.assertIn('does not exist', result.stderr)

    def test_ignore_pattern(self):
        """Test branch ignore pattern functionality."""
        analyzer = GitUnmerged(
            repo_path=self.test_repo_path,
            base_branch='origin/dev',
            ignore_pattern='hotfix',
            days=365
        )

        unmerged_branches = analyzer.analyze(fetch=False)
        branch_names = [b['name'] for b in unmerged_branches]

        # hotfix branches should be ignored
        for name in branch_names:
            self.assertNotIn('hotfix', name,
                           f"Branch {name} should be ignored by pattern")


if __name__ == '__main__':
    unittest.main(verbosity=2)
