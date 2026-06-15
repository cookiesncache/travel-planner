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

- **Export gate** (PreToolUse) — for a connector write during an active trip it returns `ask`, so the harness surfaces a native approve/deny prompt; that prompt *is* the gate-2 confirmation. It does not try to read the conversation for prior approval — a prompt hook can't see it reliably (see P0-5 in the ROADMAP).
- **Sync-back check** (Stop) — blocks ending the turn while connector writes or approved imports are not yet recorded in the plan file's ## Sync State. It is also the sole enforcer of sync-debt (recording earlier writes before finishing).

How to cooperate:

- Gate `ask` → tell the user exactly what you'll create or change and in which app; they approve or decline at the prompt. Once it succeeds, record the result in Sync State.
- Sync-back block → record the writes in Sync State (and update the plan body / Spending Tracker), then finish.

Never work around a hook by switching tools. The hooks only see MCP tool calls, so writes made another way — controlling an app's screen, a browser, or a shell — are not mechanically gated; the gate-2 confirm-first rule still applies to them in full, by prose.

**Connector writes happen in the main thread only.** Subagents are read-only with respect to connectors: they read the plan, search, and report, but never call a connector write tool — the main thread performs every export and records it. This is deliberate — both hooks operate on the main agent's turn, so a connector write made inside a subagent would bypass the gate and the sync-back check. A discovery agent that surfaces bookings or tasks (e.g. `booking-intel`) returns them as data; the main thread does the writing and the recording.

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
- **Status** is one of: `synced` (plan and connector agree) · `pending` (approved but not yet exported — or an export that was deferred or failed before returning a remote ID) · `stale` (remote change detected, not yet reconciled into the plan body) · `declined` (user rejected the item — never re-surface or export) · `untracked` (item lives in a connector but the user declined recording it in the plan — kept only so reconciliation won't re-surface it) · `needs-attention` (problem item, e.g. payment rejected — see `email-integration.md`) · `cancelled` (the booking/item was cancelled at the source — a cancellation email or a user cancellation; no longer happening) · `orphaned` (a once-`synced` row whose remote item no longer exists in its connector — detected during reconcile; surface to the user, don't assume).

## Item IDs

`<tripcode>-<type><n>` — e.g. `tyo-bk1`, `tyo-tk3`, `tyo-rm1`. The trip code is a short lowercase slug chosen when the plan is created and recorded in the state file. Types: `bk` (bookings and itinerary items, including the trip calendar block), `tk` (tasks), `rm` (reminders). IDs are assigned when an item first enters the plan and are never reused or renumbered. Stamp the ID inline next to the item in the plan body (e.g. ``09:00 Flight JAL 123 `tyo-bk1` ``) so body and ledger stay joinable.

## Recording rules

