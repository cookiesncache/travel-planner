---
description: Find more to do — events, activities, and dining matched to your trip — surfaced as a pick-list, without the full workflow.
argument-hint: [optional: destination/day/category, e.g. "Kyoto, food"]
---

Surface a **broad candidate set** for the current trip — do not run the full workflow or the feasibility loop. Invoke the read-only `activity-discovery` agent with the plan, the traveler's preference signals (interests, pace, party, dietary, accessibility, must-do anchors, budget), destinations, and dates.

It returns Events / Activities / Dining candidates (each tagged with cost, duration, indoor/outdoor, opening hours, reservation/urgency, and more), deduped against the plan and `## Sync State`. Present them via native multi-select — one prompt per category — and add the user's picks to the plan through gate 1. For a trip in progress, scope to the remaining days.

To also vet the additions for realism in the same pass, use `/travel-planner:enrich` instead.

Scope (may be empty → the whole trip): $ARGUMENTS
