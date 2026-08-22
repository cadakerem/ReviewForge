# Changelog

All notable changes to this project will be documented in this file.

## [v1.0.7] - 2026-08-22
### Changed
- **Docs:** Synchronized README with actual action defaults. Updated model examples to `gemini-3.7-flash/pro`.
- **Docs:** Fixed the quick setup guide to recommend pinning to the stable `@v1` tag instead of the mutable `@master` branch.
- **Docs:** Added `auto_create_issues` input flag to the configuration table.

## [v1.0.6] - 2026-08-22
### Fixed
- **Encoding:** Replaced literal emoji characters with explicit Python Unicode escape sequences (e.g., `\U0001f6e1\ufe0f`) in `src/core.py` to permanently prevent Mojibake corruption regardless of the host OS or terminal encoding.

## [v1.0.5] - 2026-08-22
### Added
- **Security (Anti-DoS):** Implemented a `MAX_DIFF_LENGTH` limit (20,000 characters). Diffs exceeding this limit are truncated before being sent to the AI, preventing token exhaustion and cost-inflation attacks.
- **Feature:** Added the `auto_create_issues` toggle to allow users to disable autonomous issue creation.

### Changed
- **Architecture:** Extracted the core orchestration logic from `action_entry.py` into a unified `src/core.py`.
- **Architecture:** Aligned the standalone FastAPI server (`src/main.py`) to use `src/core.py` via asynchronous background tasks, ensuring the webhook implementation benefits from all security patches applied to the GitHub Action.

### Removed
- **Cleanup:** Deleted unused/vulnerable dummy files (`src/auth/dummy_login.py`) and development test scripts (`test_google.py`, `test_openai.py`).

## [v1.0.4] - 2026-08-22
### Fixed
- **Security:** Added `author_association` checks. Only PRs from `OWNER`, `MEMBER`, or `COLLABORATOR` are analyzed, preventing prompt injection from untrusted external contributors.
- **Security:** Fixed the webhook `verify_signature` logic to be "fail-closed" instead of "fail-open".
- **Stability:** Hardened the JSON regex extractor to ensure raw JSON is stripped from comments even on parse failure, preventing internal prompt leakage.
- **Routing:** Updated the Agentic Router to fetch changed files in a PR using `per_page=100` to prevent missing critical files due to GitHub API pagination limits.

## [v1.0.3] - 2026-08-22
### Added
- **GitHub Action:** Officially converted the project into a Serverless GitHub Action (`action.yml`).

## [v1.0.2] - 2026-08-22
### Added
- **Integration:** Implemented GitHub API hooks to automatically post PR and Commit comments with AI reviews.
- **Automation:** Added automatic JSON extraction and GitHub Issue creation for critical vulnerabilities.

## [v1.0.1] - 2026-08-22
### Added
- **Multi-Provider AI:** Introduced support for seamless switching between Gemini, OpenAI, Groq, and Nvidia endpoints.

## [v1.0.0] - 2026-08-22
### Added
- **Initial Release:** Core webhook listener, basic AI routing logic (`src/router.py`), and diff analysis functionality established.
