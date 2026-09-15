#!/usr/bin/env python3
"""Convert the scraped BBZ solutions into the wizard range-store schema.

Usage:
  bbz_to_store.py                 write ../bbz/store{,-asym,-pko}/ + manifests
  bbz_to_store.py --products A,B  restrict products (default: ChipEV,ICM,PKO)

Output mirrors packages/ranges/data: one dir per hero position
(utg/ utg1/ lj/ hj/ co/ btn/ sb/ bb/), one JSON per preflop line
(rfi.json, vs-utg.json, vs-3bet-bb.json, vs-sb-limp.json, ...) with a
shared title/position and one stacks[] entry per solution x depth.

Three stores (one per Live page):
- store/       equal-stack 8max — ChipEV + ICM (FT / bubble / 40% / 83%)
- store-asym/  asymmetric 8max ICM — the same ICM stages solved on
               full-table stack configs; entry.stack is the HERO's own
               stack, entry.config lists every seat's stack in order
               UTG, UTG+1, LJ, HJ, CO, BTN, SB, BB (RangeBrowser renders
               it as the color-coded table strip)
- store-pko/   PKO 8max (10/30/50/70% / bubble / FT) — per-seat stack
               configs, each stage solved with equal bounties (type
               ...-flat) and $N bounty variants (type ...-bN)

Schema conventions matched to the wizard store:
- fold is NOT stored (it is the complement; RangeGrid renders it)
- sizings carries the raise size only (smallest raise action); the
  biggest raise that covers >= 60% of the hero stack becomes allIn
- actions are class:freq strings (169 hand classes — the PioViewer
  paste shape); the app expands classes to concrete combos at load
- asymmetric/PKO entries carry config (per-seat stacks); equal-stack
  entries omit it. Their subtitle also carries the AVG level, since
  several table configs can share the hero's stack depth.

Skipped on purpose: 3max/6max, limp-variant solution files, asymmetric
ChipEV (chip-EV strategy keys off the effective stack, not the seat
distribution) and anything without a store-line mapping.

Also writes each store's index.json — the navigation manifest
(positions -> lines -> types -> depths) so the Live BBZ pages can
browse without loading every line file.
"""

import json
import os
import re
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
BBZ = os.path.join(os.path.dirname(HERE), "bbz")
STORES = ("store", "store-asym", "store-pko")

# BBZ label -> (store slug, display)
POS = {
    "UTG": ("utg", "UTG"), "MP": ("utg1", "UTG+1"), "LJ": ("lj", "LJ"),
    "HJ": ("hj", "HJ"), "CO": ("co", "CO"), "BU": ("btn", "BTN"),
    "SB": ("sb", "SB"), "BB": ("bb", "BB"),
}

# per-seat stack config order — matches RangeBrowser's SEATS display order
SEAT_ORDER = ["UTG", "MP", "LJ", "HJ", "CO", "BU", "SB", "BB"]

# equal-stack products -> (type, subtitle)
EQUAL = {
    ("ChipEV", ""): ("cEV", "ChipEV"),
    ("ICM", "FT"): ("ICM-FT", "ICM · BBZ final table"),
    ("ICM", "ITM Bubble"): ("ICM-BBZ-bubble", "ICM · BBZ bubble"),
    ("ICM", "40%"): ("ICM-BBZ-40pct", "ICM · BBZ · 40% left"),
    ("ICM", "83%"): ("ICM-BBZ-83pct", "ICM · BBZ · 83% left"),
}
# asymmetric ICM products -> (type, subtitle)
ASYM = {
    ("ICM", "FT"): ("ICM-FT-asym", "ICM · BBZ final table"),
    ("ICM", "ITM Bubble"): ("ICM-BBZ-bubble-asym", "ICM · BBZ bubble"),
    ("ICM", "40%"): ("ICM-BBZ-40pct-asym", "ICM · BBZ · 40% left"),
    ("ICM", "83%"): ("ICM-BBZ-83pct-asym", "ICM · BBZ · 83% left"),
}
# PKO stages -> (type base, subtitle base)
PKO = {
    "10%": ("PKO-10pct", "PKO · BBZ · 10% left"),
    "30%": ("PKO-30pct", "PKO · BBZ · 30% left"),
    "50%": ("PKO-50pct", "PKO · BBZ · 50% left"),
    "70%": ("PKO-70pct", "PKO · BBZ · 70% left"),
    "FT": ("PKO-FT", "PKO · BBZ final table"),
    "ITM Bubble": ("PKO-bubble", "PKO · BBZ bubble"),
}

SUITS = "shdc"


