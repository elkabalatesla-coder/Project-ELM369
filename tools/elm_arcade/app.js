(function () {
  "use strict";
  const E = window.ELMArcade;
  const $ = id => document.getElementById(id);
  const canvas = $("screen"), ctx = canvas.getContext("2d");
  const casino = new E.Casino();
  const games = E.listGames();
  const casinoNames = {
    "poker-jacks": "Video Poker · Jacks or Better",
    "poker-tens": "Video Poker · Tens or Better",
    "poker-bonus": "Video Poker · Bonus",
    blackjack: "Blackjack", slots: "Six-symbol Slots",
    roulette: "European Roulette", dice: "High / Low Dice"
  };
  function option(select, value, title) {
    const node = document.createElement("option");
    node.value = value; node.textContent = title; select.append(node);
  }
  games.forEach(g => option($("game"), g.id, g.title));
  Object.entries(casinoNames).forEach(([id, name]) => option($("game"), id, name));

  let selected = games[0].id, state = null, running = false, paused = false;
  let held = [false, false, false, false, false], casinoArt = [];
  const input = { x: 0.5, y: 0.5, dx: 0, dy: 0 };
  const keys = new Set();
  let accumulator = 0, previous = null, lastScore = "";
  $("motion").checked = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const isAction = () => games.some(g => g.id === selected);
  const message = text => { $("message").textContent = text; };

  class AudioBus {
    constructor() { this.context = null; this.enabled = false; this.voices = 0; }
    async toggle() {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (!AudioContext) { message("Audio is unavailable; games remain playable."); return; }
      try {
        if (!this.context) {
          this.context = new AudioContext();
          this.master = this.context.createGain();
          const limiter = this.context.createDynamicsCompressor();
          limiter.threshold.value = -18; limiter.knee.value = 12;
          limiter.ratio.value = 12; limiter.attack.value = 0.003; limiter.release.value = 0.15;
          this.master.gain.value = Number($("volume").value);
          this.master.connect(limiter); limiter.connect(this.context.destination);
        }
        this.enabled = !this.enabled;
        if (this.enabled && !document.hidden) await this.context.resume();
        else await this.context.suspend();
        $("sound").textContent = this.enabled ? "Mute audio" : "Enable audio";
        $("sound").setAttribute("aria-pressed", String(this.enabled));
        if (this.enabled) this.play("score", 0.5);
      } catch (_) {
        this.enabled = false;
        $("sound").textContent = "Enable audio";
        $("sound").setAttribute("aria-pressed", "false");
        message("Audio could not start; games remain playable.");
      }
    }
    play(event, position) {
      if (!this.enabled || this.context.state !== "running" || this.voices >= 8) return;
      const t = this.context.currentTime;
      const osc = this.context.createOscillator(), envelope = this.context.createGain();
      const pan = this.context.createStereoPanner();
      pan.pan.value = Math.max(-1, Math.min(1, position * 2 - 1));
      osc.type = event === "lose" ? "triangle" : "sine";
      osc.frequency.setValueAtTime(event === "score" ? 660 : event === "lose" ? 160 : 330, t);
      osc.frequency.exponentialRampToValueAtTime(event === "lose" ? 60 : 220, t + 0.18);
      envelope.gain.setValueAtTime(0.001, t);
      envelope.gain.exponentialRampToValueAtTime(0.25, t + 0.008);
      envelope.gain.exponentialRampToValueAtTime(0.001, t + 0.22);
      osc.connect(envelope); envelope.connect(pan); pan.connect(this.master);
      this.voices++;
      osc.onended = () => { this.voices--; osc.disconnect(); envelope.disconnect(); pan.disconnect(); };
      osc.start(t); osc.stop(t + 0.24);
    }
  }
  const audio = new AudioBus();
  $("sound").onclick = () => audio.toggle();
  $("volume").oninput = () => {
    if (audio.context) audio.master.gain.setTargetAtTime(Number($("volume").value), audio.context.currentTime, 0.02);
  };

  function pause(value) {
    paused = value; accumulator = 0; keys.clear();
    $("pause").textContent = paused ? "Resume" : "Pause";
    $("pause").setAttribute("aria-pressed", String(paused));
    $("overlay").textContent = paused ? "Paused" : "";
  }
  $("restart").onclick = () => {
    state = E.createArcade(selected); E.updateArcade(state, input, 0);
    running = true; pause(false); canvas.focus(); message("");
  };
  $("pause").onclick = () => { if (running) pause(!paused); };
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) {
      if (running && !paused) pause(true);
      if (audio.context) audio.context.suspend().catch(() => {});
    } else if (audio.enabled && audio.context) audio.context.resume().catch(() => {});
    previous = null;
  });
  window.addEventListener("blur", () => { if (running && !paused) pause(true); keys.clear(); });
  canvas.addEventListener("blur", () => keys.clear());

  const directions = {
    ArrowUp: [0, -1], w: [0, -1], ArrowDown: [0, 1], s: [0, 1],
    ArrowLeft: [-1, 0], a: [-1, 0], ArrowRight: [1, 0], d: [1, 0]
  };
  canvas.addEventListener("keydown", event => {
    const key = event.key.length === 1 ? event.key.toLowerCase() : event.key;
    if (directions[key]) {
      event.preventDefault(); keys.add(key);
      [input.dx, input.dy] = directions[key];
    }
    if (key === "p" && !event.repeat && running) { event.preventDefault(); pause(!paused); }
  });
  canvas.addEventListener("keyup", event => keys.delete(event.key.length === 1 ? event.key.toLowerCase() : event.key));
  canvas.addEventListener("pointerdown", event => {
    canvas.focus(); canvas.setPointerCapture(event.pointerId); pointer(event);
  });
  canvas.addEventListener("pointermove", pointer);
  function pointer(event) {
    const box = canvas.getBoundingClientRect();
    input.x = Math.max(0, Math.min(1, (event.clientX - box.left) / box.width));
    input.y = Math.max(0, Math.min(1, (event.clientY - box.top) / box.height));
  }
  const touchDirections = { up: [0, -1], down: [0, 1], left: [-1, 0], right: [1, 0] };
  document.querySelectorAll("[data-direction]").forEach(button => {
    const move = () => {
      [input.dx, input.dy] = touchDirections[button.dataset.direction];
      input.x = Math.max(0, Math.min(1, input.x + input.dx * 0.1));
      input.y = Math.max(0, Math.min(1, input.y + input.dy * 0.1));
    };
    button.onclick = move;
  });

  function showCards(cards, canHold) {
    $("cards").replaceChildren();
    cards.forEach((card, i) => {
      const node = document.createElement(canHold ? "button" : "span");
      node.className = "card";
      node.textContent = card === null ? "Hidden" : E.cardLabel(card);
      if (canHold) {
        node.type = "button";
        node.setAttribute("aria-pressed", String(held[i]));
        node.setAttribute("aria-label", E.cardLabel(card) + (held[i] ? ", held" : ", not held"));
        node.onclick = () => { held[i] = !held[i]; showCards(cards, true); $("cards").children[i].focus(); };
      }
      $("cards").append(node);
    });
  }
  function syncRound() {
    const active = casino.round;
    const poker = active && active.kind === "poker";
    const blackjack = active && active.kind === "blackjack";
    $("deal").textContent = poker ? "Draw / settle" : selected.startsWith("poker") || selected === "blackjack" ? "Deal" : "Play";
    $("deal").disabled = Boolean(blackjack);
    $("hit").hidden = $("stand").hidden = !blackjack;
    $("bet").disabled = $("choice").disabled = Boolean(active);
    $("balance").textContent = casino.credits + " demo credits";
    $("game").disabled = Boolean(active);
  }
  function resultText(result, prefix) {
    $("result").textContent = prefix + (result.payout === undefined ? "" :
      " · Gross return " + result.payout + " credits (includes returned bet).");
    if (result.payout !== undefined) audio.play(result.payout > 0 ? "score" : "lose", 0.5);
  }
  function showBlackjack(result) {
    const dealer = result.done ? result.dealer : [...result.dealer, null];
    showCards([...result.player, ...dealer], false);
    resultText(result, "Player: " + result.player.map(E.cardLabel).join(" ") +
      " (" + E.blackjackTotal(result.player) + "). Dealer: " +
      result.dealer.map(E.cardLabel).join(" ") + (result.done ? " (" + E.blackjackTotal(result.dealer) + ")." : " + hidden card. Hit or stand."));
    casinoArt = result.player.map(c => c % 4);
  }
  function act(action) {
    try {
      message("");
      const stake = Number($("bet").value);
      let result;
      if (action === "hit" || action === "stand") showBlackjack(casino.blackjack(action));
      else if (selected.startsWith("poker")) {
        if (casino.round) {
          result = casino.drawPoker(held); showCards(result.cards, false);
          resultText(result, result.category + " · " + result.multiplier + "×");
          casinoArt = result.cards.map(c => c % 4);
        } else {
          held = [false, false, false, false, false];
          const cards = casino.dealPoker(stake, selected.slice(6));
          showCards(cards, true);
          $("result").textContent = "Select cards to hold, then draw once.";
          casinoArt = cards.map(c => c % 4);
        }
      } else if (selected === "blackjack") showBlackjack(casino.dealBlackjack(stake));
      else if (selected === "slots") {
        result = casino.slots(stake);
        const symbols = ["Droplet", "Prism", "Wave", "Star", "Moon", "ELM"];
        resultText(result, result.reels.map(r => symbols[r]).join(" · ") + " · " + result.multiplier + "×");
        casinoArt = result.reels;
      } else if (selected === "roulette") {
        const choice = $("choice").value;
        result = casino.roulette(stake, /^\d+$/.test(choice) ? Number(choice) : choice);
        resultText(result, "Pocket " + result.number + " · " + result.multiplier + "×");
        casinoArt = [result.number % 4];
      } else {
        result = casino.dice(stake, $("choice").value);
        resultText(result, "Dice " + result.dice.join(" + ") + " = " + result.sum + " · " + result.multiplier + "×");
        casinoArt = result.dice;
      }
      syncRound();
    } catch (error) { message(error.message); }
  }
  $("deal").onclick = () => act("deal");
  $("hit").onclick = () => act("hit");
  $("stand").onclick = () => act("stand");

  const instructions = {
    pong: "Move vertically with pointer, touch, ↑/↓ or W/S. Return the ball; three misses end the game.",
    breakout: "Move horizontally with pointer, touch, ←/→ or A/D. Clear bricks; three misses end the game.",
    snake: "Use arrows, WASD, or directional buttons. Eat pink droplets; avoid walls and yourself.",
    dodge: "Move horizontally with pointer, touch, ←/→ or A/D. Dodge meteors; three hits end the game."
  };
  function chooseGame() {
    if (casino.round) { $("game").value = selected; message("Finish the current hand first."); return; }
    selected = $("game").value; state = null; running = false; pause(false);
    input.x = input.y = 0.5; input.dx = input.dy = 0;
    $("cards").replaceChildren(); $("choice").replaceChildren(); casinoArt = [];
    $("result").textContent = ""; message(""); lastScore = ""; $("score").textContent = "Score 0";
    const action = isAction();
    $("action-panel").hidden = $("directions").hidden = !action;
    $("casino-panel").hidden = action;
    $("overlay").textContent = action ? "Press Start to play" : casinoNames[selected];
    $("instructions").textContent = (instructions[selected] || "") + " Focus the playfield for keyboard controls. P pauses. Levels increase with score.";
    $("choice-label").hidden = selected !== "roulette" && selected !== "dice";
    if (selected.startsWith("poker")) {
      const paytable = E.PAYTABLES[selected.slice(6)];
      $("rules").textContent = "Five cards from one shuffled 52-card deck, one draw, no wild cards. Gross returns per credit: " +
        Object.entries(paytable).map(([name, n]) => name + " " + n + "×").join("; ") +
        ". Royal flush always 250×; no five-credit bonus. Tens variant pays pairs of tens or higher; others pay jacks or higher.";
    } else if (selected === "roulette") {
      option($("choice"), "red", "Red"); option($("choice"), "black", "Black");
      for (let n = 0; n <= 36; n++) option($("choice"), String(n), "Pocket " + n);
      $("rules").textContent = "Single-zero wheel, 37 equally likely pockets. Red/black gross return 2×; straight pocket 36×. Zero loses color bets. Theoretical return: 36/37 (97.30%).";
    } else if (selected === "slots") {
      $("rules").textContent = "Three independent reels, six equally likely symbols each. Three ELM: 100×; any other triple: 10×; otherwise matching first two reels: 2×. Highest award only. Theoretical return: 210/216 (97.22%).";
    } else if (selected === "blackjack") {
      $("rules").textContent = "One shuffled deck per hand. Dealer stands on all 17s; ace counts 1 or 11. Dealer checks natural immediately. Natural pays 3:2 profit; ordinary win 1:1; tie returns bet. Even bets only. Hit/stand only: no split, double, surrender or insurance. Dealer hole card stays hidden until settlement.";
    } else if (selected === "dice") {
      option($("choice"), "low", "Low (2–6)"); option($("choice"), "high", "High (8–12)");
      $("rules").textContent = "Two independent fair six-sided dice. Low wins 2–6; high wins 8–12; 7 loses. Gross win 2×. Theoretical return: 30/36 (83.33%).";
    }
    syncRound();
  }
  $("game").onchange = chooseGame;
  chooseGame();

  function background(time) {
    const reduced = $("motion").checked;
    const angle = reduced || $("camera").value === "still" ? 0 : time * 0.00025;
    const mode = $("camera").value;
    ctx.fillStyle = "#090d21"; ctx.fillRect(0, 0, 960, 600);
    for (let i = 0; i < 24; i++) {
      const phase = i * 2.399;
      const x = 480 + Math.sin(phase + angle) * (180 + i * 10);
      const y = 300 + Math.cos(phase * 1.3 + angle) * 220;
      const radius = 40 + 12 * Math.sin(phase + angle);
      const gradient = ctx.createRadialGradient(x, y, 1, x, y, radius);
      gradient.addColorStop(0, E.PALETTE[i % 4] + "30");
      gradient.addColorStop(1, E.PALETTE[i % 4] + "00");
      ctx.fillStyle = gradient; ctx.fillRect(x - radius, y - radius, radius * 2, radius * 2);
    }
    const dimensions = mode === "4d" ? 4 : 3;
    const points = Array.from({ length: 2 ** dimensions }, (_, i) =>
      E.project(Array.from({ length: 4 }, (_, d) => d < dimensions ? ((i >> d) & 1 ? 1 : -1) * 0.85 : 0), angle, mode));
    ctx.strokeStyle = "#8b63df55"; ctx.lineWidth = 1.5;
    for (let i = 0; i < points.length; i++) for (let d = 0; d < dimensions; d++) {
      const j = i ^ (1 << d);
      if (j <= i) continue;
      ctx.beginPath(); ctx.moveTo(480 + points[i].x * 260, 300 + points[i].y * 220);
      ctx.lineTo(480 + points[j].x * 260, 300 + points[j].y * 220); ctx.stroke();
    }
  }
  function drawShape(shape) {
    const color = E.PALETTE[shape.color % 4];
    ctx.fillStyle = color;
    if (shape.type === "orb") {
      const x = shape.x * 960, y = shape.y * 600, r = shape.r * 600;
      const gradient = ctx.createRadialGradient(x - r * 0.3, y - r * 0.3, r * 0.1, x, y, r);
      gradient.addColorStop(0, "#ffffff"); gradient.addColorStop(0.3, color); gradient.addColorStop(1, color + "66");
      ctx.fillStyle = gradient; ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.fill();
    } else {
      ctx.fillRect(shape.x * 960, shape.y * 600, shape.w * 960, shape.h * 600);
      ctx.fillStyle = "#ffffff66"; ctx.fillRect(shape.x * 960, shape.y * 600, shape.w * 960, 2);
    }
  }
  function frame(time) {
    const dt = previous === null ? 0 : Math.min((time - previous) / 1000, 0.1);
    previous = time;
    if (running && !paused && state && !state.over) {
      accumulator += dt;
      const step = 1 / 120;
      while (accumulator >= step) {
        for (const key of keys) {
          const [dx, dy] = directions[key];
          input.x = Math.max(0, Math.min(1, input.x + dx * step * 0.9));
          input.y = Math.max(0, Math.min(1, input.y + dy * step * 0.9));
        }
        E.updateArcade(state, input, step);
        state.events.forEach(event => audio.play(event, state.x ?? 0.5));
        accumulator -= step;
        if (state.over) { running = false; $("overlay").textContent = "Game over · Restart to try again"; break; }
      }
      const score = "Score " + state.score + " · Level " + state.level + (state.lives === undefined ? "" : " · Lives " + Math.max(0, state.lives));
      if (score !== lastScore) { $("score").textContent = score; lastScore = score; }
    }
    background(time);
    if (state) (state.shapes || []).forEach(drawShape);
    else casinoArt.forEach((color, i) => drawShape({ type: "orb", x: (i + 1) / (casinoArt.length + 1), y: 0.7, r: 0.055, color }));
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
})();
