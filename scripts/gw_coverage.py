#!/usr/bin/env python3
"""Generate coverage.html — a single-file report mapping what we have scraped
from GTO Wizard (solutions/), what made it into the range store
(packages/ranges/data/), and what the course still wants.

Usage:  python3 straddle-solutions/scripts/gw_coverage.py
Writes: straddle-solutions/coverage.html
"""

import datetime
import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
REPO = ROOT.parent
SOLUTIONS = ROOT / "solutions"
STORE = REPO / "packages" / "ranges" / "data"
CATALOG = ROOT / "catalog.json"
OUT = ROOT / "coverage.html"

SEATS = ["UTG", "UTG1", "LJ", "HJ", "CO", "BTN", "SB", "BB"]
SEAT_DIR = {"UTG": "utg", "UTG1": "utg1", "LJ": "lj", "HJ": "hj",
            "CO": "co", "BTN": "btn", "SB": "sb", "BB": "bb"}
OPENERS = SEATS[:7]

# gametype dir -> catalog gametype name
GAMETYPES = {
    "cev": "MTTGeneral_8m",
    "icm-8m-200ptbubblemid": "MTTGeneral_ICM8m200PTBUBBLEMID",
    "mttgeneral-icm-8m-200-ptft": "MTTGeneral_ICM8m200PTFT",
}

RFI_DEPTHS = [6, 8, 10, 13, 15, 20, 25, 30, 35, 40, 50, 60, 70, 80, 100]
VS_OPEN_DEPTHS = [10, 15, 20, 25, 30, 40, 50]
VS_3BET_DEPTHS = [40, 50]
LIMP_DEPTHS = [20, 25, 30, 40, 50, 70]
BUBBLE_SYMMETRIC = [20, 25, 30, 40]


def seat_index(name):
    return SEATS.index(name)


# ---------------------------------------------------------------- archive

def parse_archive():
    """Walk solutions/ into structured dicts."""
    rfi = {}          # (gametype, stacks, pos) -> True
    vsopen = {}       # (gametype, stacks, opener, defender) -> True
    vs3bet = {}       # (gametype, stacks, opener, raiser) -> True
    vslimp = {}       # (gametype, stacks, opener, defender) -> True
    flops = {}        # (gametype, stacks, line) -> {board_id: [node token lists]}
    files = 0
    for gt_dir in sorted(SOLUTIONS.iterdir()):
        if not gt_dir.is_dir() or gt_dir.name not in GAMETYPES:
            continue
        gt = gt_dir.name
        for stacks_dir in sorted(gt_dir.iterdir()):
            if not stacks_dir.is_dir():
                continue
            stacks = stacks_dir.name
            for cat_dir in sorted(stacks_dir.iterdir()):
                if not cat_dir.is_dir():
                    continue
                for f in sorted(p for p in cat_dir.iterdir() if p.is_file()):
                    files += 1
                    if cat_dir.name == "rfi":
                        rfi[(gt, stacks, f.stem.upper())] = True
                    elif cat_dir.name == "vs-open":
                        op, df = f.stem.split("-")
                        vsopen[(gt, stacks, op.upper(), df.upper())] = True
                    elif cat_dir.name == "vs-3bet":
                        op, r = f.stem.split("-")
                        vs3bet[(gt, stacks, op.upper(), r.upper())] = True
                    elif cat_dir.name == "vs-limp":
                        op, df = f.stem.split("-")
                        vslimp[(gt, stacks, op.upper(), df.upper())] = True
            # flops handled separately (flops/<line>/<file>)
            for line_dir in sorted(stacks_dir.glob("flops/*")):
                if not line_dir.is_dir():
                    continue
                key = (gt, stacks, line_dir.name)
                boards = flops.setdefault(key, {})
                # captures are usually .json but some older ones are
                # extensionless — take every regular file
                for f in sorted(p for p in line_dir.iterdir() if p.is_file()):
                    files += 1
                    toks = f.stem.split("-")
                    board = toks[0]
                    node = toks[1:]
                    boards.setdefault(board, []).append(node)
    return dict(rfi=rfi, vsopen=vsopen, vs3bet=vs3bet, vslimp=vslimp,
                flops=flops, files=files)


# ---------------------------------------------------------------- store

def parse_store():
    """Read packages/ranges/data into lookup structures."""
    rfi = {}       # (pos, depth) -> True        (cEV only)
    vsopen = {}    # (defender, opener, depth) -> True (cEV)
    vs3bet = {}    # (opener, raiser, depth) -> True (cEV)
    vslimp = {}    # (defender, opener, depth) -> True (cEV)
    flop_ids = set()  # postflop child ids present anywhere
    icm_depths = set()   # (type, pos-or-pair, depth) for ICM/ICM-FT
    cfg = {}             # config token -> store entry count
    icm_vo = set()       # (defender, opener, depth) ICM vs-open entries
    icm_v3 = set()       # (opener, 3-bettor, depth) ICM vs-3bet entries
    n_files = 0
    for f in STORE.glob("*/*.json"):
        n_files += 1
        pos_dir = f.parent.name
        line = f.stem
        try:
            d = json.loads(f.read_text())
        except Exception:
            continue
        for s in d.get("stacks", []):
            typ = s.get("type", "")
            depth = s.get("stack")
            if typ == "cEV":
                if line == "rfi":
                    rfi[(pos_dir.upper(), depth)] = True
                elif line.startswith("vs-3bet-"):
                    r = line[len("vs-3bet-"):]
                    vs3bet[(pos_dir.upper(), r.upper(), depth)] = True
                elif line == "vs-sb-limp":
                    vslimp[(pos_dir.upper(), "SB", depth)] = True
                elif line.startswith("vs-"):
                    op = line[len("vs-"):].replace("-raise", "")
                    vsopen[(pos_dir.upper(), op.upper(), depth)] = True
            else:
                icm_depths.add((typ, f"{pos_dir}/{line}", depth))
                if typ == "ICM":
                    if line.startswith("vs-3bet-"):
                        icm_v3.add((pos_dir.upper(),
                                    line[len("vs-3bet-"):].upper(), depth))
                    elif line == "vs-sb-limp":
                        pass
                    elif line == "vs-sb-raise":
                        icm_vo.add((pos_dir.upper(), "SB", depth))
                    elif line.startswith("vs-"):
                        op = line[len("vs-"):]
                        icm_vo.add((pos_dir.upper(), op.upper(), depth))
            if s.get("config"):
                cfg["-".join(str(x) for x in s["config"])] = cfg.get("-".join(str(x) for x in s["config"]), 0) + 1
            for child in s.get("postflop", []) or []:
                flop_ids.add(child.get("id", ""))
    return dict(rfi=rfi, vsopen=vsopen, vs3bet=vs3bet, vslimp=vslimp,
                flop_ids=flop_ids, icm=icm_depths, files=n_files, configs=cfg,
                icm_vo=icm_vo, icm_v3=icm_v3)


