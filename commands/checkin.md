---
description: Check in on an existing trip — reconciles connectors and email against the plan and surfaces what changed.
argument-hint: [optional: which trip, e.g. "Tokyo"]
---

Resume an **existing** trip. Engage the `travel-planner:travel-workflow` skill on the **returning user** path (Step 1 → returning-user reconcile):

1. Read `.claude/travel-planner.local.md` to locate the plan. If `$ARGUMENTS` names a trip, use that one; otherwise use `active_trip`. If no plan can be found, say so before doing anything.
2. Reconcile **both directions**: run the read-only `booking-intel` agent for new/changed email bookings, and diff each connected tool against the plan's `## Sync State`.
3. Present what's new, changed, or still ahead — and confirm before writing anything (gate 1) or exporting (gate 2).
4. Route by trip dates per the workflow (future → full workflow; in progress → scoped; passed → follow-ups).

Trip to check in on (may be empty → use the active trip): $ARGUMENTS
