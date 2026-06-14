# Roadmap

## v0.7.0 Pre-Release Verification

The v0.7.0 hooks (export gate, sync-back check) are prompt-based and rely on a few runtime behaviors worth verifying once with `claude --debug` — ideally on a Windows machine — before tagging the release:

- [ ] Both hooks register at session start (`/hooks` shows them; no schema errors)
- [ ] The PreToolUse matcher fires on a real connector write (e.g. Todoist `add-tasks`) and does NOT fire on reads (`find-tasks`, `list_events`)
- [ ] In a non-travel session, a matched write resolves via the fast-path allow with no visible friction
- [ ] Gate flow works end-to-end: unconfirmed export → deny → Claude confirms with user → retry → allow
- [ ] Stop hook blocks when an export was made but not recorded in Sync State, and approves after recording (no block loop)
- [x] ~~write tools whose names don't start with a matched verb (e.g. `project-move`) bypass the gate~~ — addressed by **P0-2** below (matcher broadened; `project-move`, Notion, camelCase now caught). Re-verify the broadened matcher against real connectors during `claude --debug`.

### Prompt-hook decision tests

The hook prompts are LLM-evaluated, so their *logic* needs scenario testing, not just registration testing. Run each scenario below by feeding the hook's prompt text plus a short synthetic transcript to a model (or spot-check during `claude --debug`) and confirm the decision. **Every case must resolve to exactly one decision — a hook that returns "insufficient evidence" or any non-answer is a failure by itself.** These cases each pin a behavior a real session broke.

**Stop hook (sync-back check):**
- [ ] **S1 — plugin meta-session** (a dev/review/support chat that discusses plan files like `tokyo-itinerary.md` but makes no connector write) → **approve**. *(Regression: this exact case returned "insufficient evidence" before the activation/decision fix.)*
- [ ] **S2 — unrelated non-travel session** → **approve**
- [ ] **S3 — connector write made and recorded** in `## Sync State` → **approve**
- [ ] **S4 — partial write**: exported, plan *body* updated, but Sync State rows omitted → **block** *(the P0-1 case the temporal proxy used to wave through)*
- [ ] **S5 — export made, nothing recorded** → **block**, then **approve** after recording (no loop)
- [ ] **S6 — compacted history**: writes clearly happened, recording unconfirmable → **block once** with re-read instruction, then **approve** on retry (anti-loop holds)

**PreToolUse gate (export gate):**
- [ ] **G1 — plugin meta-session** where a matched write tool fires → **allow** (activation excludes discussing/developing the plugin)
- [ ] **G2 — active-trip travel export with no prior chat confirmation** → **ask** (v0.7.2 gate never denies; the native prompt is where the user declines if unwanted)
- [ ] **G3 — unrelated write** (groceries to Todoist) mid-travel-session → **allow**
- [ ] **G4 — ambiguous/compacted** — no clear trip active → **allow** (fast-path 1)
- [ ] **G5 — active trip, travel connector write** → **ask** (native harness prompt appears; user approves → write proceeds; user denies → write blocked)
- [ ] **G6 — active trip, auth/auth-completion write** → **allow** (fast-path 2)
- [ ] **G7 — approval via AskUserQuestion**: user selects proposed items in a multi-select → native ask prompt appears → user approves → **allow** *(architectural fix for field incident P0-5: gate no longer attempts to detect AskUserQuestion results, which are not visible to a prompt hook)*
- [ ] **G8 — terse confirmation**: Claude proposes specific writes, user replies "do it" → native ask prompt appears → user approves → **allow** *(architectural fix for field incident P0-5)*
- [ ] **G9 — no deadlock**: a write the gate blocked (user denied the ask prompt), or one not yet made, must not cause the Stop hook to block the turn *(field incident P0-5 — Stop hook already handles this correctly)*

---

## v0.7.x Hardening — Review Findings (prioritized)

