(function (root, factory) {
  "use strict";
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.ELMArcade = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  const VERSION = 1;
  const PALETTE = ["#00D4FF", "#8B00FF", "#FF006E", "#00FF88"];
  const clamp = (x, lo, hi) => Math.max(lo, Math.min(hi, x));

  // Rejection sampling avoids modulo bias; no real-money suitability is implied.
  function randomInt(limit) {
    if (!Number.isSafeInteger(limit) || limit < 1 || limit > 0x100000000) {
      throw new RangeError("Invalid random bound");
    }
    const cutoff = Math.floor(0x100000000 / limit) * limit;
    const word = new Uint32Array(1);
    do { globalThis.crypto.getRandomValues(word); } while (word[0] >= cutoff);
    return word[0] % limit;
  }

  function shuffledDeck(rng = randomInt) {
    const deck = Array.from({ length: 52 }, (_, i) => i);
    for (let i = deck.length - 1; i > 0; i--) {
      const j = rng(i + 1);
      [deck[i], deck[j]] = [deck[j], deck[i]];
    }
    return deck;
  }

  function cardLabel(card) {
    return ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"][card % 13] +
      ["♠", "♥", "♦", "♣"][Math.floor(card / 13)];
  }

  const PAYTABLES = Object.freeze({
    jacks: Object.freeze({ royal: 250, straightFlush: 50, four: 25, fullHouse: 9,
      flush: 6, straight: 4, three: 3, twoPair: 2, highPair: 1, nothing: 0 }),
    tens: Object.freeze({ royal: 250, straightFlush: 50, four: 25, fullHouse: 6,
      flush: 5, straight: 4, three: 3, twoPair: 2, highPair: 1, nothing: 0 }),
    bonus: Object.freeze({ royal: 250, straightFlush: 50, fourAces: 80, fourLow: 40,
      four: 25, fullHouse: 8, flush: 5, straight: 4, three: 3, twoPair: 2,
      highPair: 1, nothing: 0 })
  });

  function evaluatePoker(cards, variant = "jacks") {
    if (!Object.hasOwn(PAYTABLES, variant)) throw new Error("Unknown poker variant");
    if (!Array.isArray(cards) || cards.length !== 5 || new Set(cards).size !== 5 ||
        cards.some(c => !Number.isInteger(c) || c < 0 || c >= 52)) {
      throw new Error("A poker hand requires five distinct cards");
    }
    const ranks = cards.map(c => c % 13 + 2).sort((a, b) => a - b);
    const counts = new Map();
    for (const rank of ranks) counts.set(rank, (counts.get(rank) || 0) + 1);
    const groups = [...counts.values()].sort((a, b) => b - a);
    const flush = cards.every(c => Math.floor(c / 13) === Math.floor(cards[0] / 13));
    const straight = counts.size === 5 &&
      (ranks[4] - ranks[0] === 4 || ranks.join(",") === "2,3,4,5,14");
    const quad = [...counts].find(([, n]) => n === 4);
    let category = "nothing";
    if (straight && flush) category = ranks[0] === 10 ? "royal" : "straightFlush";
    else if (quad) {
      category = variant === "bonus" && quad[0] === 14 ? "fourAces" :
        variant === "bonus" && quad[0] <= 4 ? "fourLow" : "four";
    } else if (groups[0] === 3 && groups[1] === 2) category = "fullHouse";
    else if (flush) category = "flush";
    else if (straight) category = "straight";
    else if (groups[0] === 3) category = "three";
    else if (groups[0] === 2 && groups[1] === 2) category = "twoPair";
    else if ([...counts].some(([r, n]) => n === 2 && r >= (variant === "tens" ? 10 : 11))) {
      category = "highPair";
    }
    return { category, multiplier: PAYTABLES[variant][category] };
  }

  function blackjackTotal(cards) {
    let total = 0, aces = 0;
    for (const card of cards) {
      const rank = card % 13 + 2;
      total += rank === 14 ? 11 : Math.min(rank, 10);
      if (rank === 14) aces++;
    }
    while (total > 21 && aces-- > 0) total -= 10;
    return total;
  }

  const RED = new Set([1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]);
  function rouletteMultiplier(number, choice) {
    if (!Number.isInteger(number) || number < 0 || number > 36) throw new Error("Invalid pocket");
    if (Number.isInteger(choice) && choice >= 0 && choice <= 36) return number === choice ? 36 : 0;
    if (choice !== "red" && choice !== "black") throw new Error("Choose red, black, or a pocket 0–36");
    return number !== 0 && (RED.has(number) === (choice === "red")) ? 2 : 0;
  }

  class Casino {
    constructor(rng = randomInt) {
      this.rng = rng;
      this.credits = 1000;
      this.round = null;
    }
    wager(stake) {
      if (this.round) throw new Error("Finish the current hand first");
      if (!Number.isInteger(stake) || stake < 1 || stake > 100 || stake > this.credits) {
        throw new Error("Bet must be 1–100 whole credits within your balance");
      }
      this.credits -= stake;
    }
    settle(round, multiplier, details) {
      if (this.round !== round) throw new Error("This hand is already settled");
      const payout = round.stake * multiplier;
      this.credits += payout;
      this.round = null;
      return { ...details, payout, credits: this.credits };
    }
    dealPoker(stake, variant) {
      if (!Object.hasOwn(PAYTABLES, variant)) throw new Error("Unknown poker variant");
      const deck = shuffledDeck(this.rng);
      this.wager(stake);
      this.round = { kind: "poker", stake, variant, deck, cards: deck.splice(0, 5) };
      return this.round.cards.slice();
    }
    drawPoker(held) {
      const round = this.round;
      if (!round || round.kind !== "poker") throw new Error("Deal a poker hand first");
      if (!Array.isArray(held) || held.length !== 5 || held.some(h => typeof h !== "boolean")) {
        throw new Error("Supply five hold decisions");
      }
      round.cards = round.cards.map((c, i) => held[i] ? c : round.deck.pop());
      const result = evaluatePoker(round.cards, round.variant);
      return this.settle(round, result.multiplier, { ...result, cards: round.cards.slice() });
    }
    slots(stake) {
      const reels = Array.from({ length: 3 }, () => this.rng(6));
      this.wager(stake);
      const multiplier = reels.every(r => r === reels[0]) ? (reels[0] === 5 ? 100 : 10) :
        reels[0] === reels[1] ? 2 : 0;
      this.round = { stake };
      return this.settle(this.round, multiplier, { reels, multiplier });
    }
    roulette(stake, choice) {
      rouletteMultiplier(0, choice);
      const number = this.rng(37);
      const multiplier = rouletteMultiplier(number, choice);
      this.wager(stake);
      this.round = { stake };
      return this.settle(this.round, multiplier, { number, multiplier });
    }
    dice(stake, choice) {
      if (choice !== "low" && choice !== "high") throw new Error("Choose low or high");
      const dice = [this.rng(6) + 1, this.rng(6) + 1];
      const sum = dice[0] + dice[1];
      const multiplier = (choice === "low" ? sum < 7 : sum > 7) ? 2 : 0;
      this.wager(stake);
      this.round = { stake };
      return this.settle(this.round, multiplier, { dice, sum, multiplier });
    }
    dealBlackjack(stake) {
      if (!Number.isInteger(stake) || stake % 2) throw new Error("Blackjack bets must be even for 3:2 payouts");
      const deck = shuffledDeck(this.rng);
      this.wager(stake);
      const round = { kind: "blackjack", stake, deck, player: deck.splice(0, 2), dealer: deck.splice(0, 2) };
      this.round = round;
      const playerNatural = blackjackTotal(round.player) === 21;
      const dealerNatural = blackjackTotal(round.dealer) === 21;
      if (playerNatural || dealerNatural) {
        return this.settle(round, playerNatural ? (dealerNatural ? 1 : 2.5) : 0,
          { player: round.player.slice(), dealer: round.dealer.slice(), done: true });
      }
      return this.blackjackView();
    }
    blackjackView() {
      const r = this.round;
      return { player: r.player.slice(), dealer: [r.dealer[0]], done: false };
    }
    blackjack(action) {
      const r = this.round;
      if (!r || r.kind !== "blackjack") throw new Error("Deal a blackjack hand first");
      if (action !== "hit" && action !== "stand") throw new Error("Choose hit or stand");
      if (action === "hit") r.player.push(r.deck.pop());
      const player = blackjackTotal(r.player);
      if (action === "hit" && player < 21) return this.blackjackView();
      if (player <= 21) {
        while (blackjackTotal(r.dealer) < 17) r.dealer.push(r.deck.pop());
      }
      const dealer = blackjackTotal(r.dealer);
      const multiplier = player > 21 ? 0 : dealer > 21 || player > dealer ? 2 : player === dealer ? 1 : 0;
      return this.settle(r, multiplier, { player: r.player.slice(), dealer: r.dealer.slice(), done: true });
    }
  }

  const registry = new Map();
  function registerGame(spec) {
    if (!spec || !/^[a-z][a-z0-9-]*$/.test(spec.id) || registry.has(spec.id) ||
        spec.version !== VERSION || typeof spec.title !== "string" ||
        typeof spec.create !== "function" || typeof spec.update !== "function") {
      throw new Error("A unique ID, title, compatible version, create and update are required");
    }
    registry.set(spec.id, Object.freeze({ ...spec }));
  }
  const listGames = () => [...registry.values()].map(({ id, title, version }) => ({ id, title, version }));

  function createArcade(id, rng = randomInt) {
    const spec = registry.get(id);
    if (!spec) throw new Error("Unknown arcade game");
    return { id, score: 0, level: 1, over: false, elapsed: 0, events: [], ...spec.create(rng) };
  }
  function updateArcade(state, input, dt, rng = randomInt) {
    if (!Number.isFinite(dt) || dt < 0 || dt > 0.05) throw new Error("Use a timestep of at most 50ms");
    state.events = [];
    if (state.over) return state;
    state.elapsed += dt;
    state.level = 1 + Math.floor(state.score / 100);
    registry.get(state.id).update(state, input, dt, rng);
    return state;
  }
  const rect = (x, y, w, h, color = 0) => ({ type: "rect", x, y, w, h, color });
  const orb = (x, y, r, color = 0) => ({ type: "orb", x, y, r, color });

  registerGame({
    id: "pong", title: "Liquid Rally", version: VERSION,
    create: () => ({ x: 0.5, y: 0.5, vx: 0.38, vy: 0.21, paddle: 0.5, ai: 0.5, lives: 3 }),
    update(s, input, dt) {
      s.paddle = clamp(input.y ?? s.paddle, 0.1, 0.9);
      s.ai = clamp(s.ai + clamp(s.y - s.ai, -dt * 0.45, dt * 0.45), 0.1, 0.9);
      s.x += s.vx * dt; s.y += s.vy * dt;
      if ((s.y < 0.025 && s.vy < 0) || (s.y > 0.975 && s.vy > 0)) {
        s.y = clamp(s.y, 0.025, 0.975); s.vy *= -1; s.events.push("bounce");
      }
      for (const [x, paddle, direction] of [[0.055, s.paddle, 1], [0.945, s.ai, -1]]) {
        if (Math.abs(s.x - x) < 0.025 && Math.abs(s.y - paddle) < 0.12 && s.vx * direction < 0) {
          s.x = x + direction * 0.026;
          s.vx = direction * Math.min(0.85, Math.abs(s.vx) + 0.02);
          s.vy = (s.y - paddle) * 3;
          if (direction === 1) s.score += 10;
          s.events.push("bounce");
        }
      }
      if (s.x < 0 || s.x > 1) {
        if (s.x < 0) s.lives--; else s.score += 50;
        s.x = s.y = 0.5; s.vx = 0.38; s.vy = 0.21;
        s.over = s.lives === 0; s.events.push(s.over ? "lose" : "score");
      }
      s.shapes = [rect(0.025, s.paddle - 0.1, 0.02, 0.2), rect(0.955, s.ai - 0.1, 0.02, 0.2, 2), orb(s.x, s.y, 0.02, 3)];
    }
  });

  registerGame({
    id: "breakout", title: "Prism Breaker", version: VERSION,
    create: () => ({ x: 0.5, y: 0.7, vx: 0.26, vy: -0.4, paddle: 0.5, lives: 3,
      bricks: Array.from({ length: 32 }, (_, i) => ({ x: 0.035 + (i % 8) * 0.12, y: 0.08 + Math.floor(i / 8) * 0.065, alive: true })) }),
    update(s, input, dt) {
      s.paddle = clamp(input.x ?? s.paddle, 0.1, 0.9);
      s.x += s.vx * dt; s.y += s.vy * dt;
      if ((s.x < 0.02 && s.vx < 0) || (s.x > 0.98 && s.vx > 0)) {
        s.x = clamp(s.x, 0.02, 0.98); s.vx *= -1;
      }
      if (s.y < 0.02 && s.vy < 0) { s.y = 0.02; s.vy *= -1; }
      if (s.vy > 0 && s.y >= 0.88 && s.y <= 0.93 && Math.abs(s.x - s.paddle) < 0.12) {
        s.y = 0.879; s.vy = -Math.min(0.75, Math.abs(s.vy) + 0.01);
        s.vx = (s.x - s.paddle) * 4; s.events.push("bounce");
      }
      for (const b of s.bricks) {
        if (b.alive && s.x + 0.015 > b.x && s.x - 0.015 < b.x + 0.105 &&
            s.y + 0.015 > b.y && s.y - 0.015 < b.y + 0.045) {
          b.alive = false; s.vy *= -1; s.score += 10; s.events.push("score"); break;
        }
      }
      if (s.y > 1) {
        s.lives--; s.x = 0.5; s.y = 0.7; s.vy = -0.4;
        s.over = s.lives === 0; s.events.push(s.over ? "lose" : "bounce");
      }
      if (s.bricks.every(b => !b.alive)) {
        s.score += 100; s.bricks.forEach(b => { b.alive = true; });
        s.x = 0.5; s.y = 0.7; s.vy = -0.4;
      }
      s.shapes = [...s.bricks.filter(b => b.alive).map(b => rect(b.x, b.y, 0.105, 0.045, Math.floor(b.y * 15) % 4)),
        rect(s.paddle - 0.1, 0.91, 0.2, 0.025), orb(s.x, s.y, 0.018, 3)];
    }
  });

  function spawnFood(body, rng) {
    const empty = [];
    for (let y = 0; y < 20; y++) for (let x = 0; x < 20; x++) {
      if (!body.some(p => p.x === x && p.y === y)) empty.push({ x, y });
    }
    return empty.length ? empty[rng(empty.length)] : null;
  }
  registerGame({
    id: "snake", title: "Neon Serpent", version: VERSION,
    create(rng) {
      const body = [{ x: 10, y: 10 }, { x: 9, y: 10 }, { x: 8, y: 10 }];
      return { body, dx: 1, dy: 0, nextDx: 1, nextDy: 0, clock: 0, food: spawnFood(body, rng) };
    },
    update(s, input, dt, rng) {
      if ((Math.abs(input.dx) + Math.abs(input.dy)) === 1 && input.dx * s.dx + input.dy * s.dy !== -1) {
        s.nextDx = input.dx; s.nextDy = input.dy;
      }
      s.clock += dt;
      const period = Math.max(0.07, 0.17 - s.level * 0.008);
      if (s.clock >= period) {
        s.clock -= period; s.dx = s.nextDx; s.dy = s.nextDy;
        const head = { x: s.body[0].x + s.dx, y: s.body[0].y + s.dy };
        const eats = s.food && head.x === s.food.x && head.y === s.food.y;
        const collisionBody = eats ? s.body : s.body.slice(0, -1);
        if (head.x < 0 || head.y < 0 || head.x >= 20 || head.y >= 20 ||
            collisionBody.some(p => p.x === head.x && p.y === head.y)) {
          s.over = true; s.events.push("lose");
        } else {
          s.body.unshift(head);
          if (eats) {
            s.score += 20; s.food = spawnFood(s.body, rng); s.events.push("score");
            if (!s.food) s.over = true;
          } else s.body.pop();
        }
      }
      s.shapes = s.body.map((p, i) => rect(p.x / 20, p.y / 20, 0.045, 0.045, i ? 0 : 3));
      if (s.food) s.shapes.push(orb((s.food.x + 0.5) / 20, (s.food.y + 0.5) / 20, 0.022, 2));
    }
  });

  registerGame({
    id: "dodge", title: "Meteor Drift", version: VERSION,
    create: () => ({ x: 0.5, rocks: [], spawn: 0, lives: 3 }),
    update(s, input, dt, rng) {
      s.x = clamp(input.x ?? s.x, 0.035, 0.965);
      s.spawn -= dt;
      if (s.spawn <= 0) {
        s.rocks.push({ x: (rng(900) + 50) / 1000, y: -0.05 });
        s.spawn = Math.max(0.18, 0.65 - s.level * 0.035);
      }
      for (const rock of s.rocks) {
        rock.y += (0.25 + Math.min(0.5, s.level * 0.03)) * dt;
        if (Math.hypot(rock.x - s.x, rock.y - 0.87) < 0.055) {
          rock.y = 2; s.lives--; s.events.push("bounce");
        } else if (rock.y > 1.05) { s.score += 10; s.events.push("score"); }
      }
      s.rocks = s.rocks.filter(r => r.y <= 1.05);
      s.over = s.lives <= 0;
      if (s.over) s.events.push("lose");
      s.shapes = [orb(s.x, 0.87, 0.03, 3), ...s.rocks.map(r => orb(r.x, r.y, 0.027, 2))];
    }
  });

  // Rotate XW before projecting 4D -> 3D, then orbit the 3D camera.
  function project(point, angle, mode) {
    let [x, y, z, w = 0] = point;
    if (mode === "4d") {
      const rotatedX = x * Math.cos(angle) - w * Math.sin(angle);
      w = x * Math.sin(angle) + w * Math.cos(angle);
      const scale4 = 3 / (3 - w);
      x = rotatedX * scale4; y *= scale4; z *= scale4;
    }
    const yaw = mode === "orbit" ? angle : 0.3;
    const rx = x * Math.cos(yaw) - z * Math.sin(yaw);
    z = x * Math.sin(yaw) + z * Math.cos(yaw);
    const scale = 3 / (4 + z);
    return { x: rx * scale, y: y * scale, scale };
  }

  return { VERSION, PALETTE, PAYTABLES, randomInt, shuffledDeck, cardLabel, evaluatePoker,
    blackjackTotal, rouletteMultiplier, Casino, registerGame, listGames, createArcade, updateArcade, project };
});
