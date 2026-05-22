# Poker Pool Implementation Spec

Version: 1.3  
Source: `poker-pool.html` / embedded GDD v1.1  
Audience: AI coding agent implementing the game across the milestone roadmap

## 1. Product Summary

Poker Pool is a 1v1 competitive browser game on a 6-pocket pool table, playable first as local pass-and-play and later as online multiplayer. Players alternate pool shots to pocket numbered balls. Each valid pocketed ball becomes a poker card in the active player's visible hand. The goal is to win by building the strongest poker hand, forcing showdown through Stand, or eliminating the opponent through repeated missed turns.

The game has no hidden information. Both hands, claimed suits, miss counters, and valid pocket indicators are always visible.

## 2. Core Design Pillars

1. Pool skill and poker strategy matter equally.
2. Every shot must advance a hand, block a plan, claim territory, or carry risk.
3. The game state must be readable to spectators at a glance.

## 3. Game Entities

### 3.1 Players

Each player has:

- `id`
- `name`
- `hand`: 0 to 5 cards
- `missCount`: 0 to 3
- `hasStood`: boolean
- `isEliminated`: boolean

### 3.2 Balls

| Ball | Role | Card Rank | Pocket Behavior |
|---|---|---|---|
| 1 | Rank ball | Ace | Registers in valid Suit Holes |
| 2-10 | Rank balls | Face value | Registers in valid Suit Holes |
| 11 | Rank ball | Jack | Registers in valid Suit Holes |
| 12 | Rank ball | Queen | Registers in valid Suit Holes |
| 13 | Rank ball | King | Registers in valid Suit Holes |
| 14-15 | Wildcard balls | Chosen on use | Register only in Wild Holes during Phase 2 |
| Cue ball | Shot controller | None | Scratching is a foul |

Rank balls always respawn after valid registration. Wildcard balls are permanently removed after valid registration.

### 3.3 Pockets

There are six pockets:

- Four corner pockets.
- Two side pockets.

Pocket states:

- `unclaimed`: no suit yet.
- `suit`: assigned exactly one of ♠, ♥, ♦, ♣.
- `wild`: one of the two pockets left unclaimed after all four suits are assigned.

### 3.4 Forgiving Pocket Model

Poker Pool should feel more accessible than real billiards. The table still rewards good aiming, but shots should fail because the player chose a poor line or power, not because the simulation demands real pool precision.

Pocket tuning:

- Pocket collision radius should be 1.35x to 1.6x normal pool scale relative to ball radius.
- Add a subtle pocket capture zone: if an object ball enters the capture radius with a plausible inward velocity, guide it into the pocket center.
- Do not magnetize balls from unrealistic side angles. Capture should feel forgiving, not fake.
- Rail jaws should be rounded and generous.
- Cue ball scratching should use the same pocket capture rules as object balls.
- Expose pocket size and capture strength as debug-tunable constants.

## 4. Match Flow

1. Determine breaker.
2. Rack all balls.
3. Break shot.
4. Phase 1: Suit Mapping.
5. Phase 2: Hand Race.
6. Endgame through Stand, immediate showdown, elimination, or concede.
7. Showdown compares hands with standard poker ranking.

## 5. Setup

### 5.1 Breaker Selection

Use a coin-flip animation for breaker selection. A full pool lag shot is not planned unless playtests show the opening needs more pool authenticity.

### 5.2 Rack

Use a standard 15-ball triangle at the foot spot.

Rack rules:

- Place balls 1, 11, 12, and 13 in the center cluster.
- Randomize balls 2-10, 14, and 15 across all remaining positions.
- The apex ball must come from the outer randomized set.

Implementation note: define rack coordinates explicitly. Do not rely on prose positions such as "middle 4" without mapping them to deterministic rack indices.

### 5.3 Respawn Spots

Define nine respawn spots as table-relative coordinates:

| Spot | X | Y |
|---|---:|---:|
| 1 | 25% | 15% |
| 2 | 50% | 12% |
| 3 | 75% | 15% |
| 4 | 20% | 50% |
| 5 | 50% | 50% |
| 6 | 80% | 50% |
| 7 | 25% | 85% |
| 8 | 50% | 88% |
| 9 | 75% | 85% |

Respawn algorithm:

1. Shuffle all respawn spots.
2. Pick the first spot that is clear by at least one ball diameter plus a small margin.
3. If all spots are blocked, place at the foot spot only if clear.
4. If no safe spot exists, queue the respawn until physics settles, then retry.

## 6. Break Shot Rules

The break is exciting but must not award cards or suits.

Legal break:

