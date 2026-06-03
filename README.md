# ✈️ Travel Planner

> A plugin that structures trip planning from first idea to follow-up — and stays useful every time you come back to it.

---

## 🗺️ What it does

Tell Claude about your trip. It'll ask what's already handled, figure out what's still ahead, and build out your task project and calendar from there.

Come back mid-planning and it picks up where you left off — checking your task project for progress, your calendar for new events, and your email (if connected) for new booking confirmations, before asking you anything.

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

Nothing is required — the plugin works out of the box and gets more powerful as you connect tools. Connect anything and it's used automatically on your next trip.

**📋 Task management** *(recommended)* — Todoist, Things, Apple Reminders, Asana, etc.
Where your trip tasks live. Not connected? The plugin keeps your plan as a checklist file you can save and bring back later.

**📅 A calendar** *(recommended)* — Google Calendar, Outlook, Apple Calendar, etc.
Used to block out your trip and add key events. Not connected? Key dates go into your checklist, and the plugin can set scheduled reminders for time-sensitive prep.

**📬 An email app** *(optional)* — Gmail, Outlook, etc.
If connected, the plugin scans for booking confirmations when you revisit a trip and flags anything not yet captured. Worth knowing: connecting email gives Claude access to your inbox beyond just travel confirmations.

---

## 📥 How to install

For installation instructions, see the official docs:
- Claude Code (CLI) — [add the marketplace](https://code.claude.com/docs/en/discover-plugins#add-from-github) `cookiesncache/travel-planner`, then [install](https://code.claude.com/docs/en/discover-plugins#install-plugins) `travel-planner@travel-planner-marketplace`
- [Claude Desktop](https://code.claude.com/docs/en/desktop#install-plugins) — add a marketplace from repository `cookiesncache/travel-planner`, then install **Travel Planner**

---

## 💬 How to trigger it

Just mention a trip:

- *"I'm flying to Tokyo in September, help me plan it"*
- *"Planning a road trip, what am I missing?"*
- *"Can you set up my Portugal trip in Todoist?"*
