import {Registry} from './core/registry.mjs';
import {Store} from './core/storage.mjs';
import {GameLoop, StateMachine} from './core/loop.mjs';
import {Input} from './core/input.mjs';
import {Camera} from './core/camera.mjs';
import {AudioEngine} from './core/audio.mjs';
import {LiquidRenderer} from './core/renderer.mjs';
import {SecureRNG, SeededRNG} from './math/rng.mjs';
import {loadCatalog} from './catalog.mjs';
import {ReplayTape} from './replay.mjs';

const $ = id => document.getElementById(id);
const store = new Store();
let settings = store.getSettings();
const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
if (reducedMotion) settings = store.setSettings({quality: 'low', reducedMotion: true});
const registry = new Registry();
const machine = new StateMachine();
const canvas = $('game'), ctx = canvas.getContext('2d');
const input = new Input(canvas);
const camera = new Camera();
const audio = new AudioEngine({camera, settings});
const renderer = new LiquidRenderer($('liquid'), camera, settings);
let active = null, game = null, random = null, gameInput = input;
let tape = null, lastTape = null, replaying = false, simulationTime = 0;
let completed = false, initial = null;

const isCasino = manifest => manifest.genre.toLowerCase().includes('casino') ||
  manifest.features.includes('virtual credits');
function status(message) { $('status').textContent = message; }
function setCamera() {
  const mode = $('camera-mode').value;
  if (settings.quality === 'low' || settings.reducedMotion) {
    camera.follow({x: 0, y: 0, z: 0}, {x: 0, y: 2, z: 10});
  } else if (mode === 'orbit') camera.orbit({x: 0, y: 0, z: 0}, 12, 0.2, 4);
  else if (mode === 'dolly' || mode === 'cinematic') {
    camera.track([
      {time: 0, position: {x: -5, y: 4, z: 12}, target: {x: 0, y: 0, z: 0}},
      {time: 5, position: {x: 4, y: 2, z: 8}, target: {x: 0, y: 0, z: 0}},
      {time: 10, position: {x: 0, y: 6, z: 14}, target: {x: 0, y: 0, z: 0}},
      {time: 15, position: {x: -5, y: 4, z: 12}, target: {x: 0, y: 0, z: 0}},
    ], {loop: true});
  } else {
    camera.follow(() => ({
      x: input.pointer.inside ? (input.pointer.x / canvas.width - 0.5) * 3 : 0,
      y: 0, z: 0,
    }), {x: 0, y: 3, z: 10});
  }
  camera.setTimeScale(Number($('time-scale').value));
}
setCamera();

