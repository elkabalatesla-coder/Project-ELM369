import { aabb, circles, astar, difficulty, scoreMultiplier } from '../math/arcade.mjs';

const W = 960, H = 540, clamp = (n, lo, hi) => Math.max(lo, Math.min(hi, n));
const soundProfiles = {
  'space-shooter': { type: 'triangle', base: 110 },
  'brick-breaker': { type: 'sine', base: 440 },
  snake: { type: 'square', base: 196 },
  'maze-chase': { type: 'triangle', base: 246.94 },
  platformer: { type: 'sine', base: 329.63 },
  'endless-runner': { type: 'sawtooth', base: 164.81 },
  racing: { type: 'sawtooth', base: 82.41 },
  fighting: { type: 'square', base: 146.83 },
  'falling-blocks': { type: 'sine', base: 261.63 },
  pinball: { type: 'triangle', base: 392 },
  rhythm: { type: 'square', base: 293.66 },
  'tower-defense': { type: 'sine', base: 220 },
};
const upgrade = (id, title, cost = 80) => ({ id, title, cost });
const rect = (g, x, y, w, h, color) => { g.fillStyle = color; g.fillRect(x, y, w, h); };
const text = (g, value, x, y, size = 18, color = '#eaf4ff') => {
  g.fillStyle = color; g.font = `${size}px system-ui`; g.fillText(String(value), x, y);
};
const orb = (g, x, y, radius, color) => {
  g.fillStyle = color; g.beginPath(); g.arc(x, y, radius, 0, Math.PI * 2); g.fill();
};
const copy = value => JSON.parse(JSON.stringify(value));
const replace = (target, source) => target.splice(0, target.length, ...copy(source));
const positions = (value, visit, path = '', seen = new WeakSet()) => {
  if (!value || typeof value !== 'object' || seen.has(value)) return;
  seen.add(value);
  if (Number.isFinite(value.x) && Number.isFinite(value.y)) visit(value, path);
  for (const [key, child] of Object.entries(value)) positions(child, visit, `${path}/${key}`, seen);
};
const finiteTree = value => {
  if (typeof value === 'number') return Number.isFinite(value);
  if (!value || typeof value !== 'object') return true;
  return Object.values(value).every(finiteTree);
};
const compatible = (template, value) => {
  if (Array.isArray(template)) return Array.isArray(value) && value.length <= 4096 &&
    (!template.length || value.every(item => compatible(template[0], item)));
  if (template && typeof template === 'object') return value && typeof value === 'object' &&
    !Array.isArray(value) && Object.keys(template).every(key => compatible(template[key], value[key]));
  return typeof value === typeof template && (typeof value !== 'number' || Number.isFinite(value));
};

function plugin(id, title, genre, status, description, controls, upgrades, build, color) {
  return {
    manifest: {
      id, title, genre, status, version: '1.0.0', description, controls,
      config: { width: W, height: H, fixedStep: 1 / 60 },
      features: ['scoring', 'difficulty', 'upgrades', 'keyboard', 'save-resume', 'interpolation'],
      upgrades, sound: { ...soundProfiles[id], bus: 'sfx', positional: true },
    },
    create(context) {
      const g = context.ctx, input = context.input;
      const state = { score: 0, level: 1, lives: 3, time: 0, over: false };
      let randomState = (context.random?.int?.(0x100000000) ?? Math.floor(Math.random() * 0x100000000)) >>> 0;
      const has = key => context.upgrades?.has(key) ?? false;
      const down = key => Boolean(input?.down?.(key));
      const pressed = key => Boolean(input?.pressed?.(key));
      const tone = (freq = 440, duration = 0.06, x = W / 2) =>
        context.audio?.tone?.(freq, duration, 'sfx', { x, y: H / 2 });
      const end = () => {
        if (state.over) return;
        state.over = true;
        context.save?.(snapshot());
        context.finish?.(state.score);
      };
      const add = points => { state.score += Math.max(0, Math.round(points)); };
      const rand = max => {
        // Persist this arcade-only stream so resumed waves and fruit remain deterministic.
        randomState = (Math.imul(randomState, 1664525) + 1013904223) >>> 0;
        return Math.floor(randomState / 0x100000000 * max);
      };
      const api = { state, has, down, pressed, tone, end, add, rand, context };
      const game = build(api);
      function snapshot() { return copy({ ...state, game: id, rng: randomState, data: game.data() }); }
      let previous = new WeakMap(), previousPaths = new Map(), saveTimer = 0;
      const remember = () => {
        previous = new WeakMap(); previousPaths = new Map();
        positions(game.data(), (body, path) => {
          const p = { x: body.x, y: body.y };
          previous.set(body, p); previousPaths.set(path, p);
        });
      };
      const saved = context.load?.();
      const loaded = saved?.game === id ? saved : saved?.data?.game === id ? saved.data : null;
      if (loaded && !loaded.over && compatible(snapshot(), loaded) && finiteTree(loaded) && loaded.score >= 0 &&
          loaded.level >= 1 && loaded.lives > 0 && loaded.time >= 0 &&
          Number.isInteger(loaded.rng) && loaded.rng >= 0 && loaded.rng < 0x100000000 &&
          loaded.data && Object.keys(game.data()).every(key => Object.hasOwn(loaded.data, key))) {
        game.restore(copy(loaded.data));
        for (const key of Object.keys(state)) state[key] = loaded[key];
        randomState = loaded.rng;
      }
      remember();
      return {
        update(dt) {
          if (!Number.isFinite(dt) || dt < 0) throw new TypeError('Expected nonnegative finite timestep');
          if (state.over || dt === 0) return;
          remember();
          // Bound stalled-tab steps. Games with fast bodies subdivide further themselves.
          dt = Math.min(dt, 0.1);
          state.time += dt;
          game.update(dt);
          saveTimer += dt;
          if (!state.over && saveTimer >= 5) { saveTimer = 0; context.save?.(snapshot()); }
          state.score = Math.max(0, Math.round(state.score));
          if (state.lives <= 0) end();
          const target = game.target?.();
          if (target && context.camera) {
            if (typeof context.camera.follow === 'function') context.camera.follow(target);
            else context.camera.target = { x: target.x, y: target.y };
          }
        },
        render(alpha = 1) {
          if (!g) return;
          alpha = Number.isFinite(alpha) ? clamp(alpha, 0, 1) : 1;
          g.save();
          rect(g, 0, 0, W, H, color);
          const restored = [];
          positions(game.data(), (body, path) => {
            const prev = id === 'snake' ? previousPaths.get(path) : previous.get(body);
            if (!prev) return;
            restored.push([body, body.x, body.y]);
            body.x = prev.x + (body.x - prev.x) * alpha;
            body.y = prev.y + (body.y - prev.y) * alpha;
          });
          try { game.render(g); }
          finally { for (const [body, x, y] of restored) { body.x = x; body.y = y; } }
          rect(g, 0, 0, W, 40, '#07101feb');
          text(g, `${title}   Score ${state.score}   Level ${state.level}   Lives ${state.lives}`, 16, 27);
          text(g, controls, 14, H - 12, 14);
          if (state.over) {
            rect(g, 240, 205, 480, 100, '#07101fee');
            text(g, `GAME OVER — ${state.score} points`, 280, 265, 26);
          }
          g.restore();
        },
        serialize: snapshot,
        destroy() { context.save?.(snapshot()); game.destroy?.(); },
      };
    },
  };
}