Whole-plugin review after the v0.7.0 refactor (consistency, workflow, and hook-correctness lenses, each finding adversarially verified). 16 issues, deduplicated and ranked. Fix **P0** before promoting v0.7.0 to users; **P1** are logic gaps that break advertised behavior; **P2** are honesty/polish. Each item cites the file to change.

### P0 — Correctness bugs  ✅ all fixed — P0-1–4 from the review, P0-5 from a field incident (v0.7.2: architectural fix)

**P0-1 · Stop-hook fast-path approves unrecorded exports** *(bug; found independently by all 3 lenses)* — ✅ **fixed:** approve-condition 2 now keys on whether trip-data writes *happened* this session (not plan-edit recency), with an explicit note that a later plan edit does not imply the rows exist — so the row-existence verification always runs.
`hooks/hooks.json` Stop prompt, approve-condition 2 keys on *recency* ("no connector writes since the plan file was last updated"), not *content*. The most likely failure — Claude updates the plan body but omits the `## Sync State` rows in that same or a later edit — makes the condition literally true, so the deep check that looks for rows never runs. This defeats the exact invariant the hook exists to enforce (`sync-protocol.md`: "an export is not complete until its row exists"). *Fix:* approve only if every connector write this session already has a matching Sync State row (and no approved imports are unwritten); delete the "since the plan file was last updated" clause.

**P0-2 · Matcher silently bypasses real connector write tools, including the whole Notion connector** *(bug)*
`hooks/hooks.json` matcher requires a verb token *immediately* after `mcp__<server>__`, ending in `[_-]` or end-of-string. It misses `notion-create-pages`/`notion-update-page` (product-prefixed — the flagship itinerary connector named in `capabilities.md`, so Step 2 Notion export is 100% un-gated), `project-management` (verb mid-name), and camelCase (`createEvent`). README promises confirmation "before Claude writes to any connected app" — deterministically false for these. Wider than the `project-move` note already in the checklist. ✅ **fixed:** matcher now tolerates an optional product-name prefix (`[a-z0-9]+[_-]`) and a camelCase continuation (`[_A-Z-].*`); regression-tested against 20 real write tools (all match, incl. the 7 former bypasses and now `project-move` too) and 17 read/auth tools (all excluded). Tradeoff: a few non-write names like `settings_update` now match, but the prompt's fast-path allow absorbs them — a handled false-positive beats a silent bypass.

**P0-3 · Decline rule erases the remote ID that suppression depends on** *(bug)*
`sync-protocol.md` Decline rule writes Connector/Remote ID `—` for *all* declines, including connector-sourced ones where both are known. Next-session dedup is remote-ID-keyed, so a declined Todoist task or calendar event reappears, caught only by fuzzy title match. Breaks the "✅ Resolved in v0.7.0" guarantee. ✅ **fixed:** the Decline rule now keeps the source Connector + Remote ID for connector-sourced declines (`—` only for email/user-surfaced items), the Dedup rule suppresses on a remote-ID match against a `declined` row, and the example table shows both forms.

**P0-4 · Gate sync-debt clause is unscoped and exemption-free** *(bug)*
`hooks/hooks.json` PreToolUse "ADDITIONALLY DENY … earlier connector writes … never recorded" (a) doesn't restrict "earlier writes" to trip data, so an allowed unrelated write (e.g. groceries to Todoist mid-session) becomes phantom debt that false-blocks the next user-directed travel export; (b) lacks the Stop hook's exemptions (user declined recording; plan file missing), so it deadlocks against them. ✅ **fixed:** the clause now scopes debt to writes "OF TRIP DATA," and exempts unrelated writes, user-declined recording, and a known-missing plan file — mirroring the Stop hook's exemptions.

