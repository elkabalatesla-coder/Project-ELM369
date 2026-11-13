# Adding and upgrading a game

Install trusted JavaScript under `tools/elm_arcade/games/` and add its module
and named array export to `tools/elm_arcade/catalog.json`. No core-engine edit
is needed. Catalog paths must stay inside the local games directory; manifests
and saves cannot supply remote code. Plugins are trusted installed code, not
untrusted uploads, and execute with the page's privileges.

```js
export const plugins = [{
  manifest: {
    id: 'example', title: 'Example', version: '1.0.0',
    genre: 'puzzle', status: 'minimal',
    description: 'A playable example; remaining content is labeled.',
    controls: 'Arrows move; Space acts; Enter confirms.',
    config: {
      featureFlags: {liquid: true, audio: true, upgrades: true},
    },
    features: ['keyboard', 'snapshots'],
    upgrades: [{id: 'shield', title: 'Shield', cost: 100}],
    sound: {type: 'triangle', base: 220},
  },
  create(context) {
    // Restore and validate context.load(); keep state private.
    return {
      update(dt) { /* Fixed-step simulation, no wall-clock dependence. */ },
      render(alpha) { /* Interpolate previous/current positions. */ },
      serialize() { return {}; },
      destroy() { /* Release game-specific listeners/resources. */ },
    };
  },
}];
```

## Context and invariants

* `canvas` (960×540), `ctx`: foreground rendering; render must balance
  `save()`/`restore()` and avoid injecting HTML.
* `input.down(action)`, `input.pressed(action)`, `input.pointer`:
  directional, `fire`, `confirm`, `pause` actions; pointer coordinates are in
  canvas pixels. The shell consumes edges once per simulation tick. Do not
  install extra global listeners unless `destroy()` removes them.
* `random.int(max)`: use this instead of `Math.random()` for game outcomes.
  Casino context uses secure entropy. Arcade context is seeded for replay.
* `audio.tone(frequency, seconds, bus, position)`: procedural profile sound;
  positions use game pixel coordinates and are adapted to world units.
* `camera.follow(subject)`, `camera.shake(strength, seconds)`: game facade,
  preserving the user's selected camera mode.
* `load()`, `save(data)`, `finish(score)`: load validates game-specific data;
  save only JSON data (never executable code); finish is idempotent in the
  shell and enters high scores. Serialize every timer/queue needed to resume.
* `upgrades`: set of this game's unlocked IDs. Upgrade `cost` in this shell
  is a **best-score threshold**, not a purchase price. Unlocks apply next run.
  They must actually change the intended mechanic. Do not change casino
  payouts without updating paytable/RTP assumptions.
* `features`: declared capabilities; `featureFlags`: optional plugin config.
  Shell flags `audio`, `liquid`, and `upgrades` disable those shared features.
  Game-specific flags should be checked explicitly by that game.

Local data is untrusted: validate dimensions, array bounds, uniqueness of cards,
finite values, phases, stakes, and pending bets before resuming. Never use a
save as a script/module path or render its values with `innerHTML`. Refuse
invalid saves without crediting an unresolved wager twice.

## Semantic-version migrations

Each plugin declares its own semantic version. New games start at `1.0.0`;
no migration is needed until a save format changes. For a `1.1.0` release:

```js
migrations: {
  '1.0.0': {
    to: '1.1.0',
    up(old) {
      return {...old, combo: 0};
    },
  },
},
```

Attach `migrations` to the plugin alongside `manifest` and `create`.
Migrations run on cloned data, follow explicit ascending version edges, and
must reach the current version. Missing paths, cycles, invalid semantic
versions, and future saves are errors. Keep every supported source edge and
test it; never simply overwrite the saved version. The outer storage schema
and per-game semantic version are separate.

## Upgrade checklist

1. Preserve the manifest ID; increment version when behavior/data changes.
2. Add a migration for changed save fields, plus invalid/old/future-save tests.
3. Keep outcomes deterministic under the injected arcade RNG.
4. Add a sound profile and meaningful power-up without new asset dependencies.
5. Exercise touch, keyboard, gamepad, pause, resume, loss, and replay.
6. Update prototype status/TODOs and [RTP disclosures](rtp.md) if rules change.
7. Keep virtual credits isolated from accounts, network services, and money.
