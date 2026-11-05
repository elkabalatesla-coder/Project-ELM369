const TRANSITIONS = {
  attract: ["menu"], menu: ["attract", "play", "highscore"],
  play: ["pause", "gameover", "menu"], pause: ["play", "menu"],
  gameover: ["highscore", "play", "menu"], highscore: ["menu", "play", "attract"],
};
export class StateMachine {
  constructor(initial = "attract") {
    if (!Object.hasOwn(TRANSITIONS, initial)) throw new Error(`Unknown state: ${initial}`);
    this.state = initial;
  }
  canTransition(next) { return TRANSITIONS[this.state].includes(next); }
  transition(next) {
    if (!this.canTransition(next)) throw new Error(`Invalid transition: ${this.state} → ${next}`);
    this.state = next;
    return next;
  }
}
export class GameLoop {
  constructor({ update = () => {}, render = () => {}, step = 1 / 60, maxCatchup = 5,
    requestFrame = cb => globalThis.requestAnimationFrame(cb), cancelFrame = id => globalThis.cancelAnimationFrame(id),
    document = globalThis.document } = {}) {
    if (!(step > 0) || !Number.isFinite(step) || !Number.isInteger(maxCatchup) || maxCatchup < 1) throw new TypeError("Invalid fixed timestep");
    Object.assign(this, { update, render, step, maxCatchup, requestFrame, cancelFrame, document });
    this.running = false; this.paused = false; this.hidden = Boolean(document?.hidden);
    this.accumulator = 0; this.lastTime = null; this.frame = null;
    this.onVisibility = () => { this.hidden = Boolean(document.hidden); this.lastTime = null; this.accumulator = 0; };
    document?.addEventListener("visibilitychange", this.onVisibility);
    this.onFrame = time => { if (!this.running) return; this.tick(time); if (this.running) this.frame = this.requestFrame(this.onFrame); };
  }
  tick(time) {
    if (!Number.isFinite(time)) return;
    if (this.paused || this.hidden) { this.lastTime = null; return; }
    if (this.lastTime === null) { this.lastTime = time; this.render(0); return; }
    const delta = Math.min(Math.max((time - this.lastTime) / 1000, 0), this.step * this.maxCatchup);
    this.lastTime = time;
    this.accumulator += delta;
    let count = 0;
    while (this.accumulator + 1e-10 >= this.step && count < this.maxCatchup) {
      this.update(this.step); this.accumulator = Math.max(0, this.accumulator - this.step); count++;
    }
    this.render(Math.min(1, this.accumulator / this.step));
  }
  start() { if (!this.running) { this.running = true; this.lastTime = null; this.frame = this.requestFrame(this.onFrame); } }
  stop() { this.running = false; if (this.frame !== null) this.cancelFrame(this.frame); this.frame = null; this.lastTime = null; this.accumulator = 0; }
  pause() { this.paused = true; this.lastTime = null; this.accumulator = 0; }
  resume() { this.paused = false; this.lastTime = null; }
  destroy() { this.stop(); this.document?.removeEventListener("visibilitychange", this.onVisibility); }
}
