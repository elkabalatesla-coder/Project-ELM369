import { deck } from './rng.mjs';

const freezeTable = table => Object.freeze({ nothing: 0, ...table });
const standard = { royalFlush: 800, straightFlush: 50, fourKind: 25, fullHouse: 9,
  flush: 6, straight: 4, threeKind: 3, twoPair: 2, jacksOrBetter: 1 };

/** Gross credits per credit wagered, normalized to maximum-credit schedules.
 * Royal 800 applies linearly to EVERY bet amount in this model; physical-machine
 * reduced royal awards at lower credit counts are NOT modeled.
 * These are explicit schedules, not a promise of a particular strategy RTP.
 */
export const PAYTABLES = Object.freeze({
  jacks: freezeTable(standard),
  tens: freezeTable({ ...standard, fullHouse: 6, flush: 5, jacksOrBetter: 0, tensOrBetter: 1 }),
  bonus: freezeTable({ ...standard, fullHouse: 8, flush: 5,
    fourAces: 80, four234: 40, four5K: 25 }),
  doubleBonus: freezeTable({ ...standard, fullHouse: 10, flush: 7, straight: 5, twoPair: 1,
    fourAces: 160, four234: 80, four5K: 50 }),
  doubleDoubleBonus: freezeTable({ ...standard, fullHouse: 9, flush: 6, twoPair: 1,
    fourAcesLowKicker: 400, four234LowKicker: 160, fourAces: 160, four234: 80, four5K: 50 }),
  acesFaces: freezeTable({ ...standard, fullHouse: 8, flush: 5,
    fourAces: 80, fourFaces: 40, fourKind: 25 }),
  allAmerican: freezeTable({ ...standard, straightFlush: 200, fourKind: 40,
    fullHouse: 8, flush: 8, straight: 8, twoPair: 1 }),
  deuces: freezeTable({ royalFlush: 800, fourDeuces: 200, wildRoyal: 25, fiveKind: 15,
    straightFlush: 9, fourKind: 5, fullHouse: 3, flush: 2, straight: 2, threeKind: 1 }),
  joker: freezeTable({ royalFlush: 800, fiveKind: 200, wildRoyal: 100,
    straightFlush: 50, fourKind: 20, fullHouse: 7, flush: 5, straight: 3,
    threeKind: 2, twoPair: 1, kingsOrBetter: 1 }),
});

export const pokerVariants = Object.freeze(Object.entries(PAYTABLES).map(([id, paytable]) =>
  Object.freeze({ id, name: ({
    jacks: 'Jacks or Better (9/6)', tens: 'Tens or Better (6/5)',
    bonus: 'Bonus Poker (8/5)', doubleBonus: 'Double Bonus (10/7)',
    doubleDoubleBonus: 'Double Double Bonus (9/6)', acesFaces: 'Aces and Faces (8/5)',
    allAmerican: 'All American (8/8/8)',
    deuces: 'Deuces Wild (full pay)', joker: 'Joker Poker (Kings or Better)',
  })[id], paytable, deckSize: id === 'joker' ? 53 : 52,
  theoreticalRTP: id === 'jacks' ? 0.995439 : id === 'deuces' ? 1.00762 : null,
  rtpProvenance: id === 'jacks' || id === 'deuces' ? 'Published optimal-strategy reference, rounded; NOT a local calculation.' : null,
  rtpReference: id === 'jacks'
    ? 'https://wizardofodds.com/games/video-poker/tables/jacks-or-better/'
    : id === 'deuces' ? 'https://wizardofodds.com/games/video-poker/tables/deuces-wild/' : null,
  assumptions: 'Normalized maximum-credit paytable: royal pays 800 per credit at EVERY bet size. Physical-machine reduced royal awards at lower credit counts are not modeled. Any reference RTP assumes perfect optimal strategy, uniform independent deals and the exact listed paytable; actual player RTP can differ.' })));

