---
system: BM8
title: BTN Covers BB (Postflop)
type: postflop-icm
course: Bubble Mastery
scenario: BTN (50bb) covers BB (20bb) on the bubble. How does postflop change?
source_files:
  - transcripts/Bubble Mastery/Bubble_Mastery_11_Postflop_BTN_Covers_BB_Play_and_Explain_with_GTOWizard_-_BTN_50BB_vs_BB_20BB.txt
  - transcripts/Bubble Mastery/Bubble_Mastery_11_Postflop_BTN_Covers_BB_Takeaways.txt
  - transcripts/Bubble Mastery/Bubble_Mastery_12_Postflop_BTN_Covers_BB_-_BU_C-Betting_Play_and_Explain_with_GTOWizard_-_BTN_C-Betting.txt
  - transcripts/Bubble Mastery/Bubble_Mastery_12_Postflop_BTN_Covers_BB_-_BU_C-Betting_Risk_Factors_BTN_C-Bet_Covering_BB.txt
stack_depth: 20-50bb
positions: [BTN, BB]
street: flop, turn, river
---

# BM8 — BTN Covers BB (Postflop)

## Overview
BTN (50bb) covers BB (20bb) on the bubble. ICM pressure amplifies risk factors for c-betting. The covered stack must be more cautious — reduce actions where marginal hands get stuck putting in chips. Protection is a real thing in tournaments.

## Buckets
- **Range bet boards**: High-card boards with an ace (AKQ, AKJ, AKT, AQT, AJT). These connect well with BTN's opening range. C-bet 100%.
- **Check-back boards**: AJ8 type (middling draws), queen-high, jack-high boards. Develop a check range. Monotone boards = high check (high risk for covered stack).
- **Overbet boards**: Boards with multiple gut shots (AQ2, Q84, J74 type). Use ~105% pot for protection/immediate value. NOT on open-ended or two-tone boards.

## Decision Rules
- **Range bet ace-high Broadway boards**: AKQ, AKJ, AKT, AQT, AJT — all range bets. AQJ has ~20% check but simplifying to range bet is fine.
- **Develop check range on middling boards**: AJ8 (middling draws) starts checking. Extends to K-high, Q-high, J-high boards.
- **Monotone = high risk for covered stack**: Back to checking. Very different from ChipEV where BTN covers BB (monotone gets c-bet a lot).
- **Overbet on multiple-gut-shot boards**: ~105% pot. Protection from draws + overcards. Removes hands from villain's check-call range, creating better turn value spots.
- **No overbet on open-ended or two-tone boards**: Only on boards with multiple gut shots where BB is not leading with open-enders.
- **Little to no leading on low/mid boards**: BB doesn't lead much. Check-shove low boards (strong, polar). Protection > inducing under ICM.
- **Check-call top pair on safe boards**: AQx, AKx — don't need protection (jammed strong hands preflop). Check-raise top pair when it CAN be outdrawn (Q-high, J-high boards).
- **Non-all-in river sizings**: Leave tournament equity behind when called and losing. Don't shove the nuts and raise non-all-in with air — stay balanced.

## Risk Factors
| Factor | Effect |
|--------|--------|
| Monotone boards | High risk for covered stack — check more |
| Middling draws (AJ8 type) | Develop check range |
| Multiple gut shots (AQ2, Q84) | Overbet ~105% pot for protection |
| Open-ended straight draws | NO overbet (unless BB leads with them) |
| Two-tone boards | NO overbet |
| ICM pressure (bubble) | Amplifies all risk factors vs ChipEV |

## Sizing
- Range bet boards: small c-bet (standard)
- Overbet boards: ~105% pot (protection + immediate value)
- River: non-all-in sizings (leave tournament equity behind)
- Size down on turns/rivers when covered

## Common Leaks
- Smash-betting every board without developing a check range
- Using overbet sizing on boards with open-enders or flush draws
- Shoving the river with the nuts and raising non-all-in with bluffs (exploitable)
- Not recognizing protection element under ICM

## Heuristics
- "ICM amplifies risk factors — check more on marginal boards"
- "Range bet ace-high Broadway; check back middling draws"
- "Overbet ~105% on multiple gut shots (not open-enders, not two-tone)"
- "Protection > inducing under ICM pressure"
- "Non-all-in river sizings — leave tournament equity behind"
- "Stay balanced — don't shove nuts and raise non-all-in with air"

## Rules Q&A
- Q: What boards does the covered BTN range bet?
  Options: [Ace-high Broadway boards (AKQ, AKJ, AKT, AQT, AJT), All boards, Low boards, Monotone boards]
  Correct: 0
  Explanation: These connect well with BTN's opening range. C-bet 100%. AQJ has ~20% check but simplifying to range bet costs ~0 EV.
- Q: What happens to monotone boards when BTN is covered?
  Options: [High check — back to checking (high risk for covered stack), Range bet, Overbet, No change from ChipEV]
  Correct: 0
  Explanation: Monotone is high risk for the covered stack. When BTN covers BB, monotone gets c-bet a lot. When BTN is covered, it's a very high check.
- Q: When does the covered BTN use an overbet (~105% pot)?
  Options: [Boards with multiple gut shots (AQ2, Q84, J74) — protection + immediate value, All boards, Monotone boards, Open-ended boards]
  Correct: 0
  Explanation: Overbet removes hands from villain's check-call range, creating better turn value spots. NOT on open-ended or two-tone boards (unless BB leads with open-enders).
- Q: Why use non-all-in sizings on the river when covered?
  Options: [Leave tournament equity behind when called and losing — preserve some stack, To confuse opponents, It's bigger, To match the solver]
  Correct: 0
  Explanation: Under ICM, leaving yourself some stack when called and losing preserves tournament equity. But stay balanced — same sizing for value and bluffs.

## Source Quotes
- "little to no leading on low to mid boards... check shoving low boards, strong and polar"
- "inducing on low draw heavy boards may maximize for chips, but it's not maximizing under high ICM pressure because the element of protection is a real thing"
- "risk factors for C betting as covered stack are amplified under high ICM pressure"
- "very few boards range bet, but the ones that really connect with button open range do tend to lean on range betting"
- "monotone boards, we are back to higher risk for C betting"
- "overbet sizing... not a thing on two-tone boards, and it's not a thing on open-ended straight draw boards"
- "make sure you use non-all-in sizings on river... leave some room for some tournament equity"

## Cross-References
- BM9: BB Covers BTN (Postflop) — the reverse stack configuration
- S1: UTG vs BB C-bet (ChipEV c-bet strategy — the baseline this adjusts from)
- S2: BTN vs BB C-bet (ChipEV BTN c-bet — the baseline)
- BM-Primer: ICM & FGS Foundations (why ICM amplifies risk factors)
