#!/usr/bin/env python3
"""Fetch GTO Wizard spot solutions by driving the logged-in app tab (CDP).

Requires the debug Chrome (logged-in profile at .scratch/gw-chrome-profile)
running with --remote-debugging-port=9222. The app itself makes every
authed/signed request — this script only navigates it and captures
responses off the wire. Nothing here ever calls api.gtowizard.com directly.

Awareness: every fetch is validated against the solutions library catalog
(the app's own /v4/game-modes/ response, captured on page load and cached at
catalog.json at the repo root) — gametype, depth and the exact stack config must
exist, because for nonexistent spots the app silently falls back to an
unrelated solution. Walk modes derive lines from real node responses, so
open sizes (R2 vs R2.1) are never guessed:

  --rfi BTN                       BTN's RFI node
  --bb-vs BTN                     BTN RFI node, then BB's defend node
  --rfi HJ --vs-3bet BB           HJ open, BB's defend node (real 3-bet size
                                  read from it), then HJ's vs-3bet node
  ... --board Kh8h3c --cbet       continue to the opener's c-bet node

Each capture prints the actions available at that node (exact bet sizes)
and is archived under solutions/<gametype>/<stacks>/<category>/:

  solutions/cev/40/rfi/btn.json                   position RFI
  solutions/cev/40/vs-open/btn-bb.json            BB defending vs an open
  solutions/cev/40/flops/r2-f-f-f-f-f-f-c/kh8h3c-x.json   c-bet node
  solutions/icm-8m-200ptbubblemid/40/rfi/btn.json  one dir per gametype

A node is fully determined by (gametype, stacks, preflop line, board,
flop history) — multiway lines and longer boards file naturally, and
unnamed node types die loudly instead of being misfiled.

Usage (repo root):
  python3 straddle-solutions/scripts/fetch_browser.py --catalog
  python3 straddle-solutions/scripts/fetch_browser.py --rfi BTN --depth 30
  python3 straddle-solutions/scripts/fetch_browser.py --bb-vs UTG --depth 40
  python3 straddle-solutions/scripts/fetch_browser.py --rfi UTG --board Kh8h3c --cbet
  python3 straddle-solutions/scripts/fetch_browser.py --stacks 40.125-35.125-... --rfi UTG
  python3 straddle-solutions/scripts/fetch_browser.py --history-spot 9 \
      --preflop-actions R2-F-F-F-F-F-F-C --board Kh8h3c      # manual mode
"""

import argparse
import datetime
import json
import pathlib
import random
import re
import sys
import time
import urllib.parse
import urllib.request

import websocket

CDP = "http://localhost:9222"
ROOT = pathlib.Path(__file__).resolve().parents[1]
SOLUTIONS = ROOT / "solutions"
CATALOG = ROOT / "catalog.json"
APP = "https://app.gtowizard.com/solutions"
# pacing: --pace P scales the in-app render pause to uniform(0.7P, 1.6P)
# seconds (default without the flag: 0.5-1.5s, a quick human click). Bulk
# sweeps must pass a larger --pace and add inter-request gaps in the driver
# — a uniform, rapid cadence is the fingerprint of a scraper.
PACE = None
WIZARD = (APP + "?solution_type=gwiz&soltab=range&gmfs_solution_tab=ai_sols"
          "&gametype={gametype}&depth={depth}&stacks={stacks}"
          "&gmfft_sort_key=0&gmfft_sort_order=desc&history_spot={spot}"
          "&preflop_actions={preflop}&gmff_stacks_type=SYMMETRIC&gmff_favorite=false")
# flop params (flop_actions, board) are appended ONLY when a board exists —
# X is a postflop-only code; sending flop_actions=X with an empty board
# makes the app resolve preflop nodes to wrong spots
POSITIONS = ["UTG", "UTG+1", "LJ", "HJ", "CO", "BTN", "SB", "BB"]
ORDINAL = {p: i + 1 for i, p in enumerate(POSITIONS)}


def die(msg):
    print(msg, file=sys.stderr)
    sys.exit(1)


def slug(position):
    return position.lower().replace("+", "")  # UTG+1 -> utg1


def targets():
    with urllib.request.urlopen(CDP + "/json", timeout=5) as r:
        return json.load(r)


