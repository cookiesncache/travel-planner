# ✈️ Travel Planner

> A plugin that structures trip planning from first idea to follow-up — and stays useful every time you come back to it.

---

## 🗺️ What it does

Tell Claude about your trip. It'll ask what's already handled, figure out what's still ahead, and build a **travel plan** — a single day-by-day record of your trip that works with or without any connected apps.

Connect your calendar, itinerary, or task apps and the plan syncs both ways: it pushes events and tasks out to them, and pulls new bookings back in. Come back mid-planning and it picks up where you left off — reconciling your connected apps and email against the plan before asking you anything.

Works for any trip type:

| Type | Examples |
|---|---|
| 🚗 Road trip | Weekend drive, cross-country |
| ✈️ Domestic flight | City break, short-haul |
| 🌍 International | Visa, passport, insurance and all |
| 🏙️ City break | Light logistics, activities focus |
| 🔀 Multi-destination | Multiple legs, lodging gaps |

Adapts based on who's traveling, whether you have kids, and what's happening with your pets.

🧭 For road trips and multi-stop trips, it runs a **feasibility check before you book** — estimating travel times (driving, flights, trains, ferries, door-to-door) *and the time meals actually eat* (the detour plus sitting down), then flagging over-packed days, days that would miss a check-in cutoff or dinner reservation, "sightseeing" days that are really transit, and base towns that don't match the day's plan — with sources and concrete rebalancing options. Catch the unrealistic days while moving a night is still free, not after the hotels are paid for.

✨ Connectors are detected automatically at the start of each session — add one anytime and the plugin will start using it on your next trip. Switch apps by disconnecting the old one and connecting the new one; no reconfiguration needed.

---

## 🔧 What you can connect

Nothing is required — your travel plan always works on its own, and connected apps are sync targets that make it more powerful. Connect anything and it's used automatically on your next trip.

**🗺️ An itinerary app** *(optional)* — Wanderlog, Notion, Google Docs, etc.
A richer home for the day-by-day plan. The plugin syncs your plan there and pulls changes back.

**📅 A calendar** *(recommended)* — Google Calendar, Outlook, Apple Calendar, etc.
Your trip's dated items sync here as events. Not connected? Key dates stay in the plan.

**📋 Task management** *(recommended)* — Todoist, Things, Apple Reminders, Asana, etc.
Your trip tasks sync here. Not connected? Tasks stay in the plan as a checklist you can save and bring back later.

**📬 An email app** *(optional)* — Gmail, Outlook, etc.
If connected, the plugin scans for booking confirmations and flags anything missing from your plan. Worth knowing: connecting email gives Claude access to your inbox beyond just travel confirmations.

---

## 🔒 How it stays reliable

Two things keep the plan-is-source-of-truth rule reliable — no setup needed:

- **Confirm before write** — before Claude writes anything to a connected app, it shows you a native prompt listing exactly what it'll create and in which app (one prompt for a whole batch, where you pick which to add). Nothing is written until you approve. This confirmation happens in the conversation, not as a hook.
- **Sync-back check** *(a built-in hook)* — before Claude finishes a turn, the hook verifies that everything it pushed to or pulled from your apps is recorded back in the travel plan, so the plan never silently drifts behind.

In sessions where you aren't travel planning, the sync-back hook resolves right away via a fast allow and lets Claude carry on. Your plan file carries a **Sync State** section — a small ledger of what's synced where (and what you've declined, so it's never suggested again).

Worth knowing:
- The sync-back hook runs a quick check at the end of each turn, so it adds a little latency even outside travel planning. If you travel only occasionally, you can disable the plugin between trips and re-enable it when you need it.
- The plugin keeps a small state file at `.claude/travel-planner.local.md` in your project so it can find your trip across sessions. If the project is a git repository, add `*.local.md` to `.gitignore`.
- After installing or updating the plugin, start a fresh session — hooks load at session start.

---

## 📥 How to install

- Claude Desktop — Add a marketplace from the GitHub repository `cookiesncache/claude-plugins`, then install "Travel planner"
- Claude Code (CLI) — [Add the marketplace](https://code.claude.com/docs/en/discover-plugins#add-from-github) `cookiesncache/claude-plugins`, then [install the plugin](https://code.claude.com/docs/en/discover-plugins#install-plugins) `travel-planner@cookiesncache-marketplace`

---

## 🔄 How to update

For update instructions, see the [official docs](https://code.claude.com/docs/en/discover-plugins#configure-auto-updates). Auto-update can be enabled per marketplace via `/plugin` → **Marketplaces** → select the marketplace → **Enable auto-update**.

---

## 💬 How to trigger it

Just mention a trip:

- *"I'm flying to Tokyo in September, help me plan it"*
- *"Planning a road trip, what am I missing?"*
- *"Can you set up my Portugal trip in Todoist?"*
