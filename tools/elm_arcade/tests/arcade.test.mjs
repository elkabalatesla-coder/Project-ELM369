import test from 'node:test';
import assert from 'node:assert/strict';
import { aabb, circles, sat, integrate, astar, difficulty, scoreMultiplier } from '../math/arcade.mjs';
import { arcadePlugins } from '../games/arcade.mjs';

function harness(id, upgrades = [], saved = null) {
  const held = new Set(), tapped = new Set(), finishes = [], tones = [], saves = [];
  const renderCalls = [];
  const ctx = new Proxy({}, {
    get: (_, key) => (...args) => renderCalls.push([key, ...args]),
    set: () => true,
  });
  let seed = 42;
  const context = {
    canvas: { width: 960, height: 540 }, ctx,
    input: {
      down: key => held.has(key), pressed: key => tapped.has(key),
      pointer: { x: 480, y: 270, down: false }, endFrame: () => tapped.clear(),
    },
    audio: { tone: (...args) => tones.push(args) }, camera: {}, settings: {},
    random: { int: max => { seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0; return seed % max; } },
    finish: score => finishes.push(score), save: value => saves.push(value), load: () => saved,
    upgrades: new Set(upgrades),
  };
  const game = arcadePlugins.find(p => p.manifest.id === id).create(context);
  const step = (count = 1, dt = 1 / 60) => {
    for (let i = 0; i < count; i++) { game.update(dt); context.input.endFrame(); }
    return game.serialize();
  };
  const tap = action => { tapped.add(action); return step(); };
  return { game, step, tap, held, tapped, finishes, tones, saves, context, renderCalls };
}

test('collision helpers include touching edges and reject invalid inputs', () => {
  assert.equal(aabb({ x: 0, y: 0, w: 10, h: 10 }, { x: 10, y: 10, width: 2, height: 2 }), true);
  assert.equal(aabb({ x: 0, y: 0, w: 10, h: 10 }, { x: 11, y: 0, w: 1, h: 1 }), false);
  assert.equal(circles({ x: 0, y: 0, r: 2 }, { x: 4, y: 0, radius: 2 }), true);
  assert.equal(circles({ x: 0, y: 0, r: 2 }, { x: 5, y: 0, r: 2 }), false);
  assert.throws(() => aabb({ x: NaN, y: 0, w: 1, h: 1 }, {}), TypeError);
  assert.throws(() => aabb({ x: 0, y: 0, w: -1, h: 1 }, { x: 0, y: 0, w: 1, h: 1 }), RangeError);
  assert.throws(() => circles({ x: Infinity, y: 0, r: 1 }, { x: 0, y: 0, r: 1 }), TypeError);
  assert.throws(() => circles({ x: 0, y: 0, r: -1 }, { x: 0, y: 0, r: 1 }), RangeError);
});

test('SAT checks axes from both polygons', () => {
  const square = [{ x: 0, y: 0 }, { x: 4, y: 0 }, { x: 4, y: 4 }, { x: 0, y: 4 }];
  const diamond = [{ x: 6, y: 2 }, { x: 8, y: 4 }, { x: 6, y: 6 }, { x: 4, y: 4 }];
  assert.equal(sat(square, diamond), true);
  assert.equal(sat(square, diamond.map(p => ({ x: p.x + 1, y: p.y }))), false);
  assert.equal(sat(diamond, square), true);
  assert.throws(() => sat([], square), TypeError);
  assert.throws(() => sat([{ x: 0, y: 0 }, { x: 1, y: 0 }, { x: 2, y: 0 }], square), RangeError);
  assert.throws(() => sat(square, [{ x: NaN, y: 0 }, { x: 2, y: 0 }, { x: 1, y: 2 }]), TypeError);
});

test('integrate applies constant acceleration with finite, atomic updates', () => {
  const body = { x: 0, y: 5, vx: 4, vy: 0, ax: 2, ay: -10 };
  assert.equal(integrate(body, 0.5), body);
  assert.deepEqual(body, { x: 2.25, y: 3.75, vx: 5, vy: -5, ax: 2, ay: -10 });
  const still = { x: 1, y: 2 };
  integrate(still, 0);
  assert.equal(still.x, 1);
  assert.throws(() => integrate(body, -1), RangeError);
  assert.throws(() => integrate(body, NaN), TypeError);
  const huge = { x: Number.MAX_VALUE, y: 0, vx: Number.MAX_VALUE };
  assert.throws(() => integrate(huge, 2), TypeError);
  assert.equal(huge.x, Number.MAX_VALUE);
});