# ---------------------------------------------------------------- catalog

def parse_catalog():
    c = json.loads(CATALOG.read_text())
    sym = {}    # gametype -> set of int depths with a symmetric mode
    asym = {}   # gametype -> list of asymmetric config tokens
    for g in c["gametypes"]:
        name = g["name"]
        if name not in GAMETYPES.values():
            continue
        s, a = set(), []
        for m in g["game_modes"]:
            depth = m["depth"]
            if set(m["stacks"]) == {depth}:
                s.add(int(float(depth)))
            else:
                a.append("-".join(st.removesuffix(".125") for st in m["stacks"]))
        sym[name] = s
        asym[name] = sorted(set(a))
    return sym, asym


# ---------------------------------------------------------------- board utils

def board_ranks_id(board):
    """kh8h3c -> k83 (ranks only, lowercased, incl. turn/river cards)."""
    ranks = []
    for i in range(0, len(board), 2):
        r = board[i].lower()
        ranks.append(r)
    return "".join(ranks)


def norm_id(store_id):
    """Store ids sometimes spell ten as '10' (j105) — normalize to 't'."""
    return store_id.replace("10", "t")


def id_matches(my_id, store_id):
    """Fuzzy id match: store ids carry turn/river rank chars, mine may not."""
    s = norm_id(store_id)
    return s == my_id or s.startswith(my_id) or my_id.startswith(s)


def board_street(board):
    n = len(board) // 2
    return {3: "F", 4: "T", 5: "R"}.get(n, "?")


# ---------------------------------------------------------------- rendering

CSS = """
:root { color-scheme: dark; }
* { box-sizing: border-box; }
body { margin: 0; font: 14px/1.5 -apple-system, "Segoe UI", Roboto, sans-serif;
       background: #0f1115; color: #d7dae0; padding: 0 0 80px; }
a { color: #7ab7ff; text-decoration: none; }
h1 { font-size: 20px; margin: 0; }
h2 { font-size: 16px; margin: 28px 0 8px; color: #fff;
     border-bottom: 1px solid #262b33; padding-bottom: 6px; }
header { padding: 24px 28px 12px; max-width: 1280px; margin: 0 auto; }
nav { max-width: 1280px; margin: 0 auto; padding: 0 28px 10px; }
nav a { margin-right: 12px; font-size: 13px; }
nav a:hover { text-decoration: underline; }
.navgroup { display: inline-block; margin: 0 10px 0 0; padding: 1px 8px;
            border-radius: 6px; background: #1c2129; color: #7d8794;
            font-size: 10.5px; font-weight: 700; letter-spacing: .4px; }
h2 { margin-top: 44px; }
h3 { margin-top: 20px; }
main { max-width: 1280px; margin: 0 auto; padding: 0 28px; }
.sub { color: #8b93a1; font-size: 12px; margin-top: 4px; }
.cards { display: flex; gap: 12px; flex-wrap: wrap; margin: 14px 0 4px; }
.card { background: #161a21; border: 1px solid #262b33; border-radius: 10px;
        padding: 10px 16px; min-width: 130px; }
.card .n { font-size: 22px; color: #fff; font-weight: 600; }
.card .l { font-size: 11px; color: #8b93a1; }
table { border-collapse: collapse; width: 100%; margin: 8px 0 4px; }
th, td { border: 1px solid #23272f; padding: 4px 8px; text-align: left;
         font-size: 12px; }
th { background: #161a21; color: #aab2c0; font-weight: 600; position: sticky;
     top: 0; }
td.dim { color: #6b7280; }
.ok    { background: #10391f; color: #6ee7a0; }
.raw   { background: #16324a; color: #7ab7ff; }
.miss  { background: #3a2c10; color: #fbbf24; }
.na    { background: #1a1d23; color: #5b6270; }
.bad   { background: #3a1512; color: #f87171; }
.chip { display: inline-block; padding: 0 6px; margin: 1px 2px; border-radius: 5px;
        font-size: 11px; font-weight: 600; }
.chip.ok, .chip.raw, .chip.miss, .chip.na { border: none; }
.legend { display: flex; gap: 10px; flex-wrap: wrap; margin: 6px 0 14px;
          font-size: 12px; color: #8b93a1; }
.legend .chip { cursor: default; }
details { background: #161a21; border: 1px solid #262b33; border-radius: 10px;
          padding: 8px 14px; margin: 8px 0; }
summary { cursor: pointer; font-weight: 600; color: #e5e7eb; }
code, .mono { font-family: ui-monospace, "SF Mono", Menlo, monospace;
              font-size: 12px; color: #9fd0ff; }
.pill { display: inline-block; padding: 1px 8px; border-radius: 999px;
        font-size: 11px; font-weight: 600; }
.small { font-size: 12px; color: #8b93a1; }
.board { font-family: ui-monospace, Menlo, monospace; color: #fff;
         font-weight: 600; letter-spacing: .3px; }
"""


