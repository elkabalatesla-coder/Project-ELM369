export const clamp = (x, low, high) => Math.max(low, Math.min(high, x));
export const lerp = (a, b, t) => a + (b - a) * t;
const vec = (p = {}) => ({ x: p.x ?? 0, y: p.y ?? 0, z: p.z ?? 0 });
const normalize = p => { const n = Math.hypot(p.x, p.y, p.z) || 1; return { x: p.x / n, y: p.y / n, z: p.z / n }; };
const cross = (a, b) => ({ x: a.y * b.z - a.z * b.y, y: a.z * b.x - a.x * b.z, z: a.x * b.y - a.y * b.x });
const dot = (a, b) => a.x * b.x + a.y * b.y + a.z * b.z;

export function damp(current, target, velocity, dt, smoothTime = 0.25) {
  const omega = 2 / Math.max(0.001, smoothTime), offset = current - target;
  const e = Math.exp(-omega * Math.max(0, dt)), c = velocity + omega * offset;
  return { value: target + (offset + c * dt) * e, velocity: (velocity - omega * c * dt) * e };
}
export function spline(a, b, c, d, t) {
  return 0.5 * ((2 * b) + (-a + c) * t + (2 * a - 5 * b + 4 * c - d) * t * t +
    (-a + 3 * b - 3 * c + d) * t * t * t);
}