function shooter(a) {
  const { state: s, down, has, rand, add, tone, end } = a;
  const p = { x: 480, y: 452, w: 30, h: 26 }, shots = [], enemies = [], hostile = [];
  let spawn = 0.6, fire = 0, hurt = 0, kills = 0;
  return {
    target: () => p,
    update(dt) {
      const d = difficulty(s.level);
      hurt -= dt; fire -= dt; spawn -= dt;
      p.x = clamp(p.x + (down('right') - down('left')) * 370 * dt, 10, W - p.w - 10);
      p.y = clamp(p.y + (down('down') - down('up')) * 300 * dt, 300, H - 65);
      if (down('fire') && fire <= 0) {
        shots.push({ x: p.x + 12, y: p.y - 10, w: 6, h: 14 });
        if (has('twin-shot')) shots.push({ x: p.x + 27, y: p.y - 5, w: 5, h: 12 });
        fire = 0.18; tone(720, 0.025, p.x);
      }
      if (spawn <= 0) {
        enemies.push({ x: 25 + rand(880), y: 45, w: 28, h: 25, phase: rand(628) / 100, fire: 1.2 });
        spawn = d.enemyRate;
      }
      for (const shot of shots) shot.y -= 600 * dt;
      for (const shot of hostile) { shot.y += (170 + s.level * 5) * dt; shot.x += shot.vx * dt; }
      for (const e of enemies) {
        e.y += Math.min(180, 50 * d.speed) * dt;
        e.x = clamp(e.x + Math.sin(s.time * 2 + e.phase) * 65 * dt, 0, W - e.w);
        e.fire -= dt;
        if (e.fire <= 0) {
          hostile.push({ x: e.x + 12, y: e.y + 20, w: 7, h: 10,
            vx: clamp((p.x - e.x) * 0.22, -85, 85) });
          e.fire = Math.max(0.65, 2.5 - s.level * 0.12);
        }
        for (const shot of shots) {
          if (!shot.dead && !e.dead && aabb(e, shot)) {
            e.dead = shot.dead = true; add(20 * d.multiplier); kills++; tone(220, 0.08, e.x);
          }
        }
        if (!e.dead && (e.y > H - 50 || aabb(p, e))) {
          e.dead = true;
          if (hurt <= 0) { s.lives--; hurt = has('shield') ? 2 : 1; }
        }
      }
      for (const shot of hostile) if (!shot.dead && aabb(shot, p) && hurt <= 0) {
        shot.dead = true; s.lives--; hurt = has('shield') ? 2 : 1;
      }
      for (const list of [shots, hostile, enemies]) for (let i = list.length - 1; i >= 0; i--) {
        if (list[i].dead || list[i].y < 0 || list[i].y > H) list.splice(i, 1);
      }
      s.level = 1 + Math.floor(kills / 8);
      if (s.lives <= 0) end();
    },
    render(g) {
      for (let i = 0; i < 70; i++) orb(g, (i * 137) % W, (i * 73 + s.time * 20) % H, 1, '#8194c2');
      rect(g, p.x, p.y, p.w, p.h, hurt > 0 ? '#89b9d0' : '#35e8ff');
      for (const e of enemies) rect(g, e.x, e.y, e.w, e.h, '#ff5983');
      for (const shot of shots) rect(g, shot.x, shot.y, shot.w, shot.h, '#fff3b0');
      for (const shot of hostile) orb(g, shot.x, shot.y, 5, '#ff9255');
    },
    data: () => ({ player: p, shots, enemies, hostile, kills, spawn, fire, hurt }),
    restore(d) {
      Object.assign(p, d.player); replace(shots, d.shots); replace(enemies, d.enemies); replace(hostile, d.hostile);
      ({ kills, spawn, fire, hurt } = d);
    },
  };
}

