# StrengthWise — Capstone Presentation 2026

## View the slides

```bash
open presentation/index.html
```

Or double-click `index.html` in Finder. Works in Chrome and Firefox without a server.

For **speaker notes** (`S` key), run a local server first:

```bash
cd presentation && python3 -m http.server 8765
# open http://localhost:8765
```

## Keyboard shortcuts

| Key | Action |
|-----|--------|
| `Space` / `→` | Next slide |
| `←` | Previous slide |
| `S` | Speaker notes |
| `F` | Fullscreen |
| `O` | Overview |
| `B` | Blank screen |

## Export to PDF

A pre-built PDF is included: `strengthwise-capstone-2026.pdf`

To regenerate:

```bash
# 1. start the server
cd presentation && python3 -m http.server 8765

# 2. in a second terminal, run decktape
npx decktape reveal "http://localhost:8765" presentation/strengthwise-capstone-2026.pdf --size 1600x900
```

`decktape` renders each slide individually — charts and dark background come through correctly.
