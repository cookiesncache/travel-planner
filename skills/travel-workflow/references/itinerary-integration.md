# Itinerary Integration

## Structure

Organize the plan by day. For each day include:
- Date and location
- Transport legs (departures, arrivals, transfers)
- Accommodation (both check-in and check-out dates)
- Activities and bookings with times where known
- Any relevant notes (e.g. confirmation numbers, addresses)

## Bookings

The plan holds booking **identity** here — no amounts. This is the dedup anchor (email confirmations match its `Confirmation #` column), the Stop hook's check target, and what the agents read. The money — amounts, totals, budget — lives in the standalone spending file (see `## Spending` below and `spending-integration.md`).

Whenever a booking is captured to the plan (from email, user input, or a connector), add a row. Adding the row is part of the same plan write that captured the booking — it carries the same authorization, so no separate confirmation is needed beyond what already approved capturing the booking. The same write also adds the booking's spending-file row and its Sync State row.

**Do not add a row for a booking that was not captured as confirmed** — e.g. a payment-rejected or declined confirmation (see `email-integration.md`). Those are flagged "needs attention" and never appear in Bookings or the spending file.

Format:

```markdown
## Bookings

| ID | Item | Confirmation # | Payment status |
|---|---|---|---|
| tyo-bk1 | Tokyo flight (JAL 123) | ABC123 | prepaid |
| tyo-bk2 | Hotel Shinjuku (3 nights) | XYZ789 | due-on-arrival |
| tyo-bk3 | Sushi-making class | DEF456 | due-on-arrival |
```

(An unpriced booking like `tyo-bk3` — confirmed but no amount yet — still gets a row here; its Amount stays blank in the spending file until known.) The ID column uses the same item IDs as the plan body, the Sync State ledger (see `sync-protocol.md`), and the spending file (column A) — a three-way join. Bookings is the identity view, Sync State is the sync view, the spending file is the money view, all joined by ID.

## Spending

A standalone spreadsheet — `<dest>-spending.xlsx`, generated with live formulas — owns the money. The plan keeps only a **one-line summary + pointer** here, never an editable money table. See `spending-integration.md` for the schema, generation, and recalc-validation.

Format:

```markdown
## Spending

Total spent **$1,050** of **$3,000** budget · **$1,950** remaining · **$600** still due in person.
Full breakdown with live formulas: `tokyo-spending.xlsx`.
*(1 unpriced booking not yet in the total.)*
```

- The summary is a **read-only echo** of the recalculated spending file — refresh it after every change; never hand-edit it to disagree with the file.
- **Amount unknown** (not in the confirmation, or imported from a connector that carries no price) — the spending file leaves that Amount blank (excluded from the total, never counted as $0); append the "N unpriced bookings" note here so Remaining is never silently wrong.
- **No budget set** (from intake, Step 1) — omit the budget and remaining figures until one is established.

## Spending in deliverables

Do not embed an independently-editable money table in any itinerary deliverable (exported doc, Word file, PDF, shared note) — it is instantly a second copy with nothing keeping it in sync, the same drift that hit the task checklist. Reference the spending file instead — e.g. *"Full spending breakdown: `tokyo-spending.xlsx`."* If the user explicitly wants a printable budget, render a clearly-labeled point-in-time snapshot (the `<dest>-spending.csv` export in `spending-integration.md`) — *"Spending snapshot — [date]. Live figures in `tokyo-spending.xlsx`."* — regenerated on demand, never hand-edited.

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
