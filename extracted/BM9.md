---
system: BM9
title: BB Covers BTN (Postflop)
type: postflop-icm
course: Bubble Mastery
scenario: BB covers BTN on the bubble. BB leads more; BTN c-bets less.
source_files:
  - transcripts/Bubble Mastery/Bubble_Mastery_13_Postflop_BB_Covers_BTN_Play_and_Explain_-_BB_Defense.txt
  - transcripts/Bubble Mastery/Bubble_Mastery_13_Postflop_BB_Covers_BTN_Play_and_Explain_-_BTN.txt
  - transcripts/Bubble Mastery/Bubble_Mastery_13_Postflop_BB_Covers_BTN_Takeaways.txt
  - transcripts/Bubble Mastery/Bubble_Mastery_14_Postflop_BB_Covers_BTN_-_BTN_C-betting_Intro_Overview.txt
  - transcripts/Bubble Mastery/Bubble_Mastery_14_Postflop_BB_Covers_BTN_-_BTN_C-betting_Play_and_Explain_-_BTN_C-Betting.txt
  - transcripts/Bubble Mastery/Bubble_Mastery_14_Postflop_BB_Covers_BTN_-_BTN_C-betting_Takeaways.txt
stack_depth: 20-100bb
positions: [BB, BTN]
street: flop, turn, river
---

# BM9 — BB Covers BTN (Postflop)

## Overview
BB covers BTN on the bubble. The covering stack (BB) leads much more on low boards and pair boards — near pure lead on boards BTN misses. BTN c-bets less than ChipEV. Sizing down on turns/rivers for the covered stack. Non-all-in river sizings.

## Buckets
- **BB leads (covering)**: Much more prevalent on low boards and pair boards. Near pure. Small amount of leads on J64, J75, Q76 type boards. BB's range hits these; BTN's doesn't.
- **BTN c-bets (covered)**: Lower frequency than ChipEV. Fewer boards range bet. ICM amplifies risk factors.
- **BTN checks back more**: Develop check ranges on boards where BB leads or where risk factors are amplified.

## Decision Rules
- **BB leads low/pair boards**: Much higher frequency than ChipEV. Near pure on boards BTN misses. Why bet? BB's preflop range connects; BTN's doesn't.
- **BB leads some mid boards**: Small amount on J64, J75, Q76 type. Not range, but present.
- **BTN c-bet frequency drops**: Fewer boards range bet. The ones that really connect with BTN open range still lean range bet.
- **Sizing down on turns/rivers**: Covered stack uses smaller sizings to reduce risk.
- **Non-all-in river sizings**: Leave tournament equity behind. Stay balanced — same sizing for value and bluffs.
- **Blocker awareness in bluff catching**: When opponent's float range is narrow (donking and getting called), suit nuances matter more. Bluff catching the river with the correct suits vs folding.
- **ICM amplifies risk factors**: Any risk factor present in chips gets amplified. Monotone, connectedness, flush draws — all increase checking.

## Risk Factors
| Factor | Effect |
|--------|--------|
| BB covering (leads more) | BTN c-bet frequency drops — BB hits low/pair boards |
| Monotone flops | More checking back vs ChipEV |
| Flush draw presence | Increases checking and jam sizing frequency |
| Paired boards (not 886) | More checking |
| Connectedness / draws | More checking |
| ICM pressure | Amplifies ALL risk factors vs ChipEV |

## Sizing
- BB leads: standard sizing on low/pair boards
- BTN (covered): size down on turns/rivers
- River: non-all-in sizings (leave equity behind, stay balanced)

## Common Leaks
- BTN c-betting too much on boards where BB leads
- Not recognizing that BB's lead frequency is much higher than ChipEV
- Shoving river with nuts and raising non-all-in with bluffs (exploitable)
- Not paying attention to suit nuances when bluff catching with narrow ranges

## Heuristics
- "BB covers = BB leads more on low/pair boards"
- "BTN covered = c-bet less, check more"
- "ICM amplifies ALL risk factors"
- "Size down on turns/rivers when covered"
- "Non-all-in river sizings — stay balanced"
- "Blocker nuances matter more when float ranges are narrow"

## Rules Q&A
- Q: What changes about BB's leading frequency when BB covers BTN?
  Options: [Much more prevalent on low/pair boards — near pure, Less leading, No change, Only leads high boards]
  Correct: 0
  Explanation: BB's preflop range connects with low/pair boards; BTN's doesn't. BB leads at a much higher frequency than ChipEV — often pure.
- Q: What happens to BTN's c-bet frequency when covered by BB?
  Options: [Lower than ChipEV — fewer boards range bet, Higher, No change, BTN never c-bets]
  Correct: 0
  Explanation: ICM amplifies risk factors for the covered stack. BTN c-bets less, checks more. Only boards that really connect with BTN's range still lean range bet.
- Q: How does ICM affect risk factors postflop?
  Options: [Amplifies ALL risk factors — any risk factor in chips gets worse in ICM, Reduces them, No effect, Only affects preflop]
  Correct: 0
  Explanation: Monotone, connectedness, flush draws, paired boards — all increase checking more in ICM than in ChipEV. The sensitivity is higher.
- Q: What sizing should the covered stack use on turns and rivers?
  Options: [Size down — reduce risk. Use non-all-in sizings on river, Size up, Pot-sized, All-in]
  Correct: 0
  Explanation: Covered stack sizes down to reduce risk. Non-all-in river sizings leave tournament equity behind when called and losing.

## Source Quotes
- "leading is more prevalent now on low boards and pair boards... much higher than ChipEV model"
- "in position CBET frequency is going to be lower than the ChipEV model"
- "any risk factor that's present in chips just gets amplified in the ICM model"
- "sizing down... use non-all-in sizings on river"
- "be mindful of blockers and bluff catching... specific suit nuances"
- "do not be arrogant... keep your sizing the same"

## Cross-References
- BM8: BTN Covers BB (Postflop) — the reverse stack configuration
- S2: BTN vs BB C-bet (ChipEV — the baseline)
- S9: Defending Flops (ChipEV defense — the baseline for BB)
- BM-Primer: ICM & FGS Foundations (why ICM amplifies risk factors)