- At least 4 balls contact rails after impact, or
- At least one object ball is pocketed.

Illegal break:

- Fewer than 4 rail contacts and no object ball pocketed.
- Opponent chooses either accept table as-is or re-rack and re-break.

Break resolution:

- Any object balls pocketed on the break respawn.
- No cards register.
- No suits are claimed.
- If at least one object ball was pocketed and the cue ball did not scratch, the breaker keeps the turn and shoots again under normal rules.
- If no object ball was pocketed, turn passes.
- If the cue ball scratches, all object balls pocketed on that shot respawn, breaker gains one miss, turn passes, and opponent receives Ball in Hand.

## 7. Phase 1: Suit Mapping

Phase 1 starts after the break and ends when four separate pockets have been assigned the four suits.

Design intent:

- Suit claiming is not a poker-rank advantage because poker suits are equal.
- Its purpose is spatial: it maps card suits onto table geography, creates route planning, and turns pocket choice into a hand-building decision.
- Players should not feel that "owning" a suit wins the game. They should feel that assigning suits creates the board they must now exploit.

Suit claiming rules:

- Only rank balls 1-13 can claim a suit.
- The first rank ball pocketed into an unclaimed pocket triggers suit selection.
- The active player chooses one unclaimed suit.
- Each suit may be assigned once.
- Suit assignments are permanent.
- Wildcard balls 14-15 cannot claim suits in Phase 1. If pocketed before Wild Holes exist, they respawn and do not register.

When the fourth suit is assigned:

- The two remaining unclaimed pockets become Wild Holes.
- Phase 2 begins immediately after the current shot resolves.

## 8. Phase 2: Hand Race

Phase 2 starts once all four suits are assigned.

Pocket behavior:

- Rank balls 1-13 register only in Suit Holes.
- Rank balls entering Wild Holes respawn and do not register.
- Wildcard balls 14-15 register only in Wild Holes.
- Wildcard balls entering Suit Holes respawn and do not register.

## 9. Validity Rules

A pocket is valid for the active player and target ball if pocketing that ball there would create a legal card.

For rank balls 1-13:

- Valid if the pocket is a Suit Hole and the active player does not already hold the same rank and suit.
- Invalid if the pocket is unclaimed before Phase 1 normal play has begun, a Wild Hole, or would duplicate an existing card.

For wildcard balls 14-15:

- Valid only if the pocket is a Wild Hole in Phase 2.
- On valid wildcard use, the player chooses any rank and one of the four claimed suits, excluding exact duplicate cards already in their hand.

Resolved implementation decision: validity is derived live from current game state. Do not store per-ball suit restriction flags. A respawned shared ball may be valid for one player and invalid for the other depending on their hands.

## 10. Shot Resolution

Resolve every shot after all balls stop moving.

Priority order:

1. If cue ball scratched, apply scratch rules and ignore all card registration from the shot.
2. Classify each pocketed object ball as valid or invalid for the active player.
3. Register all valid cards in deterministic pocket-event order.
4. Respawn all invalid balls that should remain in play.
5. Apply hand size and swap decisions.
6. Update miss counter and turn ownership.
7. Check elimination, phase transition, Stand countdown, and showdown triggers.

Multiple balls on one shot:

- If at least one valid card registers and there is no scratch, the shot is successful.
- Invalid balls from the same successful shot respawn and do not cancel the success.
- The active player's miss counter resets to 0 after any successful shot.
- A successful shot grants a bonus shot unless the game enters showdown or the player chooses to end the turn.
- If no valid card registers, the shot is a miss and the turn passes.

Scratch rules:

- Cue ball pocketed means scratch.
- Any object balls pocketed on the same shot respawn and do not register.
- Active player gains one miss.
- Turn passes.
- Opponent receives Ball in Hand and may place the cue ball anywhere legal on the table.

## 11. Card Registration

### 11.1 Rank Balls

When a rank ball enters a valid Suit Hole:

1. Card rank comes from the ball number.
2. Card suit comes from the pocket suit.
3. Card is added to the active player's hand or enters a swap decision if the hand is full.
4. The ball respawns.

### 11.2 Wildcard Balls

When a wildcard ball enters a Wild Hole in Phase 2:

1. Open a wildcard selection modal.
2. Player chooses rank and suit.
3. Disable exact duplicates already in the player's hand.
4. Register the selected card.
5. Permanently remove that wildcard ball from the table.

## 12. Hand Building

Players can hold at most five cards.

If hand has fewer than five cards:

- Add the new card automatically.

If hand already has five cards:

