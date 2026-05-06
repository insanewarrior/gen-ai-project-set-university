# StrengthWise — Capstone Presentation 2026

14 slides. Built with Reveal.js.

| # | Slide |
|---|---|
| 1 | Hero / Title |
| 2 | Problem & Market |
| 3 | Competitive Landscape |
| 4 | Solution & UVP |
| 5 | Technical Architecture |
| 6 | How It Works (RAG Flow) |
| 7 | Knowledge Base & Test Dataset |
| 8 | AI Evaluation Framework |
| 9 | Business Model |
| 10 | Unit Economics |
| 11 | KPIs & Metrics |
| 12 | Roadmap & Scalability |
| 13 | Live Demo |
| 14 | Q&A |

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
