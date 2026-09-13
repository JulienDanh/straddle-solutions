---
system: BM1
title: ICM vs ChipEV Preflop
type: preflop-icm
course: Bubble Mastery
scenario: How ICM adjusts preflop ranges from ChipEV baseline on the bubble.
source_files:
  - transcripts/Bubble Mastery/Bubble_Mastery_04_Preflop_Bubble_Adjustments_Preflop_Bubble_Adjustments_-_ICM_Adjusted_vs_Chips_without_Takeaways.txt
  - transcripts/Bubble Mastery/Bubble_Mastery_04_Preflop_Bubble_Adjustments_Takeaways.txt
stack_depth: 10-100bb
---

# BM1 — ICM vs ChipEV Preflop

## Overview
How ICM adjusts preflop ranges from the ChipEV baseline. Opens tighten around marginal hands, 3-bets become more polar and blocker-heavy, cold calling fades at shorter stacks. The directional shift from ChipEV is the lesson.

## Buckets
- **Opens**: Tighten around marginal suited hands, lower pairs, offsuit broadways. Open more with ace-blocker hands (Ax, Kx suited) to block 3-bet bluffs.
- **3-bets**: More polar. Drop queens from value range (kings+, maybe queens). Bluffs shift from board-coverage hands to blocker-heavy (Kx, Ax suited).
- **Cold calls**: Fade aggressively at shorter stacks. Calling 2bb off 20bb is much riskier than off 40bb.

## Decision Rules
- **Opens tighten**: Drop the weakest suited hands (T9s, J9s type), lower pairs (22-44 in some configs), weakest offsuit broadways. Add more Ax/Kx suited (blocker opens).
- **3-bet value narrows**: Kings+, AK (queens mix) instead of JJ+/AQ. More polar.
- **3-bet bluffs shift to blocker-heavy**: K4s, K5s, A6s, A7s — hands that block opponent's 3-bet attack range (ace blockers).
- **Cold calling fades below ~20bb**: Calling 2bb off 20bb risks too much equity. Mostly 3-bet-fold. At 40bb+, some cold calls return.
- **Higher bubble pressure = more IP bluffing**: In equal-stack models, IP can bluff more (game of chicken). Higher pressure (152 left, 150 paid) > lower pressure (33 left, 30 paid).

## Risk Factors
| Factor | Effect |
|--------|--------|
| Shorter stacks | Cold calling fades faster — risking larger % of stack |
| Higher bubble pressure (152/150) | More IP bluffing, tighter EP defense |
| Covered by heaps | Tighten opens substantially — villain can destroy you postflop |
| Covering the table | Can open wider — pressure on others |

## Sizing
- Open smaller: 2.1x (ICM) vs 2.3x (ChipEV) on BTN
- 3-bet smaller: 7.35bb (ICM) vs 8.6bb (ChipEV) from SB vs BTN
- Larger 3-bet sizing from BB — deny equity, lower SPR for narrow value range

## Heuristics
- "Opens tighten around the margins; add blocker opens"
- "3-bets get polar — drop queens, add Kx/Ax suited bluffs"
- "Cold calling fades at short stacks"
- "Higher bubble pressure = more IP bluffing"

## Rules Q&A
- Q: What happens to 3-bet value ranges in ICM vs ChipEV?
  Options: [Narrows — drop queens, kings+ becomes the threshold, Widens — add jacks, No change, Only aces]
  Correct: 0
  Explanation: ICM 3-bet value is kings+, AK (queens mix). Much more polar than ChipEV (JJ+, AQ).
- Q: What type of hands become more valuable as opens in ICM?
  Options: [Ace-blocker hands (Ax, Kx suited) — block 3-bet bluffs, Suited connectors, Low pairs, Offsuit broadways]
  Correct: 0
  Explanation: Blocking the opponent's 3-bet attack range is more important than board coverage. Ax/Kx suited opens block ace-high 3-bet bluffs.
- Q: What happens to cold calling at shorter stacks in ICM?
  Options: [Fades aggressively — calling 2bb off 20bb is too risky, Increases, No change, Only call with premium hands]
  Correct: 0
  Explanation: Calling 2bb off 20bb risks 10% of your stack preflop. A c-bet puts in 30%+ before the river. Too risky near the bubble.

## Source Quotes
- "opens tighten up around the marginal suited hands, lower pairs and offsuit broadways"
- "we open more with ace-axe blockers"
- "the value threshold for three-betting tightens... we commonly drop queens"
- "three bet bluffs will tend to come from a more blocker heavy range"
- "cold calling starts fading away more aggressively at shorter stacks"

## Cross-References
- BM-Primer: ICM & FGS Foundations (the models behind these adjustments)
- Primer (NLH): RFI perimeters (the ChipEV baseline)
- BM2-BM5: Specific preflop adjustments by stack configuration