def esc(x):
    return html.escape(str(x))


def chip(depth, cls, title=""):
    t = f' title="{esc(title)}"' if title else ""
    return f'<span class="chip {cls}"{t}>{esc(depth)}</span>'


def cell_state(raw, store):
    if raw and store:
        return "ok"
    if raw:
        return "raw"
    if store:
        return "raw"
    return "miss"


def legend():
    return (
        '<div class="legend">'
        '<span class="chip ok">12</span> scraped + in store'
        '<span class="chip raw">12</span> scraped, not yet in store'
        '<span class="chip miss">12</span> missing (fetchable)'
        '<span class="chip na">12</span> not in Wizard catalog'
        "</div>"
    )


def render_rfi(arch, store, cat):
    rows = []
    available = cat[GAMETYPES["cev"]]
    total = covered = 0
    for pos in OPENERS:
        cells = []
        for d in RFI_DEPTHS:
            total += 1
            raw = ("cev", str(d), pos) in arch["rfi"]
            st = (pos, d) in store["rfi"]
            if raw:
                covered += 1
            cls = cell_state(raw, st)
            av = d in available
            if not raw and not av:
                cls = "na"
            cells.append(chip(d, cls, f"{pos} RFI @ {d}bb"))
        rows.append(f"<tr><th>{pos} RFI</th>{''.join(f'<td>{c}</td>' for c in cells)}</tr>")
    pct = f"{100 * covered // total}%"
    return f"""
<h2 id="rfi">cEV RFI depth ladder <span class="pill miss">{covered}/{total} covered</span></h2>
<p class="small">Every opener at every depth the Wizard catalog sells (6&ndash;100bb symmetric).
Depth ladder mirrored by the store's <code>rfi.json</code> <code>stacks</code> entries.</p>
{legend()}
<table><tr><th>Line</th>{''.join(f'<th>{d}</th>' for d in RFI_DEPTHS)}</tr>
{''.join(rows)}</table>"""


def pair_defenders(opener):
    return SEATS[seat_index(opener) + 1:]


def render_vsopen(arch, store, cat):
    cols = SEATS[1:]  # defender columns: UTG1..BB
    headers = "".join(f"<th>{c}</th>" for c in cols)
    rows = []
    total = covered = 0
    for op in OPENERS:
        cells = []
        for df in cols:
            if seat_index(df) > seat_index(op):
                chips = []
                for d in VS_OPEN_DEPTHS:
                    total += 1
                    raw = ("cev", str(d), op, df) in arch["vsopen"]
                    st = (df, op, d) in store["vsopen"]
                    if raw:
                        covered += 1
                    chips.append(chip(d, cell_state(raw, st), f"{df} vs {op} open @ {d}bb"))
                cells.append(f"<td>{''.join(chips)}</td>")
            else:
                cells.append("<td class='dim'>&mdash;</td>")
        rows.append(f"<tr><th>{esc(op)} opens</th>{''.join(cells)}</tr>")
    return f"""
<h2 id="vsopen">cEV vs-open (defend) matrix <span class="pill miss">{covered}/{total} scraped</span></h2>
<p class="small">Opener &times; every in-position defender (incl. SB/BB), depths
10&ndash;50bb per cell. The archive only covers BB/SB defenders plus
<code>utg-btn</code> and <code>utg-hj</code> &mdash; the in-position cEV defends feeding the Range
Library's <code>btn/vs-co</code> style lines are the big hole.</p>
{legend()}
<table><tr><th>Opener</th>{headers}</tr>
{''.join(rows)}</table>"""


def render_vs3bet(arch, store, cat):
    cols = SEATS[1:]  # 3-bettor columns: UTG1..BB
    headers = "".join(f"<th>{c}<br><span class='small'>40/50</span></th>" for c in cols)
    rows = []
    total = covered = 0
    for op in OPENERS[:6]:
        cells = []
        for r in cols:
            if seat_index(r) > seat_index(op):
                chips = []
                for d in VS_3BET_DEPTHS:
                    total += 1
                    raw = ("cev", str(d), op, r) in arch["vs3bet"]
                    st = (op, r, d) in store["vs3bet"]
                    if raw:
                        covered += 1
                    chips.append(chip(d, cell_state(raw, st), f"{op} open, {r} 3-bet @ {d}bb"))
                cells.append(f"<td>{''.join(chips)}</td>")
            else:
                cells.append("<td class='dim'>&mdash;</td>")
        rows.append(f"<tr><th>{esc(op)} opens</th>{''.join(cells)}</tr>")
    return f"""
<h2 id="vs3bet">cEV vs-3bet matrix <span class="pill miss">{covered}/{total} scraped</span></h2>
<p class="small">Opener's response to a 3-bet from any later seat, 40/50bb per cell.
Only UTG vs BB/BTN/HJ is scraped; utg1/lj/hj/co/btn opens facing a 3-bet
(System 12 territory) are open.</p>
{legend()}
<table><tr><th>Opener</th>{headers}</tr>
{''.join(rows)}</table>"""


def render_limp(arch, store):
    cells = []
    for d in LIMP_DEPTHS:
        raw = ("cev", str(d), "SB", "BB") in arch["vslimp"]
        st = ("BB", "SB", d) in store["vslimp"]
        cells.append(chip(d, cell_state(raw, st), f"BB vs SB limp @ {d}bb"))
    return f"""
<h2 id="limp">cEV vs-limp (BB vs SB limp)</h2>
<p class="small">Complete except 60bb (not in the course). 70bb exists raw;
System 3 content sits on 20&ndash;40.</p>
<table><tr><th>Depth</th>{''.join(f'<th>{d}</th>' for d in LIMP_DEPTHS)}</tr>
<tr><th>BB defend</th>{''.join(f'<td>{c}</td>' for c in cells)}</tr></table>"""


