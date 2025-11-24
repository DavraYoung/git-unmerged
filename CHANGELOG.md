# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-11-24

### Added
- **Contributors column** in default output showing authors who committed in each branch
- **Verbose mode** (`--verbose` flag) to display detailed commit information
  - Shows commit hash, author, date, and subject for all missing commits
  - Displays full contributor list with emails
- Comprehensive test suite with 13 test cases
- Shell script (`test_setup.sh`) for setting up test repositories
- GitHub Actions CI/CD workflow for automated testing
- Development requirements file (`requirements-dev.txt`)

### Changed
- Default output now includes Contributors column between Commits and Last Commit Date
- Updated table formatting to accommodate new contributor information
- Improved analyzer module with new methods:
  - `get_contributors()` - Get unique contributors for unmerged commits
  - `get_unmerged_commit_details()` - Get detailed commit information
  - Updated `analyze()` method with optional parameters for contributor and commit details

### Testing
- Added 13 automated tests covering:
  - Analyzer functionality (branch detection, contributor tracking, commit details)
  - CLI functionality (default mode, verbose mode, help)
  - Edge cases (invalid paths, ignore patterns, merged branches)
- Tests run on Windows, Linux, and macOS via GitHub Actions
- Python 3.8-3.12 compatibility testing

## [1.0.0] - 2025-11-24

### Added
- Initial release
- Find branches with recent commits (configurable time window)
- Identify unmerged branches compared to base branch
- Filter branches by ignore patterns
- Configurable base branch, time window, and ignore patterns
- Clean tabular output showing unmerged commit counts
- Command-line interface with multiple options
- Python module API for programmatic use
