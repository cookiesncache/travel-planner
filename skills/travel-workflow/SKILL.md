---
name: travel-workflow
description: >
  Plan any trip end-to-end using a 5-step workflow backed by a 5 Phase Task
  Checklist. Use when the user says "plan my trip", "help me organize a trip",
  "travel checklist", "what do I need for my vacation", "I'm traveling to X",
  or asks to review or add tasks to an existing trip plan. Covers all
  trip types: road trips, flights, international travel, city breaks, and
  multi-destination tours.
---

# Travel Workflow

Guide the user through planning their trip using the 5-step workflow below. The 5 Phase Task Checklist at the bottom is for scoping what's still ahead — not the workflow itself.

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

See `references/fallbacks.md` for running with no connectors. See `references/integrations.md` for how to identify which tools are connected. Once you know what's connected, proceed.

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

## Step 2 — Build the Travel Plan

Build out the plan's day-by-day content from what was gathered in Step 1, confirming updates before writing them. Then, if an itinerary app is connected, offer to export the plan there (confirm before exporting).

See `references/itinerary-integration.md` for guidance.

---

## Step 3 — Schedule

Export the plan's dated items to a connected calendar, and import existing trip events back into the plan. Confirm before either direction:
- An event spanning the full trip (departure to return) — use specific times if known, otherwise all-day
- Individual events for flights, hotel check-ins/outs, timed-entry bookings, and major planned activities

If dates aren't known yet, skip and offer to revisit once the plan has dates set.

See `references/calendar-integration.md` for guidance.

---

## Step 4 — Tasks

Identify what's still ahead and not yet captured. Cross-reference the plan's tasks against:
- What the user said is already done — exclude anything they've confirmed complete
- The 5 Phase Task Checklist below — surface genuine gaps only

Present gaps grouped by phase. Only suggest tasks for things not done in reality AND not yet in the plan. Add confirmed tasks to the plan. If a task app is connected, keep the plan and task app in sync: export plan tasks to the app and import any app tasks not yet in the plan — confirm Claude-initiated changes before writing in either direction.

See `references/task-integration.md` for guidance.

---

## Step 5 — Reminders

With the full task list settled, set reminders for time-sensitive prep tasks (e.g. visa application, flight check-in). Use whichever capability is available, in order of preference: connected calendar → connected task app → scheduled-task capability. Only skip if none are available. Only set reminders the user confirms.

If no dates are set yet, skip and offer to revisit once the plan has dates.

See `references/fallbacks.md` for the no-calendar reminder path.

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

---

## The 5 Phase Task Checklist

### Phase 1 — Define 🧠

- Confirm travel dates and duration
- Identify destinations (and order for multi-destination trips)
- Set a total trip budget (transport, lodging, food, activities, contingency)
- Clarify who's traveling (solo, couple, group, children?)
- Confirm days off work / any time constraints

### Phase 2 — Preparation 📖

**Transport:**
- Book flights (check baggage allowance and seat selection)
- Reserve rental car if driving (pickup location, vehicle class, insurance)
- Book trains, ferries, or inter-city transport for multi-destination trips
- Confirm airport/station transfers at origin and destination

**Lodging:**
- Book all accommodation — flag any gaps in nightly coverage
- Confirm cancellation policies

**Tickets & Passes:**
- Book timed-entry attractions that sell out in advance
- Purchase transit passes or city cards if applicable
- Research any entry passes relevant to the destination

**Admin (scale to trip type):**
- Check passport validity (many countries require 6 months beyond return date)
- Research and apply for visa if required
- Check travel advisories for destination
- Arrange travel insurance (especially for international trips)
- Check vaccination or health entry requirements
- Notify bank/credit card of travel dates and destinations
- Obtain local currency or confirm card acceptance
- Save copies of key documents (passport, insurance, reservations)
- Share itinerary and emergency contacts with someone at home

**Planning:**
- Finalize daily itinerary
- Research dining, neighborhoods, and must-do activities
- Download offline maps for areas with limited connectivity
- Download offline content (music, podcasts, shows) for long transit

### Phase 3 — Pre-Departure 🔨

- Build and finalize packing list (clothing, gear, adapters, medication, first aid)
- Confirm all reservations 48 hours before departure
- Check in for flights / confirm transport bookings (flight check-in usually opens 24 hrs out)
- Charge all devices and power banks
- Set out-of-office replies if needed
- For road trips: inspect vehicle, check tire pressure

### Phase 4 — The Trip 🚀

- Track spending against budget as you go
- Keep digital and physical copies of documents accessible
- Note any booking issues to follow up on after returning

### Phase 5 — Follow-up ✅

- Return any rented vehicles or equipment; confirm no extra charges
- Review final spend vs. budget
- File travel insurance claims if needed
- Save and organize photos
- Note what worked and what to do differently next time
