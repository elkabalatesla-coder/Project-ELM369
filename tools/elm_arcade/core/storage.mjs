export const DEFAULT_SETTINGS = Object.freeze({
  quality: "high", reducedMotion: false, master: 0.8, music: 0.5, sfx: 0.8, ui: 0.6,
});
const plain = value => value !== null && typeof value === "object" && !Array.isArray(value);
const volume = (value, fallback) => typeof value === "number" && Number.isFinite(value) ? Math.max(0, Math.min(1, value)) : fallback;

export class Store {
  constructor(storage, key = "elm-arcade-v1") {
    if (storage === undefined) { try { storage = globalThis.localStorage; } catch { /* Privacy mode. */ } }
    this.storage = storage;
    this.key = key;
    this.data = { version: 1, settings: { ...DEFAULT_SETTINGS }, saves: {}, unlocks: [], scores: {}, upgrades: {} };
    try {
      const parsed = JSON.parse(storage?.getItem(key) || "null");
      if (parsed?.version === 1 && plain(parsed)) {
        this.data.settings = this.validateSettings(parsed.settings);
        for (const section of ["saves", "scores", "upgrades"]) {
          if (plain(parsed[section])) this.data[section] = parsed[section];
        }
        if (Array.isArray(parsed.unlocks)) this.data.unlocks = [...new Set(parsed.unlocks.filter(v => typeof v === "string"))];
      }
    } catch { /* Corrupted or unavailable storage falls back to memory. */ }
  }
  validateSettings(settings) {
    const s = plain(settings) ? settings : {};
    return {
      quality: s.quality === "low" ? "low" : "high",
      reducedMotion: typeof s.reducedMotion === "boolean" ? s.reducedMotion : false,
      ...Object.fromEntries(["master", "music", "sfx", "ui"].map(k => [k, volume(s[k], DEFAULT_SETTINGS[k])])),
    };
  }
  persist() { try { this.storage?.setItem(this.key, JSON.stringify(this.data)); return true; } catch { return false; } }
  getSettings() { return { ...this.data.settings }; }
  setSettings(patch) {
    this.data.settings = this.validateSettings({ ...this.data.settings, ...patch });
    this.persist();
    return this.getSettings();
  }
  saveGame(id, version, data) {
    if (typeof id !== "string" || typeof version !== "string") throw new TypeError("Save requires game id and version");
    const save = JSON.parse(JSON.stringify({ version, data }));
    Object.defineProperty(this.data.saves, id, { value: save, writable: true, configurable: true, enumerable: true });
    this.persist();
  }
  loadGame(id) {
    const save = Object.hasOwn(this.data.saves, id) && this.data.saves[id];
    return plain(save) && typeof save.version === "string" && Object.hasOwn(save, "data") ? structuredClone(save) : null;
  }
  unlock(id) {
    if (typeof id === "string" && !this.data.unlocks.includes(id)) this.data.unlocks.push(id);
    this.persist();
  }
  getUnlocks() { return [...this.data.unlocks]; }
  upgradeLedger(id) {
    const entry = Object.hasOwn(this.data.upgrades, id) && this.data.upgrades[id];
    return {
      spent: plain(entry) && Number.isSafeInteger(entry.spent) && entry.spent >= 0 ? entry.spent : 0,
      owned: plain(entry) && Array.isArray(entry.owned) ? [...new Set(entry.owned.filter(v => typeof v === "string"))] : [],
    };
  }
  getUpgrades(id) { return this.upgradeLedger(id).owned; }
  getUpgradeBudget(id) {
    const earned = Math.min(Number.MAX_SAFE_INTEGER, Math.max(0, Math.floor(this.getScores(id)[0]?.score || 0)));
    return Math.max(0, earned - this.upgradeLedger(id).spent);
  }
  purchaseUpgrade(id, upgradeId, cost) {
    if (typeof id !== "string" || typeof upgradeId !== "string" || !upgradeId ||
        !Number.isSafeInteger(cost) || cost < 0) return false;
    const ledger = this.upgradeLedger(id);
    if (ledger.owned.includes(upgradeId) || this.getUpgradeBudget(id) < cost) return false;
    ledger.owned.push(upgradeId); ledger.spent += cost;
    Object.defineProperty(this.data.upgrades, id, { value: ledger, writable: true, configurable: true, enumerable: true });
    this.persist();
    return true;
  }
  getScores(id) {
    const scores = Object.hasOwn(this.data.scores, id) && this.data.scores[id];
    return (Array.isArray(scores) ? scores : []).filter(s => plain(s) && Number.isFinite(s.score) && typeof s.name === "string")
      .map(s => ({ score: s.score, name: s.name.slice(0, 24), date: typeof s.date === "string" ? s.date : "" }))
      .sort((a, b) => b.score - a.score).slice(0, 10);
  }
  addScore(id, score, name = "Player") {
    if (!Number.isFinite(score)) throw new TypeError("Score must be finite");
    const entry = { score, name: String(name).replace(/[<>&"'`]/g, "").slice(0, 24), date: new Date().toISOString() };
    Object.defineProperty(this.data.scores, id, { value: [...this.getScores(id), entry].sort((a, b) => b.score - a.score).slice(0, 10), enumerable: true, writable: true, configurable: true });
    this.persist();
    return this.getScores(id);
  }
}
