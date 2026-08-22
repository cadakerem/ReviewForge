# Changelog

All notable changes to this project will be documented in this file.

## [v1.0.7] - 2026-08-22
### Changed
- **Docs:** Synchronized README with actual action defaults. Updated model examples to `gemini-3.7-flash/pro` and `gpt-oss-120b`.
- **Docs:** Fixed the quick setup guide to recommend pinning to the stable `@v1` tag instead of the mutable `@master` branch.
- **Docs:** Documented the `auto_create_issues` input flag in the configuration table.

## [v1.0.6] - 2026-08-22
### Fixed
- **Encoding:** Replaced literal emoji characters with explicit Python Unicode escape sequences (e.g., `\U0001f6e1\ufe0f`) in `src/core.py` to permanently prevent Mojibake corruption regardless of the host OS or terminal encoding.

## [v1.0.5] - 2026-08-22
### Added
- **Security (Anti-DoS):** Implemented a `MAX_DIFF_LENGTH` limit (20,000 characters). Diffs exceeding this limit are truncated before being sent to the AI, preventing token exhaustion and cost-inflation attacks.
- **Feature:** Added the `auto_create_issues` toggle (default: true) to allow users to disable autonomous issue creation.
- **Provider Update:** Added support for Groq's new `openai/gpt-oss-120b` model.

### Changed
- **Architecture:** Extracted the core orchestration logic from `action_entry.py` into a unified `src/core.py`.
- **Architecture:** Aligned the standalone FastAPI server (`src/main.py`) to use `src/core.py` via asynchronous background tasks, ensuring the webhook implementation benefits from all security patches.
- **Configuration:** Increased AI output token limits (`max_tokens=4096`) for both Gemini Native and OpenAI-compatible SDKs to prevent output truncation during complex code reviews.

### Fixed
- **Bug Fix:** Fixed a `NameError` crash when `auto_create_issues` was set to false (caught by ReviewForge AI!).
- **Cleanup:** Removed vulnerable dummy scripts (`dummy_login.py`, `stripe_handler.py`) and development test files.

## [v1.0.4] - 2026-08-22
### Added
- **Dogfooding:** Added dummy login feature in PR #7 to test the AI review system.

### Changed
- **Provider API:** Migrated Gemini from the OpenAI-compatible endpoint to the Native REST API (`generativelanguage.googleapis.com`) to bypass 404 bugs caused by region/account layer restrictions.
- **Models:** Updated default action models to the 2026 generation (`gemini-3.7-flash` and `gemini-3.7-pro`) to resolve model deprecation 404 errors.

## [v1.0.3] - 2026-08-22
### Fixed
- **GitHub API:** Added `per_page=100` to the `fetch_pr_files` function to prevent missing critical files in large PRs due to GitHub API default pagination limits.

## [v1.0.2] - 2026-08-22
### Fixed
- **Security:** Added `author_association` checks (`OWNER`, `MEMBER`, `COLLABORATOR`) to prevent prompt injection and cost-based DoS from untrusted external PRs.
- **Security:** Modified webhook `verify_signature` logic to be "fail-closed" (rejecting requests with missing secrets).
- **Stability:** Hardened JSON regex extraction in the review pipeline to ensure raw JSON is stripped from comments even on parse failure.
- **Routing:** Updated the Agentic Router to properly inspect PR file paths for critical directories (`auth/`, `payment/`, etc.) instead of just relying on event type.

## [v1.0.1] - 2026-08-22
### Fixed
- **Encoding:** Fixed UTF-16 null byte corruption (Mojibake) across all Python source files (converted to UTF-8).

## [v1.0.0] - 2026-08-22
### Added
- **Initial Release:** Core webhook listener, basic AI routing logic (`src/router.py`), diff analysis, and custom rules injection via `.reviewforge.md`.
