import { SecureRNG, shuffle, deck } from '../math/rng.mjs';
import * as poker from '../math/poker.mjs';
import * as slots from '../math/slots.mjs';
import { kenoExpectedReturn } from '../math/casino.mjs';

const NOTICE = 'VIRTUAL CREDITS ONLY • No money, purchases, prizes or cash-out.';
const SUITS = ['♣', '♦', '♥', '♠'];
const START = 1000;
const KENO_PAYS = Object.freeze({ 3: 2, 4: 10, 5: 100 });
const KENO_RTP = kenoExpectedReturn(5, KENO_PAYS);
const copy = value => JSON.parse(JSON.stringify(value));
const bounded = (value, low, high) => Math.max(low, Math.min(high, value));
const integer = value => Number.isSafeInteger(value);
const slotReturns = new Map();
const variantKey = variant => ({
  'double-bonus': 'doubleBonus', 'double-double-bonus': 'doubleDoubleBonus',
  'all-american': 'allAmerican',
})[variant] || variant;

export function blackjackValue(cards) {
  let total = 0, aces = 0;
  for (const card of cards) {
    const rank = card % 13 + 2;
    total += rank === 14 ? 11 : Math.min(rank, 10);
    if (rank === 14) aces++;
  }
  while (total > 21 && aces) { total -= 10; aces--; }
  return total;
}

export function roulettePayout(number, selection, bet = 1) {
  return number === selection ? bet * 36 : 0;
}

function cardLabel(card) {
  if (card === 52) return 'JOKER';
  const rank = card % 13 + 2;
  return `${({ 11: 'J', 12: 'Q', 13: 'K', 14: 'A' })[rank] || rank}${SUITS[Math.floor(card / 13)]}`;
}

function metadata(variant) {
  variant = variantKey(variant);
  const variants = poker.pokerVariants || {};
  return Array.isArray(variants)
    ? variants.find(item => item.id === variant) || {}
    : variants[variant] || {};
}

function tableFor(variant) {
  variant = variantKey(variant);
  return poker.PAYTABLES?.[variant] || metadata(variant).paytable || {};
}

function category(hand, variant) {
  const result = poker.evaluate(hand, variant);
  return typeof result === 'string' ? result : result.category;
}

function pokerDescription(variant, ultimate = false) {
  if (ultimate) return 'RTP not calculated for house-rule future multipliers; base Jacks reference does NOT apply. A win makes the next hand ×2 at no extra stake; a loss resets ×1.';
  const info = metadata(variant);
  const rtp = info.theoreticalRTP ?? info.rtp ?? info.optimalRtp;
  return rtp == null
    ? `RTP not calculated; strategy dependent. ${info.assumptions || 'Gross paytable shown.'}`
    : `Reference RTP ${(rtp * 100).toFixed(4)}%. ${info.rtpProvenance || 'Theoretical math metadata.'} Listed gross multipliers apply at every stake here. ${info.rtpAssumptions || info.assumptions || 'Optimal strategy; long-run return, not a guarantee.'}`;
}