def node_actions(node, hero_stack):
    """BBZ node -> ({action: class:freq string}, sizings) without fold."""
    acts = node.get("percentages", [])
    raise_idx = [i for i, a in enumerate(acts) if a["action"] == "Raise"]
    all_in = -1
    if raise_idx:
        big = max(raise_idx, key=lambda i: float(acts[i].get("amount") or 0))
        if float(acts[big].get("amount") or 0) >= hero_stack * 0.6:
            all_in = big
    buckets = defaultdict(list)
    for ai, a in enumerate(acts):
        act = a["action"]
        if act == "Fold":
            continue
        elif act == "Call":
            bucket = "call"
        elif act == "Check":
            bucket = "check"
        elif act == "Raise":
            bucket = "allIn" if ai == all_in else "raise"
        else:
            continue
        for row in node.get("ranges", []):
            for key, v in row.items():
                f = (v.get("freq", [])[ai] if ai < len(v.get("freq", [])) else 0) / 100
                if f <= 0.00005:
                    continue
                buckets[bucket].append(f"{key.lstrip('_')}:{round(f, 4)}")
    out = {k: ",".join(v) for k, v in buckets.items() if v}
    sizings = {}
    raises = sorted((float(acts[i].get("amount") or 0) for i in raise_idx
                    if i != all_in))
    if raises:
        sizings["raise"] = round(raises[0], 2)
    return out, sizings


def classify(hero, spot):
    """(line slug, title) for a BBZ spot, or None to skip."""
    name, group = spot["name"], spot["group"]
    disp = POS[hero][1]
    m = re.fullmatch(r"vs (\w+) RFI", name)
    if group == "rfi":
        return "rfi", f"{disp} RFI"
    if group == "general" and m:
        v = POS[m.group(1)][1]
        return f"vs-{POS[m.group(1)][0]}", f"{disp} vs {v} RFI"
    m3 = re.fullmatch(r"vs (\w+) 3Bet", name)
    if group == "3bet" and m3:
        v = POS[m3.group(1)][1]
        return f"vs-3bet-{POS[m3.group(1)][0]}", f"{disp} vs {v} 3-bet"
    if group == "lfi" and re.search(r"vs SB LFI", name):
        # the limped line only exists for BB (other seats ISO instead —
        # skipped below, the wizard store has no ISO lines)
        return "vs-sb-limp", f"{disp} vs SB limp"
    return None


def stack_num(v):
    v = round(float(v), 1)
    return int(v) if v == int(v) else v