def gtowizard_tab():
    for t in targets():
        if t["type"] == "page" and "app.gtowizard.com" in t["url"]:
            return t["webSocketDebuggerUrl"]
    req = urllib.request.Request(CDP + "/json/new?url=" + APP, method="PUT")
    with urllib.request.urlopen(req, timeout=10) as r:
        json.load(r)
    time.sleep(4)
    for t in targets():
        if t["type"] == "page" and "app.gtowizard.com" in t["url"]:
            return t["webSocketDebuggerUrl"]
    die("no app.gtowizard.com tab — start the debug Chrome (see add-range skill)")


class Cdp:
    def __init__(self, ws_url):
        self.ws = websocket.create_connection(ws_url, timeout=60, suppress_origin=True)
        self.id = 0

    def send(self, method, params=None):
        self.id += 1
        self.ws.send(json.dumps({"id": self.id, "method": method,
                                 "params": params or {}}))
        return self.id

    def wait_result(self, msg_id, timeout=60):
        deadline = time.time() + timeout
        while time.time() < deadline:
            msg = json.loads(self.ws.recv())
            if msg.get("id") == msg_id:
                return msg
        die("CDP result timeout")

    def events(self, handler, timeout):
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                self.ws.settimeout(max(0.5, deadline - time.time()))
                msg = json.loads(self.ws.recv())
            except websocket.WebSocketTimeoutException:
                continue
            result = handler(msg)
            if result is not None:
                return result
        return None


# ---------------------------------------------------------------- capture

def capture_response(cdp, matcher, timeout=60):
    """Wait for a 200 response whose URL matches matcher(url) -> truthy key;
    return (key, body). Bodies are read off the wire via CDP."""
    pending = {}

    def on_event(msg):
        m, params = msg.get("method"), msg.get("params", {})
        if m == "Network.responseReceived":
            url = params.get("response", {}).get("url", "")
            key = matcher(url)
            if key and params["response"].get("status") == 200:
                pending[params["requestId"]] = key
        elif m == "Network.loadingFinished":
            rid = params.get("requestId")
            if rid in pending:
                key = pending.pop(rid)
                result = cdp.wait_result(cdp.send(
                    "Network.getResponseBody", {"requestId": rid}), 30)
                body = result.get("result", {}).get("body")
                if body:
                    return key, body
        return None

    return cdp.events(on_event, timeout=timeout)


def navigate_in_app(cdp, url, pause=None):
    """Move the app to the spot like an in-app click: pushState + popstate
    (the router's own transition path — no page reload)."""
    expr = (f"history.pushState(null, '', {json.dumps(url)});"
            "window.dispatchEvent(new PopStateEvent('popstate'))")
    cdp.send("Runtime.evaluate", {"expression": expr})
    # human pause while the app "renders" — near-zero with --fast, scaled by
    # --pace for bulk sweeps; events that arrive during the pause queue in
    # the socket and are drained when capture_response starts listening
    if PACE is not None:
        time.sleep(random.uniform(PACE * 0.7, PACE * 1.6))
    else:
        time.sleep(pause if pause is not None else random.uniform(0.5, 1.5))


# ---------------------------------------------------------------- catalog

def capture_catalog(cdp):
    """Reload the app and capture its own game-modes (solutions library)
    request off the wire — the app fetches it on every page load. Keeps the
    largest response (the app requests several filtered variants)."""
    cdp.send("Network.enable")
    nav = cdp.send("Page.navigate", {"url": APP})
    cdp.wait_result(nav)
    best = None
    deadline = time.time() + 60
    while time.time() < deadline:
        got = capture_response(cdp, lambda u: "library" if "v4/game-modes" in u else None,
                               timeout=max(1.0, deadline - time.time()))
        if got is None:
            break
        if best is None or len(got[1]) > len(best):
            best = got[1]
    if best is None:
        die("no game-modes response captured during page load — is the tab logged in?")
    catalog = {"fetched_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
               "gametypes": json.loads(best)}
    CATALOG.parent.mkdir(parents=True, exist_ok=True)
    CATALOG.write_text(json.dumps(catalog) + "\n")
    print(f"catalog captured ({len(catalog['gametypes'])} gametypes, "
          f"{len(best)} bytes) -> {CATALOG}")
    return catalog


