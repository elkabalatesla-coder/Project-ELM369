import assert from 'node:assert/strict';
import { webcrypto } from 'node:crypto';
import { SecureRNG, SeededRNG, shuffle, deck } from '../math/rng.mjs';
import { PAYTABLES, pokerVariants, evaluate, payout, handEV, optimalHolds, strategyRTP } from '../math/poker.mjs';
import { REELS3, REELS5, PAYLINES, PAYLINES5, SLOT_PAYS, spin, evaluateLines,
  simulateSlots, exactSlotsRTP } from '../math/slots.mjs';
import { blackjackValue, basicStrategy, roulettePayout, crapsPayout, resolveCraps,
  logChoose, kenoProbability, kenoExpectedReturn, casinoOdds } from '../math/casino.mjs';

const card = (rank, suit = 0) => suit * 13 + rank - 2;
const near = (a, b, tolerance = 1e-10) => assert.ok(Math.abs(a - b) < tolerance, `${a} != ${b}`);
const royal = [10, 11, 12, 13, 14].map(r => card(r));

function testRNG() {
  assert.deepEqual(deck(), Array.from({ length: 52 }, (_, i) => i));
  const a = new SeededRNG(123), b = new SeededRNG(123);
  for (let i = 0; i < 1000; i++) assert.equal(a.int(79), b.int(79));
  const source = deck(), shuffled = shuffle(source, new SeededRNG(55));
  assert.deepEqual(source, deck());
  assert.deepEqual(shuffled.slice().sort((x, y) => x - y), source);
  assert.notDeepEqual(shuffled, source);
  assert.deepEqual(shuffle(source, new SeededRNG(55)), shuffled);
  const sequence = [0xffffffff, 8];
  const rejecting = new SecureRNG({ getRandomValues(buffer) { buffer[0] = sequence.shift(); } });
  assert.equal(rejecting.int(3), 2);
  assert.equal(sequence.length, 0);
  const secure = new SecureRNG(webcrypto);
  for (let i = 0; i < 100; i++) {
    const n = secure.int(7);
    assert.ok(n >= 0 && n < 7);
  }
  for (const rng of [secure, new SeededRNG(0)]) {
    assert.equal(rng.int(1), 0);
    assert.ok(rng.int(0x100000000) < 0x100000000);
    for (const max of [0, -1, 1.2, NaN, Infinity, 0x100000001]) assert.throws(() => rng.int(max), RangeError);
  }
  assert.throws(() => new SecureRNG(null));
  assert.throws(() => new SeededRNG(NaN));
  assert.throws(() => shuffle(source, { int: () => -1 }));
  const counts = Array(7).fill(0), rng = new SeededRNG(99);
  for (let i = 0; i < 70000; i++) counts[rng.int(7)]++;
  assert.ok(counts.every(n => n > 9500 && n < 10500));
}