**P0-5 · Gate false-denies a user-confirmed write; deadlocks with the Stop hook** *(bug; field incident, BUG_REPORT_travel-planner-export-gate.md, 2026-06-11)*
A returning user approved 4 Todoist tasks twice — an AskUserQuestion multi-select, then a plain-text "do it" — and the export gate denied the `add-tasks` write 4 times with the generic gate-2 reason, then the v0.7.0 Stop hook trapped the turn (approved tasks "unwritten"). Root cause (confirmed): prompt-type PreToolUse hooks receive only event-specific JSON (`tool_name`, `tool_input`, `transcript_path`) — not the conversation inline. AskUserQuestion results and recent user messages live in the transcript file, which a prompt hook cannot open. Two prompt-wording fixes (v0.7.0 and v0.7.1) both failed for this reason. ✅ **fixed (architectural):** the gate no longer attempts to detect confirmation from the conversation. Instead it returns `ask` for any active-trip travel write — the harness surfaces a native approve/deny prompt, which *is* the confirmation mechanism. Fast-path allows (non-travel session, unrelated write) are unchanged. The ADDITIONALLY DENY sync-debt clause was removed from the gate; the Stop hook is the sole enforcer of that invariant and has better context to do so. The Stop-hook deadlock is still prevented by P0-1 (only *writes that happened* are debt; a gate-blocked write never happened).

### P1 — Logic gaps that break advertised behavior  *(7 of 7 fixed)*

**P1-1 · Intake phase is invisible to the ledger and the gate before the plan file exists** *(gap; merges two findings)*
The first-time flow surfaces email confirmations *before* the plan file is created (`SKILL.md` Step 1), but the decline rule writes to a Sync State ledger that doesn't exist yet, so an intake-time decline evaporates and re-surfaces next session. Same root cause: the gate's fast-path keys on plan/state-file artifacts existing, so the entire intake phase isn't recognized as a travel session. ✅ **fixed:** first-time intake now writes the state file as soon as the destination is known, and the plan-creation step seeds `## Sync State` with `declined` rows for anything declined during intake (`SKILL.md` Step 1/Step 2 + a Decline-rule note in `sync-protocol.md`). The activation half was already addressed by the hook-prompt rewrite (hooks reason about real connector writes, not file artifacts).

**P1-2 · Single-slot state file orphans concurrent trips** *(gap)*
`sync-protocol.md` state file holds one `active_trip` and "starting a new trip overwrites it." A second concurrent trip destroys the first's pointer, status, and connector choices, and nothing instructs scanning the project for other `*-itinerary.md` files — yet the README sells multi-trip return use. ✅ **fixed:** the state file is now a `trips` list with an `active_trip` pointer (new trips append, never overwrite); Step 1 resolves ambiguity from the list and scans the project for `*-itinerary.md` before declaring nothing found.

**P1-3 · Calendar reminders are required and forbidden at once** *(gap)*
`reminder-integration.md` says create a calendar reminder alert for "visa application"; `calendar-integration.md` forbids calendar events for prep reminders, naming "apply for visa" verbatim. A calendar-only user at Step 5 gets contradictory instructions and may refuse or hedge. ✅ **fixed:** `calendar-integration.md`'s whitelist/ban is now scoped to Step 3 itinerary export, with an explicit Step 5 exception allowing a user-confirmed `rm`-type reminder alert as a calendar event when calendar is the chosen reminder capability. Also addressed the related preference-forcing problem: when more than one reminder-capable connector is connected, the workflow now **asks the user which to use for reminders** instead of picking a default (`reminder-integration.md` "Choosing the capability", `SKILL.md` Step 5, `capabilities.md`), recording the choice in the state file.

**P1-4 · Sync State `pending` status has no lifecycle** *(gap)*
`sync-protocol.md` defines and exemplifies `pending` but no recording rule ever produces or clears it, so deferred or mid-batch-failed exports have no path — and the Stop hook's "no approved changes left unwritten" can block with no rule to satisfy. ✅ **fixed:** added a Pending recording rule to `sync-protocol.md` (write `pending` on deferral/failure, clear to `synced` on successful export, and a cross-session pending row must be re-confirmed before export).

