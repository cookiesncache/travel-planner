# Fallbacks (No Connector)

The plugin works without connected tools. Use these fallbacks so the user still
gets a complete, usable plan. Offer the connect-to-save benefit **once** per
capability, then stop nudging.

## Task management → checklist markdown artifact

When no task tool is connected, maintain the plan as a markdown file the user
can keep and re-share with Claude later.

- Create one file per trip, named after the destination (e.g. `tokyo-trip.md`).
- Structure it by the 5 phases, each task a checkbox. Add a due date in
  parentheses where the task has a natural deadline.
- Update the file as planning evolves — check off completed items, add new ones
  the user approves. Same approval rule as connected tools: never add a task
  without the user's go-ahead.
- Do not embed dates or months in the phase headings themselves.

Example:

```markdown
# Tokyo Trip — Sep 12–20, 2026

## Define
- [x] Confirm dates and travelers
- [ ] Set total trip budget

## Preparation
- [ ] Book return flight (by Jul 1)
- [ ] Reserve hotel for Sep 14
- [ ] Check passport validity (6 months beyond return)

## Pre-Departure
- [ ] Check in for flight (24h before)

## The Trip
- [ ] Track spending against budget

## Follow-up
- [ ] Review final spend vs. budget
```

Offer once, e.g.: "I'll keep this as a checklist file for now. Connect a task
app like Todoist and I'll sync it there on your next trip instead."

## Calendar → checklist dates + scheduled-task reminders

When no calendar tool is connected:

- **Dated items:** record the trip span and key dated events (flights, check-ins,
  timed bookings) in the checklist artifact, ideally in a short "Key dates"
  section at the top so they're easy to scan.
- **Reminders:** offer once to set scheduled-task reminders for time-sensitive
  prep — e.g. a reminder to apply for a visa weeks out, or to check in for a
  flight the day before. Only set reminders the user confirms.

If scheduled-task capability is also unavailable, just keep the dated items in
the checklist and note that reminders would need a connected calendar.

Offer once, e.g.: "No calendar connected, so I've listed the key dates in your
checklist. Want me to set reminders for the time-sensitive ones?"