const aliases = Object.freeze({ 'jacks-or-better': 'jacks', 'deuces-wild': 'deuces',
  'double-bonus': 'doubleBonus', 'double-double-bonus': 'doubleDoubleBonus',
  'aces-and-faces': 'acesFaces', 'all-american': 'allAmerican', 'joker-poker': 'joker' });
function variantId(variant) {
  const id = Object.hasOwn(aliases, variant) ? aliases[variant] : variant;
  if (!Object.hasOwn(PAYTABLES, id)) throw new RangeError(`Unknown poker variant: ${variant}`);
  return id;
}
function validateHand(hand, variant) {
  const max = variant === 'joker' ? 52 : 51;
  if (!Array.isArray(hand) || hand.length !== 5 ||
      Array.from(hand).some(c => !Number.isInteger(c) || c < 0 || c > max) || new Set(hand).size !== 5) {
    throw new RangeError(`hand must contain five distinct integer cards in 0..${max}`);
  }
}

const straightMasks = [0x100f, ...Array.from({ length: 9 }, (_, i) => 31 << i)];
const royalMask = 31 << 8;
function wildCategory(hand, variant) {
  const counts = new Uint8Array(15);
  let wild = 0, mask = 0, suit = -1, flush = true, naturalCount = 0;
  for (const c of hand) {
    const rank = c % 13 + 2;
    if (c === 52 || (variant === 'deuces' && rank === 2)) { wild++; continue; }
    counts[rank]++;
    mask |= 1 << (rank - 2);
    const s = Math.floor(c / 13);
    if (suit !== -1 && suit !== s) flush = false;
    suit = s;
    naturalCount++;
  }
  if (!wild && flush && mask === royalMask) return 'royalFlush';
  if (variant === 'deuces' && wild === 4) return 'fourDeuces';
  if (flush && (mask & royalMask) === mask) return 'wildRoyal';
  let largest = 0, second = 0, distinct = 0, pairRank = 0;
  for (let r = 2; r <= 14; r++) {
    const n = counts[r];
    if (n) distinct++;
    if (n >= 2) pairRank = r;
    if (n > largest) { second = largest; largest = n; }
    else if (n > second) second = n;
  }
  if (largest + wild >= 5) return 'fiveKind';
  const straight = distinct === naturalCount &&
    straightMasks.some(target => (mask & target) === mask);
  if (flush && straight) return 'straightFlush';
  if (largest + wild >= 4) return 'fourKind';
  // Allocate wild cards to the two rank groups, not to 52^wild concrete cards.
  if (distinct <= 2 && Math.max(0, 3 - largest) + Math.max(0, 2 - second) <= wild) return 'fullHouse';
  if (flush) return 'flush';
  if (straight) return 'straight';
  if (largest + wild >= 3) return 'threeKind';
  if (variant === 'joker' && largest >= 2 && second + wild >= 2) return 'twoPair';
  if (variant === 'joker' && ((wild && (counts[13] || counts[14])) ||
      (largest === 2 && pairRank >= 13))) return 'kingsOrBetter';
  return 'nothing';
}