function createCasino(context, definition) {
  const rng = context.random || new SecureRNG();
  const hands = definition.hands || 1;
  const paylines = definition.kind === 'slots'
    ? (definition.reels === 5 ? slots.PAYLINES5 : slots.PAYLINES) : [];
  const units = definition.kind === 'slots' ? paylines.length : hands;
  const guideId = `${definition.id}-rules-guide`;
  if (definition.kind === 'slots' && !slotReturns.has(definition.reels)) {
    slotReturns.set(definition.reels, slots.exactSlotsRTP({
      reels: definition.reels === 3 ? slots.REELS3 : slots.REELS5, paylines,
    }));
  }
  let state = {
    version: 1, id: definition.id, credits: START, bet: 5, phase: 'ready',
    message: 'Choose a stake, then play.', lastGross: 0, rounds: 0,
    hand: [], dealer: [], held: [false, false, false, false, false],
    shoe: [], results: [], cursor: 0, selection: 0, grid: [],
    point: 0, wager: 0, nextMultiplier: 1, activeMultiplier: 1,
    picks: [1, 2, 3, 4, 5], drawn: [], dice: [],
  };
  let pointerDown = false;
  const snapshot = () => ({ ...copy(state), score: Math.max(0, state.credits - START) });
  const persist = () => context.save?.(snapshot());
  const totalBet = () => state.bet * units;
  const maxBet = () => Math.min(100, Math.floor(state.credits / units));
  const roundActive = () => state.phase === 'draw' || state.phase === 'blackjack' || state.point !== 0;
  const finishRound = (gross, message) => {
    if (!integer(gross) || gross < 0) throw new Error('Invalid gross payout');
    state.credits += gross;
    state.lastGross = gross;
    state.message = `${message} · Gross return ${gross}`;
    state.phase = 'ready';
    state.wager = 0;
    state.rounds++;
    if (context.audio?.tone) context.audio.tone(gross ? 660 : 180, 0.09);
    else context.audio?.playTone?.({ frequency: gross ? 660 : 180, duration: 0.09 });
    persist();
  };
  const debit = () => {
    const stake = totalBet();
    if (!integer(stake) || stake < 1 || stake > state.credits) {
      state.message = 'Insufficient credits. Lower stake or explicitly reset when bankrupt.';
      return false;
    }
    state.credits -= stake;
    state.wager = stake;
    state.lastGross = 0;
    return true;
  };
  const setBet = delta => {
    if (roundActive()) return;
    state.bet = bounded(state.bet + delta, 1, Math.max(1, maxBet()));
    persist();
  };
  const reset = () => {
    if (state.credits >= units || roundActive()) return;
    state.credits = START;
    state.bet = 5;
    state.nextMultiplier = 1;
    state.message = 'Bankrupt session explicitly reset to 1000 virtual credits.';
    persist();
  };
  const freshDeck = () => {
    const cards = deck();
    if (definition.variant === 'joker') cards.push(52);
    return shuffle(cards, rng);
  };
  function playPoker() {
    const variant = definition.variant || 'jacks';
    if (state.phase !== 'draw') {
      if (!debit()) return;
      state.shoe = freshDeck();
      state.hand = state.shoe.splice(0, 5);
      state.held = [false, false, false, false, false];
      state.results = [];
      state.activeMultiplier = definition.ultimate ? state.nextMultiplier : 1;
      state.nextMultiplier = 1;
      state.phase = 'draw';
      state.message = 'Select cards; ↑ or click toggles HOLD. Draw resolves all wagers.';
      persist();
      return;
    }
    let gross = 0;
    state.results = [];
    for (let index = 0; index < hands; index++) {
      const remaining = index ? shuffle([...state.shoe], rng) : [...state.shoe];
      const hand = state.hand.map((card, i) => state.held[i] ? card : remaining.shift());
      const result = category(hand, variant);
      const paid = poker.payout(hand, variant, state.bet) * state.activeMultiplier;
      gross += paid;
      state.results.push({ hand, category: result, gross: paid });
    }
    state.hand = state.results[0].hand;
    if (definition.ultimate) {
      state.nextMultiplier = gross > 0 ? 2 : 1;
    }
    finishRound(gross, state.results.map(result => result.category).join(' / '));
  }
  function settleBlackjack() {
    while (blackjackValue(state.dealer) < 17) state.dealer.push(state.shoe.shift());
    const player = blackjackValue(state.hand), dealer = blackjackValue(state.dealer);
    const gross = player > 21 ? 0 : dealer > 21 || player > dealer ? state.wager * 2 : player === dealer ? state.wager : 0;
    finishRound(gross, `Player ${player}, dealer ${dealer}`);
  }
  function playBlackjack() {
    if (state.phase !== 'blackjack') {
      if (!debit()) return;
      state.shoe = freshDeck();
      state.hand = state.shoe.splice(0, 2);
      state.dealer = state.shoe.splice(0, 2);
      state.phase = 'blackjack';
      state.selection = 0;
      const player = blackjackValue(state.hand), dealer = blackjackValue(state.dealer);
      if (player === 21 || dealer === 21) {
        // Even-money naturals keep integer credits; this is disclosed in the rules.
        finishRound(player === dealer ? state.wager : player === 21 ? state.wager * 2 : 0,
          `Natural check: player ${player}, dealer ${dealer}`);
      } else {
        state.message = '← HIT / → STAND, then confirm. Dealer stands on all 17.';
        persist();
      }
    } else if (state.selection === 0) {
      state.hand.push(state.shoe.shift());
      if (blackjackValue(state.hand) >= 21) settleBlackjack();
      else persist();
    } else settleBlackjack();
  }
  function playBaccarat() {
    if (!debit()) return;
    const cards = freshDeck();
    const score = hand => hand.reduce((sum, card) => {
      const rank = card % 13 + 2;
      return sum + (rank === 14 ? 1 : rank >= 10 ? 0 : rank);
    }, 0) % 10;
    state.hand = cards.splice(0, 2);
    state.dealer = cards.splice(0, 2);
    let player = score(state.hand), banker = score(state.dealer);
    if (player < 8 && banker < 8) {
      let third = null;
      if (player <= 5) {
        const card = cards.shift();
        state.hand.push(card);
        third = score([card]);
      }
      const drawBanker = third === null ? banker <= 5
        : banker <= 2 || (banker === 3 && third !== 8)
          || (banker === 4 && third >= 2 && third <= 7)
          || (banker === 5 && third >= 4 && third <= 7)
          || (banker === 6 && third >= 6 && third <= 7);
      if (drawBanker) state.dealer.push(cards.shift());
      player = score(state.hand); banker = score(state.dealer);
    }
    finishRound(player > banker ? state.wager * 2 : player === banker ? state.wager : 0,
      `PLAYER bet: player ${player}, banker ${banker}`);
  }
  function playCraps() {
    if (!state.point && !debit()) return;
    state.dice = [rng.int(6) + 1, rng.int(6) + 1];
    const sum = state.dice[0] + state.dice[1];
    if (!state.point) {
      if (sum === 7 || sum === 11) finishRound(state.wager * 2, `Come-out ${sum}: pass wins`);
      else if ([2, 3, 12].includes(sum)) finishRound(0, `Come-out ${sum}: craps`);
      else {
        state.point = sum;
        state.phase = 'point';
        state.message = `Point ${sum}. Roll again: point wins; 7 loses. Stake locked.`;
        persist();
      }
    } else if (sum === state.point || sum === 7) {
      const win = sum === state.point;
      state.point = 0;
      finishRound(win ? state.wager * 2 : 0, `Rolled ${sum}: ${win ? 'point made' : 'seven out'}`);
    } else {
      state.message = `Rolled ${sum}. Point remains ${state.point}; no additional debit.`;
      persist();
    }
  }
  function play() {
    switch (definition.kind) {
      case 'poker': playPoker(); break;
      case 'blackjack': playBlackjack(); break;
      case 'baccarat': playBaccarat(); break;
      case 'craps': playCraps(); break;
      case 'roulette': {
        if (!debit()) return;
        const number = rng.int(definition.american ? 38 : 37);
        state.drawn = [number];
        finishRound(roulettePayout(number, state.selection, state.wager),
          `Ball ${number === 37 ? '00' : number}; straight-up ${state.selection === 37 ? '00' : state.selection}`);
        break;
      }
      case 'keno': {
        if (state.picks.length !== 5) { state.message = 'Select exactly 5 numbers before drawing.'; return; }
        if (!debit()) return;
        state.drawn = shuffle(Array.from({ length: 80 }, (_, i) => i + 1), rng).slice(0, 20);
        const hits = state.picks.filter(number => state.drawn.includes(number)).length;
        finishRound((KENO_PAYS[hits] || 0) * state.wager, `${hits}/5 numbers matched`);
        break;
      }
      case 'scratch': {
        if (!debit()) return;
        state.drawn = [rng.int(6), rng.int(6), rng.int(6)];
        const wins = state.drawn.every(symbol => symbol === state.drawn[0]);
        finishRound(wins ? state.wager * 20 : 0, `Scratch symbols: ${state.drawn.join(' · ')}`);
        break;
      }
      case 'slots': {
        if (!debit()) return;
        const reels = definition.reels === 3 ? slots.REELS3 : slots.REELS5;
        state.grid = slots.spin(reels, rng);
        const result = slots.evaluateLines(state.grid, paylines, slots.SLOT_PAYS);
        finishRound(result.total * state.bet, `${result.wins.length} winning lines`);
        break;
      }
    }
  }
  function toggleHold(index) {
    if (state.phase === 'draw' && index >= 0 && index < 5) {
      state.held[index] = !state.held[index];
      persist();
    }
  }
  function select(delta) {
    if (definition.kind === 'poker') state.cursor = (state.cursor + delta + 5) % 5;
    else if (definition.kind === 'roulette') state.selection = (state.selection + delta + (definition.american ? 38 : 37)) % (definition.american ? 38 : 37);
    else if (definition.kind === 'blackjack') state.selection = delta < 0 ? 0 : 1;
    else if (definition.kind === 'keno') state.cursor = (state.cursor + delta + 80) % 80;
  }
  function togglePick(number) {
    if (state.picks.includes(number)) state.picks = state.picks.filter(pick => pick !== number);
    else if (state.picks.length < 5) state.picks.push(number);
    persist();
  }
  function click(x, y) {
    if (y >= 450 && y <= 490) {
      if (x >= 35 && x <= 95) setBet(-1);
      else if (x >= 105 && x <= 165) setBet(1);
      else if (x >= 335 && x <= 625) play();
      else if (x >= 740 && x <= 925) reset();
      return;
    }
    if (definition.kind === 'poker' && y >= 175 && y <= 290) {
      const index = Math.floor((x - 40) / 110);
      if (x >= 40 && x < 590 && (x - 40) % 110 < 95) toggleHold(index);
    } else if (definition.kind === 'keno' && x >= 40 && x < 600 && y >= 155 && y < 395) {
      togglePick(Math.floor((y - 155) / 30) * 10 + Math.floor((x - 40) / 56) + 1);
    } else if (definition.kind === 'roulette' && y >= 170 && y < 370 && x >= 40 && x < 600) {
      const selection = Math.floor((y - 170) / 40) * 8 + Math.floor((x - 40) / 70);
      if (selection < (definition.american ? 38 : 37)) state.selection = selection;
    } else if (definition.kind === 'blackjack' && state.phase === 'blackjack') {
      state.selection = x < 480 ? 0 : 1;
    }
  }
  const saved = context.load?.();
  const loaded = saved?.data ?? saved;
  if (validSave(loaded, definition)) state = copy(loaded);

  function update() {
    const pressed = action => context.input?.pressed?.(action);
    const pointer = context.pointer || context.input?.pointer || {};
    if (pressed('left')) select(-1);
    if (pressed('right')) select(1);
    if (pressed('up')) {
      if (state.phase === 'draw') toggleHold(state.cursor);
      else if (definition.kind === 'keno') togglePick(state.cursor + 1);
      else setBet(1);
    }
    if (pressed('down')) setBet(-1);
    // The shared input's action edge also fires on pointer-down; buttons handle that separately.
    if (!pointer.down && (pressed('fire') || pressed('confirm') || pressed('action'))) play();
    if (pressed('reset')) reset();
    if (pointer.down && !pointerDown) {
      click(pointer.x, pointer.y);
    }
    pointerDown = Boolean(pointer.down);
  }
  function render() {
    const ctx = context.ctx;
    if (!ctx) return;
    ctx.fillStyle = '#09271f'; ctx.fillRect(0, 0, 960, 540);
    const text = (value, x, y, size = 18, color = '#ecfff4') => {
      ctx.fillStyle = color; ctx.font = `${size}px sans-serif`; ctx.fillText(String(value), x, y);
    };
    const box = (x, y, w, h, fill = '#174737') => {
      ctx.fillStyle = fill; ctx.fillRect(x, y, w, h);
    };
    text(definition.title, 30, 36, 26);
    text(`Credits ${state.credits}   Stake ${state.bet}${units > 1 ? ` × ${units} ${definition.kind === 'slots' ? 'lines' : 'hands'} = ${totalBet()}` : ''}   Gross ${state.lastGross}`, 30, 69);
    text(NOTICE, 30, 98, 15, '#ffde8c');
    if (context.upgrades?.has(guideId)) {
      const guide = {
        poker: 'GUIDE: Deal debits all hands. HOLD keeps cards. DRAW credits gross returns.',
        slots: 'GUIDE: Stake is per line. Only consecutive matches from the leftmost reel pay.',
        blackjack: 'GUIDE: Choose HIT or STAND before confirming. Aces count as 1 or 11.',
        roulette: 'GUIDE: Select one pocket. Gross 36× includes the returned winning stake.',
        baccarat: 'GUIDE: You wager on PLAYER; a tie returns your stake.',
        keno: 'GUIDE: Select exactly five numbers; starred numbers were drawn.',
        craps: 'GUIDE: After the point is set, keep rolling without paying another stake.',
        scratch: 'GUIDE: All three revealed symbols must match to win.',
      }[definition.kind];
      text(guide, 30, 122, 12, '#ffde8c');
    }
    if (definition.kind === 'poker') {
      for (let i = 0; i < 5; i++) {
        box(40 + i * 110, 175, 95, 115, state.cursor === i ? '#e4bd52' : '#b4c9be');
        text(state.hand[i] == null ? '?' : cardLabel(state.hand[i]), 48 + i * 110, 222, 25, '#10251e');
        text(state.held[i] ? 'HOLD' : '—', 48 + i * 110, 268, 17, '#10251e');
      }
      const table = tableFor(definition.variant || 'jacks');
      text('GROSS × stake (not profit)', 620, 136, 16, '#ffde8c');
      Object.entries(table).slice(0, 15).forEach(([name, value], i) =>
        text(`${name}: ${typeof value === 'object' ? JSON.stringify(value) : value}`, 620, 158 + i * 17, 12));
      if (hands > 1) {
        text('Independent replacement decks; held cards copied to every hand.', 35, 321, 14);
        state.results.forEach((result, i) => {
          const column = Math.floor(i / 5), row = i % 5;
          text(`${i + 1}: ${result.hand.map(cardLabel).join(' ')} ${result.category} +${result.gross}`,
            35 + column * 290, 342 + row * 15, 10);
        });
      }
      if (definition.ultimate) text(`House-rule future multiplier: current ×${state.activeMultiplier}; next ×${state.nextMultiplier}. Any win makes next ×2; loss ×1.`, 35, 330, 13);
      const words = pokerDescription(definition.variant || 'jacks', definition.ultimate).split(' ');
      const lines = [''];
      for (const word of words) {
        const last = lines.length - 1;
        if ((lines[last] + word).length > 145) lines.push(`${word} `);
        else lines[last] += `${word} `;
      }
      lines.slice(0, 3).forEach((line, i) => text(line, 30, 412 + i * 12, 10));
    } else if (definition.kind === 'slots') {
      state.grid.forEach((symbols, row) => {
        symbols.forEach((symbol, reel) => {
          box(60 + reel * 105, 155 + row * 65, 95, 58);
          text(symbol, 70 + reel * 105, 193 + row * 65, 23);
        });
      });
      text('Gross multipliers / paylines:', 610, 150, 15, '#ffde8c');
      const pays = slots.SLOT_PAYS;
      Object.entries(pays).slice(0, 10).forEach(([symbol, pay], i) =>
        text(`${symbol}: ${JSON.stringify(pay)}`, 610, 175 + i * 21, 13));
      text(`Lines: ${JSON.stringify(paylines)}`, 30, 390, 12);
      text(`Exact RTP ${(slotReturns.get(definition.reels).rtp * 100).toFixed(4)}%; uniform independent stops, leftmost matches; stake PER LINE.`, 30, 422, 13);
    } else if (definition.kind === 'roulette') {
      for (let n = 0; n < (definition.american ? 38 : 37); n++) {
        const x = 40 + n % 8 * 70, y = 170 + Math.floor(n / 8) * 40;
        box(x, y, 64, 35, n === state.selection ? '#947b20' : '#174737');
        text(n === 37 ? '00' : n, x + 15, y + 25);
      }
      text('Straight-up only: gross 36×. Select number with arrows/click.', 40, 140, 16);
      text(`Theoretical RTP ${definition.american ? '36/38 = 94.7368%' : '36/37 = 97.2973%'}; uniform pockets.`, 40, 410, 15);
    } else if (definition.kind === 'keno') {
      for (let n = 1; n <= 80; n++) {
        const x = 40 + (n - 1) % 10 * 56, y = 155 + Math.floor((n - 1) / 10) * 30;
        box(x, y, 52, 27, state.picks.includes(n) ? '#947b20' : '#174737');
        text(`${n}${state.drawn.includes(n) ? '*' : ''}`, x + 5, y + 20, 14,
          state.cursor === n - 1 ? '#ffde8c' : '#ecfff4');
      }
      text('Pick exactly 5; 20/80 drawn. Gross: 3 hits 2×, 4 hits 10×, 5 hits 100×.', 35, 135, 15);
      text(`Exact RTP ${(KENO_RTP * 100).toFixed(4)}%; uniform 20-of-80 draw, five fixed picks. Click/↑ toggles.`, 35, 422, 13);
    } else {
      const hideDealer = definition.kind === 'blackjack' && state.phase === 'blackjack';
      text(`Player: ${state.hand.map(cardLabel).join('  ')}`, 40, 190, 25);
      text(`Dealer / banker: ${state.dealer.map((card, i) => hideDealer && i ? '?' : cardLabel(card)).join('  ')}`, 40, 235, 25);
      if (definition.kind === 'blackjack') text(`HIT ${state.selection === 0 ? '◀' : ''}                    STAND ${state.selection === 1 ? '◀' : ''}`, 40, 295, 23);
      if (definition.kind === 'craps') text(`Dice: ${state.dice.join(' + ')}    Point: ${state.point || 'come-out'}`, 40, 295, 25);
      if (definition.kind === 'scratch') text(`Symbols: ${state.drawn.join('   |   ')}`, 40, 295, 30);
      text(definition.rules, 35, 360, 15);
      const odds = definition.kind === 'craps'
        ? `Exact pass-line RTP ${((488 / 495) * 100).toFixed(4)}%; fair dice, completed pass-line cycles.`
        : definition.kind === 'scratch'
          ? `Exact RTP ${((20 / 36) * 100).toFixed(4)}%; three independent uniform symbols from six, gross 20×.`
          : 'RTP not calculated for these simplified rules.';
      text(odds, 35, 420, 14);
    }
    box(35, 450, 60, 40); text('− bet', 40, 477);
    box(105, 450, 60, 40); text('+ bet', 110, 477);
    box(335, 450, 290, 40, '#756123');
    text(state.phase === 'draw' ? 'DRAW' : state.phase === 'blackjack' ? (state.selection === 0 ? 'HIT' : 'STAND') : state.point ? 'ROLL POINT' : 'PLAY / DEAL', 365, 478);
    if (state.credits < units && !roundActive()) {
      box(740, 450, 185, 40, '#653b2b'); text('RESET BANKRUPTCY', 746, 476, 14);
    }
    text(state.message.slice(0, 120), 30, 515, 14);
  }
  return { update, render, serialize: snapshot, destroy: persist };
}

