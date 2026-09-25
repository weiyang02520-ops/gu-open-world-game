# M5 Economy and Logistics

M5 extends the M1 `ResourceLot`, `ResourceNode`, `LocalMarket`, `WorldClock`,
and durable event log instead of creating a second inventory authority.

## State

- 20 finite nodes keep stock, capacity, health, environmental modifier,
  controller, contest state, infrastructure, and workers.
- Three local markets have independent finite lots, currencies, demand, and
  price adjustments. A market quote is derived from its own stock/demand.
- Six directed routes expose travel time and stateful risk from combat,
  criminal activity, shortage pressure, patrols, faction control, and guards.
- `Shipment` owns actual `ResourceLot` cargo. Dispatch removes lots from the
  origin immediately; success adds them to the destination or a faction
  warehouse; loss destroys the cargo and leaves a shortage.
- `Caravan` is the route/security record for each shipment. Faction economies
  track treasury, reserves, warehouse lots, procurement orders, and shortage
  intensity.

## Causality

Overharvest reduces node health and future yield. Finite stock changes local
prices, creates shortages, changes NPC goals, raises route pressure, and can
trigger faction procurement. Market rumors only mutate a receiver's
`MarketBelief`; they never create physical stock.

## Persistence

The layer serializes under `WorldState.game_state["m5_economy"]`, including
in-transit cargo, route state, beliefs, shortages, goals, and trade history.
`EconomyLogisticsEngine.load` restores the same deterministic RNG and event
log, so resolving a saved in-transit shipment follows the same result.