test('A* returns shortest legal paths and handles impossible or malformed grids', () => {
  const grid = [[0, 1, 0, 0], [0, 1, 0, 1], [0, 0, 0, 0]];
  const path = astar(grid, { x: 0, y: 0 }, { x: 3, y: 0 });
  assert.equal(path.length, 8);
  assert.deepEqual(path[0], { x: 0, y: 0 });
  assert.deepEqual(path.at(-1), { x: 3, y: 0 });
  for (let i = 1; i < path.length; i++) {
    assert.equal(grid[path[i].y][path[i].x], 0);
    assert.equal(Math.abs(path[i].x - path[i - 1].x) + Math.abs(path[i].y - path[i - 1].y), 1);
  }
  assert.deepEqual(astar([[0]], { x: 0, y: 0 }, { x: 0, y: 0 }), [{ x: 0, y: 0 }]);
  assert.deepEqual(astar([[0, 1, 0]], { x: 0, y: 0 }, { x: 2, y: 0 }), []);
  assert.deepEqual(astar(grid, { x: -1, y: 0 }, { x: 0, y: 0 }), []);
  assert.throws(() => astar([[0], [0, 1]], { x: 0, y: 0 }, { x: 0, y: 0 }), TypeError);
  assert.throws(() => astar([[NaN]], { x: 0, y: 0 }, { x: 0, y: 0 }), TypeError);
  assert.throws(() => astar(grid, { x: 0.5, y: 0 }, { x: 0, y: 0 }), TypeError);
});

test('difficulty and score multipliers grow within bounds', () => {
  assert.deepEqual(difficulty(1), { level: 1, speed: 1, enemyRate: 1.5, multiplier: 1 });
  assert.ok(difficulty(4).speed > difficulty(1).speed);
  assert.ok(difficulty(4).enemyRate < difficulty(1).enemyRate);
  assert.ok(difficulty(1000).enemyRate > 0);
  assert.ok(difficulty(2).speed - difficulty(1).speed > difficulty(100).speed - difficulty(99).speed);
  assert.ok(difficulty(2).enemyRate - 0.25 < difficulty(1).enemyRate - 0.25);
  assert.ok(difficulty(100).enemyRate >= 0.25);
  assert.ok(difficulty(100).speed < 2.3);
  assert.deepEqual(difficulty(Number.MAX_VALUE), difficulty(100));
  assert.deepEqual(difficulty(4.9), difficulty(4));
  assert.equal(scoreMultiplier(0), 1);
  assert.equal(scoreMultiplier(10), 1.5);
  assert.equal(scoreMultiplier(9999), 5);
  assert.throws(() => difficulty(0), RangeError);
  assert.throws(() => difficulty(Infinity), TypeError);
  assert.throws(() => scoreMultiplier(-1), RangeError);
});

test('twelve distinct genres declare honest completion, instructions and upgrades', () => {
  assert.equal(arcadePlugins.length, 12);
  assert.equal(new Set(arcadePlugins.map(p => p.manifest.id)).size, 12);
  assert.equal(new Set(arcadePlugins.map(p => p.manifest.genre)).size, 12);
  assert.equal(arcadePlugins.filter(p => p.manifest.status === 'complete').length, 4);
  assert.equal(arcadePlugins.filter(p => p.manifest.status === 'minimal').length, 8);
  assert.equal(new Set(arcadePlugins.map(p => `${p.manifest.sound.type}/${p.manifest.sound.base}`)).size, 12);
  for (const { manifest: m } of arcadePlugins) {
    assert.equal(m.version, '1.0.0');
    assert.ok(m.description.length > 40);
    assert.ok(m.controls.length > 25);
    assert.ok(m.upgrades.length > 0);
    assert.ok(['sine', 'triangle', 'square', 'sawtooth'].includes(m.sound.type));
    assert.ok(Number.isFinite(m.sound.base) && m.sound.base > 0);
    for (const u of m.upgrades) assert.ok(u.id && u.title && u.cost > 0);
  }
});

