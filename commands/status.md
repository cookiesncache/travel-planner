---
description: A read-only snapshot of the trip — days to departure, what's booked, what's still ahead, and budget remaining.
argument-hint: [optional: which trip]
---

Show a **read-only snapshot** of the current trip — make no changes, write nothing, call no connector.

Locate the plan via `.claude/travel-planner.local.md` (use `$ARGUMENTS` if it names a trip, otherwise `active_trip`). Read the plan and its spending file, then summarize at a glance:

- destination(s) and dates, with days until departure (or "in progress" / "completed")
- what's booked vs. still unbooked (from `## Bookings`)
- budget — total spent / remaining / still due in person (from the spending file)
- outstanding tasks and any reminders still ahead

Keep it brief and scannable. Do **not** propose or make changes — for reconciliation and updates, use `/travel-planner:checkin`.

Trip (may be empty → the active trip): $ARGUMENTS