function breaker(a) {
  const { state: s, down, pressed, has, add, tone } = a;
  const p = { x: 410, y: 465, w: has('wide-paddle') ? 145 : 105, h: 14 };
  const ball = { x: 465, y: 451, r: 8, vx: 140, vy: -255 };
  let bricks = [], waiting = true, cleared = 0;
  const level = () => {
    bricks = [];
    for (let y = 0; y < Math.min(7, 3 + s.level); y++) for (let x = 0; x < 10; x++)
      bricks.push({ x: 35 + x * 90, y: 65 + y * 28, w: 82, h: 20, hp: s.level > 2 && y < 2 ? 2 : 1 });
  };
  level();
  return {
    target: () => ball,
    update(dt) {
      p.x = clamp(p.x + (down('right') - down('left')) * 480 * dt, 0, W - p.w);
      if (waiting) {
        ball.x = p.x + p.w / 2; ball.y = p.y - 12;
        if (pressed('confirm') || down('fire')) waiting = false;
        else return;
      }
      const steps = Math.ceil(dt / 0.008), step = dt / steps;
      for (let i = 0; i < steps; i++) {
        const oldY = ball.y;
        ball.x += ball.vx * step; ball.y += ball.vy * step;
        if (ball.x < ball.r || ball.x > W - ball.r) { ball.x = clamp(ball.x, ball.r, W - ball.r); ball.vx *= -1; }
        if (ball.y < 48) { ball.y = 48; ball.vy = Math.abs(ball.vy); }
        if (ball.vy > 0 && oldY + ball.r <= p.y + 3 &&
            aabb({ x: ball.x - 8, y: ball.y - 8, w: 16, h: 16 }, p)) {
          const offset = (ball.x - p.x - p.w / 2) / (p.w / 2);
          const speed = Math.min(460, 290 + s.level * 15);
          ball.vx = offset * speed * 0.8;
          ball.vy = -Math.sqrt(speed * speed - ball.vx * ball.vx);
          ball.y = p.y - ball.r - 1; tone(440);
        }
        for (const b of bricks) {
          if (b.hp && aabb({ x: ball.x - 8, y: ball.y - 8, w: 16, h: 16 }, b)) {
            b.hp--; add(10 * s.level); tone(650);
            if (oldY + ball.r <= b.y) { ball.vy = -Math.abs(ball.vy); ball.y = b.y - ball.r - 0.1; }
            else if (oldY - ball.r >= b.y + b.h) { ball.vy = Math.abs(ball.vy); ball.y = b.y + b.h + ball.r + 0.1; }
            else {
              ball.x = ball.vx > 0 ? b.x - ball.r - 0.1 : b.x + b.w + ball.r + 0.1;
              ball.vx *= -1;
            }
            break;
          }
        }
        if (ball.y > H - 24) {
          s.lives--; waiting = true; ball.vx = 140; ball.vy = -255;
          break;
        }
      }
      if (bricks.every(b => !b.hp)) {
        cleared++; s.level++; add(100); level(); waiting = true;
      }
    },
    render(g) {
      for (const b of bricks) if (b.hp) rect(g, b.x, b.y, b.w, b.h, b.hp === 2 ? '#ffe28a' : ['#ff7e9f', '#a4a0ff', '#62e3ba'][Math.floor((b.y - 65) / 28) % 3]);
      rect(g, p.x, p.y, p.w, p.h, '#f9e4ac'); orb(g, ball.x, ball.y, ball.r, '#fff');
      if (waiting) text(g, 'FIRE / CONFIRM to launch', 345, 320, 22);
    },
    data: () => ({ paddle: p, ball, bricks, waiting, cleared }),
    restore(d) { Object.assign(p, d.paddle); Object.assign(ball, d.ball); ({ bricks, waiting, cleared } = d); },
  };
}

function snake(a) {
  const { state: s, pressed, down, has, rand, add, tone, end } = a;
  s.lives = 1;
  const cols = 30, rows = 14, cell = 28, ox = 60, oy = 65;
  const body = [{ x: 8, y: 7 }, { x: 7, y: 7 }, { x: 6, y: 7 }];
  let dir = { x: 1, y: 0 }, queued = dir, timer = 0, eaten = 0, food;
  const place = () => {
    const free = [];
    for (let y = 0; y < rows; y++) for (let x = 0; x < cols; x++)
      if (!body.some(p => p.x === x && p.y === y)) free.push({ x, y });
    food = free.length ? free[rand(free.length)] : null;
  };
  place();
  return {
    target: () => ({ x: ox + body[0].x * cell, y: oy + body[0].y * cell }),
    update(dt) {
      for (const [key, x, y] of [['left', -1, 0], ['right', 1, 0], ['up', 0, -1], ['down', 0, 1]]) {
        if ((pressed(key) || down(key)) && !(x === -dir.x && y === -dir.y)) { queued = { x, y }; break; }
      }
      timer += dt;
      const interval = Math.max(0.065, 0.18 - (s.level - 1) * 0.012) * (has('slow-snake') ? 1.25 : 1);
      if (timer < interval) return;
      timer -= interval; dir = queued;
      const head = { x: body[0].x + dir.x, y: body[0].y + dir.y };
      const eating = food && head.x === food.x && head.y === food.y;
      if (head.x < 0 || head.x >= cols || head.y < 0 || head.y >= rows ||
          body.slice(0, eating ? body.length : -1).some(p => p.x === head.x && p.y === head.y)) {
        s.lives = 0; end(); return;
      }
      body.unshift(head);
      if (eating) {
        eaten++; add(25 * scoreMultiplier(eaten)); s.level = 1 + Math.floor(eaten / 4); place(); tone(800);
        if (!food) { add(1000); end(); }
      } else body.pop();
    },
    render(g) {
      rect(g, ox - 4, oy - 4, cols * cell + 8, rows * cell + 8, '#315f42');
      rect(g, ox, oy, cols * cell, rows * cell, '#12291d');
      for (let i = body.length - 1; i >= 0; i--) rect(g, ox + body[i].x * cell + 2, oy + body[i].y * cell + 2, cell - 4, cell - 4, i ? '#5dca77' : '#e4ff9b');
      if (food) orb(g, ox + food.x * cell + cell / 2, oy + food.y * cell + cell / 2, 9, '#ff8c7a');
    },
    data: () => ({ body, food, direction: dir, queued, timer, eaten }),
    restore(d) { replace(body, d.body); ({ food, queued, timer, eaten } = d); dir = d.direction; },
  };
}

