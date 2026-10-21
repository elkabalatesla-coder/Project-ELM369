const finite = (...values) => {
  if (!values.every(Number.isFinite)) throw new TypeError('Expected finite numbers');
};
const box = b => {
  const w = b.width ?? b.w, h = b.height ?? b.h;
  finite(b.x, b.y, w, h);
  if (w < 0 || h < 0) throw new RangeError('Negative box size');
  return [b.x, b.y, w, h];
};

export function aabb(a, b) {
  const [x, y, w, h] = box(a), [u, v, s, t] = box(b);
  return x <= u + s && x + w >= u && y <= v + t && y + h >= v;
}

export function circles(a, b) {
  const r = a.radius ?? a.r, s = b.radius ?? b.r;
  finite(a.x, a.y, r, b.x, b.y, s);
  if (r < 0 || s < 0) throw new RangeError('Negative radius');
  return Math.hypot(a.x - b.x, a.y - b.y) <= r + s;
}

export function sat(a, b) {
  for (const polygon of [a, b]) {
    if (!Array.isArray(polygon) || polygon.length < 3) throw new TypeError('Expected convex polygons');
    for (const point of polygon) finite(point.x, point.y);
    let area = 0;
    for (let i = 0; i < polygon.length; i++) {
      const p = polygon[i], q = polygon[(i + 1) % polygon.length];
      area += p.x * q.y - p.y * q.x;
    }
    if (Math.abs(area) < 1e-10) throw new RangeError('Degenerate polygon');
  }
  for (const polygon of [a, b]) {
    for (let i = 0; i < polygon.length; i++) {
      const p = polygon[i], q = polygon[(i + 1) % polygon.length];
      const nx = p.y - q.y, ny = q.x - p.x;
      if (nx === 0 && ny === 0) continue;
      const project = points => points.map(v => v.x * nx + v.y * ny);
      const pa = project(a), pb = project(b);
      if (Math.max(...pa) < Math.min(...pb) || Math.max(...pb) < Math.min(...pa)) return false;
    }
  }
  return true;
}

export function integrate(body, dt) {
  finite(body.x, body.y, body.vx ?? 0, body.vy ?? 0, body.ax ?? 0, body.ay ?? 0, dt);
  if (dt < 0) throw new RangeError('Negative timestep');
  const vx = body.vx ?? 0, vy = body.vy ?? 0, ax = body.ax ?? 0, ay = body.ay ?? 0;
  const next = { x: body.x + vx * dt + ax * dt * dt / 2,
    y: body.y + vy * dt + ay * dt * dt / 2, vx: vx + ax * dt, vy: vy + ay * dt };
  finite(next.x, next.y, next.vx, next.vy);
  Object.assign(body, next);
  return body;
}

// Zero/false cells are walkable; four-way paths include both endpoints.
export function astar(grid, start, goal) {
  if (!Array.isArray(grid) || !grid.length || !Array.isArray(grid[0]) || !grid[0].length ||
      grid.some(row => !Array.isArray(row) || row.length !== grid[0].length ||
        row.some(cell => typeof cell !== 'boolean' && (!Number.isFinite(cell) || cell < 0)))) {
    throw new TypeError('Expected a rectangular finite grid');
  }
  finite(start.x, start.y, goal.x, goal.y);
  if (![start.x, start.y, goal.x, goal.y].every(Number.isInteger)) throw new TypeError('Expected integer cells');
  const valid = p => p.x >= 0 && p.y >= 0 && p.y < grid.length && p.x < grid[0].length && !grid[p.y][p.x];
  if (!valid(start) || !valid(goal)) return [];
  const key = p => `${p.x},${p.y}`, heuristic = p => Math.abs(p.x - goal.x) + Math.abs(p.y - goal.y);
  const open = [{ ...start, g: 0, f: heuristic(start) }], costs = new Map([[key(start), 0]]), parents = new Map();
  while (open.length) {
    open.sort((a, b) => b.f - a.f);
    const current = open.pop(), k = key(current);
    if (current.g !== costs.get(k)) continue;
    if (current.x === goal.x && current.y === goal.y) {
      const path = [{ x: current.x, y: current.y }];
      while (parents.has(key(path[0]))) path.unshift(parents.get(key(path[0])));
      return path;
    }
    for (const [dx, dy] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
      const next = { x: current.x + dx, y: current.y + dy }, g = current.g + 1;
      if (!valid(next) || g >= (costs.get(key(next)) ?? Infinity)) continue;
      costs.set(key(next), g);
      parents.set(key(next), { x: current.x, y: current.y });
      open.push({ ...next, g, f: g + heuristic(next) });
    }
  }
  return [];
}

export function difficulty(level) {
  finite(level);
  if (level < 1) throw new RangeError('Level must be positive');
  const n = Math.min(100, Math.floor(level));
  const growth = Math.log1p(n - 1);
  return {
    level: n,
    speed: 1 + 0.28 * growth,
    enemyRate: 0.25 + 1.25 * Math.exp(-(n - 1) / 18),
    multiplier: 1 + 0.5 * growth,
  };
}

export function scoreMultiplier(streak) {
  finite(streak);
  if (streak < 0) throw new RangeError('Negative streak');
  return 1 + Math.min(4, Math.floor(streak / 5) * 0.25);
}
