# Readiness Integration

The readiness step derives what the traveler must **do, obtain, and pack** before they go — after the itinerary is finalized and pacing/viability-checked. Run by the `trip-readiness` agent, which is read-only; the main thread routes its digest into tasks (Step 6) and reminders (Step 7) through the gates.

## When it runs

As **Step 4**, after the feasibility loop has converged on a realistic, enriched plan, and **before** Steps 5–7 (Schedule, Tasks, Reminders). Readiness must see the finalized plan so packing reflects the actual activities chosen, and it must see the feasibility digest so prep actions derive from real itinerary constraints — not from a skeleton.

Skip for trips already in progress or fully passed (prep is moot). For a returning user asking "what do I still need to prepare or pack?", run it scoped to what's still ahead.

## The feasibility → readiness contract

The feasibility agent emits **constraints** about the itinerary ("a visa is required for this nationality", "Day 4 is outdoor / rain likely", "a travel advisory applies to this area"). The readiness agent converts each into the **prep action** ("apply for the visa", "pack a rain shell", "register with your embassy / confirm insurance"). This division is what keeps items from appearing twice:

| Feasibility finding | Readiness action |
|---|---|
| `legality-risk`: visa required for nationality X | Apply for visa — cite lead time; flag passport validity if borderline |
| `legality-risk`: park/trekking permit needed | Obtain permit — book in advance; lead time |
| `legality-risk`: driving permit required | Obtain IDP before travel |
| `weather-risk`: rain likely on outdoor day(s) | Pack: rain shell, waterproof footwear, bag covers |
| `weather-risk`: extreme heat / UV | Pack: sun protection, cooling gear, extra water |
| `weather-risk`: cold / snow | Pack: layers, insulated gear |
| `weather-risk`: monsoon / hurricane season | Travel insurance that covers weather cancellation; consider trip timing |
| `safety-risk`: area advisory | Travel insurance covering the region; register with embassy; share itinerary |
| `safety-risk`: altitude | Acclimatization plan; altitude meds if prescription warranted |
| `safety-risk`: water / health risk | Vaccinations / prophylaxis; water purification |
| `budget-risk`: estimated overrun | Flag to the main thread — surface the overrun before tasks are created so the user can rebalance |
| `route-risk`: seasonal closure flagged | Confirm alternate route / mode before booking |
| Activity `requiresGear` | Pack the specific gear |
| Activity `requiresPermit` | Obtain permit; include lead time |

**Readiness never re-states the constraint** — it states the action. "A visa is required" was feasibility's job; "apply for the visa 6–8 weeks before departure" is readiness's.

## Inputs to pass the agent

- Path to the finalized plan
- Trip context: trip type, party (incl. kids' ages and minors), pets (travelling), **nationality/passport details**, dietary needs, accessibility needs
- The **feasibility digest** (all flags, especially weather/safety/legality/route/budget)
- Path to the `## Sync State` ledger (so already-handled prep items aren't re-raised)

## Prep categories and items

Scale to trip type and traveler — not every item applies to every trip:

| Category | Typical items |
|---|---|
| **Documents / entry** | Passport validity check (6-month rule); visa or eTA (nationality-specific); international driving permit; minors' consent letters and entry rules |
| **Health** | Vaccinations or prophylaxis (destination-specific); prescriptions; altitude or other health prep flagged by feasibility |
| **Insurance** | Travel/medical/cancellation insurance; confirm coverage matches any `safety-risk` areas |
| **Packing / gear** | Clothing for weather; activity-specific gear (`requiresGear`); adapters; medications; dietary aids; accessibility aids |
| **Money** | Local currency / card acceptance; FX; bank travel notice; cost drivers (visa/insurance fees surfaced here so the budget picture is complete) |
| **Connectivity** | eSIM / roaming plan; offline maps for low-signal stretches flagged in the itinerary |
| **Vehicle** | Service / tyres / roadside kit; permits for seasonal routes; check-in to any `route-risk` mitigations |
| **Pet** | Carrier rules; health certificate; vet records; pet supplies |
| **Minors** | Travel documents; consent letters; entry requirements for children; car seats |

## Lead times and reminder dates

Each item carries a `leadTime` and `suggestedReminderDate` derived from the trip's departure date. Default anchors (verify by WebSearch for nationality/destination-specific rules; lower confidence when unverified):

| Item | Typical lead time |
|---|---|
| Visa / eTA | 4–8 weeks minimum; some countries require months |
| Passport renewal | Several months; check current processing times |
| Vaccinations | 4–8 weeks (some courses need multiple doses) |
| Travel insurance | Buy near booking; cancellation cover starts at purchase |
| Permits (trekking, entry) | Days to weeks depending on destination |
| Bank notice / currency / eSIM | 1–2 weeks before departure |
| Packing / gear | Final week before departure |

## How the digest flows downstream

The main thread receives the prep digest and routes each item:

1. **Step 6 (Tasks)** — present prep tasks grouped by category from `task-checklist.md` alongside the regular task audit. Items with a `deadline` get a due date; items that are open-ended go into Planning or Pre-Departure. The `taskChecklistCategory` field on each item maps it to the right section.
2. **Step 7 (Reminders)** — items with `suggestedReminderDate` are offered as time-sensitive reminders (visa application, vaccination, insurance purchase). Gate 2 applies — one native `AskUserQuestion` per batch.

**Reservation tasks** (booking a restaurant, buying a timed-entry ticket flagged by discovery) are **plain Tasks (Step 6), not Readiness items** — they flow from the discovery step's `reservationNeeded` + `availabilityUrgency` fields, not from this agent.

## Sync State

Readiness items that become tasks in a connected app get Sync State rows via the normal task-export path (gate 2 → `synced`). Readiness items noted in the plan body only (packing list, in-session reminders) follow the reminder-integration.md rules — in-session scheduled tasks are not connector items and don't get ledger rows.

## Task-checklist mapping

Map each readiness item to a `task-checklist.md` category so the Step 6 audit can slot it cleanly:

| Readiness category | task-checklist.md section |
|---|---|
| Documents / entry | Preparation → Admin |
| Health | Preparation → Admin |
| Insurance | Preparation → Admin |
| Packing / gear | Pre-Departure |
| Money | Preparation → Admin |
| Connectivity | Pre-Departure |
| Vehicle | Preparation → Transport (road trip) |
| Pet | Preparation → Pets / Pre-Departure → Pets |
| Minors | Preparation → Admin / Traveler Context (family) |

Don't invent new categories — map into what `task-checklist.md` already defines. If an item fits two categories, use the one closer to when the action must happen.
