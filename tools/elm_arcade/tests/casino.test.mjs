import test from 'node:test';
import assert from 'node:assert/strict';
import { casinoPlugins, blackjackValue, roulettePayout } from '../games/casino.mjs';
import { SeededRNG } from '../math/rng.mjs';
import { payout } from '../math/poker.mjs';
import { evaluateLines, PAYLINES, PAYLINES5, SLOT_PAYS } from '../math/slots.mjs';
import { Registry } from '../core/registry.mjs';
import { kenoExpectedReturn } from '../math/casino.mjs';

function harness(id, { saved, random = { int: max => max - 1 } } = {}) {
  const actions = new Set();
  const text = [];
  let stored = saved;
  const context = {
    canvas: { width: 960, height: 540 },
    ctx: { fillRect() {}, fillText(value) { text.push(String(value)); } },
    input: { pressed: action => actions.has(action), down: () => false },
    pointer: { x: 0, y: 0, down: false }, random, settings: {}, upgrades: new Set(),
    save(value) { stored = structuredClone(value); },
    load() { return stored; },
  };
  const plugin = casinoPlugins.find(item => item.manifest.id === id);
  assert.ok(plugin, `Plugin ${id} is registered`);
  const game = plugin.create(context);
  return {
    game, context, text, plugin,
    state: () => game.serialize(), stored: () => stored,
    press(action) { actions.add(action); game.update(1 / 60); actions.clear(); },
    click(x, y) {
      Object.assign(context.pointer, { x, y, down: true });
      game.update(1 / 60);
      context.pointer.down = false;
      game.update(1 / 60);
    },
  };
}

test('every casino manifest is unique, safe and renderable, with genuinely playable mechanics', () => {
  assert.equal(new Set(casinoPlugins.map(plugin => plugin.manifest.id)).size, casinoPlugins.length);
  const registry = new Registry();
  for (const plugin of casinoPlugins) registry.register(plugin);
  for (const { manifest } of casinoPlugins) {
    assert.equal(manifest.version, '1.0.0');
    assert.ok(['complete', 'minimal'].includes(manifest.status));
    assert.match(manifest.description, /VIRTUAL CREDITS ONLY/);
    assert.equal(manifest.upgrades.length, 1);
    assert.match(manifest.upgrades[0].title, /odds unchanged/);
    const instance = harness(manifest.id, { random: new SeededRNG(1234) });
    instance.game.render(0);
    instance.press('confirm');
    if (instance.state().phase === 'draw') instance.press('fire');
    if (instance.state().phase === 'blackjack') {
      instance.press('right');
      instance.press('confirm');
    }
    instance.game.render(0);
    assert.ok(Number.isSafeInteger(instance.state().credits));
    assert.ok(instance.state().credits >= 0);
    assert.ok(instance.text.some(line => line.includes('VIRTUAL CREDITS ONLY')));
    instance.game.destroy();
    assert.deepEqual(instance.stored(), instance.state());
  }
});

test('all casino games declare distinct valid waveform and pitch profiles', () => {
  const profiles = new Set();
  for (const { manifest } of casinoPlugins) {
    assert.ok(['sine', 'triangle', 'square', 'sawtooth'].includes(manifest.sound.type));
    assert.ok(Number.isFinite(manifest.sound.base) && manifest.sound.base > 0);
    profiles.add(`${manifest.sound.type}:${manifest.sound.base}`);
  }
  assert.equal(profiles.size, casinoPlugins.length);
});

test('poker debits once on deal; hold controls preserve cards; draw returns gross rather than profit', () => {
  const instance = harness('video-poker-jacks');
  instance.press('fire');
  assert.equal(instance.state().credits, 995);
  assert.equal(instance.state().phase, 'draw');
  const initial = instance.state().hand;
  for (let index = 0; index < 5; index++) instance.click(50 + 110 * index, 200);
  instance.press('down');
  assert.equal(instance.state().bet, 5, 'stake cannot change after deal');
  instance.press('confirm');
  const final = instance.state();
  assert.deepEqual(final.hand, initial);
  assert.equal(final.credits, 995 + payout(initial, 'jacks', 5));
  assert.equal(final.lastGross, 250);
  assert.equal(final.rounds, 1);
  assert.equal(final.phase, 'ready');
});