function testPoker() {
  const examples = [
    [royal, 'royalFlush'],
    [[2, 3, 4, 5, 14].map(r => card(r)), 'straightFlush'],
    [[card(7), card(7, 1), card(7, 2), card(7, 3), card(4)], 'fourKind'],
    [[card(7), card(7, 1), card(7, 2), card(4, 3), card(4)], 'fullHouse'],
    [[2, 5, 8, 11, 14].map(r => card(r)), 'flush'],
    [[card(14), card(2, 1), card(3, 2), card(4), card(5)], 'straight'],
    [[card(7), card(7, 1), card(7, 2), card(3, 3), card(4)], 'threeKind'],
    [[card(7), card(7, 1), card(4, 2), card(4, 3), card(14)], 'twoPair'],
    [[card(11), card(11, 1), card(7, 2), card(3, 3), card(4)], 'jacksOrBetter'],
    [[card(10), card(10, 1), card(7, 2), card(3, 3), card(4)], 'nothing'],
  ];
  for (const [hand, expected] of examples) assert.equal(evaluate(hand), expected);
  assert.equal(payout(royal, 'jacks', 5), 4000);
  assert.equal(PAYTABLES.jacks.fullHouse, 9);
  assert.equal(PAYTABLES.jacks.flush, 6);
  assert.equal(evaluate(examples.at(-1)[0], 'tens'), 'tensOrBetter');
  assert.equal(evaluate(royal, 'jacks-or-better'), 'royalFlush');
  assert.equal(evaluate(royal, 'all-american'), 'royalFlush');
  assert.equal(payout(examples[1][0], 'allAmerican'), 200);
  assert.equal(payout(examples[2][0], 'allAmerican'), 40);
  assert.equal(payout(examples[3][0], 'allAmerican'), 8);
  assert.equal(payout(examples[4][0], 'allAmerican'), 8);
  assert.equal(payout(examples[5][0], 'allAmerican'), 8);
  assert.equal(payout(examples[7][0], 'allAmerican'), 1);
  assert.equal(pokerVariants.length, Object.keys(PAYTABLES).length);
  for (const metadata of pokerVariants) {
    if (metadata.id === 'jacks' || metadata.id === 'deuces') {
      assert.equal(metadata.theoreticalRTP, metadata.id === 'jacks' ? 0.995439 : 1.00762);
      assert.match(metadata.rtpProvenance, /reference.*NOT a local calculation/);
    } else assert.equal(metadata.theoreticalRTP, null);
  }
  const fourAces = [0, 1, 2, 3].map(s => card(14, s));
  assert.equal(payout([...fourAces, card(2)], 'bonus'), 80);
  assert.equal(payout([...fourAces, card(2)], 'doubleBonus'), 160);
  assert.equal(payout([...fourAces, card(2)], 'doubleDoubleBonus'), 400);
  assert.equal(payout([...fourAces, card(5)], 'doubleDoubleBonus'), 160);
  const fours = [0, 1, 2, 3].map(s => card(4, s));
  assert.equal(payout([...fours, card(14)], 'doubleDoubleBonus'), 160);
  assert.equal(payout([...fours, card(5)], 'doubleDoubleBonus'), 80);
  const kings = [0, 1, 2, 3].map(s => card(13, s));
  assert.equal(payout([...kings, card(2)], 'acesFaces'), 40);
  assert.equal(payout([...kings, card(2)], 'bonus'), 25);
  const deuceHands = [
    [royal, 'royalFlush'],
    [[0, 13, 26, 39, card(14)], 'fourDeuces'],
    [[0, ...[10, 11, 12, 13].map(r => card(r))], 'wildRoyal'],
    [[0, ...fourAces], 'fiveKind'],
    [[0, ...[5, 6, 7, 8].map(r => card(r))], 'straightFlush'],
    [[0, card(7), card(7, 1), card(7, 2), card(3, 3)], 'fourKind'],
    [[0, card(7), card(7, 1), card(3, 2), card(3, 3)], 'fullHouse'],
    [[0, ...[3, 6, 9, 14].map(r => card(r, 1))], 'flush'],
    [[0, card(14), card(3, 1), card(4, 2), card(5, 3)], 'straight'],
    [[0, card(7), card(7, 1), card(3, 2), card(11, 3)], 'threeKind'],
    [[card(3), card(3, 1), card(7), card(7, 1), card(14)], 'nothing'],
    [[0, 13, card(3), card(8, 1), card(12, 2)], 'threeKind'],
  ];
  for (const [hand, expected] of deuceHands) assert.equal(evaluate(hand, 'deuces'), expected, JSON.stringify(hand));
  assert.equal(evaluate([52, ...fourAces], 'joker'), 'fiveKind');
  assert.equal(evaluate([52, ...royal.slice(0, 4)], 'joker'), 'wildRoyal');
  assert.equal(evaluate([card(13), card(13, 1), card(3), card(6), card(9)], 'joker'), 'kingsOrBetter');
  assert.equal(evaluate([card(12), card(12, 1), card(3), card(6), card(9)], 'joker'), 'nothing');
  assert.equal(evaluate([52, card(3), card(6), card(9, 1), card(12, 2)], 'joker'), 'nothing');
  assert.equal(evaluate([52, card(3), card(6), card(9, 1), card(13, 2)], 'joker'), 'kingsOrBetter');
  for (const hand of [[], [, 1, 2, 3, 4], [0, 1, 2, 3, 3], [0, 1, 2, 3, 52], [0, 1, 2, 3, -1], [0, 1, 2, 3, 1.5]]) {
    assert.throws(() => evaluate(hand), RangeError);
  }
  assert.throws(() => evaluate(royal, 'constructor'), RangeError);
  assert.throws(() => payout(royal, 'jacks', -1), RangeError);
  assert.throws(() => payout(royal, 'jacks', Infinity), RangeError);
  assert.throws(() => payout(royal, 'jacks', Number.MAX_VALUE), RangeError);
  assert.equal(handEV(royal, 31), 800);
  assert.equal(handEV(royal, [0, 1, 2, 3, 4]), 800);
  assert.throws(() => handEV(royal, [0, 0]));
  assert.throws(() => optimalHolds(royal, 'jacks', { signal: { aborted: true } }));

  const rng = new SeededRNG(29);
  for (let i = 0; i < 300; i++) {
    const hand = shuffle(deck(), rng).slice(0, 5);
    for (const variant of Object.keys(PAYTABLES)) {
      const result = evaluate(hand, variant);
      assert.ok(Object.hasOwn(PAYTABLES[variant], result));
      assert.equal(evaluate(shuffle(hand, rng), variant), result);
      assert.ok(Number.isFinite(payout(hand, variant)));
    }
  }
  // Independent concrete-card oracle for one/two wilds (five-of-kind separately).
  for (let i = 0; i < 24; i++) {
    const wilds = i % 2 + 1;
    const base = shuffle(deck().filter(c => c % 13 !== 0), rng).slice(0, 5 - wilds);
    const hand = [...base, ...[0, 13].slice(0, wilds)];
    const count = Array(15).fill(0);
    for (const c of base) count[c % 13 + 2]++;
    let best = Math.max(...count) + wilds >= 5 ? PAYTABLES.deuces.fiveKind : 0;
    const available = deck().filter(c => !base.includes(c));
    const replacement = [];
    function oracle(start) {
      if (replacement.length === wilds) {
        let category = evaluate([...base, ...replacement]);
        if (category === 'royalFlush') category = 'wildRoyal';
        best = Math.max(best, PAYTABLES.deuces[category] ?? 0);
        return;
      }
      for (let n = start; n < available.length; n++) {
        replacement.push(available[n]); oracle(n + 1); replacement.pop();
      }
    }
    oracle(0);
    assert.equal(payout(hand, 'deuces'), best, `wild oracle: ${hand}`);
  }
  let progress = 0;
  const solved = optimalHolds(royal, 'jacks', { onProgress: () => progress++ });
  assert.equal(progress, 32);
  assert.equal(solved.results.length, 32);
  assert.deepEqual(solved.hold, [0, 1, 2, 3, 4]);
  assert.equal(solved.mask, 31);
  assert.equal(solved.ev, 800);
  assert.equal(solved.exact, true);
  assert.equal(solved.results[0].outcomes, 1533939); // 47 choose 5
  assert.equal(solved.results[30].outcomes, 47);
  assert.equal(solved.results.reduce((n, r) => n + r.outcomes, 0), 2598960);
  const wildSolved = optimalHolds([0, 13, 26, 39, card(14)], 'deuces');
  assert.equal(wildSolved.ev, 200);
  assert.equal(wildSolved.mask, 31); // Equivalent EV holds prefer more retained cards.
  assert.equal(wildSolved.results[15].ev, 200);
  assert.throws(() => strategyRTP('jacks', { signal: { aborted: true } }), /aborted/);
  assert.throws(() => strategyRTP('jacks', { strategy: 31 }), TypeError);
  assert.throws(() => strategyRTP('jacks', { progressEvery: 0 }), RangeError);
  let lastProgress;
  const strategyReturn = strategyRTP('jacks', {
    strategy: () => 31, progressEvery: 1000000,
    onProgress: value => { lastProgress = value; },
  });
  // Independently tabulated five-card category frequencies: never draw.
  const gross = 4 * 800 + 36 * 50 + 624 * 25 + 3744 * 9 + 5108 * 6 +
    10200 * 4 + 54912 * 3 + 123552 * 2 + 337920;
  near(strategyReturn.rtp, gross / 2598960);
  assert.equal(strategyReturn.hands, 2598960);
  assert.equal(strategyReturn.exact, true);
  assert.equal(strategyReturn.strategy, 'provided');
  assert.deepEqual(lastProgress, { hands: 2598960, totalHands: 2598960 });
}