**P1-5 · Scheduled-task reminders have no valid Connector value** *(gap)* — ✅ fixed (Option 2)
A session-capability reminder isn't an app, but Sync State requires a human app name. ✅ **fixed:** in-session scheduled-task reminders are now explicitly **exempt from the Sync State ledger** — noted in the plan body instead; only reminders set in a connected app (calendar/task app) get an `rm` row (`reminder-integration.md`, `sync-protocol.md` Recording rules, `SKILL.md` Step 5). Residual (accepted): `create_scheduled_task` still matches the export-gate verb pattern, so it draws a native `ask` prompt — benign under the v0.7.2 ask-gate (the user confirms, and Step 5 confirms each reminder anyway). Suppress later with a gate fast-path for in-session capability tools if the extra prompt proves annoying.

**P1-6 · Post-trip route skips reminders** *(gap)*
The returning-user route sends a passed trip to Step 4 only; deadline-bound Follow-up tasks (insurance claims, rental returns) never get reminder offers. ✅ **fixed:** the post-trip route now runs Steps 4 *and* 5 scoped to the Follow-up checklist, and Step 5 explicitly scopes passed trips to deadline-bound Follow-up tasks (`SKILL.md` Step 1 routing + Step 5).

**P1-7 · Stop-hook blind spots: compaction and user veto** *(gap; merges two findings)* — ✅ fixed
(a) No compaction guard — the gate fails closed on truncated history, but the Stop fast-path *approves* on the same blindness, ending a turn with unrecorded exports invisible. (b) Condition 3 lets the user veto recording, breaking the ledger invariant with no recovery path. ✅ **partly fixed:** compaction guard added to the Stop prompt (block-once + re-read instruction; the anti-loop rule prevents a second block). This work also fixed a related flaw caught while testing the hook live — **both hooks over-triggered their "active travel session" detection on mere discussion/reading/development of the plugin** (a plugin-dev or support session looked like a live trip), and the **Stop prompt could return a non-decision** ("insufficient evidence in transcript") instead of approve/block. Both hooks now lead with "did a real connector write of trip data actually happen this session," explicitly exclude discussing/developing/supporting the plugin, and the Stop prompt is forced to resolve to exactly one decision with a default-approve on residual doubt. ✅ **now fully fixed:** a recording-veto leaves a minimal `untracked` Sync State row (new status; item + connector + remote ID, no Spending Tracker row, no day-by-day detail) — it honors "don't track it in my plan" while giving reconciliation the remote ID it needs so the connector item isn't re-surfaced as new next session.

### P2 — Honesty & polish  *(5 of 5 fixed)*

**P2-1 · GUI/computer-use connectors bypass both hooks** *(gap)*
Apple Calendar/Reminders/Things on Desktop are driven via computer-use, whose tool names never match `mcp__`. The README overclaimed "before Claude writes to any connected app." ✅ **fixed:** the README and `hooks.json` description are scoped honestly to MCP connectors (with a note that screen-driven apps fall back to the prose confirm-first rule), and `sync-protocol.md`'s "never work around a hook" rule now states that non-MCP write paths (screen, browser, shell) are gate-2 prose territory, not mechanically gated.

**P2-2 · "No-op instantly" overstates hook cost** *(improvement)*
Both hooks are prompt (LLM) evaluations; the Stop check runs at the end of *every* turn in *every* enabled session. ✅ **fixed:** `hooks.json` description and README now say the hooks "resolve via a fast-path allow," and the README notes the small per-turn cost and that infrequent travelers can disable the plugin between trips.

**P2-3 · `task-integration.md` missing the state-file recording line** *(improvement)*
Two of three sibling integration files tell Claude to record the chosen app in the state file; `task-integration.md`'s multiple-apps sentence didn't. ✅ **fixed:** added the recording clause to `task-integration.md` and to the central multiple-tools rule in `capabilities.md`.

**P2-4 · Dangling plan-file pointer has no handler** *(gap)* — ✅ fixed
The regenerate fallback only fired when *both* the plan file and state file were missing; state-file-present-but-`plan_file`-path-dangling had no instruction. ✅ **fixed:** `itinerary-integration.md`'s Updating fallback now splits into two cases — state file missing (scan the project per Step 1, else ask to regenerate/start fresh) and **state file present but `plan_file` unresolved** (surface it explicitly, scan for a renamed/moved `*-itinerary.md` and repoint, else ask to regenerate or supply the file — noting lost decline/sync history can't be recovered). No silent proceed on a dangling pointer.

