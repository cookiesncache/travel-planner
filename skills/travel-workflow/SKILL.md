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

**Two confirmation gates apply to changes Claude initiates on its own inference:**
1. Confirm before **updating the travel plan**.
2. Confirm before **exporting plan data to any connector**.

When the user explicitly directs an action in the current exchange — including multi-item directives ("add all three flights," "push everything to my calendar") — act on it directly without re-confirming each item. Broad standing permissions given earlier in the session ("add any bookings you find") do not bypass per-item confirmation.

## Capabilities

Connected tools make the plugin more powerful; without them, the plan still stands on its own as a complete, usable artifact. **Never hard-stop because a tool is missing.** When a capability is missing, mention the connect-to-save benefit **once**, then drop it — do not nudge again later in the session.

**All tool use is conditional on availability — never attempt to use a tool that isn't connected.** When a connector is absent, the relevant content simply lives in the plan with no external sync.

**Calendar — blocks dates and reminds you.** Look for any connected calendar (Google Calendar, Outlook, Apple Calendar, etc.). Export the trip's dated items as events; import existing trip events back into the plan.

**Itinerary apps — a richer home for the day-by-day plan.** Look for any connected itinerary app, notes tool, or docs tool (Wanderlog, Notion, Google Docs, etc.). Export the plan there; import any changes back. If multiple are connected, ask the user which to sync to.

**Task management — tracks what still needs to be done.** Look for any connected task tool (Todoist, Things, Apple Reminders, Asana, TickTick, etc.). Export the plan's tasks; import existing tasks back.

**Email — surfaces existing bookings.** Look for any connected email tool (Gmail, Outlook, etc.). Search for booking confirmations and surface anything missing from the plan. If not connected, skip silently — do not mention it to the user.

See `references/integrations.md` for how to identify which tools are connected. Once you know what's connected, proceed.

---

## Step 1 — Intake

Before asking the user anything — and again whenever they ask to update their trip status — load context from all connected tools. Use what you find, along with the conversation, to determine whether this is a returning or first-time user. A returning user is one who has previously run this workflow for this trip in a prior session — a travel plan already exists. Anything said in the current conversation does not count as prior invocation. A first-time user has not previously run the workflow for this trip.

### Returning user (travel plan already exists)

**1.1 Reconstruct the travel plan.** Rebuild the current plan from the prior plan artifact, connected tools, and the conversation. Present it to the user and get explicit confirmation before proceeding — do not begin reconciling or writing until the user approves the baseline. If multiple distinct trips are found, ask which one they mean before proceeding. If no plan or trip data can be found anywhere, surface this explicitly and ask whether to start fresh.

**1.2 Reconcile connectors against the plan.** Cross-reference findings from all connected tools and email against the plan:
- **Surface gaps** — if a booking or event appears in a connector or email but is missing from the plan, surface it; add it to the plan once confirmed.
- **Deduplicate** — if something already appears in the plan, do not surface it again regardless of which tool it also appears in.

See `references/email-integration.md` for email-specific guidance.

Only ask about what genuinely can't be inferred. Summarize what you found, then proceed with Steps 2–5 only where an update is needed:

> "Looks like you're flying to Tokyo in September — solo trip, flights and hotel already in your plan. Found a new tour confirmation in your email that's not captured yet. Want me to add it and check what else is still ahead?"

### First-time user (no travel plan yet)

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

Build out the plan's day-by-day content from what was gathered in Step 1, confirming updates before writing them. Then, if an itinerary app is connected, offer to export the plan there (confirm before exporting).

See `references/itinerary-integration.md` for guidance.

---

## Step 3 — Schedule

Export the plan's dated items to a connected calendar, and import existing trip events back into the plan. Confirm before either direction:
- A trip event spanning the full trip (departure to return) — use specific times if known, otherwise all-day
- Individual items — see `references/calendar-integration.md` for item-by-item guidance

If dates aren't known yet, skip and offer to revisit once the plan has dates set.

See `references/calendar-integration.md` for guidance.

---

## Step 4 — Tasks

Identify what's still ahead and not yet captured. Cross-reference the plan's tasks against:
- What the user said is already done — exclude anything they've confirmed complete
- `references/task-checklist.md` — surface genuine gaps only

Present gaps grouped by category from `references/task-checklist.md`. Only suggest tasks for things not done in reality AND not yet in the plan. Add confirmed tasks to the plan. If a task app is connected, keep the plan and task app in sync: export plan tasks to the app and import any app tasks not yet in the plan — confirm Claude-initiated changes before writing in either direction.

See `references/task-integration.md` for guidance.

---

## Step 5 — Reminders

With the full task list settled, offer to set reminders for time-sensitive prep tasks (e.g. visa application, flight check-in). Use whichever reminder capability is available and best fits the user's context and preferences. Only skip if none are available. Only set reminders the user confirms.

If no dates are set yet, skip and offer to revisit once the plan has dates.

See `references/reminder-integration.md` for reminder capabilities and the no-calendar path.

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
- Add (Preparation): pet-friendly lodging, transport pet policy and fees, health certificate and vaccination records, vet check, pet-friendly activities at destination
- Add (Pre-Departure): pet supplies (food, carrier, comfort items, medication), confirm carrier meets transport requirements
- Add (The Trip): nearest vet at destination