function testSlots() {
  const rng = new SeededRNG(4);
  const grid = spin(REELS3, rng);
  assert.equal(grid.length, 3);
  assert.ok(grid.every(row => row.length === 3));
  const line = [[0, 0, 0]];
  const pays = { A: { 3: 8 } }, reels = [['A', 'B'], ['A', 'B'], ['A', 'B']];
  assert.deepEqual(evaluateLines([['A', 'A', 'A']], line, pays),
    { total: 8, wins: [{ line: 0, symbol: 'A', count: 3, payout: 8 }] });
  assert.equal(evaluateLines([['B', 'A', 'A']], line, pays).total, 0);
  const exact = exactSlotsRTP({ reels, paylines: line, pays });
  assert.equal(exact.outcomes, 8);
  assert.equal(exact.rtp, 1);
  assert.equal(exact.hitRate, 1 / 8);
  assert.equal(exact.exact, true);
  near(exact.variance, 7); // X=8 with probability 1/8, otherwise X=0.
  near(exact.stddev, Math.sqrt(7));
  assert.equal(exact.volatility, exact.stddev);
  assert.equal(exact.standardError, 0);
  assert.equal(exact.confidenceInterval, null);
  const simulated = simulateSlots({ reels, paylines: line, pays, spins: 50000, rng: new SeededRNG(5), bet: 2 });
  assert.equal(simulated.wagered, 100000);
  assert.equal(simulated.net, simulated.gross - simulated.wagered);
  near(simulated.rtp, 1, 0.04);
  near(simulated.variance, exact.variance, 0.2);
  near(simulated.stddev ** 2, simulated.variance);
  near(simulated.standardError, simulated.stddev / Math.sqrt(simulated.spins));
  assert.equal(simulated.volatility, simulated.stddev);
  assert.equal(simulated.confidenceInterval.level, 0.95);
  assert.ok(simulated.confidenceInterval.low < simulated.rtp);
  assert.ok(simulated.confidenceInterval.high > simulated.rtp);
  assert.equal(simulated.exact, false);
  assert.deepEqual(simulated, simulateSlots({ reels, paylines: line, pays, spins: 50000, rng: new SeededRNG(5), bet: 2 }));
  const unitBet = simulateSlots({ reels, paylines: line, pays, spins: 50000, rng: new SeededRNG(5), bet: 1 });
  assert.equal(unitBet.variance, simulated.variance);
  assert.equal(unitBet.rtp, simulated.rtp);
  const single = simulateSlots({ reels, paylines: line, pays, spins: 1, rng: new SeededRNG(5) });
  assert.equal(single.variance, null);
  assert.equal(single.stddev, null);
  assert.equal(single.standardError, null);
  assert.equal(single.confidenceInterval, null);
  const constant = simulateSlots({
    reels: [['A'], ['A'], ['A']], paylines: line, pays, spins: 5, rng: new SeededRNG(5),
  });
  assert.equal(constant.rtp, 8);
  assert.equal(constant.variance, 0);
  assert.equal(constant.standardError, 0);
  // Duplicated simultaneous lines are perfectly correlated, not independent.
  const duplicate = exactSlotsRTP({ reels, paylines: [line[0], line[0]], pays });
  near(duplicate.variance, exact.variance);
  const defaultExact = exactSlotsRTP();
  const defaultSimulation = simulateSlots({ spins: 50000, rng: new SeededRNG(8) });
  near(defaultSimulation.rtp, defaultExact.rtp, 0.05);
  const oneLine = exactSlotsRTP({ paylines: [PAYLINES[0]] });
  near(oneLine.rtp, defaultExact.rtp);
  const five = exactSlotsRTP({ reels: REELS5 });
  assert.equal(five.outcomes, 12 ** 5);
  assert.ok(Number.isFinite(five.rtp));
  assert.ok(evaluateLines(spin(REELS5, rng), PAYLINES5, SLOT_PAYS).total >= 0);
  assert.throws(() => spin([]));
  assert.throws(() => spin([[]]));
  assert.throws(() => spin([['A', , 'B']]));
  assert.throws(() => spin(REELS3, { int: () => -1 }));
  assert.throws(() => evaluateLines([['A'], []], [[0]], pays));
  assert.throws(() => evaluateLines([['A']], [[1]], pays));
  assert.throws(() => evaluateLines([['A']], [[0]], { A: { 1: -1 } }));
  assert.throws(() => exactSlotsRTP({ maxOutcomes: 2 }));
  assert.throws(() => simulateSlots({ spins: 0 }));
  assert.throws(() => simulateSlots({ spins: 1, bet: -1 }));
}

