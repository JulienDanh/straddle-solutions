---
system: BM-Primer
title: ICM & FGS Foundations
type: primer
course: Bubble Mastery
source_files:
  - transcripts/Bubble Mastery/Bubble_Mastery_02_The_ICM_Model_The_ICM_Model_-_Application_to_Bubble.txt
  - transcripts/Bubble Mastery/Bubble_Mastery_03_Demonstration_of_FGS_on_Bubble_ICM_FGS_with_HRC_Pro_without_Takeaways.txt
  - transcripts/Bubble Mastery/Bubble_Mastery_03_Demonstration_of_FGS_on_Bubble_Takeaways.txt
  - transcripts/Bubble Mastery/Bubble_Mastery_04_Preflop_Bubble_Adjustments_Preflop_Bubble_Adjustments_-_ICM_Adjusted_vs_Chips_without_Takeaways.txt
  - transcripts/Bubble Mastery/Bubble_Mastery_04_Preflop_Bubble_Adjustments_Takeaways.txt
stack_depth: 10-100bb
---

# ICM & FGS Foundations

## Overview
The conceptual framework for bubble play. Three models: ChipEV (linear chips = equity), ICM (stack-relative equity, doubling ≠ double equity), FGS (ICM + future hands). The bubble is where these models diverge most from ChipEV.

## Key Concepts
- **ChipEV**: Chips scale linearly. $1 of chips = $1 of equity. Good for early game/cash. Doubling your stack doubles your equity.
- **ICM**: Chips do NOT scale linearly. Doubling your stack does NOT double your equity. A $100 buy-in doubled to 10,000 chips is worth ~$195, not $200. The bubble is where ICM matters most.
- **FGS (Future Game Simulation)**: ICM + N future hands. Captures blind cycles, forced all-ins, who busts next. Limited to single-table. Cannot run multi-table.
- **Hierarchy**: ICM is the baseline → FGS tells you the DIRECTION to deviate → table/stack/position logic tells you the MAGNITUDE.
- **ICM pitfalls**: No skill edge, no future hands, no position/blind accounting, computational breakdown at scale (50-500+ players → output may be 10-15% off).
- **Study approach**: Study the two extremes (ChipEV and direct bubble) with ~40% each, ~20% in the middle. Everything stems from the extremes.

## Decision Rules
- **Stack situation × model**: The directional shift is the lesson.
  - Short stack, posts BB next (4.5bb): ICM shove ~18% → FGS shove ~25% (wider — blind cost + fold equity now)
  - Ultra-short, forced all-in next (1.5bb): ICM shove ~49% → FGS shove ~25% (tighter — no fold equity, doubling doesn't help)
  - 15bb HJ, shorter stack at table: ICM allows some open shoves → FGS min-raise only (no shoves — preserve tournament life, open shove loses ~$18-35)
- **Preflop bubble adjustments**: ICM tightens ranges vs ChipEV. Open smaller, defend tighter, 3-bet smaller. The degree depends on stack configuration (covered vs covering).
- **FGS deviations**: When FGS says deviate from ICM, the direction is: shove WIDER when you post blinds soon (blind cost), shove TIGHTER when you're forced all-in next (no fold equity).

## Sizing
- BTN open: 2.1x (ICM) vs 2.3x (ChipEV) — smaller open in ICM
- SB 3-bet vs BTN: 7.35bb (ICM) vs 8.6bb (ChipEV) — smaller 3-bet, yet defense still tighter
- Cost of posting BB+ante: ~-112bb/100 — why short stacks should shove before the blind hits

## Heuristics
- "Doubling your stack does not double your equity"
- "ICM is the baseline → FGS gives direction → table logic gives magnitude"
- "Study the extremes: ChipEV and direct bubble"
- "FGS: wider when blinds are coming, tighter when forced all-in"
- "Folding is not zero EV on the bubble"

## Rules Q&A
- Q: What does ICM mean for chip equity?
  Options: [Doubling your stack does not double your equity, Chips scale linearly, Equity is always 1:1 with chips, ICM doesn't affect equity]
  Correct: 0
  Explanation: Under ICM, chips do not scale linearly. Doubling from 5,000 to 10,000 chips might take you from $100 to $195, not $200.
- Q: What does FGS add beyond ICM?
  Options: [Future hands — blind cycles, forced all-ins, who busts next, Nothing, Only skill edge, Only position]
  Correct: 0
  Explanation: FGS = ICM + N future hands. It captures the cost of posting blinds, the benefit of others busting before you, and forced all-in situations.
- Q: What is the hierarchy for applying these models?
  Options: [ICM baseline → FGS direction → table logic magnitude, FGS first then ICM, ChipEV only, Table logic only]
  Correct: 0
  Explanation: ICM gives the baseline strategy. FGS tells you which direction to deviate. Table/stack/position logic tells you how much to deviate.
- Q: What happens to your shove range when you post BB next (4.5bb) under FGS?
  Options: [Wider — blind cost + fold equity now, Tighter, No change, Fold everything]
  Correct: 0
  Explanation: FGS says shove ~25% vs ICM's ~18%. The blind cost (~112bb/100) plus having fold equity now means you should shove wider.
- Q: What happens to your shove range when you're forced all-in next (1.5bb) under FGS?
  Options: [Tighter — no fold equity, doubling doesn't help, Wider, No change, Shove everything]
  Correct: 0
  Explanation: FGS says shove ~25% vs ICM's ~49%. No fold equity (you're called regardless), and doubling doesn't help your equity much. Fold and let others bust.
- Q: What is a key ICM pitfall?
  Options: [No skill edge, no future hands, no position/blind accounting, computational breakdown at scale, All of the above, None of the above]
  Correct: 3
  Explanation: ICM doesn't account for skill edge, future hands, or position. It also breaks down computationally with 50-500+ players (output may be 10-15% off).

## Source Quotes
- "chips do not scale linearly... doubling your stack does not double your equity"
- "ICM does not account for skill edge... does not factor in future hands... does not factor in incoming blinds or positions"
- "FGS model aims to capture future hands into the ICM equation"
- "ICM is a reference point, and then we apply logic to what sort of deviation or adjustment we make"
- "when you get below 35 big blinds, the nature of the check raising range changes"
- "the cost of posting BB+ante is approximately -112bb per 100"
- "open shoving 15bb on the bubble with a shorter stack present is a massive leak"

## Cross-References
- BM1: ICM vs ChipEV Preflop (applying these models to preflop ranges)
- BM2-BM6: Preflop systems built on ICM/FGS foundations
- BM7: Identifying Bubble Impact (when ICM pressure is highest)
- Primer (No-Limit Systems): RFI perimeters (the ChipEV baseline these adjust from)
