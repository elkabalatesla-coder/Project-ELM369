# Liquid Arcade

## Run

From the repository root:

```sh
python3 -m tools.elm_arcade --port 8369
```

Open `http://127.0.0.1:8369/` in a modern browser. No build, npm install, external
assets, accounts, or network services are needed. The server binds only to
loopback, serves only the arcade directory, and disables directory listings.
The site can also be hosted as static files; ES modules require HTTP rather than
`file://`. Casino randomness requires Web Crypto (localhost or HTTPS).

**Entertainment only: virtual credits have no monetary value. There are no
deposits, purchases, withdrawals, prizes, payment integrations, or cash-outs.**
Browser saves are editable local simulation data, not a trusted currency ledger.

The existing tool layout, Python CLI, unittest discovery, and tool registry are
reused. PR #139 was inspected: its proposed-bid calculator is independent and
was not changed or connected to credits. Existing Liquid3D prompting tools
describe prompts rather than a runtime renderer; this tool supplies its own
native WebGL renderer and synthesized sounds without copying archived assets.

## Modules

| Location under `tools/elm_arcade/` | Responsibility |
|---|---|
| `catalog.json`, `catalog.mjs` | Trusted installed plugin discovery |
| `core/registry.mjs` | Manifests, semantic versions, explicit save migrations |
| `core/loop.mjs` | Fixed 60 Hz update, bounded catch-up, interpolation fraction, state transitions |
| `core/input.mjs` | Keyboard, pointer/touch, gamepad, edge-triggered actions, blur cleanup |
| `core/storage.mjs` | Versioned local settings, game snapshots, high scores, unlocks |
| `core/camera.mjs` | Follow/orbit/dolly, damped motion, spline timelines, shake |
| `core/renderer.mjs` | Liquid surface with reflection/refraction and glossy lighting, fallback |
| `core/audio.mjs` | Master/music/SFX/UI buses, limiter, reverb, spatial audio, ducking and crossfade |
| `math/` | Pure algorithms; see [math](math.md) and [RTP schedules](rtp.md) |
| `games/arcade.mjs`, `games/casino.mjs` | Installed game factories |
| `app.mjs`, `replay.mjs` | Browser shell, upgrades, bounded deterministic arcade replays |
| `strategy-worker.mjs` | Cancellable, exact hold enumeration off the main thread |

The shell walks attract → menu → play → pause or game over → high score. It
saves on pause, menu, and page exit; casino transactions also save immediately.
Settings/storage failures fall back to an in-memory session. Future-version and
missing-migration saves are rejected instead of silently reinterpreted.

Simulation runs at fixed 1/60-second steps; a separate time accumulator applies
time scale without changing the simulation step. Hidden tabs pause and do not
accumulate a large catch-up. Render receives the accumulator interpolation
fraction. The four primary arcade games interpolate moving bodies.

## Rendering, camera, and audio

Games are Canvas 2D foregrounds with a composited **3D WebGL liquid scene**.
This is not a claim that every game has 3D models or physically simulated fluid.
The shader ray-intersects an animated height field and approximates Fresnel
reflection, refraction, caustics, and specular gloss. Follow/orbit/spline
camera coordinates drive the scene and audio listener. The game-camera adapter
converts pixel coordinates to scene units; orbit/timeline selection is not
overridden by game follow updates. Low quality and reduced-motion support
provide the low-end path.

“4D” means a timed camera spline, **not a fourth spatial dimension**. The time
slider also slows arcade simulation and replay playback. Replay captures the
initial snapshot, seed, upgrades, and per-tick inputs, is bounded to ten minutes
at 60 Hz, and is in-memory only. Replay never writes saves, unlocks, or scores.
Casino games use a secure RNG and are deliberately excluded from replay rewards.

Sound starts only after a user gesture. Browser-denied audio never blocks play.
Music uses procedural harmonic voices with crossfades; SFX are per-game tones
through spatial panners, reverb, and a compressor/limiter. This is a dependency-
free procedural sound design, not a mastered sample soundtrack. Master/music/
SFX/UI volumes and quality persist locally.

## Delivery status

The catalog labels each entry; a minimal game is playable, not a production-
complete interpretation of its genre.

* Primary arcade games: **Nebula Patrol (shooter), brick breaker, snake, maze
  chase** — collision, scoring, difficulty/levels, loss conditions, upgrades.
* Minimal arcade prototypes: platformer, endless runner, racing, simple
  fighting, falling-block puzzle, pinball, rhythm, tower defense. Each has a
  distinct mechanic and explicit TODOs for deeper content.
* Video poker: Jacks or Better and Deuces Wild; Bonus, Double Bonus, Double
  Double Bonus, Joker, Tens or Better, All American; 3/5/10-hand Jacks or Better.
  Gross paytables and assumptions are shown. The future-multiplier mode is an
  explicitly labeled **house-rule prototype**, not a commercial Ultimate X clone.
* Three- and five-reel slots: explicit strips, paylines, and computed exact RTP.
* Minimal casino games: blackjack, European/American straight-bet roulette,
  Player-bet baccarat, five-pick keno, pass-line craps, and scratch reveal.
  Side bets and full casino-table interfaces are not implemented.

The registry deliberately reports the overall tool as `SCAFFOLD` rather than
claiming every requested genre is finished. See [plugin upgrades](plugins.md)
for extending these prototypes.

## Validation

Python 3.12 and Node.js 22 (no Node packages):

```sh
python3 -m unittest discover -s tools/elm_arcade/tests -v
```

The Python tests invoke native Node assertions against the same `.mjs` modules
used in the browser. CI runs this command on changes to the tool. Tests cover
math, game lifecycle/transactions, engine components, catalog restrictions,
replay isolation, and local HTTP behavior. Browser/WebGL/audio-device quality
still needs human evaluation; automated math tests do not establish casino
certification, an optimal player policy, or any payout guarantee.
