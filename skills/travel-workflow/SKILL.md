---
name: travel-workflow
description: >
  Plan any trip end-to-end using a structured 5-phase workflow. Use when the
  user says "plan my trip", "help me organize a trip", "travel checklist",
  "what do I need for my vacation", "I'm traveling to X", or asks to review
  or add tasks to an existing travel project. Covers all trip types: road
  trips, flights, international travel, city breaks, and multi-destination
  tours. Requires task management and calendar capabilities. A single connector exposing both is fine. Email integration
  is optional.
---

# Travel Workflow

Guide the user through planning their trip using the 5-phase structure below.

## Required Tools

Check for required tools before doing anything else. Be specific and actionable if something is missing — the user may not know what to do.

**Task management (required):** Look for any connected tool that supports task creation and management (Todoist, Things, Apple Reminders, Asana, TickTick, etc.). If none is found, stop and respond with something like:

> "To get started, this plugin needs a task management app connected — that's where your trip tasks will live. Apps like Todoist, Things, or Apple Reminders all work. You can find setup instructions here: https://support.claude.com/en/articles/11176164-use-connectors-to-extend-claude-s-capabilities — come back once it's connected and we'll pick up from here."

**Calendar (required):** Look for any connected tool that supports calendar events (Google Calendar, Outlook, Apple Calendar, etc.). If none is found, stop and respond with something like:

> "This plugin also needs calendar access — it'll use it to block out your trip and add key events. Google Calendar, Outlook, and Apple Calendar all work. Setup instructions: https://support.claude.com/en/articles/11176164-use-connectors-to-extend-claude-s-capabilities"

If both are missing, mention both in a single message rather than stopping twice.

**Email app (optional):** If a connected email tool is available, use it to surface existing booking confirmations. If not, skip silently — do not mention it to the user.

Once both required tools are confirmed, proceed.

---

## Step 1 — Intake

Before asking the user anything, check whether a travel project already exists in their task management tool.

### Returning user (project exists)

Pull context from connected tools before asking any questions:

- **Task management:** Fetch the project overview — infer destination, trip type, dates, and traveler context from existing tasks
- **Email (if connected):** Search for new booking confirmations since the last session — flag anything not yet in the project
- **Calendar (if connected):** Check for new trip-related events added since the last session — flag anything not yet in the project

After pulling context, cross-reference findings across connectors before surfacing anything to the user:

- If a new email confirmation matches an existing calendar event, treat it as already captured — do not surface it as a gap
- If a new calendar event matches an existing task, treat it as already captured
- Only surface something as new if it isn't already reflected in any connected tool

Only ask about what genuinely can't be inferred. If the project makes the situation clear, skip straight to Step 2 with a brief summary of what you found:

> "Looks like you're flying to Tokyo in September — solo trip, flights and hotel already in the project. Found a new tour confirmation in your email that's not captured yet. Want me to add it and check what else is still ahead?"

### First-time user (no project found)

Ask before doing anything:

- Where are they going, and when?
- Who's traveling? (solo, couple, group, family with kids — and ages of kids if relevant)
- Do they have pets? If so, are the pets coming or staying home?
- What's already done? (e.g. "flights booked, hotel sorted, nothing else yet")

**Ask only if not inferable:**
- Trip type — infer from destination and transport if possible (e.g. "driving to the coast" → road trip, "flying to Tokyo" → international). Ask only if genuinely unclear.

**Take their word for it.** If they say something is done, treat it as done. Do not create tasks for it, do not question it, do not suggest confirming it. The checklist is for what's still ahead, not a retrospective audit.

---

## Step 2 — Audit the Task Project

Find the user's travel project in their task management tool. If no travel project exists, offer to create one.

Cross-reference existing tasks against:
1. What the user said is already done — exclude anything they've confirmed complete, even if there's no task for it
2. The 5-phase checklist below — identify what's genuinely still ahead and not yet captured

Present gaps grouped by phase. Only suggest tasks for things that are both not done in reality AND not yet in the project. Ask which to add before creating anything.

If the project has no sections, offer to add them:
- "Define"
- "Preparation"
- "Pre-Departure"
- "The Trip"
- "Follow-up"

Do not embed dates or months in section names.

See `references/task-integration.md` for guidance.

---

## Step 3 — Set Up the Calendar

Using the connected calendar tool, propose the following and only create what the user confirms:
- A multi-day all-day event spanning the full trip (departure to return)
- Individual events for flights, hotel check-ins/outs, timed-entry bookings, and major planned activities
- Reminders for time-sensitive prep tasks (e.g. visa application, flight check-in) — offer these separately

If dates aren't known yet, skip and offer to revisit once tasks have due dates set.

See `references/calendar-integration.md` for guidance.

---

## Step 4 — Check Email (if available)

Only run this step for returning users (project already existed at the start of the session). For first-time users, intake already captures what's done — skip this step entirely.

If a connected email tool is available, search for booking confirmations added since the last session (flights, hotels, rental cars, tours). Cross-reference against both the task project and the calendar — only surface something if it isn't already reflected in either. Flag any confirmation that looks incomplete.

Do not read or summarize full email content — only extract booking type, date, and vendor.

See `references/email-integration.md` for guidance.

---

## Trip Types

Use the trip type (inferred or confirmed in intake) to scope which checklist items are relevant:

- **Road trip** — driving, route planning, vehicle logistics; skip flight-related items
- **Domestic flight** — flights, no passport or visa needed
- **International** — full admin checklist: passport, visa, insurance, currency, health requirements
- **City break** — short stay, lighter logistics; skip most admin unless international
- **Multi-destination** — multiple transport legs, higher risk of lodging gaps between stops

## Traveler Context

Use who's traveling and pet situation to scope suggestions:

**Solo:**
- Add: share itinerary with someone at home, check-in schedule with a contact
- Skip: group coordination tasks

**Couple:**
- Similar to solo; flag dining reservations if the destination warrants it

**Group:**
- Add: shared itinerary distribution, group transport coordination, cost-splitting plan
- Flag: lodging that accommodates the full group

**Family with kids:**
- Add: child-specific packing (medications, snacks, entertainment), car seat if renting a vehicle, kid-friendly activity research, more conservative daily pacing
- For international: travel documents and consent letters for minors, check entry requirements for children
- Flag: lodging suitability for kids, flight seat arrangements

**Pets — staying home:**
- Surface explicitly: arrange pet care (sitter, kennel, trusted contact), leave feeding and emergency vet instructions
- Do not bury this in generic "home care" language

**Pets — coming along:**
- Add across relevant phases:
  - Preparation: verify pet-friendly lodging, check airline or transport pet policy and fees, book pet in cabin or cargo as required, obtain health certificate and vaccination records, vet check before travel, confirm pet-friendly activities at destination
  - Pre-Departure: pack pet supplies (food, carrier, comfort items, medication), confirm carrier meets transport requirements
  - The Trip: locate nearest vet at destination

---

## The 5 Phases

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
- Book all accommodation — flag any gaps in the nightly calendar
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
- Confirm all reservations 48 hrs before departure
- Check in for flights (usually opens 24 hrs out)
- Charge all devices and power banks
- Set out-of-office replies if needed
- For road trips: inspect vehicle, check tire pressure

### Phase 4 — The Trip 🚀

- Track spending against budget as you go
- Keep digital and physical copies of documents accessible
- Note any booking issues to follow up on after returning

### Phase 5 — Follow-up 🚚

- Return any rented vehicles or equipment; confirm no extra charges
- Review final spend vs. budget
- File travel insurance claims if needed
- Save and organize photos
- Note what worked and what to do differently next time
