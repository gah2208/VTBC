# Copilot Instructions for the VTBC Repository

These are standing rules for any AI agent working in this repository. They are
loaded automatically at the start of every session so that work continues
consistently and does not "start over" each time.

## Working agreement with the maintainer (@gah2208)

1. **Surgical edits only.**
   - NEVER delete a single line of code, text, or blank line.
   - If a line must be removed, COMMENT IT OUT instead.
   - Never rewrite existing working code for any reason.

2. **Never shorten a file.**
   - When sending a file update, never deliver a file with fewer lines than the
     current version. Files should stay the same length or grow.
   - Example baseline: `auth_manager.py` must remain at least 177 lines.

3. **Per-file change log with every update.**
   - With every file update, include a change log that documents:
     - the problem being solved,
     - the specific change made,
     - the relevant code snippet(s).

4. **Do not push directly to GitHub.**
   - The agent must not push files or open/update PRs directly.
   - The maintainer reviews each file, confirms the changes, updates their own
     copy of the code, and pushes to GitHub themselves.

## How to keep context between sessions

- Standing rules belong in this file so they are always reloaded.
- Durable, general preferences are also saved to Copilot Memory.
- Manage saved memories here:
  - Personal: https://github.com/settings/copilot/memory
  - Repository: Settings > Copilot > Memory
- Docs: https://docs.github.com/en/copilot/how-tos/use-copilot-agents/copilot-memory