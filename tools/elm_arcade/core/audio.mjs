const clampVolume = value => typeof value === "number" && Number.isFinite(value) ? Math.max(0, Math.min(1, value)) : 0.8;
export const SOUND_PROFILES = Object.freeze({
  arcade: { type: "square", base: 220 }, runner: { type: "sawtooth", base: 330 },
  puzzle: { type: "sine", base: 440 }, shooter: { type: "triangle", base: 110 },
  casino: { type: "sine", base: 660 },
});
export class AudioEngine {
  constructor({ camera, settings = {}, AudioContext = globalThis.AudioContext || globalThis.webkitAudioContext } = {}) {
    this.camera = camera; this.AudioContext = AudioContext; this.context = null;
    this.volumes = { master: 0.8, music: 0.5, sfx: 0.8, ui: 0.6, ...settings };
    this.musicVoices = []; this.voices = new Set(); this.duckUntil = 0; this.destroyed = false;
  }
  async unlock() {
    if (this.destroyed || !this.AudioContext) return false;
    try {
      if (!this.context) {
        const c = this.context = new this.AudioContext();
        this.master = c.createGain(); this.limiter = c.createDynamicsCompressor();
        this.limiter.threshold.value = -6; this.limiter.knee.value = 3; this.limiter.ratio.value = 20;
        this.limiter.attack.value = 0.003; this.limiter.release.value = 0.1;
        this.master.connect(this.limiter); this.limiter.connect(c.destination);
        this.channels = {};
        for (const name of ["music", "sfx", "ui"]) { this.channels[name] = c.createGain(); this.channels[name].connect(this.master); }
        this.reverb = c.createConvolver(); this.wet = c.createGain(); this.wet.gain.value = 0.12;
        const length = Math.floor(c.sampleRate * 1.4), impulse = c.createBuffer(2, length, c.sampleRate);
        for (let channel = 0; channel < 2; channel++) {
          const samples = impulse.getChannelData(channel);
          for (let i = 0; i < length; i++) samples[i] = (Math.random() * 2 - 1) * (1 - i / length) ** 3;
        }
        this.reverb.buffer = impulse; this.reverb.connect(this.wet); this.wet.connect(this.master);
        for (const channel of Object.values(this.channels)) channel.connect(this.reverb);
        this.setVolumes(this.volumes);
      }
      if (this.context.state === "suspended") await this.context.resume();
      return this.context.state === "running";
    } catch { return false; }
  }
  setVolumes(settings = {}) {
    for (const name of ["master", "music", "sfx", "ui"]) {
      if (settings[name] !== undefined) this.volumes[name] = clampVolume(settings[name]);
      const gain = name === "master" ? this.master : this.channels?.[name];
      gain?.gain.setTargetAtTime(clampVolume(this.volumes[name]), this.context.currentTime, 0.03);
    }
  }
  playTone({ frequency = 440, duration = 0.15, type = "sine", channel = "sfx", volume = 0.2, position, slide = 1 } = {}) {
    const c = this.context;
    if (!c || c.state !== "running" || this.destroyed) return null;
    const oscillator = c.createOscillator(), envelope = c.createGain(), now = c.currentTime;
    oscillator.type = ["sine", "square", "triangle", "sawtooth"].includes(type) ? type : "sine";
    oscillator.frequency.setValueAtTime(Math.max(20, frequency), now);
    const length = Math.max(0.025, duration);
    oscillator.frequency.exponentialRampToValueAtTime(Math.max(20, frequency * slide), now + length);
    envelope.gain.setValueAtTime(0, now); envelope.gain.linearRampToValueAtTime(clampVolume(volume), now + 0.01);
    envelope.gain.exponentialRampToValueAtTime(0.0001, now + length);
    oscillator.connect(envelope);
    let output = envelope, panner = null;
    if (position) {
      panner = c.createPanner(); panner.panningModel = "HRTF"; panner.distanceModel = "inverse"; panner.refDistance = 5;
      if (panner.positionX) {
        panner.positionX.value = position.x || 0; panner.positionY.value = position.y || 0; panner.positionZ.value = position.z || 0;
      } else panner.setPosition(position.x || 0, position.y || 0, position.z || 0);
      envelope.connect(panner); output = panner;
    }
    output.connect(this.channels[channel] || this.channels.sfx);
    const voice = { oscillator, envelope, panner };
    this.voices.add(voice);
    oscillator.onended = () => { oscillator.disconnect(); envelope.disconnect(); panner?.disconnect(); this.voices.delete(voice); };
    oscillator.start(now); oscillator.stop(now + length + 0.02);
    if (channel !== "music") this.duck(Math.min(length + 0.15, 0.8));
    return voice;
  }
  playProfile(profile = "arcade", event = "action", options = {}) {
    const p = typeof profile === "object" ? profile : SOUND_PROFILES[profile] || SOUND_PROFILES.arcade;
    const ratios = { action: 1, hit: 0.5, win: 2, lose: 0.25, collect: 1.5, ui: 1.25 };
    return this.playTone({ frequency: (p.base || 220) * (ratios[event] || 1), type: p.type || "sine",
      slide: event === "lose" || event === "hit" ? 0.4 : 1.5, ...options });
  }
  tone(frequency = 440, duration = 0.15, bus = "sfx", position) {
    return this.playTone({ frequency, duration, channel: bus, position });
  }
  duck(duration = 0.3) {
    if (!this.context) return;
    const now = this.context.currentTime;
    this.duckUntil = Math.max(this.duckUntil, now + duration);
    this.channels.music.gain.setTargetAtTime(clampVolume(this.volumes.music) * 0.35, now, 0.025);
  }
  setMusic(profile = "arcade", fade = 0.5) {
    const c = this.context;
    if (!c || this.destroyed) return;
    const now = c.currentTime, duration = Math.max(0.02, fade);
    for (const voice of this.musicVoices) {
      voice.envelope.gain.cancelScheduledValues(now);
      voice.envelope.gain.setTargetAtTime(0, now, duration / 4);
      try { voice.oscillator.stop(now + duration); } catch { /* Already stopped. */ }
    }
    this.musicVoices = [];
    if (profile === null) return;
    const p = typeof profile === "object" ? profile : SOUND_PROFILES[profile] || SOUND_PROFILES.arcade;
    for (const ratio of [1, 1.5, 2]) {
      const oscillator = c.createOscillator(), envelope = c.createGain();
      oscillator.type = p.type || "sine"; oscillator.frequency.value = (p.base || 220) * ratio / 2;
      envelope.gain.setValueAtTime(0, now); envelope.gain.linearRampToValueAtTime(0.035, now + duration);
      oscillator.connect(envelope); envelope.connect(this.channels.music); oscillator.start();
      const voice = { oscillator, envelope }; this.musicVoices.push(voice); this.voices.add(voice);
      oscillator.onended = () => { oscillator.disconnect(); envelope.disconnect(); this.voices.delete(voice); };
    }
  }
  update() {
    const c = this.context;
    if (!c) return;
    if (this.duckUntil && c.currentTime >= this.duckUntil) {
      this.channels.music.gain.setTargetAtTime(clampVolume(this.volumes.music), c.currentTime, 0.15); this.duckUntil = 0;
    }
    if (!this.camera) return;
    const { position, forward, up } = this.camera.getListener(), listener = c.listener;
    if (listener.positionX) {
      for (const [prefix, vector] of [["position", position], ["forward", forward], ["up", up]]) {
        for (const [axis, key] of [["X", "x"], ["Y", "y"], ["Z", "z"]]) listener[prefix + axis].setTargetAtTime(vector[key], c.currentTime, 0.02);
      }
    } else {
      listener.setPosition(position.x, position.y, position.z);
      listener.setOrientation(forward.x, forward.y, forward.z, up.x, up.y, up.z);
    }
  }
  destroy() {
    this.destroyed = true;
    for (const voice of this.voices) { try { voice.oscillator.stop(); } catch { /* Already stopped. */ } voice.oscillator.disconnect(); voice.envelope.disconnect(); voice.panner?.disconnect(); }
    this.voices.clear(); this.musicVoices = [];
    const closing = this.context?.close();
    closing?.catch?.(() => {});
  }
}
