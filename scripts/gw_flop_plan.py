"""The flop universe — boards that cover every strategy the course teaches.

Derived from the transcript extracts (S1-S4, S6, S7, S9, S12 + BM8-BM11):
every texture bucket / risk factor / quiz spot in each system maps to one
representative board on the line the system is played on. If every entry
below is scraped and stored, no future system page needs an ad-hoc solve.

Each entry:
  id      short name
  sys     system(s) the board serves
  cls     texture class (the strategy distinction the board exists for)
  why     what the transcript uses it for
  gt      archive gametype (cev | icm-8m-200ptbubblemid)
  depth   symmetric depth in bb (cev); None for asymmetric ICM configs
  stacks  exact 8-seat stack config (ICM); None for cev
  line    expected preflop line token (None = derived by the walk)
  board   canonical board with suits (turn/river cards appended per node)
  walk    fetch_browser.py args
  prio    1 = transcript-cited, closes a system gap
          2 = texture completion / depth adaptation
          3 = ICM bubble postflop (verify gametype flop support first)

Status vs the archive/store is computed by gw_coverage.py.
"""

PLAN = [
    # ---- System 1: UTG RFI c-bet line @40 (r2-f-f-f-f-f-f-c) ----
    dict(id="s1-k83", sys="S1", cls="K-high disconnected, two-tone", why="clean T-high+ -> 100% c-bet (flagship)",
         gt="cev", depth=40, line="r2-f-f-f-f-f-f-c", board="Kh8h3c",
         walk="--rfi UTG --depth 40 --board Kh8h3c --cbet", prio=1),
    dict(id="s1-kk3", sys="S1", cls="high-high-low paired", why="KK3 is NOT a risk factor -> 100%",
         gt="cev", depth=40, line="r2-f-f-f-f-f-f-c", board="KhKd3c",
         walk="--rfi UTG --depth 40 --board KhKd3c --cbet", prio=1),
    dict(id="s1-aj5", sys="S1", cls="A-high monotone", why="ace-monotone risk factor: bet strong+weak, check medium",
         gt="cev", depth=40, line="r2-f-f-f-f-f-f-c", board="AhJh5h",
         walk="--rfi UTG --depth 40 --board AhJh5h --cbet", prio=1),
    dict(id="s1-j66", sys="S1", cls="high-low-low paired", why="risk factor: bet trips+trash, check underpairs",
         gt="cev", depth=40, line="r2-f-f-f-f-f-f-c", board="Jh6s6d",
         walk="--rfi UTG --depth 40 --board Jh6s6d --cbet", prio=1),
    dict(id="s1-ak2", sys="S1", cls="AKx Broadway", why="AKx family risk factor -> not 100%",
         gt="cev", depth=40, line="r2-f-f-f-f-f-f-c", board="AsKh2c",
         walk="--rfi UTG --depth 40 --board AsKh2c --cbet", prio=1),
    dict(id="s1-t55", sys="S1", cls="high-low-low, T-high", why="quiz: T55 rainbow mix (trips + trash vs underpairs)",
         gt="cev", depth=40, line="r2-f-f-f-f-f-f-c", board="Ts5c5d",
         walk="--rfi UTG --depth 40 --board Ts5c5d --cbet", prio=1),
    dict(id="s1-963", sys="S1", cls="9-high connected", why="9-high & below bucket on the UTG line (mix ~70/30)",
         gt="cev", depth=40, line="r2-f-f-f-f-f-f-c", board="9c6h3d",
         walk="--rfi UTG --depth 40 --board 9c6h3d --cbet", prio=1),
    dict(id="s1-k83-20", sys="S1", cls="depth contrast: shallow", why="bet MORE when shallow (leak correction)",
         gt="cev", depth=20, line=None, board="Kh8h3c",
         walk="--rfi UTG --depth 20 --board Kh8h3c --cbet", prio=2),
    dict(id="s1-k83-100", sys="S1", cls="depth contrast: deep", why="deeper -> more checking (100bb adaptation)",
         gt="cev", depth=100, line=None, board="Kh8h3c",
         walk="--rfi UTG --depth 100 --board Kh8h3c --cbet", prio=2),

    # ---- System 2: BTN RFI c-bet line @50 (f-f-f-f-f-r2.1-f-c) ----
    dict(id="s2-a95", sys="S2", cls="A-high clean", why="ace-high clean -> 100%",
         gt="cev", depth=50, line="f-f-f-f-f-r2.1-f-c", board="Ac9h5d",
         walk="--rfi BTN --depth 50 --board Ac9h5d --cbet", prio=1),
    dict(id="s2-k93", sys="S2", cls="K-high, two low cards", why="second-low-card risk family",
         gt="cev", depth=50, line="f-f-f-f-f-r2.1-f-c", board="Kh9d3c",
         walk="--rfi BTN --depth 50 --board Kh9d3c --cbet", prio=1),
    dict(id="s2-a72m", sys="S2", cls="A-high monotone, low", why="monotone risk on ace-high",
         gt="cev", depth=50, line="f-f-f-f-f-r2.1-f-c", board="Ah7h2h",
         walk="--rfi BTN --depth 50 --board Ah7h2h --cbet", prio=1),
    dict(id="s2-k84m", sys="S2", cls="K-high monotone", why="monotone substantially more checking",
         gt="cev", depth=50, line="f-f-f-f-f-r2.1-f-c", board="Kc8c4c",
         walk="--rfi BTN --depth 50 --board Kc8c4c --cbet", prio=1),
    dict(id="s2-963", sys="S2", cls="9-high connected", why="9-high & below mix on the BTN line",
         gt="cev", depth=50, line="f-f-f-f-f-r2.1-f-c", board="9h6d3c",
         walk="--rfi BTN --depth 50 --board 9h6d3c --cbet", prio=1),
    dict(id="s2-ajj", sys="S2", cls="A-high paired", why="AJJ: paired = risk factor, solver checks ~50%",
         gt="cev", depth=50, line="f-f-f-f-f-r2.1-f-c", board="AhJdJc",
         walk="--rfi BTN --depth 50 --board AhJdJc --cbet", prio=1),
    dict(id="s2-kj2", sys="S2", cls="K-high with deuce", why="T-K high with deuce/three -> 100% (14% check = ~0 EV)",
         gt="cev", depth=50, line="f-f-f-f-f-r2.1-f-c", board="KdJh2c",
         walk="--rfi BTN --depth 50 --board KdJh2c --cbet", prio=1),
    dict(id="s2-k63", sys="S2", cls="K-high, two low cards", why="K63: two low cards interact -> mix",
         gt="cev", depth=50, line="f-f-f-f-f-r2.1-f-c", board="Kh6h3c",
         walk="--rfi BTN --depth 50 --board Kh6h3c --cbet", prio=1),
    dict(id="s2-543", sys="S2", cls="no 8+, two-tone", why="BTN misses -> check range (bet top, some bottom)",
         gt="cev", depth=50, line="f-f-f-f-f-r2.1-f-c", board="5h4h3c",
         walk="--rfi BTN --depth 50 --board 5h4s3c --cbet", prio=1),
    dict(id="s2-742", sys="S2", cls="no 8+, rainbow", why="BTN misses, rainbow contrast",
         gt="cev", depth=50, line="f-f-f-f-f-r2.1-f-c", board="7c4h2d",
         walk="--rfi BTN --depth 50 --board 7c4h2d --cbet", prio=1),
    dict(id="s2-t53", sys="S2", cls="T-high, two low cards", why="quiz: T53 two-tone mix (~24% check)",
         gt="cev", depth=50, line="f-f-f-f-f-r2.1-f-c", board="Th5c3d",
         walk="--rfi BTN --depth 50 --board Th5c3d --cbet", prio=2),

    # ---- System 3: SB limp -> BB check, stab line (f-f-f-f-f-f-c-x) ----
    dict(id="s3-k72", sys="S3", cls="K-high paired 7", why="key card K; high-card defending",
         gt="cev", depth=70, line="f-f-f-f-f-f-c-x", board="Kh7c2s",
         walk="--history-spot 8 --preflop-actions F-F-F-F-F-F-C --board Kh7c2s --flop-actions X", prio=1),
    dict(id="s3-a42", sys="S3", cls="A-high, key 4", why="key card 4: gut shots play, 7x worst",
         gt="cev", depth=70, line="f-f-f-f-f-f-c-x", board="Ah4d2s",
         walk="--history-spot 8 --preflop-actions F-F-F-F-F-F-C --board Ah4d2s --flop-actions X", prio=1),
    dict(id="s3-kq8", sys="S3", cls="Broadway + 8", why="key card 8, rainbow BDFD premium",
         gt="cev", depth=70, line="f-f-f-f-f-f-c-x", board="KsQd8h",
         walk="--history-spot 8 --preflop-actions F-F-F-F-F-F-C --board KsQd8h --flop-actions X", prio=1),
    dict(id="s3-jj3", sys="S3", cls="mid pair under", why="key card 3: deuce = death, T9 plays",
         gt="cev", depth=70, line="f-f-f-f-f-f-c-x", board="JsJh3d",
         walk="--history-spot 8 --preflop-actions F-F-F-F-F-F-C --board JsJh3d --flop-actions X", prio=1),
    dict(id="s3-k62", sys="S3", cls="K-high, key 6", why="double-unders = gut shots -> play; 20bb example",
         gt="cev", depth=20, line="f-f-f-f-f-f-c-x", board="Kh6s2h",
         walk="--history-spot 8 --preflop-actions F-F-F-F-F-F-C --board Kh6s2h --flop-actions X", prio=1),
    dict(id="s3-a72", sys="S3", cls="A-high, key 7", why="63 worst hand even with BDFD; 35bb example",
         gt="cev", depth=35, line="f-f-f-f-f-f-c-x", board="As7c2h",
         walk="--history-spot 8 --preflop-actions F-F-F-F-F-F-C --board As7c2h --flop-actions X", prio=1),

    # ---- System 4: river bluffing chains ----
    dict(id="s4-q106", sys="S4", cls="Q-T-6 two-tone -> 3-flush river", why="one-club bias: 75c bluffs, 75o without club checks",
         gt="cev", depth=40, line="f-f-f-f-f-f-r3-c", board="QcTd6c",
         walk="line f-f-f-f-f-f-r3-c (BB stab chain: X / X-R4.4 / +turn 2d X / +X / river Tc X = bluff node)", prio=1),
    dict(id="s4-ak4", sys="S4", cls="AK4 two-tone", why="System 1 bottom-up bluff (86o); avoid clubs/hearts",
         gt="cev", depth=40, line=None, board="AhKd4c",
         walk="--rfi SB --defender BB --depth 40 --board AhKd4c --cbet (then river chain)", prio=1),
    dict(id="s4-a23", sys="S4", cls="A-2-3 rainbow -> 4c river", why="2x unblocks folds; QJ too high up to bluff",
         gt="cev", depth=50, line="f-f-f-f-f-r2.1-f-c", board="Ah2d3c",
         walk="--rfi BTN --depth 50 --board Ah2d3c --cbet (then turn, river 4c)", prio=1),
    dict(id="s4-akq", sys="S4", cls="3+ Broadway -> J, T", why="three Broadway: no offsuit air, scarce bluffs (J9s)",
         gt="cev", depth=100, line="r2.1-f-f-f-f-f-c-f", board="AsKdQc",
         walk="caller-IP line r2.1-f-f-f-f-f-c-f (app sells EP-vs-BTN, not EP-vs-CO): flop X-R2, turn Jh X-R2.6-C, river Tc = pot-size bluff node", prio=1),

    # ---- System 6: BB check-raises top pair (multiple opener lines) ----
    dict(id="s6-k84", sys="S6", cls="K-high, EP line @13", why="pure CR all Kx incl. K2 (13bb)",
         gt="cev", depth=13, line="r2-f-f-f-f-f-f-c", board="Kc8h4d",
         walk="--rfi UTG --depth 13 --board Kc8h4d --cbet", prio=1),
    dict(id="s6-q75", sys="S6", cls="Q-high, HJ line @25", why="hierarchical kicker taper KQ -> Q2",
         gt="cev", depth=25, line="f-f-f-r2-f-f-f-c", board="Qh7c5d",
         walk="--rfi HJ --depth 25 --board Qh7c5d --cbet", prio=1),
    dict(id="s6-864", sys="S6", cls="8-high connected, CO line @25", why="low flop: kicker irrelevant, CR all top pair",
         gt="cev", depth=25, line="f-f-f-f-r2-f-f-c", board="8c6h4d",
         walk="--rfi CO --depth 25 --board 8c6h4d --cbet", prio=1),
    dict(id="s6-k94", sys="S6", cls="K-high two-tone, HJ @15", why="flush-draw top pair traps (check-call)",
         gt="cev", depth=15, line="f-f-f-r2-f-f-f-c", board="Kc9c4h",
         walk="--rfi HJ --depth 15 --board Kc9c4h --cbet", prio=1),
    dict(id="s6-j96", sys="S6", cls="J-high, BTN line @25", why="QJ pure CR; J2 two pair traps",
         gt="cev", depth=25, line="f-f-f-f-f-r2-f-c", board="Jd9h6c",
         walk="--rfi BTN --depth 25 --board Jd9h6c --cbet", prio=1),

    # ---- System 7: hero c-bets, faces check-raise (BTN line) ----
    dict(id="s7-jj3", sys="S7", cls="mid pair under", why="A5 too strong to fold; trash folds (~18% vs 38% MDF)",
         gt="cev", depth=50, line="f-f-f-f-f-r2.1-f-c", board="JsJh3c",
         walk="--rfi BTN --depth 50 --board JsJh3c --cbet", prio=1),
    dict(id="s7-t33", sys="S7", cls="T-high paired 3", why="paired board: key card T, overcards call",
         gt="cev", depth=35, line="f-f-f-f-f-r2.1-f-c", board="Tc5s3d",
         walk="--rfi BTN --depth 35 --board Tc5s3d --cbet", prio=1),
    dict(id="s7-533", sys="S7", cls="low pair under", why="AJ snap call: villain bluffs have tons of equity",
         gt="cev", depth=35, line="f-f-f-f-f-r2.1-f-c", board="5c3h3d",
         walk="--rfi BTN --depth 35 --board 5c3h3d --cbet", prio=1),
    dict(id="s7-662", sys="S7", cls="low pair + deuce", why="tiny CR: fold ~2%, K2s pure call",
         gt="cev", depth=25, line="f-f-f-f-f-r2-f-c", board="6s6h2c",
         walk="--rfi BTN --depth 25 --board 6s6h2c --cbet", prio=1),
    dict(id="s7-k55", sys="S7", cls="K-high paired 5", why="paired K: T9o pure fold (disconnected)",
         gt="cev", depth=25, line="f-f-f-f-f-r2-f-c", board="Kh5c5d",
         walk="--rfi BTN --depth 25 --board Kh5c5d --cbet", prio=1),

    # ---- System 9: BB defends vs c-bet (opener lines 60-80bb) ----
    dict(id="s9-j105", sys="S9", cls="J-T-5 connected", why="super gut shot (97d) vs naked (97o) contrast",
         gt="cev", depth=60, line="f-f-f-r2.1-f-f-f-c", board="JdTc5h",
         walk="--rfi HJ --depth 60 --board JdTc5h --cbet", prio=1),
    dict(id="s9-t52", sys="S9", cls="T-high, CO line", why="J6s pure CR: overcard + BD straight + BDFD",
         gt="cev", depth=60, line="f-f-f-f-r2.1-f-f-c", board="Tc5s2d",
         walk="--rfi CO --depth 60 --board Tc5s2d --cbet", prio=1),
    dict(id="s9-t72", sys="S9", cls="T-high, BTN line @80", why="Qd overcard + BDFD pure play",
         gt="cev", depth=80, line="f-f-f-f-f-r2.3-f-c", board="Td7c2s",
         walk="--rfi BTN --depth 80 --board Td7c2s --cbet", prio=1),
    dict(id="s9-q62", sys="S9", cls="Q-high, BTN line @80", why="JTo: 3-straight + double overs; sizing-sensitive",
         gt="cev", depth=80, line="f-f-f-f-f-r2.3-f-c", board="Qc6h2d",
         walk="--rfi BTN --depth 80 --board Qc6h2d --cbet", prio=1),
    dict(id="s9-k53", sys="S9", cls="K-high, HJ line", why="K8s mix: large bet -> fold more pairs",
         gt="cev", depth=60, line="f-f-f-r2.1-f-f-f-c", board="Kc5h3d",
         walk="--rfi HJ --depth 60 --board Kc5h3d --cbet", prio=1),

    # ---- System 12: defending 3-bets OOP (3-bet call lines) ----
    dict(id="s12-842", sys="S12", cls="low disconnected, vs HJ 3-bet", why="AJs worth zero -> fold",
         gt="cev", depth=40, line="r2-f-f-r5.5-f-f-f-f-c", board="8c4h2d",
         walk="--rfi UTG --vs-3bet HJ --depth 40 --board 8c4h2d --cbet", prio=1),
    dict(id="s12-k84", sys="S12", cls="K-high danger, vs BTN 3-bet", why="77/66/55 heavy folds on K-high",
         gt="cev", depth=40, line="r2-f-f-f-f-r6.5-f-f-c", board="Kc8h4d",
         walk="--rfi UTG --vs-3bet BTN --depth 40 --board Kc8h4d --cbet", prio=1),
    dict(id="s12-984", sys="S12", cls="9-high connected, vs BTN 3-bet", why="55 worth 100+ bb/100: low board defend",
         gt="cev", depth=40, line="r2-f-f-f-f-r6.5-f-f-c", board="9h8d4c",
         walk="--rfi UTG --vs-3bet BTN --depth 40 --board 9h8d4c --cbet", prio=1),
    dict(id="s12-a85", sys="S12", cls="A-high danger, vs HJ 3-bet", why="QTs fold; A-high = maximum danger",
         gt="cev", depth=40, line="r2-f-f-r5.5-f-f-f-f-c", board="Ah8d5c",
         walk="--rfi UTG --vs-3bet HJ --depth 40 --board Ah8d5c --cbet", prio=1),
    dict(id="s12-963", sys="S12", cls="9-high, vs BTN 3-bet jam", why="44 pure call: neither player hits",
         gt="cev", depth=40, line="r2-f-f-f-f-r6.5-f-f-c", board="9h6c3d",
         walk="--rfi UTG --vs-3bet BTN --depth 40 --board 9h6c3d --cbet", prio=1),
    dict(id="s12-752", sys="S12", cls="low disconnected @25, vs BTN 3-bet", why="AQo worth 186 bb/100: call/shove",
         gt="cev", depth=25, line=None, board="7h5c2d",
         walk="--rfi UTG --vs-3bet BTN --depth 25 --board 7h5c2d --cbet", prio=1),

    # ---- BM8-BM11: ICM bubble postflop (asymmetric configs) ----
    # stacks TBD: pick the closest catalog config (BTN~50/BB~20 etc.);
    # verify the bubble gametype serves flop nodes before the sweep.
    dict(id="bm8-akq", sys="BM8", cls="A-high Broadway", why="range bet 100% (BTN covers BB)",
         gt="icm-8m-200ptbubblemid", depth=None, stacks="BTN~50 / BB~20", line=None, board="AhKhQd",
         walk="BLOCKED: bubble gametype is preflop-only (verified, 2 configs) — re-scope to MTTGeneral_ICM8m200PTFT flops", prio=3),
    dict(id="bm8-aj8", sys="BM8", cls="A-high middling draws", why="check range develops (covered stack)",
         gt="icm-8m-200ptbubblemid", depth=None, stacks="BTN~50 / BB~20", line=None, board="AhJh8c",
         walk="BLOCKED: bubble gametype is preflop-only — re-scope to PTFT flops", prio=3),
    dict(id="bm8-j74", sys="BM8", cls="multiple gut shots", why="overbet ~105% pot (protection) — not on OESD/two-tone",
         gt="icm-8m-200ptbubblemid", depth=None, stacks="BTN~50 / BB~20", line=None, board="Jh7c4d",
         walk="BLOCKED: bubble gametype is preflop-only — re-scope to PTFT flops", prio=3),
    dict(id="bm8-monotone", sys="BM8", cls="monotone", why="monotone = high check for the covered stack",
         gt="icm-8m-200ptbubblemid", depth=None, stacks="BTN~50 / BB~20", line=None, board="AhJh5h",
         walk="BLOCKED: bubble gametype is preflop-only — re-scope to PTFT flops", prio=3),
    dict(id="bm9-j75", sys="BM9", cls="J-high, BB covers BTN", why="BB lead (near pure on boards BTN misses)",
         gt="icm-8m-200ptbubblemid", depth=None, stacks="BB~50 / BTN~20", line=None, board="Jh7c5d",
         walk="BLOCKED: bubble gametype is preflop-only — re-scope to PTFT flops", prio=3),
    dict(id="bm9-q76", sys="BM9", cls="Q-high, BB covers BTN", why="BB mid-board lead + BTN check-back",
         gt="icm-8m-200ptbubblemid", depth=None, stacks="BB~50 / BTN~20", line=None, board="Qc7h6d",
         walk="BLOCKED: bubble gametype is preflop-only — re-scope to PTFT flops", prio=3),
    dict(id="bm10-k84", sys="BM10", cls="K-high, UTG covers BB", why="KT = pure check-call (strong CR threshold)",
         gt="icm-8m-200ptbubblemid", depth=None, stacks="UTG~40-50 / BB~15-20", line=None, board="Kc8h4d",
         walk="BLOCKED: bubble gametype is preflop-only — re-scope to PTFT flops", prio=3),
    dict(id="bm11-aq2-r", sys="BM11", cls="AQ2 rainbow", why="rainbow: no flush draw -> no overbet when covered",
         gt="icm-8m-200ptbubblemid", depth=None, stacks="BTN~23 / BB shallow", line=None, board="AhQd2c",
         walk="BLOCKED: bubble gametype is preflop-only — re-scope to PTFT flops", prio=3),
    dict(id="bm11-aq2-t", sys="BM11", cls="AQ2 two-tone", why="flush drives the overbet — the texture contrast",
         gt="icm-8m-200ptbubblemid", depth=None, stacks="BTN~23 / BB shallow", line=None, board="AhQh2c",
         walk="BLOCKED: bubble gametype is preflop-only — re-scope to PTFT flops", prio=3),
    dict(id="bm11-kq6-t", sys="BM11", cls="KQ6 two-tone", why="two-tone vs rainbow = vastly different in ICM",
         gt="icm-8m-200ptbubblemid", depth=None, stacks="BTN~23 / BB shallow", line=None, board="KhQh6c",
         walk="BLOCKED: bubble gametype is preflop-only — re-scope to PTFT flops", prio=3),
]