def load_catalog(cdp, refresh=False, max_age_days=14):
    if not refresh and CATALOG.exists():
        age = datetime.datetime.now(datetime.timezone.utc) - \
            datetime.datetime.fromisoformat(json.loads(CATALOG.read_text())["fetched_at"])
        if age.days < max_age_days:
            return json.loads(CATALOG.read_text())
    return capture_catalog(cdp)


def catalog_entry(catalog, gametype):
    for g in catalog["gametypes"]:
        if g["name"] == gametype:
            return g
    prefix = gametype.split("_")[0].lower()
    close = [g["name"] for g in catalog["gametypes"] if prefix in g["name"].lower()][:8]
    die(f"gametype {gametype} is not in the solutions library"
        + (f" (close: {', '.join(close)})" if close else ""))


def normalize_depth(entry, depth):
    """The app's depths are stack + 0.125 ante; accept a bare stack like 40."""
    depths = {gm["depth"] for gm in entry["game_modes"]}
    if depth in depths:
        return depth
    if f"{depth}.125" in depths:
        return f"{depth}.125"
    die(f"depth {depth} does not exist for {entry['name']}. "
        f"Available: {sorted(depths, key=float)}")


def validate_spot(catalog, gametype, stacks):
    """The app silently falls back to another solution when the exact stack
    config doesn't exist — refuse instead. Returns the catalog entry."""
    entry = catalog_entry(catalog, gametype)
    if len(stacks) != entry["players"]:
        die(f"{gametype} is {entry['players']}-max — pass "
            f"{entry['players']} stacks, got {len(stacks)}")
    for gm in entry["game_modes"]:
        if gm["stacks"] == stacks:
            return entry
    symmetric = sorted({gm["depth"] for gm in entry["game_modes"]
                        if len(set(gm["stacks"])) == 1}, key=float)
    msg = f"stack config {'-'.join(stacks)} does not exist for {gametype}."
    if symmetric:
        msg += f" Symmetric depths: {symmetric}."
    at_depth = [gm for gm in entry["game_modes"] if gm["depth"] == stacks[0]]
    if at_depth:
        msg += (" Configs at that depth: "
                + "; ".join("-".join(gm["stacks"]) for gm in at_depth[:3]))
    die(msg)


# ---------------------------------------------------------------- nodes

def node_url(gametype, stacks, spot, preflop="", flop="", board="",
             turn="", river=""):
    url = WIZARD.format(gametype=gametype, depth=stacks[0], stacks="-".join(stacks),
                        spot=spot, preflop=preflop)
    if board:
        url += f"&flop_actions={flop or 'X'}&board={board}"
        if turn:
            url += f"&turn_actions={turn}"
        if river:
            url += f"&river_actions={river}"
    return url


def flop_node_spot(preflop, flop):
    """Node ordinal for a postflop node, empirically pinned by the app's
    own click-built URLs: spot = 1 + preflop actions + max(0, flop
    actions - 1)  (X -> 9, X-R1.1 -> 10, X-R1.1-C -> 11 on the 8-action
    UTG-vs-BB line)."""
    n_preflop = len(preflop.split("-")) if preflop else 0
    n_flop = len(flop.split("-")) if flop else 0
    return 1 + n_preflop + max(0, n_flop - 1)


def spot_params(url):
    """The spot-identity params the app echoes into its spot-solution GET
    (empirically: gametype, depth, stacks, the street action histories and
    the board — no history_spot; the histories alone determine the node).
    Missing params and empty strings both normalize to '', so a preflop
    node URL (no flop params) matches the app's empty flop_actions= etc."""
    q = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)

    def one(k):
        return (q.get(k) or [""])[0]
    return {k: one(k) for k in ("gametype", "depth", "stacks",
                                "preflop_actions", "flop_actions",
                                "turn_actions", "river_actions", "board")}


def fmt_params(p):
    return ", ".join(f"{k}={v}" for k, v in p.items() if v)


