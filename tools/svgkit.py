"""Shared building blocks for the profile's SVG assets.

Everything here produces plain strings. No third-party dependencies, so the
build runs anywhere Python 3.9+ is available (locally or in GitHub Actions).

Motion rules used by every asset (see docs/DESIGN.md):
  * CSS @keyframes only (no SMIL), so `prefers-reduced-motion` can stop all of it.
  * The *base* style of every animated element is its meaningful final state.
    If animation is unsupported or reduced, the picture still reads correctly.
  * Packets travel along wires with stroke-dashoffset. Path lengths are computed
    here instead of relying on `pathLength`, which some renderers ignore.
  * CSS animation is never put on an element that also has a `transform`
    attribute (CSS would override it); position with a wrapper <g> instead.
"""
from __future__ import annotations

import html
import math
import re

# --------------------------------------------------------------------------- #
# Brand tokens
# --------------------------------------------------------------------------- #
C = {
    "bg": "#0A0E1F",       # midnight navy (plate)
    "bg2": "#121741",      # deep indigo (plate gradient end)
    "panel": "#151B42",    # glass panel fill
    "panel2": "#1B2253",   # raised panel / header fill
    "line": "#2B3470",     # hairlines, wires at rest
    "grid": "#202860",     # dot grid
    "text": "#ECEBFF",     # primary text
    "soft": "#BFC3EA",     # secondary text
    "muted": "#8990C0",    # tertiary text
    "dim": "#5D6499",      # labels, comments
    "blue": "#4F7BFF",     # electric blue
    "lav": "#B7A5FF",      # lavender (identity, response path)
    "cyan": "#5BE1F0",     # request / data in motion
    "mag": "#FF74C0",      # response / experience (used sparingly)
    "mid": "#6B74B3",      # mid-tone that reads on GitHub light AND dark themes
}

SANS = ("'Segoe UI Variable Display','Segoe UI',-apple-system,BlinkMacSystemFont,"
        "'SF Pro Display','Helvetica Neue',Ubuntu,Arial,sans-serif")
MONO = ("'JetBrains Mono','Cascadia Code','SF Mono',SFMono-Regular,Menlo,Consolas,"
        "'Liberation Mono',monospace")

EASE = "cubic-bezier(.5,0,.25,1)"      # travel: accelerate, then settle
SETTLE = "cubic-bezier(.2,.7,.2,1)"    # entrances


def esc(s: str) -> str:
    return html.escape(str(s), quote=False)


def attr(s: str) -> str:
    return html.escape(str(s), quote=True)


# --------------------------------------------------------------------------- #
# Path length (absolute M/L/H/V/C/Q/Z only — that is all the assets use)
# --------------------------------------------------------------------------- #
_TOK = re.compile(r"[MLHVCQZ]|-?\d*\.?\d+(?:e-?\d+)?", re.I)


def _bez(pts, n=160):
    total, (px, py) = 0.0, pts[0]
    for i in range(1, n + 1):
        t = i / n
        mt = 1 - t
        if len(pts) == 4:
            x = mt**3*pts[0][0] + 3*mt*mt*t*pts[1][0] + 3*mt*t*t*pts[2][0] + t**3*pts[3][0]
            y = mt**3*pts[0][1] + 3*mt*mt*t*pts[1][1] + 3*mt*t*t*pts[2][1] + t**3*pts[3][1]
        else:
            x = mt*mt*pts[0][0] + 2*mt*t*pts[1][0] + t*t*pts[2][0]
            y = mt*mt*pts[0][1] + 2*mt*t*pts[1][1] + t*t*pts[2][1]
        total += math.hypot(x - px, y - py)
        px, py = x, y
    return total