# ---- The core learn set -------------------------------------------------
# The minimal board universe: one board per distinct decision the course
# teaches — a bucket, a contrast pair, or a named risk factor. Everything
# not listed here is a variant of a lesson another board already carries
# (mono/two-low/miss/paired duplicates, kicker-taper repeats, sizing nuance)
# and is extended material: nice to have, not needed to learn the systems.
CORE = {
    # S1: the six buckets of the c-bet tree + the depth-leak contrasts
    "s1-k83", "s1-kk3", "s1-aj5", "s1-j66", "s1-ak2", "s1-963",
    "s1-k83-20", "s1-k83-100",
    # S2: ace-clean 100%, K+deuce 100%, two-low-cards mix, BTN-miss
    "s2-a95", "s2-kj2", "s2-k93", "s2-543",
    # S3: key card high, key card low (gut shots), paired/deuce-death
    "s3-k72", "s3-a42", "s3-jj3",
    # S4: the 3-flush one-club chain (System 2); System 1 rides bottom-up
    "s4-q106",
    # S6: CR-all-Kx short, kicker taper, low-flop, flush-draw trap
    "s6-k84", "s6-q75", "s6-864", "s6-k94",
    # S7: MDF trash-identification, tiny-raise fold~2%
    "s7-jj3", "s7-662",
    # S9: super gut shot, check-raise build, sizing sensitivity
    "s9-j105", "s9-t52", "s9-q62",
    # S12: high board fold, low connected defend, low disconnected fold
    "s12-k84", "s12-984", "s12-842",
    # BM: range-bet, overbet-on-gut-shots, mono-check, BB-lead, texture pair
    "bm8-akq", "bm8-j74", "bm8-monotone",
    "bm9-j75", "bm10-k84", "bm11-aq2-r", "bm11-aq2-t",
}


