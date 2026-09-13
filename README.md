# straddle-solutions

Raw GTO Wizard solution archives backing the [straddle](https://github.com/JulienDanh/straddle)
poker study app. **Licensed data — this repo must stay private.**

The main app repo gitignores this directory (`packages/ranges/imports/`); this
repo is its backup home. This directory is a nested git checkout of this repo.

## Transcripts

`transcripts/Simple Poker Systems/` and `transcripts/Bubble Mastery/` hold the
source course transcripts (licensed training material). The public straddle
repo converts them into the study guide but does not carry them; extraction
reads them from here (`packages/ranges/imports/transcripts/` on disk).

## Layout

- `solutions/<gametype>/<stacks>/<category>/<name>.json` — raw spot-solution
  payloads captured off the wire from the real GTO Wizard app:
  - `<gametype>`: `cev` (MTTGeneral_8m), `icm-8m-200ptbubblemid` (200-man
    bubble, preflop-only), `mttgeneral-icm-8m-200-ptft` (200-man final table)
  - `<stacks>`: bare depth for symmetric spots (e.g. `40`), all eight
    dash-joined stacks for asymmetric configs (e.g. `17-26-32-23-20-13-34-75`)
  - `<category>`: `rfi/<position>`, `vs-open/<opener>-<defender>`,
    `flops/<preflop-line>/<board>-<flop-actions>`
  - Each file carries the full payload: `game` (spot definition),
    `action_solutions` (per-action strategy, per-combo EVs, equity/hand/draw
    aggregates), hand/draw category arrays and blocker rates
- `catalog.json` — cached solutions-library catalog (1,101 gametypes with
  their exact depth/stack configs), used to validate fetches before
  navigating
- `*.txt` / `*-fetched.json` / `*-converted.json` — earliest raw range-view
  pastes from the manual import era, kept for provenance

## Workflow

Captures are made by `scripts/fetch_browser.py` in this repo (CDP walk of
the logged-in debug Chrome; the app itself signs every request). Solutions
are static, so captures are reused from this archive instead of re-fetched.
After new captures:

```
git add -A && git commit -m "<what was scraped>" && git push
```

`gw_to_store.py` converts these into the store (`packages/ranges/data/` in
the main repo, two levels up), which feeds the app's range library.
