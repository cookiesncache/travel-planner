# Task App Integration

## Finding the Right App

Identify which task management tool is connected. Common options: Todoist, Things, Apple Reminders, Asana, TickTick. Use whichever is available. If multiple are connected, ask the user which they'd like to use for this trip.

## Finding or Creating the Travel Project

Search for an existing project matching the trip (by destination name, "trip", "travel", or similar). If none exists, offer to create one named after the destination or trip.

## Identify Trip Type

Before gap analysis, determine the trip type from existing tasks if not already known (e.g. "rental car" → road trip, "passport" → international). If unclear, ask the user.

## Auditing Tasks

Retrieve all tasks from the source of truth. Map each to one of the 5 phases. Identify which phases have no coverage and present gaps clearly, grouped by phase. Explain why each gap matters in the context of the specific trip type — don't just list missing tasks.

Example output format:

> **Phase 1 – Define** — No budget set yet. Suggest: "Set total trip budget".
>
> **Phase 2 – Preparation** — Lodging booked ✅. Missing for international trip: passport validity check, travel insurance, visa research.

## Suggesting and Adding Tasks

Always present suggestions before creating anything. Group by phase. Let the user pick which to add. Skip suggestions clearly irrelevant to the trip type.

When the user confirms, create tasks with:
- A clear, action-oriented title
- A due date where the task has a natural deadline
- A brief description for any task that benefits from context

## Adding Sections

If the project has no sections, offer to add them using these timeless names:
- "Define"
- "Preparation"
- "Pre-Departure"
- "The Trip"
- "Follow-up"

Do not embed dates or months in section names.

## App-specific guidance

If Todoist is connected, see `references/todoist-integration.md` for tool-specific usage. For other apps, use the generic patterns above with whatever tools the app exposes.
