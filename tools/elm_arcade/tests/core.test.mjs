import test from "node:test";
import assert from "node:assert/strict";
import { Registry, compareVersions, parseVersion } from "../core/registry.mjs";
import { Store, DEFAULT_SETTINGS } from "../core/storage.mjs";
import { GameLoop, StateMachine } from "../core/loop.mjs";
import { Camera, damp, spline } from "../core/camera.mjs";
import { Input, INSTRUCTIONS } from "../core/input.mjs";
import { AudioEngine } from "../core/audio.mjs";
import { LiquidRenderer } from "../core/renderer.mjs";

const plugin = (overrides = {}) => ({
  manifest: { id: "test-game", title: "Test", version: "2.0.0", genre: "arcade", status: "ready", config: {}, features: [], upgrades: [], sound: {} },
  create: () => ({ update() {}, render() {} }), ...overrides,
});
class Events {
  constructor() { this.events = new Map(); this.hidden = false; }
  addEventListener(event, fn) { if (!this.events.has(event)) this.events.set(event, new Set()); this.events.get(event).add(fn); }
  removeEventListener(event, fn) { this.events.get(event)?.delete(fn); }
  emit(event, data = {}) { for (const fn of this.events.get(event) || []) fn({ preventDefault() {}, ...data }); }
}
const memory = () => {
  const map = new Map();
  return { getItem: k => map.get(k) || null, setItem: (k, v) => map.set(k, v) };
};