def path_length(d: str) -> float:
    toks = _TOK.findall(d)
    i, cmd = 0, None
    x = y = sx = sy = 0.0
    length = 0.0

    def nums(k):
        nonlocal i
        out = [float(v) for v in toks[i:i + k]]
        i += k
        return out

    while i < len(toks):
        if toks[i].isalpha():
            cmd = toks[i].upper()
            i += 1
            if cmd == "Z":
                length += math.hypot(sx - x, sy - y)
                x, y = sx, sy
                continue
        if cmd == "M":
            x, y = nums(2)
            sx, sy = x, y
            cmd = "L"
        elif cmd == "L":
            nx, ny = nums(2)
            length += math.hypot(nx - x, ny - y)
            x, y = nx, ny
        elif cmd == "H":
            (nx,) = nums(1)
            length += abs(nx - x)
            x = nx
        elif cmd == "V":
            (ny,) = nums(1)
            length += abs(ny - y)
            y = ny
        elif cmd == "C":
            x1, y1, x2, y2, nx, ny = nums(6)
            length += _bez([(x, y), (x1, y1), (x2, y2), (nx, ny)])
            x, y = nx, ny
        elif cmd == "Q":
            x1, y1, nx, ny = nums(4)
            length += _bez([(x, y), (x1, y1), (nx, ny)])
            x, y = nx, ny
        else:
            raise ValueError(f"unsupported path command {cmd!r} in {d!r}")
    return length


# --------------------------------------------------------------------------- #
# Animation registry: one per SVG. Returns class names; emits <style>.
# --------------------------------------------------------------------------- #
class Anim:
    def __init__(self):
        self._rules: list[str] = []
        self._cache: dict[tuple, str] = {}

    def add(self, frames: dict, dur: float, delay: float = 0.0, loop: bool = True,
            timing: str = EASE) -> str:
        """frames: {percent: "css; css"}; returns a class name."""
        key = (tuple(sorted(frames.items())), dur, delay, loop, timing)
        if key in self._cache:
            return self._cache[key]
        name = f"a{len(self._cache)}"
        self._cache[key] = name
        body = " ".join(f"{p:g}%{{{css}}}" for p, css in sorted(frames.items()))
        it = "infinite" if loop else "1"
        self._rules.append(f"@keyframes k{name}{{{body}}}")
        self._rules.append(f".{name}{{animation:k{name} {dur}s {timing} {delay}s {it} both}}")
        return name

    # Common one-shot entrances --------------------------------------------
    def fade_up(self, delay: float, dur: float = .9, dist: float = 14) -> str:
        return self.add({0: f"opacity:0;transform:translateY({dist}px)",
                         100: "opacity:1;transform:translateY(0)"},
                        dur, delay, loop=False, timing=SETTLE)

    def fade_in(self, delay: float, dur: float = .8) -> str:
        return self.add({0: "opacity:0", 100: "opacity:1"}, dur, delay, loop=False, timing=SETTLE)

    def draw(self, length: float, delay: float, dur: float = 1.4) -> str:
        """Line-drawing entrance. Pair with stroke-dasharray=length on the element."""
        return self.add({0: f"stroke-dashoffset:{length:.1f}", 100: "stroke-dashoffset:0"},
                        dur, delay, loop=False, timing=SETTLE)

    def window(self, T: float, on: float, off: float, a: str, b: str,
               ramp: float = 2.0, delay: float = 0.0) -> str:
        """Loop of T seconds: state `a`, switching to `b` during [on%, off%]."""
        frames = {0: a, max(on - ramp, 0.01): a, on: b, off: b,
                  min(off + ramp, 99.99): a, 100: a}
        return self.add(frames, T, delay)

    def css(self) -> str:
        return "\n".join(self._rules)


def style_block(anim: Anim, extra: str = "") -> str:
    return f"""<style>
.sans{{font-family:{SANS}}}
.mono{{font-family:{MONO}}}
.b{{font-weight:700}} .sb{{font-weight:600}}
.fb{{transform-box:fill-box;transform-origin:center}}
{extra}
{anim.css()}
/* Respect the viewer's OS setting: every element falls back to its final state. */
@media (prefers-reduced-motion: reduce){{*{{animation:none!important}}}}
</style>"""