GAPS = [
    # status is COMPUTED: plan-linked gaps via the plan entry, probe gaps
    # via an explicit archive check, static notes where nothing to fetch.
    dict(sys="S12", spot="963 vs BTN 3-bet @40 (jam/call)",
         plan="s12-963",
         note="<code>r2-f-f-f-f-r6.5-f-f-c</code> line exists with k84/984; the 963 board was fetched by the grid sweep",
         fetch="--rfi UTG --vs-3bet BTN --depth 40 --board 9h6c3d --cbet"),
    dict(sys="S12", spot="752 vs BTN 3-bet @25 (AQo)",
         plan="s12-752",
         note="the 3-bet-call flop line is not scraped at 25bb",
         fetch="--rfi UTG --vs-3bet BTN --depth 25 --board 7h5c2d --cbet"),
    dict(sys="S2", spot="A-J-J paired @50 (BTN c-bet)",
         plan="s2-ajj",
         note="paired ace-high: solver checks ~50%",
         fetch="--rfi BTN --depth 50 --board AhJdJc --cbet"),
    dict(sys="S2", spot="K-J-2 @50 (BTN c-bet)",
         plan="s2-kj2",
         note="K-high with deuce: still 100%",
         fetch="--rfi BTN --depth 50 --board KdJh2c --cbet"),
    dict(sys="S2", spot="K-6-3 two-tone @50 (BTN c-bet)",
         plan="s2-k63",
         note="two low cards interact: mix",
         fetch="--rfi BTN --depth 50 --board Kh6h3c --cbet"),
    dict(sys="S2", spot="5-4-3 wheel @50 (BTN misses)",
         plan="s2-543",
         note="no 8+ on board: BTN checks more, bets bigger",
         fetch="--rfi BTN --depth 50 --board 5h4h3c --cbet"),
    dict(sys="S2", spot="7-4-2 brick @50 (BTN misses)",
         plan="s2-742",
         note="rainbow miss board",
         fetch="--rfi BTN --depth 50 --board 7c4h2d --cbet"),
    dict(sys="S10", spot="957 &rarr; 5 turn, EP vs BTN caller @100 (block-bet)",
         probe=("cev", 100, "r2.1-f-f-f-f-f-c-f", "9h5d7c"),
         note="the caller-IP line is now scraped by the grid sweep; 957 is a non-deck board",
         fetch="--history-spot 9 --preflop-actions R2.1-F-F-F-F-F-C-F --board 9h5d7c --flop-actions X --depth 100"),
    dict(sys="S10", spot="AQ on J97 &rarr; T &rarr; 9 river, EP vs SB @80",
         probe=("cev", 80, "r2-f-f-f-f-f-c-f", "jh9c7d"),
         note="the full river chain (J97 + Th + 9d) is already archived",
         fetch="(archived: jh9c7d[-th][-9d] chains on r2-f-f-f-f-f-c-f @80)"),
    dict(sys="S4", spot="Q106cc &rarr; Tc river (one-club bluff, BB vs SB)",
         plan="s4-q106",
         note="BB stab chain archived on the SB-open line; store wiring pending",
         fetch="(archived: qctd6c chain on f-f-f-f-f-f-r3-c @40)"),
    dict(sys="S4", spot="AKQJ T board (EP vs BTN caller)",
         plan="s4-akq",
         note="caller-IP chain archived (app sells EP-vs-BTN, not EP-vs-CO)",
         fetch="(archived: askdqc chain on r2.1-f-f-f-f-f-c-f @100)"),
    dict(sys="S11", spot="A972K and 9642A, both 4-way",
         static="blocked — multiway postflop unproven in this gametype; verify catalog before scraping",
         note="4-way lines need their own naming",
         fetch=""),
    dict(sys="S11", spot="K7 on A73 2 K (BTN vs BB)",
         static="no scrape needed — the solved a732k flop is already in the store",
         note="page wiring, not data",
         fetch=""),
    dict(sys="S12", spot="EP vs BTN 3-bet ICM variants",
         static="closed — the vs-3bet sweep filled every opener x 3-bettor (cEV 40/50 + ICM 20-40)",
         note="cEV walks for utg1/lj/hj/co/btn openers done",
         fetch=""),
]


def gap_status(g, arch, store):
    if "static" in g:
        return g["static"], "na"
    if "plan" in g:
        from gw_flop_plan import PLAN
        e = next(x for x in PLAN if x["id"] == g["plan"])
        scraped, in_store = flop_entry_status(e, arch, store)
        if scraped and in_store:
            return "have — solved &amp; stored", "ok"
        if scraped:
            return "scraped — store wiring pending", "raw"
        return "missing — fetchable", "miss"
    gt, depth, line, board = g["probe"]
    d = SOLUTIONS / gt / str(depth) / "flops" / line
    mid = board_ranks_id(board)
    hit = any(board_ranks_id(q.name.split("-")[0].removesuffix(".json")) == mid
              for q in d.iterdir()) if d.is_dir() else False
    return ("have — archived" if hit else "missing — fetchable", "ok" if hit else "miss")


def render_gaps(arch, store):
    rows = []
    n_missing = 0
    for g in GAPS:
        text, cls = gap_status(g, arch, store)
        if cls == "miss":
            n_missing += 1
        badge = f'<span class="chip {cls}">{text}</span>'
        fetch_html = (f"<code>{esc(g['fetch'])}</code>" if g.get("fetch")
                      else '<span class="dim">&mdash;</span>')
        rows.append(
            f"<tr><td><b>{esc(g['sys'])}</b></td><td>{g['spot']}</td>"
            f"<td class='small'>{g['note']}</td><td>{badge}</td>"
            f"<td>{fetch_html}</td></tr>")
    return f"""
<h2 id="gaps">Course gaps <span class="pill miss">{n_missing} fetchable</span></h2>
<p class="small">The walkthrough-only examples the study pages render as
<code>HandExample</code> cards. Statuses are computed live from the archive and
the range store — scrape or wire one and it flips on the next report run.</p>
<table><tr><th>System</th><th>Spot</th><th>Why</th><th>Status</th><th>Fetch</th></tr>
{''.join(rows)}</table>"""