function showScores() {
  $('scores').replaceChildren();
  for (const entry of store.getScores(active.id)) {
    const item = document.createElement('li');
    item.textContent = `${entry.name}: ${Math.round(entry.score)}`;
    $('scores').append(item);
  }
  const unlocked = new Set(store.getUnlocks());
  const best = store.getScores(active.id)[0]?.score || 0;
  $('upgrades').replaceChildren();
  for (const upgrade of active.config.featureFlags?.upgrades === false ? [] : active.upgrades) {
    const key = `${active.id}:${upgrade.id}`;
    const button = document.createElement('button');
    button.textContent = `${upgrade.title || upgrade.id} — ${unlocked.has(key) ? 'unlocked' : `reach score ${upgrade.cost}`}`;
    button.disabled = unlocked.has(key) || best < upgrade.cost || replaying;
    button.addEventListener('click', () => {
      store.unlock(key);
      status('Upgrade unlocked. It takes effect next game; no money or credits are spent.');
      showScores();
    });
    $('upgrades').append(button);
  }
}
function savedData() {
  const saved = store.loadGame(active.id);
  if (!saved) return null;
  try {
    const data = registry.migrate(active.id, saved).data;
    return data?.over ? null : data;
  }
  catch (error) {
    status(`Save was not loaded: ${error.message}. Original data is preserved until you play.`);
    return null;
  }
}
function save() {
  if (!game || !active || replaying) return;
  if (typeof game.serialize === 'function') {
    store.saveGame(active.id, active.version, game.serialize());
  }
}
function showOverlay(title, message, resumable) {
  $('overlay-title').textContent = title;
  $('overlay-message').textContent = message;
  $('resume').hidden = !resumable;
  $('overlay').hidden = false;
}
function finish(score) {
  if (completed || machine.state !== 'play') return;
  completed = true;
  machine.transition('gameover');
  if (!replaying) {
    save();
    store.addScore(active.id, Number.isFinite(score) ? score : 0);
    if (tape?.complete && tape.frames.length) lastTape = tape;
  }
  machine.transition('highscore');
  $('replay').disabled = !lastTape;
  showScores();
  showOverlay(replaying ? 'Replay finished' : 'Game over',
    `Score: ${Math.round(Number.isFinite(score) ? score : 0)}. Choose New game or Save & menu.`, false);
  audio.playProfile(active.sound, 'lose');
}
function disposeGame() {
  if (!game) return;
  save();
  game.destroy?.();
  game = null;
}
async function start(id, {fresh = false, replay = null} = {}) {
  disposeGame();
  active = registry.get(id).manifest;
  replaying = Boolean(replay);
  completed = false;
  simulationTime = 0;
  initial = replay ? structuredClone(replay.initial) : fresh ? null : savedData();
  const seed = replay?.seed ?? new SecureRNG().int(0x100000000);
  random = isCasino(active) ? new SecureRNG() : new SeededRNG(seed);
  const upgrades = replay?.upgrades || store.getUnlocks()
    .filter(key => key.startsWith(`${id}:`)).map(key => key.slice(id.length + 1));
  tape = !isCasino(active) && !replay ? new ReplayTape({id, seed, initial, upgrades}) : null;
  if (replay) { replay.reset(); tape = replay; }
  gameInput = input;
  const proxyInput = {
    down: action => gameInput.down(action), pressed: action => gameInput.pressed(action),
    get pointer() { return gameInput.pointer; }, endFrame() {},
  };
  const context = {
    canvas, ctx, input: proxyInput, random, settings,
    camera: {
      follow(subject) {
        if ($('camera-mode').value !== 'follow' || settings.quality === 'low') return;
        camera.follow(() => {
          const target = typeof subject === 'function' ? subject() : subject;
          return {x: (target.x - 480) / 96, y: (270 - target.y) / 96, z: 0};
        }, {x: 0, y: 3, z: 10});
      },
      shake(strength = 3, duration) {
        if (!settings.reducedMotion && settings.quality !== 'low') camera.shake(strength / 96, duration);
      },
    },
    audio: {
      tone(frequency, duration, channel = 'sfx', position) {
        if (active.config.featureFlags?.audio === false) return;
        const world = position ? {x: (position.x - 480) / 96, y: (270 - position.y) / 96, z: position.z || 0} : undefined;
        audio.playProfile(active.sound, 'action', {frequency, duration, channel, position: world});
      },
    },
    get pointer() { return gameInput.pointer; }, upgrades: new Set(upgrades),
    features: new Set(active.features), featureFlags: {...active.config.featureFlags}, finish,
    load: () => structuredClone(initial),
    save: data => { if (!replaying) store.saveGame(id, active.version, data); },
  };
  try {
    game = registry.create(id, context);
  } catch (error) {
    status(`Unable to start ${active.title}: ${error.message}`);
    replaying = false;
    return;
  }
  if (machine.state === 'attract') machine.transition('menu');
  if (machine.state === 'pause' || machine.state === 'play') machine.transition('menu');
  machine.transition('play');
  $('lobby').hidden = true;
  $('play-area').hidden = false;
  $('overlay').hidden = true;
  $('game-title').textContent = `${active.title}${replaying ? ' — replay (no saves/rewards)' : ''}`;
  $('instructions').textContent = `${active.description || ''} ${Array.isArray(active.controls) ? active.controls.join(' · ') : active.controls || 'Arrow keys: move/select. Space: action. Enter: confirm. Escape: pause.'}`;
  $('pause').textContent = 'Pause';
  $('liquid').hidden = active.config.featureFlags?.liquid === false;
  input.release();
  canvas.focus();
  showScores();
  const title = active.title;
  status(`${replaying ? 'Replay' : 'Playing'} ${title} · ${active.status}`);
  audio.unlock().then(enabled => {
    if (active?.id !== id || !game) return;
    audio.setVolumes(settings);
    audio.setMusic(active.config.featureFlags?.audio === false ? null : active.sound);
    if (!enabled) status(`Playing ${title} · Audio unavailable or muted`);
  });
}
function pause() {
  if (machine.state === 'play') {
    machine.transition('pause'); save();
    showOverlay('Paused', 'Your session is saved. Resume or start a new game.', true);
    $('pause').textContent = 'Resume';
    audio.duck(60);
  } else if (machine.state === 'pause') {
    machine.transition('play');
    $('overlay').hidden = true;
    $('pause').textContent = 'Pause';
    input.release();
    audio.duckUntil = 0;
    audio.setVolumes(settings);
    canvas.focus();
  }
}
const loop = new GameLoop({
  update(dt) {
    if (input.pressed('pause')) { pause(); input.endFrame(); }
    if (machine.state !== 'play' || !game) { input.endFrame(); return; }
    camera.update(dt);
    simulationTime += dt * camera.timeScale;
    while (simulationTime + 1e-10 >= 1 / 60 && machine.state === 'play') {
      simulationTime = Math.max(0, simulationTime - 1 / 60);
      if (replaying) {
        gameInput = tape.next();
        if (!gameInput) { gameInput = input; finish(0); break; }
      } else {
        gameInput = input;
        tape?.record(input);
      }
      game.update(1 / 60);
      input.endFrame();
    }
    audio.update();
  },
  render() {
    if (!game) return;
    renderer.render(camera.time);
    ctx.save();
    try { game.render(Math.min(1, simulationTime * 60)); }
    finally { ctx.restore(); }
  },
});
$('pause').addEventListener('click', pause);
$('resume').addEventListener('click', pause);
$('restart').addEventListener('click', () => start(active.id, {fresh: true}));
$('replay').addEventListener('click', () => lastTape && start(lastTape.id, {replay: lastTape}));
$('back').addEventListener('click', () => {
  if (!replaying && tape?.complete && tape.frames.length) lastTape = tape;
  if (!replaying && active && isCasino(active) && !completed) {
    const credits = game?.serialize?.()?.credits;
    if (Number.isFinite(credits)) store.addScore(active.id, Math.max(0, credits - 1000));
  }
  disposeGame();
  if (machine.canTransition('menu')) machine.transition('menu');
  $('play-area').hidden = true;
  $('lobby').hidden = false;
  audio.setMusic(null);
  $('replay').disabled = !lastTape;
  status('Session saved locally. Choose another game.');
});
$('camera-mode').addEventListener('change', setCamera);
$('time-scale').addEventListener('input', () => camera.setTimeScale(Number($('time-scale').value)));
$('quality').value = settings.quality;
$('quality').addEventListener('change', () => {
  settings = store.setSettings({quality: $('quality').value});
  renderer.setQuality(settings.quality, settings.reducedMotion);
  setCamera();
});
for (const slider of document.querySelectorAll('[data-volume]')) {
  slider.value = settings[slider.dataset.volume];
  slider.addEventListener('input', async () => {
    settings = store.setSettings({[slider.dataset.volume]: Number(slider.value)});
    await audio.unlock();
    audio.setVolumes(settings);
  });
}
document.addEventListener('visibilitychange', () => {
  if (document.hidden && machine.state === 'play') pause();
});
document.addEventListener('click', event => {
  if (event.target.closest('button') && active?.config.featureFlags?.audio !== false) {
    audio.playTone({frequency: 740, duration: 0.035, channel: 'ui', volume: 0.08});
  }
});
window.addEventListener('pagehide', save);
window.addEventListener('resize', () => renderer.resize());
let solver = null;
function cancelSolver() {
  solver?.terminate(); solver = null; $('solve').disabled = false;
}
$('cancel-solve').addEventListener('click', () => { cancelSolver(); $('solver-result').textContent = 'Calculation canceled.'; });
$('solve').addEventListener('click', () => {
  cancelSolver();
  const raw = $('solver-hand').value.split(',').map(s => s.trim());
  const hand = raw.map(Number);
  if (raw.some(s => s === '') || hand.length !== 5 || new Set(hand).size !== 5 ||
      hand.some(c => !Number.isInteger(c) || c < 0 || c > 51)) {
    $('solver-result').textContent = 'Enter five distinct integer card IDs from 0 to 51.';
    return;
  }
  $('solver-result').textContent = 'Enumerating all 32 holds and replacement combinations…';
  $('solve').disabled = true;
  solver = new Worker(new URL('./strategy-worker.mjs', import.meta.url), {type: 'module'});
  solver.onmessage = ({data}) => {
    $('solver-result').textContent = data.error || JSON.stringify(data.result, null, 2);
    cancelSolver();
  };
  solver.onerror = () => { $('solver-result').textContent = 'Calculation failed; no result was assumed.'; cancelSolver(); };
  solver.postMessage({hand, variant: $('solver-variant').value});
});
try {
  const response = await fetch('./catalog.json');
  if (!response.ok) throw new Error('Cannot load local catalog');
  for (const plugin of await loadCatalog(await response.json(), import.meta.url)) registry.register(plugin);
  for (const manifest of registry.list()) {
    const card = document.createElement('article');
    card.className = 'card';
    const title = document.createElement('h3'); title.textContent = manifest.title;
    const badge = document.createElement('span'); badge.className = 'badge';
    badge.textContent = `${manifest.status} · v${manifest.version} · ${manifest.genre}`;
    const description = document.createElement('p'); description.textContent = manifest.description || '';
    const button = document.createElement('button'); button.textContent = 'Play / resume';
    button.addEventListener('click', () => start(manifest.id));
    card.append(title, badge, description, button); $('catalog').append(card);
  }
  machine.transition('menu');
  renderer.resize(); loop.start();
  status(`${registry.list().length} locally installed games. Virtual credits only.`);
} catch (error) { status(`Arcade could not load: ${error.message}`); }