for (const { manifest } of arcadePlugins) {
  test(`${manifest.id}: headless updates/render, finite snapshots and lifecycle`, () => {
    const h = harness(manifest.id);
    assert.equal(h.game.serialize().over, false);
    h.game.render(0.5);
    assert.ok(h.renderCalls.some(c => c[0] === 'fillText'));
    assert.throws(() => h.game.update(NaN), TypeError);
    assert.throws(() => h.game.update(-1), TypeError);
    for (let i = 0; i < 1200; i++) {
      if (i % 31 === 0) h.tapped.add('fire');
      if (i % 90 === 0) h.tapped.add('up');
      h.held.clear();
      if (i % 240 < 100) h.held.add('right');
      else if (i % 240 > 130) h.held.add('left');
      h.held.add('fire');
      h.step();
    }
    const snapshot = h.game.serialize();
    const check = value => {
      if (typeof value === 'number') assert.ok(Number.isFinite(value));
      else if (value && typeof value === 'object') Object.values(value).forEach(check);
    };
    check(snapshot);
    assert.ok(snapshot.score >= 0);
    assert.ok(snapshot.level >= 1);
    snapshot.score = -99;
    assert.ok(h.game.serialize().score >= 0, 'snapshots must not mutate live state');
    h.game.destroy();
    const noAudioContext = { ...h.context, audio: undefined, camera: undefined, save: undefined };
    const silent = arcadePlugins.find(p => p.manifest.id === manifest.id).create(noAudioContext);
    silent.update(1 / 60); silent.render(0); silent.destroy();
  });
}

test('shooter moves, fires, scores and ends once when invaders escape', () => {
  const h = harness('space-shooter', ['twin-shot']);
  h.held.add('right'); h.held.add('fire');
  let snapshot = h.step(60);
  assert.ok(snapshot.data.player.x > 480);
  assert.ok(snapshot.data.shots.length >= 2);
  assert.ok(h.tones.length);
  h.held.clear();
  h.step(18000);
  assert.equal(h.finishes.length, 1);
  assert.ok(h.saves.length >= 1);
  assert.equal(h.game.serialize().over, true);
  snapshot = h.game.serialize(); h.step(120);
  assert.deepEqual(h.game.serialize(), snapshot);
});

test('breaker launches, wide-paddle changes mechanics and missed balls end run', () => {
  const base = harness('brick-breaker'), wide = harness('brick-breaker', ['wide-paddle']);
  assert.ok(wide.game.serialize().data.paddle.w > base.game.serialize().data.paddle.w);
  base.tap('confirm');
  assert.equal(base.game.serialize().data.waiting, false);
  base.held.add('left');
  for (let i = 0; i < 15000 && !base.game.serialize().over; i++) {
    if (base.game.serialize().data.waiting) base.tapped.add('confirm');
    base.step();
  }
  assert.equal(base.finishes.length, 1);
  assert.ok(base.game.serialize().score > 0, 'ball should reach and hit bricks before a miss');
});

test('snake begins safely, slower upgrade changes pace and wall collision loses', () => {
  const base = harness('snake'), slow = harness('snake', ['slow-snake']);
  base.step(12); slow.step(12);
  assert.ok(base.game.serialize().data.body[0].x > slow.game.serialize().data.body[0].x);
  base.step(500);
  assert.equal(base.finishes.length, 1);
  assert.equal(base.game.serialize().lives, 0);
});

test('snake rejects reverse steering and rewards reachable fruit', () => {
  const h = harness('snake');
  h.held.add('left'); h.step(12);
  assert.equal(h.game.serialize().data.direction.x, 1);
  h.held.clear();
  // Follow shortest routes in the empty garden until at least one fruit is eaten.
  for (let i = 0; i < 300 && h.game.serialize().score === 0; i++) {
    const { body, food, direction } = h.game.serialize().data;
    const grid = Array.from({ length: 14 }, () => Array(30).fill(0));
    body.slice(1).forEach(p => { grid[p.y][p.x] = 1; });
    const path = astar(grid, body[0], food);
    if (path.length < 2) break;
    const dx = path[1].x - body[0].x, dy = path[1].y - body[0].y;
    if (dx === -direction.x && dy === -direction.y) break;
    h.held.clear(); h.held.add(dx < 0 ? 'left' : dx > 0 ? 'right' : dy < 0 ? 'up' : 'down');
    h.step(11);
  }
  assert.ok(h.game.serialize().score > 0);
});