test("semantic versions validate and order prerelease versions", () => {
  for (const invalid of ["1", "1.0", "01.0.0", "1.0.0-01", "v1.0.0", null]) assert.throws(() => parseVersion(invalid));
  assert.equal(compareVersions("1.2.3-alpha.2", "1.2.3-alpha.11"), -1);
  assert.equal(compareVersions("1.2.3-rc.1", "1.2.3"), -1);
  assert.equal(compareVersions("1.2.3+build", "1.2.3+other"), 0);
  assert.equal(compareVersions("2.0.0", "1.99.99"), 1);
});
test("registry validates manifests, duplicate IDs and game lifecycle", () => {
  const registry = new Registry().register(plugin());
  assert.equal(registry.list()[0].id, "test-game");
  assert.equal(typeof registry.create("test-game", {}).update, "function");
  assert.throws(() => registry.register(plugin()), /Duplicate/);
  assert.throws(() => registry.get("missing"), /Unknown/);
  assert.throws(() => new Registry().register({ manifest: {}, create() {} }), /manifest/);
  const bad = new Registry().register(plugin({ create: () => ({}) }));
  assert.throws(() => bad.create("test-game", {}), /update/);
});
test("migrations are sequential and do not mutate saved input", () => {
  const registry = new Registry().register(plugin({ migrations: {
    "1.0.0": { to: "1.1.0", up: data => { data.score += 1; return data; } },
    "1.1.0": { to: "2.0.0", up: data => ({ points: data.score * 2 }) },
  } }));
  const saved = { version: "1.0.0", data: { score: 3 } };
  assert.deepEqual(registry.migrate("test-game", saved), { version: "2.0.0", data: { points: 8 } });
  assert.equal(saved.data.score, 3);
  assert.deepEqual(registry.migrate("test-game", { version: "2.0.0+old-build", data: { points: 8 } }), { version: "2.0.0", data: { points: 8 } });
  assert.throws(() => registry.migrate("test-game", { version: "3.0.0", data: {} }), /future/);
  assert.throws(() => registry.migrate("test-game", { version: "0.9.0", data: {} }), /Missing/);
});
test("migrations reject backward and overshooting paths", () => {
  const registry = new Registry().register(plugin({ migrations: { "1.0.0": { to: "0.9.0", up: x => x } } }));
  assert.throws(() => registry.migrate("test-game", { version: "1.0.0", data: {} }), /target/);
});
test("settings validate and persist only known settings", () => {
  const storage = memory(), store = new Store(storage);
  assert.deepEqual(store.getSettings(), DEFAULT_SETTINGS);
  store.setSettings({ quality: "low", music: -1, sfx: 8, master: NaN, ui: "bad", reducedMotion: true, injected: true });
  assert.deepEqual(new Store(storage).getSettings(), { quality: "low", music: 0, sfx: 1, master: 0.8, ui: 0.6, reducedMotion: true });
});
test("storage corruption, unknown schema and blocked storage fail gracefully", () => {
  for (const raw of ["bad json", '{"version":100}', '{"version":1,"saves":[],"scores":false,"settings":null}']) {
    const store = new Store({ getItem: () => raw, setItem() {} });
    assert.deepEqual(store.getSettings(), DEFAULT_SETTINGS);
    assert.equal(store.loadGame("none"), null);
  }
  const store = new Store({ getItem() { throw new Error("blocked"); }, setItem() { throw new Error("quota"); } });
  store.saveGame("game", "1.0.0", { score: 5 });
  assert.equal(store.loadGame("game").data.score, 5);
  assert.equal(store.persist(), false);
});
test("saves and unlocks are isolated defensive copies", () => {
  const store = new Store(memory()), data = { score: 12 };
  store.saveGame("one", "1.0.0", data); data.score = 99;
  const loaded = store.loadGame("one"); loaded.data.score = 0;
  assert.equal(store.loadGame("one").data.score, 12);
  assert.equal(store.loadGame("two"), null);
  store.unlock("one"); store.unlock("one"); store.getUnlocks().push("two");
  assert.deepEqual(store.getUnlocks(), ["one"]);
  store.saveGame("__proto__", "1.0.0", { safe: true });
  assert.equal(store.loadGame("__proto__").data.safe, true);
  assert.equal({}.safe, undefined);
});
test("leaderboard keeps top ten finite scores and inert names", () => {
  const store = new Store(memory());
  for (let i = 0; i < 15; i++) store.addScore("one", i, "<img>");
  assert.equal(store.getScores("one").length, 10);
  assert.deepEqual(store.getScores("one").map(s => s.score), [14, 13, 12, 11, 10, 9, 8, 7, 6, 5]);
  assert.equal(store.getScores("one")[0].name, "img");
  assert.throws(() => store.addScore("one", Infinity), /finite/);
});
test("upgrade budget derives from best score, persists spending, and never spends casino saves", () => {
  const storage = memory(), store = new Store(storage);
  store.saveGame("casino", "1.0.0", { credits: 5000 });
  assert.equal(store.getUpgradeBudget("casino"), 0);
  store.addScore("casino", 100); store.addScore("casino", 40);
  assert.equal(store.getUpgradeBudget("casino"), 100);
  assert.equal(store.purchaseUpgrade("casino", "sound", 60), true);
  assert.equal(store.purchaseUpgrade("casino", "sound", 10), false);
  assert.equal(store.purchaseUpgrade("casino", "camera", 50), false);
  assert.equal(store.purchaseUpgrade("casino", "camera", -1), false);
  assert.equal(new Store(storage).getUpgradeBudget("casino"), 40);
  assert.deepEqual(new Store(storage).getUpgrades("casino"), ["sound"]);
  assert.equal(store.loadGame("casino").data.credits, 5000);
  store.addScore("casino", 150);
  assert.equal(store.getUpgradeBudget("casino"), 90);
});
test("state machine accepts legal transitions and rejects invalid ones", () => {
  const machine = new StateMachine();
  for (const state of ["menu", "play", "pause", "play", "gameover", "highscore", "menu"]) assert.equal(machine.transition(state), state);
  assert.throws(() => machine.transition("gameover"), /Invalid/);
  assert.throws(() => new StateMachine("__proto__"), /Unknown/);
});
test("fixed loop interpolates, bounds catchup and clears pause jumps", () => {
  let updates = 0; const alphas = [], deltas = [];
  const loop = new GameLoop({ update: dt => { updates++; deltas.push(dt); }, render: a => alphas.push(a), document: null });
  loop.tick(0); loop.tick(25);
  assert.equal(updates, 1); assert.ok(Math.abs(alphas.at(-1) - 0.5) < 1e-8);
  loop.tick(100000);
  assert.equal(updates, 6);
  assert.ok(deltas.every(dt => dt === 1 / 60));
  loop.pause(); loop.tick(200000); loop.resume(); loop.tick(300000);
  assert.equal(updates, 6);
  loop.tick(300017); assert.equal(updates, 7);
  loop.destroy();
});
test("visibility changes reset clocks without unpausing explicit pause", () => {
  const doc = new Events(); let updates = 0;
  const loop = new GameLoop({ document: doc, update: () => updates++ });
  loop.tick(0); doc.hidden = true; doc.emit("visibilitychange"); loop.tick(90000);
  doc.hidden = false; doc.emit("visibilitychange"); loop.tick(100000);
  assert.equal(updates, 0);
  loop.pause(); doc.emit("visibilitychange"); assert.equal(loop.paused, true);
  loop.destroy(); assert.equal(doc.events.get("visibilitychange").size, 0);
});
test("loop schedules and cancels only one animation chain", () => {
  let requests = 0, cancels = 0;
  const loop = new GameLoop({ requestFrame: () => ++requests, cancelFrame: () => cancels++, document: null });
  loop.start(); loop.start(); assert.equal(requests, 1);
  loop.stop(); assert.equal(cancels, 1);
  assert.throws(() => new GameLoop({ step: 0 }), /timestep/);
});
test("critical damping is frame-rate independent and spline has exact endpoints", () => {
  const full = damp(0, 10, 0, 1);
  let value = 0, velocity = 0;
  for (let i = 0; i < 60; i++) { const d = damp(value, 10, velocity, 1 / 60); value = d.value; velocity = d.velocity; }
  assert.ok(Math.abs(full.value - value) < 1e-9);
  assert.ok(value > 9 && value < 10);
  assert.equal(spline(0, 2, 6, 8, 0), 2); assert.equal(spline(0, 2, 6, 8, 1), 6);
});
test("camera follow, orbit, dolly, 2D and WebGL/audio transforms are usable", () => {
  const camera = new Camera();
  camera.follow({ x: 20, y: 10, z: 0 }); camera.update(2);
  assert.ok(Math.abs(camera.position.x - 20) < 0.01);
  const screen = camera.worldToScreen(camera.position, 800, 600);
  assert.deepEqual(screen, { x: 400, y: 300 });
  const calls = [];
  camera.apply({ translate: (...a) => calls.push(a), scale: (...a) => calls.push(a) }, 800, 600);
  assert.deepEqual(calls[0], [400, 300]);
  const matrix = camera.getViewMatrix(); assert.equal(matrix.length, 16); assert.ok([...matrix].every(Number.isFinite));
  assert.ok(Math.abs(camera.getListener().forward.z + 1) < 1e-8);
  camera.orbit({ x: 0, y: 0, z: 0 }, 10, 1, 3); camera.update(1);
  assert.ok(camera.desired.x > 8);
  const before = camera.desired.z; camera.dolly(2); assert.equal(camera.desired.z, before + 2);
});
test("camera timed tracks, slow motion, deterministic shake and replay metadata", () => {
  const camera = new Camera({ random: () => 1 });
  camera.track([{ time: 0, position: { x: 0, y: 0, z: 10 } }, { time: 2, position: { x: 10, y: 0, z: 10 } }]);
  camera.setTimeScale(0.5); assert.equal(camera.update(2), 1); assert.equal(camera.desired.x, 5);
  camera.shake(4, 1); camera.update(0.5); assert.equal(camera.shakeOffset.x, 2);
  camera.update(0.5); assert.equal(camera.shakeOffset.x, 0);
  const replay = camera.getReplayMetadata(); assert.equal(replay.events[0].timeScale, 0.5);
  replay.events.length = 0; assert.equal(camera.getReplayMetadata().events.length, 1);
  assert.throws(() => camera.setTimeScale(-1), /timeScale/);
  assert.throws(() => camera.track([{ time: 1, position: {} }, { time: 0, position: {} }]), /track/);
});
test("input handles keyboard aliases, one-frame edges, blur and pixel pointer", () => {
  const target = new Events(), canvas = new Events();
  canvas.width = 960; canvas.height = 540;
  canvas.getBoundingClientRect = () => ({ left: 10, top: 20, width: 200, height: 100 });
  const input = new Input(canvas, { target, buttons: null, navigator: null });
  target.emit("keydown", { code: "KeyA" }); target.emit("keydown", { code: "ArrowLeft" });
  assert.equal(input.down("left"), true); assert.equal(input.pressed("left"), true);
  input.endFrame(); target.emit("keydown", { code: "KeyA", repeat: true });
  assert.equal(input.pressed("left"), false);
  target.emit("keyup", { code: "KeyA" }); assert.equal(input.down("left"), true);
  canvas.emit("pointerdown", { clientX: 110, clientY: 45, pointerId: 1 });
  assert.deepEqual(input.pointer, { x: 480, y: 135, normalizedX: 0.5, normalizedY: 0.25, down: true, inside: true });
  assert.equal(input.down("fire"), true); assert.equal(input.pressed("action"), true);
  assert.equal(input.pressed("confirm"), false);
  target.emit("keydown", { code: "Enter" }); assert.equal(input.pressed("confirm"), true);
  target.emit("pointerup", { pointerId: 1 }); assert.equal(input.pointer.down, false);
  target.emit("blur"); assert.equal(input.down("left"), false);
  input.destroy(); assert.equal(target.events.get("keydown").size, 0);
  assert.ok(INSTRUCTIONS.action.includes("Space"));
});
test("keyboard capture requires game activation and never interferes with editable forms", () => {
  const target = new Events(), canvas = new Events();
  canvas.ownerDocument = { activeElement: null };
  const input = new Input(canvas, { target, buttons: null, navigator: null });
  let prevented = 0;
  const press = extra => target.emit("keydown", { code: "Space", preventDefault: () => prevented++, ...extra });
  press({ target: { tagName: "BODY" } }); assert.equal(prevented, 0);
  input.setActive(true);
  press({ target: { tagName: "INPUT" } }); assert.equal(prevented, 0); assert.equal(input.down("fire"), false);
  press({ target: { isContentEditable: true } }); assert.equal(prevented, 0);
  press({ target: canvas }); assert.equal(prevented, 1); assert.equal(input.down("fire"), true);
  target.emit("focusin", { target: { tagName: "TEXTAREA" } });
  assert.equal(input.down("fire"), false); assert.equal(input.active, false);
  input.destroy();
});
test("touch controls and gamepad actions share the same abstraction", () => {
  const button = new Events(); button.dataset = { action: "secondary" };
  const target = new Events(), canvas = new Events();
  const pad = { buttons: [{ pressed: true }, { pressed: false }], axes: [-0.5, 0] };
  const input = new Input(canvas, { target, buttons: { querySelectorAll: () => [button] }, navigator: { getGamepads: () => [pad] } });
  button.emit("pointerdown", { pointerId: 2 }); assert.equal(input.down("secondary"), true);
  button.emit("pointercancel", { pointerId: 2 }); assert.equal(input.down("secondary"), false);
  assert.equal(input.down("left"), true); assert.equal(input.pressed("action"), true);
  assert.equal(input.down("confirm"), false);
  pad.buttons[1].pressed = true; assert.equal(input.pressed("confirm"), true);
  input.endFrame(); assert.equal(input.pressed("action"), false);
  pad.buttons[0].pressed = false; pad.axes[0] = 0; assert.equal(input.down("left"), false);
  input.destroy();
});
test("audio remains lazy and unsupported audio fails gracefully", async () => {
  let constructions = 0;
  const audio = new AudioEngine({ AudioContext: class { constructor() { constructions++; throw new Error("blocked"); } } });
  assert.equal(constructions, 0); assert.equal(audio.playTone(), null);
  audio.setVolumes({ music: 2 });
  assert.equal(await audio.unlock(), false); assert.equal(constructions, 1);
  audio.destroy(); assert.equal(await audio.unlock(), false);
});
test("audio builds buses, procedural voices, music crossfades and camera listener", async () => {
  const param = () => ({ value: 0, setValueAtTime(v) { this.value = v; }, setTargetAtTime(v) { this.value = v; },
    linearRampToValueAtTime(v) { this.value = v; }, exponentialRampToValueAtTime(v) { this.value = v; }, cancelScheduledValues() {} });
  const node = () => ({ connections: [], connect(destination) { this.connections.push(destination); },
    disconnect() { this.connections.length = 0; }, gain: param(), frequency: param(),
    threshold: param(), knee: param(), ratio: param(), attack: param(), release: param() });
  class FakeAudioContext {
    constructor() {
      this.state = "suspended"; this.currentTime = 0; this.sampleRate = 100; this.destination = node();
      this.listener = Object.fromEntries(["position", "forward", "up"].flatMap(prefix => ["X", "Y", "Z"].map(axis => [prefix + axis, param()])));
    }
    createGain() { return node(); }
    createDynamicsCompressor() { return node(); }
    createConvolver() { return node(); }
    createOscillator() { return { ...node(), start() {}, stop() {} }; }
    createPanner() { return { ...node(), positionX: param(), positionY: param(), positionZ: param() }; }
    createBuffer(channels, length) { return { getChannelData: () => new Float32Array(length) }; }
    async resume() { this.state = "running"; }
    async close() { this.state = "closed"; }
  }
  const camera = new Camera();
  const audio = new AudioEngine({ AudioContext: FakeAudioContext, camera, settings: { music: 0.4 } });
  assert.equal(await audio.unlock(), true);
  assert.equal(audio.channels.music.gain.value, 0.4);
  for (const bus of Object.values(audio.channels)) {
    assert.ok(bus.connections.includes(audio.master));
    assert.ok(bus.connections.includes(audio.reverb));
  }
  assert.deepEqual(audio.reverb.connections, [audio.wet]);
  assert.deepEqual(audio.wet.connections, [audio.master]);
  assert.deepEqual(audio.master.connections, [audio.limiter]);
  audio.setMusic("puzzle"); assert.equal(audio.musicVoices.length, 3);
  const tone = audio.playProfile("runner", "collect", { position: { x: 3, y: 2, z: 1 } });
  assert.equal(tone.panner.positionX.value, 3);
  assert.deepEqual(tone.panner.connections, [audio.channels.sfx]);
  audio.setVolumes({ sfx: 0, ui: 0 });
  const mutedSfx = audio.tone(220, 0.1, "sfx");
  const mutedUi = audio.tone(440, 0.1, "ui");
  assert.deepEqual(mutedSfx.envelope.connections, [audio.channels.sfx]);
  assert.deepEqual(mutedUi.envelope.connections, [audio.channels.ui]);
  assert.equal(audio.channels.sfx.gain.value, 0); assert.equal(audio.channels.ui.gain.value, 0);
  assert.ok(!mutedSfx.envelope.connections.includes(audio.reverb));
  assert.ok(!mutedUi.envelope.connections.includes(audio.reverb));
  assert.equal(audio.channels.music.gain.value, 0.4 * 0.35);
  audio.context.currentTime = 2; audio.update();
  assert.equal(audio.channels.music.gain.value, 0.4);
  assert.equal(audio.context.listener.positionZ.value, 10);
  assert.equal(audio.tone(330, 0.1, "ui").oscillator.frequency.value, 330);
  audio.setMusic("casino"); assert.equal(audio.musicVoices.length, 3);
  audio.setMusic(null); assert.equal(audio.musicVoices.length, 0);
  audio.destroy(); assert.equal(audio.context.state, "closed");
});
test("renderer tolerates unavailable canvas contexts and cleans up listeners", () => {
  const canvas = new Events(); canvas.getContext = () => null;
  const renderer = new LiquidRenderer(canvas, new Camera(), { quality: "low" });
  renderer.resize(800, 600, 2); assert.equal(canvas.width, 520);
  renderer.render(1); renderer.setQuality("high", true); renderer.destroy();
  assert.equal(canvas.events.get("webglcontextlost").size, 0);
});
test("low quality never initializes or renders WebGL and supports switching back to high", () => {
  const canvas = new Events(); canvas.style = { visibility: "" }; let contexts = 0;
  canvas.getContext = () => { contexts++; return null; };
  const renderer = new LiquidRenderer(canvas, new Camera(), { quality: "low" });
  renderer.render(2); assert.equal(contexts, 0); assert.equal(canvas.style.visibility, "hidden");
  renderer.setQuality("high"); assert.ok(contexts > 0); assert.equal(canvas.style.visibility, "");
  renderer.gl = { drawArrays() { throw new Error("Low quality must not draw"); } };
  renderer.setQuality("low"); renderer.render(3);
  renderer.destroy(); assert.equal(canvas.style.visibility, "");
});
test("context loss hides liquid until restoration and respects low quality", () => {
  const canvas = new Events(); canvas.style = { visibility: "" }; canvas.getContext = () => null;
  const renderer = new LiquidRenderer(canvas, new Camera());
  canvas.emit("webglcontextlost"); assert.equal(canvas.style.visibility, "hidden");
  renderer.setQuality("high"); assert.equal(canvas.style.visibility, "hidden");
  canvas.emit("webglcontextrestored"); assert.equal(canvas.style.visibility, "");
  renderer.setQuality("low");
  canvas.emit("webglcontextlost"); canvas.emit("webglcontextrestored");
  assert.equal(canvas.style.visibility, "hidden");
  renderer.destroy();
});