def capture_spot(cdp, url, fast=False, reload_first=False):
    """Navigate to the spot in-app and capture the spot-solution response —
    matched EXACTLY against the request params the app sends. Returns
    (body, None) on capture; (None, mismatched_params) when the app asked
    for a different spot (the node URL doesn't resolve — fail fast, no
    amount of reloading fixes that); (None, None) when no request fired at
    all (stale in-memory state on the push path — a reload re-navigates).

    The OPTIONS preflights carry the same URL, so only GET requests are
    tracked. Waits are upper bounds — captures return when the response
    lands (typically 1-3s)."""
    want = spot_params(url)
    state = {"pending": {}, "mismatch": None}

    def on_event(msg):
        m, params = msg.get("method"), msg.get("params", {})
        rid = params.get("requestId")
        if m == "Network.requestWillBeSent":
            req = params.get("request", {})
            if req.get("method") == "GET" and "solutions/spot-solution" in req.get("url", ""):
                got = spot_params(req["url"])
                if got == want:
                    state["pending"][rid] = None
                elif state["mismatch"] is None:
                    state["mismatch"] = got
                    # the app re-parameterized: this navigation will never
                    # produce the requested spot — bail immediately
                    return (None, got)
        elif m == "Network.responseReceived":
            if rid in state["pending"] and params.get("response", {}).get("status") == 200:
                state["pending"][rid] = "ok"
        elif m == "Network.loadingFinished":
            if state["pending"].get(rid) == "ok":
                result = cdp.wait_result(cdp.send(
                    "Network.getResponseBody", {"requestId": rid}), 30)
                body = result.get("result", {}).get("body")
                if body:
                    return (body, state["mismatch"])
        return None

    push_wait, reload_wait = (3, 10) if fast else (6, 25)
    if not reload_first:
        navigate_in_app(cdp, url, pause=0.1 if fast else None)
        try:
            got = cdp.events(on_event, timeout=push_wait)
        except Exception as e:
            die(f"CDP connection error during capture ({e}) — is the debug "
                "Chrome still open?")
        return got if got is not None else (None, None)
    nav = cdp.send("Page.navigate", {"url": url})
    cdp.wait_result(nav)
    try:
        got = cdp.events(on_event, timeout=reload_wait)
    except Exception as e:
        die(f"CDP connection error during capture ({e}) — is the debug "
            "Chrome still open?")
    return got if got is not None else (None, None)


def app_location(cdp):
    r = cdp.wait_result(cdp.send("Runtime.evaluate",
                                 {"expression": "location.href"}), 10)
    return r.get("result", {}).get("value", "")


def check_capture(data, stacks, expected_position=None, expected_players=8,
                  board=""):
    """Return an error string if the capture isn't the spot we asked for
    (the app falls back to its default solution for nonexistent spots, and
    to unrelated nodes for stale in-session state or malformed params)."""
    g = data.get("game", {})
    players = g.get("players", [])
    if len(players) != expected_players:
        return (f"capture is a {len(players)}-player solution, expected "
                f"{expected_players} — the app fell back to another solution "
                "(bad gametype/depth?)")
    got = sorted(str(p.get("stack")) for p in players)
    if got != sorted(stacks):
        return (f"capture stacks {got} don't match requested {sorted(stacks)} — "
                "the app fell back to another solution (stack config may not exist)")
    if (g.get("board") or "").lower() != (board or "").lower():
        return (f"capture board is '{g.get('board') or 'empty'}', expected "
                f"'{board or 'empty'}' — the app fell back to another node "
                "(lowercase board in the URL? bad spot encoding?)")
    if expected_position and g.get("active_position") != expected_position:
        return (f"capture is {g.get('active_position')}'s decision, expected "
                f"{expected_position} — the app fell back to another solution")
    return None


def print_actions(data):
    parts = []
    for a in data["action_solutions"]:
        act = a["action"]
        label = act["code"]
        if act["type"] == "RAISE" and not act["allin"]:
            pct = act.get("betsize_by_pot")
            label += f" ({act['betsize']}bb" + (f", {float(pct):.0%} pot" if pct else "") + ")"
        parts.append(label)
    print(f"  {data['game']['active_position']} @ "
          f"{data['game']['board'] or 'preflop'}: " + " / ".join(parts))