test('maze starts with reachable pellets, walls block movement, pathfinding ghosts eventually catch idle player', () => {
  const h = harness('maze-chase');
  h.held.add('left'); h.step(20);
  assert.deepEqual(h.game.serialize().data.player, { x: 1, y: 1 });
  h.held.clear(); h.held.add('right'); h.step(9);
  assert.ok(h.game.serialize().score > 0);
  h.held.clear(); h.step(18000);
  assert.equal(h.finishes.length, 1);
});

test('minimal prototypes have distinct working actions and upgrades', () => {
  const platform = harness('platformer'); platform.step(20);
  const y = platform.game.serialize().data.player.y;
  platform.tap('up'); assert.ok(platform.game.serialize().data.player.y < y);
  const jump = harness('platformer', ['high-jump']); jump.step(20); jump.tap('up');
  assert.ok(jump.game.serialize().data.player.vy < platform.game.serialize().data.player.vy);
  const run = harness('endless-runner'); run.tap('up');
  assert.ok(run.game.serialize().data.player.vy < 0); run.step(3000); assert.equal(run.finishes.length, 1);
  const race = harness('racing'); race.held.add('right'); race.step(30);
  assert.ok(race.game.serialize().data.player.x > 460);
  const fight = harness('fighting'); fight.step(300);
  const enemyHP = fight.game.serialize().data.enemyHP; fight.tap('fire');
  assert.ok(fight.game.serialize().data.enemyHP < enemyHP);
  const blocks = harness('falling-blocks'); blocks.tap('fire');
  assert.ok(blocks.game.serialize().data.board.some(row => row.some(Boolean)));
  const pin = harness('pinball'); pin.tap('confirm');
  assert.equal(pin.game.serialize().data.waiting, false);
  assert.ok(pin.game.serialize().data.ball.vy < 0);
  const rhythm = harness('rhythm');
  rhythm.step(40);
  const note = rhythm.game.serialize().data.notes[0];
  assert.ok(note);
  while (rhythm.game.serialize().data.notes[0]?.y < 415) rhythm.step();
  const lane = rhythm.game.serialize().data.notes[0].lane;
  rhythm.tap(['left', 'down', 'up', 'right'][lane]);
  assert.ok(rhythm.game.serialize().score > 0);
  const tower = harness('tower-defense'); tower.tap('fire'); tower.step(1200);
  assert.equal(tower.game.serialize().data.towers.length, 1);
  assert.ok(tower.game.serialize().data.killed > 0);
});

test('falling-block overflow, rhythm misses, pinball drains and defense leaks have finite losses', () => {
  const block = harness('falling-blocks');
  for (let i = 0; i < 100 && !block.game.serialize().over; i++) block.tap('fire');
  assert.equal(block.finishes.length, 1);
  const rhythm = harness('rhythm'); rhythm.step(2400); assert.equal(rhythm.finishes.length, 1);
  const pin = harness('pinball');
  for (let i = 0; i < 10000 && !pin.game.serialize().over; i++) {
    if (pin.game.serialize().data.waiting) pin.tapped.add('fire');
    pin.step();
  }
  assert.equal(pin.finishes.length, 1);
  const defense = harness('tower-defense'); defense.step(18000);
  assert.equal(defense.finishes.length, 1);
});

test('platform falls, traffic collisions and rival attacks end their runs', () => {
  const platform = harness('platformer');
  platform.held.add('right'); platform.step(3000);
  assert.equal(platform.finishes.length, 1);
  const race = harness('racing'); race.step(18000);
  assert.equal(race.finishes.length, 1);
  const fight = harness('fighting'); fight.step(18000);
  assert.equal(fight.finishes.length, 1);
});

test('fighting rewards defeated rivals with harder levels', () => {
  const fight = harness('fighting', ['long-reach']);
  for (let frame = 0; frame < 1500 && fight.game.serialize().level === 1; frame++) {
    const { player, enemy } = fight.game.serialize().data;
    fight.held.clear();
    if (Math.abs(player.x - enemy.x) > 85) fight.held.add(player.x < enemy.x ? 'right' : 'left');
    if (frame % 21 === 0) fight.tapped.add('fire');
    fight.step();
  }
  assert.equal(fight.game.serialize().level, 2);
  assert.ok(fight.game.serialize().score >= 150);
  assert.ok(fight.game.serialize().data.enemyHP > 70);
});

