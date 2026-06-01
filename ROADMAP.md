# Roadmap

## Skill Review (Pre-Release)

The current single skill needs a careful review before sharing. Key questions to resolve:

### Architecture
- Should this be one skill or multiple? Candidates for splitting: intake, task management, calendar setup, email scanning, returning user flow
- Can one connector serve both task and calendar purposes? (e.g. Google Calendar + Google Tasks, or Notion). If so, the two-connector requirement may be overstated. **Resolved:** the plugin detects capabilities, not connector count. A single connector exposing both task and calendar tools would work fine. README updated to reflect capabilities rather than specific apps.
- **Resolved:** Keep a single orchestrating skill. Routing multiple travel skills via description-matching would create trigger ambiguity, and the workflow is sequential with shared state — splitting would force each skill to re-establish trip context. Revisit only if a sub-flow earns a genuinely distinct, standalone trigger.

### Connector behavior
- Audit exactly what Claude does in each connected app — what it reads, what it writes, what it creates
- Ensure the skill instructions are precise enough that Claude doesn't do more than intended in any connector
- Clarify what "cross-referencing" means in practice for each connector pairing
- **Resolved (v0.1.1):** Audited reads/writes across task, calendar, and email connectors. Email guidance now cross-references against both tasks and calendar (previously tasks only), matching SKILL.md Step 4.

### User-facing actions
- Review every step where Claude creates or modifies something in a user's app
- Confirm confirmation prompts are clear and appropriately scoped
- Ensure Claude never creates anything without explicit user approval
- **Resolved (v0.1.1):** Step 3 (calendar) rewritten to frontload "only create what the user confirms" instead of leading with imperative "Create"/"Add" verbs, matching the confirmation-first pattern already used in Step 2 (tasks).

---

## Booking Intel Agent

Extract all booking discovery into a dedicated agent that the main skill can call and act on, rather than doing the information gathering inline.

### What it does

Given trip context (destination, dates), the agent searches across all connected tools and returns a structured digest:

```
{
  confirmed: [ { type, vendor, dates, ref } ],   // bookings found + already captured
  new:       [ { type, vendor, dates, ref } ],   // found in email/calendar, not yet in task project
  gaps:      [ "return leg", "hotel night 3" ]   // expected bookings not found anywhere
}
```

### Why an agent

- **Encapsulation:** inbox scanning is noisy — the agent absorbs raw email content and returns only the structured fields the skill needs
- **Reusability:** both the initial intake flow and the returning-user check need booking discovery; the agent handles both without duplicating logic
- **Cleaner main thread:** the skill receives a tidy summary instead of interleaving search results with planning steps

### Connector scope

- **Email:** search for flight, hotel, rental car, tour confirmations in the date range
- **Calendar:** check for trip-related events not yet in the task project
- **Task project:** retrieve existing tasks to cross-reference against

### Changes required

- Add `agents/booking-intel/AGENT.md` defining the agent, its inputs (trip context), and its output schema
- Update `SKILL.md` Step 1 (returning user) and Step 4 to call the agent instead of doing discovery inline
- Update `references/email-integration.md` and `references/calendar-integration.md` to note they describe agent behavior, not inline skill behavior

---

## Slash Commands (Optional Polish)

Add explicit entry points as flat command files alongside the auto-triggering skill. These give power users a direct handle without relying on the description-match trigger.

| Command | Intent |
|---|---|
| `/travel-planner:plan` | Start a new trip from scratch — jumps straight to first-time intake |
| `/travel-planner:checkin` | Returning user check-in — pulls project context and surfaces what's changed |
| `/travel-planner:scan` | Run the Booking Intel Agent standalone — surface new confirmations without the full workflow |

### Changes required

- Add `commands/plan.md`, `commands/checkin.md`, `commands/scan.md` as flat skill files
- Each command can be thin — a brief description and a hand-off to the relevant section of `SKILL.md` or the Booking Intel Agent
- Low priority: the skill auto-triggers well; these are for users who prefer explicit invocation

---

## Budgeting & Cost Splitting

Add a budgeting/cost split app as an optional connector. Useful across all trip types but especially important for groups.

### Connector support
Splitwise, Tricount, YNAB, Trail Wallet — detect what's connected, use it if available, skip silently if not.

### Behavior by traveler type

| Traveler | Behavior |
|---|---|
| Solo | Offer for spend tracking against budget; don't push it |
| Couple | Light value — spend tracking only |
| Group | Surface prominently; cost splitting is a core need |
| Family | Useful for spend tracking; splitting less relevant |

### What it should do
- On first session: if a budgeting app is connected, offer to set up a trip budget and shared expense tracker
- On return sessions: check for new expenses logged since last session and flag anything that looks unaccounted for
- For groups: suggest splitting setup early in the Preparation phase before money starts moving

### Changes required
- Add budgeting connector detection to the Required Tools section of the skill
- Add traveler-context-aware budgeting tasks to the relevant phases (Define for budget-setting, Preparation for splitting setup)
- Update the README under "What you need"
