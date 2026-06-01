# Roadmap

## Skill Review (Pre-Release)

The current single skill needs a careful review before sharing. Key questions to resolve:

### Architecture
- Should this be one skill or multiple? Candidates for splitting: intake, task management, calendar setup, email scanning, returning user flow
- Can one connector serve both task and calendar purposes? (e.g. Google Calendar + Google Tasks, or Notion). If so, the two-connector requirement may be overstated. **Resolved:** the plugin detects capabilities, not connector count. A single connector exposing both task and calendar tools would work fine. README updated to reflect capabilities rather than specific apps.

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