for (const { manifest } of arcadePlugins) {
  test(`${manifest.id}: resumes full live state and timers from serialized save`, () => {
    const original = harness(manifest.id, manifest.upgrades.map(u => u.id));
    original.tap('fire');
    original.step(179);
    const saved = original.game.serialize();
    assert.equal(saved.over, false);
    const restored = harness(manifest.id, manifest.upgrades.map(u => u.id), { version: '1.0.0', data: saved });
    assert.deepEqual(restored.game.serialize(), saved);
    saved.score = -200;
    assert.ok(restored.game.serialize().score >= 0, 'load must clone saved objects');
    original.step(180); restored.step(180);
    assert.deepEqual(restored.game.serialize(), original.game.serialize(), 'physical state and internal timers continue');
    restored.game.destroy();
    assert.deepEqual(restored.saves.at(-1), restored.game.serialize());
  });
}

test('corrupt saves are ignored and live sessions autosave full state', () => {
  const invalid = harness('snake').game.serialize(); invalid.data.body = null;
  const recovered = harness('snake', [], invalid);
  assert.equal(recovered.game.serialize().data.body.length, 3);
  const h = harness('space-shooter'); h.step(310);
  assert.ok(h.saves.length >= 1);
  assert.ok(Array.isArray(h.saves[0].data.enemies));
  assert.equal(h.saves[0].game, 'space-shooter');
});

test('primary renderers use alpha interpolation without changing simulation state', () => {
  for (const id of ['space-shooter', 'brick-breaker', 'snake', 'maze-chase']) {
    const h = harness(id);
    h.held.add('right');
    const before = h.game.serialize();
    h.step(id === 'snake' ? 11 : id === 'maze-chase' ? 8 : 1);
    const after = h.game.serialize();
    h.renderCalls.length = 0; h.game.render(0);
    const startCalls = structuredClone(h.renderCalls);
    h.renderCalls.length = 0; h.game.render(0.5);
    const halfCalls = structuredClone(h.renderCalls);
    h.renderCalls.length = 0; h.game.render(1);
    const endCalls = structuredClone(h.renderCalls);
    assert.notDeepEqual(startCalls, endCalls, `${id} must interpolate its moving primary body`);
    assert.notDeepEqual(halfCalls, endCalls, `${id} must render an intermediate state`);
    assert.deepEqual(h.game.serialize(), after, `${id} rendering must not mutate state`);
    assert.ok(after.time > before.time);
  }
});

test('supplied RNG drives deterministic sessions without Math.random fallback', () => {
  const fallback = Math.random;
  Math.random = () => { throw new Error('Unexpected unseeded randomness'); };
  try {
    for (const { manifest } of arcadePlugins) {
      const first = harness(manifest.id), second = harness(manifest.id);
      first.tap('fire'); second.tap('fire');
      first.step(240); second.step(240);
      assert.deepEqual(first.game.serialize(), second.game.serialize(), manifest.id);
    }
  } finally { Math.random = fallback; }
});

function rejectsSave(id, corrupt) {
  const fresh = harness(id).game.serialize(), saved = structuredClone(fresh);
  saved.score = 123; saved.time = 12;
  corrupt(saved.data, saved);
  const h = harness(id, [], saved);
  assert.deepEqual(h.game.serialize(), fresh, `${id}: invalid save must not partially restore`);
  assert.doesNotThrow(() => { h.step(180); h.game.render(0.5); });
}

