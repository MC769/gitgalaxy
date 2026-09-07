# ✨ GitGalaxy

Turn any git repo's commit history into an animated **starfield** in your terminal.

Every commit becomes a star: **color = author**, **size = lines changed**, and stars twinkle into existence in chronological order as the animation plays. Export a static PNG-ready SVG or plain ASCII art to drop into your README.

```
╭──────────────────────────────── ✨ my-project ─────────────────────────────────╮
│     ..                                                                       │
│            *                                          .                      │
│                   .                                                          │
│                       .  .            .                                      │
│                                  .                      *                    │
│    * .                .                                                      │
│      .                   .                                                   │
│                            ..                          .                     │
│           .                             *                                    │
╰──────────────────────────────────────────────────────────────────────────────╯
✦ Alice  ✦ Bob  ✦ Carol
╭────────────────────────────── ✨ Galaxy Stats ───────────────────────────────╮
│ 30 commits  ·  285 lines changed  ·  3 contributor(s)                        │
│ 2024-01-02 → 2024-03-06                                                      │
│ Brightest star: Alice (15 commits)                                           │
╰──────────────────────────────────────────────────────────────────────────────╯
```

(In your terminal this is in full color and the stars twinkle in one-by-one — the block above is just a plain-text snapshot.)

## Install

```bash
pip install gitgalaxy
```

Or run from source:

```bash
git clone https://github.com/MC769/gitgalaxy.git
cd gitgalaxy
pip install -e .
```

Requires Python 3.8+ and `git` on your `PATH`. The only dependency is [`rich`](https://github.com/Textualize/rich).

## Usage

```bash
# Animate the current repo's whole history
gitgalaxy

# Animate a specific repo
gitgalaxy ~/code/my-project

# Only the last 90 days, sped up
gitgalaxy --days 90 --speed 3

# Skip the animation, just print the final sky
gitgalaxy --no-anim

# Save a shareable SVG (great for embedding in a README)
gitgalaxy --no-anim --export svg --out sky.svg

# Save plain ASCII art
gitgalaxy --no-anim --export ascii --out sky.txt
```

### All options

| Flag | Description |
|---|---|
| `repo` (positional) | Path to a git repo (default: current directory) |
| `--days N` | Only include commits from the last N days |
| `--limit N` | Only include the most recent N commits |
| `--branch NAME` | Limit to a specific branch/ref |
| `--width N` | Grid width (default: terminal width) |
| `--height N` | Grid height (default: auto, scaled to commit count) |
| `--speed SECONDS` | Total animation duration (default: 6) |
| `--fps N` | Animation frame rate (default: 20) |
| `--no-anim` | Print the final sky instantly, no animation |
| `--export {svg,ascii}` | Also save a static export |
| `--out PATH` | Output path for `--export` (default: `gitgalaxy.<ext>`) |
| `--title TEXT` | Custom title shown above the sky |
| `--version` | Show version |

## How stars are placed

Each commit's position is derived deterministically from a hash of its commit SHA, so **the same repo always produces the same sky** — but different repos look different, and the layout doesn't just look like a boring grid. If two commits would land on the same cell, GitGalaxy searches outward in a spiral for the next free spot, so nothing overlaps.

- **Color** — assigned per author, in order of their first commit, cycling through a 10-color palette.
- **Glyph size** — `.` → `+` → `*` → `✦` → `✵` as total lines changed (insertions + deletions) in that commit increases.
- **Flash** — the newest stars in each animation frame briefly flash white before settling into their author's color, like they just ignited.

## Embedding in your own README

```bash
gitgalaxy --no-anim --export svg --out gitgalaxy.svg
```

Then in your README:

```markdown
![Commit galaxy](./gitgalaxy.svg)
```

The SVG includes hoverable tooltips (commit SHA, author, message) when viewed in a browser or on GitHub.

## Why

Commit graphs and contribution heatmaps are everywhere. This is the same information — activity over time, by author, weighted by size — but rendered as something you'd actually want to stare at, or drop into a portfolio README as a screenshot.

## Development

```bash
git clone https://github.com/MC769/gitgalaxy.git
cd gitgalaxy
pip install -e .
gitgalaxy .   # visualize gitgalaxy's own history
```

Project layout:

```
gitgalaxy/
├── gitgalaxy/
│   ├── cli.py        # argument parsing, orchestration
│   ├── gitlog.py      # parses `git log --numstat` into Commit objects
│   ├── starfield.py    # deterministic star placement + author colors
│   └── render.py        # terminal animation + static/SVG/ASCII export
├── pyproject.toml
└── README.md
```

## License

MIT