test('poker keyboard selection and hold, pointer debouncing, and discard replacement work', () => {
  const instance = harness('video-poker-jacks');
  instance.press('confirm');
  const dealt = instance.state().hand;
  instance.press('right');
  instance.press('up');
  assert.equal(instance.state().held[1], true);
  Object.assign(instance.context.pointer, { x: 50, y: 200, down: true });
  instance.game.update();
  instance.game.update();
  assert.equal(instance.state().held[0], true, 'held mouse button toggles only once');
  instance.context.pointer.down = false;
  instance.game.update();
  instance.press('fire');
  const final = instance.state().hand;
  assert.equal(final[0], dealt[0]);
  assert.equal(final[1], dealt[1]);
  assert.ok(final.slice(2).every(card => !dealt.includes(card)));
  assert.equal(new Set(final).size, 5);
});

test('rules-guide upgrades change display only, not bankroll, stake or payout odds', () => {
  const normal = harness('video-poker-jacks', { random: new SeededRNG(66) });
  const upgraded = harness('video-poker-jacks', { random: new SeededRNG(66) });
  upgraded.context.upgrades.add('video-poker-jacks-rules-guide');
  for (const instance of [normal, upgraded]) {
    instance.press('fire');
    instance.press('fire');
    instance.game.render();
  }
  assert.deepEqual(normal.state(), upgraded.state());
  assert.ok(upgraded.text.some(line => line.startsWith('GUIDE:')));
  assert.ok(!normal.text.some(line => line.startsWith('GUIDE:')));
});

test('published poker RTP references are labelled percentages, never local strategy calculations', () => {
  for (const id of ['video-poker-jacks', 'video-poker-deuces']) {
    const instance = harness(id);
    instance.game.render();
    assert.ok(instance.text.some(line => line.includes('Reference RTP')));
    assert.match(instance.text.join(' '), /Published optimal-strategy reference/);
    assert.match(instance.text.join(' '), /NOT a local calculation/);
  }
});

test('house-rule future multipliers do not claim the base Jacks reference RTP', () => {
  const instance = harness('video-poker-ultimate-x');
  instance.game.render();
  const disclosure = instance.text.join(' ') + instance.plugin.manifest.description;
  assert.match(disclosure, /RTP not calculated for house-rule future multipliers/);
  assert.match(disclosure, /base Jacks reference does NOT apply/);
  assert.doesNotMatch(disclosure, /99\.5439/);
});

test('keno, scratch and pass-line craps disclose the exact RTP of their actual rules', () => {
  const kenoPercent = (kenoExpectedReturn(5, { 3: 2, 4: 10, 5: 100 }) * 100).toFixed(4);
  for (const [id, percent] of [
    ['keno', kenoPercent], ['scratch', '55.5556'], ['craps', '98.5859'],
  ]) {
    const instance = harness(id);
    instance.game.render();
    assert.ok(instance.text.some(line => line.includes(`RTP ${percent}%`)), id);
    assert.ok(!instance.text.some(line => line.includes('RTP not calculated')), id);
  }
  const baccarat = harness('baccarat');
  baccarat.game.render();
  assert.ok(baccarat.text.some(line => line.includes('RTP not calculated')));
});

test('shared action input and pixel pointer do not double-trigger card clicks', () => {
  const instance = harness('video-poker-jacks');
  instance.context.input.pointer = instance.context.pointer;
  instance.press('action');
  assert.equal(instance.state().phase, 'draw');
  instance.click(50, 200);
  assert.equal(instance.state().held[0], true);
  assert.equal(instance.state().phase, 'draw');
  Object.assign(instance.context.pointer, { x: 160, y: 200, down: true });
  instance.press('action');
  assert.equal(instance.state().held[1], true);
  assert.equal(instance.state().phase, 'draw', 'pointer action edge must not draw');
});