function maze(a) {
  const { state: s, down, has, add, tone, end } = a;
  const layout = [
    '###################', '#........#........#', '#.##.###.#.###.##.#',
    '#.................#', '#.##.#.#####.#.##.#', '#....#...#...#....#',
    '####.###.#.###.####', '#.................#', '#.##.###.#.###.##.#',
    '#........#........#', '###################',
  ];
  const grid = layout.map(row => [...row].map(c => c === '#' ? 1 : 0));
  const size = 37, ox = 128, oy = 63, p = { x: 1, y: 1 };
  let ghosts, pellets, timer = 0, ghostTimer = 0, invincible = 2, power = 0, direction = { x: 0, y: 0 }, desired = direction;
  const reset = () => {
    p.x = 1; p.y = 1; direction = desired = { x: 0, y: 0 };
    ghosts = [{ x: 17, y: 9 }, { x: 17, y: 1 }];
    invincible = has('maze-shield') ? 4 : 2;
  };
  const populate = () => {
    pellets = new Set();
    for (let y = 0; y < grid.length; y++) for (let x = 0; x < grid[y].length; x++)
      if (!grid[y][x] && (x !== 1 || y !== 1)) pellets.add(`${x},${y}`);
  };
  const walkable = (x, y) => grid[y]?.[x] === 0;
  const contact = () => {
    if (!ghosts.some(e => e.x === p.x && e.y === p.y)) return;
    if (power > 0) {
      ghosts.forEach(e => {
        if (e.x === p.x && e.y === p.y) {
          e.x = 17; e.y = p.x === 17 && p.y === 9 ? 1 : 9; add(100);
        }
      });
    } else if (invincible <= 0) { s.lives--; reset(); }
  };
  reset(); populate();
  return {
    target: () => ({ x: ox + p.x * size, y: oy + p.y * size }),
    update(dt) {
      invincible -= dt; power -= dt; timer += dt; ghostTimer += dt;
      for (const [key, x, y] of [['left', -1, 0], ['right', 1, 0], ['up', 0, -1], ['down', 0, 1]])
        if (down(key)) desired = { x, y };
      if (timer >= 0.13) {
        timer -= 0.13;
        if (walkable(p.x + desired.x, p.y + desired.y)) direction = desired;
        if (walkable(p.x + direction.x, p.y + direction.y)) { p.x += direction.x; p.y += direction.y; }
        if (pellets.delete(`${p.x},${p.y}`)) {
          add(10); tone(550, 0.025);
          if ((p.x === 1 || p.x === 17) && p.y === 9) power = 5;
        }
        contact();
      }
      const interval = Math.max(0.145, 0.36 - s.level * 0.018);
      if (ghostTimer >= interval) {
        ghostTimer -= interval;
        ghosts.forEach((e, i) => {
          const target = power > 0 ? { x: i ? 1 : 17, y: 9 } : p;
          const path = astar(grid, e, target);
          if (path.length > 1) Object.assign(e, path[1]);
        });
        contact();
      }
      if (!pellets.size) { s.level++; add(200); populate(); reset(); }
      if (s.lives <= 0) end();
    },
    render(g) {
      for (let y = 0; y < grid.length; y++) for (let x = 0; x < grid[y].length; x++) {
        if (grid[y][x]) rect(g, ox + x * size, oy + y * size, size - 2, size - 2, '#2941a0');
        else if (pellets.has(`${x},${y}`)) orb(g, ox + x * size + size / 2, oy + y * size + size / 2, (x === 1 || x === 17) && y === 9 ? 8 : 3, '#ffdc89');
      }
      orb(g, ox + p.x * size + size / 2, oy + p.y * size + size / 2, 13, invincible > 0 ? '#fffcc4' : '#ffd23f');
      ghosts.forEach((e, i) => orb(g, ox + e.x * size + size / 2, oy + e.y * size + size / 2, 13, power > 0 ? '#76d3ff' : i ? '#f278db' : '#ff647e'));
      if (power > 0) text(g, `POWER ${Math.ceil(power)}`, 15, 80, 17);
    },
    data: () => ({ player: p, ghosts, pellets: [...pellets], power, timer, ghostTimer, invincible, direction, desired }),
    restore(d) {
      Object.assign(p, d.player); pellets = new Set(d.pellets);
      ({ ghosts, power, timer, ghostTimer, invincible, direction, desired } = d);
    },
  };
}

function platformer(a) {
  // TODO: Expand the handcrafted platform route with moving platforms and bosses.
  const { state: s, down, pressed, has, add, tone } = a;
  const p = { x: 50, y: 420, w: 25, h: 34, vy: 0 }, platforms = [
    { x: 0, y: 465, w: 230, h: 25 }, { x: 280, y: 405, w: 160, h: 25 },
    { x: 495, y: 345, w: 160, h: 25 }, { x: 715, y: 285, w: 210, h: 25 },
  ];
  let grounded = false, coins = [true, true, true], hurt = 0;
  return {
    target: () => p,
    update(dt) {
      hurt -= dt;
      const sub = dt / 4;
      for (let i = 0; i < 4; i++) {
        if (i === 0 && grounded && (pressed('up') || pressed('fire'))) { p.vy = has('high-jump') ? -530 : -450; grounded = false; tone(500); }
        p.x = clamp(p.x + (down('right') - down('left')) * 230 * sub, 0, W - p.w);
        const oldBottom = p.y + p.h;
        p.vy += 1000 * sub; p.y += p.vy * sub; grounded = false;
        for (const platform of platforms) if (p.vy >= 0 && oldBottom <= platform.y + 1 && aabb(p, platform)) {
          p.y = platform.y - p.h; p.vy = 0; grounded = true;
        }
      }
      for (let i = 0; i < coins.length; i++) if (coins[i] && Math.hypot(p.x - platforms[i + 1].x - 70, p.y - platforms[i + 1].y + 50) < 42) {
        coins[i] = false; add(30);
      }
      const enemy = { x: 310 + Math.sin(s.time * (1 + s.level * 0.15)) * 45, y: 380, w: 22, h: 25 };
      if (aabb(p, enemy) && hurt <= 0) { s.lives--; hurt = 2; p.x = 50; p.y = 420; p.vy = 0; }
      if (p.y > H) { s.lives--; p.x = 50; p.y = 420; p.vy = 0; }
      if (p.x > 850 && p.y < 290) { add(150); s.level++; p.x = 50; p.y = 420; p.vy = 0; coins = [true, true, true]; }
    },
    render(g) {
      rect(g, 0, 400, W, 100, '#4d705e');
      platforms.forEach(b => rect(g, b.x, b.y, b.w, b.h, '#9ed686'));
      coins.forEach((on, i) => { if (on) orb(g, platforms[i + 1].x + 82, platforms[i + 1].y - 30, 9, '#ffe574'); });
      rect(g, 310 + Math.sin(s.time * (1 + s.level * 0.15)) * 45, 380, 22, 25, '#ed6675');
      rect(g, 875, 225, 6, 60, '#fff'); rect(g, 881, 225, 26, 20, '#ffd26b');
      rect(g, p.x, p.y, p.w, p.h, hurt > 0 ? '#fff' : '#7be4ff');
    },
    data: () => ({ player: p, coins, grounded, hurt }),
    restore(d) { Object.assign(p, d.player); ({ coins, grounded, hurt } = d); },
  };
}

