<div align="center">
  <h1>🛡️ ReviewForge</h1>
  <p><b>Autonomous SecOps & Code Review AI Agent (Serverless GitHub Action)</b></p>
  <img src="https://img.shields.io/badge/AI_Provider-Gemini_|_OpenAI_|_Groq_|_Nvidia-blue.svg" alt="AI Providers" />
  <img src="https://img.shields.io/badge/Platform-GitHub_Actions-2088FF.svg?logo=github" alt="Platform" />
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License" />
</div>

<br>

**ReviewForge** is not just a passive linter. It is a proactive, AI-driven Security Operations (SecOps) and Code Review engineer that lives directly inside your GitHub workflows. 

Whenever a developer pushes code or opens a Pull Request, ReviewForge analyzes the changes. If it spots a typo, it leaves a polite PR comment. **If it detects a critical security vulnerability or architectural flaw, it autonomously creates a labeled GitHub Issue, links it to your PR, and alerts your team.**

## ✨ Key Features

- 🌍 **Multi-Provider AI:** Out-of-the-box support for Google Gemini, OpenAI, Nvidia NIM, Groq, or any OpenAI-compatible endpoint. No vendor lock-in!
- 🧠 **Agentic Routing:** Smart routing ensures small UI tweaks get a fast, cheap review (e.g., `gemini-3.7-flash`), while complex core changes get deep security analysis (e.g., `gemini-3.7-pro` or `gpt-oss-120b`).
- 🤖 **Autonomous Issue Creation:** When the AI detects a critical bug or security flaw, it automatically opens a GitHub Issue with the correct labels (`bug`, `security`, `architecture`) and cross-references the offending PR.
- 💡 **Auto-Fix Code Blocks:** The AI doesn't just complain; it provides the exact corrected code block so developers can easily copy-paste and solve the issue instantly.
- 🏗️ **Company-Specific Rules (`.reviewforge.md`):** Drop a `.reviewforge.md` file in your repository root to teach the AI your specific coding standards (e.g., "Always use strict typing", "Never use raw SQL").
- ⚡ **Serverless:** Runs entirely on GitHub Actions. Zero servers to maintain. Zero webhook configs. Zero hosting costs.

## 🚀 Quick Setup (GitHub Actions)

Add ReviewForge to any repository in **under 30 seconds**. 

Create a workflow file in your repo at `.github/workflows/reviewforge.yml`:

```yaml
name: ReviewForge SecOps
on: [pull_request, push]

jobs:
  ai_review:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
      issues: write
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4
      
      - name: Run ReviewForge AI
        uses: cadakerem/ReviewForge@v1
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          ai_provider: "gemini" 
          ai_api_key: ${{ secrets.GEMINI_API_KEY }}
          # Optional Configuration (Defaults shown below)
          # light_model: "gemini-3.7-flash"
          # deep_model: "gemini-3.7-pro"
          # auto_create_issues: "true"
```

> **Note:** Don't forget to add your `GEMINI_API_KEY` (or OpenAI/Groq key) to your repository's [GitHub Secrets](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions).

## ⚙️ Configuration Options

| Input | Description | Default | Required |
| --- | --- | --- | --- |
| `github_token` | GitHub token for posting comments/issues. | `${{ github.token }}` | Yes |
| `ai_provider` | `gemini`, `openai`, `nvidia`, `groq` | `gemini` | Yes |
| `ai_api_key` | Your AI provider's API Key. | - | Yes |
| `light_model` | Faster model used for standard changes. | `gemini-3.7-flash` | No |
| `deep_model` | Advanced model used for complex/security PRs. | `gemini-3.7-pro` | No |
| `auto_create_issues` | Automatically create GitHub issues for critical vulnerabilities. | `true` | No |

## 🛡️ How the Autonomous Issue Creator Works

ReviewForge's AI engine is instructed to output a specific JSON payload if a change is highly destructive (e.g., SQL Injection, unauthenticated endpoint). 

When the underlying Python engine detects this JSON output from the AI, it intercepts it, creates a formal GitHub Issue tagged with `bug` or `security`, and then leaves a warning comment on the developer's PR linking to the newly created issue ticket.

## 🤝 Contributing

Contributions, issues, and feature requests are always welcome! Feel free to check the issues page.

## 📜 License

This project is licensed under the [MIT License](LICENSE).
