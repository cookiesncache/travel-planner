---
description: Scan email for new booking confirmations and cancellations, cross-referenced against the trip plan — no full workflow.
argument-hint: [optional: trip or vendor to focus on]
---

Run a **standalone inbox scan** — do not run the full workflow. Invoke the read-only `booking-intel` agent to search the connected email for trip-relevant booking **confirmations** and **cancellations/changes**, cross-referenced against the current plan:

- Dedup confirmations by confirmation number against the plan's `## Bookings` list.
- Skip anything matching a `declined` / `untracked` / `cancelled` / `orphaned` row in `## Sync State`.

Present the agent's `missing` / `flagged` / `cancelled` digest and **ask before changing anything** — this command only surfaces findings. If no email app is connected, say so and stop. If no trip plan exists yet, the agent still scans — surface what it finds, note it can't be deduped against a plan, and suggest `/travel-planner:plan` to start one.

Focus (may be empty): $ARGUMENTS
