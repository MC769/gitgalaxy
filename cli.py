import argparse
import os
import shutil
import sys

from rich.console import Console

from . import __version__
from .gitlog import load_commits, NotAGitRepoError, EmptyRepoError
from .starfield import StarField, AuthorColors
from .render import animate, render_static, export_ascii, export_svg


def build_parser():
    parser = argparse.ArgumentParser(
        prog="gitgalaxy",
        description="Turn a git repo's commit history into a starfield in your terminal.",
    )
    parser.add_argument("repo", nargs="?", default=".", help="Path to a git repository (default: current dir)")
    parser.add_argument("--days", type=int, default=None, help="Only include commits from the last N days")
    parser.add_argument("--limit", type=int, default=None, help="Only include the most recent N commits")
    parser.add_argument("--branch", type=str, default=None, help="Limit to a specific branch/ref")
    parser.add_argument("--width", type=int, default=None, help="Grid width (default: terminal width)")
    parser.add_argument("--height", type=int, default=None, help="Grid height (default: auto)")
    parser.add_argument("--speed", type=float, default=6.0, help="Animation duration in seconds (default: 6)")
    parser.add_argument("--fps", type=int, default=20, help="Animation frames per second (default: 20)")
    parser.add_argument("--no-anim", action="store_true", help="Skip the animation and print the final sky instantly")
    parser.add_argument("--export", choices=["svg", "ascii"], help="Also export a static image/text file")
    parser.add_argument("--out", type=str, default=None, help="Output path for --export (default: gitgalaxy.<ext>)")
    parser.add_argument("--title", type=str, default=None, help="Title shown above the sky")
    parser.add_argument("--version", action="version", version=f"gitgalaxy {__version__}")
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    console = Console()

    repo_path = os.path.abspath(args.repo)

    try:
        commits = load_commits(repo_path, days=args.days, limit=args.limit, branch=args.branch)
    except NotAGitRepoError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        return 1
    except EmptyRepoError as e:
        console.print(f"[yellow]{e}[/yellow]")
        return 0

    if not commits:
        console.print("[yellow]No commits found for the given range.[/yellow]")
        return 0

    term_size = shutil.get_terminal_size(fallback=(100, 40))
    width = args.width or min(max(term_size.columns - 6, 20), 140)
    height = args.height
    if height is None:
        import math

        height = max(8, min(40, math.ceil(len(commits) / max(width, 1)) + 6))

    repo_name = os.path.basename(repo_path.rstrip(os.sep)) or repo_path
    title = args.title or f"\u2728 {repo_name}"

    field = StarField(width=width, height=height)
    author_colors = AuthorColors()
    stars = field.place(commits, author_colors)

    if args.no_anim:
        render_static(console, stars, width, height, commits, title)
    else:
        animate(
            console,
            stars,
            width,
            height,
            commits,
            title,
            duration=args.speed,
            fps=args.fps,
        )

    if args.export:
        ext = args.export
        out_path = args.out or f"gitgalaxy.{ext}"
        if ext == "svg":
            export_svg(stars, width, height, out_path)
        else:
            export_ascii(stars, width, height, out_path)
        console.print(f"\n[green]Saved {ext.upper()} to[/green] [bold]{out_path}[/bold]")

    return 0


if __name__ == "__main__":
    sys.exit(main())
