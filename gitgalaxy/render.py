import time

from rich.console import Console, Group
from rich.text import Text
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich.align import Align


def _build_grid_text(stars, width, height, flash_set=None):
    flash_set = flash_set or set()
    grid = [[(" ", None) for _ in range(width)] for _ in range(height)]
    for star in stars:
        if star in flash_set:
            grid[star.y][star.x] = (star.glyph, "bold white on grey19")
        else:
            grid[star.y][star.x] = (star.glyph, f"{star.style} {star.color}")

    text = Text()
    for row in grid:
        for ch, style in row:
            text.append(ch, style=style)
        text.append("\n")
    return text


def _legend_table(author_colors, top_n=8):
    table = Table.grid(padding=(0, 2))
    table.add_column()
    table.add_column()
    items = author_colors.items()[:top_n]
    row = []
    for author, color in items:
        row.append(Text(f"\u2726 {author}", style=color))
    for i in range(0, len(row), 3):
        table.add_row(*row[i : i + 3])
    return table


def _stats_panel(commits, title):
    if not commits:
        return Panel("No commits found.", title=title)
    total = len(commits)
    total_churn = sum(c.churn for c in commits)
    authors = {c.author for c in commits}
    start = min(c.timestamp for c in commits).strftime("%Y-%m-%d")
    end = max(c.timestamp for c in commits).strftime("%Y-%m-%d")
    counts = {}
    for c in commits:
        counts[c.author] = counts.get(c.author, 0) + 1
    top_author = max(counts.items(), key=lambda kv: kv[1])

    body = Text()
    body.append(f"{total:,} commits", style="bold bright_white")
    body.append("  \u00b7  ")
    body.append(f"{total_churn:,} lines changed", style="bold bright_white")
    body.append("  \u00b7  ")
    body.append(f"{len(authors)} contributor(s)", style="bold bright_white")
    body.append("\n")
    body.append(f"{start} \u2192 {end}", style="dim")
    body.append("\n")
    body.append(f"Brightest star: {top_author[0]} ({top_author[1]} commits)", style="italic")
    return Panel(body, title=title, border_style="bright_blue")


def render_static(console: Console, stars, width, height, commits, title):
    grid_text = _build_grid_text(stars, width, height)
    console.print(Panel(grid_text, border_style="grey35", title=title))
    console.print(_legend_table_from_stars(stars))
    console.print(_stats_panel(commits, "\u2728 Galaxy Stats"))


def _legend_table_from_stars(stars, top_n=10):
    seen = {}
    for star in stars:
        seen.setdefault(star.commit.author, star.color)
    table = Table.grid(padding=(0, 2))
    row = []
    for author, color in list(seen.items())[:top_n]:
        row.append(Text(f"\u2726 {author}", style=color))
    if not row:
        return Text("")
    for i in range(0, len(row), 3):
        table.add_row(*row[i : i + 3])
    return table


def animate(console: Console, stars, width, height, commits, title, duration=6.0, fps=20):
    if not stars:
        console.print("[yellow]No commits to animate.[/yellow]")
        return

    total_frames = max(1, int(duration * fps))
    n = len(stars)
    frame_boundaries = [int(round(i * n / total_frames)) for i in range(total_frames + 1)]

    revealed = []
    with Live(console=console, refresh_per_second=fps, screen=False) as live:
        for f in range(total_frames):
            start_idx = frame_boundaries[f]
            end_idx = frame_boundaries[f + 1]
            newly = stars[start_idx:end_idx]
            revealed.extend(newly)
            flash_set = set(newly)
            grid_text = _build_grid_text(revealed, width, height, flash_set=flash_set)
            frame = Panel(grid_text, border_style="grey35", title=title, subtitle=f"{len(revealed)}/{n} commits")
            live.update(frame)
            time.sleep(1 / fps)

        final_text = _build_grid_text(stars, width, height)
        live.update(Panel(final_text, border_style="grey35", title=title, subtitle=f"{n}/{n} commits"))

    console.print(_legend_table_from_stars(stars))
    console.print(_stats_panel(commits, "\u2728 Galaxy Stats"))


def export_ascii(stars, width, height, path):
    grid = [[" " for _ in range(width)] for _ in range(height)]
    for star in stars:
        grid[star.y][star.x] = star.glyph
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join("".join(row) for row in grid))
        f.write("\n")


_SVG_COLOR_MAP = {
    "bright_cyan": "#56d8e0",
    "bright_magenta": "#e05de0",
    "bright_yellow": "#f0e05a",
    "bright_green": "#6ee06e",
    "bright_red": "#ff6b6b",
    "bright_blue": "#6b9bff",
    "orange3": "#ff9f45",
    "turquoise2": "#45e0d0",
    "plum2": "#e0a3ff",
    "gold3": "#e0c04a",
}


def export_svg(stars, width, height, path, cell=16):
    w_px = width * cell
    h_px = height * cell
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w_px}" height="{h_px}" '
        f'viewBox="0 0 {w_px} {h_px}">',
        f'<rect width="{w_px}" height="{h_px}" fill="#0d1117"/>',
    ]
    max_churn = max((s.commit.churn for s in stars), default=1) or 1
    for star in stars:
        cx = star.x * cell + cell / 2
        cy = star.y * cell + cell / 2
        radius = 1.4 + 3.2 * (star.commit.churn / max_churn) ** 0.5
        color = _SVG_COLOR_MAP.get(star.color, "#ffffff")
        title = f"{star.commit.sha[:7]} by {star.commit.author}: {star.commit.message}"
        safe_title = (
            title.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
        )
        parts.append(
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{radius:.1f}" fill="{color}" opacity="0.9">'
            f"<title>{safe_title}</title></circle>"
        )
    parts.append("</svg>")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))