function runner(a) {
  // TODO: Add branching routes and more obstacle silhouettes.
  const { state: s, pressed, has, rand } = a;
  s.lives = 1;
  const p = { x: 120, y: 420, w: 28, h: 38, vy: 0 };
  const obstacles = [];
  let spawn = 1.5, distance = 0;
  return {
    target: () => p,
    update(dt) {
      const ground = 458;
      if ((pressed('up') || pressed('fire')) && p.y + p.h >= ground - 1) p.vy = has('runner-jump') ? -570 : -490;
      p.vy += 1250 * dt; p.y += p.vy * dt;
      if (p.y + p.h > ground) { p.y = ground - p.h; p.vy = 0; }
      const speed = Math.min(490, 250 + s.level * 18);
      distance += speed * dt; s.score = Math.floor(distance / 12); s.level = 1 + Math.floor(distance / 2500);
      spawn -= dt;
      if (spawn <= 0) { obstacles.push({ x: W + 30, y: 418, w: 25 + rand(15), h: 40 }); spawn = 1.4 + rand(50) / 100; }
      for (const b of obstacles) { b.x -= speed * dt; if (aabb(p, b)) { s.lives = 0; a.end(); } }
      while (obstacles[0]?.x < -60) obstacles.shift();
    },
    render(g) {
      rect(g, 0, 458, W, 45, '#76628b');
      for (let i = 0; i < 12; i++) rect(g, ((i * 100 - distance) % 1100 + 1100) % 1100, 475, 45, 4, '#d6a3da');
      rect(g, p.x, p.y, p.w, p.h, '#ffd57d');
      obstacles.forEach(b => rect(g, b.x, b.y, b.w, b.h, '#f388a0'));
    },
    data: () => ({ player: p, obstacles, distance, spawn }),
    restore(d) { Object.assign(p, d.player); replace(obstacles, d.obstacles); ({ distance, spawn } = d); },
  };
}

function racing(a) {
  // TODO: Add cornering physics and opponent overtaking strategy.
  const { state: s, down, has, rand } = a;
  const p = { x: 460, y: 410, w: 35, h: 60 }, cars = [];
  let distance = 0, spawn = 1, hurt = 0;
  return {
    target: () => p,
    update(dt) {
      hurt -= dt;
      p.x = clamp(p.x + (down('right') - down('left')) * (has('race-grip') ? 420 : 310) * dt, 280, 645);
      const speed = (down('down') ? 140 : down('up') ? 320 : 230) + Math.min(160, s.level * 10);
      distance += speed * dt; s.score = Math.floor(distance / 15); s.level = 1 + Math.floor(distance / 3000);
      spawn -= dt;
      if (spawn <= 0) {
        const baseX = [305, 415, 525, 625][rand(4)];
        cars.push({ x: baseX, baseX, phase: rand(628) / 100, y: -70, w: 48, h: 60 });
        spawn = Math.max(0.55, 1.4 - s.level * 0.06);
      }
      for (const car of cars) {
        car.x = car.baseX + Math.sin(s.time * 1.7 + car.phase) * 18;
        car.y += speed * dt;
        if (aabb(p, car) && hurt <= 0) { s.lives--; hurt = has('race-grip') ? 1.8 : 1.2; }
      }
      while (cars[0]?.y > H) cars.shift();
    },
    render(g) {
      rect(g, 270, 40, 420, 465, '#343a4b');
      for (let lane = 1; lane <= 3; lane++) for (let i = 0; i < 9; i++)
        rect(g, 270 + lane * 105, (i * 70 + distance) % 550, 4, 35, '#dce5d9');
      cars.forEach(b => rect(g, b.x, b.y, b.w, b.h, '#ee8e6b'));
      rect(g, p.x, p.y, p.w, p.h, hurt > 0 ? '#fff' : '#83ecf2');
    },
    data: () => ({ player: p, cars, distance, spawn, hurt }),
    restore(d) { Object.assign(p, d.player); replace(cars, d.cars); ({ distance, spawn, hurt } = d); },
  };
}

