import { SecureRNG } from './rng.mjs';

const reel = symbols => Object.freeze(symbols.split(' '));
/** Illustrative, transparent reel strips; not a commercial machine's math. */
export const REELS3 = Object.freeze([
  reel('CHERRY LEMON BELL LEMON SEVEN CHERRY BAR LEMON CHERRY BELL LEMON BAR'),
  reel('LEMON CHERRY BAR BELL LEMON SEVEN CHERRY LEMON BELL BAR LEMON CHERRY'),
  reel('BELL LEMON CHERRY BAR CHERRY LEMON SEVEN BELL LEMON CHERRY BAR LEMON'),
]);
export const REELS5 = Object.freeze([...REELS3, REELS3[1], REELS3[0]]);
export const PAYLINES = Object.freeze([
  [1, 1, 1], [0, 0, 0], [2, 2, 2], [0, 1, 2], [2, 1, 0],
].map(Object.freeze));
export const PAYLINES5 = Object.freeze([
  [1, 1, 1, 1, 1], [0, 0, 0, 0, 0], [2, 2, 2, 2, 2],
  [0, 1, 2, 1, 0], [2, 1, 0, 1, 2],
].map(Object.freeze));
export const SLOT_PAYS = Object.freeze(Object.fromEntries(
  Object.entries({ CHERRY: [4, 10, 25], LEMON: [2, 5, 12], BELL: [8, 20, 60],
    BAR: [12, 40, 120], SEVEN: [30, 100, 500] })
    .map(([symbol, amounts]) => [symbol, Object.freeze({ 3: amounts[0], 4: amounts[1], 5: amounts[2] })])));
export const slotOdds = Object.freeze({
  assumptions: 'Independent uniform reel stops; three circular visible rows; left-to-right consecutive matches; one award per line; all lines wagered equally. No wilds or scatters.',
  theoreticalRTP: null,
  note: 'Use exactSlotsRTP for these strips/paylines/pays; simulation RTP is an estimate, not theoretical.',
});
const momentBasis = 'Gross return per spin divided by total wager per spin across all supplied paylines.';

function validateReels(reels) {
  if (!Array.isArray(reels) || !reels.length ||
      Array.from(reels).some(r => !Array.isArray(r) || !r.length ||
        Array.from(r).some(s => typeof s !== 'string' || !s.length))) {
    throw new RangeError('reels must be nonempty arrays of nonempty symbol strings');
  }
}
function validateRules(width, rows, paylines, pays) {
  if (!Array.isArray(paylines) || !paylines.length ||
      Array.from(paylines).some(line => !Array.isArray(line) || line.length !== width ||
        Array.from(line).some(row => !Number.isInteger(row) || row < 0 || row >= rows))) {
    throw new RangeError('each payline must specify one valid row per reel');
  }
  if (!pays || typeof pays !== 'object' || Array.isArray(pays)) throw new TypeError('pays must be a symbol-to-count paytable');
  for (const amounts of Object.values(pays)) {
    if (!amounts || typeof amounts !== 'object') throw new TypeError('each symbol needs a count paytable');
    for (const [count, amount] of Object.entries(amounts)) {
      if (!/^[1-9]\d*$/.test(count) || !Number.isSafeInteger(Number(count)) ||
          !Number.isFinite(amount) || amount < 0) throw new RangeError('invalid match count or payout');
    }
  }
}
function fromStops(reels, stops) {
  return Array.from({ length: 3 }, (_, row) =>
    reels.map((strip, col) => strip[(stops[col] + row) % strip.length]));
}

/** Returns a row-major grid, grid[row][reel], with three circular rows. */
export function spin(reels = REELS3, rng = new SecureRNG()) {
  validateReels(reels);
  if (!rng || typeof rng.int !== 'function') throw new TypeError('rng.int is required');
  const stops = reels.map(strip => {
    const stop = rng.int(strip.length);
    if (!Number.isInteger(stop) || stop < 0 || stop >= strip.length) throw new RangeError('rng returned an invalid stop');
    return stop;
  });
  return fromStops(reels, stops);
}
function lineAwards(grid, paylines, pays) {
  const wins = [];
  let total = 0;
  paylines.forEach((line, lineIndex) => {
    const symbol = grid[line[0]][0];
    let count = 1;
    while (count < line.length && grid[line[count]][count] === symbol) count++;
    const amount = Object.hasOwn(pays, symbol) && Object.hasOwn(pays[symbol], count)
      ? pays[symbol][count] : 0;
    if (amount > 0) {
      total += amount;
      wins.push({ line: lineIndex, symbol, count, payout: amount });
    }
  });
  if (!Number.isFinite(total)) throw new RangeError('line payouts overflowed');
  return { total, wins };
}

/** Gross multiplier summed over lines. Only the longest leftmost run pays.
 * pays = { SYMBOL: { 3: multiplier, 4: multiplier, 5: multiplier } }.
 */
