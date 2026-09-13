#!/usr/bin/env python3
"""Query the cached GTO Wizard solutions library (imports/catalog.json).

Reads the local capture only — it never touches the network. To refresh the
catalog: python3 straddle-solutions/scripts/fetch_browser.py --catalog

Usage:
  gw_catalog.py gametypes [pattern]     list gametypes (name, players, configs)
  gw_catalog.py depths <gametype>       symmetric depths for a gametype
  gw_catalog.py configs <gametype> [--all]   stack configs (symmetric only
                                        unless --all)
"""

import json
import pathlib
import sys

CATALOG = pathlib.Path(__file__).resolve().parents[1] / "catalog.json"


def load():
    if not CATALOG.exists():
        sys.exit("no cached catalog — run: "
                 "python3 straddle-solutions/scripts/fetch_browser.py --catalog")
    return json.loads(CATALOG.read_text())["gametypes"]


def entry(gametypes, name):
    for g in gametypes:
        if g["name"] == name:
            return g
    close = [g["name"] for g in gametypes if name.split("_")[0].lower() in g["name"].lower()]
    sys.exit(f"unknown gametype {name}" + (f"; close: {', '.join(close[:8])}" if close else ""))


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    cmd, gametypes = sys.argv[1], load()

    if cmd == "gametypes":
        pattern = (sys.argv[2] if len(sys.argv) > 2 else "").lower()
        for g in gametypes:
            if pattern in g["name"].lower():
                print(f"{g['name']:<45} {g['variant']:<8} {g['format']:<6} "
                      f"{g['players']}p  {len(g['game_modes'])} configs")
    elif cmd == "depths":
        g = entry(gametypes, sys.argv[2] if len(sys.argv) > 2 else "")
        sym = sorted({gm["depth"] for gm in g["game_modes"]
                      if len(set(gm["stacks"])) == 1}, key=float)
        print(f"{g['name']} symmetric depths:", " ".join(sym))
    elif cmd == "configs":
        name = sys.argv[2] if len(sys.argv) > 2 else ""
        all_configs = "--all" in sys.argv
        g = entry(gametypes, name)
        for gm in sorted(g["game_modes"], key=lambda m: float(m["depth"])):
            if not all_configs and len(set(gm["stacks"])) > 1:
                continue
            kind = "SYM " if len(set(gm["stacks"])) == 1 else "ASYM"
            print(f"{kind} id={gm['id']:<6} depth={gm['depth']:<8} "
                  f"{'-'.join(gm['stacks'])}")
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