def core_plan():
    return [e for e in PLAN if e["id"] in CORE]


def extended_plan():
    return [e for e in PLAN if e["id"] not in CORE]

# ---- The study deck ------------------------------------------------------
# The overall universe, human-memorizable: 15 archetype boards. Every flop a
# player sees maps to one of these; every system lesson is an overlay on the
# archetype (position, stack, pot type), not a new board. The rule line is
# the flashcard: recognize the texture, recall the default, adjust for the
# overlay. The solve plan above decides WHERE each archetype gets solved.
DECK = [
    # HIGH — the c-bet ladder (S1/S2)
    dict(id="a-clean", group="High", label="A-high clean", board="Ac9h5d",
         rule="Range bet small — the ace is yours (deeper = a bit more checking)"),
    dict(id="a-mono", group="High", label="A-high monotone", board="AhJh5h",
         rule="Polarize: bet flushes/sets/trash, check medium"),
    dict(id="akx", group="High", label="AKx Broadway", board="AsKd2c",
         rule="Broadway pair: slow down — not 100%"),
    dict(id="k-clean", group="High", label="K-high clean", board="Kh8h3c",
         rule="Range bet; shallower = bet MORE, deeper = more checking"),
    dict(id="k-deuce", group="High", label="K-high + deuce/three", board="KdJh2c",
         rule="The low card disconnects — still 100%"),
    dict(id="k-two-low", group="High", label="K-high, two low cards", board="Kh6h3c",
         rule="Lows interact — mix: bet top+bottom, check middle"),
    dict(id="k-mono", group="High", label="K-high monotone", board="Kc8c4c",
         rule="Substantially more checking than two-tone/rainbow"),
    dict(id="broadway-connected", group="High", label="Broadway connected", board="JdTc5h",
         rule="Straights live: gut shot + BDFD = super draw (defend/CR)"),

    # PAIRED — the contrast pair is the lesson (S1/S7)
    dict(id="h-h-l", group="Paired", label="High-high-low", board="KsKd3c",
         rule="NOT a risk factor — range bet"),
    dict(id="h-l-l", group="Paired", label="High-low-low", board="Ts5c5d",
         rule="Bet trips + trash, check underpairs (THE paired risk factor)"),
    dict(id="low-pair", group="Paired", label="Low pair", board="6s6h2c",
         rule="Fold almost nothing to small raises; find the trash, not more"),

    # LOW — 9-high and below (S1/S2/S3/S12)
    dict(id="nine-connected", group="Low", label="9-high connected", board="9h6d3c",
         rule="No 100% exists — mix ~70/30; no offsuit air in EP"),
    dict(id="wheel", group="Low", label="Wheel miss board", board="5h4h3c",
         rule="Wide ranges miss: c-bettor checks more, defender is sticky/gangster"),
    dict(id="brick", group="Low", label="Low brick", board="7c4h2d",
         rule="Fewest draws: BDFDs trade at a premium; identify the worst hand"),

    # ACE + LOWS — the defend-system archetype (S3/S12)
    dict(id="a-low-conn", group="Low", label="Ace-high, connected lows", board="Ah4d2s",
         rule="The ace is yours, but the lows make wheels — defending builds around the middle low card (gut shots)"),
]

