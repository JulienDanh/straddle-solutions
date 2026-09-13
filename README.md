# straddle-solutions

Raw GTO Wizard solution archives backing the [straddle](https://github.com/JulienDanh/straddle)
poker study app. **Licensed data — this repo must stay private.**

The main app repo gitignores this directory (`packages/ranges/imports/`); this
repo is its backup home. This directory is a nested git checkout of this repo.

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

Captures are made by `packages/ranges/scripts/fetch_browser.py` in the main
repo (CDP walk of the logged-in debug Chrome; the app itself signs every
request). Solutions are static, so captures are reused from this archive
instead of re-fetched. After new captures:

```
git add -A && git commit -m "<what was scraped>" && git push
```

The store (`packages/ranges/data/` in the main repo) converts these into the
app's range library via `gw_to_store.py`.