- Show the five current cards plus the new card.
- Player chooses one of the six cards to discard.
- Discarded card is removed permanently.
- Hand remains exactly five cards.
- The decision must resolve before the next bonus shot.

Cards are always visible to both players.

## 13. Turn Structure

A turn consists of one or more shots by the active player.

Shot sequence:

1. Aim.
2. Set power.
3. Release.
4. Wait for physics to settle.
5. Resolve shot.

Bonus shot:

- A successful shot grants another shot to the same player.
- Bonus shots can chain indefinitely.
- The player may voluntarily end their turn after any resolved successful shot.

Turn passes when:

- A shot registers no valid card.
- A scratch occurs.
- The player voluntarily ends their turn.
- The player declares Stand.
- Showdown or elimination triggers.

## 14. 3-Miss Elimination

Each player has an independent consecutive miss counter.

Miss count increments when:

- A turn ends with no valid card registered.
- Only invalid pockets occurred.
- The cue ball scratched.

Miss count resets when:

- The player registers at least one valid card during a shot.

At 3 consecutive misses:

- The player is eliminated immediately.
- The opponent wins.

UI requirement:

- Show three miss pips near each player.
- On second miss, play warning audio and animate the pips.
- On third miss, play elimination feedback and end the match.

## 15. Stand and Endgame

A player may declare Stand only at the start of their own turn and only while holding exactly five cards.

When a player declares Stand:

- That player takes no more shots.
- The opponent gets up to three turns to complete or improve their hand.
- The 3-miss rule still applies during the countdown.
- Countdown is shown as 3, 2, 1 near the opponent's active state.

Resolved countdown rule:

- If the responding opponent reaches five cards during the countdown, go to Showdown immediately after that shot and any required swap decision resolve.
- The responder does not need to declare Stand.
- If the responder never reaches five cards, go to Showdown after their third countdown turn ends.

Immediate showdown also occurs when both players have five-card hands after any shot resolution and no Stand countdown is needed.

## 16. Showdown and Winning

At Showdown:

1. Evaluate each player's current hand.
2. Compare with standard 5-card poker rules.
3. Higher-ranked hand wins.

Ranking order:

1. Royal Flush
2. Straight Flush
3. Four of a Kind
4. Full House
5. Flush
6. Straight
7. Three of a Kind
8. Two Pair
9. One Pair
10. High Card

Ace can be high or low for straights. A-2-3-4-5 is valid. Q-K-A-2-3 is not.

Tie rules:

- If hand category matches, use standard poker kickers.
- If hands are completely identical, the player who triggered the endgame wins.
- If neither player triggered the endgame, use active-player priority from the shot that caused showdown.
- If a player has fewer than five cards at forced showdown, evaluate the partial hand as the best available poker hand. A complete made hand beats unmatched high cards.

Other win conditions:

- Opponent reaches 3 misses.
- Opponent concedes.

## 17. Edge Cases

| Situation | Resolution |
|---|---|
| Valid and invalid balls pocketed together | Register valid cards, respawn invalid balls, count shot as success |
| Scratch with valid object balls pocketed | Scratch overrides all; object balls respawn, no cards register |
| Wildcard pocketed before Phase 2 | Respawn, no card, no suit claim |
| Wildcard enters Suit Hole in Phase 2 | Respawn, no card |
| Rank ball enters Wild Hole | Respawn, no card |
| Duplicate exact card would be created | Treat that pocket as invalid for that player |
| Respawn spot occupied | Try another clear spot; retry after physics settle if needed |
| Stand countdown opponent is eliminated | Declarer wins immediately |
| Both players reach five cards after one shot resolution | Immediate Showdown |
| All balls absent due to bug/failsafe | If one player has five cards, force Showdown; otherwise compare current hands and log error |

## 18. Controls

Desktop:

- Aim: click-drag from cue ball.
- Shoot: release mouse.
- Fine aim: arrow keys when aiming.
- Power: drag distance, or bracket keys for keyboard control.
- Stand: `S` when available.
- Swap: click card, confirm; keyboard `1`-`6`, Enter.
- Menu: Esc.

Mobile:

- Aim: drag from cue ball outward.
- Shoot: release finger.
- Pan: two-finger drag.
- Zoom: pinch.
- Swap: tap card, confirm.

Control constraints:

- No cue-ball spin, English, masse, or jump-shot controls in the planned milestone scope.
- The shot model is deliberately simple: choose direction, choose power, release.
- All tutorial copy, settings, and UI labels should reinforce "Aim + Power" as the complete control model.

## 19. Aiming Assist

Aiming assist is always active.

It shows:

- Valid Suit Hole: green glow.
- Invalid pocket: red glow.
- Unclaimed pocket during Phase 1: yellow pulse.
- Wild Hole: gold star/rim.
- Cue ball trajectory and first-struck object ball trajectory.

Do not show full multi-ball chain predictions. Preserve the skill ceiling.

## 20. UI Requirements

Design intent:

- Keep the center of the table clear during play.
- Use DOM overlays for text-heavy surfaces.
- Make rules help available in one tap/click at all times.
- Teach the game through contextual prompts, not long blocking tutorials.

Primary HUD:

- Active player indicator.
- Both visible hands.
- Current best hand label for each player.
- Miss pips for each player.
- Claimed pocket suits on the table.
- Phase indicator: Suit Mapping or Hand Race.
- Stand countdown when active.
- Help button that opens the info panel.

Modals:

- Suit selection after first rank ball enters an unclaimed pocket.
- Wildcard rank/suit selection.
- Swap decision when hand is full.
- Showdown result.
- Concede confirmation.

Cards:

- Use standard card faces when available.
- Suit colors follow poker convention: spades/clubs black, hearts/diamonds red.

### 20.1 Main Play HUD Mockup

Desktop layout:

```text
┌──────────────────────────────────────────────────────────────────────┐
│ Bob                     Hand: 5♠ 4♣ 6♠       Best: High Card     ?   │
│ Misses: ○ ○ ○                                      Phase: Suit Map   │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│                         TOP-DOWN POOL TABLE                          │
│                                                                      │
│       ♠ pocket                         unclaimed pocket              │
│                                                                      │
│              aim line + first-ball path only                         │
│                                                                      │
│       ♥ pocket                         ♦ pocket                      │
│                                                                      │
├──────────────────────────────────────────────────────────────────────┤
│ Alice                  Hand: A♥ 7♥ 9♦       Best: Pair Draw          │
│ Misses: ● ○ ○       [End Turn] [Stand] [Rules ?]        Power ▓▓░░   │
└──────────────────────────────────────────────────────────────────────┘
```

Mobile layout:

```text
┌─────────────────────────────┐
│ Bob: 5♠ 4♣      ○ ○ ○    ?  │
├─────────────────────────────┤
│                             │
│         POOL TABLE          │
│                             │
│   pocket labels on table    │
│                             │
├─────────────────────────────┤
│ Alice: A♥ 7♥ 9♦    ● ○ ○    │
│ Best: Pair Draw             │
│ [End] [Stand]     Power ▓▓░ │
└─────────────────────────────┘
```

HUD behavior:

- Opponent hand appears at the top edge in compact form.
- Active player hand appears at the bottom edge with larger cards.
- Power meter appears only while aiming or charging.
- Stand button is disabled until the active player has exactly 5 cards.
- Rules button opens a side drawer on desktop and a bottom sheet on mobile.
- Suit labels are anchored to pockets on the table, not duplicated in a large separate panel.

### 20.2 Rules and Poker Info Panel

The info panel must be available from the HUD with a `?` / Rules button and from pause.

Panel tabs:

- `How To Play`: short turn summary.
- `Poker Ranks`: ordered hand rankings with examples.
- `Pocket Rules`: Suit Holes, Wild Holes, valid vs invalid pockets.
- `Controls`: Aim, power, shoot, end turn, Stand, swap.

Panel content requirements:

- Keep each tab scannable; no paragraph longer than three lines.
- Poker Ranks tab must show the full ranking order from Royal Flush to High Card.
- Pocket Rules tab must explicitly say suits are equal in poker scoring; suit labels matter because they map card suits onto table pockets.
- Include a "Resume" button and close on Esc / backdrop tap.
- Opening the panel pauses aiming input but does not reset the current shot setup.

## 21. FTUE Flow

FTUE should teach Poker Pool in playable slices. Do not explain all rules before the first shot.

Implementation timing: full FTUE belongs to Milestone 3. Earlier milestones may include temporary contextual hints, but they should not be treated as final onboarding.

### 21.1 First Launch

Flow:

1. Show a short title card: "Build a poker hand by pocketing pool balls."
2. Offer `Quick Tutorial` and `Skip`.
3. Default focus is `Quick Tutorial`.

### 21.2 Tutorial Match Script

Use a guided local match with controlled ball placement and forgiving aim.

Step 1: Aim and power

- Highlight cue ball and one nearby rank ball.
- Prompt: "Drag from the cue ball to aim. Pull farther for more power."
- Require player to pocket the highlighted ball.
- On success, show: "Nice. That ball becomes a card."

Step 2: Suit mapping

