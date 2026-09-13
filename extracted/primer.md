---
system: Primer
title: Preflop Primer — RFI, BB Defense, 3-Betting
type: primer
course: No-Limit Systems
source_files:
  - transcripts/Simple Poker Systems/Simple_Poker_Systems_02_Pre-Flop_Lessons_Raise_First_In_(RFI).txt
  - transcripts/Simple Poker Systems/Simple_Poker_Systems_02_Pre-Flop_Lessons_vs._RFI.txt
  - transcripts/Simple Poker Systems/Simple_Poker_Systems_02_Pre-Flop_Lessons_3-Betting_vs_Steals.txt
stack_depth: 10-40bb
---

# Preflop Primer — RFI, BB Defense, 3-Betting

## Overview
Foundation for all postflop systems. Core skill: memorize the perimeter (bottom) of preflop ranges. If you know the bottom, you know the top. Three areas: raise first in (RFI), big blind defense, and 3-betting vs steals.

## Key Concepts
- **Perimeter memorization**: Focus on the bottom of every range. You won't open A2o and fold A2o — if you know the weakest hand in the range, you know everything above it is in
- **Metagame bias**: In most low-to-mid-stakes games, villains under-invest — they don't 3-bet enough, don't call enough, don't check-raise enough. Bottom of RFI ranges is more profitable than solver suggests
- **Suited hands are resilient**: Suited combos are far less sensitive to sizing and position than offsuit. Offsuit combos are enormously sensitive — they come out vs larger sizes and vs earlier positions
- **3-betting from blinds**: Tend to be relatively linear (emanates downward from best hands). Key variable: make the bottom of the opener's range available to fold — stay away from the opener's automatic fold cards

## Decision Rules
- **RFI perimeters (40bb):**
  - BTN: Suited 5s+, Q2s+, J3s+, A2s+, K6s+, T8o+, A2o+, K6o+, Q7o+, 22+ — offsuit 8s are the backbone
  - CO: Suited 6s+, Q4s+, K2s+, T9o+, A5o, A7o+, 22+ — offsuit 9s are the backbone
  - HJ: Suited 7s+, K4s+, A8o+, ATo+, KJo+, 33+ — offsuit Ts are the backbone
  - UTG: A3s+, Q9s+, 55+, ATo+, KJo+, QJo+ (mix)
- **BB defense perimeters (40bb):**
  - vs BTN (2.3x): Offsuit 6s+, all suited, Q2o+
  - vs UTG (same size): Offsuit 9s+ floor, nearly all suited in
- **3-bet vs BTN (SB):** Linear from best hands. Include hands with a 7 (Q7s, T7s, 97s) to make offsuit 8s available to fold. Stay away from 8s and 9s.
- **3-bet vs CO (SB):** Same principle — make offsuit 9s available to fold. Prefer A8s, Q8s, J8s, T8s, T7s over offsuit 9s.
- **3-bet vs BTN (BB):** Stay away from 8s and 9s. Prefer A7s, J7s, A6s, 96s, T6s, K5s, K4s, Q4s. Fade offsuit 9s for board coverage reasons but keep a few.
- **Short stack adjustment:** At shorter stacks, suited connectors deteriorate and offsuit ace-high hands become more competitive. At deeper stacks, offsuit aces are more challenged.

## Sizing
- BTN open: 2.3x (ChipEV baseline)
- 3-bet sizes are narrower at shorter stacks — don't 3-bet-fold hands that are too good

## Heuristics
- "Memorize the perimeter, not every combo"
- "One pip higher per position" (BTN offsuit 8s → CO offsuit 9s → HJ offsuit Ts)
- "Suited hands are resilient; offsuit hands are sensitive"
- "Table size matters — 7-handed vs 8-handed changes UTG+1 ranges"

## Rules Q&A
- Q: What is the backbone of the BTN RFI range?
  Options: [Offsuit 8s and suited 5s, Offsuit 9s and suited 6s, Offsuit Ts and suited 7s, Suited connectors only]
  Correct: 0
  Explanation: BTN backbone is offsuit 8s and suited 5s. CO is one pip higher (offsuit 9s, suited 6s). HJ is one pip higher again (offsuit Ts, suited 7s).
- Q: What happens to suited connectors at shorter stacks?
  Options: [They deteriorate — offsuit aces replace them, They get stronger, No change, They become folds]
  Correct: 0
  Explanation: Suited connectors deteriorate at shorter stacks. Offsuit ace-high hands become more competitive and replace them.
- Q: When 3-betting from the SB vs BTN, what should you try to make available?
  Options: [The bottom of BTN's range (offsuit 8s) to fold, The top of BTN's range to call, Mid pairs to fold, Suited connectors to fold]
  Correct: 0
  Explanation: The first hands BTN folds vs a 3-bet are offsuit 8s. Include hands with a 7 (Q7s, T7s) to make those folds available. Stay away from 8s and 9s.
- Q: Which combos are more sensitive to sizing and position?
  Options: [Offsuit combos, Suited combos, Pocket pairs, All equally sensitive]
  Correct: 0
  Explanation: Offsuit combos are enormously sensitive. Suited combos are resilient. Vs min-raise: more offsuit. Vs 2.5x: offsuit comes out. Vs EP: offsuit floor rises.
- Q: What is the BB defense floor vs UTG at 40bb?
  Options: [Offsuit 9s, nearly all suited, Offsuit 6s, all suited, Offsuit Ts only, All hands]
  Correct: 0
  Explanation: vs UTG (same size): offsuit 9s+ floor, nearly all suited in. Only 72s is clearly below zero.

## Source Quotes
- "focus on memorizing the perimeter of the range"
- "the bottom of the range will tend to be more profitable as raised first in than a solver would suggest"
- "as we move one position over, we move one pip higher"
- "offsuit combos are enormously sensitive to sizing and position — suited combos are resilient"
- "the first hands the button will fold versus a three bet will be the bottom of that range"
- "queen seven suited makes those weakest raise first ins available to fold"

## Cross-References
- S1-S12: All postflop systems depend on knowing these preflop ranges
- BM Primer: ICM adjustments to these same preflop ranges on the bubble
