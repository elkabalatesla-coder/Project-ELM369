/** All payout helpers return GROSS stake-inclusive multipliers, not net odds. */
export const casinoOdds = Object.freeze({
  blackjack: Object.freeze({ theoreticalRTP: null,
    assumptions: 'Basic strategy: 4–8 decks, dealer stands on soft 17, double after split, no surrender, peek. No strategy RTP calculated. Pair splitting assumes DAS.' }),
  roulette: Object.freeze({ europeanHouseEdge: 1 / 37, americanHouseEdge: 2 / 38,
    assumptions: 'Standard single/double-zero rules, no la partage/en prison. American five-number basket has 3/38 house edge.' }),
  craps: Object.freeze({ passHouseEdge: 7 / 495, dontPassHouseEdge: 3 / 220,
    assumptions: "Don't pass pushes on come-out 12. Odds bets pay true odds, separate from flat line bet." }),
  keno: Object.freeze({ theoreticalRTP: null, assumptions: 'Uniform draws without replacement. Return depends on the supplied gross paytable.' }),
});

function rank(card) {
  if (Number.isInteger(card) && card >= 0 && card < 52) return card % 13 + 2;
  if (typeof card === 'string') {
    const ranks = { A: 14, K: 13, Q: 12, J: 11, T: 10 };
    const text = card.toUpperCase();
    if (Object.hasOwn(ranks, text)) return ranks[text];
    if (/^(?:[2-9]|10)$/.test(text)) return Number(text);
  }
  throw new RangeError('card must be an integer 0..51 or a rank string 2..10/J/Q/K/A');
}
function checkedHand(cards) {
  if (!Array.isArray(cards) || cards.length < 1) throw new RangeError('cards must be a nonempty array');
  return Array.from(cards, rank);
}

/** Integer deck cards or rank strings; ace is 11 unless reducing to 1 is needed. */
export function blackjackValue(cards) {
  const ranks = checkedHand(cards);
  let total = 0, aces = 0;
  for (const r of ranks) {
    total += r === 14 ? 11 : Math.min(r, 10);
    if (r === 14) aces++;
  }
  while (total > 21 && aces > 0) { total -= 10; aces--; }
  return { total, soft: aces > 0, bust: total > 21 };
}

/** S17 multi-deck, DAS, no-surrender table. Returns hit/stand/double/split.
 * canDouble/canSplit must reflect table legality, split limits and bankroll.
 * Dealer is ONE card, not a numeric blackjack value: use "6" for rank six.
 */
export function basicStrategy(hand, dealer, { canDouble = true, canSplit = true } = {}) {
  const ranks = checkedHand(hand);
  if (typeof canDouble !== 'boolean' || typeof canSplit !== 'boolean') throw new TypeError('strategy flags must be boolean');
  const up = rank(dealer), d = up === 14 ? 11 : Math.min(up, 10);
  const { total, soft, bust } = blackjackValue(hand);
  if (bust || total >= 21) return 'stand';
  const two = hand.length === 2, double = canDouble && two;
  const dh = () => double ? 'double' : 'hit';
  if (two && canSplit && ranks[0] === ranks[1]) {
    const r = ranks[0];
    if (r === 14 || r === 8) return 'split';
    if (r === 9 && (d <= 6 || d === 8 || d === 9)) return 'split';
    if (r === 7 && d <= 7) return 'split';
    if (r === 6 && d <= 6) return 'split';
    if (r === 4 && (d === 5 || d === 6)) return 'split';
    if ((r === 2 || r === 3) && d <= 7) return 'split';
  }
  if (soft) {
    if (total >= 19) return 'stand';
    if (total === 18) {
      if (d >= 3 && d <= 6) return double ? 'double' : 'stand';
      return d <= 8 ? 'stand' : 'hit';
    }
    if (total === 17) return d >= 3 && d <= 6 ? dh() : 'hit';
    if (total === 15 || total === 16) return d >= 4 && d <= 6 ? dh() : 'hit';
    return d === 5 || d === 6 ? dh() : 'hit';
  }
  if (total >= 17) return 'stand';
  if (total >= 13) return d <= 6 ? 'stand' : 'hit';
  if (total === 12) return d >= 4 && d <= 6 ? 'stand' : 'hit';
  if (total === 11) return d !== 11 ? dh() : 'hit';
  if (total === 10) return d <= 9 ? dh() : 'hit';
  if (total === 9) return d >= 3 && d <= 6 ? dh() : 'hit';
  return 'hit';
}