def render_postflop(arch, store):
    total_flop = total_turn = total_river = 0
    sections = []
    by_gt = {}
    for (gt, stacks, line), boards in arch["flops"].items():
        by_gt.setdefault(gt, {}).setdefault(stacks, {})[line] = boards
    for gt in sorted(by_gt):
        for stacks in sorted(by_gt[gt], key=lambda s: (len(s), [int(x) for x in s.split("-")])):
            lines = by_gt[gt][stacks]
            parts = []
            for line in sorted(lines):
                chips = []
                for board, nodes in lines[line].items():
                    total_flop += 1
                    street = board_street(board)
                    if street == "T":
                        total_turn += 1
                    elif street == "R":
                        total_river += 1
                    mid = board_ranks_id(board)
                    in_store = any(id_matches(mid, sid)
                                   for sid in store["flop_ids"])
                    cls = "ok" if in_store else "raw"
                    node_txt = esc("&rarr;".join("/".join(n) if isinstance(n, list) else str(n) for n in nodes))
                    chips.append(
                        f'<span class="chip {cls}" title="flop node chain: {node_txt}">'
                        f'<span class="board">{esc(board)}</span></span>')
                parts.append(
                    f"<div style='margin:6px 0'><code>{esc(line)}</code><br>"
                    f"{''.join(chips)}</div>")
            label = stacks if stacks == str(int(stacks)) else stacks
            sections.append(
                f"<details><summary>{esc(gt)} &middot; stacks {esc(label)} "
                f"<span class='small'>({len(lines)} lines)</span></summary>"
                f"{''.join(parts)}</details>")
    return f"""
<h2 id="postflop">Postflop archive <span class="pill raw">{total_flop} board-nodes</span></h2>
<p class="small">{total_flop - total_turn - total_river} flop nodes, {total_turn} turn,
{total_river} river captures, grouped by preflop line. Green chips are materialized
in the store (postflop children); blue chips are scraped but not yet converted.
Hover a chip for its node chain.</p>
{''.join(sections)}"""


def flop_entry_status(e, arch, store):
    """(scraped, in_store) for a plan entry: board ranks under the entry's
    gametype + depth + line (line ignored when walk-derived)."""
    mid = board_ranks_id(e["board"])
    for (gt, stacks, line), boards in arch["flops"].items():
        if gt != e["gt"]:
            continue
        if e["depth"] is not None and stacks != str(e["depth"]):
            continue
        if e["line"] is not None and line != e["line"]:
            continue
        for b in boards:
            if board_ranks_id(b) == mid or board_ranks_id(b).startswith(mid):
                in_store = any(id_matches(mid, sid) for sid in store["flop_ids"])
                return True, in_store
    return False, False


BUBBLE_DEPTHS = [20, 25, 30, 40]


def render_icm_sym(arch, store):
    """Symmetric bubble ICM: vs-open and vs-3bet matrices per depth."""
    gt = "icm-8m-200ptbubblemid"

    def depth_chips(have, stored):
        chips = []
        for d in BUBBLE_DEPTHS:
            if have and stored:
                chips.append(chip(d, "ok", f"@{d}bb in archive + store"))
            elif have:
                chips.append(chip(d, "raw", f"@{d}bb archived, store pending"))
            else:
                chips.append(chip(d, "miss", f"@{d}bb missing"))
        return chips

    # vs-open matrix
    cols = SEATS[1:]
    heads = "".join(f"<th>{c}</th>" for c in cols)
    rows = []
    n_ok = n_have = n_all = 0
    for op in OPENERS:
        cells = []
        for df in cols:
            if seat_index(df) > seat_index(op):
                chips = depth_chips(
                    [d for d in BUBBLE_DEPTHS
                     if (gt, str(d), op, df) in arch["vsopen"]],
                    [d for d in BUBBLE_DEPTHS
                     if (df, op, d) in store["icm_vo"]])
                have = any(c.startswith('20') or True for c in chips)  # placeholder
                got = sum(1 for d in BUBBLE_DEPTHS
                          if (gt, str(d), op, df) in arch["vsopen"])
                st = sum(1 for d in BUBBLE_DEPTHS
                         if (df, op, d) in store["icm_vo"])
                n_all += len(BUBBLE_DEPTHS)
                n_have += got
                n_ok += st
                cells.append(f"<td>{''.join(chips)}</td>")
            else:
                cells.append("<td class='dim'>&mdash;</td>")
        rows.append(f"<tr><th>{esc(op)} opens</th>{''.join(cells)}</tr>")
    vo = (f"""<h3>Bubble symmetric vs-open <span class="pill miss">{n_ok}/{n_all} archived+stored</span></h3>
<p class="small">Every opener x in-position defender on the 200-man bubble at the four
symmetric depths. Green = archived and imported into the store; blue =
archived, store pending.</p>
{legend()}
<table><tr><th>Opener</th>{heads}</tr>
{''.join(rows)}</table>""")

    # vs-3bet matrix
    heads3 = "".join(f"<th>{c}</th>" for c in cols)
    rows3 = []
    m_ok = m_have = m_all = 0
    for op in OPENERS[:6]:
        cells = []
        for r in cols:
            if seat_index(r) > seat_index(op):
                chips = depth_chips(
                    [d for d in BUBBLE_DEPTHS
                     if (gt, str(d), op, r) in arch["vs3bet"]],
                    [d for d in BUBBLE_DEPTHS
                     if (op, r, d) in store["icm_v3"]])
                got = sum(1 for d in BUBBLE_DEPTHS
                          if (gt, str(d), op, r) in arch["vs3bet"])
                st = sum(1 for d in BUBBLE_DEPTHS
                         if (op, r, d) in store["icm_v3"])
                m_all += len(BUBBLE_DEPTHS)
                m_have += got
                m_ok += st
                cells.append(f"<td>{''.join(chips)}</td>")
            else:
                cells.append("<td class='dim'>&mdash;</td>")
        rows3.append(f"<tr><th>{esc(op)} opens</th>{''.join(cells)}</tr>")
    v3 = (f"""<h3>Bubble symmetric vs-3bet <span class="pill miss">{m_ok}/{m_all} archived+stored</span></h3>
<p class="small">Opener's response to a 3-bet from any later seat, on the bubble.
The BTN-vs-SB/BB cells are the known gap (BTN opens facing 3-bets were
never walked on the bubble gametype).</p>
{legend()}
<table><tr><th>Opener</th>{heads3}</tr>
{''.join(rows3)}</table>""")

    return f"""
<h2 id="icmsym">ICM symmetric (bubble) <span class="pill raw">{n_have}/{n_all} vs-open &middot; {m_have}/{m_all} vs-3bet archived</span></h2>
<p class="small">The 200-man bubble gametype's symmetric-depth defend matrices — what
BM1&ndash;BM7 are built on. Depth chips per pair; the asymmetric configs are
in the Asymmetric ICM section below.</p>
{vo}
{v3}"""