function fighting(a) {
  // TODO: Expand the one-opponent duel with combos and selectable fighters.
  const { state: s, down, pressed, has, add, tone, end } = a;
  const p = { x: 260, y: 360, w: 48, h: 100 }, e = { x: 680, y: 360, w: 48, h: 100 };
  let hp = 100, enemyHP = 70, cooldown = 0, enemyCooldown = 1, flash = 0, enemyFlash = 0;
  return {
    target: () => p,
    update(dt) {
      cooldown -= dt; enemyCooldown -= dt; flash -= dt; enemyFlash -= dt;
      p.x = clamp(p.x + (down('right') - down('left')) * 240 * dt, 25, W - p.w - 25);
      const delta = p.x - e.x;
      if (Math.abs(delta) > 65) e.x += Math.sign(delta) * Math.min(170, 95 + s.level * 6) * dt;
      const range = Math.abs(p.x - e.x) < (has('long-reach') ? 125 : 100);
      if (pressed('fire') && cooldown <= 0) {
        cooldown = 0.32; flash = 0.12; tone(200);
        if (range) { enemyHP -= has('long-reach') ? 24 : 18; add(10); enemyFlash = 0.15; }
      }
      if (Math.abs(p.x - e.x) < 105 && enemyCooldown <= 0) {
        hp -= down('down') ? 3 : 13; enemyCooldown = Math.max(0.45, 1.1 - s.level * 0.04);
      }
      if (enemyHP <= 0) {
        s.level++; add(150); enemyHP = 70 + s.level * 12; hp = Math.min(100, hp + 20); e.x = p.x < 480 ? 760 : 150;
      }
      s.lives = Math.ceil(Math.max(0, hp) / 34);
      if (hp <= 0) end();
    },
    render(g) {
      rect(g, 40, 460, 880, 25, '#876778');
      rect(g, 120, 70, hp * 3, 18, '#6df7b3');
      rect(g, 560, 70, Math.max(0, enemyHP) / (70 + (s.level > 1 ? s.level * 12 : 0)) * 280, 18, '#ff8194');
      rect(g, p.x, p.y + (down('down') ? 20 : 0), p.w, down('down') ? 80 : p.h, '#79d5ff');
      rect(g, e.x, e.y, e.w, e.h, enemyFlash > 0 ? '#fff' : '#ef8a91');
      if (flash > 0) rect(g, p.x + (e.x > p.x ? 40 : -55), 380, 60, 18, '#ffe1a3');
      text(g, 'HP', 70, 85); text(g, 'RIVAL', 800, 115);
    },
    data: () => ({ player: p, enemy: e, hp, enemyHP, cooldown, enemyCooldown, flash, enemyFlash }),
    restore(d) { Object.assign(p, d.player); Object.assign(e, d.enemy); ({ hp, enemyHP, cooldown, enemyCooldown, flash, enemyFlash } = d); },
  };
}

function blocks(a) {
  // TODO: Add rotation kicks, a hold queue and a complete seven-piece set.
  const { state: s, pressed, down, has, rand, add, end } = a;
  s.lives = 1;
  const cols = 10, rows = 18, cell = 23, ox = 365, oy = 64;
  const board = Array.from({ length: rows }, () => Array(cols).fill(0));
  const shapes = [[[0, 0], [1, 0], [0, 1], [1, 1]], [[-1, 0], [0, 0], [1, 0]], [[0, 0], [1, 0], [0, 1]]];
  let piece, timer = 0, repeat = 0, lines = 0;
  const spawn = () => { piece = { x: 4, y: 0, cells: shapes[rand(shapes.length)].map(p => [...p]) }; if (!valid(piece.x, piece.y, piece.cells)) { s.lives = 0; end(); } };
  const valid = (x, y, cells) => cells.every(([dx, dy]) => x + dx >= 0 && x + dx < cols && y + dy >= 0 && y + dy < rows && !board[y + dy][x + dx]);
  const lock = () => {
    piece.cells.forEach(([dx, dy]) => { board[piece.y + dy][piece.x + dx] = 1; });
    add(5);
    for (let y = rows - 1; y >= 0; y--) if (board[y].every(Boolean)) {
      board.splice(y, 1); board.unshift(Array(cols).fill(0)); lines++; add(100 * s.level); y++;
    }
    s.level = 1 + Math.floor(lines / 3); spawn();
  };
  spawn();
  return {
    update(dt) {
      timer += dt; repeat -= dt;
      if (repeat <= 0) {
        const dx = down('right') - down('left');
        if (dx && valid(piece.x + dx, piece.y, piece.cells)) piece.x += dx;
        repeat = 0.12;
      }
      if (pressed('up')) {
        const rotated = piece.cells.map(([x, y]) => [-y, x]);
        if (valid(piece.x, piece.y, rotated)) piece.cells = rotated;
      }
      if (pressed('fire')) {
        while (valid(piece.x, piece.y + 1, piece.cells)) { piece.y++; add(1); }
        lock(); timer = 0; return;
      }
      const interval = down('down') ? 0.04 : Math.max(0.09, 0.65 - s.level * 0.035) * (has('block-time') ? 1.3 : 1);
      if (timer >= interval) {
        timer = 0;
        if (valid(piece.x, piece.y + 1, piece.cells)) piece.y++;
        else lock();
      }
    },
    render(g) {
      rect(g, ox - 3, oy - 3, cols * cell + 6, rows * cell + 6, '#526180');
      for (let y = 0; y < rows; y++) for (let x = 0; x < cols; x++)
        rect(g, ox + x * cell, oy + y * cell, cell - 1, cell - 1, board[y][x] ? '#a398ef' : '#152037');
      for (const [dx, dy] of piece.cells) rect(g, ox + (piece.x + dx) * cell, oy + (piece.y + dy) * cell, cell - 1, cell - 1, '#74f1d8');
      text(g, `Lines ${lines}`, 630, 220, 23);
    },
    data: () => ({ board, piece, lines, timer, repeat }),
    restore(d) { replace(board, d.board); ({ piece, lines, timer, repeat } = d); },
  };
}

