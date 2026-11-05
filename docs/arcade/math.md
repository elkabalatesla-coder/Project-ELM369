# Algorithms and numerical conventions

All algorithms live in `tools/elm_arcade/math/`; tests execute those browser
modules directly under Node. Credits/payouts mean **gross return**, including a
returned stake where applicable. A losing wager returns zero, not minus one.

## Randomness and cards

`SecureRNG.int(n)` rejection-samples a 32-bit Web Crypto value below
`floor(2^32/n)*n`, then reduces modulo `n`. This avoids modulo bias. It refuses
missing cryptographic entropy rather than falling back to `Math.random()`.
`SeededRNG` is Mulberry32 with the same bounded-integer contract for repeatable
tests, simulations, and arcade replays; it is not cryptographic.

Fisher–Yates shuffles a copy, swapping each position `i` with a uniformly
selected `0..i`. A deck is integer cards `0..51`: rank is `card % 13 + 2`,
suit is `floor(card/13)`. Ace is rank 14, with A2345 handled as a wheel.
Joker Poker alone adds card 52. Rejected hands include duplicates and
out-of-range cards.

## Poker and exact holds

The evaluator uses rank counts, suit comparison, and 13-bit straight masks.
Deuces Wild removes deuces into a wild count, then tests feasible rank groups,
flush/straight masks, wild royals, five of a kind, and four-deuce precedence.
Joker evaluation follows its own pay schedule. This avoids substituting
every possible concrete card for every wild.

`handEV(hand, hold, variant)` enumerates unordered replacement combinations
from the deck excluding **all five original cards**, including discards.
`optimalHolds(hand, variant)` evaluates all 32 masks:

```
EV(H) = sum(gross payout of H + draw) / C(deckSize - 5, 5 - |H|)
```

The best hold maximizes expected **gross credits per credit wagered**. Across
all 32 masks, a standard hand requires 2,598,960 evaluated outcomes, so the
browser runs this work in a cancellable worker. Ties are not a claim of a
unique strategy. This is exact enumeration, not a sampled “optimal” hint.

Whole-game RTP additionally weights the player policy over all initial
hands. One hand's best EV is **not** the game's RTP. Full global optimal
enumeration is expensive; no ordinary simulation or finite session should
be labeled a proof of optimal RTP. Published benchmark figures are identified
separately in [the tables](rtp.md).

`strategyRTP(variant, {strategy, onProgress, signal})` exhausts every initial
deal and the replacement draws for its chosen hold; with no policy it calls
the optimal solver for every deal. This can take days or longer and is an
offline research API, not a launcher action. It never labels a prefix/sample
as exact. Tests verify the tractable hold-all policy over all 2,598,960 deals.

## Slots

Each reel has an explicit circular symbol strip. A stop is uniformly sampled
independently per reel; the visible grid has three consecutive rows. Paylines
choose one row per reel and pay the longest matching left-to-right run,
once per line. Stake is **per line**:

```
total stake = stake per line × number of active lines
RTP = expected sum of gross line returns / total stake
```

`exactSlotsRTP` enumerates the product of the strip lengths and refuses models
over its outcome bound instead of freezing on unbounded input. Correlation
between paylines does not invalidate summing returns, but it matters for
volatility. `simulateSlots` estimates return and spread from sampled complete
spins, rather than pretending line wins are independent.

Simulation uses Welford sample variance of gross return divided by the
total per-spin wager. Results include `variance`, `stddev`/`volatility`,
`standardError`, and an approximate normal 95% `confidenceInterval`; a
single spin has no estimated uncertainty. Exact enumeration reports population
variance and zero sampling error. Rare wins can make short-run normal intervals
unreliable; they are not payout guarantees or proof of agreement with theory.

## Other casino math

* Blackjack reduces aces from 11 to 1 as needed. The basic-strategy helper
  documents multi-deck, stand-on-soft-17, double-after-split, no-surrender,
  peek assumptions. Its table supports legality flags for double/split.
  The **minimal playable blackjack** has fewer actions and an even-money
  natural; do not apply a standard blackjack RTP to it.
* Roulette helpers provide gross multipliers. Single zero is 37 pockets;
  double zero is 38. American five-number basket has a different edge.
* Craps separates come-out and point resolution, flat line bets, and true-
  odds returns. Don't-pass pushes on come-out 12. The playable prototype
  exposes pass-line only and saves a pending point/stake.
* Keno draws without replacement. For `N` numbers, `D` drawn, `P` picks:

```
Pr(h hits) = exp(log C(P,h) + log C(N-P,D-h) - log C(N,D))
```

  `logChoose` sums logarithms rather than constructing factorials. Impossible
  outcomes have probability zero; expected gross return is the dot product
  of hit probabilities and the actual paytable.

## Arcade math

The shared library supplies AABB and circle overlap, separating-axis tests
for convex polygons, velocity/position integration, and grid A* search.
SAT checks edge normals from **both** polygons. A* uses a Manhattan heuristic
for four-neighbor movement and does not cross blocked tiles. Maze enemies
use this pathfinding rather than moving through walls.

Difficulty combines bounded logarithmic/exponential curves to increase speed,
spawn pressure, and score values without unbounded time-step growth. Score
multipliers scale streak rewards; collision/timestep subdivision in the brick
breaker reduces tunneling. These are arcade approximations, not a general
rigid-body physics solver.

Arcade snapshots additionally persist an internal LCG stream, seeded once
through the injected RNG, to resume exactly without needing to serialize a
browser cryptographic generator. Casino games do not use this stream.