test('pixel input.pointer coordinates remain authoritative even with normalized helper fields', () => {
  const instance = harness('video-poker-jacks');
  instance.press('fire');
  instance.context.pointer = undefined;
  instance.context.input.pointer = {
    x: 480, y: 270, inside: true, normalizedX: 0.5, normalizedY: 0.5, down: true,
  };
  instance.game.update();
  assert.deepEqual(instance.state().held, [false, false, false, false, true]);
  assert.equal(instance.state().phase, 'draw');
});

for (const variant of ['deuces', 'bonus', 'double-bonus', 'double-double-bonus', 'joker', 'tens', 'all-american']) {
  test(`${variant} poker integrates the selected variant's gross paytable`, () => {
    const instance = harness(`video-poker-${variant}`);
    instance.press('confirm');
    const original = instance.state().hand;
    for (let index = 0; index < 5; index++) instance.click(50 + 110 * index, 200);
    instance.press('confirm');
    assert.equal(instance.state().credits, 995 + payout(original, variant, 5));
    instance.game.render();
    assert.ok(instance.text.includes('GROSS × stake (not profit)'));
  });
}

for (const hands of [3, 5, 10]) {
  test(`${hands}-hand poker charges every hand, uses held cards, and sums gross returns`, () => {
    const instance = harness(`video-poker-multi-${hands}`);
    instance.press('confirm');
    assert.equal(instance.state().credits, 1000 - 5 * hands);
    const initial = instance.state().hand;
    for (let i = 0; i < 5; i++) instance.click(50 + i * 110, 200);
    instance.press('confirm');
    const final = instance.state();
    assert.equal(final.results.length, hands);
    for (const result of final.results) assert.deepEqual(result.hand, initial);
    assert.equal(final.credits, 1000 - 5 * hands + hands * payout(initial, 'jacks', 5));
  });
}

test('multi-hand replacements are independent and never duplicate dealt cards', () => {
  const instance = harness('video-poker-multi-10', { random: new SeededRNG(7) });
  instance.press('fire');
  const original = instance.state().hand;
  instance.press('up');
  instance.press('fire');
  const results = instance.state().results;
  for (const result of results) {
    assert.equal(result.hand[0], original[0]);
    assert.equal(new Set(result.hand).size, 5);
    assert.ok(result.hand.slice(1).every(card => !original.includes(card)));
  }
  assert.ok(new Set(results.map(result => JSON.stringify(result.hand))).size > 1);
});

test('future multipliers apply only to the subsequent hand and survive save/load', () => {
  let instance = harness('video-poker-ultimate-x');
  instance.press('fire');
  for (let i = 0; i < 5; i++) instance.click(50 + i * 110, 200);
  instance.press('fire');
  assert.equal(instance.state().activeMultiplier, 1);
  assert.equal(instance.state().nextMultiplier, 2);
  instance = harness('video-poker-ultimate-x', { saved: instance.stored() });
  instance.press('fire');
  assert.equal(instance.state().activeMultiplier, 2);
  for (let i = 0; i < 5; i++) instance.click(50 + i * 110, 200);
  instance.press('fire');
  assert.equal(instance.state().lastGross, 500);
  assert.equal(instance.plugin.manifest.status, 'minimal');
});