- Ball enters an unclaimed pocket.
- Open suit selection with four choices.
- Prompt: "Choose which suit this pocket makes. Suits score equally; this only maps suits to table positions."
- Register the card and label the pocket.

Step 3: Valid pockets

- Highlight a second ball and two pockets.
- Show one green valid pocket and one red invalid pocket.
- Prompt: "Green pockets add cards. Red pockets respawn the ball."

Step 4: Build to five cards

- Fast-forward or prefill hand to four cards.
- Prompt player to pocket one more valid card.
- Show current best hand label updating.

Step 5: Swap decision

- Give the player a sixth card.
- Open swap modal.
- Prompt: "Keep your best five. Discard one card."

Step 6: Stand and showdown

- Enable Stand.
- Prompt: "Stand starts the endgame when you like your hand."
- Run a scripted mini showdown and show why the winning hand wins.

### 21.3 FTUE Rules

- Keep tutorial prompts dismissible after first completion.
- Store `hasCompletedFtue`.
- Allow replay from the info panel.
- If the player skips, show lightweight contextual hints during the first normal match.
- Contextual hints should stop after the player performs the related action twice.

### 21.4 Contextual Hint Triggers

| Trigger | Hint |
|---|---|
| First aim | Drag from the cue ball, then release to shoot. |
| First unclaimed pocket | Pick the suit this pocket will create. Suits are equal; position matters. |
| First invalid pocket aim | Red means the ball will respawn instead of becoming a card. |
| First 5-card hand | You can Stand at the start of your turn or keep shooting to improve. |
| First sixth card | Choose one card to discard; your hand stays at five. |
| Second miss | One more missed turn eliminates you. |

## 22. Visual and Audio Direction

Use Kenney assets where available:

- Playing Cards Pack for hand cards.
- Board Game Pack for felt/table texture and token bases.
- Board Game Icons for suits, stars, and UI symbols.
- Impact Sounds for ball collisions and rails.
- Casino Audio for pocket and card moments.
- UI Audio / Interface Sounds for modal and confirmation feedback.
- Music Loops / Jingles for ambient and results.

Programmatic visuals:

- Pool table rails and pockets.
- Ball rank overlays.
- Wildcard gold/star treatment.
- Pocket validity glows.
- Respawn drop-in animation.

## 23. Designer-Friendly Configuration and Project Structure

Poker Pool is expected to be built with AI assistance and iterated by non-technical collaborators. The project must therefore expose clear, safe tuning surfaces and avoid burying design values in scene code.

### 23.1 Architecture Principles

- Keep gameplay simulation outside Phaser scenes.
- Keep Phaser scenes thin: scene code loads assets, creates sprites, reads simulation state, emits input actions, plays effects, and updates presentation.
- Keep DOM overlays responsible for HUD, menus, help panels, settings, FTUE text, and accessibility-sensitive UI.
- Use stable manifest keys for assets. Gameplay code must not reference raw file paths.
- Put every designer-tweakable number in a named config file.
- No magic numbers in rule systems, Phaser scenes, UI layout, AI logic, or animation code.
- Save serializable game state only. Never save Phaser sprites, Matter bodies, tweens, emitters, or DOM nodes.

### 23.2 Recommended Directory Shape

```text
src/
  game/
    simulation/
      state.ts
      rules/
      systems/
      selectors/
    config/
      gameplay.config.ts
      physics.config.ts
      ai.config.ts
      scoring.config.ts
      debug.config.ts
    input/
      actions.ts
      bindings.ts
    assets/
      manifest.ts
      preloadGroups.ts
    content/
      pokerRanks.ts
      tutorialSteps.ts
      rulesHelp.ts
  phaser/
    scenes/
      BootScene.ts
      PreloadScene.ts
      GameScene.ts
      DebugScene.ts
    view/
      tableView.ts
      ballView.ts
      pocketView.ts
      effectsView.ts
    adapters/
      sceneBridge.ts
      matterBridge.ts
  ui/
    hud/
    panels/
    modals/
    ftue/
    theme.css
    layout.config.ts
  docs/
    TUNING.md
    ASSET_SWAP_GUIDE.md
```

### 23.3 Required Non-Tech Editing Surfaces

Create these files early, even if some values start as placeholders:

