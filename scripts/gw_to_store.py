#!/usr/bin/env python3
"""Convert fetched GTO Wizard spot-solutions (see fetch_browser.py) into the
range store's combo-line format.

  python3 packages/ranges/imports/scripts/gw_to_store.py flop .scratch/k83-fetched.json
      --parent utg/rfi.json --stack 40
  python3 packages/ranges/imports/scripts/gw_to_store.py preflop .scratch/utg40-fetched.json

Flop responses are per-combo (1326, gw_order.combo_order); preflop responses
are per-class (169, gw_order.class_order — class values are copied to every
combo of the class, which is display-equivalent). Flop lines are stored
open-weighted (conditional x parent open weight) per the store convention.
Prints JSON: {actions, sizing, stats} — the add-range skill's procedure then
validates and writes the store entry.
"""

import argparse
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gw_order import combo_order, class_order, class_of, combos_of_class

# scripts live in imports/ (the nested solutions repo); the store is
# in the main repo at packages/ranges/data — two levels up from here
STORE = pathlib.Path(__file__).resolve().parents[2] / "data"
MIN_FREQ = 0.00005


def die(msg):
    print(msg, file=sys.stderr)
    sys.exit(1)


def load_actions(data):
    return data["action_solutions"], data["game"]


def fmt(v):
    return f"{v:.6f}".rstrip("0").rstrip(".") or "0"


def flop(data, parent_rel, stack, ptype=None):
    combos = combo_order()
    actions, game = load_actions(data)
    board = game.get("board")
    if not board:
        die("no board in response — not a flop solution?")
    blocked = {board[i:i + 2] for i in range(0, len(board), 2)}

    parent = json.loads((STORE / parent_rel).read_text())
    entry = next((s for s in parent["stacks"] if s["stack"] == stack
                  and "raise" in s.get("actions", {})
                  and (ptype is None or s["type"] == ptype)), None)
    if entry is None:
        die(f"no stack-{stack} raise entry in {parent_rel}")
    weights = {e.split(":")[0]: float(e.split(":")[1])
               for e in entry["actions"]["raise"].split(",")}

    check = next((a for a in actions if a["action"]["code"] == "X"), None)
    bet = next((a for a in actions if a["action"]["type"] == "RAISE"
                and not a["action"].get("allin")), None)
    if not bet:
        die("no bet action in response")

    lines, kept = {}, 0
    for name, action in (("bet", bet), ("check", check)):
        strat = action["strategy"]
        parts = []
        for idx, combo in enumerate(combos):
            w = weights.get(combo)
            if w is None or combo[:2] in blocked or combo[2:] in blocked:
                continue
            cond = strat[idx]
            if cond < MIN_FREQ:
                continue
            parts.append(f"{combo}:{fmt(w * cond)}")
        lines[name] = ",".join(parts)
        kept = max(kept, len(parts))

    sizing = float(bet["action"]["betsize"])
    sizing = int(sizing) if sizing == int(sizing) else sizing
    den = sum(weights.get(c, 0) for c in weights
              if c[:2] not in blocked and c[2:] not in blocked)
    cond_bet = {e.split(":")[0]: float(e.split(":")[1]) / weights[e.split(":")[0]]
                for e in lines["bet"].split(",")} if lines["bet"] else {}
    betpct = sum(weights.get(c, 0) * v for c, v in cond_bet.items()) / den
    return {"board": board, "actions": lines, "sizing": sizing,
            "combos": kept, "betPct": round(100 * betpct, 1),
            "checkPct": round(100 * (1 - betpct), 1)}


def preflop(data):
    classes = class_order()
    actions, game = load_actions(data)
    lines = {}
    sizing = None
    for a in actions:
        act = a["action"]
        if act["type"] == "FOLD":
            continue
        key = ("allIn" if act.get("allin")
               else "check" if act["type"] == "CHECK"
               else "call" if act["type"] == "CALL" else "raise")
        if key == "raise" and sizing is None:
            s = float(act.get("betsize") or 0)
            sizing = int(s) if s == int(s) else s
        if key == "raise" and "raise" in lines:
            # multi-size nodes (covering-stack opens offer 2bb and ~half-stack):
            # keep the FIRST (min) raise — the primary open the store displays
            continue
        parts = []
        for ci, value in enumerate(a["strategy"]):
            if value < MIN_FREQ:
                continue
            for combo in combos_of_class(classes[ci]):
                parts.append(f"{combo}:{fmt(value)}")
        if parts:
            lines[key] = ",".join(parts)
    return {"actions": lines, "sizing": sizing,
            "combos": sum(len(v.split(",")) for v in lines.values()),
            "openPct": round(100 * sum(float(e.split(":")[1]) for v in lines.values()
                                       for e in v.split(",")) / 1326, 1)}


def main():
    ap = argparse.ArgumentParser(prog="gw_to_store")
    ap.add_argument("mode", choices=("flop", "preflop"))
    ap.add_argument("fetched", type=pathlib.Path)
    ap.add_argument("--parent", default="utg/rfi.json", help="parent line file (flop mode)")
    ap.add_argument("--stack", type=int, default=40, help="parent stack (flop mode)")
    ap.add_argument("--parent-type", default=None, help="parent entry type when several share the stack (flop mode)")
    args = ap.parse_args()
    data = json.loads(args.fetched.read_text())
    out = flop(data, args.parent, args.stack, args.parent_type) if args.mode == "flop" else preflop(data)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