for (const reels of [3, 5]) {
  test(`${reels}-reel slots charges per line and credits exactly the math award`, () => {
    const instance = harness(`slots-${reels}`);
    instance.press('fire');
    const state = instance.state();
    const lines = reels === 3 ? PAYLINES : PAYLINES5;
    assert.equal(state.grid.length, 3);
    assert.ok(state.grid.every(row => row.length === reels));
    const expected = evaluateLines(state.grid, lines, SLOT_PAYS).total * 5;
    assert.equal(state.credits, 1000 - 5 * lines.length + expected);
    assert.equal(state.lastGross, expected);
    instance.game.render();
    assert.ok(instance.text.some(line => /Exact RTP \d+\.\d+%/.test(line)));
    assert.ok(instance.text.some(line => line.includes('stake PER LINE')));
  });
}

test('saved in-progress poker resumes without charging again', () => {
  const first = harness('video-poker-jacks');
  first.press('fire');
  first.press('up');
  const saved = first.stored();
  const resumed = harness('video-poker-jacks', { saved });
  assert.deepEqual(resumed.state(), saved);
  resumed.press('fire');
  assert.equal(resumed.state().credits, saved.credits + resumed.state().lastGross);
  assert.equal(resumed.state().rounds, 1);
  const wrapped = harness('video-poker-jacks', { saved: { version: '1.0.0', data: saved } });
  assert.deepEqual(wrapped.state(), saved);
  wrapped.press('fire');
  assert.equal(wrapped.state().credits, saved.credits + wrapped.state().lastGross);
});

test('invalid saves are rejected and serialization is a detached copy', () => {
  const valid = harness('video-poker-jacks').state();
  for (const bad of [
    { ...valid, credits: -1 }, { ...valid, bet: 0 }, { ...valid, credits: NaN },
    { ...valid, id: 'other' }, { ...valid, phase: 'draw', hand: [0, 0, 0, 0, 0] },
    { ...valid, grid: ['not a row'] }, { ...valid, results: [null] },
  ]) {
    const instance = harness('video-poker-jacks', { saved: bad });
    assert.equal(instance.state().credits, 1000);
    assert.equal(instance.state().phase, 'ready');
    instance.game.render();
  }
  const instance = harness('video-poker-jacks');
  const detached = instance.state();
  detached.credits = -100;
  detached.hand.push(999);
  assert.equal(instance.state().credits, 1000);
  assert.deepEqual(instance.state().hand, []);
});

test('credit bounds and bankruptcy require explicit reset, never automatic refill', () => {
  const base = harness('video-poker-multi-10').state();
  const instance = harness('video-poker-multi-10', { saved: { ...base, credits: 4 } });
  instance.press('fire');
  assert.equal(instance.state().credits, 4);
  instance.press('down');
  instance.press('fire');
  assert.equal(instance.state().credits, 4);
  instance.game.render();
  assert.ok(instance.text.includes('RESET BANKRUPTCY'));
  instance.click(800, 470);
  assert.equal(instance.state().credits, 1000);
  instance.click(800, 470);
  assert.equal(instance.state().credits, 1000);
  for (let i = 0; i < 110; i++) instance.press('up');
  assert.equal(instance.state().bet, 100);
  instance.press('fire');
  assert.equal(instance.state().credits, 0);
  instance.click(800, 470);
  assert.equal(instance.state().credits, 0, 'cannot reset while wager is in progress');
});

test('roulette distinguishes zero, double zero and losses, with 36x gross', () => {
  const european = harness('roulette-european', { random: { int: () => 0 } });
  european.press('fire');
  assert.equal(european.state().credits, 1175);
  european.press('right');
  european.press('fire');
  assert.equal(european.state().credits, 1170);
  const american = harness('roulette-american');
  american.press('left');
  assert.equal(american.state().selection, 37);
  american.press('fire');
  assert.equal(american.state().drawn[0], 37);
  assert.equal(american.state().lastGross, 180);
  assert.equal(roulettePayout(0, 37, 5), 0);
});

