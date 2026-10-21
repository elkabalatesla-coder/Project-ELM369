export const ACTIONS = ['left', 'right', 'up', 'down', 'fire', 'confirm', 'pause'];

/** Bounded, in-memory replay tape. Casino rounds are never replayed into a bankroll. */
export class ReplayTape {
  constructor({id, seed, initial = null, upgrades = [], maxFrames = 36000}) {
    Object.assign(this, {id, seed, initial: structuredClone(initial), upgrades: [...upgrades], maxFrames});
    this.frames = [];
    this.complete = true;
    this.cursor = 0;
  }
  record(input) {
    if (this.frames.length >= this.maxFrames) { this.complete = false; return; }
    this.frames.push({
      down: ACTIONS.filter(action => input.down(action)),
      pressed: ACTIONS.filter(action => input.pressed(action)),
      pointer: {...input.pointer},
    });
  }
  reset() { this.cursor = 0; }
  next() {
    const frame = this.frames[this.cursor++];
    return frame ? {
      down: action => frame.down.includes(action),
      pressed: action => frame.pressed.includes(action),
      pointer: {...frame.pointer},
      endFrame() {},
    } : null;
  }
}
