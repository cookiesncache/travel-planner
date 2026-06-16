---
name: travel-workflow
description: >
  This skill plans any trip end-to-end using a multi-step workflow. It applies
  when the user says "plan my trip", "help me organize a trip", "travel
  checklist", "what do I need for my vacation", "I'm traveling to X",
  "I'm going to X", "I'm heading to X", "planning a trip to X",
  "I have a trip coming up", "book a trip", "plan my vacation", "plan my
  holiday", "planning a weekend away", "we're taking a getaway to X",
  or asks to review or add tasks to an existing trip plan, update a travel
  plan, check what's still missing for a trip, or says "what's left for
  my trip" or "I'm back, let's wrap up my trip".
---

# Travel Workflow

Guide the user through planning their trip using the multi-step workflow below.

## The Travel Plan

After intake, **always generate a baseline travel plan** — a structured artifact containing the day-by-day itinerary, key dates, and tasks. The plan exists regardless of which tools are connected and is the **single source of truth** for the trip. Everything in the workflow reads from and writes to the plan.

Connected tools are **bidirectional sync targets**, never the source of truth:
- **Import** (connector → plan): surface anything in a connected tool but missing from the plan; add it to the plan once confirmed.
- **Export** (plan → connector): push plan data out to the relevant connected tool.

**Two confirmation gates apply to changes Claude initiates** — gate 1: confirm before updating the travel plan; gate 2: confirm before exporting plan data to any connector. When the user directs an action, act on it directly — do not re-confirm what was just instructed. The canonical gate definitions, the plan's **Sync State** ledger, the item ID scheme, and all recording rules live in `references/sync-protocol.md` — read it before any import or export.

One plugin hook (a **sync-back check**) blocks ending a turn until connector writes are recorded in Sync State. **Gate 2 is confirmed in the main thread**: before any connector write, present a native `AskUserQuestion` naming exactly what will be created and in which app, and export only what the user approves (one prompt per batch). If the sync-back hook blocks, record the writes in Sync State and finish.

## Capabilities

See `references/capabilities.md` for all available tools and session capabilities. All tool use is conditional on availability — never hard-stop because a tool is missing. When a capability is missing, mention the connect-to-save benefit **once**, then drop it.

---

## Step 1 — Intake

Before asking the user anything — and again whenever they ask to update their trip status — load context from all connected tools. Use what you find, along with the conversation, to determine whether this is a returning or first-time user. A returning user is one who has previously run this workflow for this trip in a prior session — a travel plan already exists. Anything said in the current conversation does not count as prior invocation. A first-time user has not previously run the workflow for this trip.

### Returning user (travel plan already exists)

Reconcile the travel plan:

1. **Resolve ambiguity first.** Read `.claude/travel-planner.local.md` if it exists — its `trips` list names every known trip and its plan file, with `active_trip` as the default (see `references/sync-protocol.md`). If the request could match more than one trip, ask which they mean. If the state file is missing, scan the project directory for `*-itinerary.md` plan files before concluding there's nothing. Only if none is found anywhere, surface this explicitly and ask whether to start fresh.
2. **Reconcile against connectors and email — both directions, then propose.**
   - **Additive (new/changed in email):** run the read-only `booking-intel` agent to scan email; it returns `missing` confirmations, `flagged` items, and `cancelled`/changed items, already cross-referenced against the plan (email confirmations deduped by confirmation number against the plan's Bookings / Spending Tracker; `declined`/`untracked`/`cancelled`/`orphaned` items skipped). See `references/email-integration.md` for how to handle each.
   - **Subtractive (gone from connectors):** read each connected tool and diff it against `## Sync State`. Only treat a `synced` row as `orphaned` when the read is **conclusive** — a direct fetch of its remote ID returns not-found, or a complete/unfiltered listing omits it; a partial/scoped read, a tool error, or a task merely filtered out because it's closed is **not** an orphan. A task completed in the app is a status change, not an orphan — fetch completed tasks too. Also re-offer cleanup for any row marked `cleanup pending` (a prior cleanup that was denied or failed), and set a `synced` row `stale` if the remote item's key fields no longer match the plan body. (This reconciliation stays in the main thread — see `references/sync-protocol.md`.)
   - **Propose, don't apply:** present everything — additions (from `missing`), removals/flags (from `cancelled`/`orphaned`), status changes — and get the user's confirmation before writing (gate 1). Then apply per `sync-protocol.md` (re-status rows; connector cleanup after gate-2 confirmation). The plan is the deduplication anchor; never re-surface a handled item as new — but a *new* confirmation number for the same vendor + dates of a `cancelled`/`orphaned` item is a re-booking, so surface it.
3. **Confirm the baseline.** Present the plan to the user and get explicit confirmation before proceeding — do not begin writing until the user approves.
4. **Route by trip dates:**
   - Trip is in the future → run the full workflow (Steps 2–6)
   - Trip is in progress → Steps 2, then 4–6 (scoped to The Trip tasks); skip the feasibility check (Step 3) — the trip is already underway
   - Trip has fully passed → Steps 5 and 6, scoped to the Follow-up checklist (deadline-bound follow-ups — insurance-claim windows, equipment returns — still get reminders); when Follow-up wraps up, set that trip's `status: done` in the state file

Only ask about what genuinely can't be inferred. Summarize what you found, then proceed with Steps 2–6 only where an update is needed:

> "Looks like you're flying to Tokyo in September — solo trip, flights and hotel already in your plan. Found a new tour confirmation in your email that's not captured yet. Want me to add it and check what else is still ahead?"

### First-time user (no travel plan yet)

If email is connected, run the read-only `booking-intel` agent to surface booking confirmations matching the trip (and any cancellations) before generating the baseline plan; present anything not yet captured for the user to confirm. There's no plan or Sync State yet, so a `cancelled` finding just means **don't add that as a booking** — and if a `missing` confirmation for the same vendor/dates is also surfaced, treat it as cancelled (don't add it), seeding a `cancelled` row when the plan is created in Step 2. As soon as the destination is known, write the state file (see `references/sync-protocol.md`) so the trip is discoverable. If the user declines any surfaced booking *before* the plan file exists, remember it and record its `declined` row when the plan is created in Step 2 — otherwise it re-surfaces next session.

Gather intake, then generate the baseline travel plan. Only ask for what can't be inferred from connected tools or the conversation:
- **Destination and dates** — infer from the user's message if possible
- **Trip type** — infer from destination and transport (e.g. "driving to the coast" → road trip, "flying to Tokyo" → international)
- **Who's traveling** — solo, couple, group, family with kids (and ages if relevant)
- **Pets** — coming along or staying home
- **Budget** — the total trip budget, if the user has one in mind. Feeds the Spending Tracker's budget and remaining figures. If they don't have one, leave it unset (the tracker omits those rows until a budget is established).
- **What's already booked** — use any context already loaded from connected tools; ask only for what isn't already known. Capture as free text (e.g. "flights booked, hotel sorted, nothing else yet")

Generate the plan from what you gathered and confirm it with the user before proceeding.

**Take their word for it.** If they say something is done, treat it as done and focus on what's still ahead.

---

## Step 2 — Itinerary

Build out the plan's day-by-day content from what was gathered in Step 1, confirming updates before writing them.

**Always generate a named markdown file** for the plan (e.g. `tokyo-itinerary.md`) — even when a connected itinerary app is present. Include a Spending Tracker section; populate it automatically whenever a booking is confirmed, and recalculate the running total and remaining budget. Use lowercase, hyphens for spaces, strip special characters; for multiple destinations use the first or primary. For returning users, update the existing file in place — do not regenerate from scratch.

Every plan file ends with a `## Sync State` section, and every item carries an inline ID (see `references/sync-protocol.md`). When the plan file is created, seed `## Sync State` with a `declined` row for anything the user declined during intake. Ensure `.claude/travel-planner.local.md` lists this trip in its `trips` list with `active_trip` pointing at it — append, don't overwrite other trips — so future sessions can find the plan.

If an itinerary app is connected, offer to export the plan there in addition to the markdown file (confirm before exporting).

See `references/itinerary-integration.md` for guidance, including the fallback if the prior markdown file cannot be located.

---

## Step 3 — Feasibility

**Run this before any scheduling, task sync, or reminders — and before the user books anything.** It gates Steps 4–6: do not export to a calendar, sync tasks, or set reminders until the itinerary's pacing has been checked and the user has rebalanced or accepted the trade-offs. Verifying now, while rebalancing nights and base towns is still cheap, is the whole point — once bookings are confirmed the fixes are gone.

Run automatically for any trip with inter-stop travel — road trips, and multi-destination trips by car, flight, train, or ferry; offer it (lighter) for single-base city breaks. Skip only when the trip is already in progress or has passed — pacing is moot then. Use the `feasibility-check` agent: give it the plan file and trip context; it returns travel-time and pacing findings (door-to-door, by mode) with confidence and sources. Present them grouped by day and let the user rebalance (move a night, change a base town, reorder stops, swap a leg's mode) or accept the trade-offs before proceeding.

See `references/feasibility-integration.md` for full guidance.

---

## Step 4 — Schedule

Export the plan's dated items to a connected calendar, and import existing trip events back into the plan. Gates and Sync State recording per `references/sync-protocol.md`. If dates aren't known yet, skip and offer to revisit once the plan has dates set.

See `references/calendar-integration.md` for full guidance.

---

## Step 5 — Tasks

If a task app is connected, import tasks from it — for returning users this includes syncing status changes for tasks already in the plan. For first-time users, task context was already loaded in Step 1. Then identify what's still ahead and not yet captured. Cross-reference the plan's tasks against:
- What the user said is already done — exclude anything they've confirmed complete
- `references/task-checklist.md` — surface genuine gaps only; for post-trip sessions scope to the Follow-up category only

Present gaps grouped by category from `references/task-checklist.md`. Only suggest tasks for things not done in reality AND not yet in the plan. Add confirmed tasks to the plan. If a task app is connected, keep the plan and task app in sync: export plan tasks to the app and import any app tasks not yet in the plan — gates and Sync State recording per `references/sync-protocol.md`.

See `references/task-integration.md` for guidance.

---

## Step 6 — Reminders

With the full task list settled, offer to set reminders for outstanding time-sensitive tasks. For trips in the future or in progress, scope to tasks still ahead (e.g. upcoming check-ins, outstanding bookings) — not pre-departure prep that has already passed. For trips that have fully passed, scope to deadline-bound Follow-up tasks (e.g. insurance-claim windows, equipment-return dates). If more than one reminder capability is connected, ask the user which to use — don't choose for them; if only one is available, use it; if none, note it in the plan. See `references/reminder-integration.md`. Confirm the reminders before setting them — present them in **one native `AskUserQuestion`** and set only what the user selects, making explicit what will be created and in which app (gate 2 — see `references/sync-protocol.md`); record reminders set in a connected app in Sync State, and note in-session scheduled-task reminders in the plan body instead (see `references/reminder-integration.md`).

If no dates are set yet, skip and offer to revisit once the plan has dates.

See `references/reminder-integration.md` for reminder guidance.

---

## Trip Types

Use the trip type (inferred or confirmed in intake) to scope which checklist items are relevant:

- **Road trip** — driving, route planning, vehicle logistics; skip flight-related items
- **Domestic flight** — flights, no passport or visa needed
- **International** — full admin checklist: passport, visa, insurance, currency, health requirements
- **City break** — short stay, lighter logistics; skip most admin unless international
- **Multi-destination** — multiple transport legs, higher risk of lodging gaps between stops

---

## Traveler Context

Use who's traveling and pet situation to scope suggestions:

**Solo:**
- Add: share itinerary with a contact at home, set up a regular check-in schedule with them
- Skip: group coordination tasks

**Couple:**
- Add: dining reservations for destinations known for competitive bookings (major food cities, peak season)

**Group:**
- Add: shared itinerary distribution, group transport coordination, cost-splitting plan
- Flag: lodging that accommodates the full group

**Family with kids:**
- Add: child-specific packing (medications, snacks, entertainment), car seat if renting, kid-friendly activity research, conservative daily pacing
- Add (international): travel documents and consent letters for minors, entry requirements for children
- Flag: lodging suitability for kids, flight seat arrangements

**Pets — staying home:**
- Add: pet care arrangements (sitter, kennel, trusted contact), feeding and emergency vet instructions
- Note: surface pet care explicitly — do not bury it in generic "home care" tasks

**Pets — coming along:**
- Surface pet-specific tasks from `references/task-checklist.md` across Preparation and Pre-Departure