function validSave(saved, definition) {
  if (!saved || saved.version !== 1 || saved.id !== definition.id
    || !integer(saved.credits) || saved.credits < 0 || saved.credits > 1e12
    || !integer(saved.bet) || saved.bet < 1 || saved.bet > 100
    || !integer(saved.wager) || saved.wager < 0 || saved.wager > 1000
    || !['ready', 'draw', 'blackjack', 'point'].includes(saved.phase)
    || !integer(saved.cursor) || saved.cursor < 0 || saved.cursor > 79
    || !integer(saved.selection) || saved.selection < 0 || saved.selection > 37
    || ![0, 4, 5, 6, 8, 9, 10].includes(saved.point)
    || ![1, 2].includes(saved.nextMultiplier) || ![1, 2].includes(saved.activeMultiplier)) return false;
  for (const key of ['hand', 'dealer', 'shoe']) {
    if (!Array.isArray(saved[key]) || saved[key].length > 53
      || saved[key].some(card => !integer(card) || card < 0 || card > (definition.variant === 'joker' ? 52 : 51))) return false;
  }
  if (!Array.isArray(saved.held) || saved.held.length !== 5 || saved.held.some(item => typeof item !== 'boolean')
    || !integer(saved.rounds) || saved.rounds < 0
    || !integer(saved.lastGross) || saved.lastGross < 0
    || !Array.isArray(saved.results) || saved.results.length > 10
    || saved.results.some(result => !result || !Array.isArray(result.hand) || result.hand.length !== 5
      || result.hand.some(card => !integer(card) || card < 0 || card > 52)
      || typeof result.category !== 'string' || !integer(result.gross) || result.gross < 0)
    || !Array.isArray(saved.grid) || saved.grid.length > 3
    || saved.grid.some(row => !Array.isArray(row) || row.length > 5 || row.some(symbol => typeof symbol !== 'string'))
    || !Array.isArray(saved.picks) || saved.picks.length > 5
    || new Set(saved.picks).size !== saved.picks.length
    || saved.picks.some(n => !integer(n) || n < 1 || n > 80)
    || !Array.isArray(saved.drawn) || saved.drawn.length > 20 || saved.drawn.some(n => !integer(n) || n < 0 || n > 80)
    || !Array.isArray(saved.dice) || saved.dice.length > 2 || saved.dice.some(n => !integer(n) || n < 1 || n > 6)
    || typeof saved.message !== 'string') return false;
  if (saved.phase === 'draw' && (definition.kind !== 'poker' || saved.hand.length !== 5
    || saved.shoe.length !== (definition.variant === 'joker' ? 48 : 47)
    || new Set([...saved.hand, ...saved.shoe]).size !== saved.hand.length + saved.shoe.length
    || saved.wager !== saved.bet * (definition.hands || 1))) return false;
  if (saved.phase === 'blackjack' && (definition.kind !== 'blackjack'
    || saved.hand.length < 2 || saved.dealer.length !== 2 || saved.shoe.length < 1 || saved.wager !== saved.bet)) return false;
  if (saved.point && (definition.kind !== 'craps' || saved.phase !== 'point' || saved.wager !== saved.bet)) return false;
  if (saved.phase === 'point' && !saved.point) return false;
  if (saved.phase === 'ready' && (saved.wager !== 0 || saved.point !== 0)) return false;
  return true;
}

