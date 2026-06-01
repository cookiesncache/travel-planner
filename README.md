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

## 🔧 What you need

**📋 Task management** — Todoist, Things, Apple Reminders, Asana, etc.
This is where your trip tasks will be created and managed. Connect one before getting started.

**📅 A calendar** — Google Calendar, Outlook, Apple Calendar, etc.
The plugin will use this to block out your trip and add events as you plan. Connect one before getting started.

**📬 An email app** *(optional)* — Gmail, Outlook, etc.
Not required, but if you connect one, the plugin will scan for booking confirmations when you revisit a trip and flag anything not yet in your task project. Worth knowing: connecting email gives Claude access to your inbox beyond just travel confirmations.

---

## 📥 How to install

You'll need [Claude Desktop](https://claude.com/download) with a paid plan (Pro, Max, Team, or Enterprise) and Cowork enabled.

Download the `.plugin` file from this repo's [Releases](../../releases), then follow [Anthropic's plugin install guide](https://support.claude.com/en/articles/13837440-use-plugins-in-claude).

---

## 💬 How to trigger it

Just mention a trip:

- *"I'm flying to Tokyo in September, help me plan it"*
- *"Planning a road trip, what am I missing?"*
- *"Can you set up my Portugal trip in Todoist?"*