def render_asym(arch, store, cat, asym_catalog):
    """Asymmetric ICM configs: coverage per catalog config, archive + store."""
    def frac(n, m):
        return f"{n}/{m}"
    parts = []
    for gt_name, gt_dir in (("MTTGeneral_ICM8m200PTBUBBLEMID", "icm-8m-200ptbubblemid"),
                            ("MTTGeneral_ICM8m200PTFT", "mttgeneral-icm-8m-200-ptft")):
        tokens = asym_catalog.get(gt_name, [])
        rows = []
        touched = complete = 0
        for tok in tokens:
            stacks = tok.split("-")
            hero_stack = min(int(x) for x in stacks)
            # archive coverage per config
            rfi_n = sum(1 for (g, st, pos) in arch["rfi"] if g == gt_dir and st == tok)
            vo_n = sum(1 for (g, st, o, d) in arch["vsopen"] if g == gt_dir and st == tok)
            t3_n = sum(1 for (g, st, o, r) in arch["vs3bet"] if g == gt_dir and st == tok)
            st_n = store["configs"].get(tok, 0)
            total = rfi_n + vo_n + t3_n
            if total or st_n:
                touched += 1
            if rfi_n >= 7 and vo_n >= 10:
                complete += 1
            if not total and not st_n:
                cls, badge = "na", '<span class="chip na">0</span>'
            else:
                f = (rfi_n / 7 + vo_n / 28 + t3_n / 27) / 3
                cls = ("ok" if f > 0.75 else "raw" if f > 0.25 else "miss")
                badge = (f'<span class="chip {cls}" title="rfi {rfi_n}/7, vs-open {vo_n}/28, '
                         f'vs-3bet {t3_n}/27, store {st_n}">{frac(rfi_n, 7)} / '
                         f'{frac(vo_n, 28)} / {frac(t3_n, 27)}</span>')
            rows.append(
                f"<tr><td><code>{esc(tok)}</code><br>"
                f"<span class='small'>min stack {hero_stack}bb</span></td>"
                f"<td>{badge}</td>"
                f"<td>{st_n}</td></tr>")
        label = "bubble" if "BUBBLE" in gt_name else "final table"
        parts.append(f"""
<h3>{label} <span class="pill miss">{touched}/{len(tokens)} configs touched, {complete} near-complete</span></h3>
<details><summary>all {len(tokens)} configs</summary>
<table><tr><th>Config (UTG&hellip;BB)</th><th>RFI / vs-open / vs-3bet archived</th><th>store entries</th></tr>
{''.join(rows)}</table></details>""")
    return f"""
<h2 id="asym">Asymmetric ICM <span class="pill raw">per-config coverage</span></h2>
<p class="small">The bubble and final-table asymmetric stack configs from the
catalog — one row per config, archive coverage by category (RFI seats,
vs-open pairs, vs-3bet pairs) plus how many entries the range store carries.
Green = well covered, blue = partial, amber = thin, gray = untouched.</p>
{''.join(parts)}"""


def render_flopdeck(arch, store):
    """The study deck: 14 memorizable archetype boards vs their solves."""
    from gw_flop_plan import DECK, DECK_LINKS, PLAN
    by_id = {e["id"]: e for e in PLAN}
    rows = []
    n_have = 0
    last_group = None
    for d in DECK:
        chips = []
        have = False
        for pid in DECK_LINKS[d["id"]]:
            e = by_id[pid]
            scraped, in_store = flop_entry_status(e, arch, store)
            label = f"{e['sys']} {e['depth']}bb" if e["depth"] else f"{e['sys']} ICM"
            if scraped and in_store:
                chips.append(f'<span class="chip ok">{esc(label)}</span>')
                have = True
            elif scraped:
                chips.append(f'<span class="chip raw">{esc(label)}</span>')
                have = True
            else:
                chips.append(f'<span class="chip miss">{esc(label)}</span>')
        if have:
            n_have += 1
        group = d["group"] if d["group"] != last_group else ""
        last_group = d["group"]
        rows.append(
            f"<tr><td><b>{esc(group)}</b></td>"
            f"<td><span class='board'>{esc(d['board'])}</span><br>"
            f"<span class='small'>{esc(d['label'])}</span></td>"
            f"<td class='small'>{esc(d['rule'])}</td>"
            f"<td>{''.join(chips)}</td></tr>")
    return f"""
<h2 id="deck">Study deck <span class="pill miss">{n_have}/{len(DECK)} solved</span></h2>
<p class="small">The overall universe, human-memorizable: {len(DECK)} archetype boards in three
groups. Every flop maps to one of these textures; every system lesson is an
overlay (position, stack, pot type), never a new board. Chips show where each
archetype is solved (system + depth); amber = planned but not fetched yet.</p>
<table><tr><th>Group</th><th>Board</th><th>Rule (the flashcard)</th><th>Solves</th></tr>
{''.join(rows)}</table>"""