| File | Purpose | Non-Tech Editing Rule |
|---|---|---|
| `gameplay.config.ts` | Turn rules, miss limits, Stand countdown, hand limits, wildcard behavior | Values must use plain names and short comments |
| `physics.config.ts` | ball size, friction, restitution, shot power, pocket capture, table dimensions | Every value must explain whether bigger means easier, faster, or stronger |
| `ai.config.ts` | AI aim error, risk tolerance, scoring weights, search depth | Difficulty presets should be editable without reading AI code |
| `scoring.config.ts` | poker rank labels, display names, help examples | Do not alter poker math here unless explicitly intended |
| `layout.config.ts` | HUD placement, card sizes, mobile breakpoints, drawer sizes | Layout values should be grouped by desktop/tablet/mobile |
| `theme.css` | colors, fonts, shadows, spacing, motion tokens | Use CSS variables with readable names |
| `assets/manifest.ts` | sprites, atlases, audio, UI icons, card faces | Use stable keys such as `card.hearts.A`, not filenames in game code |
| `content/tutorialSteps.ts` | FTUE text and step order | Tutorial copy should be editable without touching systems |
| `content/rulesHelp.ts` | info panel copy for rules and poker ranks | Keep help text centralized |
| `docs/TUNING.md` | plain-language tuning guide | Explain common tweaks and safe ranges |
| `docs/ASSET_SWAP_GUIDE.md` | asset replacement guide | Show exact manifest keys and expected dimensions |

### 23.4 Tweakable Gameplay Variables

Expose at least these variables:

- `missLimit`
- `standResponseTurns`
- `maxHandSize`
- `wildcardCount`
- `breakRequiresRailContacts`
- `breakRequiredRailContactCount`
- `duplicateCardsAllowed`
- `allowLagShot`
- `allowVoluntaryEndTurn`
- `allowStandOnlyAtTurnStart`

Default expected values:

- `missLimit = 3`
- `standResponseTurns = 3`
- `maxHandSize = 5`
- `wildcardCount = 2`
- `breakRequiresRailContacts = true`
- `breakRequiredRailContactCount = 4`
- `duplicateCardsAllowed = false`
- `allowLagShot = false`
- `allowVoluntaryEndTurn = true`
- `allowStandOnlyAtTurnStart = true`

### 23.5 Tweakable Physics and Feel Variables

Expose at least these variables:

- `tableWidth`
- `tableHeight`
- `ballRadius`
- `railRestitution`
- `ballRestitution`
- `feltFriction`
- `linearDamping`
- `maxShotPower`
- `minShotPower`
- `powerCurve`
- `aimLineLength`
- `objectBallPreviewLength`
- `pocketRadiusMultiplier`
- `pocketCaptureRadiusMultiplier`
- `pocketCaptureMaxAngle`
- `pocketCaptureMaxSpeed`
- `pocketCapturePullStrength`
- `respawnDropDurationMs`
- `physicsSettleVelocityThreshold`
- `physicsSettleTimeMs`

Every value must include a comment with:

- Recommended range.
- What happens when the value increases.
- Whether it is safe to change mid-match or only before match start.

Example:

```ts
export const physicsConfig = {
  // Bigger = easier pocketing. Safe range: 1.35-1.6. Read at match start.
  pocketRadiusMultiplier: 1.45,

  // Bigger = stronger pocket assist once a ball enters the capture zone.
  // Safe range: 0.08-0.22. Too high feels magnetic.
  pocketCapturePullStrength: 0.14,
};
```

### 23.6 Tweakable UI, Layout, and Accessibility Variables

Expose at least these variables:

- HUD card size for desktop/tablet/mobile.
- Top and bottom HUD heights.
- Rules drawer width.
- Mobile rules sheet height.
- Power meter size.
- Aim line color and thickness.
- Valid, invalid, unclaimed, and wild pocket colors.
- Font family and scale tokens.
- Animation duration tokens.
- Reduced-motion multipliers.
- Minimum touch target size.
- Safe-area padding.

Use CSS variables for theme values:

```css
:root {
  --color-felt: #1f6f4a;
  --color-pocket-valid: #34c759;
  --color-pocket-invalid: #ff453a;
  --color-pocket-wild: #f6c945;
  --hud-card-size: 64px;
  --motion-fast: 140ms;
}
```

### 23.7 Asset Manifest Rules

All assets must be referenced through manifest keys.

Good:

```ts
assets.cards["hearts.A"]
assets.audio["card.flip"]
assets.ui["icon.rules"]
```

Avoid:

```ts
"/assets/cards/AH.png"
"../../Kenney/Some Folder/card_heart_A.png"
```

Manifest entries should include:

- `key`
- `path`
- `type`
- `defaultSize`
- `usage`
- `replaceable`
- `notes`

The asset swap guide must document:

- Required image dimensions.
- Transparent background expectations.
- Naming conventions.
- How to replace table, balls, cards, icons, audio, and UI panels.
- How to verify the asset loaded correctly.

