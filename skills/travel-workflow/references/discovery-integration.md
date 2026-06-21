# Discovery Integration

The activity & dining discovery step enriches the baseline itinerary before the feasibility check, so the plan the user vets is the full, realistic one — not a skeleton the feasibility check later fills in. Run by the `activity-discovery` agent, which is read-only; the main thread presents candidates, the user selects, and the main thread writes.

## When it runs

In **Step 2 (Itinerary)**, after the day-by-day baseline exists and before **Step 3 (Feasibility)**. Order matters: the feasibility check must see the enriched plan (the events, activities, and dining the user actually chose) so its meal-time math, time-validity checks, and budget sum are accurate.

**Trip-status scope.** For a future trip, run the full broad pass. For a trip **in progress**, scope candidates to the **remaining days** (or run only when the user asks) — don't surface activities for days already elapsed. For a **passed** trip, skip enrichment. Unlike feasibility and readiness (which skip outright for in-progress/passed trips), discovery stays available on request, since "find me more to do in X" is useful mid-trip.

Re-run on request: "find me more to do in X", or inside the feasibility loop when a targeted swap is needed.

## Inputs to pass the agent

- Path to the plan file
- Preference signals from Step 1 intake and the plan's "Traveler Context": **party** (solo/couple/group/family + kids' ages), **pets** (travelling or staying home), **interests**, **travel-style/pace**, **dietary needs**, **accessibility needs**, **must-do anchors**, **budget**
- Destinations and dates (exact, so events can be date-bounded)
- Path to the `## Sync State` ledger (for dedup)

## Preference signals the agent uses

The agent **filters to the party** — don't surface picks that contradict who's travelling:

| Signal | Effect on candidates |
|---|---|
| Kids' ages | Filter out 21+ / nightlife; flag age-minimum for attractions |
| Accessibility | Filter inaccessible venues; relax pacing suggestions |
| Dietary | Filter incompatible dining; surface suitable alternatives |
| Pets (travelling) | Filter non-pet-friendly venues |
| Interests | Bias toward matching categories; still cast a wide net |
| Pace (relaxed vs packed) | Influences how many candidates per day to surface |
| Budget | Flag above-budget picks as `overBudgetFlag: true`, but still surface |

## Category coverage

Three categories, each broad across price points and styles:

- **Events** — concerts, festivals, sports, exhibitions, markets, seasonal happenings. **Must fall within the trip dates** — never surface an event outside the window.
- **Activities & attractions** — sights, tours, outdoors, neighborhoods, classes, day trips.
- **Dining** — notable spots, local specialties, reservation-worthy places, food markets.

Also surface **public holidays** during the trip as context (they affect crowds, hours, and transport).

## Time-validity capture

For every candidate, the agent captures `openingHours`, `closedDays`, `seasonalWindow`. These are **consumed by the feasibility check** to test whether the plan's timeline actually reaches each stop when it's open. If the agent can't find reliable hours, it notes that; feasibility will flag the uncertainty rather than assume the stop is always open.

## Candidate schema (what the agent returns)

Each candidate carries:

- `name`, `category`, `type`
- `when` — fixed date/time for events; flexible window otherwise
- `where` — a **routable** location (address/place name + city); never "downtown"
- `areaCluster` — sub-area / neighborhood, for day-placement (keeps geo-consistent legs)
- `durationMin`
- `cost` — `{ basis: "total-for-party", amount, priceTier, overBudgetFlag }`
- `indoorOutdoor`, `weatherSensitivity`
- `openingHours`, `closedDays`, `seasonalWindow`
- `reservationNeeded` + `leadTimeDays`; `availabilityUrgency.booksOutLeadDays`
- `requiresGear`, `requiresPermit` (feed the readiness agent)
- `suitability` — `{ minAge, accessible, petFriendly, dietary: [...] }`
- `venueType` (dining) — feasibility's dining enum: `popular sit-down` | `standard` | `casual` | `tasting`
- `whyItFits`, `source`, `confidence`

**Cost basis is always total-for-party** — same basis as the Spending Tracker, so feasibility's budget sum stays consistent.

## Dedup rule

Check the plan body and `## Sync State` before surfacing. Dedup key = **name/vendor + dates** (candidates have no confirmation number or remote ID, so this is the fallback — consistent with sync-protocol.md).

Skip anything matching a `declined`, `untracked`, `cancelled`, or `orphaned` row. A candidate the user deselects at the multi-select is **not** a decline — write **no** Sync State row for an unpicked suggestion (only explicit user rejections get a `declined` row).

**Re-run freshness:** on a "find me more" top-up or a targeted swap re-discovery, exclude candidates already surfaced this session and return genuinely new options.

## Multi-select presentation

The main thread presents candidates via one or more native `AskUserQuestion` (`multiSelect: true`) — one prompt per category (Events / Activities / Dining) as the default; sub-chunk by day or destination when the list is large (more than ~6–8 items per prompt is overwhelming).

Show the key metadata inline so the user can decide without digging: name, why-it-fits, rough cost (over-budget flagged), duration, indoor/outdoor, and whether a reservation is needed / urgency to book.

For each category the user selects items from, add them to the plan via **gate 1** (one confirmation per batch, not per item). Then proceed to the feasibility check.

## How candidates flow downstream

| Candidate type | Effect after selection |
|---|---|
| Fixed-date **event** | Becomes a **fixed anchor** in the day — feasibility respects it; never proposes cutting it |
| **Activity** (timed entry) | Slot on the appropriate day; `reservationNeeded` + `availabilityUrgency.booksOutLeadDays` → Task Step 6 |
| **Dining** pick | Feeds feasibility's meal-time math via `venueType` + `where` (for detour calc) |
| Any with `requiresGear`/`requiresPermit` | Fed to the readiness agent (Step 4) → packing / permit task |
| Any with high `availabilityUrgency` (books out far ahead) | Flags as an early task in Step 6 (separate from a same-day reservation) |

**Reservation tasks** (booking a restaurant, buying a ticket) flow to **Step 6 Tasks** directly — they are not Readiness items. Readiness covers preparedness (visa, packing, insurance), not activity booking.

## Budget handling

Surface above-budget picks but flag them clearly (`overBudgetFlag: true` + the over-by amount). Don't silently omit splurge options — the user may choose to accept the overrun, especially for a must-do anchor. Feasibility's `budget-risk` flag catches trip-level overruns after selection.

## Targeted re-discovery (inside the feasibility loop)

When the feasibility check flags a conflict (weather/budget/over-packed) on an item the user selected, the main thread may re-invoke discovery for a targeted swap. Pass to the agent:

- **Scope**: the day and category of the conflict
- **Constraints to preserve**: the clean flags that must remain satisfied (e.g. "indoor, total ≤ $X for party, ≤ 90 min, in area Y")

The agent returns only candidates that satisfy every passed constraint and excludes anything already surfaced. The main thread caps re-discovery at **two rounds**, then presents an AskUserQuestion with: *Apply this swap / Find different options / Accept as-is and proceed*. "Accept as-is" is always offered from round 1.