def render_deckmatrix(arch, store):
    """Deck archetypes x situations: the full-deck study matrix."""
    from gw_flop_plan import DECK, SITUATIONS, DECK_MATRIX, PLAN
    by_id = {e["id"]: e for e in PLAN}
    heads = "".join(
        f"<th>{esc(t['id'])}<br><span class='small'>{esc(t['label'])}</span>"
        f"<br><span class='small'>{esc(t['sys'])}</span></th>" for t in SITUATIONS)
    rows = []
    n_solved = n_planned = 0
    for d in DECK:
        cells = []
        for t in SITUATIONS:
            pids = DECK_MATRIX.get((d["id"], t["id"]))
            if not pids:
                cells.append("<td class='dim'>&mdash;</td>")
                continue
            chips = []
            for pid in pids:
                e = by_id[pid]
                scraped, in_store = flop_entry_status(e, arch, store)
                short = (f"{e['sys']} {e['depth']}" if e["depth"]
                         else f"{e['sys']} ICM")
                if scraped and in_store:
                    chips.append(chip(short, "ok", f"{e['board']} — {e['why']}"))
                    n_solved += 1
                elif scraped:
                    chips.append(chip(short, "raw", f"{e['board']} — {e['why']}"))
                    n_solved += 1
                else:
                    chips.append(chip(short, "miss", f"{e['board']} — {e['why']}"))
                    n_planned += 1
            cells.append(f"<td>{''.join(chips)}</td>")
        rows.append(
            f"<tr><th><span class='board'>{esc(d['board'])}</span><br>"
            f"<span class='small'>{esc(d['label'])}</span></th>{''.join(cells)}</tr>")
    return f"""
<h2 id="deckmatrix">Deck &times; situations <span class="pill miss">{n_solved} solved / {n_planned} planned</span></h2>
<p class="small">The full-deck study target: 15 archetypes &times; 11 situations. A dash is a
deliberate blank — that overlay does not change the lesson. Chips show the
solves behind each cell (hover for the board and lesson); amber = in the
plan, not fetched yet.</p>
<div style="overflow-x:auto">
<table><tr><th>Board</th>{heads}</tr>
{''.join(rows)}</table></div>"""


def render_flopplan(arch, store):
    """The flop universe (gw_flop_plan) vs archive + store."""
    from gw_flop_plan import core_plan, extended_plan
    def rows_for(plan):
        rows = []
        n_ok = n_miss = 0
        for e in plan:
            mid = board_ranks_id(e["board"])
            lines_hit = []
            for (gt, stacks, line), boards in arch["flops"].items():
                if gt != e["gt"]:
                    continue
                if e["depth"] is not None and stacks != str(e["depth"]):
                    continue
                if e["line"] is not None and line != e["line"]:
                    continue
                for b in boards:
                    if board_ranks_id(b) == mid or board_ranks_id(b).startswith(mid):
                        lines_hit.append(line)
            scraped = bool(lines_hit)
            in_store = any(id_matches(mid, sid) for sid in store["flop_ids"])
            if scraped:
                n_ok += 1
            else:
                n_miss += 1
            if scraped and in_store:
                badge = '<span class="chip ok">have</span>'
            elif scraped:
                badge = '<span class="chip raw">scraped</span>'
            else:
                badge = f'<span class="chip miss">P{e["prio"]}</span>'
            depth = f"{e['depth']}bb" if e["depth"] else (e["stacks"] or "")
            line_html = (f"<code>{esc(e['line'])}</code>" if e["line"]
                         else '<span class="dim">walk-derived</span>')
            rows.append(
                f"<tr><td><b>{esc(e['sys'])}</b></td>"
                f"<td><span class='board'>{esc(e['board'])}</span>"
                f"<br><span class='small'>{esc(e['cls'])}</span></td>"
                f"<td class='small'>{esc(e['why'])}</td>"
                f"<td>{esc(depth)}<br>{line_html}</td>"
                f"<td>{badge}</td></tr>")
        return rows, n_ok, n_miss
    core_rows, c_ok, c_miss = rows_for(core_plan())
    ext_rows, x_ok, x_miss = rows_for(extended_plan())
    def table(rows):
        return ("<table><tr><th>System</th><th>Board</th><th>Why</th>"
                "<th>Depth / line</th><th>Status</th></tr>"
                + "".join(rows) + "</table>")
    return f"""
<h2 id="flopplan">Flop plan <span class="pill miss">core {c_ok}/{c_ok + c_miss} have</span></h2>
<p class="small">The <b>core learn set</b>: one board per distinct decision the
transcripts teach — every bucket, contrast pair and named risk factor, nothing
twice. Extended boards (26 more) are variants of lessons below and stay in
<code>scripts/gw_flop_plan.py</code>. P1/P3 chips are the fetch priorities.</p>
{table(core_rows)}
<details><summary>Extended universe <span class="small">({x_ok}/{x_ok + x_miss} have)</span></summary>
{table(ext_rows)}
</details>"""


