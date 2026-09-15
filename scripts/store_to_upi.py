#!/usr/bin/env python3
"""Emit UPI (PioSOLVER Universal Poker Interface) weight arrays from a
wizard-schema range-store line file — works for both the BBZ store
(bbz/store/) and the GTO Wizard store (packages/ranges/data/).

The store keeps combo:freq strings per action; UPI's set_range wants
1326 space-separated weights in Pio's canonical hand order (deck order,
ranks 2..A, suits c d h s, later card first — the same order as
gw_order.combo_order()).

Usage:
  store_to_upi.py <line.json> [--stack N] [--type cEV] [--json OUT]

Output: one line per action per matching stack entry:
  <type> <stack>bb <action> <1326 floats...>
With --json: {"<type>-<stack>bb-<action>": [1326 floats]} written to OUT.

Combo:freq entries can be concrete combos (AsKd:0.5) — the weight lands
on that combo only. Weights are rounded to 4 decimals.
"""

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from gw_order import combo_order  # noqa: E402 — 1326 combos, UPI order

HANDS = combo_order()


def entry_upi_weights(actions):
    """actions dict -> {action: [1326 weights]}"""
    out = {}
    for action, raw in actions.items():
        weights = [0.0] * 1326
        for entry in raw.split(","):
            parts = entry.strip().split(":")
            if len(parts) != 2:
                continue
            combo, freq = parts[0].strip(), parts[1].strip()
            combo = combo[0].upper() + combo[1] + combo[2].upper() + combo[3] \
                if len(combo) == 4 else combo
            try:
                f = float(freq)
            except ValueError:
                continue
            try:
                idx = HANDS.index(combo)
            except ValueError:
                raise SystemExit(f"ERROR: combo {combo!r} not in UPI hand order")
            weights[idx] = f
        out[action] = [round(w, 4) for w in weights]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("line", help="wizard-schema line JSON (bbz/store or packages/ranges/data)")
    ap.add_argument("--stack", type=int, help="filter to this effective stack (bb)")
    ap.add_argument("--type", dest="stype", help="filter to this solution type (e.g. cEV, ICM-FT)")
    ap.add_argument("--action", help="filter to one action (e.g. raise)")
    ap.add_argument("--json", dest="json_out", help="also write {key: [weights]} to this file")
    args = ap.parse_args()

    with open(args.line) as f:
        line = json.load(f)
    entries = line.get("stacks", [])
    if args.stype:
        entries = [e for e in entries if e.get("type") == args.stype]
    if args.stack:
        entries = [e for e in entries if e.get("stack") == args.stack]
    if not entries:
        raise SystemExit("no matching stack entries")
    if not args.json_out:
        print(f"# {line.get('title')} ({line.get('position')}) — {args.line}")
    dump = {}
    for e in entries:
        weights = entry_upi_weights(e.get("actions", {}))
        for action, w in weights.items():
            if args.action and action != args.action:
                continue
            key = f"{e['type']}-{e['stack']}bb-{action}"
            dump[key] = w
            if not args.json_out:
                total = sum(w) / 1326 * 100
                print(f"{e['type']} {e['stack']}bb {action:6} "
                      f"({total:.2f}% of hands): {' '.join(str(x) for x in w)}")
    if args.json_out:
        with open(args.json_out, "w") as f:
            json.dump(dump, f)
        print(f"{len(dump)} arrays -> {args.json_out}")
    elif not args.json_out:
        pass


if __name__ == "__main__":
    main()