const corruptions = {
  'space-shooter': [
    d => { d.shots = [null]; }, d => { d.enemies = [null]; }, d => { d.hostile = [null]; },
    d => { d.shots = Array(1); }, d => { d.shots = [{ x: 0, y: 0 }]; },
    d => { d.enemies = [{ x: 0, y: 0, w: 28, h: 25, phase: 0, fire: 'soon' }]; },
  ],
  'brick-breaker': [
    d => { d.bricks = []; }, d => { d.bricks[0] = null; }, d => { d.bricks.pop(); },
    d => { d.bricks[0].hp = 3; }, d => { d.bricks[1] = { ...d.bricks[0] }; },
    d => { d.bricks[0].x = 36; },
  ],
  snake: [
    d => { d.body = []; }, d => { d.body = [null]; }, d => { d.body.length = 1; },
    d => { d.body[0].x = 30; }, d => { d.body[1] = { ...d.body[0] }; },
    d => { d.body[1].y = 10; }, d => { d.food = { ...d.body[0] }; },
    d => { d.queued = { x: 0, y: 0 }; }, d => { d.queued = { x: -1, y: 0 }; },
  ],
  'maze-chase': [
    d => { d.ghosts = []; }, d => { d.ghosts = [null, null]; },
    d => { d.ghosts[0].x = 19; }, d => { d.player = { x: 0, y: 0 }; },
    d => { d.pellets = [null]; }, d => { d.pellets = ['0,0']; },
    d => { d.pellets.push(d.pellets[0]); }, d => { d.direction = { x: 1, y: 1 }; },
  ],
  platformer: [
    d => { d.coins = []; }, d => { d.coins[0] = null; }, d => { d.coins.push(true); },
    d => { d.player = null; }, d => { d.player.w = -25; },
  ],
  'endless-runner': [
    d => { d.obstacles = [null]; },
    d => { d.obstacles = [{ x: 960, y: 418, w: -1, h: 40 }]; },
    d => { d.player.vy = NaN; }, d => { d.spawn = Infinity; },
  ],
  racing: [
    d => { d.cars = [null]; },
    d => { d.cars = [{ x: 305, y: 60, w: 48, h: 60, baseX: 999, phase: 0 }]; },
    d => { d.player.h = 0; },
  ],
  fighting: [
    d => { d.player = null; }, d => { d.enemy = []; },
    d => { d.hp = '100'; }, d => { d.enemyHP = 0; },
  ],
  'falling-blocks': [
    d => { d.board = []; }, d => { d.board.pop(); }, d => { d.board[0].pop(); },
    d => { d.board[0].push(0); }, d => { d.board[0] = null; },
    d => { d.board[0] = Array(10); }, d => { d.board[0][0] = 2; },
    d => { d.piece.cells = []; }, d => { d.piece.cells = [null, null, null]; },
    d => { d.piece.x = 10; }, d => { d.piece.y = 18; },
    d => { d.piece.cells = [[0, 0], [0, 0], [1, 0]]; },
    d => { const [x, y] = d.piece.cells[0]; d.board[d.piece.y + y][d.piece.x + x] = 1; },
    d => { d.piece.x = 0; d.piece.cells = [[-1, 0], [0, 0], [1, 0]]; },
  ],
  pinball: [
    d => { d.ball = null; }, d => { d.ball.r = -9; }, d => { d.ball.vx = Infinity; },
  ],
  rhythm: [
    d => { d.notes = [null]; }, d => { d.notes = [{ lane: 4, y: 60 }]; },
    d => { d.notes = [{ lane: -1, y: 60 }]; }, d => { d.health = 0; },
  ],
  'tower-defense': [
    d => { d.towers = [null]; }, d => { d.enemies = [null]; }, d => { d.selected = 5; },
    d => { d.towers = [{ x: 170, y: 210, pad: 5, cooldown: 0 }]; },
    d => { d.towers = [{ x: 171, y: 210, pad: 0, cooldown: 0 }]; },
    d => { d.towers = Array(2).fill({ x: 170, y: 210, pad: 0, cooldown: 0 }); },
    d => { d.enemies = [{ x: 0, y: 280, hp: 0, dead: false }]; },
  ],
};
for (const [id, cases] of Object.entries(corruptions)) {
  test(`${id}: rejects malformed saves and retains a healthy initialized state`, () => {
    cases.forEach(corrupt => rejectsSave(id, corrupt));
  });
}

test('all games reject malformed shared state before restoring entities', () => {
  for (const { manifest } of arcadePlugins) {
    for (const change of [
      s => { s.score = NaN; }, s => { s.score = -1; }, s => { s.level = 0; },
      s => { s.level = 1.5; }, s => { s.time = Infinity; }, s => { s.rng = 0x100000000; },
      s => { s.lives = 11; }, s => { s.over = true; },
      s => { s.data = {}; }, s => { s.data.unexpected = { nested: null }; },
    ]) rejectsSave(manifest.id, (_, s) => change(s));
  }
});