const definitions = [
  ...[
    ['jacks', 'Jacks or Better'], ['deuces', 'Deuces Wild'], ['bonus', 'Bonus Poker'],
    ['double-bonus', 'Double Bonus'], ['double-double-bonus', 'Double Double Bonus'],
    ['joker', 'Joker Poker'], ['tens', 'Tens or Better'], ['all-american', 'All American'],
  ].map(([variant, title]) => ({ id: `video-poker-${variant}`, title, kind: 'poker', variant })),
  ...[3, 5, 10].map(hands => ({ id: `video-poker-multi-${hands}`, title: `${hands}-Hand Jacks or Better`, kind: 'poker', variant: 'jacks', hands })),
  { id: 'video-poker-ultimate-x', title: 'Future Multiplier Poker (house rules)', kind: 'poker', variant: 'jacks', ultimate: true, minimal: true },
  { id: 'slots-3', title: 'Three Reel Slots', kind: 'slots', reels: 3 },
  { id: 'slots-5', title: 'Five Reel Slots', kind: 'slots', reels: 5 },
  { id: 'blackjack', title: 'Blackjack', kind: 'blackjack', minimal: true, rules: 'Gross: win 2×, push 1×, loss 0×. Naturals pay even money. No splits, double, insurance.' },
  { id: 'roulette-european', title: 'European Roulette', kind: 'roulette', minimal: true },
  { id: 'roulette-american', title: 'American Roulette', kind: 'roulette', american: true, minimal: true },
  { id: 'baccarat', title: 'Baccarat — Player Bet', kind: 'baccarat', minimal: true, rules: 'Standard third-card rules. Player bet only: gross win 2×, tie 1×, loss 0×.' },
  { id: 'keno', title: 'Five Pick Keno', kind: 'keno', minimal: true },
  { id: 'craps', title: 'Craps — Pass Line', kind: 'craps', minimal: true, rules: 'Come-out: 7/11 win; 2/3/12 lose; otherwise point. Point before 7 wins. Gross win 2×.' },
  { id: 'scratch', title: 'Virtual Scratch', kind: 'scratch', minimal: true, rules: 'Reveal 3 independent symbols, each 0–5. Three equal symbols return gross 20×; otherwise 0×.' },
];