def render_icm(arch, store, cat, n_bubble_asym, n_ft_asym):
    gt = "icm-8m-200ptbubblemid"
    n_ok = sum(1 for d in BUBBLE_DEPTHS for pos in OPENERS
               if (gt, str(d), pos) in arch["rfi"])
    ft_cells = sum(1 for (g, st, pos) in arch["rfi"]
                   if g == "mttgeneral-icm-8m-200-ptft"
                   and "-" not in st)
    # bubble symmetric
    rows = []
    total = covered = 0
    for pos in OPENERS:
        cells = []
        for d in BUBBLE_SYMMETRIC:
            total += 1
            raw = ("icm-8m-200ptbubblemid", str(d), pos) in arch["rfi"]
            if raw:
                covered += 1
            cells.append(chip(d, cell_state(raw, False), f"bubble {pos} RFI @ {d}bb"))
        rows.append(f"<tr><th>{pos} RFI</th>{''.join(f'<td>{c}</td>' for c in cells)}</tr>")
    bubble_dirs = set()
    gt = "icm-8m-200ptbubblemid"
    for (g, stacks, *_) in arch["rfi"]:
        if g == gt and "-" in stacks:
            bubble_dirs.add(stacks)
    n_asym_scraped = len(bubble_dirs)
    # FT symmetric
    ft_name = GAMETYPES["mttgeneral-icm-8m-200-ptft"]
    ft_depths = sorted(cat.get(ft_name, set()))
    ft_rows = []
    for pos in OPENERS:
        cells = []
        for d in ft_depths:
            raw = ("mttgeneral-icm-8m-200-ptft", str(d), pos) in arch["rfi"]
            cells.append(chip(d, cell_state(raw, False), f"FT {pos} RFI @ {d}bb"))
        ft_rows.append(f"<tr><th>{pos} RFI</th>{''.join(f'<td>{c}</td>' for c in cells)}</tr>")
    ft_asym = sum(1 for (g, stacks, *_) in arch["rfi"]
                  if g == "mttgeneral-icm-8m-200-ptft" and "-" in stacks)
    return f"""
<h2 id="icm">ICM symmetric RFI <span class="pill raw">bubble {n_ok}/28 &middot; FT symmetric {ft_cells}</span></h2>
<p class="small">The bubble gametype is preflop-only &mdash; BM1&ndash;BM7 need no postflop.
Rows show symmetric RFI coverage at the depths the catalog sells; asymmetric
stack configs (ICM-covered/covering) are the 8-dash directories
({n_asym_scraped} bubble, {ft_asym} FT scraped of {n_bubble_asym}/{n_ft_asym} catalog configs).</p>
<h3>Bubble symmetric RFI <span class="pill miss">{covered}/{total} scraped</span></h3>
<table><tr><th>Line</th>{''.join(f'<th>{d}</th>' for d in BUBBLE_SYMMETRIC)}</tr>
{''.join(rows)}</table>
<h3>Final table symmetric RFI</h3>
<table><tr><th>Line</th>{''.join(f'<th>{d}</th>' for d in ft_depths)}</tr>
{''.join(ft_rows)}</table>"""


def main():
    arch = parse_archive()
    store = parse_store()
    cat, asym_catalog = parse_catalog()

    rfi_covered = sum(1 for p in OPENERS for d in RFI_DEPTHS
                      if ("cev", str(d), p) in arch["rfi"])
    rfi_total = len(OPENERS) * len(RFI_DEPTHS)
    vo_covered = sum(1 for (g, s, op, df) in arch["vsopen"] if g == "cev")
    t3_covered = sum(1 for (g, s, op, r) in arch["vs3bet"] if g == "cev")
    flop_nodes = sum(len(b) for b in arch["flops"].values())
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    doc = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Straddle &mdash; GTO Wizard coverage</title>
<style>{CSS}</style></head>
<body>
<header>
  <h1>GTO Wizard solution coverage</h1>
  <div class="sub">Generated {now} &middot; archive: <code>straddle-solutions/solutions/</code>
  ({arch['files']} captures) &middot; store: <code>packages/ranges/data/</code>
  ({store['files']} files) &middot; catalog: 3 gametypes tracked</div>
  <div class="cards">
    <div class="card"><div class="n">{arch['files']}</div><div class="l">raw captures</div></div>
    <div class="card"><div class="n">{rfi_covered}/{rfi_total}</div><div class="l">cEV RFI cells</div></div>
    <div class="card"><div class="n">{vo_covered}</div><div class="l">cEV vs-open cells</div></div>
    <div class="card"><div class="n">{t3_covered}</div><div class="l">cEV vs-3bet cells</div></div>
    <div class="card"><div class="n">{flop_nodes}</div><div class="l">postflop board-nodes</div></div>
  </div>
</header>
<nav>
  <span class="navgroup">Study universe</span>
  <a href="#gaps">Course gaps</a><a href="#deck">Study deck</a><a href="#deckmatrix">Deck &times; situations</a><a href="#flopplan">Flop plan</a>
  <span class="navgroup">ChipEV (MTT 8-max)</span>
  <a href="#rfi">RFI ladder</a><a href="#vsopen">vs-open</a><a href="#vs3bet">vs-3bet</a><a href="#limp">vs-limp</a><a href="#postflop">Postflop archive</a>
  <span class="navgroup">ICM (bubble &amp; final table)</span>
  <a href="#icmsym">Symmetric defends</a><a href="#icm">Symmetric RFI</a><a href="#asym">Asymmetric configs</a>
</nav>
<main>
{render_gaps(arch, store)}
{render_flopdeck(arch, store)}
{render_deckmatrix(arch, store)}
{render_flopplan(arch, store)}
{render_rfi(arch, store, cat)}
{render_vsopen(arch, store, cat)}
{render_vs3bet(arch, store, cat)}
{render_limp(arch, store)}
{render_postflop(arch, store)}
{render_icm_sym(arch, store)}
{render_icm(arch, store, cat, len(asym_catalog.get("MTTGeneral_ICM8m200PTBUBBLEMID", [])), len(asym_catalog.get("MTTGeneral_ICM8m200PTFT", [])))}
{render_asym(arch, store, cat, asym_catalog)}
</main>
</body></html>
"""
    OUT.write_text(doc)
    print(f"wrote {OUT} ({len(doc)//1024} KiB)")


if __name__ == "__main__":
    main()
