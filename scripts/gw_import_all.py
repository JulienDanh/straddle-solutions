#!/usr/bin/env python3
"""Import every archived PREFLOP capture into the range store.

Idempotent: nodes already stored (same position, stack and stack config)
are skipped, so re-running is a no-op and existing hand-labeled entries are
never re-derived. New entries are derived mechanically:

  store file   rfi/<pos>.json · vs-open -> <defender>/vs-<opener>.json
               (SB opener -> vs-sb-raise) · vs-3bet -> <opener>/vs-3bet-<villain>.json
               vs-limp -> bb/vs-sb-limp.json
  type         cEV · ICM / ICM-FT (symmetric) · ICM-covering / ICM-covered-{deep,
               similar} (+ FT- variants) from the hero's stack direction
               vs the players still in the hand (see derive_type)
  subtitle     course prefix + config description (who covers whom)

Flop nodes are NOT handled — they are content-driven (parent line, board,
page wiring) and stay on the manual add-range procedure.

Usage (repo root):
  python3 straddle-solutions/scripts/gw_import_all.py --dry-run   # review proposal
  python3 straddle-solutions/scripts/gw_import_all.py             # import
  python3 straddle-solutions/scripts/gw_import_all.py --skip cev  # limit gametypes
"""

import argparse
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from gw_to_store import preflop  # noqa: E402  (conversion, verbatim store format)

ROOT = HERE.parent                      # straddle-solutions/
SOLUTIONS = ROOT / "solutions"
STORE = ROOT.parent / "packages" / "ranges" / "data"

SEATS = ["UTG", "UTG+1", "LJ", "HJ", "CO", "BTN", "SB", "BB"]
SHORT = {"utg": "UTG", "utg1": "UTG+1", "lj": "LJ", "hj": "HJ",
         "co": "CO", "btn": "BTN", "sb": "SB", "bb": "BB"}
GAMETYPES = {
    # archive dir -> (store type prefix, subtitle prefix)
    "cev": ("cEV", ""),
    "icm-8m-200ptbubblemid": ("ICM", "ICM · 200-man bubble"),
    "mttgeneral-icm-8m-200-ptft": ("ICM-FT", "ICM · 200-man final table"),
}
# covered deep vs similar threshold: the biggest coverer at >= 1.75x the
# hero is "covered by heaps"-style deep; closer stacks are "similar" (the
# BM2 30-40bb covered zone). Existing hand-labeled entries are never
# re-derived, so this only governs NEW nodes.
# The covered/covering classification — shared with the store's SolutionType
# union (design-system data/ranges/types.ts). POSITION-RELATIVE: hero's stack
# H vs the players still in the hand at the decision point, not the whole
# table (folded stacks cannot bust you in this hand):
#   rfi       only the seats AFTER hero (everyone before hero folded —
#             UTG RFI is the whole table, BTN RFI just the blinds, SB RFI BB)
#   vs-open   the opener + every seat behind hero (seats between opener and
#             hero have folded)
#   vs-3bet   the 3-bettor only (everyone else folds back to hero)
#   vs-limp   SB only (blind vs blind)
#   covering      no relevant stack > H — hero covers the line's villain
#   covered-*     the BIGGEST relevant coverer S decides: S < DEEP_RATIO*H
#                 similar, S >= DEEP_RATIO*H deep, S >= HEAPS_RATIO*H "heaps"
DEEP_RATIO = 1.75
HEAPS_RATIO = 3


def slug(pos):
    return pos.lower().replace("+", "")


def store_file(category, name):
    """archive category/name -> store file relative to packages/ranges/data."""
    if category == "rfi":
        return f"{slug(name)}/rfi.json"
    if category == "vs-open":
        opener, defender = name.split("-")
        vs = "vs-sb-raise" if opener == "sb" else f"vs-{opener}"
        return f"{defender}/{vs}.json"
    if category == "vs-3bet":
        opener, villain = name.split("-")
        return f"{opener}/vs-3bet-{villain}.json"
    if category == "vs-limp":
        return "bb/vs-sb-limp.json"
    return None


def node_hero_stacks(data):
    """(hero position, config stacks in SEATS order, hero stack) from a capture."""
    cfg, hero, hero_stack = [None] * 8, None, None
    for p in data["game"]["players"]:
        cfg[SEATS.index(p["position"])] = int(float(p["stack"]))
        if p["is_hero"]:
            hero, hero_stack = p["position"], int(float(p["stack"]))
    return hero, cfg, hero_stack


def villain_of(category, name):
    """The line's villain seat, or None for RFI (no single villain)."""
    if category == "vs-3bet":
        return SHORT[name.split("-")[-1]]
    if category == "vs-limp":
        return "SB"
    if category == "vs-open":
        return SHORT[name.split("-")[0]]
    return None


def relevant_others(category, name, hero, cfg):
    """(seat, stack) pairs still in the hand at hero's decision point."""
    hi = SEATS.index(hero)
    others = [(SEATS[i], s) for i, s in enumerate(cfg) if i != hi]
    villain = villain_of(category, name)
    if villain is None:  # rfi — everyone before hero folded; only the
        # seats after hero talk next, so only they can bust hero this hand
        hi = SEATS.index(hero)
        return [(SEATS[i], s) for i, s in enumerate(cfg) if i > hi]
    if category == "vs-3bet":  # everyone folds back to hero
        return [(s, v) for s, v in others if s == villain]
    if category in ("vs-limp", "vs-open"):
        # vs-open: opener + every seat behind hero (in between has folded);
        # vs-limp / SB opens: SB (+ BB behind, but hero IS BB there)
        behind = set(SEATS[hi + 1:]) if category == "vs-open" else set()
        return [(s, v) for s, v in others if s == villain or s in behind]
    raise ValueError(category)


