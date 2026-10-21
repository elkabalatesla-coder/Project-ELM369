export const INSTRUCTIONS = Object.freeze({
  move: "Arrow keys / WASD / left stick / touch arrows",
  action: "Space / gamepad A / touch fire",
  fire: "Space / gamepad A / touch fire", confirm: "Enter / gamepad B / touch confirm",
  secondary: "Shift / gamepad X / touch secondary", pause: "Escape / P / gamepad Start",
  pointer: "Mouse or touch: point, drag, and tap",
});
const KEYS = {
  ArrowLeft: "left", KeyA: "left", ArrowRight: "right", KeyD: "right",
  ArrowUp: "up", KeyW: "up", ArrowDown: "down", KeyS: "down",
  Space: "fire", Enter: "confirm", ShiftLeft: "secondary", ShiftRight: "secondary",
  Escape: "pause", KeyP: "pause",
};
const canonical = action => action === "action" ? "fire" : action;
const editable = element => Boolean(element?.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(element?.tagName || "") ||
  element?.closest?.('[contenteditable="true"],[contenteditable=""]'));
export class Input {
  constructor(canvas, { target = globalThis.window, buttons = globalThis.document, navigator = globalThis.navigator } = {}) {
    this.canvas = canvas; this.navigator = navigator;
    this.sources = new Map(); this.edges = new Set(); this.listeners = []; this.gamepad = new Set();
    this.active = !canvas?.ownerDocument;
    this.pointer = { x: (canvas?.width || 960) / 2, y: (canvas?.height || 540) / 2, normalizedX: 0.5, normalizedY: 0.5, down: false, inside: false };
    if (canvas && canvas.tabIndex < 0) canvas.tabIndex = 0;
    const listen = (el, type, fn, options) => { el?.addEventListener(type, fn, options); this.listeners.push(() => el?.removeEventListener(type, fn, options)); };
    listen(target, "keydown", e => {
      const a = KEYS[e.code];
      if (a && !editable(e.target) && (this.active || canvas?.ownerDocument?.activeElement === canvas)) {
        e.preventDefault?.(); this.set(e.code, a, true);
      }
    });
    listen(target, "keyup", e => { if (KEYS[e.code]) this.set(e.code, KEYS[e.code], false); });
    listen(target, "blur", () => { this.setActive(false); });
    listen(canvas, "focus", () => this.setActive(true));
    listen(target, "focusin", e => { if (editable(e.target)) this.setActive(false); });
    listen(canvas, "pointermove", e => this.move(e));
    listen(canvas, "pointerdown", e => { e.preventDefault?.(); this.setActive(true); canvas.focus?.({ preventScroll: true }); this.move(e); this.pointer.down = true; this.set(`pointer:${e.pointerId}`, "fire", true); canvas.setPointerCapture?.(e.pointerId); });
    const releasePointer = e => { this.set(`pointer:${e.pointerId}`, "fire", false); this.pointer.down = [...this.sources.keys()].some(k => k.startsWith("pointer:")); };
    listen(target, "pointerdown", e => {
      if (e.target && e.target !== canvas && !canvas?.contains?.(e.target) && !e.target.closest?.("[data-action]")) this.setActive(false);
    });
    listen(target, "pointerup", releasePointer);
    listen(target, "pointercancel", releasePointer);
    listen(canvas, "lostpointercapture", releasePointer);
    listen(canvas, "pointerleave", () => { this.pointer.inside = false; });
    for (const button of buttons?.querySelectorAll?.("[data-action]") || []) {
      const action = canonical(button.dataset.action);
      listen(button, "pointerdown", e => { e.preventDefault(); this.setActive(true); button.setPointerCapture?.(e.pointerId); this.set(`touch:${e.pointerId}`, action, true); });
      for (const event of ["pointerup", "pointercancel", "lostpointercapture"]) {
        listen(button, event, e => this.set(`touch:${e.pointerId}`, action, false));
      }
    }
  }
  set(source, action, down) {
    const wasDown = [...this.sources.values()].includes(action);
    if (down) { this.sources.set(source, action); if (!wasDown) this.edges.add(action); }
    else this.sources.delete(source);
  }
  move(e) {
    const r = this.canvas.getBoundingClientRect();
    this.pointer.normalizedX = Math.max(0, Math.min(1, (e.clientX - r.left) / (r.width || 1)));
    this.pointer.normalizedY = Math.max(0, Math.min(1, (e.clientY - r.top) / (r.height || 1)));
    this.pointer.x = this.pointer.normalizedX * (this.canvas.width || r.width);
    this.pointer.y = this.pointer.normalizedY * (this.canvas.height || r.height);
    this.pointer.inside = true;
  }
  pollGamepad() {
    const next = new Set();
    let pads = [];
    try { pads = this.navigator?.getGamepads?.() || []; } catch { /* Gamepad may be policy-blocked. */ }
    for (const pad of pads) {
      if (!pad) continue;
      for (const [index, action] of [[0, "fire"], [1, "confirm"], [2, "secondary"], [9, "pause"], [12, "up"], [13, "down"], [14, "left"], [15, "right"]]) {
        if (pad.buttons[index]?.pressed) next.add(action);
      }
      if (pad.axes[0] < -0.25) next.add("left");
      if (pad.axes[0] > 0.25) next.add("right");
      if (pad.axes[1] < -0.25) next.add("up");
      if (pad.axes[1] > 0.25) next.add("down");
    }
    for (const action of new Set([...next, ...this.gamepad])) this.set(`pad:${action}`, action, next.has(action));
    this.gamepad = next;
  }
  down(action) { this.pollGamepad(); return [...this.sources.values()].includes(canonical(action)); }
  pressed(action) { this.pollGamepad(); return this.edges.has(canonical(action)); }
  setActive(active = true) { this.active = Boolean(active); if (!this.active) this.release(); }
  endFrame() { this.edges.clear(); }
  release() { this.sources.clear(); this.edges.clear(); this.gamepad.clear(); this.pointer.down = false; }
  destroy() { for (const remove of this.listeners) remove(); this.listeners = []; this.release(); }
}