# deck archetype -> plan entry ids that instantiate it (the solves to show
# the archetype on the lines/depths where its strategy is taught)
DECK_LINKS = {
    "a-clean": ["s2-a95"],
    "a-mono": ["s1-aj5", "s2-a72m"],
    "akx": ["s1-ak2"],
    "k-clean": ["s1-k83", "s1-k83-20", "s1-k83-100"],
    "k-deuce": ["s2-kj2"],
    "k-mono": ["s2-k84m"],
    "broadway-connected": ["s9-j105", "s3-kq8"],
    "h-h-l": ["s1-kk3"],
    "h-l-l": ["s1-j66", "s1-t55", "s7-k55", "s3-jj3"],
    "low-pair": ["s7-662", "s7-533", "s7-t33"],
    "nine-connected": ["s2-963", "s1-963"],
    "wheel": ["s2-543", "s2-742"],
    "brick": ["s12-842", "s12-752"],
    "a-low-conn": ["s3-a42", "s12-a85"],
    "k-two-low": ["s2-k93", "s2-k63", "s2-t53", "s3-k72"],
}

# ---- The situation set ----------------------------------------------------
# The overlay layer of the universe: the situations a board is played in.
# Every system lesson is (archetype board) x (situation) — never more boards,
# never more situations than these. Full-deck study = the matrix below, and
# a blank cell is a deliberate "the overlay doesn't change this lesson".
SITUATIONS = [
    dict(id="cbet-oop-40", label="EP open, BB call — c-bet, 40bb", sys="S1"),
    dict(id="cbet-depth", label="same line, 20bb / 100bb", sys="S1 depth rule"),
    dict(id="cbet-ip-50", label="BTN open, BB call — c-bet/check, 50bb", sys="S2 (+S4 rivers)"),
    dict(id="limp-stab-70", label="SB limp, BB check — vs stab, 70bb", sys="S3"),
    dict(id="bvb-river-40", label="SB open, BB defend — river chain, 40bb", sys="S4"),
    dict(id="caller-ip-100", label="EP open, CO call — 100bb", sys="S4/S10"),
    dict(id="bb-cr-short", label="BB vs c-bet, 13-25bb — check-raise", sys="S6"),
    dict(id="bb-defend-deep", label="BB vs c-bet, 60-80bb — call/raise", sys="S9"),
    dict(id="vs-cr-25-50", label="c-bettor vs check-raise, BTN 25-50bb", sys="S7"),
    dict(id="3bet-oop-40", label="EP open, 3-bet, call — defend, 40/25bb", sys="S12"),
    dict(id="bubble-asym", label="bubble, covering / covered stacks", sys="BM8-11"),
]