function testCasino() {
  assert.deepEqual(blackjackValue(['A', '6']), { total: 17, soft: true, bust: false });
  assert.deepEqual(blackjackValue(['A', '6', 'K']), { total: 17, soft: false, bust: false });
  assert.deepEqual(blackjackValue(['A', 'A', '9']), { total: 21, soft: true, bust: false });
  assert.deepEqual(blackjackValue(['K', 'Q', '2']), { total: 22, soft: false, bust: true });
  assert.equal(blackjackValue([card(14), card(13, 1)]).total, 21);
  for (const [hand, dealer, action, options] of [
    [['A', '7'], '6', 'double'], [['A', '7'], '9', 'hit'],
    [['A', '7'], '6', 'stand', { canDouble: false }],
    [['A', '7'], '2', 'stand'], [['A', '8'], '6', 'stand'],
    [['A', '6'], '3', 'double'], [['A', '2'], '4', 'hit'],
    [['A', 'A'], 'A', 'split'], [['8', '8'], '10', 'split'],
    [['9', '9'], '7', 'stand'], [['9', '9'], '8', 'split'],
    [['4', '4'], '5', 'split'], [['5', '5'], '8', 'double'],
    [['5', '6'], 'A', 'hit'], [['5', '6'], '10', 'double'],
    [['8', '8'], '10', 'hit', { canSplit: false }],
    [['6', '6'], '2', 'split'], [['7', '5'], '3', 'hit'],
    [['7', '5'], '4', 'stand'], [['10', '7'], 'A', 'stand'],
    [['2', '3', '6'], '6', 'hit'],
  ]) assert.equal(basicStrategy(hand, dealer, options), action, `${hand} vs ${dealer}`);
  assert.throws(() => blackjackValue([]));
  assert.throws(() => blackjackValue([52]));
  assert.throws(() => blackjackValue(Array(2)));
  assert.throws(() => blackjackValue(['11']));
  assert.equal(roulettePayout('straight', true), 36);
  assert.equal(roulettePayout('red', true), 2);
  assert.equal(roulettePayout('red', false), 0);
  assert.equal(roulettePayout('basket', true, true), 7);
  assert.throws(() => roulettePayout('basket', true));
  assert.throws(() => roulettePayout('constructor', true));
  assert.throws(() => roulettePayout('red', 1));
  assert.deepEqual(resolveCraps(12), { point: null, pass: 'lose', dontPass: 'push' });
  assert.deepEqual(resolveCraps(6), { point: 6, pass: 'pending', dontPass: 'pending' });
  assert.deepEqual(resolveCraps(8, 6), { point: 6, pass: 'pending', dontPass: 'pending' });
  assert.deepEqual(resolveCraps(6, 6), { point: null, pass: 'win', dontPass: 'lose' });
  assert.deepEqual(resolveCraps(7, 6), { point: null, pass: 'lose', dontPass: 'win' });
  assert.equal(crapsPayout('pass', 'win'), 2);
  assert.equal(crapsPayout('dontPass', 'push'), 1);
  assert.equal(crapsPayout('passOdds', 'win', 4), 3);
  near(crapsPayout('dontOdds', 'win', 6), 11 / 6);
  assert.equal(crapsPayout('passOdds', 'lose', 6), 0);
  assert.throws(() => resolveCraps(1));
  assert.throws(() => resolveCraps(7, 7));
  assert.throws(() => crapsPayout('passOdds', 'win', 7));
  assert.throws(() => crapsPayout('pass', 'pending'));
  near(Math.exp(logChoose(5, 2)), 10);
  assert.equal(logChoose(0, 0), 0);
  assert.equal(logChoose(5, 6), -Infinity);
  assert.equal(logChoose(5, -1), -Infinity);
  for (let picks = 0; picks <= 80; picks++) {
    let sum = 0;
    for (let hits = 0; hits <= picks; hits++) sum += kenoProbability(picks, hits);
    near(sum, 1);
  }
  near(kenoProbability(1, 1), 0.25);
  near(kenoProbability(1, 0), 0.75);
  assert.equal(kenoProbability(80, 20), 1);
  assert.equal(kenoProbability(1, 2), 0);
  assert.equal(kenoProbability(1, -1), 0);
  assert.equal(kenoProbability(0, 0, 0, 0), 1);
  near(kenoExpectedReturn(1, { 1: 4 }), 1);
  near(kenoExpectedReturn(1, { 0: 1, 1: 1 }), 1);
  assert.equal(kenoExpectedReturn(10, {}), 0);
  assert.throws(() => kenoProbability(81, 1));
  assert.throws(() => kenoProbability(2, 1.5));
  assert.throws(() => kenoProbability(2, 1, 81));
  assert.throws(() => kenoExpectedReturn(2, { 3: 1 }));
  assert.throws(() => kenoExpectedReturn(2, { 1: -1 }));
  assert.equal(casinoOdds.blackjack.theoreticalRTP, null);
}

testRNG();
testPoker();
testSlots();
testCasino();
console.log('Casino math: RNG, poker/exact solver/wild oracle, slots/exact RTP, blackjack, roulette, craps and keno passed.');