function naturalCategory(hand, variant) {
  const counts = new Uint8Array(15);
  let mask = 0, flush = true;
  const suit = Math.floor(hand[0] / 13);
  for (const c of hand) {
    const rank = c % 13 + 2;
    counts[rank]++;
    mask |= 1 << (rank - 2);
    if (Math.floor(c / 13) !== suit) flush = false;
  }
  const straight = straightMasks.includes(mask);
  if (flush && mask === royalMask) return 'royalFlush';
  if (flush && straight) return 'straightFlush';
  let four = 0, three = 0, pairs = 0, pairRank = 0, kicker = 0;
  for (let r = 2; r <= 14; r++) {
    if (counts[r] === 4) four = r;
    else if (counts[r] === 3) three = r;
    else if (counts[r] === 2) { pairs++; pairRank = r; }
    else if (counts[r] === 1) kicker = r;
  }
  if (four) {
    if (variant === 'acesFaces') return four === 14 ? 'fourAces' : four >= 11 ? 'fourFaces' : 'fourKind';
    if (['bonus', 'doubleBonus', 'doubleDoubleBonus'].includes(variant)) {
      if (variant === 'doubleDoubleBonus') {
        if (four === 14 && kicker >= 2 && kicker <= 4) return 'fourAcesLowKicker';
        if (four >= 2 && four <= 4 && (kicker === 14 || kicker <= 4)) return 'four234LowKicker';
      }
      return four === 14 ? 'fourAces' : four <= 4 ? 'four234' : 'four5K';
    }
    return 'fourKind';
  }
  if (three && pairs) return 'fullHouse';
  if (flush) return 'flush';
  if (straight) return 'straight';
  if (three) return 'threeKind';
  if (pairs === 2) return 'twoPair';
  if (pairs && pairRank >= (variant === 'tens' ? 10 : 11)) {
    return variant === 'tens' ? 'tensOrBetter' : 'jacksOrBetter';
  }
  return 'nothing';
}

const category = (hand, variant) => variant === 'deuces' || variant === 'joker'
  ? wildCategory(hand, variant) : naturalCategory(hand, variant);

/** Cards 0..51, plus card 52 (joker) only in the joker variant. */
export function evaluate(hand, variant = 'jacks') {
  variant = variantId(variant);
  validateHand(hand, variant);
  return category(hand, variant);
}

/** Gross return, not net profit. All multipliers apply linearly to every bet,
 * including the maximum-credit-normalized 800 royal; no credit-count adjustment.
 */
export function payout(hand, variant = 'jacks', bet = 1) {
  variant = variantId(variant);
  if (!Number.isFinite(bet) || bet < 0) throw new RangeError('bet must be finite and nonnegative');
  const gross = PAYTABLES[variant][evaluate(hand, variant)] * bet;
  if (!Number.isFinite(gross)) throw new RangeError('payout overflowed');
  return gross;
}

function holdMask(hold) {
  if (Number.isInteger(hold) && hold >= 0 && hold < 32) return hold;
  if (!Array.isArray(hold) || new Set(hold).size !== hold.length ||
      Array.from(hold).some(i => !Number.isInteger(i) || i < 0 || i > 4)) {
    throw new RangeError('hold must be a mask 0..31 or distinct card indices 0..4');
  }
  return hold.reduce((mask, index) => mask | (1 << index), 0);
}

function prepared(hand, variant) {
  const remaining = deck();
  if (variant === 'joker') remaining.push(52);
  return remaining.filter(c => !hand.includes(c));
}

function drawEV(hand, mask, variant, remaining) {
  const cards = hand.filter((_, i) => mask & (1 << i));
  const held = cards.length, needed = 5 - held;
  const table = PAYTABLES[variant];
  let sum = 0, outcomes = 0;
  function visit(start, depth) {
    if (depth === needed) {
      sum += table[category(cards, variant)];
      outcomes++;
      return;
    }
    for (let i = start; i <= remaining.length - (needed - depth); i++) {
      cards[held + depth] = remaining[i];
      visit(i + 1, depth + 1);
    }
  }
  visit(0, 0);
  return { mask, hold: hand.flatMap((_, i) => mask & (1 << i) ? [i] : []),
    ev: sum / outcomes, outcomes };
}

/** Exact gross expected credits for a specified hold; discarded cards cannot return. */
export function handEV(hand, hold, variant = 'jacks') {
  variant = variantId(variant);
  validateHand(hand, variant);
  return drawEV(hand, holdMask(hold), variant, prepared(hand, variant)).ev;
}

/** Exact enumeration of EVERY hold and possible replacement combination.
 * Synchronous and expensive (~2.6 million final hands for a 52-card deck).
 * Run in a worker for interactive UIs. Never substitutes sampled strategy.
 * options.onProgress(result) is called once per hold; options.signal can cancel.
 * Returns {hold: indices, mask, ev, results: all 32 hold results, exact: true}.
 */