# every CORE plan entry -> (deck archetype, situation)
DECK_MATRIX = {
    # cbet-oop-40
    ("k-clean", "cbet-oop-40"): ["s1-k83"],
    ("h-h-l", "cbet-oop-40"): ["s1-kk3"],
    ("a-mono", "cbet-oop-40"): ["s1-aj5"],
    ("h-l-l", "cbet-oop-40"): ["s1-j66"],
    ("akx", "cbet-oop-40"): ["s1-ak2"],
    ("nine-connected", "cbet-oop-40"): ["s1-963"],
    # cbet-depth
    ("k-clean", "cbet-depth"): ["s1-k83-20", "s1-k83-100"],
    # cbet-ip-50
    ("a-clean", "cbet-ip-50"): ["s2-a95"],
    ("k-deuce", "cbet-ip-50"): ["s2-kj2"],
    ("k-two-low", "cbet-ip-50"): ["s2-k93"],
    ("wheel", "cbet-ip-50"): ["s2-543"],
    ("nine-connected", "cbet-ip-50"): ["s2-963"],
    # limp-stab-70
    ("k-two-low", "limp-stab-70"): ["s3-k72"],
    ("a-low-conn", "limp-stab-70"): ["s3-a42"],
    ("h-l-l", "limp-stab-70"): ["s3-jj3"],
    ("broadway-connected", "limp-stab-70"): ["s3-kq8"],
    # bvb-river-40
    ("broadway-connected", "bvb-river-40"): ["s4-q106"],
    # caller-ip-100
    ("akx", "caller-ip-100"): ["s4-akq"],
    # bb-cr-short
    ("k-two-low", "bb-cr-short"): ["s6-k84", "s6-q75", "s6-k94"],
    ("nine-connected", "bb-cr-short"): ["s6-864"],
    # bb-defend-deep
    ("broadway-connected", "bb-defend-deep"): ["s9-j105"],
    ("k-two-low", "bb-defend-deep"): ["s9-t52", "s9-q62"],
    # vs-cr-25-50
    ("h-l-l", "vs-cr-25-50"): ["s7-jj3"],
    ("low-pair", "vs-cr-25-50"): ["s7-662"],
    # 3bet-oop-40
    ("k-two-low", "3bet-oop-40"): ["s12-k84"],
    ("nine-connected", "3bet-oop-40"): ["s12-984"],
    ("brick", "3bet-oop-40"): ["s12-842"],
    # bubble-asym
    ("akx", "bubble-asym"): ["bm8-akq"],
    ("a-clean", "bubble-asym"): ["bm8-aj8", "bm11-aq2-r", "bm11-aq2-t"],
    ("brick", "bubble-asym"): ["bm8-j74"],
    ("a-mono", "bubble-asym"): ["bm8-monotone"],
    ("k-two-low", "bubble-asym"): ["bm9-j75", "bm10-k84"],
}
