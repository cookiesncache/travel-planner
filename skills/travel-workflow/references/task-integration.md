# Task App Integration

Tasks always live in the travel plan (the source of truth) — with or without a connected task app. If a task app is connected, keep the plan and task app in sync: export plan tasks to the app, import any app tasks not yet in the plan. Gates and Sync State recording: see `sync-protocol.md`. If no task app is connected, tasks stay in the plan only.

## Finding the Right App

Check whether a task management tool is connected before proceeding with any sync operations. If none is connected, task work stays in the plan only — skip the rest of this file.

Identify which task management tool is connected. Common options: Todoist, Things, Apple Reminders, Asana, TickTick. Use whichever is available. If multiple are connected, ask the user which they'd like to use for this trip, and record the choice in the state file (see `sync-protocol.md`).

## Finding or Creating the Travel Project

Search for an existing project matching the trip (by destination name, "trip", "travel", or similar). If multiple match, surface them and ask the user to pick before proceeding. If none exists, offer to create one named after the destination or trip.

## Auditing Tasks

**Step 1 — Import first.** Before auditing, complete the import from the task app into the plan: pull any tasks that exist in the app but aren't yet in the plan, preserving their completion status (completed tasks are added as closed, not open). A task whose remote ID already appears in the plan's Sync State is already imported — only its status may need reconciling. Also sync status changes for tasks already in both places — if a task is open in the plan but completed in the app, update the plan's status to match. Batch all status changes into a single summary and ask for one confirmation before writing (gate 1 — see `sync-protocol.md`); record imports and status changes in Sync State as part of the same write. This must be finished before gap analysis begins.

**Step 2 — Audit.** With the plan now reflecting all known tasks, map them against `task-checklist.md`. For post-trip sessions, scope the audit to the Follow-up category only. Identify which categories have no coverage and present gaps clearly grouped by category. Explain why each gap matters in the context of the specific trip type — don't just list missing tasks.

Example output format:

> **Define** — No budget set yet. Suggest: "Set total trip budget".
>
> **Preparation** — Lodging booked ✅. Missing for international trip: passport validity check, travel insurance, visa research.

## Suggesting and Adding Tasks

Always present suggestions before creating anything. Group by category. Let the user pick which to add. Skip suggestions clearly irrelevant to the trip type.

When the user confirms, create tasks with:
- A clear, action-oriented title
- A due date where the task has a natural deadline
- A brief description for any task that benefits from context

After the batch, record each created task's ID in the plan's Sync State table per `sync-protocol.md`.

## Adding Sections

If the project has no sections, offer to add them using the category names from `task-checklist.md` (Define, Preparation, Pre-Departure, The Trip, Follow-up). Do not embed dates or months in section names.

## Syncing Completions

Completions flow to the task app in two cases:

- **User marks a task complete** during the session (in the plan or conversation) — export that status change to the task app (gate 2 — see `sync-protocol.md`).
- **A confirmed booking fulfills an open task** — when a booking is confirmed and updated in the plan (e.g. a flight confirmation fulfills "Book flights"), ask the user before marking the corresponding task complete in the task app.

Either way, update the task's Sync State row (Last action) in the same step.

In both cases, **actually complete the task — call the app's completion action** (e.g. `complete-tasks` in Todoist). Do not simulate completion by renaming the task, adding a checkmark, or striking through the title. The task must be genuinely closed in the app.

## Using the Connected App

Use whichever tools the connected task app exposes. Typical patterns:
- **Retrieve tasks:** use the app's project overview or task list tool, scoped to the travel project
- **Create tasks:** use the app's task creation tool with the project ID, a due date where relevant, and a brief description for context
- **Complete tasks:** use the app's dedicated completion action (e.g. `complete-tasks`) — never a title edit — when a task is done
