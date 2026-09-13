#!/usr/bin/env python3
"""GTO Wizard API strategy-array orders (derived empirically, verified
against stored range data; see the add-range skill).

Both orders derive from one 52-card deck order: ranks 2..A ascending,
suits c,d,h,s within rank (deck[0]='2c' ... deck[51]='As').

- combo order (1326, flop responses): every unordered pair (later card
  first in the combo string) at index i*(i-1)//2 + j for deck positions
  i > j. E.g. 4d4c -> i=9, j=8 -> 44.
- class order (169, preflop responses): hand classes sorted by the
  combo-index of their LAST combo (offsuit before suited, pairs last
  within their rank group).
"""

DECK = [r + s for r in "23456789TJQKA" for s in "cdhs"]
POS = {card: i for i, card in enumerate(DECK)}
RANKS = "AKQJT98765432"


def combo_index(combo):
    i, j = POS[combo[:2]], POS[combo[2:]]
    if i < j:
        i, j = j, i
    return i * (i - 1) // 2 + j


def combo_order():
    """The 1326 combos in API strategy order."""
    out = [None] * 1326
    for i in range(52):
        for j in range(i):
            out[i * (i - 1) // 2 + j] = DECK[i] + DECK[j]
    return out


def class_of(combo):
    r1, s1, r2, s2 = combo
    if r1 == r2:
        return r1 + r2
    hi, lo = (r1, r2) if RANKS.index(r1) < RANKS.index(r2) else (r2, r1)
    return hi + lo + ("s" if s1 == s2 else "o")


def combos_of_class(cls):
    """All combos of a hand class, in combo-string form (higher card first)."""
    if cls[0] == cls[1]:
        r = cls[0]
        return [r + b + r + a for a in "cdhs" for b in "cdhs" if b > a]  # 4d4c,4h4c,...
    hi, lo, kind = cls[0], cls[1], cls[2]
    suits = "cdhs"
    if kind == "s":
        return [hi + s + lo + s for s in suits]
    return [hi + s1 + lo + s2 for s1 in suits for s2 in suits if s1 != s2]


def class_order():
    """The 169 hand classes in API strategy order: plain ASCII sort of the
    class names ('2'<'3'<...<'9'<'A'<'J'<'K'<'Q'<'T', 'o'<'s') — e.g. AA
    sits between A9s and AJo, and TT is last."""
    classes = set()
    for i in range(52):
        for j in range(i):
            classes.add(class_of(DECK[i] + DECK[j]))
    return sorted(classes)


if __name__ == "__main__":
    combos, classes = combo_order(), class_order()
    assert len(set(combos)) == 1326 and len(classes) == 169
    print("combo[44] =", combos[44], "| combo[1257] =", combos[1257])
    print("class[8] =", classes[8], "| class[14] =", classes[14],
          "| class[23] =", classes[23])
