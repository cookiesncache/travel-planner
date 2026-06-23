---
description: Plan a new trip from scratch — runs the travel-workflow first-time intake and builds the baseline plan.
argument-hint: [destination + dates, e.g. "Tokyo Sep 12-20, solo"]
---

Start planning a **new** trip. Engage the `travel-planner:travel-workflow` skill on the **first-time user** path (Step 1 → first-time intake):

1. Load context from any connected tools first (calendar, tasks, itinerary, email).
2. Gather only what can't be inferred — destination, dates, trip type, who's travelling (and kids' ages/pets), budget + home currency, interests + pace, must-do anchors, and — for international trips — nationality/passport.
3. Generate the baseline travel plan (markdown + the standalone spending file), then continue the workflow (discovery → feasibility → readiness → schedule → tasks → reminders).

Take the user's word for what's already booked; focus on what's still ahead.

User's trip details (may be empty): $ARGUMENTS
