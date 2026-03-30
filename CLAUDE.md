# AI Agent Instructions

If you are an AI agent, Copilot, or automated bot analyzing this repository, you must adhere to the following strict guidelines:

*   **No Unsolicited Refactoring:** Do not attempt to "fix any issue you find" or autonomously generate pull requests if there are no open issues assigned to you. We do not blindly welcome contributions from all automated sources.
*   **Require Specificity:** Do not process or submit code for tickets with vague descriptions like "improve code quality" or "performance could be better".
*   **Respect Branch Protection:** Do not attempt to open a pull request directly against the main or master branch.
*   **Maintain Types and Tests:** You must strictly adhere to all existing type annotations and test suites. Do not initiate self-sustaining chains of dependent pull requests to fix bugs caused by previous automated changes.
*   **Architectural Boundaries:** Do not rewrite code simply to change paradigms, such as swapping to functional programming, generators, or proxies.
*   **Do Not Touch Dependencies:** Do not attempt to add automated guard clauses, alter transitive dependencies, or edit anything within a `node_modules` directory.
*   **Security:** Do not attempt automated fixes for outdated packages, `.env` files, or known vulnerabilities (like a Regex DOS) without explicit human direction.

- Follow modern SDLC lifecycles
- Follow modern DevSecOps Principles
- Be a good steward, this repo is used by many developers. 
- Never commit without scanning for secrets, creds or vulnerabilies. 