const casinoVoices = {
  poker: ['sine', 440], slots: ['triangle', 330], blackjack: ['triangle', 220],
  roulette: ['sine', 330], baccarat: ['sine', 550], keno: ['triangle', 550],
  craps: ['square', 220], scratch: ['sawtooth', 110],
};

// Minimal table games intentionally omit side bets and advanced betting interfaces.
export const casinoPlugins = definitions.map((definition, index) => ({
  manifest: {
    id: definition.id, title: definition.title, version: '1.0.0', genre: 'casino',
    status: definition.minimal ? 'minimal' : 'complete',
    config: { startingCredits: START, maximumBet: 100, virtualOnly: true, hands: definition.hands || 1 },
    features: ['virtual credits', 'saved bankroll', 'keyboard', 'pointer', 'gross paytable', 'optional rules guide'],
    upgrades: [{ id: `${definition.id}-rules-guide`, cost: 25, title: 'Quick rules guide (display only; odds unchanged)' }],
    sound: {
      profile: 'casino', bus: 'sfx', type: casinoVoices[definition.kind][0],
      base: casinoVoices[definition.kind][1] + index * 7,
    },
    description: `${NOTICE} ${definition.kind === 'poker' ? pokerDescription(definition.variant || 'jacks', definition.ultimate) : definition.rules || 'See in-game rules and gross returns.'}`,
    controls: '←/→ select; ↑ hold or increase stake; ↓ decrease stake; Space/Enter play. Click cards, numbers and buttons. Reset button only when bankrupt.',
  },
  create: context => createCasino(context, definition),
}));
