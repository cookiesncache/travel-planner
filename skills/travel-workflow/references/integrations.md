# Integrations Reference

## Google Calendar

Use when connected to create structure around the trip dates.

**Trip event:**
- Create a single all-day multi-day event spanning the full trip (departure to return date)
- Title: destination(s) — e.g. "Tokyo & Kyoto Trip"

**Individual events to create:**
- Flights (departure time, airline/flight number in description, arrival airport in location)
- Hotel check-ins and check-outs
- Timed-entry bookings (museums, parks, tours)
- Major planned activities with known times

**Reminders:**
- Offer to add calendar reminders for time-sensitive prep tasks — e.g. "Apply for visa" 6 weeks out, "Check in for flight" day before

Only create events the user confirms. If dates aren't known yet, skip and offer to revisit once Todoist tasks have due dates set.

## Gmail

Use when connected to cross-reference existing booking confirmations.

**Search for:**
- Flight confirmations (search: "flight confirmation booking")
- Hotel reservations (search: "hotel reservation confirmation")
- Rental car bookings (search: "rental car reservation")
- Tour or attraction tickets (search: "booking confirmation ticket")

**For each confirmation found:**
- Check whether a corresponding task already exists in the Todoist project
- If not, surface it to the user and offer to add a task
- Flag any confirmation that looks incomplete (e.g. missing return leg, no confirmation number)

Do not read or summarize full email content — only extract booking type, date, and vendor to match against Todoist tasks.