const roulette = Object.freeze({
  straight: 36, split: 18, street: 12, corner: 9, sixLine: 6,
  dozen: 3, column: 3, red: 2, black: 2, odd: 2, even: 2,
  low: 2, high: 2, basket: 7,
});
export function roulettePayout(betType, hit, american = false) {
  if (!Object.hasOwn(roulette, betType)) throw new RangeError('unknown roulette bet type');
  if (typeof hit !== 'boolean' || typeof american !== 'boolean') throw new TypeError('hit and american must be boolean');
  if (betType === 'basket' && !american) throw new RangeError('five-number basket requires American roulette');
  return hit ? roulette[betType] : 0;
}

const points = [4, 5, 6, 8, 9, 10];
function checkPoint(point) {
  if (!points.includes(point)) throw new RangeError('point must be 4, 5, 6, 8, 9 or 10');
}
/** Resolved bets only. outcome is win/lose/push. Odds require a valid point.
 * passOdds gross: 3, 2.5, 2.2; dontOdds gross: 1.5, 5/3, 11/6.
 */
export function crapsPayout(betType, outcome, point = null) {
  if (!['pass', 'dontPass', 'passOdds', 'dontOdds'].includes(betType)) throw new RangeError('unknown craps bet type');
  if (!['win', 'lose', 'push'].includes(outcome)) throw new RangeError('outcome must be win, lose or push');
  if (betType.endsWith('Odds')) checkPoint(point);
  if (outcome === 'lose') return 0;
  if (outcome === 'push') return 1;
  if (betType === 'pass' || betType === 'dontPass') return 2;
  const odds = point === 4 || point === 10 ? 2 : point === 5 || point === 9 ? 1.5 : 1.2;
  return 1 + (betType === 'passOdds' ? odds : 1 / odds);
}

/** Resolve one roll; null point is come-out. Returns the next point and statuses.
 * Statuses are win/lose/push/pending; use crapsPayout only on resolved bets.
 */
export function resolveCraps(roll, point = null) {
  if (!Number.isInteger(roll) || roll < 2 || roll > 12) throw new RangeError('roll must be an integer 2..12');
  if (point !== null) checkPoint(point);
  if (point === null) {
    if (roll === 7 || roll === 11) return { point: null, pass: 'win', dontPass: 'lose' };
    if (roll === 2 || roll === 3) return { point: null, pass: 'lose', dontPass: 'win' };
    if (roll === 12) return { point: null, pass: 'lose', dontPass: 'push' };
    return { point: roll, pass: 'pending', dontPass: 'pending' };
  }
  if (roll === point) return { point: null, pass: 'win', dontPass: 'lose' };
  if (roll === 7) return { point: null, pass: 'lose', dontPass: 'win' };
  return { point, pass: 'pending', dontPass: 'pending' };
}
export const crapsResolution = resolveCraps;

function nonnegativeInteger(n, name) {
  if (!Number.isSafeInteger(n) || n < 0) throw new RangeError(`${name} must be a nonnegative safe integer`);
}
/** Natural logarithm of n choose k; impossible k gives -Infinity. */
export function logChoose(n, k) {
  nonnegativeInteger(n, 'n');
  if (!Number.isSafeInteger(k)) throw new RangeError('k must be a safe integer');
  if (k < 0 || k > n) return -Infinity;
  k = Math.min(k, n - k);
  let result = 0;
  for (let i = 1; i <= k; i++) result += Math.log((n - k + i) / i);
  return result;
}
function kenoArgs(picks, drawn, population) {
  nonnegativeInteger(population, 'population');
  nonnegativeInteger(picks, 'picks');
  nonnegativeInteger(drawn, 'drawn');
  if (picks > population || drawn > population) throw new RangeError('picks and drawn cannot exceed population');
}
/** Hypergeometric probability of exactly hits; impossible hits have probability 0. */
export function kenoProbability(picks, hits, drawn = 20, population = 80) {
  kenoArgs(picks, drawn, population);
  if (!Number.isSafeInteger(hits)) throw new RangeError('hits must be an integer');
  if (hits < 0 || hits > picks || hits > drawn || drawn - hits > population - picks) return 0;
  const probability = Math.exp(logChoose(picks, hits) +
    logChoose(population - picks, drawn - hits) - logChoose(population, drawn));
  return Math.min(1, probability);
}
/** paytable maps hits -> GROSS multiplier (including stake); omitted hits pay 0. */
export function kenoExpectedReturn(picks, paytable, drawn = 20, population = 80) {
  kenoArgs(picks, drawn, population);
  if (!paytable || typeof paytable !== 'object' || Array.isArray(paytable)) throw new TypeError('paytable must map hit counts to gross payouts');
  let ev = 0;
  for (const [hits, pay] of Object.entries(paytable)) {
    if (!/^(0|[1-9]\d*)$/.test(hits) || !Number.isSafeInteger(Number(hits)) ||
        Number(hits) > picks || !Number.isFinite(pay) || pay < 0) throw new RangeError('invalid keno paytable');
    ev += kenoProbability(picks, Number(hits), drawn, population) * pay;
  }
  return ev;
}
