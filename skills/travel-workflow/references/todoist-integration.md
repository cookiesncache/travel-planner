# Todoist Integration

This reference covers how to apply the travel workflow when the user has Todoist connected.

## Discovery

Use `get-overview` on the travel project to retrieve all existing tasks and sections.

## Identify Trip Type

Before gap analysis, determine the trip type from existing tasks (e.g. "rental car" → road trip, "passport" → international). If unclear, ask the user.

## Gap Analysis

Map each existing task to one of the 5 phases. Then identify which phases have no coverage. Present gaps grouped by phase — don't just list missing tasks, explain why each matters in the context of their specific trip type.

Example output format:

> **Phase 1 – Define** — No budget set yet. Suggest: "Set total trip budget".
>
> **Phase 2 – Preparation** — Lodging booked ✅. Missing for international trip: passport validity check, travel insurance, visa research.

## Suggesting Tasks

Always present suggestions before creating anything. Group by phase. Let the user pick which to add. Skip suggestions clearly irrelevant to the trip type (e.g. don't suggest "fuel up before remote stretches" for a city break).

## Creating Tasks

When the user confirms, use `add-tasks` with:
- `projectId` of the travel project
- A `dueDate` where the task has a natural deadline
- A short `description` for context where helpful

## Adding Sections

If the project has no sections, offer to add them mirroring the 5 phases. Use timeless names:
- "Define"
- "Preparation"
- "Pre-Departure"
- "The Trip"
- "Follow-up"

Do not embed dates or months in section names.
