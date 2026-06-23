---
description: Derive your trip preparedness checklist — visa, vaccinations, insurance, packing, gear — with lead times, without the full workflow.
argument-hint: [optional: focus, e.g. "documents" or "packing"]
---

Run a **standalone readiness pass** on the current trip plan — do not run the full workflow. Invoke the read-only `trip-readiness` agent with the plan, the trip context (trip type, party incl. kids' ages and minors, pets, nationality/passport, dietary, accessibility), and any feasibility findings already on hand.

It returns a categorized prep digest — documents/visa, health/vaccinations, insurance, packing/gear, money, connectivity, vehicle, pet, minors — each with a lead time and a suggested reminder date. Present it grouped by category and offer to add items as tasks (and time-sensitive ones as reminders) through the usual gates. Scope to what's still ahead.

Focus (may be empty → everything still ahead): $ARGUMENTS
