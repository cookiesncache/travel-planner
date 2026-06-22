# Itinerary Integration

## Structure

Organize the plan by day. For each day include:
- Date and location
- Transport legs (departures, arrivals, transfers)
- Accommodation (both check-in and check-out dates)
- Activities and bookings with times where known
- Any relevant notes (e.g. confirmation numbers, addresses)

## Spending Tracker

Include a **Spending Tracker** section in the plan. Whenever a booking is captured to the plan (from email, user input, or a connector), add a row. Adding the row is part of the same plan write that captured the booking — it carries the same authorization, so no separate confirmation is needed beyond what already approved capturing the booking.

**Do not add a row for a booking that was not captured as confirmed** — e.g. a payment-rejected or declined confirmation (see `email-integration.md`). Those are flagged "needs attention" and never appear in the tracker.

Format:

```markdown
## Spending Tracker

| ID | Item | Amount | Confirmation # |
|---|---|---|---|
| tyo-bk1 | Tokyo flight (JAL 123) | $450 | ABC123 |
| tyo-bk2 | Hotel Shinjuku (3 nights) | $600 | XYZ789 |
| | **Total spent** | **$1,050** | |
| | **Trip budget** | **$3,000** | |
| | **Remaining** | **$1,950** | |
```

The ID column uses the same item IDs as the plan body and the Sync State ledger (see `sync-protocol.md`) — the tracker is the money view, Sync State is the sync view, joined by ID.

- **Amount known** — record it in the row.
- **Amount unknown** (not in the confirmation, or imported from a connector that carries no price) — add the row with the Amount left blank and confirm the amount with the user. Until an amount is provided, exclude that row from the Total (do not count it as $0) and note that unpriced bookings exist, so Remaining is never silently wrong.
- Recalculate Total (sum of known amounts only) and Remaining after every change.
- The Trip budget comes from intake (Step 1). If no budget was set, omit the budget and remaining rows until one is established.

## Syncing to a connected itinerary app

If an itinerary app or notes tool is connected (Wanderlog, Notion, Google Docs, etc.), offer to export the plan there in addition to the markdown file, matching the app's native structure where possible. Import any changes made in the app back into the plan (and update the markdown file accordingly). Gates and Sync State recording: see `sync-protocol.md`. If multiple itinerary apps are connected, ask the user which to sync to and record the choice in the state file.

## Tasks in deliverables

Do not embed an independently-editable task checklist in any itinerary deliverable (exported doc, Word file, PDF, shared note, etc.) when a task connector is connected. An embedded list is immediately a third copy with nothing keeping it in sync — it will drift (confirmed in real use: a dropped task stayed in the docx while seven newer tasks were missing from it, all while Todoist and the plan's `## Tasks` were current).

- **Connector connected:** replace the checklist with a reference — e.g. *"Tasks live in your Todoist [Trip Name] project."* Never duplicate the list.
- **No connector:** an inline task list in the deliverable is acceptable; the plan's `## Tasks` is the only copy, so the deliverable and the source of truth are the same artifact.
- **User explicitly requests a printable checklist:** render it, but label it clearly as a point-in-time snapshot — e.g. *"Task snapshot — [date]. Authoritative list is in [app]."* Regenerate it from the current plan+connector state on demand; never hand-edit it after generation.

---

## Updating

Gate 1 applies to Claude-initiated updates (see `sync-protocol.md`). For returning users, update only what's changed — do not regenerate the full plan unless asked.

If the prior markdown file cannot be located in the current session, check `.claude/travel-planner.local.md` first — each trip entry records its `plan_file` path (see `sync-protocol.md`). Then:

- **State file missing too** — scan the project for a `*-itinerary.md` plan file (per Step 1); if none is found anywhere, ask the user whether to regenerate the plan from context and connected tools, or start the first-time flow from scratch.
- **State file present but its `plan_file` doesn't resolve** (the file was renamed, moved, or deleted) — say so explicitly; do not silently proceed on a dangling pointer or start a duplicate plan. Scan the project for a renamed/moved `*-itinerary.md` that matches the trip and, if one matches, repoint the state file at it. If none matches, ask whether to regenerate from context and connectors — noting that any decline/sync history in the lost file can't be recovered — or to supply the correct file.
