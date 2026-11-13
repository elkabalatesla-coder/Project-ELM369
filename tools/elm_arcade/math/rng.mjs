/** Integer-card convention: rank = card % 13 + 2; suit = floor(card / 13). */
export function deck() {
  return Array.from({ length: 52 }, (_, i) => i);
}

function checkMax(max) {
  if (!Number.isSafeInteger(max) || max < 1 || max > 0x100000000) {
    throw new RangeError('max must be an integer from 1 through 2^32');
  }
}

/** Cryptographically secure, unbiased integers; deliberately no insecure fallback. */
export class SecureRNG {
  constructor(crypto = globalThis.crypto) {
    if (!crypto || typeof crypto.getRandomValues !== 'function') {
      throw new Error('Web Crypto getRandomValues is required');
    }
    this.crypto = crypto;
    this.buffer = new Uint32Array(1);
  }

  int(max) {
    checkMax(max);
    const limit = Math.floor(0x100000000 / max) * max;
    let value;
    do {
      this.crypto.getRandomValues(this.buffer);
      value = this.buffer[0];
    } while (value >= limit);
    return value % max;
  }
}

/** Reproducible Mulberry32 generator, for simulations only, NOT real-money play. */
export class SeededRNG {
  constructor(seed = 0) {
    if (!Number.isSafeInteger(seed)) throw new TypeError('seed must be a safe integer');
    this.state = seed >>> 0;
  }

  uint32() {
    let t = this.state = (this.state + 0x6d2b79f5) >>> 0;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return (t ^ (t >>> 14)) >>> 0;
  }

  int(max) {
    checkMax(max);
    const limit = Math.floor(0x100000000 / max) * max;
    let value;
    do { value = this.uint32(); } while (value >= limit);
    return value % max;
  }
}

/** Fisher–Yates on a copy; the input is never mutated. */
export function shuffle(items, rng = new SecureRNG()) {
  if (!Array.isArray(items)) throw new TypeError('items must be an array');
  if (!rng || typeof rng.int !== 'function') throw new TypeError('rng.int is required');
  const result = items.slice();
  for (let i = result.length - 1; i > 0; i--) {
    const j = rng.int(i + 1);
    if (!Number.isInteger(j) || j < 0 || j > i) throw new RangeError('rng returned an invalid index');
    [result[i], result[j]] = [result[j], result[i]];
  }
  return result;
}
