const E = require("../engine");

const card = (rank, suit = 0) => suit * 13 + rank - 2;
const hand = (...ranks) => ranks.map((r, i) => card(r, i % 4));
const sequence = values => {
  let index = 0;
  return limit => {
    const value = values[index++];
    if (!Number.isInteger(value) || value < 0 || value >= limit) throw new Error("Bad test RNG");
    return value;
  };
};

describe("cards and payout mathematics", () => {
  test("shuffle preserves exactly 52 distinct cards", () => {
    const deck = E.shuffledDeck(() => 0);
    expect(new Set(deck).size).toBe(52);
    expect(deck.slice().sort((a, b) => a - b)).toEqual(Array.from({ length: 52 }, (_, i) => i));
    expect(E.cardLabel(card(14, 3))).toBe("A♣");
  });
  test.each([
    [[10, 11, 12, 13, 14].map(r => card(r)), "royal", 250],
    [[14, 2, 3, 4, 5].map(r => card(r, 1)), "straightFlush", 50],
    [hand(8, 8, 8, 8, 2), "four", 25],
    [hand(8, 8, 8, 2, 2), "fullHouse", 9],
    [[2, 5, 7, 11, 14].map(r => card(r)), "flush", 6],
    [hand(14, 2, 3, 4, 5), "straight", 4],
    [hand(8, 8, 8, 2, 4), "three", 3],
    [hand(8, 8, 2, 2, 4), "twoPair", 2],
    [hand(11, 11, 2, 5, 8), "highPair", 1],
    [hand(10, 10, 2, 5, 8), "nothing", 0],
    [hand(14, 2, 3, 4, 6), "nothing", 0]
  ])("classifies %j as %s", (cards, category, multiplier) => {
    expect(E.evaluatePoker(cards)).toEqual({ category, multiplier });
  });
  test("variant-specific pairs and quads", () => {
    expect(E.evaluatePoker(hand(10, 10, 2, 5, 8), "tens").multiplier).toBe(1);
    expect(E.evaluatePoker(hand(14, 14, 14, 14, 2), "bonus").multiplier).toBe(80);
    expect(E.evaluatePoker(hand(3, 3, 3, 3, 2), "bonus").multiplier).toBe(40);
    expect(E.evaluatePoker(hand(5, 5, 5, 5, 2), "bonus").multiplier).toBe(25);
    expect(() => E.evaluatePoker([0, 0, 1, 2, 3])).toThrow();
    expect(() => E.evaluatePoker([0, 1, 2, 3, 52])).toThrow();
    expect(() => E.evaluatePoker(hand(2, 3, 4, 5, 6), "__proto__")).toThrow();
  });
  test("all 2,598,960 poker hands match established category counts", () => {
    const counts = {};
    for (let a = 0; a < 48; a++) for (let b = a + 1; b < 49; b++)
      for (let c = b + 1; c < 50; c++) for (let d = c + 1; d < 51; d++)
        for (let e = d + 1; e < 52; e++) {
          const category = E.evaluatePoker([a, b, c, d, e]).category;
          counts[category] = (counts[category] || 0) + 1;
        }
    expect(counts).toEqual({
      royal: 4, straightFlush: 36, four: 624, fullHouse: 3744, flush: 5108,
      straight: 10200, three: 54912, twoPair: 123552, highPair: 337920, nothing: 2062860
    });
  }, 60000);
  test("roulette has 18 red and 18 black pockets; zero loses color bets", () => {
    const red = Array.from({ length: 37 }, (_, n) => E.rouletteMultiplier(n, "red"));
    const black = Array.from({ length: 37 }, (_, n) => E.rouletteMultiplier(n, "black"));
    expect(red.reduce((a, b) => a + b)).toBe(36);
    expect(black.reduce((a, b) => a + b)).toBe(36);
    expect(red[0]).toBe(0); expect(black[0]).toBe(0);
    expect(E.rouletteMultiplier(0, 0)).toBe(36);
    expect(E.rouletteMultiplier(36, 35)).toBe(0);
    expect(() => E.rouletteMultiplier(37, "red")).toThrow();
    expect(() => E.rouletteMultiplier(0, "invalid")).toThrow();
  });
  test("enumerates slots: return is exactly 210/216, not stacked awards", () => {
    let returns = 0;
    for (let a = 0; a < 6; a++) for (let b = 0; b < 6; b++) for (let c = 0; c < 6; c++) {
      const casino = new E.Casino(sequence([a, b, c]));
      const result = casino.slots(1);
      returns += result.payout;
      expect(casino.credits).toBe(999 + result.payout);
    }
    expect(returns).toBe(210);
  });
  test.each(["low", "high"])("dice %s: return is exactly 30/36 and 7 loses", choice => {
    let returns = 0;
    for (let a = 0; a < 6; a++) for (let b = 0; b < 6; b++) {
      const result = new E.Casino(sequence([a, b])).dice(1, choice);
      returns += result.payout;
      if (result.sum === 7) expect(result.payout).toBe(0);
    }
    expect(returns).toBe(30);
  });
});