function pinball(a) {
  // TODO: Add articulated flipper physics, ramps and multiball.
  const { state: s, down, pressed, has, add, tone } = a;
  const ball = { x: 480, y: 440, r: 9, vx: 90, vy: -480 };
  const bumpers = [{ x: 380, y: 180, r: 32 }, { x: 580, y: 180, r: 32 }, { x: 480, y: 285, r: 32 }];
  let waiting = true, hits = 0;
  return {
    target: () => ball,
    update(dt) {
      if (waiting) {
        if (pressed('confirm') || pressed('fire')) { waiting = false; ball.x = 480; ball.y = 440; ball.vx = 90; ball.vy = -480; }
        else return;
      }
      for (let i = 0; i < 6; i++) {
        const step = dt / 6, oldY = ball.y;
        ball.vy += (290 + Math.min(100, s.level * 8)) * step;
        ball.x += ball.vx * step; ball.y += ball.vy * step;
        if (ball.x < 279 || ball.x > 681) { ball.x = clamp(ball.x, 279, 681); ball.vx *= -1; }
        if (ball.y < 64) { ball.y = 64; ball.vy = Math.abs(ball.vy); }
        for (const b of bumpers) if (circles(ball, b)) {
          let dx = ball.x - b.x, dy = ball.y - b.y, length = Math.hypot(dx, dy);
          if (!length) { dx = 0; dy = 1; length = 1; }
          ball.x = b.x + dx / length * 42; ball.y = b.y + dy / length * 42;
          ball.vx = dx / length * 290; ball.vy = dy / length * 290;
          add(25); hits++; tone(900); s.level = 1 + Math.floor(hits / 8);
        }
        const left = ball.x < 480, active = down(left ? 'left' : 'right');
        const reach = has('pinball-flippers') ? 176 : 150;
        if (ball.vy > 0 && oldY < 435 && ball.y >= 435 && Math.abs(ball.x - 480) < reach && active) {
          ball.vy = -490; ball.vx = left ? 120 : -120; add(5);
        }
        if (ball.y > 495) { s.lives--; waiting = true; ball.y = 440; break; }
      }
    },
    render(g) {
      rect(g, 267, 50, 426, 453, '#5a315f'); rect(g, 275, 58, 410, 437, '#211f39');
      bumpers.forEach(b => { orb(g, b.x, b.y, b.r, '#ef8cd5'); orb(g, b.x, b.y, 18, '#ffeaa3'); });
      const reach = has('pinball-flippers') ? 176 : 150;
      rect(g, 480 - reach, 435, reach - 10, 13, down('left') ? '#fff' : '#70dbd6');
      rect(g, 490, 435, reach - 10, 13, down('right') ? '#fff' : '#70dbd6');
      orb(g, ball.x, ball.y, ball.r, '#fff');
      if (waiting) text(g, 'FIRE to plunge', 390, 365, 22);
    },
    data: () => ({ ball, waiting, hits }),
    restore(d) { Object.assign(ball, d.ball); ({ waiting, hits } = d); },
  };
}

function rhythm(a) {
  // TODO: Add authored songs and tempo changes instead of generated beats.
  const { state: s, pressed, has, rand, add, tone, end } = a;
  const lanes = ['left', 'down', 'up', 'right'], notes = [];
  let spawn = 0.5, streak = 0, hits = 0, misses = 0, health = 8;
  const fail = () => { streak = 0; health--; misses++; if (health <= 0) { s.lives = 0; end(); } };
  return {
    update(dt) {
      const speed = Math.min(330, 180 + s.level * 12), window = has('rhythm-window') ? 48 : 32;
      spawn -= dt;
      if (spawn <= 0) { notes.push({ lane: rand(4), y: 60 }); spawn = Math.max(0.38, 0.85 - s.level * 0.025); }
      for (const note of notes) note.y += speed * dt;
      lanes.forEach((key, lane) => {
        if (!pressed(key)) return;
        const note = notes.filter(n => n.lane === lane && !n.dead).sort((a, b) => Math.abs(a.y - 430) - Math.abs(b.y - 430))[0];
        if (note && Math.abs(note.y - 430) <= window) {
          note.dead = true; streak++; hits++; add(40 * scoreMultiplier(streak)); tone(330 + lane * 110);
          if (hits % 10 === 0) health = Math.min(8, health + 1);
        } else fail();
      });
      for (const note of notes) if (!note.dead && note.y > 430 + window) { note.dead = true; fail(); }
      for (let i = notes.length - 1; i >= 0; i--) if (notes[i].dead) notes.splice(i, 1);
      s.level = 1 + Math.floor(hits / 12); s.lives = Math.ceil(Math.max(0, health) / 3);
    },
    render(g) {
      lanes.forEach((key, i) => {
        rect(g, 270 + i * 110, 50, 95, 440, '#302347');
        rect(g, 270 + i * 110, 428, 95, 4, '#f5c5fd');
        text(g, key.toUpperCase(), 280 + i * 110, 480, 15);
      });
      notes.forEach(n => rect(g, 280 + n.lane * 110, n.y - 8, 75, 16, '#91f5ec'));
      text(g, `Combo ${streak}   Energy ${Math.max(0, health)}/8`, 300, 65);
    },
    data: () => ({ notes, streak, hits, misses, health, spawn }),
    restore(d) { replace(notes, d.notes); ({ streak, hits, misses, health, spawn } = d); },
  };
}

function defense(a) {
  // TODO: Add branching paths, enemy armor types and tower targeting choices.
  const { state: s, pressed, has, add, tone } = a;
  const pads = [{ x: 170, y: 210 }, { x: 330, y: 340 }, { x: 490, y: 210 }, { x: 650, y: 340 }, { x: 810, y: 210 }];
  const towers = [], enemies = [];
  let selected = 0, gold = 75, spawn = 1.6, spawned = 0, killed = 0;
  s.lives = 10;
  return {
    update(dt) {
      if (pressed('left')) selected = (selected + pads.length - 1) % pads.length;
      if (pressed('right')) selected = (selected + 1) % pads.length;
      if ((pressed('confirm') || pressed('fire')) && gold >= 50 && !towers.some(t => t.pad === selected)) {
        gold -= 50; towers.push({ ...pads[selected], pad: selected, cooldown: 0 });
      }
      spawn -= dt;
      if (spawn <= 0) {
        enemies.push({ x: 0, y: 280, hp: 3 + Math.floor((s.level - 1) / 2), dead: false });
        spawned++; s.level = 1 + Math.floor(spawned / 8);
        spawn = Math.max(0.65, 2.4 - s.level * 0.07);
      }
      for (const e of enemies) {
        e.x += Math.min(140, 35 + s.level * 5) * dt;
        if (e.x > W && !e.dead) { e.dead = true; s.lives--; }
      }
      for (const tower of towers) {
        tower.cooldown -= dt;
        const target = enemies.find(e => !e.dead && Math.hypot(tower.x - e.x, tower.y - e.y) < 170);
        if (target && tower.cooldown <= 0) {
          target.hp -= has('tower-power') ? 2 : 1; tower.cooldown = 0.55; tone(500, 0.025, tower.x);
          if (target.hp <= 0) { target.dead = true; killed++; gold += 20; add(30 * s.level); }
        }
      }
      for (let i = enemies.length - 1; i >= 0; i--) if (enemies[i].dead) enemies.splice(i, 1);
    },
    render(g) {
      rect(g, 0, 255, W, 50, '#b4a47a');
      pads.forEach((p, i) => orb(g, p.x, p.y, 27, i === selected ? '#ffe898' : '#4c7568'));
      towers.forEach(t => { rect(g, t.x - 14, t.y - 18, 28, 36, '#8edcfe'); orb(g, t.x, t.y, 8, '#24394e'); });
      enemies.forEach(e => { orb(g, e.x, e.y, 13, '#fc7c89'); text(g, e.hp, e.x - 4, e.y - 20, 13); });
      text(g, `Gold ${gold}   Build 50   Pad ${selected + 1}`, 280, 100, 22);
    },
    data: () => ({ selected, gold, towers, enemies, spawned, killed, spawn }),
    restore(d) { replace(towers, d.towers); replace(enemies, d.enemies); ({ selected, gold, spawned, killed, spawn } = d); },
  };
}

