# Long-Term Memory

## Network Monitoring
- **Speedtest Configuration:** Implemented `run_speedtest.py` with custom server selection to prioritize Lebanese ISPs (Antelias, Kaslik, Beirut, etc.) over Israeli servers, resolving previous upload speed discrepancies.
- **CLI Strategy:** Prioritized official Ookla `speedtest` CLI for accuracy, with `speedtest-cli` and `librespeed-cli` as fallbacks for blockages/failures.
- **Automation:** Integrated monitoring scripts into Telegram and cron jobs for continuous performance tracking.

## Company-Wide Implementation
- **Project Scope:** This is a research project to implement OpenClaw infrastructure across all departments of your company.
- **API Management:** Integrated and configured multiple APIs for streamlined data processing and efficient token management.

## Operational Habits
- **Resource Management:** Adopted a policy of using isolated sub-agents (`--mode run`) for throwaway tasks (like quick weather checks or URL summaries) to minimize token consumption and keep the main session context clean.
- **Session Hygiene:** Agreed to periodic session resets to keep token usage efficient, with distilled learnings captured here in `MEMORY.md` first.