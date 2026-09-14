#!/usr/bin/env python3
"""Convert the scraped BBZ solutions into the wizard range-store schema.

Usage:
  bbz_to_store.py                 write ../bbz/store/ + index manifest
  bbz_to_store.py --products A,B  restrict products (default: ChipEV,ICM)

Output mirrors packages/ranges/data: one dir per hero position
(utg/ utg1/ lj/ hj/ co/ btn/ sb/ bb/), one JSON per preflop line
(rfi.json, vs-utg.json, vs-3bet-bb.json, vs-sb-limp.json, ...) with a
shared title/position and one stacks[] entry per solution × depth.

Schema conventions matched to the wizard store:
- fold is NOT stored (it is the complement; RangeGrid renders it)
- sizings carries the raise size only (smallest raise action); the
  biggest raise that covers >= 60% of the hero stack becomes allIn
- per-class BBZ frequencies expand to concrete combo:freq strings
- equal-stack 8max solutions only, across the BBZ products: ChipEV,
  ICM (FT / bubble / 40% / 83%) and PKO (10/30/50/70% / FT / bubble);
  asymmetric files, limp-variant files and non-8max formats are skipped

Also writes store/index.json — the navigation manifest (positions ->
lines -> types -> depths) so the Live BBZ page can browse without
loading every line file.
"""

import json
import os
import re
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
BBZ = os.path.join(os.path.dirname(HERE), "bbz")
STORE = os.path.join(BBZ, "store")

# BBZ label -> (store slug, display)
POS = {
    "UTG": ("utg", "UTG"), "MP": ("utg1", "UTG+1"), "LJ": ("lj", "LJ"),
    "HJ": ("hj", "HJ"), "CO": ("co", "CO"), "BU": ("btn", "BTN"),
    "SB": ("sb", "SB"), "BB": ("bb", "BB"),
}

PRODUCTS = {
    # product_name, players_left -> (store type, subtitle)
    ("ChipEV", ""): ("cEV", "ChipEV"),
    ("ICM", "FT"): ("ICM-FT", "ICM · BBZ final table"),
    ("ICM", "ITM Bubble"): ("ICM-BBZ-bubble", "ICM · BBZ bubble"),
    ("ICM", "40%"): ("ICM-BBZ-40pct", "ICM · BBZ · 40% left"),
    ("ICM", "83%"): ("ICM-BBZ-83pct", "ICM · BBZ · 83% left"),
}

SUITS = "shdc"


def combos_of_class(cls):
    if len(cls) == 2:  # pair
        return [cls[0] + a + cls[0] + b
                for i, a in enumerate(SUITS) for b in SUITS[i + 1:]]
    hi, lo, kind = cls[0], cls[1], cls[2]
    if kind == "s":
        return [hi + s + lo + s for s in SUITS]
    return [hi + a + lo + b for a in SUITS for b in SUITS if a != b]


def node_actions(node, hero_stack):
    """BBZ node -> {action: combo:freq string} without fold."""
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
                cls = key.lstrip("_")
                for combo in combos_of_class(cls):
                    buckets[bucket].append(f"{combo}:{round(f, 4)}")
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


def main():
    wanted = None
    if "--products" in sys.argv:
        wanted = set(sys.argv[sys.argv.index("--products") + 1].split(","))
    with open(os.path.join(BBZ, "index.json")) as f:
        index = json.load(f)

    # line file -> {"title", "position", "stacks": {key: entry}}
    lines = defaultdict(lambda: {"title": None, "position": None,
                                 "stacks": {}})
    manifest = defaultdict(lambda: defaultdict(lambda: defaultdict(set)))
    skipped = defaultdict(int)
    n_entries = 0

    for meta in index:
        prod = (meta["product_name"], meta["players_left"])
        if prod not in PRODUCTS:
            continue
        if wanted and meta["product_name"] not in wanted:
            continue
        if meta["table_size"] != "8max" or "Equal" not in meta["stack_distribution"] \
                or "Limp" in meta["name"]:
            continue
        depth = int(re.search(r"AVG(\d+)", meta["avg_stack"]).group(1))
        stype, subtitle = PRODUCTS[prod]
        with open(os.path.join(BBZ, meta["path"])) as f:
            d = json.load(f)
        cols = [c.split("|") for c in d["columns"]]
        stacks = {pos: float(s) for pos, s in cols}
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
            for spot in hs:
                cls = classify(hero, spot)
                if not cls:
                    skipped[f"spot:{spot['name']}"] += 1
                    continue
                line_slug, title = cls
                slug, disp = POS[hero]
                node = d["nodes"][str(spot["nodeId"])]
                actions, sizings = node_actions(node, stacks[hero])
                key = f"{stype}-{depth}"
                entry = {"type": stype, "subtitle": subtitle, "stack": depth,
                         "actions": actions}
                if sizings:
                    entry["sizings"] = sizings
                fkey = f"{slug}/{line_slug}"
                lines[fkey]["title"] = title
                lines[fkey]["position"] = disp
                lines[fkey]["stacks"][key] = entry
                manifest[slug][line_slug][f"{stype}|{subtitle}"].add(depth)
                n_entries += 1

    os.makedirs(STORE, exist_ok=True)
    n_files = 0
    for fkey, data in sorted(lines.items()):
        order = {
            # tournament progression: more of the field left first, then
            # bubble, then the final table
            "cEV": 0, "ICM-BBZ-83pct": 1, "ICM-BBZ-40pct": 2,
            "ICM-BBZ-bubble": 3, "ICM-FT": 4,
        }
        stack_list = sorted(data["stacks"].values(),
                            key=lambda e: (order.get(e["type"], 9), -e["stack"]))
        out = {"title": data["title"], "position": data["position"],
               "stacks": stack_list}
        path = os.path.join(STORE, fkey + ".json")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(out, f, separators=(",", ":"))
        n_files += 1

    # navigation manifest
    m_out = {}
    for slug, lns in sorted(manifest.items()):
        m_out[slug] = {}
        for line, types in sorted(lns.items()):
            m_out[slug][line] = {
                "title": lines[f"{slug}/{line}"]["title"],
                "types": [
                    {"type": t.split("|")[0], "subtitle": t.split("|")[1],
                     "stacks": sorted(depths, reverse=True)}
                    for t, depths in sorted(types.items())
                ],
            }
    with open(os.path.join(STORE, "index.json"), "w") as f:
        json.dump(m_out, f, separators=(",", ":"))

    print(f"{n_files} line files, {n_entries} stack entries -> {STORE}")
    if skipped:
        print("skipped (no store-line mapping):")
        for k, v in sorted(skipped.items(), key=lambda x: -x[1])[:10]:
            print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
