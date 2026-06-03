# Fallbacks (No Connector)

The plugin works without connected tools. Use these fallbacks so the user still
gets a complete, usable plan. Offer the connect-to-save benefit **once** per
capability, then stop nudging.

## Task management → markdown task file

When no task tool is connected, maintain tasks as a markdown file the user
can keep and re-share with Claude later.

- Create one file per trip, named after the destination (e.g. `tokyo-tasks.md`).
- List tasks as checkboxes. Add a due date in parentheses where the task has
  a natural deadline.
- Update the file as planning evolves — check off completed items, add new ones
  the user approves. Same approval rule as connected tools: never add a task
  without the user's go-ahead.

Example:

```markdown
# Tokyo Trip — Tasks

- [x] Confirm dates and travelers
- [ ] Set total trip budget
- [ ] Book return flight (by Jul 1)
- [ ] Reserve hotel for Sep 14
- [ ] Check passport validity (6 months beyond return)
- [ ] Check in for flight (24h before Sep 12)
- [ ] Track spending against budget
- [ ] Review final spend vs. budget
```

Offer once, e.g.: "I'll keep your tasks as a file for now. Connect a task
app like Todoist and I'll manage them there instead."

## Calendar → itinerary file + scheduled-task reminders

When no calendar tool is connected:

- **Dated items:** record the trip span and key dated events (flights, check-ins,
  timed bookings) in the itinerary file, ideally in a short "Key dates"
  section at the top so they're easy to scan.
- **Reminders:** offer once to set reminders for time-sensitive prep (e.g. visa
  application, flight check-in). Use whichever is available in order of
  preference: task app → scheduled-task capability → skip if neither available.
  Only set reminders the user confirms.

If no reminder capability is available, just keep the dated items in the
itinerary file and note that reminders would need a connected calendar or task app.

Offer once, e.g.: "No calendar connected, so I've listed the key dates in your
itinerary. Want me to set reminders for the time-sensitive ones?"
