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

One plugin hook (a **sync-back check**) blocks ending a turn until connector writes are recorded in Sync State. **Gate 2 is confirmed in the main thread**: before any connector write, present a native `AskUserQuestion` naming exactly what will be created, changed, or deleted and in which app, and export only what the user approves (one prompt per batch). If the sync-back hook blocks, record the writes in Sync State and finish.

## Capabilities

See `references/capabilities.md` for all available tools and session capabilities. All tool use is conditional on availability — never hard-stop because a tool is missing. When a capability is missing, mention the connect-to-save benefit **once**, then drop it.

---

## Step 1 — Intake

Before asking the user anything — and again whenever they ask to update their trip status — load context from all connected tools. Use what you find, along with the conversation, to determine whether this is a returning or first-time user. A returning user is one who has previously run this workflow for this trip in a prior session — a travel plan already exists. Anything said in the current conversation does not count as prior invocation. A first-time user has not previously run the workflow for this trip.

### Returning user (travel plan already exists)

Reconcile the travel plan:

1. **Resolve ambiguity first.** Read `.claude/travel-planner.local.md` if it exists — its `trips` list names every known trip and its plan file, with `active_trip` as the default (see `references/sync-protocol.md`). If the request could match more than one trip, ask which they mean. If the state file is missing, scan the project directory for `*-itinerary.md` plan files before concluding there's nothing. Only if none is found anywhere, surface this explicitly and ask whether to start fresh.
2. **Reconcile against connectors and email — both directions, then propose.**
   - **Additive (new/changed in email):** run the read-only `booking-intel` agent to scan email; it returns `missing` confirmations, `flagged` items, and `cancelled`/changed items, already cross-referenced against the plan (email confirmations deduped by confirmation number against the plan's `## Bookings` list; `declined`/`untracked`/`cancelled`/`orphaned` items skipped). See `references/email-integration.md` for how to handle each.
   - **Subtractive (gone from connectors):** read each connected tool and diff it against `## Sync State`. Only treat a `synced` row as `orphaned` when the read is **conclusive** — a direct fetch of its remote ID returns not-found, or a complete/unfiltered listing omits it; a partial/scoped read, a tool error, or a task merely filtered out because it's closed is **not** an orphan. A task completed in the app is a status change, not an orphan — fetch completed tasks too. Also re-offer cleanup for any row marked `cleanup pending` (a prior cleanup that was denied or failed), and set a `synced` row `stale` if the remote item's key fields no longer match the plan body. (This reconciliation stays in the main thread — see `references/sync-protocol.md`.)
   - **Propose, don't apply:** present everything — additions (from `missing`), removals/flags (from `cancelled`/`orphaned`), status changes — and get the user's confirmation before writing (gate 1). Then apply per `sync-protocol.md` (re-status rows; connector cleanup after gate-2 confirmation). The plan is the deduplication anchor; never re-surface a handled item as new — but a *new* confirmation number for the same vendor + dates of a `cancelled`/`orphaned` item is a re-booking, so surface it.
3. **Confirm the baseline.** Present the plan to the user and get explicit confirmation before proceeding — do not begin writing until the user approves.
4. **Route by trip dates:**
   - Trip is in the future → run the full workflow (Steps 2–7)
   - Trip is in progress → Steps 2, then 5–7 (scoped to The Trip tasks); skip the feasibility loop (Step 3) and readiness (Step 4) — pacing and prep are moot once travel is underway
   - Trip has fully passed → Steps 6 and 7, scoped to the Follow-up checklist (deadline-bound follow-ups — insurance-claim windows, equipment returns — still get reminders); when Follow-up wraps up, set that trip's `status: done` in the state file

Only ask about what genuinely can't be inferred. Summarize what you found, then proceed with Steps 2–7 only where an update is needed:

> "Looks like you're flying to Tokyo in September — solo trip, flights and hotel already in your plan. Found a new tour confirmation in your email that's not captured yet. Want me to add it and check what else is still ahead?"

### First-time user (no travel plan yet)

If email is connected, run the read-only `booking-intel` agent to surface booking confirmations matching the trip (and any cancellations) before generating the baseline plan; present anything not yet captured for the user to confirm. There's no plan or Sync State yet, so a `cancelled` finding just means **don't add that as a booking** — and if a `missing` confirmation for the same vendor/dates is also surfaced, treat it as cancelled (don't add it), seeding a `cancelled` row when the plan is created in Step 2. As soon as the destination is known, write the state file (see `references/sync-protocol.md`) so the trip is discoverable. If the user declines any surfaced booking *before* the plan file exists, remember it and record its `declined` row when the plan is created in Step 2 — otherwise it re-surfaces next session.

Gather intake, then generate the baseline travel plan. Only ask for what can't be inferred from connected tools or the conversation:
- **Destination and dates** — infer from the user's message if possible
- **Trip type** — infer from destination and transport (e.g. "driving to the coast" → road trip, "flying to Tokyo" → international)
- **Who's traveling** — solo, couple, group, family with kids (and ages if relevant)
- **Pets** — coming along or staying home
- **Budget** — the total trip budget, if the user has one in mind. Feeds the spending file's Trip budget and Remaining figures. If they don't have one, leave it unset (the spending file omits those figures until a budget is established).
- **What's already booked** — use any context already loaded from connected tools; ask only for what isn't already known. Capture as free text (e.g. "flights booked, hotel sorted, nothing else yet")
- **Interests + travel-style/pace** — what they enjoy (museums, outdoors, food, nightlife) and whether they prefer a packed schedule or a relaxed one. Infer if the user's message makes it clear; ask briefly if not.
- **Must-do anchors** — anything they definitely want to see or do (unbooked wishes). Record these in the plan so discovery can dedup against them and feasibility treats them as fixed points that are never proposed for cutting.
- **Nationality + passport validity** (international trips only) — needed for visa/entry assessment in the feasibility check and the readiness step. Check passport expiry if offered; flag if it falls within 6 months of the return date.
- **Dietary needs + accessibility needs** — ask only when relevant (group with mixed needs, a traveler who mentioned a restriction). These filter discovery candidates and relax feasibility's pacing thresholds.

Generate the plan from what you gathered and confirm it with the user before proceeding.

**Take their word for it.** If they say something is done, treat it as done and focus on what's still ahead.

---

## Step 2 — Itinerary

Build out the plan's day-by-day content from what was gathered in Step 1, confirming updates before writing them.

**Always generate a named markdown file** for the plan (e.g. `tokyo-itinerary.md`) — even when a connected itinerary app is present. Keep a `## Bookings` identity list and a one-line `## Spending` summary + pointer in the plan — not a money table; the money lives in a standalone **`<dest>-spending.xlsx`** generated alongside it with live formulas (see `references/spending-integration.md`). Generate/update the spending file whenever a booking is confirmed; its formulas recalculate the total and remaining automatically — run the recalc-validation pass and refresh the `## Spending` summary. Use lowercase, hyphens for spaces, strip special characters; for multiple destinations use the first or primary. For returning users, update the existing files in place — do not regenerate from scratch.

Every plan file ends with a `## Sync State` section, and every item carries an inline ID (see `references/sync-protocol.md`). When the plan file is created, seed `## Sync State` with a `declined` row for anything the user declined during intake. Ensure `.claude/travel-planner.local.md` lists this trip in its `trips` list with `active_trip` pointing at it — append, don't overwrite other trips — so future sessions can find the plan.

If an itinerary app is connected, offer to export the plan there in addition to the markdown file (confirm before exporting).

**Enrich the plan with the `activity-discovery` agent.** After the baseline exists, invoke the read-only `activity-discovery` agent: give it the plan file, the traveler's preference signals (interests, pace, party, dietary, accessibility, must-do anchors, budget), destinations, dates, and the Sync State ledger. It returns a categorized set of candidates (Events / Activities / Dining) each tagged with cost, duration, indoor/outdoor, weather sensitivity, opening hours, venue type, and more. Present them to the user via one or more native `AskUserQuestion` (`multiSelect: true`) per `references/discovery-integration.md` — one prompt per category, sub-chunked by day when the list is large. Add the selected items to the plan via **gate 1** (one confirmation per batch). Fixed-date events become anchors; dining picks feed the feasibility meal-time math. Re-runnable on request ("find me more to do in X"). **For a trip already in progress, scope discovery to the remaining days** (or run it only when the user explicitly asks); **skip it for a passed trip** — broad pre-trip enrichment is moot once travel is underway, though the on-request re-run stays available. See `references/discovery-integration.md` for full guidance.

See `references/itinerary-integration.md` for guidance, including the fallback if the prior markdown file cannot be located, and `references/spending-integration.md` for the spending file's schema, generation, and recalc-validation.

---

## Step 3 — Feasibility

**Run this before any scheduling, task sync, or reminders — and before the user books anything.** It gates Steps 5–7: do not export to a calendar, sync tasks, or set reminders until the itinerary's pacing and viability have been checked and the user has rebalanced or accepted the trade-offs. Verifying now, while rebalancing nights and base towns is still cheap, is the whole point — once bookings are confirmed the fixes are gone.

Run automatically for any trip with inter-stop travel — road trips, and multi-destination trips by car, flight, train, or ferry; offer it (lighter pacing pass but full non-pacing dimensions) for single-base city breaks. Skip only when the trip is already in progress or has passed — pacing is moot then.

**The adversarial enrichment loop:**

1. Invoke the `feasibility-check` agent on the enriched plan. Give it the plan file, trip context (party, pace preference, accessibility, must-do anchors, nationality, budget), and the spending file (its path and the Trip budget value). The agent checks pacing, weather, budget, safety, legality, seasonal route viability, and time-validity across all days. It returns findings with confidence and sources.
2. Present findings to the user grouped by day. For each conflict the agent flags, offer at least one concrete rebalancing option. When the fix is a swap of an activity or dining pick, you may re-invoke the `activity-discovery` agent for that slot — pass it the day scope and the **constraints to preserve** (clean flags that must remain satisfied) so the swap can't reintroduce a problem the loop just cleared.
3. After the user chooses (apply swap / rebalance manually / accept as-is), update the plan via gate 1 if anything changed, then re-invoke feasibility if the change affected other days.
4. **Cap at 2 targeted re-discovery rounds** per conflict, then present a native `AskUserQuestion` with: *Apply suggested swap / Find different options / Accept as-is and proceed*. "Accept as-is" is always offered from the first round — findings are advisory, never blocking.
5. Once the user has resolved or accepted all findings, proceed to Step 4.

See `references/feasibility-integration.md` for full guidance on flag types, thresholds, the data contract with discovery, and the loop protocol.

---

## Step 4 — Readiness

After the adversarial loop converges on a realistic, enriched plan, invoke the read-only `trip-readiness` agent to derive trip preparedness. Give it the plan file, trip context (trip type, party incl. kids' ages and minors, pets, **nationality/passport details**, dietary needs, accessibility needs), and the **feasibility digest** from Step 3 (especially its weather, safety, legality, route, and budget findings). The agent is the **sole emitter of prep actions**: it converts feasibility's constraints into the tasks and packing items the user must act on, so nothing is surfaced twice.

The agent returns a categorized prep digest (documents/visa, health, insurance, packing/gear, money, connectivity, vehicle, pet, minors), each item with a lead time, a suggested reminder date, and a mapping to a `task-checklist.md` category. Route the digest:
- **Step 6 (Tasks)** — prep tasks grouped by checklist category, with due dates where applicable
- **Step 7 (Reminders)** — items with `suggestedReminderDate` (visa deadlines, vaccination start dates) offered as reminders via gate 2

Skip this step for trips already in progress or fully passed. For a returning user asking "what do I still need to prepare or pack?", run it scoped to what's still ahead.

See `references/readiness-integration.md` for full guidance on the feasibility→readiness contract, prep categories, lead-time defaults, and task-checklist mapping.

---

## Step 5 — Schedule

Export the plan's dated items to a connected calendar, and import existing trip events back into the plan. Gates and Sync State recording per `references/sync-protocol.md`. If dates aren't known yet, skip and offer to revisit once the plan has dates set.

See `references/calendar-integration.md` for full guidance.

---

## Step 6 — Tasks

If a task app is connected, import tasks from it — for returning users this includes syncing status changes for tasks already in the plan. For first-time users, task context was already loaded in Step 1. Then identify what's still ahead and not yet captured. Cross-reference the plan's tasks against:
- What the user said is already done — exclude anything they've confirmed complete
- `references/task-checklist.md` — surface genuine gaps only; for post-trip sessions scope to the Follow-up category only

Present gaps grouped by category from `references/task-checklist.md`. Only suggest tasks for things not done in reality AND not yet in the plan. Add confirmed tasks to the plan. If a task app is connected, keep the plan and task app in sync: export plan tasks to the app and import any app tasks not yet in the plan — gates and Sync State recording per `references/sync-protocol.md`.

See `references/task-integration.md` for guidance.

---

## Step 7 — Reminders

With the full task list settled, offer to set reminders for outstanding time-sensitive tasks. For trips in the future or in progress, scope to tasks still ahead (e.g. upcoming check-ins, outstanding bookings) — not pre-departure prep that has already passed. For trips that have fully passed, scope to deadline-bound Follow-up tasks (e.g. insurance-claim windows, equipment-return dates). If more than one reminder capability is connected, ask the user which to use — don't choose for them; if only one is available, use it; if none, note it in the plan. See `references/reminder-integration.md`. Confirm the reminders before setting them — present them in **one native `AskUserQuestion`** and set only what the user selects, making explicit what will be created and in which app (gate 2 — see `references/sync-protocol.md`); record reminders set in a connected app in Sync State, and for any the user deselects at the prompt record an `export-declined` row (per `references/sync-protocol.md`) so they aren't re-offered every session; note in-session scheduled-task reminders in the plan body instead (see `references/reminder-integration.md`).

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

**Interests + pace:**
- Use interests to bias discovery candidates toward matching categories and to weight must-do anchors as fixed points
- Use pace preference to scale feasibility's over-packed thresholds: a "relaxed" traveler hits over-packed sooner; a "packed schedule" traveler tolerates more per day

**Accessibility:**
- Add accessibility buffer to feasibility pacing; filter inaccessible discovery candidates
- Add accessible transport and lodging checks to tasks where relevant

**Dietary needs:**
- Filter dining discovery to compatible venues; flag incompatible options rather than silently omitting them