describe("credit and hand lifecycle", () => {
  test.each([0, -1, 1.5, 101, NaN, Infinity, "2"])("rejects invalid wager %s without debiting", stake => {
    const casino = new E.Casino(() => 0);
    expect(() => casino.slots(stake)).toThrow();
    expect(casino.credits).toBe(1000);
    expect(casino.round).toBeNull();
  });
  test("insufficient credits, invalid choices and variants do not debit", () => {
    const casino = new E.Casino(() => 0);
    casino.credits = 1;
    expect(() => casino.slots(2)).toThrow();
    expect(() => casino.roulette(1, "green")).toThrow();
    expect(() => casino.dice(1, "seven")).toThrow();
    expect(() => casino.dealPoker(1, "unknown")).toThrow();
    expect(casino.credits).toBe(1);
  });
  test("draw respects holds, excludes dealt cards, debits once and cannot repeat settlement", () => {
    const casino = new E.Casino(() => 0);
    const original = casino.dealPoker(2, "jacks");
    expect(casino.credits).toBe(998);
    expect(() => casino.slots(2)).toThrow();
    expect(() => casino.dealBlackjack(2)).toThrow();
    expect(() => casino.drawPoker([true])).toThrow();
    const result = casino.drawPoker([true, false, true, false, false]);
    expect(result.cards[0]).toBe(original[0]); expect(result.cards[2]).toBe(original[2]);
    [1, 3, 4].forEach(i => expect(original).not.toContain(result.cards[i]));
    expect(new Set(result.cards).size).toBe(5);
    expect(casino.credits).toBe(998 + result.payout);
    expect(() => casino.drawPoker([true, true, true, true, true])).toThrow();
  });
  test("blackjack ace handling and even-bet validation", () => {
    expect(E.blackjackTotal(hand(14, 14, 9))).toBe(21);
    expect(E.blackjackTotal(hand(14, 6))).toBe(17);
    expect(E.blackjackTotal(hand(14, 13, 8))).toBe(19);
    const casino = new E.Casino(() => 0);
    expect(() => casino.dealBlackjack(3)).toThrow();
    expect(casino.credits).toBe(1000);
  });
  function blackjackRound(player, dealer, deck = []) {
    const casino = new E.Casino(() => 0);
    casino.wager(2);
    casino.round = { kind: "blackjack", player, dealer, deck, stake: 2 };
    return casino;
  }
  test("blackjack hides the dealer card until settlement and stands on soft 17", () => {
    const casino = blackjackRound(hand(10, 8), hand(14, 6), [card(13)]);
    expect(casino.blackjackView().dealer).toHaveLength(1);
    const result = casino.blackjack("stand");
    expect(result.dealer).toHaveLength(2);
    expect(result.payout).toBe(4);
    expect(() => casino.blackjack("stand")).toThrow();
  });
  test("blackjack hit, bust, dealer draw and push settle once", () => {
    const bust = blackjackRound(hand(10, 9), hand(10, 8), [card(5)]);
    expect(bust.blackjack("hit").payout).toBe(0);
    const hit = blackjackRound(hand(2, 3), hand(10, 6), [card(5), card(4)]);
    expect(hit.blackjack("hit").done).toBe(false);
    expect(hit.blackjack("stand").payout).toBe(0);
    const push = blackjackRound(hand(10, 8), hand(10, 8));
    expect(push.blackjack("stand").payout).toBe(2);
  });
  test("natural blackjack pays 3:2 profit, opposing naturals push", () => {
    // Fisher-Yates can be scripted to produce a chosen deck prefix.
    function rngForPrefix(prefix) {
      const target = [...prefix, ...Array.from({ length: 52 }, (_, i) => i).filter(i => !prefix.includes(i))];
      const working = Array.from({ length: 52 }, (_, i) => i), draws = [];
      for (let i = 51; i > 0; i--) {
        const j = working.indexOf(target[i]);
        draws.push(j); [working[i], working[j]] = [working[j], working[i]];
      }
      return sequence(draws);
    }
    const casino = new E.Casino(rngForPrefix([card(14), card(13), card(10, 1), card(8, 1)]));
    expect(casino.dealBlackjack(2).payout).toBe(5);
    expect(casino.credits).toBe(1003);
    const push = new E.Casino(rngForPrefix([card(14), card(13), card(14, 1), card(13, 1)]));
    expect(push.dealBlackjack(2).payout).toBe(2);
    const loss = new E.Casino(rngForPrefix([card(10), card(8), card(14, 1), card(13, 1)]));
    expect(loss.dealBlackjack(2).payout).toBe(0);
  });
});

