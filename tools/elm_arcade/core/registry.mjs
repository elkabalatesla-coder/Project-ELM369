const SEMVER = /^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$/;

export function parseVersion(version) {
  const match = typeof version === "string" && version.match(SEMVER);
  if (!match || (match[4] && match[4].split(".").some(v => /^\d+$/.test(v) && v.length > 1 && v[0] === "0"))) {
    throw new TypeError(`Invalid semantic version: ${version}`);
  }
  return { numbers: match.slice(1, 4).map(Number), pre: match[4]?.split(".") || [] };
}

export function compareVersions(a, b) {
  const x = parseVersion(a), y = parseVersion(b);
  for (let i = 0; i < 3; i++) if (x.numbers[i] !== y.numbers[i]) return Math.sign(x.numbers[i] - y.numbers[i]);
  if (!x.pre.length || !y.pre.length) return Math.sign(y.pre.length - x.pre.length);
  for (let i = 0; i < Math.max(x.pre.length, y.pre.length); i++) {
    if (x.pre[i] === y.pre[i]) continue;
    if (x.pre[i] === undefined) return -1;
    if (y.pre[i] === undefined) return 1;
    const xn = /^\d+$/.test(x.pre[i]), yn = /^\d+$/.test(y.pre[i]);
    if (xn && yn) return Math.sign(Number(x.pre[i]) - Number(y.pre[i]));
    if (xn !== yn) return xn ? -1 : 1;
    return x.pre[i] < y.pre[i] ? -1 : 1;
  }
  return 0;
}

export class Registry {
  constructor() { this.plugins = new Map(); }
  register(plugin) {
    const m = plugin?.manifest;
    if (!m || !/^[a-z][a-z0-9-]*$/.test(m.id) || !m.title || typeof m.title !== "string" ||
        typeof m.genre !== "string" || typeof m.status !== "string" ||
        !m.config || typeof m.config !== "object" || !Array.isArray(m.features) ||
        !Array.isArray(m.upgrades) || !m.sound || typeof m.sound !== "object" ||
        typeof plugin.create !== "function") throw new TypeError("Invalid game plugin manifest");
    parseVersion(m.version);
    if (this.plugins.has(m.id)) throw new Error(`Duplicate game: ${m.id}`);
    this.plugins.set(m.id, plugin);
    return this;
  }
  list() { return [...this.plugins.values()].map(p => p.manifest); }
  get(id) {
    const plugin = this.plugins.get(id);
    if (!plugin) throw new Error(`Unknown game: ${id}`);
    return plugin;
  }
  create(id, context) {
    const game = this.get(id).create(context);
    if (!game || typeof game.update !== "function" || typeof game.render !== "function") {
      throw new TypeError("Game must provide update(dt) and render(alpha)");
    }
    return game;
  }
  migrate(id, saved) {
    const plugin = this.get(id), current = plugin.manifest.version;
    if (!saved || !Object.hasOwn(saved, "data")) throw new TypeError("Invalid saved game");
    let version = saved.version, data = structuredClone(saved.data);
    if (compareVersions(version, current) > 0) throw new Error("Save is from a future version");
    const visited = new Set();
    while (compareVersions(version, current) !== 0) {
      if (visited.has(version)) throw new Error("Cyclic migration path");
      visited.add(version);
      const migration = plugin.migrations?.[version];
      // Each source version explicitly names the next version; no implicit skipped upgrades.
      if (!migration || typeof migration.up !== "function") throw new Error(`Missing migration from ${version}`);
      const next = migration.to;
      if (compareVersions(next, version) <= 0 || compareVersions(next, current) > 0) throw new Error("Invalid migration target");
      data = migration.up(data);
      version = next;
    }
    return { version: current, data };
  }
}