export function optimalHolds(hand, variant = 'jacks', options = {}) {
  variant = variantId(variant);
  validateHand(hand, variant);
  if (!options || typeof options !== 'object') throw new TypeError('options must be an object');
  if (options.onProgress !== undefined && typeof options.onProgress !== 'function') {
    throw new TypeError('onProgress must be a function');
  }
  const remaining = prepared(hand, variant), results = [];
  let best;
  for (let mask = 0; mask < 32; mask++) {
    if (options.signal?.aborted) throw new Error('Poker calculation aborted');
    const result = drawEV(hand, mask, variant, remaining);
    results.push(result);
    if (!best || result.ev > best.ev ||
        (result.ev === best.ev && result.hold.length > best.hold.length)) best = result;
    options.onProgress?.({ ...result, hold: result.hold.slice() });
  }
  return { ...best, hold: best.hold.slice(), results, exact: true };
}

/** Exact strategy RTP, NOT the conditional EV of one starting hand.
 * Exhausts EVERY uniformly dealt five-card starting hand and EVERY subsequent
 * draw for the chosen hold. Floating-point roundoff still applies.
 *
 * options.strategy(hand, variant) returns a mask, index array, or {hold: indices}.
 * If omitted, EVERY starting hand runs optimalHolds: trillions of final hands.
 * This can take days or longer; use a worker and cancellation, never the UI thread.
 * No sampling, prefix truncation, or published reference replaces this calculation.
 * options.signal cancels between deals; onProgress({hands,totalHands}) is called
 * every options.progressEvery deals (default 1000) and after the final deal.
 */
export function strategyRTP(variant = 'jacks', options = {}) {
  variant = variantId(variant);
  if (!options || typeof options !== 'object') throw new TypeError('options must be an object');
  const { strategy, onProgress, signal, progressEvery = 1000 } = options;
  if (strategy !== undefined && typeof strategy !== 'function') throw new TypeError('strategy must be a function');
  if (onProgress !== undefined && typeof onProgress !== 'function') throw new TypeError('onProgress must be a function');
  if (!Number.isSafeInteger(progressEvery) || progressEvery < 1) throw new RangeError('progressEvery must be a positive integer');
  const cards = deck();
  if (variant === 'joker') cards.push(52);
  const n = cards.length;
  const totalHands = n * (n - 1) * (n - 2) * (n - 3) * (n - 4) / 120;
  const hand = Array(5);
  let hands = 0, sum = 0, compensation = 0;
  function visit(start, depth) {
    if (signal?.aborted) throw new Error('Strategy RTP calculation aborted');
    if (depth === 5) {
      let ev;
      if (strategy) {
        const decision = strategy(hand.slice(), variant);
        const mask = holdMask(decision && typeof decision === 'object' && !Array.isArray(decision)
          ? decision.hold : decision);
        ev = mask === 31 ? PAYTABLES[variant][category(hand, variant)]
          : drawEV(hand, mask, variant, prepared(hand, variant)).ev;
      } else {
        ev = optimalHolds(hand, variant, { signal }).ev;
      }
      // Compensated summation limits accumulated error across millions of deals.
      const adjusted = ev - compensation;
      const next = sum + adjusted;
      compensation = (next - sum) - adjusted;
      sum = next;
      hands++;
      if (hands % progressEvery === 0 || hands === totalHands) onProgress?.({ hands, totalHands });
      return;
    }
    for (let i = start; i <= n - (5 - depth); i++) {
      hand[depth] = cards[i];
      visit(i + 1, depth + 1);
    }
  }
  visit(0, 0);
  return { rtp: sum / hands, hands, totalHands, exact: true,
    strategy: strategy ? 'provided' : 'optimal',
    assumptions: 'Every uniform starting deal and every replacement draw enumerated; gross return per credit, maximum-credit-normalized royal 800 at every stake; floating-point arithmetic.' };
}
