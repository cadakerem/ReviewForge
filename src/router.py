def route_analysis(event_type: str, payload: dict) -> str:
    """
    Agentic Router Core:
    Determines whether a change requires light or deep analysis.
    Fix #5: Now inspects changed file paths for high-risk directories
    in addition to commit count and PR title keywords.
    """
    # High-risk file path patterns — always trigger deep analysis
    CRITICAL_PATHS = [
        "auth", "security", "payment", "billing", "admin",
        ".github/workflows", "settings", "config", "middleware", "core"
    ]

    def has_critical_files(files: list) -> bool:
        for f in files:
            for path in CRITICAL_PATHS:
                if path in f.lower():
                    return True
        return False

    if event_type == "push":
        commits = payload.get("commits", [])
        print(f"[Router] Analyzing {len(commits)} commit(s)...")

        changed_files = []
        for commit in commits:
            changed_files += commit.get("added", [])
            changed_files += commit.get("modified", [])
            changed_files += commit.get("removed", [])

        if has_critical_files(changed_files):
            print(f"[Router] Decision: DEEP_ANALYSIS (Critical file paths detected: {changed_files})")
            return "DEEP_ANALYSIS"

        if len(commits) > 3:
            print("[Router] Decision: DEEP_ANALYSIS (High commit volume)")
            return "DEEP_ANALYSIS"

        print("[Router] Decision: LIGHT_ANALYSIS (Small change)")
        return "LIGHT_ANALYSIS"

    elif event_type == "pull_request":
        action = payload.get("action")
        pr_data = payload.get("pull_request", {})
        pr_title = pr_data.get("title", "").lower()

        print(f"[Router] PR: '{pr_title}' | Action: {action}")

        # Only analyze open or updated PRs
        if action not in ["opened", "synchronize", "reopened"]:
            return "IGNORED_ACTION"

        # Check PR title for critical keywords
        critical_keywords = ["sec", "auth", "architecture", "refactor", "core", "payment", "admin"]
        if any(keyword in pr_title for keyword in critical_keywords):
            print("[Router] Decision: DEEP_ANALYSIS (Critical keyword in PR title)")
            return "DEEP_ANALYSIS"

        print("[Router] Decision: LIGHT_ANALYSIS (Standard PR)")
        return "LIGHT_ANALYSIS"

    return "UNKNOWN_EVENT"
