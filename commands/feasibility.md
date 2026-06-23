---
description: Check whether the current itinerary is realistic — pacing, weather, budget, safety, legality, seasonal routes — without the full workflow.
argument-hint: [optional: a day or "the whole trip"]
---

Run a **standalone feasibility check** on the current trip plan — do not run the full workflow. Invoke the read-only `feasibility-check` agent against the plan's day-by-day itinerary, passing the trip context (party, pace preference, accessibility, must-do anchors, nationality) and the spending file (its path and the Trip budget value).

It returns findings — with confidence and sources — across pacing/travel-time, weather, budget, safety, legality, seasonal route viability, and time-validity, each with at least one concrete rebalancing option. Present them grouped by day and let the user decide. This command **surfaces constraints**; it never books or writes a connector, and findings are advisory.

Scope (may be empty → the whole trip): $ARGUMENTS
