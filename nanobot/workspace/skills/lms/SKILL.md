---
name: lms
description: Use LMS MCP tools for live course data
always: true
---

# LMS Agent Skill

You have access to the LMS backend via MCP tools. Use them to answer questions about labs, learners, scores, and system health.

## Available Tools

- `lms_health` — Check if the LMS backend is healthy and get item count
- `lms_labs` — List all available labs
- `lms_pass_rates` — Get pass rate statistics for a specific lab
- `lms_scores` — Get score distribution for a specific lab
- `lms_learners` — List all learners
- `lms_groups` — Get group performance data
- `lms_timeline` — Get submission timeline for a specific lab
- `lms_top_learners` — Get top performing learners for a specific lab
- `lms_completion_rate` — Get completion rate for a specific lab
- `lms_sync_pipeline` — Trigger the ETL sync pipeline

## Strategy Rules

### When the user asks about labs, scores, pass rates, completion, groups, timeline, or top learners WITHOUT naming a lab:

1. First call `lms_labs` to get the list of available labs
2. Present the lab list to the user and ask them to choose one
3. Use the lab identifier (e.g., `lab-01`, `lab-02`) when calling other tools

Example:
- User: "Show me the scores"
- You: Call `lms_labs`, then say "Which lab would you like to see scores for? Available: lab-01, lab-02, ..."

### When the user asks about system health:

- Call `lms_health` and report the status and item count

### When the user asks about learners:

- Call `lms_learners` for the full list
- Call `lms_groups` for group-level statistics

### Formatting responses:

- Present numeric results clearly (e.g., "Pass rate: 85%", "15 out of 20 learners completed")
- Keep responses concise but informative
- When showing multiple labs, use a numbered list with lab titles

### When you don't know something:

- Say you don't have that information rather than guessing
- Offer to check what data is available using your tools
