import hashlib
import random

PALETTE = [
    "bright_cyan",
    "bright_magenta",
    "bright_yellow",
    "bright_green",
    "bright_red",
    "bright_blue",
    "orange3",
    "turquoise2",
    "plum2",
    "gold3",
]

GLYPHS = [
    (0, ".", "dim white"),
    (10, "+", "white"),
    (40, "*", "bold white"),
    (120, "\u2726", "bold white"),
    (400, "\u2735", "bold white"),
]


def glyph_for_churn(churn: int):
    chosen = GLYPHS[0]
    for threshold, glyph, style in GLYPHS:
        if churn >= threshold:
            chosen = (threshold, glyph, style)
    return chosen[1], chosen[2]


def _hash_to_ints(sha: str):
    digest = hashlib.md5(sha.encode("utf-8")).hexdigest()
    a = int(digest[:8], 16)
    b = int(digest[8:16], 16)
    return a, b


class AuthorColors:
    def __init__(self):
        self._map = {}
        self._next = 0

    def color_for(self, author: str) -> str:
        if author not in self._map:
            self._map[author] = PALETTE[self._next % len(PALETTE)]
            self._next += 1
        return self._map[author]

    def items(self):
        return list(self._map.items())


class Star:
    __slots__ = ("commit", "x", "y", "glyph", "style", "color")

    def __init__(self, commit, x, y, glyph, style, color):
        self.commit = commit
        self.x = x
        self.y = y
        self.glyph = glyph
        self.style = style
        self.color = color


class StarField:
    """Places commits deterministically on a width x height grid, avoiding overlap."""

    def __init__(self, width: int, height: int):
        self.width = max(10, width)
        self.height = max(6, height)
        self._occupied = set()
        self.stars = []

    def _find_free_slot(self, seed_x, seed_y):
        if (seed_x, seed_y) not in self._occupied:
            return seed_x, seed_y
        rng = random.Random(seed_x * 100003 + seed_y)
        radius = 1
        while radius < max(self.width, self.height):
            candidates = []
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    if abs(dx) != radius and abs(dy) != radius:
                        continue
                    nx, ny = seed_x + dx, seed_y + dy
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        candidates.append((nx, ny))
            rng.shuffle(candidates)
            for c in candidates:
                if c not in self._occupied:
                    return c
            radius += 1
        return seed_x % self.width, seed_y % self.height

    def place(self, commits, author_colors: AuthorColors):
        self.stars = []
        for commit in commits:
            a, b = _hash_to_ints(commit.sha)
            seed_x = a % self.width
            seed_y = b % self.height
            x, y = self._find_free_slot(seed_x, seed_y)
            self._occupied.add((x, y))
            glyph, style = glyph_for_churn(commit.churn)
            color = author_colors.color_for(commit.author)
            self.stars.append(Star(commit, x, y, glyph, style, color))
        return self.stars