export function evaluateLines(grid, paylines = PAYLINES, pays = SLOT_PAYS) {
  if (!Array.isArray(grid) || !grid.length || !Array.isArray(grid[0]) || !grid[0].length ||
      Array.from(grid).some(row => !Array.isArray(row) || row.length !== grid[0].length ||
        Array.from(row).some(s => typeof s !== 'string' || !s.length))) throw new RangeError('grid must be a rectangular symbol array');
  validateRules(grid[0].length, grid.length, paylines, pays);
  return lineAwards(grid, paylines, pays);
}
function config({ reels = REELS3, paylines, pays = SLOT_PAYS, bet = 1 } = {}) {
  validateReels(reels);
  paylines ??= reels.length === 5 ? PAYLINES5 : PAYLINES;
  validateRules(reels.length, 3, paylines, pays);
  if (!Number.isFinite(bet) || bet <= 0) throw new RangeError('bet per line must be positive');
  return { reels, paylines, pays, bet };
}

/** bet is PER LINE. Empirical RTP = gross return / total wager, not net profit.
 * Welford sample variance/stddev describe normalized gross returns per spin,
 * including covariance between simultaneous paylines. Volatility = stddev.
 * standardError = stddev / sqrt(spins); confidenceInterval is a 95% normal
 * approximation, NOT guaranteed coverage for small samples or rare jackpots.
 * For one spin the sample variance and uncertainty fields are null, not zero.
 */
export function simulateSlots(options = {}) {
  const { reels, paylines, pays, bet } = config(options);
  const { spins = 10000, rng = new SecureRNG() } = options;
  if (!Number.isSafeInteger(spins) || spins < 1) throw new RangeError('spins must be a positive integer');
  let gross = 0, winningSpins = 0, mean = 0, m2 = 0;
  for (let i = 0; i < spins; i++) {
    const multiplier = lineAwards(spin(reels, rng), paylines, pays).total;
    const award = multiplier * bet;
    gross += award;
    if (award > 0) winningSpins++;
    const normalized = multiplier / paylines.length;
    const delta = normalized - mean;
    mean += delta / (i + 1);
    m2 += delta * (normalized - mean);
  }
  const wagered = spins * paylines.length * bet;
  if (!Number.isFinite(wagered) || !Number.isFinite(gross) || !Number.isFinite(m2)) throw new RangeError('simulation totals or moments overflowed');
  const variance = spins > 1 ? Math.max(0, m2 / (spins - 1)) : null;
  const stddev = variance === null ? null : Math.sqrt(variance);
  const standardError = stddev === null ? null : stddev / Math.sqrt(spins);
  const confidenceInterval = standardError === null ? null : {
    level: 0.95, low: mean - 1.959963984540054 * standardError,
    high: mean + 1.959963984540054 * standardError,
    method: 'Normal approximation; rare jackpots and small samples can invalidate coverage.',
  };
  return { spins, wagered, gross, net: gross - wagered, rtp: mean,
    hitRate: winningSpins / spins, exact: false, variance, stddev,
    volatility: stddev, standardError, confidenceInterval, momentBasis };
}

/** Enumerates every equiprobable stop combination; refuses oversized models.
 * Returns gross RTP and population variance/stddev for equal wagers on ALL
 * supplied lines, including inter-line covariance. No sampling uncertainty.
 */
export function exactSlotsRTP(options = {}) {
  const { reels, paylines, pays } = config(options);
  const { maxOutcomes = 1000000 } = options;
  if (!Number.isSafeInteger(maxOutcomes) || maxOutcomes < 1) throw new RangeError('maxOutcomes must be a positive integer');
  const outcomes = reels.reduce((n, r) => n * r.length, 1);
  if (!Number.isSafeInteger(outcomes) || outcomes > maxOutcomes) {
    throw new RangeError(`Exact enumeration needs ${outcomes} outcomes; limit is ${maxOutcomes}`);
  }
  const stops = Array(reels.length).fill(0);
  let sum = 0, hits = 0, mean = 0, m2 = 0;
  for (let i = 0; i < outcomes; i++) {
    const award = lineAwards(fromStops(reels, stops), paylines, pays).total;
    sum += award;
    if (award > 0) hits++;
    const normalized = award / paylines.length;
    const delta = normalized - mean;
    mean += delta / (i + 1);
    m2 += delta * (normalized - mean);
    for (let col = 0; col < stops.length; col++) {
      if (++stops[col] < reels[col].length) break;
      stops[col] = 0;
    }
  }
  if (!Number.isFinite(sum) || !Number.isFinite(m2)) throw new RangeError('exact payout totals or moments overflowed');
  const variance = Math.max(0, m2 / outcomes), stddev = Math.sqrt(variance);
  return { rtp: sum / outcomes / paylines.length, hitRate: hits / outcomes,
    outcomes, exact: true, assumptions: slotOdds.assumptions,
    variance, stddev, volatility: stddev, standardError: 0,
    confidenceInterval: null, momentBasis };
}
export const exactRTP = exactSlotsRTP;