export class Camera {
  constructor({ position = { x: 0, y: 0, z: 10 }, target = { x: 0, y: 0, z: 0 }, smoothTime = 0.25, random = Math.random } = {}) {
    this.position = vec(position); this.target = vec(target); this.desired = vec(position);
    this.velocity = vec(); this.smoothTime = smoothTime; this.random = random;
    this.zoom = 1; this.timeScale = 1; this.time = 0; this.mode = "manual"; this.keyframes = [];
    this.shakeOffset = vec(); this.shakeTime = 0; this.shakeDuration = 0; this.shakeStrength = 0;
    this.replay = { version: 1, elapsed: 0, timeScale: 1, events: [] };
  }
  follow(subject, offset = { x: 0, y: 0, z: 10 }) {
    this.subject = subject; this.offset = vec(offset); this.mode = "follow"; return this;
  }
  orbit(center = { x: 0, y: 0, z: 0 }, radius = 10, speed = 0.2, elevation = 4) {
    this.orbitSettings = { center: vec(center), radius, speed, elevation, angle: 0 }; this.mode = "orbit"; return this;
  }
  dolly(distance) { this.desired.z = Math.max(0.1, this.desired.z + distance); this.mode = "manual"; return this; }
  track(keyframes, { loop = false } = {}) {
    if (!Array.isArray(keyframes) || keyframes.length < 2 ||
        keyframes.some((k, i) => !Number.isFinite(k.time) || k.time < 0 || !k.position ||
          ["x", "y", "z"].some(axis => !Number.isFinite(k.position[axis])) ||
          (i > 0 && k.time <= keyframes[i - 1].time))) throw new TypeError("Camera track needs increasing timed positions");
    this.keyframes = structuredClone(keyframes); this.trackLoop = loop; this.trackTime = 0; this.mode = "track"; return this;
  }
  setTimeScale(scale) {
    if (!Number.isFinite(scale) || scale < 0 || scale > 4) throw new RangeError("timeScale must be between 0 and 4");
    this.timeScale = scale; this.replay.events.push({ time: this.time, timeScale: scale }); return this;
  }
  shake(strength = 3, duration = 0.25) {
    this.shakeStrength = Math.max(0, strength); this.shakeDuration = this.shakeTime = Math.max(0, duration); return this;
  }
  update(dt) {
    if (!Number.isFinite(dt) || dt < 0) return;
    const scaled = dt * this.timeScale;
    this.time += dt;
    if (this.mode === "follow") {
      const subject = typeof this.subject === "function" ? this.subject() : this.subject;
      if (subject) {
        this.target = vec(subject);
        for (const axis of ["x", "y", "z"]) this.desired[axis] = (subject[axis] || 0) + this.offset[axis];
      }
    } else if (this.mode === "orbit") {
      const o = this.orbitSettings;
      o.angle += scaled * o.speed; this.target = vec(o.center);
      this.desired = { x: o.center.x + Math.sin(o.angle) * o.radius, y: o.center.y + o.elevation, z: o.center.z + Math.cos(o.angle) * o.radius };
    } else if (this.mode === "track") {
      const frames = this.keyframes, last = frames.at(-1).time;
      this.trackTime += scaled;
      const t = this.trackLoop && last > 0 ? this.trackTime % last : Math.min(this.trackTime, last);
      let i = frames.findIndex((k, index) => index < frames.length - 1 && t < frames[index + 1].time);
      if (i < 0) i = frames.length - 2;
      const a = frames[Math.max(0, i - 1)], b = frames[i], c = frames[i + 1], d = frames[Math.min(frames.length - 1, i + 2)];
      const u = clamp((t - b.time) / (c.time - b.time), 0, 1);
      for (const axis of ["x", "y", "z"]) {
        this.desired[axis] = spline(a.position[axis], b.position[axis], c.position[axis], d.position[axis], u);
        if (b.target && c.target) this.target[axis] = lerp(b.target[axis] ?? 0, c.target[axis] ?? 0, u);
      }
      if (b.timeScale !== undefined && c.timeScale !== undefined) this.timeScale = clamp(lerp(b.timeScale, c.timeScale, u), 0, 4);
    }
    for (const axis of ["x", "y", "z"]) {
      const result = damp(this.position[axis], this.desired[axis], this.velocity[axis], scaled, this.smoothTime);
      this.position[axis] = result.value; this.velocity[axis] = result.velocity;
    }
    this.shakeTime = Math.max(0, this.shakeTime - dt);
    const strength = this.shakeDuration ? this.shakeStrength * this.shakeTime / this.shakeDuration : 0;
    this.shakeOffset = { x: (this.random() * 2 - 1) * strength, y: (this.random() * 2 - 1) * strength, z: 0 };
    this.replay.elapsed = this.time; this.replay.timeScale = this.timeScale;
    return scaled;
  }
  getPosition() { return { x: this.position.x + this.shakeOffset.x, y: this.position.y + this.shakeOffset.y, z: this.position.z }; }
  apply(ctx, width, height) {
    const p = this.getPosition(), scale = this.zoom * 10 / Math.max(0.1, Math.abs(p.z));
    ctx.translate(width / 2, height / 2); ctx.scale(scale, scale); ctx.translate(-p.x, -p.y);
  }
  worldToScreen(point, width, height) {
    const p = this.getPosition(), s = this.zoom * 10 / Math.max(0.1, Math.abs(p.z));
    return { x: width / 2 + (point.x - p.x) * s, y: height / 2 + (point.y - p.y) * s };
  }
  getListener() {
    const position = this.getPosition();
    let forward = normalize({ x: this.target.x - position.x, y: this.target.y - position.y, z: this.target.z - position.z });
    if (!Math.hypot(forward.x, forward.y, forward.z)) forward = { x: 0, y: 0, z: -1 };
    const up = Math.abs(forward.y) > 0.999 ? { x: 0, y: 0, z: 1 } : { x: 0, y: 1, z: 0 };
    return { position, forward, up };
  }
  getViewMatrix() {
    const { position: p, forward: f, up } = this.getListener();
    const z = { x: -f.x, y: -f.y, z: -f.z }, x = normalize(cross(up, z)), y = cross(z, x);
    return new Float32Array([x.x, y.x, z.x, 0, x.y, y.y, z.y, 0, x.z, y.z, z.z, 0, -dot(x, p), -dot(y, p), -dot(z, p), 1]);
  }
  getReplayMetadata() { return structuredClone(this.replay); }
}