test('blackjack ace values, stand settlement and locked stakes', () => {
  assert.equal(blackjackValue([12, 25, 8]), 12);
  assert.equal(blackjackValue([12, 8]), 21);
  const instance = harness('blackjack');
  instance.press('fire');
  assert.equal(instance.state().credits, 995);
  assert.equal(instance.state().phase, 'blackjack');
  instance.press('up');
  assert.equal(instance.state().bet, 5);
  instance.press('right');
  instance.press('fire');
  assert.equal(instance.state().credits, 1005, 'dealer bust returns 2x gross');
  assert.equal(instance.state().phase, 'ready');
});

test('baccarat player bet handles banker natural without additional draws', () => {
  const instance = harness('baccarat');
  instance.press('fire');
  assert.equal(instance.state().credits, 995);
  assert.equal(instance.state().hand.length, 2);
  assert.equal(instance.state().dealer.length, 2);
  assert.match(instance.state().message, /player 5, banker 9/);
});

test('craps locks the pass wager through come-out and point rolls, including saved sessions', () => {
  const rolls = [1, 1, 2, 2, 1, 1];
  const random = { int: () => rolls.shift() };
  let instance = harness('craps', { random });
  instance.press('fire');
  assert.equal(instance.state().point, 4);
  assert.equal(instance.state().credits, 995);
  instance = harness('craps', { random, saved: instance.stored() });
  instance.press('up');
  assert.equal(instance.state().bet, 5);
  instance.press('fire');
  assert.equal(instance.state().credits, 995, 'non-resolving roll has no debit');
  assert.equal(instance.state().point, 4);
  instance.press('fire');
  assert.equal(instance.state().credits, 1005);
  assert.equal(instance.state().point, 0);
  assert.equal(instance.state().rounds, 1);
});

test('craps come-out wins, craps losses, and seven-out use one wager per cycle', () => {
  for (const [rolls, expected] of [
    [[2, 3], 1005], // Seven on the come-out.
    [[0, 0], 995], // Two on the come-out.
    [[1, 1, 2, 3], 995], // Point four followed by seven-out.
  ]) {
    const queue = [...rolls];
    const instance = harness('craps', { random: { int: () => queue.shift() } });
    instance.press('fire');
    if (instance.state().point) instance.press('fire');
    assert.equal(instance.state().credits, expected);
    assert.equal(instance.state().point, 0);
    assert.equal(instance.state().wager, 0);
    assert.equal(instance.state().rounds, 1);
  }
});

test('poker cannot overdraw a low bankroll or auto-reset after a losing hand', () => {
  const base = harness('video-poker-jacks').state();
  const instance = harness('video-poker-jacks', { saved: { ...base, credits: 5 } });
  instance.press('fire');
  assert.equal(instance.state().credits, 0);
  const active = instance.state();
  active.hand = [0, 16, 32, 48, 11];
  active.shoe = Array.from({ length: 52 }, (_, i) => i).filter(card => !active.hand.includes(card));
  active.held.fill(true);
  const resumed = harness('video-poker-jacks', { saved: active });
  resumed.press('fire');
  assert.equal(resumed.state().lastGross, 0);
  assert.equal(resumed.state().credits, 0);
  resumed.press('fire');
  assert.equal(resumed.state().credits, 0);
  assert.equal(resumed.state().rounds, 1);
  resumed.click(800, 470);
  assert.equal(resumed.state().credits, 1000);
});

test('keno draws without replacement and scratch has its own symbol-match mechanic', () => {
  const keno = harness('keno');
  keno.press('fire');
  assert.equal(new Set(keno.state().drawn).size, 20);
  assert.equal(keno.state().lastGross, 500);
  assert.equal(keno.state().credits, 1495);
  keno.click(45, 160);
  const credits = keno.state().credits;
  keno.press('fire');
  assert.equal(keno.state().credits, credits, 'invalid pick count cannot debit');
  const scratch = harness('scratch', { random: { int: () => 0 } });
  scratch.press('fire');
  assert.deepEqual(scratch.state().drawn, [0, 0, 0]);
  assert.equal(scratch.state().credits, 1095);
});
