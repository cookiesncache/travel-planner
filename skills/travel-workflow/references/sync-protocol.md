# Sync Protocol

Canonical reference for keeping the travel plan (the source of truth) and connectors in sync. The workflow steps and integration references point here; the rules live here and nowhere else.

## The Two Confirmation Gates

Both gates apply to changes **Claude initiates**. When the user directs an action, act on it directly — do not re-confirm what was just instructed.

- **Gate 1 — plan writes.** Confirm before updating the travel plan, including data imported from connected tools or email.
- **Gate 2 — connector exports.** Confirm before exporting plan data to any connector. Make explicit what will be created or changed and in which app.

**Recording exemption (gate 1):** the plan write that records an export carries the authorization of the export it records. After a confirmed export, update Sync State and the affected plan sections immediately — never ask again for that.

Gate 2 and sync-back recording are enforced by plugin hooks (below). Gate 1 is deliberately prose-only: hooking local file edits would run a check on every Write/Edit in every session, travel or not.

## Hooks — how to cooperate

The plugin ships two hooks:

- **Export gate** (PreToolUse) — blocks Claude-initiated connector writes that lack user confirmation, and blocks new connector writes while earlier ones are unrecorded in Sync State.
- **Sync-back check** (Stop) — blocks ending the turn while connector writes or approved imports are not reflected in the plan file.

When a hook blocks you, do what its reason says — then retry:

- Gate-2 deny → present the exact change and app to the user, get their yes, retry the call.
- Sync-back deny/block → record the writes in Sync State (and update the plan body / Spending Tracker), then retry or finish.

Never retry the same call unchanged, and never work around a hook by switching to a different tool.

## Sync State section

Every plan file ends with a `## Sync State` section: one table, one row per (item, connector) pair.

```markdown
## Sync State
<!-- Sync ledger: one row per item-connector pair. Never delete rows; update Status. -->

| ID | Item | Connector | Remote ID | Last action | Status |
|---|---|---|---|---|---|
| tyo-bk1 | Flight JAL 123 (Sep 12) | Google Calendar | evt_8f3k2 | exported 2026-06-10 | synced |
| tyo-tk1 | Apply for visa | Todoist | 7788991122 | imported 2026-06-10 | synced |
| tyo-tk2 | Book airport transfer | Todoist | — | confirmed for export | pending |
| tyo-bk4 | Robot Restaurant tour | — | — | declined by user 2026-06-08 | declined |
| tyo-tk3 | Buy JR Pass | Todoist | 7788991155 | declined by user 2026-06-09 | declined |
```

(`tyo-bk4` was surfaced from email, so it has no remote ID; `tyo-tk3` was surfaced from Todoist, so its app name and remote ID are kept — that ID is what suppresses it next session.)

- **Connector** is the human app name (Google Calendar, Todoist) — never the `mcp__<server>__` segment of a tool name; server names can be opaque and session-specific.
- **Status** is one of: `synced` (plan and connector agree) · `pending` (confirmed in the plan, not yet exported) · `stale` (remote change detected, not yet reconciled into the plan body) · `declined` (user said no — never re-surface or export) · `needs-attention` (problem item, e.g. payment rejected — see `email-integration.md`).

## Item IDs

`<tripcode>-<type><n>` — e.g. `tyo-bk1`, `tyo-tk3`, `tyo-rm1`. The trip code is a short lowercase slug chosen when the plan is created and recorded in the state file. Types: `bk` (bookings and itinerary items, including the trip calendar block), `tk` (tasks), `rm` (reminders). IDs are assigned when an item first enters the plan and are never reused or renumbered. Stamp the ID inline next to the item in the plan body (e.g. ``09:00 Flight JAL 123 `tyo-bk1` ``) so body and ledger stay joinable.

## Recording rules

- **Export:** after the connector call(s), add or update one row per item per connector with the remote ID the connector returned, Last action `exported <date>`, Status `synced`. An export is not complete until its row exists — this is the invariant the sync-back hook checks.
- **Batches:** one user approval covers the whole batch it describes; one Sync State update after the batch is correct — do not interleave a plan write between every call.
- **Import:** assign a new ID, add the item to the plan body, add a row with the source connector and remote ID, Last action `imported <date>`, Status `synced`.
- **Status change** (completion pushed or pulled, remote edit reconciled): update Last action; Status stays `synced`. If a remote change is detected but not yet reconciled into the plan body, set `stale` until it is.
- **Decline:** when the user says no to a surfaced booking or task, add a row with Last action `declined by user <date>`, Status `declined`. **Record the source Connector and Remote ID if the item came from a connector** (a declined Todoist task or calendar event keeps its app name and remote ID) — that ID is the suppression key. Use Connector/Remote ID `—` only for email- or user-surfaced items that have no remote ID. Before surfacing anything from email or a connector, check Sync State: a declined row suppresses it permanently unless the user asks.
- **Dedup on import:** an item whose remote ID already appears in Sync State is already handled — if the matching row is `declined`, suppress it (do not re-surface); otherwise reconcile its status. Do not re-surface it.

## Spending Tracker interaction

The Spending Tracker's first column is the item ID, joined to Sync State (see `itinerary-integration.md` for the format). Capturing a confirmed booking writes plan body, tracker row, and Sync State row in one authorized write. Declined and needs-attention items never get tracker rows.

## The state file

`.claude/travel-planner.local.md` in the project directory marks travel planning active and locates the plan across sessions:

```markdown
---
plugin: travel-planner
active_trip: tokyo-2026-09
trip_code: tyo
plan_file: tokyo-itinerary.md
status: planning   # planning | in-trip | done
connectors:
  calendar: Google Calendar
  tasks: Todoist
updated: 2026-06-10
---
```

- **Write it** (ordinary Write tool) the moment the plan file is created or located in Step 2; **update it** when the plan filename, trip status, or connector choices change; set `status: done` when Follow-up wraps up. Record the user's app choice under `connectors` when they pick one — that name is what Sync State's Connector column uses.
- **Never delete it** — it doubles as the returning-user pointer: Step 1 intake reads it to find the active trip and plan file instead of guessing. Starting a new trip overwrites it.
- Users should gitignore `*.local.md` (README note).

## After compaction

If context was compacted or history looks truncated, re-read the state file and the plan file **before any connector write**. Sync State on disk outranks your memory of the session: recorded remote IDs prevent duplicate re-exports, and missing confirmations must be re-asked, not assumed.
