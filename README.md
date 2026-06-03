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

✨ Connectors are detected automatically at the start of each session — add one anytime and the plugin will start using it on your next trip. Switch apps by disconnecting the old one and connecting the new one; no reconfiguration needed.

---

## 🔧 What you can connect

Nothing is required — your travel plan always works on its own, and connected apps are sync targets that make it more powerful. Connect anything and it's used automatically on your next trip.

**📅 A calendar** *(recommended)* — Google Calendar, Outlook, Apple Calendar, etc.
Your trip's dated items sync here as events. Not connected? Key dates stay in the plan, and the plugin can set scheduled reminders for time-sensitive prep.

**🗺️ An itinerary app** *(optional)* — Wanderlog, Notion, Google Docs, etc.
A richer home for the day-by-day plan. The plugin syncs your plan there and pulls changes back.

**📋 Task management** *(recommended)* — Todoist, Things, Apple Reminders, Asana, etc.
Your trip tasks sync here. Not connected? Tasks stay in the plan as a checklist you can save and bring back later.

**📬 An email app** *(optional)* — Gmail, Outlook, etc.
If connected, the plugin scans for booking confirmations and flags anything missing from your plan. Worth knowing: connecting email gives Claude access to your inbox beyond just travel confirmations.

---

## 📥 How to install

For installation instructions, see the official docs:
- [Claude Desktop](https://code.claude.com/docs/en/desktop#install-plugins) — add a marketplace from repository `cookiesncache/travel-planner`, then install **Travel Planner**
- Claude Code (CLI) — [add the marketplace](https://code.claude.com/docs/en/discover-plugins#add-from-github) `cookiesncache/travel-planner`, then [install](https://code.claude.com/docs/en/discover-plugins#install-plugins) `travel-planner@travel-planner-marketplace`

---

## 💬 How to trigger it

Just mention a trip:

- *"I'm flying to Tokyo in September, help me plan it"*
- *"Planning a road trip, what am I missing?"*
- *"Can you set up my Portugal trip in Todoist?"*
