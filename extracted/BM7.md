---
system: BM7
title: Identifying Bubble Impact
type: preflop-icm
course: Bubble Mastery
scenario: How to identify and quantify bubble impact on your decisions.
source_files:
  - transcripts/Bubble Mastery/Bubble_Mastery_10_Identifying_Bubble_Impact_HRC_Pro_Testing.txt
  - transcripts/Bubble Mastery/Bubble_Mastery_10_Identifying_Bubble_Impact_Identifying_Bubble_Impact.txt
  - transcripts/Bubble Mastery/Bubble_Mastery_10_Identifying_Bubble_Impact_Takeaways.txt
stack_depth: 10-100bb
---

# BM7 — Identifying Bubble Impact

## Overview
How to identify and quantify bubble impact. The core skill: express players-left-to-bubble as a percentage of field, weigh table stacks vs other-table stacks, and apply FGS logic (even when you can't run multi-table FGS). Player tendencies overlay last.

## Buckets
- **Players left to bubble**: Express as % of field. 3 left out of 30 is very different from 3 left out of 3,000.
- **Short stack ranges**: Impacted MORE by bubble adjustments — 1-2% range shift on single-digit open frequencies is a large % of your stack.
- **Large stack ranges**: Impacted less — risking more chips is less detrimental to tournament position. Same 1-2% shift on mid-double-digit frequencies is a smaller % of stack.

## Decision Rules
- **Express bubble distance as % of field**: 3 players left to bust out of 30 (9.1%) vs 3 out of 3,000 (0.1%). Higher % = moderate pressure. Lower % = extreme pressure.
- **Short stack precision matters more**: Getting short stack ranges correct is more impactful to your bottom line. A mistake on a 9% open = 10-20% of your stack. A mistake on a 35% open = a couple % of your stack.
- **Weigh multi-table stacks**: Your table stacks are not the complete picture. Other tables, relative positions, and who's hitting blinds next all matter. ICM models don't account for positions at other tables — use FGS logic to get directional shifts correct.
- **Player tendencies overlay last**: Learn GTO baseline first. Then overlay tendencies. If you don't know where you should be, you can't exploit for what mistakes people are making.

## Risk Factors
| Factor | Effect |
|--------|--------|
| Higher bubble pressure (fewer players left as % of field) | More extreme adjustments |
| Short stacks at other tables | Tighten further — folding has positive $EV (FGS) |
| Position of stacks at other tables | Not factored by ICM — use FGS logic for direction |
| Your stack is the shortest | Loosen — can't rely on others busting |
| Large stack | Less impacted by bubble adjustments — mistakes cost smaller % of stack |

## Heuristics
- "Express players-left-to-bubble as % of field"
- "Short stack precision matters more to your bottom line"
- "Table stacks aren't the full picture — weigh other tables"
- "Player tendencies overlay last — learn GTO baseline first"
- "ICM doesn't factor positions at other tables — use FGS logic"

## Rules Q&A
- Q: How should you express players-left-to-bubble?
  Options: [As a percentage of field — 3 out of 30 is very different from 3 out of 3,000, As an absolute number, By minutes remaining, By blind level]
  Correct: 0
  Explanation: 3 players left out of 30 (9.1%) is moderate pressure. 3 out of 3,000 (0.1%) is extreme pressure. The % determines the magnitude of adjustments.
- Q: Why do short stack range adjustments matter more than large stack adjustments?
  Options: [A mistake on a 9% open costs 10-20% of your stack; on a 35% open it costs a couple %, Short stacks have more hands, Large stacks are always correct, It doesn't matter]
  Correct: 0
  Explanation: Getting short stack ranges correct is more impactful. A 1-2% range shift when opening single-digit frequencies is a large % of your stack.
- Q: What does ICM NOT account for that you must consider?
  Options: [Positions of stacks at other tables, who's hitting blinds next, Your hand strength, The pot size, Your position at the table]
  Correct: 0
  Explanation: ICM gives a snapshot of stack sizes. It doesn't factor in positions at other tables, blind cycles, or who gets to beat up on players. Use FGS logic for directional shifts.
- Q: When should you overlay player tendencies?
  Options: [Last — after GTO baseline, bubble distance, and stack analysis, First — before anything else, Never, Only in cash games]
  Correct: 0
  Explanation: Learn GTO baseline first. Then overlay tendencies. If you don't know the correct range, you can't know when a mistake becomes not a mistake.

## Source Quotes
- "be mindful of the number of players left till bubble bursting... express this as a percentage of field"
- "short stack ranges will be impacted greater than large stack ranges"
- "our table stack is just not the complete picture... we do have to be mindful of the other tables"
- "ICM is not factoring in these positions... we can at least play around with single table or final table and use those ideas"
- "player tendencies... I teach very much a learn GTO, learn the theory, learn the baseline ranges, and then overlay tendencies"

## Cross-References
- BM-Primer: ICM & FGS Foundations (the models behind bubble impact)
- BM1-BM6: All preflop systems affected by bubble impact identification
- BM8-BM11: Postflop systems where bubble impact changes c-bet/defense strategies
