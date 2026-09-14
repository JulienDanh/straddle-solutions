#!/usr/bin/env python3
"""Build bbz/catalog.json from the scraped BBZ solution files.

Usage:
  bbz_catalog.py                write catalog.json (default: ../bbz/catalog.json)
  bbz_catalog.py --json FILE    output path override

The catalog is parsed from the solution files themselves (not the scrape
index): per solution — position stacks, every table spot with its nodeId,
and every node's action list (action, amount, percentage). Spot-level
strategy is NOT copied; load the solution file for that. Aggregate
summaries (per product / players_left / table_size) are included for
browsing.
"""

import json
import os
import re
import sys
import time
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
BBZ = os.path.join(os.path.dirname(HERE), "bbz")


def parse_solution(path, meta):
    with open(path) as f:
        d = json.load(f)
    columns = d.get("columns", [])
    positions = {}
    for col in columns:
        pos, _, stack = col.partition("|")
        positions[pos] = stack
    table = d.get("table", {})
    nodes = d.get("nodes", {})
    referenced = set()
    spots = []
    for row in sorted(table, key=lambda k: int(k)):
        for ci, cell in enumerate(table[row]):
            hero = columns[ci].partition("|")[0] if ci < len(columns) else str(ci)
            for c in cell:
                # cells like {"name": "x"} are empty placeholders
                if not c.get("name") or c.get("name") == "x" or "nodeId" not in c:
                    continue
                nid = c["nodeId"]
                node = nodes.get(str(nid))
                actions = (
                    [
                        {
                            "action": p.get("action"),
                            "amount": p.get("amount"),
                            "percentage": p.get("percentage"),
                        }
                        for p in node.get("percentages", [])
                    ]
                    if node
                    else None
                )
                summary = {}
                if actions:
                    for a in actions:
                        try:
                            val = float(a.get("percentage"))
                        except (TypeError, ValueError):
                            continue
                        summary[a["action"]] = round(
                            summary.get(a["action"], 0.0) + val, 2
                        )
                spots.append(
                    {
                        "hero": hero,
                        "name": c["name"],
                        "group": c.get("group"),
                        "nodeId": nid,
                        "summary": summary or None,
                        "actions": actions,
                    }
                )
                referenced.add(str(nid))
    orphans = len([k for k in nodes if k not in referenced])
    return {
        "product": meta["product_name"],
        "solution_id": meta.get("solution_id"),
        "name": meta["name"],
        "path": meta["path"],
        "table_size": meta.get("table_size"),
        "players_left": meta.get("players_left"),
        "avg_stack": meta.get("avg_stack"),
        "stack_distribution": meta.get("stack_distribution"),
        "positions": positions,
        "spots": spots,
        "orphan_nodes": orphans,
    }


def main():
    out = sys.argv[sys.argv.index("--json") + 1] if "--json" in sys.argv else \
        os.path.join(BBZ, "catalog.json")
    idx_path = os.path.join(BBZ, "index.json")
    with open(idx_path) as f:
        index = json.load(f)

    solutions = []
    errors = []
    for meta in index:
        path = os.path.join(BBZ, meta["path"])
        try:
            solutions.append(parse_solution(path, meta))
        except Exception as e:  # noqa: BLE001 — record and continue
            errors.append({"path": meta["path"], "error": str(e)})

    # aggregate browsing view
    by_product = defaultdict(lambda: defaultdict(list))
    for s in solutions:
        by_product[s["product"]][s["players_left"]].append(s)
    products = {}
    for prod, by_pl in by_product.items():
        products[prod] = {
            pl: {
                "solutions": len(lst),
                "table_sizes": dict(Counter(s["table_size"] for s in lst)),
                "symmetric_depths": sorted(
                    {
                        int(s["avg_stack"].removeprefix("AVG"))
                        for s in lst
                        if s["stack_distribution"] == "Equal"
                        and s["avg_stack"].startswith("AVG")
                    }
                ),
                "stack_configs": sorted(
                    {s["stack_distribution"] for s in lst}
                ),
                "paths": [s["path"] for s in lst],
            }
            for pl, lst in by_pl.items()
        }

    spot_names = Counter(s["name"] for sol in solutions for s in sol["spots"])
    groups = Counter(s["group"] for sol in solutions for s in sol["spots"])
    catalog = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "source": "bbz",
        "total_solutions": len(solutions),
        "total_spots": sum(len(s["spots"]) for s in solutions),
        "distinct_spot_names": len(spot_names),
        "spot_groups": dict(groups),
        "products": products,
        "solutions": solutions,
    }
    if errors:
        catalog["errors"] = errors
    with open(out, "w") as f:
        json.dump(catalog, f, separators=(",", ":"))
    print(f"{len(solutions)} solutions, {catalog['total_spots']} spots, "
          f"{len(spot_names)} distinct spot names -> {out}")
    print(f"groups: {dict(groups)}")
    if errors:
        print(f"ERRORS: {len(errors)}")
        for e in errors[:5]:
            print(" ", e)


if __name__ == "__main__":
    main()