export const arcadePlugins = [
  plugin('space-shooter', 'Nebula Patrol', 'space-shooter', 'complete',
    'Pilot through escalating enemy waves. Dodge aimed shots; escaped invaders cost a life. Defeat eight invaders to advance.',
    'Arrows: move · FIRE: shoot · Lose all 3 lives to end', [upgrade('twin-shot', 'Twin cannons'), upgrade('shield', 'Longer damage shield', 100)], shooter, '#080e27'),
  plugin('brick-breaker', 'Prism Breaker', 'brick-breaker', 'complete',
    'Keep the ball above the paddle and clear every brick. New levels add rows, armor and ball speed.',
    'LEFT/RIGHT: paddle · FIRE/CONFIRM: launch · 3 missed balls ends run', [upgrade('wide-paddle', 'Wide paddle')], breaker, '#241c38'),
  plugin('snake', 'Garden Circuit', 'snake', 'complete',
    'Eat fruit to grow and increase speed. Avoid walls and your own body. Fill the garden for a perfect finish.',
    'Arrows: steer · Eat fruit · Wall or self collision ends run', [upgrade('slow-snake', 'Patient growth')], snake, '#102017'),
  plugin('maze-chase', 'Moonlit Maze', 'maze-chase', 'complete',
    'Collect all dots while two pathfinding ghosts pursue you. Large lower-corner dots grant five seconds of ghost-eating power.',
    'Arrows: steer · Clear dots to advance · Avoid ghosts unless powered', [upgrade('maze-shield', 'Longer respawn grace')], maze, '#0d1028'),
  plugin('platformer', 'Sky Steps', 'platformer', 'minimal',
    'Jump the floating route, collect coins, avoid the patrolling guard and reach the gold flag. Each lap speeds the guard.',
    'LEFT/RIGHT: run · UP/FIRE: jump · Reach flag · 3 falls/hits ends run', [upgrade('high-jump', 'Spring boots')], platformer, '#273f57'),
  plugin('endless-runner', 'Sunset Sprint', 'endless-runner', 'minimal',
    'Jump over incoming hurdles. Distance raises speed and score; a collision ends the run.',
    'UP/FIRE: jump · Clear hurdles · One collision ends run', [upgrade('runner-jump', 'Higher vault')], runner, '#34283f'),
  plugin('racing', 'Midnight Motorway', 'racing', 'minimal',
    'Dodge traffic on a four-lane highway. Distance raises traffic density and speed.',
    'LEFT/RIGHT: steer · UP: accelerate · DOWN: brake · 3 crashes ends run', [upgrade('race-grip', 'Responsive tires')], racing, '#204a43'),
  plugin('fighting', 'Neon Duel', 'fighting', 'minimal',
    'Close in and strike the rival, then retreat or guard against their attacks. Each defeated rival is tougher and faster.',
    'LEFT/RIGHT: move · FIRE: strike · DOWN: guard · Zero health ends run', [upgrade('long-reach', 'Extended strike')], fighting, '#39243c'),
  plugin('falling-blocks', 'Stack Studio', 'falling-block-puzzle', 'minimal',
    'Fit falling shapes into complete rows. Cleared lines increase gravity. The stack reaching the spawn ends the game.',
    'LEFT/RIGHT: slide · UP: rotate · DOWN: soft drop · FIRE: hard drop', [upgrade('block-time', 'Gentler gravity')], blocks, '#111b30'),
  plugin('pinball', 'Comet Table', 'pinball', 'minimal',
    'Plunge a ball, rebound off bumpers and use the two flippers to prevent a drain. Bumper hits increase gravity.',
    'FIRE/CONFIRM: plunge · Hold LEFT/RIGHT: flippers · 3 drains ends run', [upgrade('pinball-flippers', 'Long flippers')], pinball, '#1c1229'),
  plugin('rhythm', 'Pulse Lanes', 'rhythm', 'minimal',
    'Press each note’s arrow as it crosses the bright target line. Accurate streaks multiply points; misses drain energy.',
    'LEFT/DOWN/UP/RIGHT: match lanes at target · Empty energy ends run', [upgrade('rhythm-window', 'Wider timing window')], rhythm, '#20162f'),
  plugin('tower-defense', 'Orchard Watch', 'tower-defense', 'minimal',
    'Spend starting gold on a tower beside the path. Towers attack automatically; kills fund more towers. Waves grow tougher.',
    'LEFT/RIGHT: select pad · FIRE/CONFIRM: build (50 gold) · 10 leaks ends run', [upgrade('tower-power', 'Double tower damage')], defense, '#193c30'),
];
