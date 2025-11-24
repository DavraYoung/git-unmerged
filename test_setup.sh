#!/bin/bash
# Test setup script for git-unmerged
# Creates a test repository with branches and commits to verify functionality

set -e  # Exit on error

# Check if test path is provided
if [ -z "$1" ]; then
    TEST_REPO_PATH="/tmp/git-unmerged-test-repo"
else
    TEST_REPO_PATH="$1"
fi

echo "Setting up test repository at: $TEST_REPO_PATH"

# Clean up existing test repo if it exists
if [ -d "$TEST_REPO_PATH" ]; then
    echo "Removing existing test repository..."
    rm -rf "$TEST_REPO_PATH"
fi

# Create test repository
echo "Creating test repository..."
git init "$TEST_REPO_PATH"
cd "$TEST_REPO_PATH"

# Configure git user for commits
git config user.name "Test User"
git config user.email "test@example.com"

# Create initial commit on main branch
echo "Creating initial commit on main..."
echo "Initial content" > README.md
git add README.md
git commit -m "Initial commit"

# Create and switch to dev branch
echo "Creating dev branch..."
git checkout -b dev
echo "Dev content" >> README.md
git add README.md
git commit -m "Dev branch commit"

# Create feature branch 1 with multiple commits from different authors
echo "Creating feature/user-auth branch..."
git checkout -b feature/user-auth
echo "User auth feature" > auth.txt
git add auth.txt
git commit -m "Add user authentication"

# Change author for second commit
git config user.name "John Doe"
git config user.email "john@example.com"
echo "Password validation" >> auth.txt
git add auth.txt
git commit -m "Add password validation"

# Third commit from same author
echo "JWT tokens" >> auth.txt
git add auth.txt
git commit -m "Implement JWT token support"

# Create feature branch 2 with single author
echo "Creating feature/database branch..."
git checkout dev
git checkout -b feature/database
git config user.name "Jane Smith"
git config user.email "jane@example.com"
echo "Database schema" > schema.sql
git add schema.sql
git commit -m "Add database schema"

echo "Database migrations" >> schema.sql
git add schema.sql
git commit -m "Add migration support"

# Create feature branch 3 with different author
echo "Creating feature/api-endpoints branch..."
git checkout dev
git checkout -b feature/api-endpoints
git config user.name "Bob Johnson"
git config user.email "bob@example.com"
echo "API routes" > api.py
git add api.py
git commit -m "Add REST API endpoints"

# Create a branch that will be merged (no unmerged commits)
echo "Creating and merging hotfix/bug-123 branch..."
git checkout dev
git checkout -b hotfix/bug-123
git config user.name "Alice Brown"
git config user.email "alice@example.com"
echo "Bug fix" > bugfix.txt
git add bugfix.txt
git commit -m "Fix critical bug #123"

# Merge hotfix into dev
git checkout dev
git merge hotfix/bug-123 --no-edit

# Set up remote tracking
echo "Setting up remote tracking..."
git checkout dev
git remote add origin "$TEST_REPO_PATH"

# Rename master to main if it exists
if git show-ref --verify --quiet refs/heads/master; then
    git branch -m master main
fi

# Create remote-tracking branches (simulate remote)
git update-ref refs/remotes/origin/dev refs/heads/dev
git update-ref refs/remotes/origin/main refs/heads/main
git update-ref refs/remotes/origin/feature/user-auth refs/heads/feature/user-auth
git update-ref refs/remotes/origin/feature/database refs/heads/feature/database
git update-ref refs/remotes/origin/feature/api-endpoints refs/heads/feature/api-endpoints
git update-ref refs/remotes/origin/hotfix/bug-123 refs/heads/hotfix/bug-123

echo ""
echo "Test repository created successfully at: $TEST_REPO_PATH"
echo ""
echo "Repository structure:"
echo "  - origin/main: 1 commit"
echo "  - origin/dev: 2 commits (includes merged hotfix)"
echo "  - origin/feature/user-auth: 3 unmerged commits (2 authors: Test User, John Doe)"
echo "  - origin/feature/database: 2 unmerged commits (1 author: Jane Smith)"
echo "  - origin/feature/api-endpoints: 1 unmerged commit (1 author: Bob Johnson)"
echo "  - origin/hotfix/bug-123: Already merged into dev (0 unmerged)"
echo ""
echo "You can now run git-unmerged against this repository:"
echo "  git-unmerged --repo $TEST_REPO_PATH --base-branch origin/dev --ignore-pattern \"\" --no-fetch --days 365"
