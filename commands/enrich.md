---
description: Enrich the plan and keep it realistic — runs the adversarial discovery↔feasibility loop on the current trip.
argument-hint: [optional: destination/day to focus the loop on]
---

Run the **adversarial enrichment loop** on the current plan (the `travel-workflow` Step 2 discovery + Step 3 feasibility loop) — turn a thin itinerary into an *enriched but realistic* one, without re-doing intake:

1. Invoke `activity-discovery` to surface Events / Activities / Dining; the user multi-selects and picks are added via gate 1.
2. Invoke `feasibility-check` on the enriched plan; surface any conflicts (pacing / weather / budget / safety / legality / route) with concrete rebalancing options.
3. For a flagged pick, re-invoke discovery for a **targeted swap**, passing the clean flags to preserve so a swap can't reintroduce a cleared problem. Cap at **2 re-discovery rounds**, then offer *apply swap / find different / accept as-is* — "accept as-is" is available from round 1; all findings are advisory.
4. Converge on the enriched-but-realistic plan, then stop — don't carry on into scheduling/tasks/reminders unless the user asks.

Skip enrichment for a passed trip; scope to the remaining days for one in progress.

Focus (may be empty → the whole trip): $ARGUMENTS