def raise_code(data, what):
    """The node's raise code, read from a captured response (sizes are never
    guessed). Prefers the smallest non-all-in raise; falls back to the
    all-in code (short-stack 3-bets can be shove-only); dies when the node
    offers no raise at all."""
    acts = [a["action"] for a in data["action_solutions"]]
    raises = [a for a in acts if a["type"] == "RAISE" and not a["allin"]]
    if raises:
        raises.sort(key=lambda r: float(r["betsize"]))
        if len(raises) > 1:
            print(f"  {what} sizes available: "
                  + ", ".join(f"{r['code']} ({r['betsize']}bb)" for r in raises)
                  + f" — using {raises[0]['code']}", file=sys.stderr)
        return raises[0]["code"]
    allins = [a for a in acts if a["type"] == "RAISE" and a["allin"]]
    if allins:
        print(f"  {what} is all-in only at this node — using RAI", file=sys.stderr)
        return allins[0]["code"]
    die(f"no {what} at this node — cannot walk past it")


def fetch_node(cdp, url, out, stacks, expected_position=None, expected_players=8,
               board="", reuse=False, fast=False):
    """Capture a node and archive it. With reuse=True, serve an already-
    archived capture instead of re-fetching (solver spots are static).

    The capture is request-matched (capture_spot), so fallbacks and stale
    state are detected in-flight; check_capture validates the response
    itself as the last line of defense. Flow: router push (fast path),
    full reload (stale in-memory state), die — no third retry."""
    if reuse and out.exists():
        data = json.loads(out.read_text())
        print(f"cached   -> {out.relative_to(SOLUTIONS)}")
        print_actions(data)
        return data

    for reload_first in (False, True):
        body, mismatch = capture_spot(cdp, url, fast=fast, reload_first=reload_first)
        if body is not None:
            data = json.loads(body)
            error = check_capture(data, stacks, expected_position,
                                  expected_players, board)
            if error:
                die(error)  # the app asked for THIS spot — retrying won't change the answer
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(data, indent=2) + "\n")
            print(f"archived -> {out.relative_to(SOLUTIONS)}")
            print_actions(data)
            return data
        if mismatch is not None:
            if reload_first:
                die(f"the app re-parameterized the spot even after a full "
                    f"reload — it requested [{fmt_params(mismatch)}] instead "
                    f"of [{fmt_params(spot_params(url))}]; the node doesn't "
                    "resolve (bad line/spot encoding or unsupported spot)")
            # a stale in-app state re-serves its own spot on the push —
            # a fresh reload resolves it
            print(f"  push requested a different spot "
                  f"[{fmt_params(mismatch)}] — stale state, reloading",
                  file=sys.stderr)
        if not reload_first:
            print("  no spot-solution request on the router push — reloading",
                  file=sys.stderr)

    loc = app_location(cdp)
    where = f" (app is at {loc})" if loc else ""
    die(f"no spot-solution response captured for {url}{where} — "
        "if the app left the solutions page the session may have expired; "
        "log in again in the debug Chrome window")


# ---------------------------------------------------------------- archive
#
# solutions/<gametype>/<stacks>/<category>/<name>.json
#   rfi/       <position>.json                     first-to-act open decision
#   vs-open/   <opener>-<defender>.json            defense vs a single open
#   flops/     <preflop-line>/<board>-<flop-actions>.json
# Any node that doesn't fit a category dies loudly — never misfile.
# A node is fully determined by (gametype, stacks, preflop line, board,
# flop history), so this scheme covers multiway (longer line dirs),
# turn/river (longer boards) and facing-bet nodes (flop history in the name).

GAMETYPE_DIRS = {
    "MTTGeneral_8m": "cev",
    "MTTGeneral_ICM8m200PTBUBBLEMID": "icm-8m-200ptbubblemid",
}


def gametype_dir(gametype):
    """Unique directory per gametype — ICM variants must never collide
    (several bubble structures exist; one 'icm/' dir would overwrite
    data). Aliases for the gametypes we scrape; deterministic slug
    otherwise, verified unique against the catalog at fetch time."""
    if gametype in GAMETYPE_DIRS:
        return GAMETYPE_DIRS[gametype]
    return re.sub(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Za-z])(?=\d)|_+",
                  "-", gametype).lower().strip("-")