# --------------------------------------------------------------------------- #
# Reusable pieces
# --------------------------------------------------------------------------- #
def svg_open(w: int, h: int, title: str, desc: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" role="img" aria-labelledby="t d">\n'
            f'<title id="t">{esc(title)}</title>\n<desc id="d">{esc(desc)}</desc>\n')


def plate_defs(uid: str = "p") -> str:
    """Gradients + dot grid for the dark 'workshop' plate."""
    return f"""<linearGradient id="{uid}bg" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="{C['bg']}"/><stop offset="1" stop-color="{C['bg2']}"/>
</linearGradient>
<radialGradient id="{uid}glowL" cx=".85" cy=".1" r=".6">
  <stop offset="0" stop-color="{C['lav']}" stop-opacity=".22"/><stop offset="1" stop-color="{C['lav']}" stop-opacity="0"/>
</radialGradient>
<radialGradient id="{uid}glowB" cx=".1" cy="1" r=".6">
  <stop offset="0" stop-color="{C['blue']}" stop-opacity=".2"/><stop offset="1" stop-color="{C['blue']}" stop-opacity="0"/>
</radialGradient>
<linearGradient id="{uid}edge" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{C['lav']}" stop-opacity="0"/>
  <stop offset=".5" stop-color="{C['lav']}" stop-opacity=".55"/>
  <stop offset="1" stop-color="{C['lav']}" stop-opacity="0"/>
</linearGradient>
<pattern id="{uid}dots" width="24" height="24" patternUnits="userSpaceOnUse">
  <circle cx="12" cy="12" r="1" fill="{C['grid']}"/>
</pattern>"""


def plate(w: int, h: int, uid: str = "p", rx: int = 26) -> str:
    """Dark rounded plate. Looks intentional on GitHub's light and dark themes."""
    return f"""<rect width="{w}" height="{h}" rx="{rx}" fill="url(#{uid}bg)"/>
<rect width="{w}" height="{h}" rx="{rx}" fill="url(#{uid}dots)" opacity=".7"/>
<rect width="{w}" height="{h}" rx="{rx}" fill="url(#{uid}glowL)"/>
<rect width="{w}" height="{h}" rx="{rx}" fill="url(#{uid}glowB)"/>
<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="{rx}" fill="none" stroke="{C['line']}"/>
<rect x="{rx}" y=".4" width="{w-2*rx}" height="1.2" fill="url(#{uid}edge)"/>"""


def panel(x, y, w, h, rx=14, fill=None, stroke=None, op=.92) -> str:
    fill = fill or C["panel"]
    stroke = stroke or C["line"]
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" '
            f'fill-opacity="{op}" stroke="{stroke}"/>'
            f'<line x1="{x+rx}" y1="{y+.5}" x2="{x+w-rx}" y2="{y+.5}" stroke="{C["lav"]}" '
            f'stroke-opacity=".25"/>')


def window_dots(x, y) -> str:
    return "".join(f'<circle cx="{x+i*14}" cy="{y}" r="4" fill="{c}" opacity=".85"/>'
                   for i, c in enumerate((C["mag"], C["lav"], C["cyan"])))


def text(x, y, s, size=16, fill=None, cls="sans", anchor="start", extra="") -> str:
    fill = fill or C["text"]
    a = f' text-anchor="{anchor}"' if anchor != "start" else ""
    return (f'<text x="{x}" y="{y}" class="{cls}" font-size="{size}" fill="{fill}"{a}'
            f'{(" " + extra) if extra else ""}>{esc(s)}</text>')


def wire(d, color=None, width=1.5, op=1.0, dash=None) -> str:
    color = color or C["line"]
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" '
            f'stroke-opacity="{op}" stroke-linecap="round"{da}/>')