**P2-5 · Export gate behavior inside subagents** *(gap)* — ✅ closed by constraint (Option A)
Original concern: PreToolUse fires inside subagents where the parent's approval isn't visible, so the old deny-gate false-blocked a delegated approved export; and the Stop sync-back hook doesn't fire for subagents, so a subagent's connector writes wouldn't be recorded. The v0.7.2 ask-gate already removed the false-deny half (the gate no longer detects confirmation). ✅ **closed:** `sync-protocol.md` now codifies that **connector writes happen in the main thread only — subagents are read-only with respect to connectors** (they read and report; the main thread exports and records). That moots both halves at once: no subagent ever trips the gate, and none needs SubagentStop recording. Re-open only if a future feature genuinely requires a subagent to write to a connector — at which point: verify `ask`-in-subagent with `claude --debug` and add a SubagentStop mirror.

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

- Add `agents/booking-intel.md` defining the agent, its inputs (plan + trip context), and its output schema *(flat `agents/<name>.md` — the auto-discovered convention; not a nested `AGENT.md`)*
- Update `SKILL.md` Step 1.2 to call the agent instead of pointing to `email-integration.md` inline
- Update `references/email-integration.md` to describe agent behavior and output schema
- **No connector/plan writes from the agent itself.** Per the read-only-subagent constraint (`sync-protocol.md`, P2-5), Booking Intel reads email and **returns data only**; the main thread adds to the plan and exports, so the main-thread Stop hook already covers recording. No SubagentStop mirror is needed as long as the agent makes no writes of its own.

---

## Itinerary Feasibility Check (pre-booking pacing review) *(High priority)* — ✅ implemented & validated

From a field user story (`USER_STORY_travel-planner-feasibility-check.md`): a 9-day California road trip was fully booked before anyone checked whether the day-to-day schedule was physically realistic. A later drive-time review found a "sightseeing" day that was really a ~7–8.5 h transit day (Joshua Tree → Yosemite), a compressed coast leg (Mendocino → Big Sur), a departure-day backtrack past the airport, and a geographically inconsistent lodging label. Because everything was booked, these could only be *managed*, not *fixed*. The check must run **before** booking, while rebalancing nights and base towns is still cheap.

