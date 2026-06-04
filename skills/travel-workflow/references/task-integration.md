# Task App Integration

Tasks always live in the travel plan (the source of truth) — with or without a connected task app. If a task app is connected, keep the plan and task app in sync: export plan tasks to the app, import any app tasks not yet in the plan. Confirm Claude-initiated plan updates (gate 1) and exports to the task app (gate 2) with the user unless they directed the action. If no task app is connected, tasks stay in the plan only.

## Finding the Right App

Check whether a task management tool is connected before proceeding with any sync operations. If none is connected, task work stays in the plan only — skip the rest of this file.

Identify which task management tool is connected. Common options: Todoist, Things, Apple Reminders, Asana, TickTick. Use whichever is available. If multiple are connected, ask the user which they'd like to use for this trip.

## Finding or Creating the Travel Project

Search for an existing project matching the trip (by destination name, "trip", "travel", or similar). If none exists, offer to create one named after the destination or trip.

## Auditing Tasks

Start from the plan's tasks as the source of truth. Cross-reference against the connected task app to pick up any tasks that exist there but aren't yet in the plan — add those to the plan first, preserving their completion status (completed tasks are added as closed, not open). Then map all tasks against `task-checklist.md`, identify which categories have no coverage, and present gaps clearly grouped by category. Explain why each gap matters in the context of the specific trip type — don't just list missing tasks.

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

## Adding Sections

If the project has no sections, offer to add them using the category names from `task-checklist.md` (Define, Preparation, Pre-Departure, The Trip, Follow-up). Do not embed dates or months in section names.

## Using the Connected App

Use whichever tools the connected task app exposes. Typical patterns:
- **Retrieve tasks:** use the app's project overview or task list tool, scoped to the travel project
- **Create tasks:** use the app's task creation tool with the project ID, a due date where relevant, and a brief description for context
- **Complete tasks:** use the app's task completion or status-update tool when the plan marks an item done