def check_dir_unique(catalog, gametype):
    mine = gametype_dir(gametype)
    for g in catalog["gametypes"]:
        if g["name"] != gametype and gametype_dir(g["name"]) == mine:
            die(f"archive dir '{mine}' collides with gametype {g['name']} "
                "— add an alias to GAMETYPE_DIRS")


def spot_token(stacks):
    """Stack-config token: bare depth when symmetric (40.125 -> 40), all
    stacks when asymmetric (no collisions between configs)."""
    if len(set(stacks)) == 1:
        return stacks[0].removesuffix(".125")
    return "-".join(s.removesuffix(".125") for s in stacks)


def archive_path(gametype, token, category, name):
    return SOLUTIONS / gametype_dir(gametype) / token / category / f"{name}.json"


def manual_category(preflop, spot, board, flop_actions, players=8):
    """Classify a manual-mode node into (category, archive name, expected
    decider). The acting position is POSITIONS[spot-1] (None for the
    vs-3bet lines, where the OPENER acts again); the line's leading folds
    give the opener. Anything else is a node type we haven't named yet —
    die rather than guess."""
    tokens = preflop.split("-") if preflop else []
    k = 0
    while k < len(tokens) and tokens[k] == "F":
        k += 1
    if not board and k < len(tokens) and tokens[k].startswith("R"):
        # opener facing a 3-bet: open, folds, one raise, folds folding back
        # around to the opener (after a 3-bet the seats in between act
        # first — UTG only decides once it folds back to them)
        rest = tokens[k + 1:]
        raises = [i for i, t in enumerate(rest) if t.startswith("R")]
        if (len(raises) == 1
                and all(t == "F" for i, t in enumerate(rest) if i != raises[0])):
            opener = POSITIONS[k]
            threebettor = POSITIONS[k + 1 + raises[0]]
            return "vs-3bet", f"{slug(opener)}-{slug(threebettor)}", opener
    if board:
        # limped lines end in BB's preflop check-vs-limp (the one preflop X
        # the app codes): F-F-F-F-F-F-C-X — the SB limps (C), BB checks (X)
        limped = (len(tokens) >= 2 and tokens[-1] == "X" and tokens[-2] == "C"
                  and all(t == "F" for t in tokens[:-2]))
        # caller-IP lines: opener raises, one seat calls, everyone else
        # folds AFTER the call (blinds/BTN fold) — a 2-way pot where the
        # caller has position: R2.1-F-F-F-C-F-F. The flop decider is the
        # opener (OOP aggressor).
        caller_ip = (k < len(tokens) and tokens[k].startswith("R")
                     and tokens.count("C") == 1
                     and all(t == "F" for t in tokens[k + 1:]
                            if t != "C") and tokens[-1] == "F")
        if not tokens or (tokens[-1] != "C" and not limped and not caller_ip):
            die("flop captures expect a preflop line ending in -C; a call "
                "mid-line without one is a preflop overcall decision — needs "
                "its own naming before scraping")
        flop = (flop_actions or "X").lower()
        # caller-IP flops: validate the decider is the opener (OOP aggressor)
        expected = POSITIONS[k] if caller_ip else None
        return "flops", f"{preflop.lower()}/{board.lower()}-{flop}", expected
    if players != 8:
        die(f"preflop-node naming is 8-max only; {players}-max needs its own "
            "position names — add them before scraping")
    if k >= len(POSITIONS):
        die(f"cannot classify preflop line '{preflop}'")
    if k == len(tokens):            # only folds: an RFI decision node
        if spot != k + 1:
            die(f"history-spot {spot} doesn't match preflop line '{preflop}'")
        return "rfi", slug(POSITIONS[spot - 1]), POSITIONS[spot - 1]
    if tokens[k].startswith("R") and all(t == "F" for t in tokens[k + 1:]):
        if spot > len(POSITIONS):
            die(f"history-spot {spot} out of range")
        opener, defender = POSITIONS[k], POSITIONS[spot - 1]
        return "vs-open", f"{slug(opener)}-{slug(defender)}", POSITIONS[spot - 1]
    if tokens[k] == "C" and k == len(tokens) - 1:
        # a blind completing/limping: the last token is a preflop CALL
        # (e.g. SB limp F-F-F-F-F-F-C -> BB's iso-or-check decision)
        if spot > len(POSITIONS):
            die(f"history-spot {spot} out of range")
        opener, defender = POSITIONS[k], POSITIONS[spot - 1]
        return "vs-limp", f"{slug(opener)}-{slug(defender)}", POSITIONS[spot - 1]
    die(f"no archive naming for line '{preflop}' at spot {spot} — preflop "
        "calls/3-bets need their own category before scraping")


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(prog="fetch_browser")
    ap.add_argument("--catalog", action="store_true",
                    help="capture the solutions library catalog (game-modes) and exit")
    ap.add_argument("--refresh-catalog", action="store_true")
    ap.add_argument("--gametype", default="MTTGeneral_8m")
    ap.add_argument("--depth", default="40.125",
                    help="stack depth (bare stack like 40 is normalized to 40.125)")
    ap.add_argument("--stacks", default="",
                    help="explicit 8-stack config, dash-joined; overrides --depth")
    ap.add_argument("--rfi", choices=POSITIONS[:7], metavar="POSITION",
                    help="walk: fetch this position's RFI node")
    ap.add_argument("--bb-vs", choices=POSITIONS[:6], metavar="OPENER",
                    help="walk: fetch OPENER's RFI node, then BB's defend node "
                         "(open size is read from the RFI response)")
    ap.add_argument("--defender", choices=POSITIONS, metavar="SEAT",
                    help="with --rfi: fetch SEAT's defend node against the "
                         "open (generalizes --bb-vs to any seat after the "
                         "opener; the open code is read from the RFI response)")
    ap.add_argument("--vs-3bet", choices=POSITIONS, metavar="VILLAIN",
                    help="with --rfi: fetch VILLAIN's defend node (reading the "
                         "real 3-bet size from it), then the opener's "
                         "vs-3bet decision node")
    ap.add_argument("--board", default="", help="flop board, e.g. Kh8h3c")
    ap.add_argument("--cbet", action="store_true",
                    help="with --rfi/--bb-vs: continue to the flop c-bet node "
                         "(needs --board)")
    ap.add_argument("--flop-actions", default="X",
                    help="flop history code (X = node before any flop action)")
    ap.add_argument("--turn-actions", default="",
                    help="turn history code, street-split (e.g. X-R8.7-C)")
    ap.add_argument("--river-actions", default="",
                    help="river history code, street-split (e.g. X)")
    ap.add_argument("--history-spot", default="",
                    help="manual mode: node ordinal (1 = UTG first to act)")
    ap.add_argument("--preflop-actions", default="",
                    help="manual mode: preflop history, e.g. R2-F-F-F-F-F-F-C")
    ap.add_argument("--refetch", action="store_true",
                    help="ignore already-archived captures and fetch live")
    ap.add_argument("--fast", action="store_true",
                    help="short waits and no human pauses (debugging)")
    ap.add_argument("--pace", type=float, default=None,
                    help="in-app pause scale in seconds for bulk sweeps "
                         "(human-paced cadence; e.g. --pace 2.5)")
    ap.add_argument("--out", type=pathlib.Path,
                    help="write JSON here instead of the imports/solutions/ archive")
    args = ap.parse_args()
    global PACE
    PACE = args.pace

    cdp = Cdp(gtowizard_tab())
    cdp.send("Network.enable")

    if args.catalog:
        capture_catalog(cdp)
        return
    catalog = load_catalog(cdp, refresh=args.refresh_catalog)

    # resolve the exact stack config and validate it against the library
    entry = catalog_entry(catalog, args.gametype)
    check_dir_unique(catalog, args.gametype)
    if args.stacks:
        stacks = args.stacks.split("-")
    else:
        stacks = [normalize_depth(entry, args.depth)] * entry["players"]
    entry = validate_spot(catalog, args.gametype, stacks)
    players = entry["players"]
    token = spot_token(stacks)

    # ---- walk modes (8-max: node ordinals and fold lines are 8-max) ---
    if args.rfi or args.bb_vs:
        if players != 8:
            die(f"walk modes are 8-max only; {args.gametype} is {players}-max "
                "— use manual mode")
        opener = args.rfi or args.bb_vs
        n = ORDINAL[opener]
        folds = "F-" * (n - 1)
        url = node_url(args.gametype, stacks, n, folds.rstrip("-"))
        rfi = fetch_node(cdp, url,
                         args.out or archive_path(args.gametype, token, "rfi",
                                                  slug(opener)),
                         stacks, expected_position=opener,
                         expected_players=players, reuse=not args.refetch)

        code = raise_code(rfi, "open")
        # defender walk: any seat after the opener (--bb-vs is BB for
        # back-compat). The defend line is open + folds up to the seat's
        # decision; the fetched node feeds --vs-3bet when it's the villain
        defender = args.defender
        if args.bb_vs:
            if defender:
                die("--bb-vs and --defender are mutually exclusive")
            defender = "BB"
        defend_data = None
        if defender:
            d = ORDINAL[defender]
            if d <= n:
                die(f"defender {defender} must act after the opener {opener}")
            defend_data = fetch_node(
                cdp,
                node_url(args.gametype, stacks, d,
                         (folds + code + "-F" * (d - n - 1)).strip("-")),
                archive_path(args.gametype, token, "vs-open",
                             f"{slug(opener)}-{slug(defender)}"),
                stacks, expected_position=defender,
                expected_players=players, reuse=not args.refetch)

        if args.vs_3bet:
            # the 3-bet size is derived, never guessed: read the villain's
            # raise code from their defend node, then fold back around to
            # the opener's decision
            v = ORDINAL[args.vs_3bet]
            if v <= n:
                die(f"--vs-3bet {args.vs_3bet} must act after the opener {opener}")
            if defend_data is None:
                defend_data = fetch_node(
                    cdp,
                    node_url(args.gametype, stacks, v,
                             (folds + code + "-F" * (v - n - 1)).strip("-")),
                    archive_path(args.gametype, token, "vs-open",
                                 f"{slug(opener)}-{slug(args.vs_3bet)}"),
                    stacks, expected_position=args.vs_3bet,
                    expected_players=players, reuse=not args.refetch)
            three = raise_code(defend_data, "3-bet")
            line = (folds + code + "-F" * (v - n - 1) + "-" + three
                    + "-F" * (8 - v)).strip("-")
            fetch_node(
                cdp,
                node_url(args.gametype, stacks, 1 + len(line.split("-")), line),
                archive_path(args.gametype, token, "vs-3bet",
                             f"{slug(opener)}-{slug(args.vs_3bet)}"),
                stacks, expected_position=opener,
                expected_players=players, reuse=not args.refetch)

        if args.cbet:
            if not args.board:
                die("--cbet needs --board")
            line = (folds + code + "-F" * (7 - n) + "-C").strip("-")
            url = node_url(args.gametype, stacks, flop_node_spot(line, args.flop_actions),
                           line, flop=args.flop_actions, board=args.board)
            fetch_node(cdp, url,
                       archive_path(args.gametype, token, "flops",
                                    f"{line.lower()}/{args.board.lower()}-"
                                    f"{(args.flop_actions or 'X').lower()}"),
                       stacks, expected_position=opener,
                       expected_players=players, board=args.board,
                       reuse=not args.refetch)
        return

    # ---- manual mode (params exactly as in the app's share URL) ------
    if args.history_spot:
        url = node_url(args.gametype, stacks, args.history_spot,
                       args.preflop_actions, args.flop_actions, args.board,
                       args.turn_actions, args.river_actions)
        category, name, expected = manual_category(args.preflop_actions,
                                                   int(args.history_spot),
                                                   args.board, args.flop_actions,
                                                   players=players)
        if expected is None and category != "flops" and players == 8:
            expected = POSITIONS[int(args.history_spot) - 1]
        # turn/river histories extend the archive name (street-split in the
        # URL, dash-joined in the name)
        suffix = "".join(f"-{t.lower()}" for t in (args.turn_actions, args.river_actions) if t)
        fetch_node(cdp, url,
                   args.out or archive_path(args.gametype, token, category, name + suffix),
                   stacks, expected_position=expected, expected_players=players,
                   board=args.board, reuse=not args.refetch, fast=args.fast)
        return

    ap.print_help()


if __name__ == "__main__":
    main()