def main():
    wanted = None
    if "--products" in sys.argv:
        wanted = set(sys.argv[sys.argv.index("--products") + 1].split(","))
    with open(os.path.join(BBZ, "index.json")) as f:
        index = json.load(f)

    # per store: fkey -> {"title", "position", "stacks": {key: entry}}
    lines = {s: defaultdict(lambda: {"title": None, "position": None,
                                     "stacks": {}}) for s in STORES}
    manifest = {s: defaultdict(lambda: defaultdict(lambda: defaultdict(set)))
                for s in STORES}
    # type -> (group order, model order) for the stack-list sort
    type_order = {}
    skipped = defaultdict(int)
    n_entries = {s: 0 for s in STORES}

    def note_order(stype, group, model):
        if stype not in type_order:
            type_order[stype] = (group, model)

    for meta in index:
        if wanted and meta["product_name"] not in wanted:
            continue
        if meta["table_size"] != "8max" or "Limp" in meta["name"]:
            continue
        prod = (meta["product_name"], meta["players_left"])
        equal = meta["stack_distribution"] == "Equal"

        if meta["product_name"] == "PKO":
            if prod[1] not in PKO:
                skipped[f"prod:{prod}"] += 1
                continue
            store = "store-pko"
            base, sub = PKO[prod[1]]
            mm = re.search(r"\$(\d+)$", meta["name"])
            if mm:
                stype = f"{base}-b{mm.group(1)}"
                subtitle = f"{sub} · ${mm.group(1)} bounty"
                model = int(mm.group(1))
            else:
                stype = f"{base}-flat"
                subtitle = f"{sub} · equal bounties"
                model = 0
            # stage order: 70% -> 50% -> 30% -> 10% -> bubble -> FT
            group = {"70%": 1, "50%": 2, "30%": 3, "10%": 4,
                     "ITM Bubble": 5, "FT": 6}[prod[1]]
            note_order(stype, group, model)
        elif equal and prod in EQUAL:
            store = "store"
            stype, subtitle = EQUAL[prod]
            group = 0
            model = {"cEV": 0, "ICM-BBZ-83pct": 10, "ICM-BBZ-40pct": 20,
                     "ICM-BBZ-bubble": 30, "ICM-FT": 40}[stype]
            note_order(stype, group, model)
        elif not equal and prod in ASYM:
            store = "store-asym"
            stype, subtitle = ASYM[prod]
            group = 0
            model = {"ICM-BBZ-83pct-asym": 10, "ICM-BBZ-40pct-asym": 20,
                     "ICM-BBZ-bubble-asym": 30, "ICM-FT-asym": 40}[stype]
            note_order(stype, group, model)
        else:
            skipped[f"prod:{prod}{'-equal' if equal else '-asym'}"] += 1
            continue

        depth = int(re.search(r"AVG(\d+)", meta["avg_stack"]).group(1))
        with open(os.path.join(BBZ, meta["path"])) as f:
            d = json.load(f)
        cols = [c.split("|")[:2] for c in d["columns"]]
        stacks = {pos: float(s) for pos, s in cols}
        if not equal:
            if not all(s in stacks for s in SEAT_ORDER):
                skipped[f"cols:{meta['name']}"] += 1
                continue
            config = [stack_num(stacks[s]) for s in SEAT_ORDER]
        else:
            config = None
        # spots per hero, deduped by nodeId
        seen = set()
        spots = defaultdict(list)
        for row in sorted(d["table"], key=int):
            for ci, cell in enumerate(d["table"][row]):
                hero = cols[ci][0]
                for c in cell:
                    if not c.get("name") or c.get("name") == "x":
                        continue
                    nid = c.get("nodeId")
                    if nid is None or (hero, nid) in seen:
                        continue
                    seen.add((hero, nid))
                    spots[hero].append({"name": c["name"],
                                         "group": c.get("group", "general"),
                                         "nodeId": nid})
        for hero, hs in spots.items():
            if hero not in POS:
                skipped[f"pos:{hero}"] += 1
                continue
            hstack = depth if equal else stack_num(stacks[hero])
            for spot in hs:
                cls = classify(hero, spot)
                if not cls:
                    skipped[f"spot:{spot['name']}"] += 1
                    continue
                line_slug, title = cls
                slug, disp = POS[hero]
                node = d["nodes"][str(spot["nodeId"])]
                actions, sizings = node_actions(node, hstack)
                if not actions:
                    continue
                sub = subtitle if equal else f"{subtitle} · AVG{depth}"
                entry = {"type": stype, "subtitle": sub, "stack": hstack,
                         "actions": actions}
                if sizings:
                    entry["sizings"] = sizings
                if config:
                    entry["config"] = config
                key = f"{stype}-{depth}" if equal else \
                    f"{stype}-{depth}-{meta['stack_distribution']}"
                fkey = f"{slug}/{line_slug}"
                lines[store][fkey]["title"] = title
                lines[store][fkey]["position"] = disp
                lines[store][fkey]["stacks"][key] = entry
                # manifest keys carry the base subtitle (no AVG level —
                # the AVG belongs to the individual entries)
                manifest[store][slug][line_slug][f"{stype}|{subtitle}"].add(hstack)
                n_entries[store] += 1

    for store in STORES:
        out_dir = os.path.join(BBZ, store)
        os.makedirs(out_dir, exist_ok=True)
        n_files = 0
        for fkey, data in sorted(lines[store].items()):
            stack_list = sorted(data["stacks"].values(),
                                key=lambda e: (type_order.get(e["type"], (9, 9)),
                                               -e["stack"]))
            out = {"title": data["title"], "position": data["position"],
                   "stacks": stack_list}
            path = os.path.join(out_dir, fkey + ".json")
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as f:
                json.dump(out, f, separators=(",", ":"))
            n_files += 1

        m_out = {}
        for slug, lns in sorted(manifest[store].items()):
            m_out[slug] = {}
            for line, types in sorted(lns.items()):
                m_out[slug][line] = {
                    "title": lines[store][f"{slug}/{line}"]["title"],
                    "types": [
                        {"type": t.split("|")[0], "subtitle": t.split("|")[1],
                         "stacks": sorted(depths, reverse=True)}
                        for t, depths in sorted(types.items())
                    ],
                }
        with open(os.path.join(out_dir, "index.json"), "w") as f:
            json.dump(m_out, f, separators=(",", ":"))

        print(f"{store}: {n_files} line files, {n_entries[store]} entries")
    if skipped:
        print("skipped:")
        for k, v in sorted(skipped.items(), key=lambda x: -x[1])[:10]:
            print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