- **Export:** after the connector call(s), add or update one row per item per connector with the remote ID the connector returned, Last action `exported <date>`, Status `synced`. An export is not complete until its row exists — this is the invariant the sync-back hook checks.
- **Pending (deferred or failed export):** if the user approves an export but it is deferred ("push it once the dates firm up") or a connector call fails before returning a remote ID, write the row now with Remote ID `—`, Last action `confirmed for export <date>` (or `export failed <date>`), Status `pending`. When the export later succeeds, update the same row to the returned remote ID, Last action `exported <date>`, Status `synced`. A `pending` row does **not** authorize a silent export later: one carried over from a previous session must be re-confirmed with the user before the call, since the export gate cannot see a past session's approval.
- **Batches:** one user approval covers the whole batch it describes; one Sync State update after the batch is correct — do not interleave a plan write between every call.
- **Import:** assign a new ID, add the item to the plan body, add a row with the source connector and remote ID, Last action `imported <date>`, Status `synced`.
- **Status change** (completion pushed or pulled, remote edit reconciled): update Last action; Status stays `synced`. If a remote change is detected but not yet reconciled into the plan body, set `stale` until it is.
- **Decline:** when the user says no to a surfaced booking or task, add a row with Last action `declined by user <date>`, Status `declined`. **Record the source Connector and Remote ID if the item came from a connector** (a declined Todoist task or calendar event keeps its app name and remote ID) — that ID is the suppression key. Use Connector/Remote ID `—` only for email- or user-surfaced items that have no remote ID. If a decline happens during first-time intake **before the plan file exists**, remember it and write its declined row when the plan file is created (Step 2). Before surfacing anything from email or a connector, check Sync State: a declined row suppresses it permanently unless the user asks.
- **Recording declined (untracked):** if the user accepts an item in a connector but declines having it recorded in the plan ("don't bother tracking that here"), still add a minimal row — item, connector, remote ID, Last action `not tracked per user <date>`, Status `untracked` — with no Spending Tracker row and no day-by-day detail. This honors the request (no itinerary clutter, no spend row) while giving reconciliation the remote ID it needs so the item isn't re-surfaced as new next session.
- **Reminders:** a reminder set in a connected app (calendar alert or task-app due-date) gets an `rm` Sync State row like any export. A reminder set via the in-session scheduled-task capability is **not** a connector item — note it in the plan body, not the ledger.
- **Cancellation & orphan (subtractive reconcile):** reconciliation runs in the **main thread**, not an agent. (a) When the `booking-intel` agent reports a `cancelled` item — or the user cancels one — set its row to Status `cancelled` and update Last action. (b) During Step 1 reconcile, check whether each `synced` row's remote item still exists in its connector — but **only treat it as `orphaned` when the check is conclusive**: a direct fetch of that remote ID returns not-found, or a *complete, unfiltered* listing of the scope it lives in omits it. A partial / scoped / paginated / date-windowed read, a tool error, multiple calendars, or a task merely filtered out because it's closed is **not** evidence of deletion — never orphan on it (fetch completed tasks before judging a task row — see `task-integration.md`). In both cases **surface the change and get the user's confirmation before editing the plan body** (gate 1): remove or flag the item, recalculate the Spending Tracker, and make any connector cleanup (deleting a leftover calendar event, closing a task) through the export gate (`ask`). If that cleanup is approved but the `ask` is denied or the call fails, keep the row and set Last action `cleanup pending <date>` so the leftover remote item is re-offered next session (parallels the **Pending** rule) — don't leave plan and connector divergent silently. Never drop a row — re-status it (rows are never deleted).
- **Dedup on import — match the right identifier.** A **connector** item (calendar event, task) carries a remote ID, so an item whose remote ID already appears in Sync State is already handled. An **email** confirmation has a *confirmation number*, not a remote ID — Sync State's Remote ID column holds connector IDs, a different identifier space — so match its confirmation number against the plan's **Bookings / Spending Tracker** (`Confirmation #`), not the Remote ID column. Either way: if the match is a `declined`, `untracked`, `cancelled`, or `orphaned` row/item, suppress it (do not re-surface as new); otherwise reconcile its status. Do not re-surface a handled item.

## Spending Tracker interaction

The Spending Tracker's first column is the item ID, joined to Sync State (see `itinerary-integration.md` for the format). Capturing a confirmed booking writes plan body, tracker row, and Sync State row in one authorized write. Declined, untracked, and needs-attention items never get tracker rows. When an item becomes `cancelled` or `orphaned`, remove its tracker row and recalculate the total — you're no longer paying for it (unless a non-refundable charge stands, which the user can note).

## The state file

`.claude/travel-planner.local.md` in the project directory marks travel planning active and locates the plan across sessions:

```markdown
---
plugin: travel-planner
active_trip: tokyo-2026-09
trips:
  - id: tokyo-2026-09
    trip_code: tyo
    plan_file: tokyo-itinerary.md
    status: planning      # planning | in-trip | done
    connectors:
      calendar: Google Calendar
      tasks: Todoist
  - id: lisbon-2026-07
    trip_code: lis
    plan_file: lisbon-itinerary.md
    status: done
    connectors:
      calendar: Google Calendar
updated: 2026-06-13
---
```

- **Write it** (ordinary Write tool) as soon as a trip is identified in intake — at the latest when the plan file is created. **Update it** when a plan filename, trip status, or connector choice changes; set a trip's `status: done` when its Follow-up wraps up. Record the user's app choice under that trip's `connectors` when they pick one — that name is what Sync State's Connector column uses.
- **One entry per trip — never overwrite or delete entries.** Starting a new trip *appends* a new entry and repoints `active_trip`; it does not replace the previous trip, whose entry stays so its plan file remains discoverable. `active_trip` is the trip the current session is working on, and the default when the user doesn't say which.
- **It doubles as the returning-user pointer:** Step 1 reads the `trips` list to find each trip's plan file instead of guessing.
- Users should gitignore `*.local.md` (README note).

## After compaction

If context was compacted or history looks truncated, re-read the state file and the plan file **before any connector write**. Sync State on disk outranks your memory of the session: recorded remote IDs prevent duplicate re-exports, and missing confirmations must be re-asked, not assumed.
