---
name: travel-workflow
description: >
  This skill plans any trip end-to-end using a 5-step workflow. It applies
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

Guide the user through planning their trip using the 5-step workflow below.

## The Travel Plan

After intake, **always generate a baseline travel plan** — a structured artifact containing the day-by-day itinerary, key dates, and tasks. The plan exists regardless of which tools are connected and is the **single source of truth** for the trip. Everything in the workflow reads from and writes to the plan.

Connected tools are **bidirectional sync targets**, never the source of truth:
- **Import** (connector → plan): surface anything in a connected tool but missing from the plan; add it to the plan once confirmed.
- **Export** (plan → connector): push plan data out to the relevant connected tool.

**Two confirmation gates apply to changes Claude initiates** — gate 1: confirm before updating the travel plan; gate 2: confirm before exporting plan data to any connector. When the user directs an action, act on it directly — do not re-confirm what was just instructed. The canonical gate definitions, the plan's **Sync State** ledger, the item ID scheme, and all recording rules live in `references/sync-protocol.md` — read it before any import or export.

Two plugin hooks enforce this protocol: an **export gate** before connector writes and a **sync-back check** before ending a turn. If a hook blocks an action, do what its reason says — confirm with the user or record in Sync State — rather than retrying the same call.

## Capabilities

See `references/capabilities.md` for all available tools and session capabilities. All tool use is conditional on availability — never hard-stop because a tool is missing. When a capability is missing, mention the connect-to-save benefit **once**, then drop it.

---

## Step 1 — Intake

Before asking the user anything — and again whenever they ask to update their trip status — load context from all connected tools. Use what you find, along with the conversation, to determine whether this is a returning or first-time user. A returning user is one who has previously run this workflow for this trip in a prior session — a travel plan already exists. Anything said in the current conversation does not count as prior invocation. A first-time user has not previously run the workflow for this trip.

### Returning user (travel plan already exists)

Reconcile the travel plan:

1. **Resolve ambiguity first.** Read `.claude/travel-planner.local.md` if it exists — its `trips` list names every known trip and its plan file, with `active_trip` as the default (see `references/sync-protocol.md`). If the request could match more than one trip, ask which they mean. If the state file is missing, scan the project directory for `*-itinerary.md` plan files before concluding there's nothing. Only if none is found anywhere, surface this explicitly and ask whether to start fresh.
2. **Reconcile against connectors and email.** Cross-reference findings from all connected tools and email against the plan. Surface a booking or event only if it isn't already in the plan — the plan is the deduplication anchor: match against Sync State remote IDs, and never re-surface anything with a `declined` row. Add surfaced items once confirmed. See `references/email-integration.md` for email-specific guidance.
3. **Confirm the baseline.** Present the plan to the user and get explicit confirmation before proceeding — do not begin writing until the user approves.
4. **Route by trip dates:**
   - Trip is in the future → run the full workflow (Steps 2–5)
   - Trip is in progress → Steps 2, 3, 4 (scoped to The Trip tasks), then Step 5
   - Trip has fully passed → Steps 4 and 5, scoped to the Follow-up checklist (deadline-bound follow-ups — insurance-claim windows, equipment returns — still get reminders); when Follow-up wraps up, set that trip's `status: done` in the state file

Only ask about what genuinely can't be inferred. Summarize what you found, then proceed with Steps 2–5 only where an update is needed:

> "Looks like you're flying to Tokyo in September — solo trip, flights and hotel already in your plan. Found a new tour confirmation in your email that's not captured yet. Want me to add it and check what else is still ahead?"

### First-time user (no travel plan yet)

If email is connected, search for booking confirmations matching the trip and surface anything not yet captured before generating the baseline plan. As soon as the destination is known, write the state file (see `references/sync-protocol.md`) so the trip is discoverable. If the user declines any surfaced booking *before* the plan file exists, remember it and record its `declined` row when the plan is created in Step 2 — otherwise it re-surfaces next session.

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

## Step 3 — Schedule

Export the plan's dated items to a connected calendar, and import existing trip events back into the plan. Gates and Sync State recording per `references/sync-protocol.md`. If dates aren't known yet, skip and offer to revisit once the plan has dates set.

See `references/calendar-integration.md` for full guidance.

---

## Step 4 — Tasks

If a task app is connected, import tasks from it — for returning users this includes syncing status changes for tasks already in the plan. For first-time users, task context was already loaded in Step 1. Then identify what's still ahead and not yet captured. Cross-reference the plan's tasks against:
- What the user said is already done — exclude anything they've confirmed complete
- `references/task-checklist.md` — surface genuine gaps only; for post-trip sessions scope to the Follow-up category only

Present gaps grouped by category from `references/task-checklist.md`. Only suggest tasks for things not done in reality AND not yet in the plan. Add confirmed tasks to the plan. If a task app is connected, keep the plan and task app in sync: export plan tasks to the app and import any app tasks not yet in the plan — gates and Sync State recording per `references/sync-protocol.md`.

See `references/task-integration.md` for guidance.

---

## Step 5 — Reminders

With the full task list settled, offer to set reminders for outstanding time-sensitive tasks. For trips in the future or in progress, scope to tasks still ahead (e.g. upcoming check-ins, outstanding bookings) — not pre-departure prep that has already passed. For trips that have fully passed, scope to deadline-bound Follow-up tasks (e.g. insurance-claim windows, equipment-return dates). Use whichever reminder capability is available and best fits the user's context and preferences. If none are available, note it in the plan. Confirm each reminder with the user before setting it — when using a task app, make explicit what will be created and in which app (gate 2 — see `references/sync-protocol.md`); record set reminders in Sync State.

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

