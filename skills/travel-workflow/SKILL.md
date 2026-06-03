---
name: travel-workflow
description: >
  Plan any trip end-to-end using a 4-step workflow backed by a 5 Phase Task
  Checklist. Use when the user says "plan my trip", "help me organize a trip",
  "travel checklist", "what do I need for my vacation", "I'm traveling to X",
  or asks to review or add tasks to an existing trip plan. Covers all
  trip types: road trips, flights, international travel, city breaks, and
  multi-destination tours.
---

# Travel Workflow

Guide the user through planning their trip using the 4-step workflow below. The 5 Phase Task Checklist at the bottom is for scoping what's still ahead — not the workflow itself.

## Capabilities

Connected tools make the plugin more powerful; without them, fall back as described below so the user still gets a complete, usable plan. **Never hard-stop because a tool is missing.**

When a capability is missing, mention the connect-to-save benefit **once**, then drop it — do not nudge again later in the session.

**Calendar — blocks dates and reminds you.** Look for any connected calendar (Google Calendar, Outlook, Apple Calendar, etc.).
- *Connected:* create the trip event, key dated events, and reminders.
- *Not connected:* record dated items in the itinerary file instead. Offer once, e.g.: "No calendar connected, so I've added key dates to your itinerary. Want me to set reminders for the time-sensitive ones?"

**Itinerary — the day-by-day trip plan.** Look for any connected itinerary app, notes tool, or docs tool (Wanderlog, Notion, Google Docs, etc.).
- *Connected:* create and maintain the trip itinerary there.
- *Not connected:* generate an **itinerary markdown file** named after the destination (e.g. `tokyo-itinerary.md`). Offer once, e.g.: "I'll keep your itinerary as a file for now. Connect an app like Wanderlog or Notion and I'll maintain it there instead."

The source of truth is the most capable connected itinerary tool — see capability tiers in Step 1. If data exists in a less capable tool, offer to migrate it. If only one itinerary tool is connected, that is the source of truth regardless of capability.

**Task management — tracks what still needs to be done.** Look for any connected task tool (Todoist, Things, Apple Reminders, Asana, TickTick, etc.).
- *Connected:* create and manage trip tasks there.
- *Not connected:* maintain tasks as a **markdown task file**. Offer once, e.g.: "I'll keep your tasks as a file for now. Connect a task app like Todoist and I'll manage them there instead."

**Email — surfaces existing bookings.** Look for any connected email tool (Gmail, Outlook, etc.).
- *Connected:* search for booking confirmations and surface anything not yet captured.
- *Not connected:* skip silently — do not mention it to the user.

**All tool use throughout this skill is conditional on availability — never attempt to use a tool that isn't connected.** Fallback behavior for each capability is defined above.

See `references/fallbacks.md` for fallback behavior. See `references/integrations.md` for how to identify which tools are connected. Once you know what's connected, proceed.

---

## Step 1 — Intake

Before asking the user anything — and again whenever they ask to update their trip status — load context from all connected tools. Use what you find, along with the conversation, to determine whether this is a returning or first-time user. A returning user is one who has previously run this workflow for this trip in a prior session — their data must exist somewhere. Anything said in the current conversation does not count as prior invocation. A first-time user has not previously run the workflow for this trip.

**Itinerary tool capability tiers** (most to least capable): purpose-built travel apps (Wanderlog, TripIt) → structured notes tools (Notion) → general docs (Google Docs) → generated markdown file. If multiple itinerary tools are connected, use these tiers to select the best one, surface the recommendation, and confirm with the user before proceeding.

### Returning user (workflow previously invoked)

**1.1 Establish the source of truth.** Identify the most capable connected itinerary tool using the tiers above and treat it as the source of truth — but let the user override this if they prefer a different tool. Cross-reference everything else against it. If multiple distinct trips are found, ask the user which one they mean before proceeding. If no data is found in any connected tool, surface this explicitly — do not silently create a new file. Ask whether to start fresh or check a different tool.

**1.2 Offer to upgrade if a more capable connector is available.** If a more capable itinerary tool is connected but isn't the current source of truth, surface this and offer to port the trip plan over. If the user declines, continue with the existing source of truth.

**1.3 Surface what's new.** Load findings from all connected tools and cross-reference them against the source of truth in both directions:
- **Into the source of truth** — if a booking or event appears in email, calendar, or tasks but is missing from the source of truth, surface it as new
- **Deduplication** — if something already appears in the source of truth, do not surface it again regardless of which other tool it also appears in

See `references/email-integration.md` for email-specific guidance.

Only ask about what genuinely can't be inferred. Summarize what you found, then proceed with Steps 2–4 only where an update is needed:

> "Looks like you're flying to Tokyo in September — solo trip, flights and hotel already captured. Found a new tour confirmation in your email that's not in your itinerary yet. Want me to add it and check what else is still ahead?"

### First-time user (workflow not previously invoked)

Use what was loaded from connected tools, along with the conversation. Only ask for what still can't be inferred:
- **Destination and dates** — infer from the user's message if possible
- **Trip type** — infer from destination and transport (e.g. "driving to the coast" → road trip, "flying to Tokyo" → international)
- **Who's traveling** — solo, couple, group, family with kids (and ages if relevant)
- **Pets** — coming along or staying home
- **What's already booked** — use any context already loaded from connected tools; ask only for what isn't already known. Capture as free text (e.g. "flights booked, hotel sorted, nothing else yet")

**Take their word for it.** If they say something is done, treat it as done and focus on what's still ahead.

---

## Step 2 — Itinerary

Create or update the day-by-day trip plan using what was gathered in Step 1. Only add or change what the user confirms.

See `references/itinerary-integration.md` for guidance.

---

## Step 3 — Schedule

Create or update calendar events — only make changes the user confirms:
- An event spanning the full trip (departure to return) — use specific times if known, otherwise all-day
- Individual events for flights, hotel check-ins/outs, timed-entry bookings, and major planned activities
- Reminders for time-sensitive prep tasks (e.g. visa application, flight check-in) — use whichever is available: calendar, task app, or scheduled-task capability. Only skip reminders if none of these are available.

If dates aren't known yet, skip and offer to revisit once the itinerary has dates set.

See `references/calendar-integration.md` for guidance.

---

## Step 4 — Tasks

Identify what's still ahead and not yet captured. Cross-reference against:
- What the user said is already done — exclude anything they've confirmed complete
- The 5 Phase Task Checklist below — surface genuine gaps only

Present gaps grouped by phase. Only suggest tasks for things not done in reality AND not yet in the source of truth. Ask which to add before creating anything.

See `references/task-integration.md` for guidance.

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
