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

**Two confirmation gates apply to changes Claude initiates:**
1. Confirm before **updating the travel plan** — including data imported from connected tools or email, unless the user explicitly directed that action.
2. Confirm before **exporting plan data to any connector**.

When the user directs an action, act on it directly — do not re-confirm what was just instructed.

## Capabilities

See `references/capabilities.md` for all available tools and session capabilities. All tool use is conditional on availability — never hard-stop because a tool is missing. When a capability is missing, mention the connect-to-save benefit **once**, then drop it.

---

## Step 1 — Intake

Before asking the user anything — and again whenever they ask to update their trip status — load context from all connected tools. Use what you find, along with the conversation, to determine whether this is a returning or first-time user. A returning user is one who has previously run this workflow for this trip in a prior session — a travel plan already exists. Anything said in the current conversation does not count as prior invocation. A first-time user has not previously run the workflow for this trip.

### Returning user (travel plan already exists)

**1.1 Reconcile the travel plan.**

1. **Resolve ambiguity first.** If multiple distinct trips are found, ask which one they mean. If no plan or trip data can be found anywhere, surface this explicitly and ask whether to start fresh.
2. **Reconcile.** Update the plan from the prior artifact, connected tools, and the conversation — updating only what has changed.
3. **Confirm the baseline.** Present the plan to the user and get explicit confirmation before proceeding — do not begin writing until the user approves.
4. **Route by trip dates:**
   - Trip is in the future → run the full workflow (Steps 2–5)
   - Trip is in progress → Steps 2, 3, 4 (scoped to The Trip tasks), then Step 5
   - Trip has fully passed → go to Step 4, scoped to the Follow-up checklist

**1.2 Reconcile connectors against the plan.** Cross-reference findings from all connected tools and email against the plan:
- **Surface gaps** — if a booking or event appears in a connector or email but is missing from the plan, surface it; add it to the plan once confirmed.
- **Deduplicate** — the plan is the deduplication anchor. If something already appears in the plan, do not surface it again regardless of which connector also has it.

See `references/email-integration.md` for email-specific guidance.

Only ask about what genuinely can't be inferred. Summarize what you found, then proceed with Steps 2–5 only where an update is needed:

> "Looks like you're flying to Tokyo in September — solo trip, flights and hotel already in your plan. Found a new tour confirmation in your email that's not captured yet. Want me to add it and check what else is still ahead?"

### First-time user (no travel plan yet)

If email is connected, search for booking confirmations matching the trip and surface anything not yet captured before generating the baseline plan.

Gather intake, then generate the baseline travel plan. Only ask for what can't be inferred from connected tools or the conversation:
- **Destination and dates** — infer from the user's message if possible
- **Trip type** — infer from destination and transport (e.g. "driving to the coast" → road trip, "flying to Tokyo" → international)
- **Who's traveling** — solo, couple, group, family with kids (and ages if relevant)
- **Pets** — coming along or staying home
- **What's already booked** — use any context already loaded from connected tools; ask only for what isn't already known. Capture as free text (e.g. "flights booked, hotel sorted, nothing else yet")

Generate the plan from what you gathered and confirm it with the user before proceeding.

**Take their word for it.** If they say something is done, treat it as done and focus on what's still ahead.

---

## Step 2 — Itinerary

Build out the plan's day-by-day content from what was gathered in Step 1, confirming updates before writing them.

**Always generate a named markdown file** for the plan (e.g. `tokyo-itinerary.md`) — even when a connected itinerary app is present. Use lowercase, hyphens for spaces, strip special characters; for multiple destinations use the first or primary. For returning users, update the existing file in place — do not regenerate from scratch.

If an itinerary app is connected, offer to export the plan there in addition to the markdown file (confirm before exporting).

See `references/itinerary-integration.md` for guidance.

---

## Step 3 — Schedule

Export the plan's dated items to a connected calendar, and import existing trip events back into the plan. Confirm before either direction. If dates aren't known yet, skip and offer to revisit once the plan has dates set.

See `references/calendar-integration.md` for full guidance.

---

## Step 4 — Tasks

If a task app is connected, import tasks from it — for returning users this includes syncing status changes for tasks already in the plan. For first-time users, task context was already loaded in Step 1. Then identify what's still ahead and not yet captured. Cross-reference the plan's tasks against:
- What the user said is already done — exclude anything they've confirmed complete
- `references/task-checklist.md` — surface genuine gaps only

Present gaps grouped by category from `references/task-checklist.md`. Only suggest tasks for things not done in reality AND not yet in the plan. Add confirmed tasks to the plan. If a task app is connected, keep the plan and task app in sync: export plan tasks to the app and import any app tasks not yet in the plan — confirm Claude-initiated changes before writing in either direction.

See `references/task-integration.md` for guidance.

---

## Step 5 — Reminders

With the full task list settled, offer to set reminders for time-sensitive prep tasks (e.g. visa application, flight check-in). Use whichever reminder capability is available and best fits the user's context and preferences. If none are available, note it in the plan. Confirm each reminder with the user before setting it — when using a task app, make explicit what will be created and in which app (gate 2 applies).

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
- Add (Preparation): pet-friendly lodging, transport pet policy and fees, health certificate and vaccination records, vet check, pet-friendly activities at destination, locate nearest vet at destination
- Add (Pre-Departure): pet supplies (food, carrier, comfort items, medication), confirm carrier meets transport requirements

