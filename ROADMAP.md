# Roadmap

## v0.7.0 Pre-Release Verification

The v0.7.0 hooks (export gate, sync-back check) are prompt-based and rely on a few runtime behaviors worth verifying once with `claude --debug` — ideally on a Windows machine — before tagging the release:

- [ ] Both hooks register at session start (`/hooks` shows them; no schema errors)
- [ ] The PreToolUse matcher fires on a real connector write (e.g. Todoist `add-tasks`) and does NOT fire on reads (`find-tasks`, `list_events`)
- [ ] In a non-travel session, a matched write resolves via the fast-path allow with no visible friction
- [ ] Gate flow works end-to-end: unconfirmed export → deny → Claude confirms with user → retry → allow
- [ ] Stop hook blocks when an export was made but not recorded in Sync State, and approves after recording (no block loop)
- [ ] Known gaps to re-check against real connectors occasionally: write tools whose names don't start with a matched verb (e.g. `project-move`) bypass the gate — prose still covers them

---

## ~~Skill Review (Pre-Release)~~ ✅ Archived

All concerns resolved through v0.3.0. Architecture settled on a single orchestrating skill with a plan-centric source of truth, connector-agnostic bidirectional sync, and explicit confirmation gates on all Claude-initiated changes.

---

## Booking Intel Agent

Extract email booking discovery into a dedicated agent. Currently, email scanning is handled by inline prose instructions in `references/email-integration.md`, which means Claude does ad-hoc inbox searches with no structured output. An agent encapsulates the noise and returns clean, plan-aware data.

### What it does

Given the current travel plan and trip context (destination, dates), the agent searches email and returns a structured digest cross-referenced against the plan:

```
{
  missing: [ { type, vendor, dates, ref } ],   // found in email, not yet in plan
  flagged: [ { type, vendor, dates, issue } ], // structurally incomplete or payment rejected
}
```

### Why an agent

- **Encapsulation:** inbox scanning is noisy — the agent absorbs raw email content and returns only the structured fields the skill needs
- **Reusability:** called from Step 1.2 (reconcile) for returning users, and could power a standalone `/scan` slash command
- **Cleaner main thread:** the skill receives a tidy summary instead of interleaving raw search results with planning steps

### Changes required

- Add `agents/booking-intel/AGENT.md` defining the agent, its inputs (plan + trip context), and its output schema
- Update `SKILL.md` Step 1.2 to call the agent instead of pointing to `email-integration.md` inline
- Update `references/email-integration.md` to describe agent behavior and output schema
- **Add a SubagentStop hook mirroring the Stop sync-back check** in the same release — the v0.7.0 Stop hook only fires for the main agent, so an agent that imports bookings would otherwise bypass sync-back enforcement

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

## Budgeting & Cost Splitting *(raised priority)*

Add a budgeting/cost split app as an optional connector. Especially valuable for groups. The travel plan is the natural home for budget tracking — the connector syncs spend data in and out.

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
- On first session: if a budgeting app is connected, offer to set up a trip budget and shared expense tracker; add a budget line to the travel plan
- On return sessions: import new expenses from the connected app into the plan; flag anything that looks unaccounted for
- For groups: suggest splitting setup early in the Preparation phase before money starts moving

### Changes required
- Add budgeting as a capability in `SKILL.md` (alongside Calendar, Itinerary, Task management, Email)
- Add a `references/budget-integration.md` reference file
- Add traveler-context-aware budgeting tasks to the relevant phases (Define for budget-setting, Preparation for splitting setup)
- Update the README

---

## GitHub Release Packaging *(low priority)*

Attach a `.zip` of the plugin directory to each GitHub release so users can install a specific version via `--plugin-url` without going through the marketplace update cycle. Useful for version pinning and offline installs.

### Changes required
- Add a GitHub Action that zips the plugin directory and attaches it as a release asset on each version tag

---

## ~~Email Declined-Item Suppression~~ ✅ Resolved in v0.7.0

Resolved by the Sync State ledger (`references/sync-protocol.md`): declining a surfaced booking writes a `declined` row, and email/connector reconciliation checks Sync State before surfacing anything. Declined items are suppressed permanently unless the user asks.

---

## Integration file review *(low priority)*

The integration reference files (`calendar-integration.md`, `task-integration.md`, `itinerary-integration.md`, etc.) have not been reviewed end-to-end by the author. A manual pass is recommended to verify that the guidance matches real-world connector behavior and that trip-type scoping (e.g. the city-break Admin items question — what to apply when a city break is also international) is correctly specified.

### Changes likely required
- `references/task-checklist.md` city-break row: clarify which Admin items apply when a city break is also international, rather than leaving "unless international" unexplained