describe("arcade lifecycle and extensions", () => {
  test.each(["pong", "breakout", "snake", "dodge"])("%s starts, updates and stops after game over", id => {
    const state = E.createArcade(id, () => 0);
    E.updateArcade(state, { x: 0.5, y: 0.5, dx: 0, dy: 0 }, 1 / 120, () => 0);
    expect(state.shapes.length).toBeGreaterThan(0);
    expect(state.score).toBeGreaterThanOrEqual(0);
    state.over = true;
    const saved = JSON.stringify(state);
    E.updateArcade(state, {}, 1 / 120, () => 0);
    expect(JSON.stringify(state)).toBe(saved);
    expect(() => E.updateArcade(state, {}, 1)).toThrow();
    expect(() => E.updateArcade(state, {}, NaN)).toThrow();
  });
  test("snake cannot reverse; food never spawns in its body; walls end play", () => {
    const state = E.createArcade("snake", () => 0);
    E.updateArcade(state, { dx: -1, dy: 0 }, 0.05, () => 0);
    expect(state.nextDx).toBe(1);
    expect(state.body).not.toContainEqual(state.food);
    for (let i = 0; i < 100; i++) E.updateArcade(state, { dx: 1, dy: 0 }, 0.05, () => 0);
    expect(state.over).toBe(true);
  });
  test("snake may move into the vacating tail but not the body", () => {
    const state = E.createArcade("snake", () => 0);
    state.body = [{ x: 1, y: 1 }, { x: 1, y: 2 }, { x: 2, y: 2 }, { x: 2, y: 1 }];
    state.dx = 0; state.dy = -1; state.clock = 0.16;
    E.updateArcade(state, { dx: 1, dy: 0 }, 0.01, () => 0);
    expect(state.over).toBe(false);
    state.body = [{ x: 2, y: 1 }, { x: 2, y: 2 }, { x: 3, y: 2 }, { x: 3, y: 1 }, { x: 4, y: 1 }];
    state.clock = 0.16;
    E.updateArcade(state, { dx: 0, dy: 1 }, 0.01, () => 0);
    expect(state.over).toBe(true);
  });
  test("pong and breakout consume lives; dodge scores only avoided meteors", () => {
    for (const id of ["pong", "breakout"]) {
      const state = E.createArcade(id);
      for (let i = 0; i < 3; i++) {
        if (id === "pong") { state.x = -0.1; state.vx = -0.3; }
        else state.y = 1.1;
        E.updateArcade(state, {}, 0.01);
      }
      expect(state.lives).toBe(0); expect(state.over).toBe(true);
    }
    const dodge = E.createArcade("dodge");
    dodge.rocks = [{ x: 0.5, y: 0.87 }, { x: 0.1, y: 1.06 }];
    E.updateArcade(dodge, { x: 0.5 }, 0.01, () => 0);
    expect(dodge.lives).toBe(2); expect(dodge.score).toBe(10);
  });
  test("level upgrades and compatible trusted-code registration", () => {
    E.registerGame({ id: "test-plugin", title: "Test", version: 1, create: () => ({}),
      update: s => { s.shapes = []; } });
    const state = E.createArcade("test-plugin");
    state.score = 300; E.updateArcade(state, {}, 0);
    expect(state.level).toBe(4);
    expect(() => E.registerGame({ id: "test-plugin" })).toThrow();
    expect(() => E.registerGame({ id: "bad-version", version: 2 })).toThrow();
    expect(() => E.createArcade("not-registered")).toThrow();
  });
  test("3D and 4D projections are finite and rotate along distinct axes", () => {
    for (const mode of ["still", "orbit", "4d"]) {
      for (let a = 0; a < 10; a += 0.1) {
        const p = E.project([0.85, -0.85, 0.85, -0.85], a, mode);
        expect(Number.isFinite(p.x + p.y + p.scale)).toBe(true);
      }
    }
    expect(E.project([1, 1, 1, 1], 0, "4d")).not.toEqual(E.project([1, 1, 1, 1], 1, "4d"));
    expect(() => E.randomInt(0)).toThrow();
    expect(() => E.randomInt(1.5)).toThrow();
    for (let i = 0; i < 20; i++) expect(E.randomInt(7)).toBeLessThan(7);
  });
});