def packet(anim: Anim, d: str, color: str, T: float, start: float, end: float,
           dash: float = 18, width: float = 4, delay: float = 0.0, glow: bool = True) -> str:
    """A glowing data packet that travels path `d` during [start%, end%] of a T-second loop.

    At rest (static fallback / reduced motion) it sits hidden before the path start.
    """
    L = path_length(d)
    pad = width * 3
    hide_a = f"stroke-dashoffset:{dash + pad:.1f}"
    hide_b = f"stroke-dashoffset:{-(L + pad):.1f}"
    cls = anim.add({0: hide_a, start: hide_a, end: hide_b, 100: hide_b}, T, delay)
    da = f"{dash} {L + dash + 2 * pad + 10:.1f}"
    out = ""
    if glow:
        out += (f'<path d="{d}" class="{cls}" fill="none" stroke="{color}" stroke-opacity=".28" '
                f'stroke-width="{width*3.2}" stroke-linecap="round" stroke-dasharray="{da}" '
                f'stroke-dashoffset="{dash + pad:.1f}"/>')
    out += (f'<path d="{d}" class="{cls}" fill="none" stroke="{color}" stroke-width="{width}" '
            f'stroke-linecap="round" stroke-dasharray="{da}" stroke-dashoffset="{dash + pad:.1f}"/>')
    return out


def s_route(x, y, s=1.0, stroke=None, width=3.0, nodes=True) -> tuple[str, str]:
    """The signature mark: an 'S' drawn as a request route.

    Top-right end = a screen (interface). Bottom-left end = a cylinder (data).
    Returns (svg, path_d) so callers can run packets along the same route.
    Designed on a 48x56 grid; (x, y) is the top-left corner, `s` the scale.
    """
    stroke = stroke or C["lav"]

    def p(px, py):
        return f"{x + px*s:.1f} {y + py*s:.1f}"
    d = (f"M{p(38, 10)} C{p(30, 3)} {p(12, 3)} {p(12, 16)} "
         f"C{p(12, 28)} {p(36, 26)} {p(36, 39)} C{p(36, 51)} {p(16, 52)} {p(10, 46)}")
    out = (f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{width}" '
           f'stroke-linecap="round"/>')
    if nodes:
        # screen (top-right)
        out += (f'<rect x="{x+35*s:.1f}" y="{y+3*s:.1f}" width="{12*s:.1f}" height="{9*s:.1f}" '
                f'rx="{2*s:.1f}" fill="{C["bg"]}" stroke="{C["cyan"]}" stroke-width="{max(width*.6,1):.1f}"/>')
        # cylinder (bottom-left)
        cx, cy, rx_, ry_, hh = x + 8*s, y + 46*s, 6*s, 2.4*s, 7*s
        out += (f'<path d="M{cx-rx_:.1f} {cy-hh/2:.1f} V{cy+hh/2:.1f} '
                f'Q{cx:.1f} {cy+hh/2+ry_*2:.1f} {cx+rx_:.1f} {cy+hh/2:.1f} V{cy-hh/2:.1f}" '
                f'fill="{C["bg"]}" stroke="{C["mag"]}" stroke-width="{max(width*.6,1):.1f}"/>'
                f'<ellipse cx="{cx:.1f}" cy="{cy-hh/2:.1f}" rx="{rx_:.1f}" ry="{ry_:.1f}" '
                f'fill="{C["bg"]}" stroke="{C["mag"]}" stroke-width="{max(width*.6,1):.1f}"/>')
    return out, d


def status_glyph(anim: Anim, cx, cy, status: str, r=6.5) -> str:
    """practiced = filled cyan, learning = half-filled lavender (breathing), studied = hollow."""
    if status == "practiced":
        return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{C["cyan"]}"/>'
    if status == "learning":
        pulse = anim.add({0: "opacity:.55;transform:scale(1)", 50: "opacity:0;transform:scale(2.1)",
                          100: "opacity:0;transform:scale(2.1)"}, 3.2)
        return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{C["lav"]}" '
                f'class="{pulse} fb" opacity="0"/>'
                f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{C["lav"]}" stroke-width="2"/>'
                f'<path d="M{cx} {cy-r} A{r} {r} 0 0 0 {cx} {cy+r} Z" fill="{C["lav"]}"/>')
    return (f'<circle cx="{cx}" cy="{cy}" r="{r-1}" fill="none" stroke="{C["muted"]}" '
            f'stroke-width="2"/>')