### 23.8 Debug and Tuning Panel

Development builds must include a debug/tuning panel. It may be hidden behind a keyboard shortcut such as backtick.

Required controls:

- Pocket radius multiplier.
- Pocket capture radius multiplier.
- Pocket capture pull strength.
- Shot power multiplier.
- Felt friction.
- Ball restitution.
- Aim-line length.
- AI difficulty preset.
- AI aim error.
- Animation speed multiplier.
- Audio volume groups.
- Toggle pocket validity labels.
- Toggle physics body overlay.
- Force specific phase.
- Deal test hands.
- Trigger Stand countdown.
- Trigger Showdown.

Panel rules:

- Debug panel must never be shown in public production builds unless explicitly enabled.
- Tweaks should update live when safe.
- Values that require a restart or new match must say so.
- Include a reset-to-defaults button.
- Include a copy-current-config button for easy sharing.

### 23.9 Documentation Requirements

Create `docs/TUNING.md` with:

- "Make shots easier" recipe.
- "Make matches shorter" recipe.
- "Make AI easier/harder" recipe.
- "Adjust mobile HUD size" recipe.
- "Swap card art" recipe.
- "Replace audio" recipe.
- Safe ranges for common values.
- A warning list of values that can break rule integrity.

Create `docs/ASSET_SWAP_GUIDE.md` with:

- Asset folders and manifest keys.
- Required dimensions and formats.
- Example before/after manifest entry.
- Screenshot checklist after replacing assets.

### 23.10 Acceptance Criteria

- A non-technical designer can adjust pocket forgiveness, shot power, AI difficulty, HUD scale, and colors without reading Phaser scene code.
- A non-technical designer can swap card, ball, table, icon, and audio assets by editing the manifest and following the asset guide.
- A developer can run unit tests after config changes and know whether rules still pass.
- No designer-facing value is duplicated in multiple files.
- Every tuning value has one source of truth.

## 24. Implementation State Model

Suggested top-level state:

```ts
type Suit = "spades" | "hearts" | "diamonds" | "clubs";
type Phase = "break" | "suit-mapping" | "hand-race" | "stand-countdown" | "showdown" | "game-over";

interface Card {
  rank: "A" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" | "10" | "J" | "Q" | "K";
  suit: Suit;
}

interface PocketState {
  id: string;
  kind: "unclaimed" | "suit" | "wild";
  suit?: Suit;
}

interface GameState {
  phase: Phase;
  players: [PlayerState, PlayerState];
  activePlayerIndex: 0 | 1;
  pockets: PocketState[];
  balls: BallState[];
  stand?: {
    declarerIndex: 0 | 1;
    responderTurnsRemaining: number;
  };
}
```

Important implementation rules:

- Keep physics state and rules state separate.
- Emit pocket events from physics; resolve game rules only after all balls settle.
- Make rule resolution deterministic and unit-testable without rendering.
- Derive pocket validity from `GameState`, active player, ball id, and pocket id.

## 25. Testing Checklist

This checklist is cumulative. Apply each test when the related system enters the milestone scope.

Unit tests:

- Suit claiming assigns each suit once.
- Wildcards cannot claim suits before Phase 2.
- Wild Holes appear after exactly four suits are claimed.
- Duplicate exact cards are invalid.
- Valid plus invalid same-shot pockets count as success.
- Scratch overrides all other pocket events.
- Rank balls respawn after valid registration.
- Wildcards are removed after valid registration.
- Swap decision always leaves exactly five cards.
- Stand countdown ends early when responder reaches five cards.
- 3 misses eliminates immediately.
- Poker comparison handles kickers and ace-low straights.
- FTUE can be completed, skipped, and replayed.
- Rules panel opens without changing game state.
- Designer config files load and validate.
- Asset manifest rejects missing keys and invalid paths.
- Debug panel changes safe tuning values without corrupting match state.

Integration tests:

- Break pocketed balls respawn and do not claim suits.
- Full match can reach Showdown.
- Player can win by elimination.
- Player can win by Stand-triggered showdown.
- Mobile viewport keeps table, hands, and action controls usable.

## 26. Development Milestones

Build Poker Pool in three clear milestones. Each milestone should be playable, testable, and shippable to a small audience before moving on.

### 26.1 Milestone 1: Local Playable Prototype

Goal: prove the core rules and feel with a complete local 2-player match.

Player-facing scope:

- Local pass-and-play 1v1 on one device.
- Aim + power shot controls.
- Forgiving pocket geometry.
- Basic top-down table, balls, pockets, and labels.
- Coin-flip breaker selection.
- Suit Mapping, Hand Race, card registration, respawn, swap, Stand, showdown, and 3-miss elimination.
- Minimal HUD showing both hands, active player, miss pips, phase, and pocket suit labels.
- Rules panel with How To Play, Poker Ranks, Pocket Rules, and Controls tabs in simple form.

Technical scope:

- Phaser 3 + Matter physics scaffold.
- Pure TypeScript rules engine separated from Phaser scene code.
- Deterministic shot-resolution event pipeline.
- Designer-friendly config files for core gameplay, physics, layout, and assets.
- Basic asset manifest with placeholder or simple Kenney assets.
- Unit tests for core rule resolution.
- Debug toggles for pocket size, pocket capture strength, shot power, and rules events.

Exit criteria:

- Two local players can complete a match from break to win screen.
- No rule-blocking bugs in card registration, swap, Stand, or showdown.
- Pocket feel is forgiving enough for non-pool players to intentionally make shots.
- A coder can run the game locally and understand the architecture.
- A non-technical collaborator can tune pocket forgiveness and shot power from config files.

### 26.2 Milestone 2: Juiced Prototype With AI and Production Assets

Goal: make the prototype fun to replay alone and good enough to show publicly.

Player-facing scope:

- Single-player vs AI opponent.
- Local 2-player remains available.
- Improved visual identity: polished table, pocket states, card balls, wildcard balls, hand cards, and menus.
- Game juice pass: pocket animations, respawn animation, card flip, suit-claim celebration, Stand countdown, showdown reveal, win/loss feedback.
- Full audio pass for collisions, pocketing, card registration, UI confirms, warnings, showdown, and victory.
- Improved rules panel with examples and readable poker-rank cards.
- Settings for audio, reduced motion, and pocket-assist strength.

AI opponent scope:

- AI chooses shots using simple tactical scoring, not perfect physics search.
- Inputs: current hand, opponent hand, pocket map, available ball-pocket lanes, miss risk, Stand state.
- Priorities: complete stronger hands, deny obvious opponent improvements, avoid third miss, use wildcard when it improves expected hand rank.
- AI difficulty can be tuned by aim error, candidate search depth, and risk tolerance.

Technical scope:

- Asset manifest finalized around Kenney assets plus programmatic ball/table overlays.
- Asset swap guide written for cards, balls, table, UI icons, and audio.
- AI decision module separated from rules engine and renderer.
- Shot helper that estimates candidate lines and power.
- Playtest telemetry hooks for match length, miss frequency, Stand timing, and win condition.
- Expanded integration tests for AI turns and game-state transitions.

Exit criteria:

- A solo player can play a complete satisfying match against AI.
- Match presentation feels lively without obscuring the playfield.
- AI appears purposeful at beginner/intermediate level.
- Visual/audio assets are cohesive enough for a trailer-style capture or demo page.
- A non-technical collaborator can swap major visual/audio assets through the manifest.

### 26.3 Milestone 3: Polished Online Game

Goal: ship a complete onboarding and multiplayer-ready version.

Player-facing scope:

- Full FTUE with guided tutorial, contextual hints, skip, and replay.
- Real online multiplayer with random matchmaking.
- AI backup if no human opponent is found within 15 seconds.
- Rematch flow.
- Connection status, reconnect handling, and clean forfeit/timeout states.
- Polished menus: title, mode select, tutorial, settings, credits, matchmaking, pause, results.
- Final responsive pass for desktop, tablet, and phone.

Multiplayer scope:

- Random matchmaking queue.
- 15-second matchmaking timer.
- If matched: start PvP game.
- If no opponent found after 15 seconds: offer instant AI match or automatically start AI match, depending on product preference.
- Server-authoritative rules state for online matches.
- Client-side prediction is allowed only for aiming preview and local animation, not final rule outcomes.
- Turn timers and inactivity handling.
- Basic anti-desync validation for pocket events and resolved game state.

Technical scope:

- Network layer with authoritative match state.
- Serialization format for rules state, shot input, pocket events, and match results.
- Lobby/matchmaking service.
- AI service or local AI fallback that can replace a missing opponent.
- Save player preferences and FTUE completion.
- Error handling, analytics, and crash reporting.
- Browser QA matrix across desktop and mobile.

Exit criteria:

- New players can learn through FTUE and finish a first match without external explanation.
- Random matchmaking reliably starts PvP when an opponent is available.
- AI backup starts within the 15-second no-match window.
- Online match state remains synchronized across normal play, reconnects, forfeits, and endgame.
- Game has final-feeling UX polish, audio, visual feedback, and responsive layout.
