#!/usr/bin/env python3
"""Convert fetched GTO Wizard spot-solutions (see fetch_browser.py) into the
range store's combo-line format.

  python3 straddle-solutions/scripts/gw_to_store.py flop .scratch/k83-fetched.json
      --parent utg/rfi.json --stack 40
  python3 straddle-solutions/scripts/gw_to_store.py preflop .scratch/utg40-fetched.json

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

# scripts live in the straddle-solutions submodule at the repo root;
# the store is in the main repo at packages/ranges/data — two levels up
STORE = pathlib.Path(__file__).resolve().parents[2] / "packages/ranges/data"
MIN_FREQ = 0.00005


def die(msg):
    print(msg, file=sys.stderr)
    sys.exit(1)


def load_actions(data):
    return data["action_solutions"], data["game"]


def fmt(v):
    return f"{v:.6f}".rstrip("0").rstrip(".") or "0"


def flop(data, parent_rel, stack, ptype=None, parent_action="raise",
         raise_key="bet"):
    """Convert a flop decision node to weighted store lines.

    parent_action: which line of the parent entry is the hero's reach
    ("raise" — opener lines, "check" — BB vs SB limp, "call" — defend
    lines). raise_key: how the hero's RAISE is keyed in the store ("bet"
    for aggressor nodes — c-bet/stab, "raise" when facing a bet — defend
    and vs-raise nodes)."""
    combos = combo_order()
    actions, game = load_actions(data)
    board = game.get("board")
    if not board:
        die("no board in response — not a flop solution?")

    parent = json.loads((STORE / parent_rel).read_text())
    entry = next((s for s in parent["stacks"] if s["stack"] == stack
                  and parent_action in s.get("actions", {})
                  and (ptype is None or s["type"] == ptype)), None)
    if entry is None:
        die(f"no stack-{stack} {parent_action} entry in {parent_rel}")
    weights = {e.split(":")[0]: float(e.split(":")[1])
               for e in entry["actions"][parent_action].split(",")}

    blocked = {board[i:i + 2] for i in range(0, len(board), 2)}
    keys = {"FOLD": "fold", "CHECK": "check", "CALL": "call", "RAISE": raise_key}
    lines, sizings, kept = {}, {}, 0
    for action in actions:
        act = action["action"]
        key = "allIn" if act.get("allin") else keys.get(act["type"])
        if key is None or key in lines:
            continue
        strat = action["strategy"]
        parts = []
        for idx, combo in enumerate(combos):
            w = weights.get(combo)
            if w is None or combo[:2] in blocked or combo[2:] in blocked:
                continue
            cond = strat[idx]
            # keep every nonzero strategy: coverage of the parent line must be
            # exact (tiny weighted values are verbatim solver output)
            if cond <= 0:
                continue
            parts.append(f"{combo}:{fmt(w * cond)}")
        if parts:
            lines[key] = ",".join(parts)
            kept = max(kept, len(parts))
        if key in ("raise", "bet", "allIn"):
            s = float(act["betsize"])
            sizings[key] = int(s) if s == int(s) else s

    den = sum(weights.get(c, 0) for c in weights
              if c[:2] not in blocked and c[2:] not in blocked)
    stats = {}
    for key, line in lines.items():
        num = sum(weights[c] * min(v / weights[c], 1)
                  for c, v in ((e.split(":")[0], float(e.split(":")[1]))
                               for e in line.split(",")))
        stats[key] = round(100 * num / den, 1) if den else 0.0
    # the hero's reach at the node, verbatim from the capture (open x street
    # conditionals for deep nodes) — the display base. None for preflop
    # responses (reach = the parent line itself).
    hero = next((p for p in data["players_info"]
                 if p.get("player", {}).get("position") == game.get("active_position")),
                data["players_info"][0])
    reach_parts = []
    for idx, combo in enumerate(combos):
        w = hero.get("range", [])[idx] if hero.get("range") else None
        if w and w > 0 and combo[:2] not in blocked and combo[2:] not in blocked:
            reach_parts.append(f"{combo}:{fmt(w)}")
    return {"board": board, "actions": lines, "sizings": sizings,
            "combos": kept, "stats": stats,
            "reach": ",".join(reach_parts)}


def preflop(data):
    classes = class_order()
    actions, game = load_actions(data)
    # the hero's reach at the node, per combo — classes outside the hero's
    # range carry meaningless values (e.g. an opener's vs-3bet node fills
    # junk classes with 1.0); only in-range combos are real strategy
    hero = next((p for p in data["players_info"]
                 if p.get("player", {}).get("position") == game.get("active_position")),
                data["players_info"][0])
    # preflop responses are per-class: the hero's reach is per-class too
    reach = hero.get("range") or []
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
            # classes outside the hero's reach carry meaningless values —
            # an opener's vs-3bet node fills never-opened junk with 1.0
            if reach and len(reach) == len(classes) and reach[ci] <= 0:
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
    ap.add_argument("mode", choices=["flop", "preflop"])
    ap.add_argument("capture", type=pathlib.Path)
    ap.add_argument("--parent", default="utg/rfi.json",
                    help="parent store file (flop mode)")
    ap.add_argument("--stack", type=int, default=40)
    ap.add_argument("--ptype", default=None)
    ap.add_argument("--parent-action", default="raise",
                    help="parent line the hero's reach weights come from")
    ap.add_argument("--raise-key", default="bet", choices=["bet", "raise"],
                    help="store key for the hero's RAISE")
    args = ap.parse_args()
    data = json.loads(args.capture.read_text())
    if args.mode == "flop":
        out = flop(data, args.parent, args.stack, args.ptype,
                   args.parent_action, args.raise_key)
    else:
        out = preflop(data)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
