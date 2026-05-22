# Poker Pool — Development Plan

## Milestone 1: Local Playable Prototype

**Goal:** Prove the core rules and feel with a complete local 2-player match.

### Phase A: Foundation (Tasks 1-3)
1. **Project scaffold** — Phaser 3 + Matter.js, TypeScript, directory structure, config files, HTML entry
2. **Game state model & rules engine** — Pure TS state, suit claiming, card registration, validity, shot resolution, miss counting, Stand, showdown triggers
3. **Poker hand evaluator** — Standard 5-card ranking, kickers, ace-low straights, partial hands

### Phase B: Physics & Controls (Tasks 4-5)
4. **Physics layer** — Table, 6 pockets, 15+1 balls, forgiving pocket geometry, capture zones, rails, settling detection
5. **Shot controls** — Click-drag aim, power from distance, trajectory preview, arrow key fine aim

### Phase C: Match Flow (Task 6)
6. **Full match flow** — Coin-flip breaker, rack, break rules, Phase 1 (suit mapping), Phase 2 (hand race), shot resolution pipeline, card registration, respawn, swap, turns, Stand + showdown, 3-miss elimination

### Phase D: UI (Tasks 7-9)
7. **HUD & modals** — Both hands, active player, miss pips, phase, pocket labels, Stand countdown. Suit selection, wildcard, swap, showdown, concede modals
8. **Rules panel** — 4-tab info panel (How To Play, Poker Ranks, Pocket Rules, Controls)
9. **Debug toggles** — Backtick panel for tuning pocket size, capture, power, friction, overlays

### Phase E: Verification (Tasks 10, 12)
10. **Unit tests** — Core rule resolution coverage per spec §25
12. **Integration test** — Full match playthrough from break to win

### Exit Criteria
- Two local players can complete a match from break to win screen
- No rule-blocking bugs in card registration, swap, Stand, or showdown
- Pockets forgiving enough for non-pool players
- Architecture clean and understandable
- Config files tunable by non-technical collaborator

---

## Milestone 2: Juiced Prototype With AI (Future)
- AI opponent, polished visuals, audio, settings, expanded rules panel

## Milestone 3: Polished Online Game (Future)
- FTUE, online multiplayer, matchmaking, reconnect, responsive polish