def derive_type(kind, category, name, hero, cfg, hero_stack):
    """(type, config-description) from the stack direction.

    POSITION-RELATIVE — mirrors the store's SolutionType union: classify
    hero's stack H against the players still in the hand (relevant_others),
    not the whole table. covering when no relevant stack covers H (the desc
    names the line's villain); otherwise the biggest relevant coverer S
    picks covered-similar (S < DEEP_RATIO*H) or covered-deep (S >=
    DEEP_RATIO*H, "by heaps" at S >= HEAPS_RATIO*H)."""
    sym = len(set(cfg)) == 1
    if kind == "cEV" or sym:
        return kind, None if kind == "cEV" else "equal stacks"
    ft = kind.startswith("ICM-FT")
    t = "ICM-FT" if ft else "ICM"
    rel = relevant_others(category, name, hero, cfg)
    coverers = [(s, v) for s, v in rel if v > hero_stack]
    covered = [(s, v) for s, v in rel if v < hero_stack]
    if not coverers and covered:
        villain = villain_of(category, name)
        if category == "rfi" and len(covered) == len(rel):
            desc = "you cover the table"
        elif villain is not None and villain in dict(covered):
            desc = f"you cover {villain} ({dict(covered)[villain]}bb)"
        else:
            seat, s = max(covered, key=lambda x: x[1])
            desc = f"you cover {seat} ({s}bb)"
        return f"{t}-covering", desc
    if coverers:
        seat, s = max(coverers, key=lambda x: x[1])
        ratio = s / hero_stack
        if ratio >= HEAPS_RATIO:
            desc = "they cover you by heaps"
        elif ratio >= DEEP_RATIO:
            desc = f"{seat} {s}bb covers you"
        else:
            desc = f"{seat} {s}bb similar — covers you"
        kind2 = "deep" if ratio >= DEEP_RATIO else "similar"
        return f"{t}-covered-{kind2}", desc
    return t, "equal stacks"


def main():
    ap = argparse.ArgumentParser(prog="gw_import_all")
    ap.add_argument("--dry-run", action="store_true",
                    help="print the proposal without writing")
    ap.add_argument("--skip", nargs="*", default=[],
                    help="archive gametype dirs to skip (e.g. cev)")
    args = ap.parse_args()

    stored, skipped, errors = [], [], []
    for gt_dir, (kind, prefix) in GAMETYPES.items():
        if gt_dir in args.skip:
            continue
        gt_root = SOLUTIONS / gt_dir
        if not gt_root.exists():
            continue
        for cfg_dir in sorted(gt_root.iterdir()):
            if not cfg_dir.is_dir():
                continue
            for cat_dir in sorted(cfg_dir.iterdir()):
                if cat_dir.name == "flops" or not cat_dir.is_dir():
                    continue
                for node in sorted(cat_dir.glob("*.json")):
                    rel = f"{gt_dir}/{cfg_dir.name}/{cat_dir.name}/{node.name}"
                    try:
                        data = json.loads(node.read_text())
                        hero, cfg, hero_stack = node_hero_stacks(data)
                        sfile = store_file(cat_dir.name, node.stem)
                        if not sfile:
                            errors.append(f"{rel}: no store mapping")
                            continue
                        spath = STORE / sfile
                        if not spath.exists():
                            errors.append(f"{rel}: store file {sfile} missing — create it first")
                            continue
                        store = json.loads(spath.read_text())
                        if store["position"] != hero:
                            errors.append(f"{rel}: hero {hero} != store position {store['position']}")
                            continue
                        dup = [s for s in store["stacks"]
                               if s.get("config") == cfg and s["stack"] == hero_stack]
                        sym = len(set(cfg)) == 1
                        if not sym:
                            if dup:
                                skipped.append(rel)
                                continue
                        else:
                            have = [s for s in store["stacks"]
                                    if s["type"] == kind and s["stack"] == hero_stack]
                            if have:
                                skipped.append(rel)
                                continue
                        conv = preflop(data)
                        if not conv["actions"]:
                            errors.append(f"{rel}: empty actions")
                            continue
                        if kind == "cEV":
                            etype, sub = "cEV", "ChipEV"
                        else:
                            etype, desc = derive_type(kind, cat_dir.name,
                                                       node.stem, hero, cfg,
                                                       hero_stack)
                            sub = prefix + (f" · {desc}" if desc else "")
                        entry = {
                            "type": etype,
                            "subtitle": sub,
                            "stack": hero_stack,
                        }
                        if not sym:
                            entry["config"] = cfg
                        entry["actions"] = conv["actions"]
                        entry["sizings"] = {"raise": conv["sizing"]}
                        print(f"{'DRY ' if args.dry_run else ''}STORE "
                              f"{sfile}: {etype} {hero_stack}bb "
                              f"({conv['combos']} combos, raise {conv['sizing']}bb) "
                              f"— {sub}")
                        if args.dry_run:
                            stored.append(rel)
                            continue
                        store["stacks"].append(entry)
                        spath.write_text(
                            json.dumps(store, indent=2, ensure_ascii=True) + "\n")
                        stored.append(rel)
                    except Exception as e:
                        errors.append(f"{rel}: {e}")

    print(f"\nstored: {len(stored)}, already present: {len(skipped)}, errors: {len(errors)}")
    for e in errors:
        print(f"  ERROR {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
