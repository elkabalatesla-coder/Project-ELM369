# Paytables, RTP, and limitations

**Virtual credits only.** RTP is a long-run expected **gross return / wager**,
not the probability of winning a session. Above-100% illustrative schedules
are allowed because no credits can be bought or redeemed. All displayed
paytables are authoritative for this simulation; commercial games can use
different schedules.

## Poker

The full schedules are exported by `math/poker.mjs::PAYTABLES` and displayed
in each video-poker game. Royal flush pays **800 per credit at the modeled
maximum-credit schedule**, including when this simulation uses a one-credit
unit; there is no separate reduced-royal minimum-coin schedule.

| Variant | Schedule identifier / distinguishing gross awards | RTP disclosure |
|---|---|---|
| Jacks or Better | 9 full house / 6 flush; 25 quads, 50 straight flush, 800 royal | Full-pay optimal-strategy reference: about **99.5439%** |
| Deuces Wild | 800 natural royal, 200 four deuces, 25 wild royal, 15 five-kind, 9 straight flush, 5 quads, 3 full house, 2 flush/straight, 1 trips | Full-pay optimal-strategy reference: about **100.762%** |
| Bonus Poker | 8/5; quads A=80, 2–4=40, 5–K=25 | Strategy-dependent; not globally calculated |
| Double Bonus | 10/7/5; quads A=160, 2–4=80, 5–K=50; two pair=1 | Strategy-dependent; not globally calculated |
| Double Double Bonus | 9/6; special low-kicker quad awards | Strategy-dependent; not globally calculated |
| Joker Poker | 53-card Kings-or-Better schedule; five-kind=200 | Strategy-dependent; not globally calculated |
| Tens or Better | 6/5; qualifying pair begins at tens | Strategy-dependent; not globally calculated |
| All American | See explicit in-game schedule | Strategy-dependent; not globally calculated |
| 3/5/10-hand | Jacks or Better schedule; one wager per hand | Same per-unit expectation for the same hold policy; correlated outcomes change variance |
| Future Multiplier | House-rule future-hand multiplier, not commercial Ultimate X | Not calculated; base-game RTP does **not** apply |

Reference figures are not outputs of the local test suite or certifications.
They assume optimal holds, uniform independent deals and the exact full-pay
maximum-credit schedules. The exact hold solver computes per-hand EV, not
a proof of either global benchmark. Other variants explicitly show “not
calculated” rather than invented RTP numbers.

Reference locations for independent checking:

* <https://wizardofodds.com/games/video-poker/tables/jacks-or-better/>
* <https://wizardofodds.com/games/video-poker/tables/deuces-wild/>

External source retrieval was unavailable during implementation; the URLs are
reference pointers, not a claim of a live source audit.

## Slots

Both example models use 12 stops per reel, three visible rows, five equally
wagered lines, no wild/scatter/bonus, and left-to-right longest-match awards.
Every stop combination is enumerated by `exactSlotsRTP`:

| Model | Equiprobable stop combinations | Displayed theoretical return |
|---|---:|---|
| Three reels | 12³ = 1,728 | Computed directly from installed strips/paylines/paytable |
| Five reels | 12⁵ = 248,832 | Computed directly from installed strips/paylines/paytable |

Symbol awards for 3 / 4 / 5 matches: CHERRY 4/10/25, LEMON 2/5/12,
BELL 8/20/60, BAR 12/40/120, SEVEN 30/100/500. The application shows exact
RTP when opening the game; it does not substitute a Monte Carlo estimate.
Simulation hit rate and volatility concern complete spins across all lines.

## Minimal table and reveal games

| Game/rules | Theoretical gross return |
|---|---|
| European straight-number roulette, gross 36× | 36/37 ≈ 97.2973% |
| American straight-number roulette, gross 36× | 36/38 ≈ 94.7368% |
| Craps pass-line, gross win 2× | 488/495 ≈ 98.5859% |
| Five-pick keno, 20 of 80 drawn | Computed from hypergeometric odds and displayed awards (3 hits=2×, 4=10×, 5=100×) |
| Scratch, 3 equal symbols from 6, gross 20× | 20/36 ≈ 55.5556% |
| Player-bet baccarat | Standard third-card drawing; no strategy choice; no locally enumerated global RTP |
| Minimal blackjack | Even-money naturals; no double/split/insurance; no calculated policy RTP |

The blackjack strategy library covers a richer ruleset than the prototype.
No standard 3:2 blackjack return is advertised for this simplified game.
Roulette side bets, baccarat Banker/Tie bets, craps odds/side bets, commercial
slot bonuses, and commercial multiplier-poker schedules remain extension work.