### What it does
On a draft itinerary, estimate per-leg **travel time by mode** (drive/flight/train/ferry — door-to-door, so a short flight still counts its airport + transfer overhead) and per-stop time, then flag: over-packed travel days; "sightseeing" days that are really transit; rushed or under-used stops; geographically inconsistent lodging / departure-day backtracks. Every finding carries a confidence level + sources and at least one concrete rebalancing option (move a night, change a base town, reorder stops, swap a leg's mode), framed as still-cheap-to-change. *(Generalized 2026-06-14 from drive-only to all travel modes.)*

### Where it runs
Its own **Step 3**, after the itinerary is drafted (Step 2) and before Steps 4–6 (scheduling, task sync, reminders) generate booking-type commitments — never only after bookings are confirmed. (Originally shipped as a sub-paragraph of Step 2, which caused real runs to order it *last*, after task sync and calendar export; promoted to a first-class gating step to fix the ordering.) Auto-run for any trip with inter-stop travel — road trips, and multi-destination trips by car, flight, train, or ferry; offer it (lighter: intra-day/transfer feasibility) for single-base city breaks. For a returning user whose trip is already booked, still run it but frame findings as *manage-only* — and note that pre-booking is the right time.

### Data source (pivotal constraint — verified this session)
There is **no maps/routing/directions connector** available, and the only distance-ish tool (Uber `get_estimates_between_two_locations_claude`) is unusable here — immediate-ride-only, refuses future dates, returns a booking widget. So estimates come from **WebSearch/WebFetch** (typical travel times by mode — drive/train/flight/ferry, with citations) — preferred, and it satisfies the "sources + confidence" criterion — falling back to model geographic/transport knowledge flagged **low confidence** when search is unavailable or inconclusive. If a routing connector is added later, the agent should prefer it.

### Why an agent
Like the Booking Intel Agent, this is noisy multi-step work (per-leg searches, threshold checks, geo reasoning). A dedicated **Feasibility Check Agent** absorbs the noise and returns a clean structured digest. It is **read-only** (reads the plan; makes no connector or plan writes), so it needs no Stop/SubagentStop sync-back hook. Reusable as a standalone `/check` command.

Output schema (sketch):
```
{ days: [ { date, label,
    legs: [ { from, to, mode, travelTime, distanceMi (if driving), confidence, sources[] } ],
    totalTravelTime,
    flags: [ { type: over-packed-travel | mislabeled-transit | rushed-stop | underused-stop | geo-inconsistent-lodging | departure-day-backtrack, detail, confidence, sources[] } ],
    rebalanceOptions: [ string ] } ],
  overallVerdict, confidence }
```

### Thresholds (defaults, tunable in the reference file)
Heavy travel day > ~5 h door-to-door; effectively-transit > ~7 h (a single flight often lands here once airport overhead + transfers count). A "sightseeing"/activity label whose travel time dominates usable daytime → mislabel. Stop time below a typical minimum for the stop type → rushed; a marquee destination with far more time than planned use → under-used. Lodging far from the day's activity cluster, or routing that backtracks past the destination/airport → geo-inconsistent / backtrack.

### Changes required
- ✅ Added `agents/feasibility-check.md` — read-only agent (Read/Grep/Glob/WebSearch/WebFetch), inputs, output schema, WebSearch-with-citations + low-confidence fallback. *(Flat `agents/<name>.md` — that is the auto-discovered convention; a nested `agents/<name>/AGENT.md` would NOT load.)*
- ✅ Added `references/feasibility-integration.md` — leg definition, flag types, thresholds, rebalancing patterns, manage-vs-fix framing.
- ✅ `SKILL.md` — its own **Step 3** gating Steps 4–6 (trip-type gated; skipped for in-progress/passed trips; agent hand-off; resolve or accept findings before proceeding). Schedule/Tasks/Reminders renumbered to Steps 4/5/6.
- ✅ `references/task-checklist.md` — folded the check into "Finalize daily itinerary," ahead of Preparation booking tasks.
- ✅ README — pre-booking feasibility note.

### Definition of done — ✅ met (validated 2026-06-13)
Validated live (WebSearch) against a pre-booking draft of the California trip (`Projects/Travel/california-road-trip-prebooking-draft.md`): the agent independently surfaced all four documented problems — Sep 21 Joshua Tree → Yosemite transit-day (mislabeled sightseeing), Sep 27 Mendocino → Big Sur compression, Sep 28 departure-day backtrack (flagged must-fix), and the inconsistent Ukiah lodging — each with a confidence level, cited sources, and concrete rebalancing options, while correctly passing the genuinely-fine days. Minor cosmetic nit observed: the verdict miscounted "8 days" for a 9-day trip (findings all correct).

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

## Email Declined-Item Suppression *(partially resolved in v0.7.0 — two holes remain)*

The v0.7.0 Sync State ledger resolves this for the common case: declining a surfaced booking writes a `declined` row, and reconciliation checks Sync State before surfacing. **But the v0.7.x review found two holes that break "suppressed permanently":** connector-sourced declines erase the remote ID suppression depends on (**P0-3**), and declines during first-time intake have no ledger to write to yet (**P1-1**). Suppression is only durable once both are fixed.

---

## Integration file review *(low priority)*

The v0.7.x review above covered cross-file consistency and connector behavior (P1-3, P2-3, P2-4 in particular). This item is now narrowed to the trip-type *scoping* question the review did not target: the city-break Admin items (what to apply when a city break is also international).

### Changes likely required
- `references/task-checklist.md` city-break row: clarify which Admin items apply when a city break is also international, rather than leaving "unless international" unexplained
