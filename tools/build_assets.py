"""Build every SVG in assets/ from profile.json.

    python tools/build_assets.py

Each asset is a function below. They share the tokens and helpers in svgkit.py,
so palette, type and motion stay consistent. Colour semantics used everywhere:
    cyan     = a request / data travelling toward the database
    magenta  = a response travelling back toward the person
    lavender = identity, structure, things in progress
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from svgkit import (C, EASE, Anim, attr, esc, packet, panel, path_length, plate,  # noqa: E402
                    plate_defs, s_route, status_glyph, style_block, svg_open, text,
                    window_dots, wire)
import activity  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"


def reverse_s(d: str) -> str:
    """Reverse an 'M p0 C a b p1 C c d p2 ...' path so packets can run it backwards."""
    import re
    nums = [n for n in re.findall(r"-?\d*\.?\d+", d)]
    pts = [(nums[i], nums[i + 1]) for i in range(0, len(nums), 2)]
    start, segs = pts[0], [pts[i:i + 3] for i in range(1, len(pts), 3)]
    anchors = [start] + [s[2] for s in segs]
    out = f"M{anchors[-1][0]} {anchors[-1][1]}"
    for k in range(len(segs) - 1, -1, -1):
        a, b, _ = segs[k]
        p = anchors[k]
        out += f" C{b[0]} {b[1]} {a[0]} {a[1]} {p[0]} {p[1]}"
    return out


def particles(anim: Anim, pts, color=None) -> str:
    """Slow ambient dust. Static fallback: faint dots."""
    color = color or C["lav"]
    out = ""
    for i, (x, y, r, dur) in enumerate(pts):
        cls = anim.add({0: "opacity:0;transform:translateY(0)", 30: "opacity:.7",
                        100: "opacity:0;transform:translateY(-26px)"}, dur, delay=-(i * 1.3) % dur,
                       timing="linear")
        out += f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}" opacity=".35" class="{cls}"/>'
    return out


def code_line(x, y, tokens, size=13) -> str:
    spans = "".join(f'<tspan fill="{C[c]}">{esc(t)}</tspan>' for t, c in tokens)
    return f'<text x="{x}" y="{y}" class="mono" font-size="{size}" xml:space="preserve">{spans}</text>'


def crow(x, y, dx, dy, kind, color=None) -> str:
    """Crow's-foot end at (x, y). (dx, dy) = unit vector pointing INTO the table."""
    color = color or C["mid"]
    px, py = -dy, dx  # perpendicular
    if kind == "many":
        bx, by = x - dx * 12, y - dy * 12
        return "".join(f'<line x1="{bx}" y1="{by}" x2="{x + px*k*7}" y2="{y + py*k*7}" '
                       f'stroke="{color}" stroke-width="1.6"/>' for k in (-1, 0, 1))
    tx, ty = x - dx * 8, y - dy * 8
    return (f'<line x1="{tx + px*7}" y1="{ty + py*7}" x2="{tx - px*7}" y2="{ty - py*7}" '
            f'stroke="{color}" stroke-width="1.6"/>')


def write(name: str, svg: str) -> None:
    (OUT / name).write_text(svg, encoding="utf-8")
    print(f"  {name:28s} {len(svg.encode()) / 1024:6.1f} KB")


# =========================================================================== #
# 1. HERO
# =========================================================================== #
def hero(cfg) -> str:
    W, H = 1200, 540
    a = Anim()
    T, D = 9.0, 2.6  # loop length, loop start (after the intro)

    first, last = cfg["first_name"], cfg["last_name"]
    longest = max(len(first), len(last))
    name_size = min(88, int(520 / (longest * .6)))

    # --- left column ---------------------------------------------------------
    mono_s, _ = s_route(72, 50, .78, stroke=C["lav"], width=3)
    prompt = f"~/{cfg['handle']} $ whoami"
    pw = len(prompt) * 10  # forced with textLength so the caret lands exactly
    typing = a.add({0: "transform:scaleX(0)", 100: "transform:scaleX(1)"}, 1.1, .3, loop=False,
                   timing=f"steps({len(prompt)},end)")
    caret = a.add({0: "opacity:1", 49: "opacity:1", 50: "opacity:0", 100: "opacity:0"}, 1.1,
                  timing="linear")

    left = f"""
<g class="{a.fade_in(.1)}">{mono_s}</g>
<clipPath id="typed"><rect x="122" y="60" width="{pw + 4}" height="30" class="{typing}" style="transform-origin:122px 0"/></clipPath>
<text x="122" y="81" class="mono" font-size="17" fill="{C['muted']}" textLength="{pw}" lengthAdjust="spacing" clip-path="url(#typed)">{esc(prompt)}</text>
<rect x="{122 + pw + 6}" y="66" width="9" height="19" rx="1.5" fill="{C['cyan']}" class="{caret}"/>
<g class="{a.fade_up(.6)}"><text x="68" y="196" class="sans b" font-size="{name_size}" fill="url(#nameGrad)" letter-spacing="-1.5">{esc(first)}</text></g>
<g class="{a.fade_up(.75)}"><text x="68" y="{196 + name_size - 2}" class="sans b" font-size="{name_size}" fill="url(#nameGrad)" letter-spacing="-1.5">{esc(last)}</text></g>
<g class="{a.fade_up(1.0)}">{text(72, 338, cfg['title'], 25, C['soft'], 'sans sb')}</g>
<g class="{a.fade_up(1.2)}"><text x="72" y="400" class="sans b" font-size="32" fill="url(#tagGrad)">{esc(cfg['tagline'])}</text></g>
<g class="{a.fade_up(1.35)}">{text(72, 436, cfg['subline'], 20, C['muted'])}</g>
"""
    # interface -> logic -> data chips; the packet slips *behind* the logic chip
    chips = [("interface", 72, 108), ("logic", 214, 78), ("data", 326, 70)]
    chip_wire = "M180 486 L326 486"
    chip_svg = wire(chip_wire, C["line"], 1.5)
    chip_svg += packet(a, chip_wire, C["cyan"], 4.5, 5, 45, dash=10, width=3, delay=D)
    chip_svg += packet(a, "M326 486 L180 486", C["mag"], 4.5, 55, 95, dash=10, width=3, delay=D)
    for label, x, w in chips:
        chip_svg += (f'<rect x="{x}" y="472" width="{w}" height="28" rx="14" fill="{C["panel"]}" '
                     f'stroke="{C["line"]}"/>' + text(x + w / 2, 491, label, 14, C['soft'], 'mono', 'middle'))
    left += f'<g class="{a.fade_up(1.5)}">{chip_svg}</g>'

    # --- right column: the workshop -----------------------------------------
    UI, CODE, DB = (780, 40, 372, 160), (636, 224, 372, 136), (780, 384, 372, 124)

    # Wires: request (cyan) runs UI -> code -> DB, response (magenta) DB -> code -> UI.
    w1 = "M780 120 C720 120 700 150 700 224"
    w2 = "M1008 292 C1068 292 1088 322 1088 384"
    w3 = "M780 446 C720 446 700 416 700 360"
    w4 = "M1008 250 C1068 250 1088 236 1088 200"
    wires = "".join(wire(w, C["line"], 1.6) for w in (w1, w2, w3, w4))
    wires += text(690, 172, "GET /students", 12, C["dim"], "mono", "end")
    wires += text(1100, 344, "SELECT", 12, C["dim"], "mono")
    wires += text(690, 410, "rows", 12, C["dim"], "mono", "end")
    wires += text(1100, 230, "200 OK", 12, C["dim"], "mono")
    pk = (packet(a, w1, C["cyan"], T, 8, 22, delay=D) + packet(a, w2, C["cyan"], T, 34, 46, delay=D)
          + packet(a, w3, C["mag"], T, 58, 70, delay=D) + packet(a, w4, C["mag"], T, 74, 86, delay=D))

    # UI panel
    x, y, w, h = UI
    ripple = a.add({0: "opacity:.6;transform:scale(.2)", 8: "opacity:0;transform:scale(2.4)",
                    100: "opacity:0;transform:scale(2.4)"}, T, D)
    rows = ""
    for i, col in enumerate((C["lav"], C["cyan"], C["mag"])):
        ry = y + 76 + i * 26
        flash = a.window(T, 88 + i * 2, 94 + i * 2, "opacity:0", "opacity:1", ramp=1.5, delay=D)
        rows += f"""<g class="{a.fade_up(1.7 + i * .12, .7, 8)}">
  <rect x="{x+14}" y="{ry-2}" width="{w-28}" height="22" rx="6" fill="{C['cyan']}" fill-opacity=".14" opacity="0" class="{flash}"/>
  <circle cx="{x+28}" cy="{ry+9}" r="7" fill="{col}" fill-opacity=".75"/>
  <rect x="{x+44}" y="{ry+5}" width="{120 - i*18}" height="8" rx="4" fill="{C['soft']}" fill-opacity=".55"/>
  <rect x="{x+176}" y="{ry+5}" width="{70 + i*12}" height="8" rx="4" fill="{C['muted']}" fill-opacity=".35"/>
  <rect x="{x+w-74}" y="{ry+2}" width="52" height="14" rx="7" fill="none" stroke="{C['line']}"/>
</g>"""
    ui = f"""<g class="{a.fade_up(.9, 1, 18)}">
{panel(x, y, w, h)}
{window_dots(x+18, y+20)}
<rect x="{x+70}" y="{y+10}" width="210" height="20" rx="10" fill="{C['bg']}" fill-opacity=".7"/>
{text(x+84, y+24, 'localhost:5173/students', 11, C['muted'], 'mono')}
{text(x+18, y+60, 'Students', 15, C['text'], 'sans b')}
<rect x="{x+w-74}" y="{y+44}" width="56" height="24" rx="12" fill="{C['blue']}"/>
{text(x+w-46, y+60, 'Load', 12, '#fff', 'sans sb', 'middle')}
<circle cx="{x+w-46}" cy="{y+56}" r="14" fill="none" stroke="{C['cyan']}" stroke-width="2" opacity="0" class="{ripple} fb"/>
{rows}
</g>"""

    # Code panel: a real FastAPI + SQLAlchemy handler
    x, y, w, h = CODE
    lines = [
        [("@router", "lav"), (".get(", "soft"), ('"/students"', "cyan"), (")", "soft")],
        [("def ", "mag"), ("list_students", "text"), ("(db: ", "soft"), ("Session", "blue"), ("):", "soft")],
        [("    query = ", "soft"), ("select", "lav"), ("(", "soft"), ("Student", "blue"), (")", "soft")],
        [("    return ", "mag"), ("db.scalars(query).all()", "soft")],
    ]
    hl_windows = {0: (22, 30, "cyan"), 2: (29, 36, "cyan"), 3: (70, 77, "mag")}
    code = ""
    for i, toks in enumerate(lines):
        ly = y + 60 + i * 20
        if i in hl_windows:
            on, off, col = hl_windows[i]
            hl = a.window(T, on, off, "opacity:0", "opacity:1", ramp=1.5, delay=D)
            code += (f'<rect x="{x+10}" y="{ly-14}" width="{w-20}" height="19" rx="4" fill="{C[col]}" '
                     f'fill-opacity=".13" opacity="0" class="{hl}"/>')
        code += f'<g class="{a.fade_up(1.5 + i * .14, .6, 0)}">'
        code += text(x + 22, ly, str(i + 1), 12, C["dim"], "mono", "end")
        code += code_line(x + 34, ly, toks) + "</g>"
    codep = f"""<g class="{a.fade_up(1.1, 1, 18)}">
{panel(x, y, w, h, fill=C['bg2'])}
{window_dots(x+18, y+18)}
{text(x+70, y+22, 'api/students.py', 12, C['muted'], 'mono')}
<line x1="{x}" y1="{y+34}" x2="{x+w}" y2="{y+34}" stroke="{C['line']}"/>
{code}
</g>"""

    # DB panel
    x, y, w, h = DB
    db_rows = ""
    for i, (rid, nm, mj) in enumerate((("1", "'Lina'", "2"), ("2", "'Omar'", "1"), ("3", "'Maya'", "2"))):
        ry = y + 66 + i * 21
        scan = a.window(T, 47 + i * 4, 51 + i * 4, "opacity:0", "opacity:1", ramp=1, delay=D)
        db_rows += (f'<rect x="{x+10}" y="{ry-14}" width="{w-20}" height="19" rx="4" fill="{C["cyan"]}" '
                    f'fill-opacity=".14" opacity="0" class="{scan}"/>'
                    + text(x + 22, ry, rid, 12, C["soft"], "mono")
                    + text(x + 72, ry, nm, 12, C["soft"], "mono")
                    + text(x + 210, ry, mj, 12, C["soft"], "mono"))
    dbp = f"""<g class="{a.fade_up(1.3, 1, 18)}">
{panel(x, y, w, h)}
<g fill="none" stroke="{C['lav']}" stroke-width="1.4"><rect x="{x+18}" y="{y+12}" width="16" height="13" rx="2"/><line x1="{x+18}" y1="{y+17}" x2="{x+34}" y2="{y+17}"/><line x1="{x+26}" y1="{y+17}" x2="{x+26}" y2="{y+25}"/></g>
{text(x+44, y+24, 'students', 13, C['lav'], 'mono b')}
{text(x+w-18, y+24, '3 rows', 11, C['dim'], 'mono', 'end')}
<rect x="{x+10}" y="{y+32}" width="{w-20}" height="20" rx="4" fill="{C['panel2']}"/>
{text(x+22, y+46, 'id PK', 11, C['muted'], 'mono')}
{text(x+72, y+46, 'name', 11, C['muted'], 'mono')}
{text(x+210, y+46, 'major_id FK', 11, C['muted'], 'mono')}
{db_rows}
</g>"""

    glow = a.add({0: "opacity:.55", 50: "opacity:1", 100: "opacity:.55"}, 10, timing="ease-in-out")
    dust = particles(a, [(620, 470, 1.6, 9), (560, 120, 1.2, 11), (1170, 330, 1.4, 8),
                         (470, 300, 1.1, 10), (740, 512, 1.3, 12), (1010, 30, 1.2, 9),
                         (400, 64, 1.5, 11)])

    defs = f"""<defs>
{plate_defs()}
<linearGradient id="nameGrad" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="#F6F4FF"/><stop offset=".55" stop-color="{C['lav']}"/><stop offset="1" stop-color="#8FA2FF"/>
</linearGradient>
<linearGradient id="tagGrad" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{C['cyan']}"/><stop offset="1" stop-color="{C['lav']}"/>
</linearGradient>
<radialGradient id="work" cx=".5" cy=".5" r=".5">
  <stop offset="0" stop-color="{C['blue']}" stop-opacity=".22"/><stop offset="1" stop-color="{C['blue']}" stop-opacity="0"/>
</radialGradient>
</defs>"""

    desc = (f"{cfg['name']}, {cfg['title']}. {cfg['tagline']} {cfg['subline']} "
            "An animated workspace: clicking Load in a small web page sends a request through "
            "a FastAPI handler to a students table, and the response flows back to update the page.")
    return (svg_open(W, H, f"{cfg['name']} — {cfg['title']}", desc) + defs + style_block(a)
            + plate(W, H)
            + f'<ellipse cx="900" cy="280" rx="330" ry="250" fill="url(#work)" class="{glow}"/>'
            + dust + left
            + "<!-- workshop: interface (top), logic (middle), data (bottom) -->"
            + wires + ui + codep + dbp + pk + "</svg>\n")


# =========================================================================== #
# 2. DIVIDER — the S-route on a hairline (transparent; reads on light + dark)
# =========================================================================== #
def divider(cfg) -> str:
    W, H = 1200, 44
    a = Anim()
    T = 7.0
    mark, d = s_route(588, 8, .5, stroke=C["mid"], width=2.2)
    up = reverse_s(d)  # bottom-left (data) -> top-right (screen)
    left, right = "M60 22 L589 22", "M612 22 L1140 22"
    body = f"""<defs><linearGradient id="hl" x1="0" y1="0" x2="1" y2="0">
<stop offset="0" stop-color="{C['mid']}" stop-opacity="0"/><stop offset=".5" stop-color="{C['mid']}" stop-opacity=".9"/><stop offset="1" stop-color="{C['mid']}" stop-opacity="0"/>
</linearGradient></defs>
<!-- thin rects, not <line>: a bounding-box gradient on a zero-height line does not render -->
<rect x="20" y="21.4" width="558" height="1.2" fill="url(#hl)"/>
<rect x="622" y="21.4" width="558" height="1.2" fill="url(#hl)"/>
{mark}
{packet(a, left, C['blue'], T, 2, 40, dash=22, width=2.5)}
{packet(a, up, C['blue'], T, 40, 52, dash=8, width=2.5, glow=False)}
{packet(a, right, C['mag'], T, 52, 92, dash=22, width=2.5)}"""
    return (svg_open(W, H, "Section divider", "A thin line with the S-route mark at its centre.")
            + style_block(a) + body + "</svg>\n")


# =========================================================================== #
# 3. STACK AS A SCHEMA
# =========================================================================== #
STATUS_COLOR = {"practiced": C["cyan"], "learning": C["lav"], "studied": C["muted"]}


def table(a: Anim, x, y, name, rows, delay, w=340) -> tuple[str, int]:
    hh, rh = 46, 32
    h = hh + len(rows) * rh + 14
    out = f'<g class="{a.fade_up(delay, .9, 16)}">' + panel(x, y, w, h, rx=12)
    out += (f'<rect x="{x+1}" y="{y+1}" width="{w-2}" height="{hh-1}" rx="11" fill="{C["panel2"]}"/>'
            f'<rect x="{x+1}" y="{y+hh-14}" width="{w-2}" height="14" fill="{C["panel2"]}"/>'
            f'<line x1="{x}" y1="{y+hh}" x2="{x+w}" y2="{y+hh}" stroke="{C["line"]}"/>')
    out += (f'<g fill="none" stroke="{C["lav"]}" stroke-width="1.4"><rect x="{x+18}" y="{y+16}" '
            f'width="16" height="14" rx="2"/><line x1="{x+18}" y1="{y+21}" x2="{x+34}" y2="{y+21}"/>'
            f'<line x1="{x+26}" y1="{y+21}" x2="{x+26}" y2="{y+30}"/></g>')
    out += text(x + 44, y + 29, name, 17, C["lav"], "mono b")
    out += text(x + w - 18, y + 29, f"({len(rows)})", 13, C["dim"], "mono", "end")
    for i, (label, status) in enumerate(rows):
        ry = y + hh + 8 + i * rh
        if i:
            out += (f'<line x1="{x+16}" y1="{ry}" x2="{x+w-16}" y2="{ry}" stroke="{C["line"]}" '
                    f'stroke-opacity=".55"/>')
        out += status_glyph(a, x + 28, ry + 16, status)
        out += text(x + 46, ry + 21.5, label, 16.5, C["text"])
        out += text(x + w - 18, ry + 21, status, 12.5, STATUS_COLOR[status], "mono", "end")
    return out + "</g>", h


def tech_schema(cfg) -> str:
    W = 1200
    a = Anim()
    st = cfg["stack"]
    X = (40, 430, 820)
    yA = 128
    hA = {k: 46 + len(st[k]) * 32 + 14 for k in ("frontend", "backend", "data")}
    yB = yA + max(hA.values()) + 64

    body = ""
    t, h_front = table(a, X[0], yA, "frontend", st["frontend"], .2)
    body += t
    t, h_back = table(a, X[1], yA, "backend", st["backend"], .35)
    body += t
    t, h_data = table(a, X[2], yA, "data", st["data"], .5)
    body += t
    t, h_fund = table(a, X[0], yB, "fundamentals", st["fundamentals"], .65)
    body += t
    t, h_erp = table(a, X[2], yB, "erp", st["erp"], .95)
    body += t

    # Hub: the engineer row that every skill table hangs off. (Easter egg: the constraints.)
    hub_rows = [("name", f"'{cfg['name']}'"), ("role", "'IT Engineer'"),
                ("focus", "'software development'"), ("curiosity", "NOT NULL"),
                ("growth", "AUTO_INCREMENT")]
    hx, hw, hh = X[1], 340, 46 + len(hub_rows) * 32 + 14
    hub = f'<g class="{a.fade_up(.8, .9, 16)}">'
    hub += panel(hx, yB, hw, hh, rx=12, stroke=C["lav"])
    hub += (f'<rect x="{hx+1}" y="{yB+1}" width="{hw-2}" height="45" rx="11" fill="url(#hubGrad)"/>'
            f'<line x1="{hx}" y1="{yB+46}" x2="{hx+hw}" y2="{yB+46}" stroke="{C["lav"]}" stroke-opacity=".5"/>')
    hub += (f'<g fill="none" stroke="{C["text"]}" stroke-width="1.5"><circle cx="{hx+24}" cy="{yB+23}" r="5"/>'
            f'<path d="M{hx+29} {yB+23} H{hx+40} M{hx+36} {yB+23} V{yB+28}"/></g>')
    hub += text(hx + 50, yB + 29, "engineer", 17, C["text"], "mono b")
    hub += text(hx + hw - 18, yB + 29, "(1)", 13, C["soft"], "mono", "end")
    for i, (k, v) in enumerate(hub_rows):
        ry = yB + 54 + i * 32
        if i:
            hub += (f'<line x1="{hx+16}" y1="{ry}" x2="{hx+hw-16}" y2="{ry}" stroke="{C["line"]}" '
                    f'stroke-opacity=".55"/>')
        hub += text(hx + 22, ry + 21, k, 14.5, C["soft"], "mono")
        hub += text(hx + hw - 18, ry + 21, v, 14.5, C["cyan"] if v.isupper() else C["lav"], "mono",
                    "end")
    body += hub + "</g>"

    # Tools: a wide, single-row table
    yT = yB + max(h_fund, hh, h_erp) + 48
    tools = st["tools"]
    tw = 1120
    cell = tw / len(tools)
    tl = f'<g class="{a.fade_up(1.1, .9, 16)}">' + panel(40, yT, tw, 100, rx=12)
    tl += (f'<rect x="41" y="{yT+1}" width="{tw-2}" height="41" rx="11" fill="{C["panel2"]}"/>'
           f'<rect x="41" y="{yT+28}" width="{tw-2}" height="14" fill="{C["panel2"]}"/>'
           f'<line x1="40" y1="{yT+42}" x2="{40+tw}" y2="{yT+42}" stroke="{C["line"]}"/>')
    tl += (f'<g fill="none" stroke="{C["lav"]}" stroke-width="1.4"><rect x="58" y="{yT+14}" width="16" '
           f'height="14" rx="2"/><line x1="58" y1="{yT+19}" x2="74" y2="{yT+19}"/><line x1="66" '
           f'y1="{yT+19}" x2="66" y2="{yT+28}"/></g>')
    tl += text(84, yT + 27, "tools", 17, C["lav"], "mono b")
    tl += text(40 + tw - 18, yT + 27, f"({len(tools)})", 13, C["dim"], "mono", "end")
    for i, (label, status) in enumerate(tools):
        cx = 40 + i * cell
        if i:
            tl += (f'<line x1="{cx}" y1="{yT+54}" x2="{cx}" y2="{yT+88}" stroke="{C["line"]}" '
                   f'stroke-opacity=".55"/>')
        tl += status_glyph(a, cx + 26, yT + 71, status)
        tl += text(cx + 42, yT + 77, label, 16.5, C["text"])
    body += tl + "</g>"

    # Relationships (crow's foot). (path, end-a, end-b, label, label-pos)
    xb_f, xb_b, xb_d = X[0] + 340, X[1] + 340, X[2] + 340
    rel = [
        (f"M{xb_f} {yA+80} L{X[1]} {yA+80}", ((xb_f, yA+80, -1, 0, "many"), (X[1], yA+80, 1, 0, "one")),
         "calls", (405, yA + 64, "middle")),
        (f"M{xb_b} {yA+80} L{X[2]} {yA+80}", ((xb_b, yA+80, -1, 0, "one"), (X[2], yA+80, 1, 0, "many")),
         "queries", (795, yA + 64, "middle")),
        (f"M990 {yA+h_data} L990 {yB}", ((990, yA+h_data, 0, -1, "many"), (990, yB, 0, 1, "many")),
         "maps (ORM)", (1000, (yA + h_data + yB) / 2 + 4, "start")),
        (f"M210 {yA+h_front} L210 {yB}", ((210, yA+h_front, 0, -1, "many"), (210, yB, 0, 1, "one")),
         "underpins", (220, (yA + h_front + yB) / 2 + 4, "start")),
        (f"M600 {yA+h_back} L600 {yB}", ((600, yA+h_back, 0, -1, "many"), (600, yB, 0, 1, "one")),
         "builds", (610, (yA + h_back + yB) / 2 + 4, "start")),
        (f"M{xb_f} {yB+80} L{X[1]} {yB+80}", ((xb_f, yB+80, -1, 0, "many"), (X[1], yB+80, 1, 0, "one")),
         "knows", (405, yB + 64, "middle")),
        (f"M{X[2]} {yB+80} L{xb_b} {yB+80}", ((X[2], yB+80, 1, 0, "many"), (xb_b, yB+80, -1, 0, "one")),
         "explores", (795, yB + 64, "middle")),
        (f"M600 {yB+hh} L600 {yT}", ((600, yB+hh, 0, -1, "one"), (600, yT, 0, 1, "many")),
         "uses", (610, (yB + hh + yT) / 2 + 4, "start")),
    ]
    T = 12.0
    rels, pk = "", ""
    for i, (d, ends, label, (lx, ly, anc)) in enumerate(rel):
        L = path_length(d)
        rels += (f'<path d="{d}" stroke="{C["mid"]}" stroke-width="1.6" fill="none" '
                 f'stroke-dasharray="{L:.1f}" class="{a.draw(L, 1.3 + i * .08, .7)}"/>')
        rels += "".join(crow(*e) for e in ends)
        rels += text(lx, ly, label, 11.5, C["dim"], "mono", anc)
        pk += packet(a, d, C["cyan"] if i % 2 == 0 else C["lav"], T, 4 + i * 11, 4 + i * 11 + 9,
                     dash=10, width=3, delay=2.2)

    H = yT + 100 + 70
    legend = ""
    for i, (s, word) in enumerate((("practiced", "practiced"), ("learning", "learning"),
                                   ("studied", "studied"))):
        lx = 832 + i * 116
        legend += status_glyph(a, lx, 86, s) + text(lx + 14, 91, word, 14, C["soft"], "mono")
    head = (text(40, 62, f"-- {cfg['handle']}.stack  ·  status ENUM('practiced','learning','studied')",
                 14, C["dim"], "mono")
            + text(40, 96, "The stack, modelled as a schema", 26, C["text"], "sans b") + legend)
    note = text(600, H - 30, "Status describes hands-on exposure, not expertise: practiced = used in "
                "coursework or projects · learning = actively learning now · studied = covered in theory.",
                14, C["muted"], "sans", "middle")

    defs = f"""<defs>{plate_defs()}
<linearGradient id="hubGrad" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{C['lav']}" stop-opacity=".45"/><stop offset="1" stop-color="{C['blue']}" stop-opacity=".35"/></linearGradient>
</defs>"""
    desc = "Skills drawn as an entity-relationship diagram. " + " ".join(
        f"{k}: " + ", ".join(f"{n} ({s})" for n, s in v) + "." for k, v in st.items())
    return (svg_open(W, H, "Technology stack as a database schema", desc) + defs + style_block(a)
            + plate(W, H) + head + rels + body + pk + note + "</svg>\n")


# =========================================================================== #
# 4. ROUND TRIP — three worlds, one request
# =========================================================================== #
def round_trip(cfg) -> str:
    W, H = 1200, 748
    a = Anim()
    T = 12.0
    step = 100 / 6
    PY, PH = 130, 418
    FX, BX, DX, PW = 30, 430, 830, 340

    def world(x, idx, label, title, sub, accent):
        return (f'<g class="{a.fade_up(.2 + idx * .2, 1, 18)}">' + panel(x, PY, PW, PH, rx=18)
                + text(x + 24, PY + 34, f"0{idx+1} · {label}", 12, accent, "mono b", extra='letter-spacing="2"')
                + text(x + 24, PY + 62, title, 22, C["text"], "sans b")
                + text(x + 24, PY + 84, sub, 14, C["muted"]) + "</g>")

    worlds = (world(FX, 0, "FRONTEND", "Interface", "components · layouts · state", C["cyan"])
              + world(BX, 1, "BACKEND", "Logic", "routes · auth · validation · rules", C["lav"])
              + world(DX, 2, "DATABASE", "Data", "tables · relations · constraints · queries", C["mag"]))

    # ---- Frontend: a page that goes from skeleton to real rows -------------
    x0 = FX
    bx, by = x0 + 18, 234
    fe = (f'<rect x="{bx}" y="{by}" width="304" height="282" rx="10" fill="{C["bg"]}" fill-opacity=".65" '
          f'stroke="{C["line"]}"/>' + window_dots(bx + 16, by + 16)
          + text(bx + 64, by + 20, "app / students", 11, C["dim"], "mono"))
    # faint design grid: the layout is built on columns
    fe += "".join(f'<rect x="{bx + 16 + i*46}" y="{by+32}" width="38" height="240" fill="{C["blue"]}" '
                  f'fill-opacity=".045"/>' for i in range(6))
    fe += (f'<rect x="{bx+16}" y="{by+42}" width="150" height="28" rx="8" fill="{C["panel2"]}" stroke="{C["line"]}"/>'
           + text(bx + 28, by + 61, "major: IT  ▾", 12, C["soft"], "mono")
           + f'<rect x="{bx+216}" y="{by+42}" width="72" height="28" rx="14" fill="{C["blue"]}"/>'
           + text(bx + 252, by + 61, "Load", 13, "#fff", "sans b", "middle"))
    ripple = a.add({0: "opacity:0;transform:scale(.3)", 2: "opacity:.7;transform:scale(.3)",
                    11: "opacity:0;transform:scale(2.6)", 100: "opacity:0;transform:scale(2.6)"}, T)
    fe += (f'<circle cx="{bx+252}" cy="{by+56}" r="16" fill="none" stroke="{C["cyan"]}" stroke-width="2" '
           f'opacity="0" class="{ripple} fb"/>')
    names = ("Lina H.", "Maya S.", "Yousef A.", "Rana M.")
    for i, nm in enumerate(names):
        ry = by + 86 + i * 44
        sk = a.add({0: "opacity:1", 84 + i*1.5: "opacity:1", 87 + i*1.5: "opacity:0", 98: "opacity:0",
                    100: "opacity:1"}, T)
        rl = a.add({0: "opacity:0;transform:translateX(-8px)", 84 + i*1.5: "opacity:0;transform:translateX(-8px)",
                    87.5 + i*1.5: "opacity:1;transform:translateX(0)", 98: "opacity:1;transform:translateX(0)",
                    100: "opacity:0;transform:translateX(-8px)"}, T)
        fe += f'<rect x="{bx+16}" y="{ry}" width="272" height="36" rx="8" fill="{C["panel2"]}"/>'
        fe += (f'<g opacity="0" class="{sk}"><circle cx="{bx+36}" cy="{ry+18}" r="9" fill="{C["line"]}"/>'
               f'<rect x="{bx+54}" y="{ry+14}" width="{110 - i*10}" height="8" rx="4" fill="{C["line"]}"/>'
               f'<rect x="{bx+236}" y="{ry+11}" width="38" height="14" rx="7" fill="{C["line"]}"/></g>')
        fe += (f'<g class="{rl}"><circle cx="{bx+36}" cy="{ry+18}" r="9" fill="{(C["lav"], C["cyan"], C["mag"], C["blue"])[i]}" fill-opacity=".8"/>'
               + text(bx + 54, ry + 23, nm, 14, C["text"])
               + f'<rect x="{bx+236}" y="{ry+11}" width="38" height="14" rx="7" fill="none" stroke="{C["cyan"]}" stroke-opacity=".7"/>'
               + text(bx + 255, ry + 22, "IT", 10, C["cyan"], "mono", "middle") + "</g>")

    # ---- Backend: a pipeline of gates -------------------------------------
    x0 = BX
    gates = [("router", "GET /api/students"), ("auth", "verify JWT · role: viewer"),
             ("validate", "major ∈ {IT, CS, …}"), ("service", "apply business rules")]
    be = ""
    spine_x = x0 + 300
    for i, (g, detail) in enumerate(gates):
        gy = 238 + i * 64
        lit = a.window(T, 36 + i * 3.5, 48 + i * 3.5, "opacity:0", "opacity:1", ramp=1, delay=0)
        chk = a.add({0: "opacity:0", 35 + i*3.5: "opacity:0", 36.5 + i*3.5: "opacity:1",
                     96: "opacity:1", 98: "opacity:0", 100: "opacity:0"}, T)
        be += (f'<rect x="{x0+18}" y="{gy}" width="304" height="50" rx="10" fill="{C["panel2"]}" stroke="{C["line"]}"/>'
               f'<rect x="{x0+18}" y="{gy}" width="304" height="50" rx="10" fill="none" stroke="{C["cyan"]}" '
               f'stroke-opacity=".8" opacity="0" class="{lit}"/>'
               + text(x0 + 36, gy + 22, g, 14, C["lav"], "mono b")
               + text(x0 + 36, gy + 40, detail, 12, C["muted"], "mono")
               + f'<circle cx="{spine_x}" cy="{gy+25}" r="10" fill="{C["bg"]}" stroke="{C["line"]}"/>'
               + f'<path d="M{spine_x-4.5} {gy+25} l3 3.2 l6 -6.6" fill="none" stroke="{C["cyan"]}" '
                 f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="{chk}"/>')
    be += text(x0 + 36, 514, "→ serialize → 200 OK", 12, C["dim"], "mono")
    spine = f"M{spine_x} 263 L{spine_x} 455"

    # ---- Database: two related tables + the query --------------------------
    x0 = DX
    db = ""
    sx, sy, sw = x0 + 16, 234, 188
    mx, my, mw = x0 + 226, 234, 98
    db += (f'<rect x="{sx}" y="{sy}" width="{sw}" height="150" rx="8" fill="{C["bg"]}" fill-opacity=".6" stroke="{C["line"]}"/>'
           + f'<rect x="{sx}" y="{sy}" width="{sw}" height="26" rx="8" fill="{C["panel2"]}"/>'
           + text(sx + 12, sy + 18, "students", 12, C["lav"], "mono b")
           + text(sx + 12, sy + 44, "id", 10.5, C["dim"], "mono") + text(sx + 40, sy + 44, "name", 10.5, C["dim"], "mono")
           + text(sx + sw - 10, sy + 44, "major_id", 10.5, C["dim"], "mono", "end"))
    srows = (("1", "Lina H.", "2"), ("2", "Omar K.", "1"), ("3", "Maya S.", "2"), ("4", "Yousef A.", "2"))
    for i, (rid, nm, mj) in enumerate(srows):
        ry = sy + 66 + i * 21
        if mj == "2":
            hit = a.window(T, 57 + i * 2, 68, "opacity:0", "opacity:1", ramp=1)
            db += (f'<rect x="{sx+4}" y="{ry-14}" width="{sw-8}" height="19" rx="4" fill="{C["cyan"]}" '
                   f'fill-opacity=".16" opacity="0" class="{hit}"/>')
        db += (text(sx + 12, ry, rid, 12, C["soft"], "mono") + text(sx + 40, ry, nm, 12, C["soft"], "mono")
               + text(sx + sw - 14, ry, mj, 12, C["soft"], "mono", "end"))
    db += (f'<rect x="{mx}" y="{my}" width="{mw}" height="98" rx="8" fill="{C["bg"]}" fill-opacity=".6" stroke="{C["line"]}"/>'
           + f'<rect x="{mx}" y="{my}" width="{mw}" height="26" rx="8" fill="{C["panel2"]}"/>'
           + text(mx + 12, my + 18, "majors", 12, C["lav"], "mono b")
           + text(mx + 12, my + 44, "id", 10.5, C["dim"], "mono") + text(mx + 40, my + 44, "code", 10.5, C["dim"], "mono"))
    for i, (rid, code) in enumerate((("1", "CS"), ("2", "IT"))):
        ry = my + 66 + i * 21
        if code == "IT":
            hit = a.window(T, 56, 68, "opacity:0", "opacity:1", ramp=1)
            db += (f'<rect x="{mx+4}" y="{ry-14}" width="{mw-8}" height="19" rx="4" fill="{C["mag"]}" '
                   f'fill-opacity=".18" opacity="0" class="{hit}"/>')
        db += text(mx + 12, ry, rid, 12, C["soft"], "mono") + text(mx + 40, ry, code, 12, C["soft"], "mono")
    # many students -> one major
    rel = f"M{sx+sw} {sy+60} C{sx+sw+12} {sy+60} {mx-12} {my+81} {mx} {my+81}"
    db += wire(rel, C["mid"], 1.5) + crow(sx + sw, sy + 60, -1, 0, "many") + crow(mx, my + 81, 1, 0, "one")
    db += f'<path d="{rel}" fill="none" stroke="{C["mag"]}" stroke-width="2" opacity="0" class="{a.window(T, 56, 68, "opacity:0", "opacity:1", ramp=1)}"/>'
    q = [[("SELECT ", "lav"), ("s.name, m.code", "soft")],
         [("FROM ", "lav"), ("students s", "soft")],
         [("JOIN ", "lav"), ("majors m ", "soft"), ("ON ", "lav"), ("m.id = s.major_id", "soft")],
         [("WHERE ", "lav"), ("m.code = ", "soft"), ("'IT'", "cyan"), (";", "soft")]]
    qx, qy = x0 + 16, 400
    qglow = a.window(T, 54, 68, "opacity:0", "opacity:1", ramp=1.5)
    db += (f'<rect x="{qx}" y="{qy}" width="308" height="112" rx="10" fill="{C["bg2"]}" stroke="{C["line"]}"/>'
           f'<rect x="{qx}" y="{qy}" width="308" height="112" rx="10" fill="none" stroke="{C["cyan"]}" '
           f'opacity="0" class="{qglow}"/>')
    db += "".join(code_line(qx + 14, qy + 26 + i * 22, line, 12.5) for i, line in enumerate(q))

    # ---- wires + packets ----------------------------------------------------
    req1 = f"M{FX+18+288} 290 C{FX+PW+40} 290 {BX-20} 263 {BX+18} 263"
    req2 = f"M{BX+322} 455 C{BX+PW+40} 455 {DX-24} 456 {DX+16} 456"
    resp = (f"M{DX+170} {qy+112} L{DX+170} 566 C{DX+170} 580 {DX+150} 584 {DX+130} 584 "
            f"L{FX+190} 584 C{FX+170} 584 {FX+170} 580 {FX+170} 566 L{FX+170} 516")
    wires = (wire(req1, C["line"], 1.8) + wire(req2, C["line"], 1.8) + wire(resp, C["line"], 1.8, dash="2 6")
             + text((FX + PW + BX) / 2, 252, "HTTP", 11, C["dim"], "mono", "middle")
             + text((BX + PW + DX) / 2, 444, "SQL", 11, C["dim"], "mono", "middle")
             + f'<rect x="530" y="573" width="140" height="22" rx="11" fill="{C["bg"]}" stroke="{C["line"]}"/>'
             + text(600, 588, "200 OK · JSON", 11, C["soft"], "mono", "middle"))
    pk = (packet(a, req1, C["cyan"], T, 18, 31) + packet(a, spine, C["cyan"], T, 35, 49, dash=14)
          + packet(a, req2, C["cyan"], T, 50, 57) + packet(a, resp, C["mag"], T, 67, 83, dash=26))

    # ---- stepper + captions -------------------------------------------------
    labels = ("Event", "Request", "Logic", "Query", "Response", "Render")
    caps = ("The user picks a filter and clicks “Load”.",
            "GET /api/students?major=IT  ·  Authorization: Bearer <token>",
            "Route matched → token verified → input validated → rules applied",
            "SELECT … FROM students JOIN majors … WHERE m.code = 'IT'",
            "200 OK  ·  application/json  ·  [ { name: 'Lina H.', … }, … ]",
            "The list re-renders: skeleton rows become real data.")
    sy0 = 646
    xs = [140 + i * 184 for i in range(6)]
    stp = (f'<line x1="{xs[0]}" y1="{sy0}" x2="{xs[-1]}" y2="{sy0}" stroke="{C["line"]}" stroke-width="1.5"/>')
    for i, (lx, lab) in enumerate(zip(xs, labels)):
        col = C["cyan"] if i < 4 else (C["mag"] if i == 4 else C["lav"])
        on = a.window(T, i * step + 1, (i + 1) * step - .5, "opacity:0", "opacity:1", ramp=1)
        stp += (f'<circle cx="{lx}" cy="{sy0}" r="14" fill="{C["bg"]}" stroke="{C["line"]}" stroke-width="1.5"/>'
                f'<circle cx="{lx}" cy="{sy0}" r="14" fill="{col}" fill-opacity=".22" stroke="{col}" '
                f'stroke-width="2" opacity="0" class="{on}"/>'
                + text(lx, sy0 + 4.5, str(i + 1), 12, C["text"], "mono b", "middle")
                + text(lx, sy0 + 36, lab, 14, C["soft"], "sans", "middle"))
    # Static summary: hidden while animating, shown when motion is off or unsupported.
    hide = a.add({0: "opacity:0", 100: "opacity:0"}, T)
    stp += (f'<text x="600" y="718" class="mono {hide}" font-size="15" fill="{C["soft"]}" '
            f'text-anchor="middle">event → request → logic → query → response → render</text>')
    for i, cap in enumerate(caps):
        on = a.window(T, i * step + 1.2, (i + 1) * step - 1, "opacity:0", "opacity:1", ramp=1.2)
        stp += (f'<text x="600" y="718" class="mono {on}" font-size="15" fill="{C["soft"]}" '
                f'text-anchor="middle" opacity="0">{esc(cap)}</text>')

    head = (text(40, 62, "-- one click, three worlds, one round trip", 14, C["dim"], "mono")
            + text(40, 98, "Interface → API → Logic → Query → Response → Interface", 25, C["text"], "sans b"))
    desc = ("Animated architecture diagram. Frontend: the user clicks Load; skeleton rows wait. "
            "Backend: the request passes router, JWT auth, validation and the service layer. "
            "Database: a query joins students to majors and selects IT students. "
            "The JSON response flows back and the list renders real rows.")
    return (svg_open(W, H, "One request through frontend, backend and database", desc)
            + f"<defs>{plate_defs()}</defs>" + style_block(a) + plate(W, H) + head + worlds
            + fe + be + db + wires + pk + stp + "</svg>\n")


# =========================================================================== #
# 5. PROJECT ILLUSTRATIONS (text lives in README; these are the 'product shots')
# =========================================================================== #
def card_frame(a: Anim, slug: str, status: str) -> str:
    W, H = 600, 320
    chip = (f'<rect x="{W-120}" y="18" width="96" height="24" rx="12" fill="none" stroke="{C["lav"]}" '
            f'stroke-dasharray="4 3"/>' + text(W - 72, 34, "blueprint", 12, C["lav"], "mono", "middle")
            if status == "blueprint" else
            f'<rect x="{W-96}" y="18" width="72" height="24" rx="12" fill="{C["cyan"]}" fill-opacity=".16" '
            f'stroke="{C["cyan"]}"/>' + text(W - 60, 34, "live", 12, C["cyan"], "mono b", "middle"))
    return (plate(W, H, rx=20) + text(26, 35, "~/projects/", 13, C["dim"], "mono")
            + text(26 + 11 * 7.9, 35, slug, 13, C["soft"], "mono") + chip
            + f'<line x1="20" y1="56" x2="{W-20}" y2="56" stroke="{C["line"]}"/>')


def proj_student(cfg) -> str:
    a = Anim()
    T = 10.0
    st = cfg["projects"]["student-system"]
    uml = (f'<g class="{a.fade_up(.2)}"><rect x="28" y="74" width="196" height="222" rx="10" fill="{C["panel"]}" stroke="{C["line"]}"/>'
           + text(126, 100, "Student", 16, C["text"], "sans b", "middle")
           + f'<line x1="28" y1="112" x2="224" y2="112" stroke="{C["line"]}"/>'
           + "".join(text(42, 136 + i * 21, f, 12, C["soft"], "mono")
                     for i, f in enumerate(("- id: int", "- name: string", "- email: string", "- year: int")))
           + f'<line x1="28" y1="216" x2="224" y2="216" stroke="{C["line"]}"/>'
           + "".join(text(42, 240 + i * 21, f, 12, C["lav"], "mono")
                     for i, f in enumerate(("+ validate(): bool", "+ save(): void")))
           + "</g>")
    ops = ("Create", "Read", "Update", "Delete")
    lst = f'<g class="{a.fade_up(.4)}"><rect x="244" y="74" width="328" height="222" rx="10" fill="{C["panel"]}" stroke="{C["line"]}"/>'
    for i, op in enumerate(ops):
        cx = 258 + i * 76
        on = a.window(T, i * 25 + 2, i * 25 + 23, "opacity:0", "opacity:1", ramp=1.5)
        lst += (f'<rect x="{cx}" y="88" width="68" height="26" rx="13" fill="{C["panel2"]}" stroke="{C["line"]}"/>'
                f'<rect x="{cx}" y="88" width="68" height="26" rx="13" fill="{C["cyan"]}" fill-opacity=".18" '
                f'stroke="{C["cyan"]}" opacity="0" class="{on}"/>'
                + text(cx + 34, 105, op, 12, C["soft"], "mono", "middle"))
    rows = (("1", "Lina H."), ("2", "Omar K."), ("3", "Maya S."), ("4", "Yousef A."))
    for i, (rid, nm) in enumerate(rows):
        ry = 130 + i * 38
        anim_cls = ""
        if i == 3:   # Create: the new row slides in
            anim_cls = a.add({0: "opacity:0;transform:translateY(8px)", 6: "opacity:0;transform:translateY(8px)",
                              14: "opacity:1;transform:translateY(0)", 100: "opacity:1;transform:translateY(0)"}, T)
        if i == 2:   # Delete: this row fades out
            anim_cls = a.window(T, 82, 96, "opacity:1", "opacity:.12", ramp=3)
        scan = a.window(T, 28 + i * 4, 32 + i * 4, "opacity:0", "opacity:1", ramp=1)
        lst += (f'<g class="{anim_cls}"><rect x="258" y="{ry}" width="300" height="30" rx="7" fill="{C["panel2"]}"/>'
                f'<rect x="258" y="{ry}" width="300" height="30" rx="7" fill="{C["cyan"]}" fill-opacity=".14" '
                f'opacity="0" class="{scan}"/>'
                + text(274, ry + 20, f"#{rid}", 12, C["dim"], "mono"))
        if i == 1:   # Update: the name is corrected in place
            o1 = a.window(T, 55, 98, "opacity:1", "opacity:0", ramp=2)
            o2 = a.window(T, 55, 98, "opacity:0", "opacity:1", ramp=2)
            lst += (f'<text x="312" y="{ry+20}" class="sans {o1}" font-size="14" fill="{C["text"]}" opacity="0">Omar K</text>'
                    f'<text x="312" y="{ry+20}" class="sans {o2}" font-size="14" fill="{C["text"]}">Omar K.</text>'
                    f'<rect x="490" y="{ry+8}" width="54" height="14" rx="7" fill="none" stroke="{C["lav"]}" opacity="0" class="{o2}"/>'
                    + f'<text x="517" y="{ry+18.5}" class="mono {o2}" font-size="9.5" fill="{C["lav"]}" text-anchor="middle" opacity="0">saved</text>')
        else:
            lst += text(312, ry + 20, nm, 14, C["text"])
        lst += "</g>"
    lst += "</g>"
    desc = "Illustration: a Student class diagram beside a list running Create, Read, Update and Delete."
    return (svg_open(600, 320, "Student Management System — illustration", desc)
            + f"<defs>{plate_defs()}</defs>" + style_block(a)
            + card_frame(a, "student-management-system", st) + uml + lst + "</svg>\n")


def proj_odoo(cfg) -> str:
    a = Anim()
    T = 10.0
    st = cfg["projects"]["odoo-module"]
    tree = ["school_mgmt/", "├─ __manifest__.py", "├─ models/", "│  └─ student.py", "├─ views/",
            "│  └─ student_views.xml", "└─ security/", "   └─ ir.model.access.csv"]
    tr = f'<g class="{a.fade_up(.2)}"><rect x="28" y="74" width="214" height="222" rx="10" fill="{C["panel"]}" stroke="{C["line"]}"/>'
    for i, t_ in enumerate(tree):
        col = C["lav"] if t_.endswith("/") else C["soft"]
        tr += f'<text x="42" y="{100 + i*25}" class="mono" font-size="11.5" fill="{col}" xml:space="preserve">{esc(t_)}</text>'
    tr += "</g>"
    stages = ("Draft", "Confirmed", "Done")
    kb = f'<g class="{a.fade_up(.4)}">'
    for i, s in enumerate(stages):
        cx = 258 + i * 106
        kb += (f'<rect x="{cx}" y="74" width="98" height="180" rx="10" fill="{C["panel"]}" stroke="{C["line"]}"/>'
               + text(cx + 12, 96, s, 12, C["muted"], "mono"))
        # one resting record per column (slot 2); the travelling record uses slot 1
        ky = 166
        kb += (f'<rect x="{cx+8}" y="{ky}" width="82" height="44" rx="7" fill="{C["panel2"]}"/>'
               f'<rect x="{cx+16}" y="{ky+12}" width="{48 - i*8}" height="6" rx="3" fill="{C["muted"]}" fill-opacity=".5"/>'
               f'<rect x="{cx+16}" y="{ky+26}" width="30" height="6" rx="3" fill="{C["line"]}"/>')
    move = a.add({0: "transform:translateX(0);opacity:1", 22: "transform:translateX(0);opacity:1",
                  34: "transform:translateX(106px);opacity:1", 56: "transform:translateX(106px);opacity:1",
                  68: "transform:translateX(212px);opacity:1", 90: "transform:translateX(212px);opacity:1",
                  95: "transform:translateX(212px);opacity:0", 96: "transform:translateX(0);opacity:0",
                  100: "transform:translateX(0);opacity:1"}, T)
    kb += (f'<g class="{move}"><rect x="266" y="112" width="82" height="44" rx="7" fill="{C["panel2"]}" stroke="{C["cyan"]}"/>'
           + text(276, 130, "S/0042", 11, C["cyan"], "mono b")
           + f'<rect x="276" y="138" width="40" height="6" rx="3" fill="{C["soft"]}" fill-opacity=".5"/>'
           + f'<circle cx="334" cy="141" r="6" fill="{C["lav"]}" fill-opacity=".8"/></g>')
    # Odoo-style status bar, synced with the card
    for i, s in enumerate(stages):
        cx = 258 + i * 106
        on = a.window(T, (0, 34, 68)[i] + .5, (22, 56, 94)[i], "opacity:0", "opacity:1", ramp=2)
        kb += (f'<path d="M{cx} 266 h90 l8 12 l-8 12 h-90 l8 -12 z" fill="{C["panel2"]}" stroke="{C["line"]}"/>'
               f'<path d="M{cx} 266 h90 l8 12 l-8 12 h-90 l8 -12 z" fill="{C["lav"]}" fill-opacity=".25" '
               f'stroke="{C["lav"]}" opacity="0" class="{on}"/>'
               + text(cx + 52, 282, s, 11, C["soft"], "mono", "middle"))
    kb += "</g>"
    desc = "Illustration: an Odoo module's file tree beside a kanban board where a record moves Draft → Confirmed → Done."
    return (svg_open(600, 320, "Odoo custom module — illustration", desc)
            + f"<defs>{plate_defs()}</defs>" + style_block(a)
            + card_frame(a, "odoo-custom-module", st) + tr + kb + "</svg>\n")


def proj_fullstack(cfg) -> str:
    a = Anim()
    T = 8.0
    st = cfg["projects"]["fullstack-app"]
    layers = (("UI", "HTML · CSS · JavaScript", C["cyan"]), ("API", "FastAPI · REST · JWT", C["lav"]),
              ("DB", "PostgreSQL", C["mag"]))
    body = ""
    for i, (tag, detail, col) in enumerate(layers):
        ly = 80 + i * 72
        lit = a.window(T, 8 + i * 12, 16 + i * 12, "opacity:0", "opacity:1", ramp=2)
        lit2 = a.window(T, 82 - i * 12, 90 - i * 12, "opacity:0", "opacity:1", ramp=2)
        body += (f'<g class="{a.fade_up(.2 + i*.15)}"><rect x="{40 + i*8}" y="{ly}" width="300" height="56" rx="12" '
                 f'fill="{C["panel"]}" stroke="{C["line"]}"/>'
                 f'<rect x="{40 + i*8}" y="{ly}" width="300" height="56" rx="12" fill="none" stroke="{C["cyan"]}" opacity="0" class="{lit}"/>'
                 f'<rect x="{40 + i*8}" y="{ly}" width="300" height="56" rx="12" fill="none" stroke="{C["mag"]}" opacity="0" class="{lit2}"/>'
                 f'<rect x="{56 + i*8}" y="{ly+16}" width="44" height="24" rx="6" fill="{col}" fill-opacity=".16" stroke="{col}"/>'
                 + text(78 + i * 8, ly + 33, tag, 12, col, "mono b", "middle")
                 + text(114 + i * 8, ly + 33, detail, 14, C["soft"]) + "</g>")
    down, up = "M370 86 L370 276", "M384 276 L384 86"
    body += wire(down, C["line"], 1.5) + wire(up, C["line"], 1.5)
    body += packet(a, down, C["cyan"], T, 4, 40) + packet(a, up, C["mag"], T, 54, 90)
    # The token panel
    tok = (("eyJhbGciOiJIUzI1", "mag"), (".eyJzdWIiOiI0Mn0", "lav"), (".SflKxwRJSMeKKF2", "cyan"))
    verified = a.add({0: "opacity:0", 18: "opacity:0", 22: "opacity:1", 94: "opacity:1", 98: "opacity:0",
                      100: "opacity:0"}, T)
    shackle = a.add({0: "transform:translateY(-5px)", 18: "transform:translateY(-5px)",
                     22: "transform:translateY(0)", 94: "transform:translateY(0)",
                     98: "transform:translateY(-5px)", 100: "transform:translateY(-5px)"}, T)
    body += (f'<g class="{a.fade_up(.6)}"><rect x="408" y="80" width="164" height="200" rx="12" fill="{C["panel"]}" stroke="{C["line"]}"/>'
             f'<g class="{shackle}"><path d="M478 112 v-10 a12 12 0 0 1 24 0 v10" fill="none" stroke="{C["lav"]}" stroke-width="3"/></g>'
             f'<rect x="470" y="110" width="40" height="30" rx="6" fill="{C["panel2"]}" stroke="{C["lav"]}" stroke-width="2"/>'
             f'<circle cx="490" cy="124" r="3.5" fill="{C["lav"]}"/>'
             + f'<g class="{verified}">' + text(490, 166, "✓ verified", 11.5, C["cyan"], "mono", "middle") + "</g>"
             + "".join(text(422, 198 + i * 20, s, 11.5, C[c], "mono") for i, (s, c) in enumerate(tok))
             + text(490, 264, "Bearer token", 11, C["dim"], "mono", "middle") + "</g>")
    desc = "Illustration: UI, API and database layers with a request travelling down and a response travelling up, and a JWT token being verified."
    return (svg_open(600, 320, "Full-stack web application — illustration", desc)
            + f"<defs>{plate_defs()}</defs>" + style_block(a)
            + card_frame(a, "fullstack-web-app", st) + body + "</svg>\n")


def proj_dbdesign(cfg) -> str:
    a = Anim()
    T = 10.0
    st = cfg["projects"]["database-design"]
    # Phase A: one wide table with repeated values (hidden in the static state)
    show_a = a.add({0: "opacity:1", 32: "opacity:1", 40: "opacity:0", 96: "opacity:0", 100: "opacity:1"}, T)
    cols = ("student", "course", "instructor", "room")
    rows = (("Lina H.", "Databases", "Dr. Amal", "B12"), ("Lina H.", "Web Dev", "Dr. Ziad", "A03"),
            ("Omar K.", "Databases", "Dr. Amal", "B12"))
    A = f'<g opacity="0" class="{show_a}"><rect x="36" y="84" width="528" height="160" rx="10" fill="{C["panel"]}" stroke="{C["line"]}"/>'
    A += text(52, 106, "enrollment_raw", 13, C["lav"], "mono b")
    for j, c in enumerate(cols):
        A += text(52 + j * 128, 132, c, 11, C["dim"], "mono")
    seen = {}
    for i, r in enumerate(rows):
        for j, v in enumerate(r):
            dup = (j, v) in seen
            seen[(j, v)] = True
            A += text(52 + j * 128, 160 + i * 28, v, 13, C["mag"] if dup else C["soft"])
    A += text(300, 272, "repeated facts → update anomalies", 12, C["mag"], "mono", "middle") + "</g>"

    # Phase B: normalized (this is the static / final state)
    show_b = a.add({0: "opacity:0", 40: "opacity:0", 48: "opacity:1", 94: "opacity:1", 99: "opacity:0",
                    100: "opacity:0"}, T)

    def tbl(x, y, w, name, fields):
        o = (f'<rect x="{x}" y="{y}" width="{w}" height="{36 + len(fields)*22}" rx="9" fill="{C["panel"]}" stroke="{C["line"]}"/>'
             f'<rect x="{x}" y="{y}" width="{w}" height="28" rx="9" fill="{C["panel2"]}"/>'
             + text(x + 12, y + 19, name, 12.5, C["lav"], "mono b"))
        for i, (f, k) in enumerate(fields):
            o += text(x + 12, y + 48 + i * 22, f, 12, C["soft"], "mono")
            if k:
                o += text(x + w - 10, y + 48 + i * 22, k, 10, C["cyan"] if k == "PK" else C["mag"], "mono b", "end")
        return o

    B = f'<g class="{show_b}">'
    B += tbl(36, 76, 150, "students", (("id", "PK"), ("name", ""), ("email", "")))
    B += tbl(414, 76, 150, "courses", (("id", "PK"), ("title", ""), ("instructor", "")))
    B += tbl(225, 170, 150, "enrollments", (("student_id", "FK"), ("course_id", "FK"), ("term", "")))
    r1 = "M186 130 C206 130 205 228 225 228"
    r2 = "M414 130 C394 130 395 250 375 250"
    for d in (r1, r2):
        L = path_length(d)
        draw = a.add({0: f"stroke-dashoffset:{L:.1f}", 48: f"stroke-dashoffset:{L:.1f}",
                      58: "stroke-dashoffset:0", 100: "stroke-dashoffset:0"}, T)
        B += f'<path d="{d}" fill="none" stroke="{C["mid"]}" stroke-width="1.6" stroke-dasharray="{L:.1f}" class="{draw}"/>'
    B += (crow(186, 130, -1, 0, "one") + crow(225, 228, 1, 0, "many")
          + crow(414, 130, 1, 0, "one") + crow(375, 250, -1, 0, "many"))
    B += text(470, 276, "3NF · one fact, one place", 12, C["cyan"], "mono", "middle") + "</g>"
    desc = ("Illustration: a wide table with repeated values is normalized into students, courses and "
            "enrollments tables joined by one-to-many relationships.")
    return (svg_open(600, 320, "Database design project — illustration", desc)
            + f"<defs>{plate_defs()}</defs>" + style_block(a)
            + card_frame(a, "university-db-design", st) + A + B + "</svg>\n")


# =========================================================================== #
# 6. MINDSET — principles as a git log
# =========================================================================== #
def mindset(cfg) -> str:
    W = 900
    a = Anim()
    T, D = 10.0, 2.6
    pr = cfg["principles"]
    gap = 104
    y0 = 128
    H = y0 + (len(pr) - 1) * gap + 96
    gx, tx = 72, 136  # graph column, text column
    main = f"M{gx} {y0 - 22} L{gx} {y0 + (len(pr) - 1) * gap + 22}"
    L = path_length(main)
    body = (f'<path d="{main}" stroke="{C["cyan"]}" stroke-opacity=".55" stroke-width="2.5" fill="none" '
            f'stroke-dasharray="{L:.1f}" class="{a.draw(L, .2, 1.6)}"/>')
    # a short side branch between 'model' and 'verify': try things on a branch, merge deliberately
    br = (f"M{gx} {y0 + gap} C{gx} {y0 + gap + 40} {gx + 30} {y0 + gap + 40} {gx + 30} {y0 + 2*gap - 10} "
          f"L{gx + 30} {y0 + 2*gap + 10} C{gx + 30} {y0 + 3*gap - 40} {gx} {y0 + 3*gap - 40} {gx} {y0 + 3*gap}")
    Lb = path_length(br)
    body += (f'<path d="{br}" stroke="{C["lav"]}" stroke-opacity=".6" stroke-width="2" fill="none" '
             f'stroke-dasharray="{Lb:.1f}" class="{a.draw(Lb, 1.2, 1.2)}"/>'
             f'<circle cx="{gx + 30}" cy="{y0 + 2*gap}" r="5" fill="{C["bg"]}" stroke="{C["lav"]}" stroke-width="2" class="{a.fade_in(2)}"/>')
    span = (len(pr) - 1) * gap + 44
    for i, (h, kind, head, detail) in enumerate(pr):
        cy = y0 + i * gap
        frac = (cy - (y0 - 22)) / span
        tp = 5 + frac * 70
        ping = a.add({0: "opacity:0;transform:scale(1)", tp - .5: "opacity:0;transform:scale(1)",
                      tp: "opacity:.8;transform:scale(1)", tp + 8: "opacity:0;transform:scale(2.6)",
                      100: "opacity:0;transform:scale(2.6)"}, T, D, timing="ease-out")
        body += f'<g class="{a.fade_up(.4 + i * .22, .8, 10)}">'
        body += (f'<circle cx="{gx}" cy="{cy}" r="9" fill="none" stroke="{C["cyan"]}" stroke-width="2" opacity="0" class="{ping} fb"/>'
                 f'<circle cx="{gx}" cy="{cy}" r="8" fill="{C["bg"]}" stroke="{C["cyan"]}" stroke-width="2.5"/>')
        body += (f'<text x="{tx}" y="{cy + 5}" class="mono" font-size="14.5" xml:space="preserve">'
                 f'<tspan fill="{C["lav"]}">{esc(h)}</tspan><tspan fill="{C["cyan"]}">  {esc(kind)}:</tspan>'
                 + (f'<tspan fill="{C["mag"]}">  (HEAD → main)</tspan>' if i == len(pr) - 1 else "")
                 + "</text>")
        body += text(tx, cy + 35, head, 23, C["text"], "sans b")
        body += text(tx, cy + 60, detail, 16, C["muted"]) + "</g>"
    # linear travel so each commit's ping lines up with the packet passing it
    Lm = path_length(main)
    trav = a.add({0: f"stroke-dashoffset:{20 + 9:.1f}", 5: f"stroke-dashoffset:{20 + 9:.1f}",
                  75: f"stroke-dashoffset:{-(Lm + 9):.1f}", 100: f"stroke-dashoffset:{-(Lm + 9):.1f}"},
                 T, D, timing="linear")
    da = f"20 {Lm + 60:.1f}"
    body += (f'<path d="{main}" fill="none" stroke="{C["cyan"]}" stroke-opacity=".3" stroke-width="10" stroke-linecap="round" '
             f'stroke-dasharray="{da}" stroke-dashoffset="29" class="{trav}"/>'
             f'<path d="{main}" fill="none" stroke="{C["cyan"]}" stroke-width="3.5" stroke-linecap="round" '
             f'stroke-dasharray="{da}" stroke-dashoffset="29" class="{trav}"/>')
    head = text(40, 56, "$ git log --reverse --oneline mindset", 15, C["dim"], "mono")
    desc = "Engineering principles shown as a git log: " + " ".join(
        f"{p[1]}: {p[2]} {p[3]}" for p in pr)
    return (svg_open(W, H, "Engineering mindset as a commit history", desc)
            + f"<defs>{plate_defs()}</defs>" + style_block(a) + plate(W, H) + head + body + "</svg>\n")


# =========================================================================== #
# 7. LEARNING ROADMAP — migrations that never finish
# =========================================================================== #
def roadmap(cfg) -> str:
    W = 900
    a = Anim()
    T, D = 12.0, 1.8
    tracks = cfg["learning"]
    y0, gap, ch = 120, 88, 74
    H = y0 + len(tracks) * gap + 22
    rx = 72
    body = ""
    rail = f"M{rx} {y0 + ch/2} L{rx} {y0 + (len(tracks)-1)*gap + ch/2}"
    Lr = path_length(rail)
    body += (f'<path d="{rail}" stroke="{C["lav"]}" stroke-opacity=".5" stroke-width="2" fill="none" '
             f'stroke-dasharray="{Lr:.1f}" class="{a.draw(Lr, .3, 1.4)}"/>')
    for i, (slug, title, detail) in enumerate(tracks):
        y = y0 + i * gap
        cy = y + ch / 2
        tp = 4 + (i / max(len(tracks) - 1, 1)) * 80
        lit = a.window(T, tp, tp + 9, "opacity:0", "opacity:1", ramp=2, delay=D)
        body += f'<g class="{a.fade_up(.3 + i * .14, .8, 10)}">'
        if i:
            body += (f'<path d="M{rx-5} {cy - gap/2 - 3} l5 6 l5 -6" fill="none" stroke="{C["lav"]}" '
                     f'stroke-opacity=".7" stroke-width="1.6"/>')
        body += (f'<rect x="{rx-7}" y="{cy-7}" width="14" height="14" rx="3" fill="{C["bg"]}" stroke="{C["lav"]}" '
                 f'stroke-width="2" transform="rotate(45 {rx} {cy})"/>')
        body += (f'<rect x="104" y="{y}" width="{W-148}" height="{ch}" rx="12" fill="{C["panel"]}" fill-opacity=".9" stroke="{C["line"]}"/>'
                 f'<rect x="104" y="{y}" width="{W-148}" height="{ch}" rx="12" fill="{C["lav"]}" fill-opacity=".06" '
                 f'stroke="{C["lav"]}" stroke-opacity=".8" opacity="0" class="{lit}"/>')
        body += text(124, y + 22, f"{i+1:04d}_{slug}", 12, C["dim"], "mono")
        body += text(124, y + 46, title, 19, C["text"], "sans b")
        body += text(124, y + 65, detail, 14.5, C["muted"])
        body += (f'<rect x="{W-152}" y="{y + ch/2 - 13}" width="92" height="26" rx="13" fill="none" stroke="{C["lav"]}" stroke-opacity=".7"/>'
                 + status_glyph(a, W - 136, y + ch / 2, "learning", r=5)
                 + text(W - 122, y + ch / 2 + 4.5, "learning", 12, C["lav"], "mono"))
        body += "</g>"
    # 'head' marker travelling down the rail
    head_move = a.add({0: f"transform:translateY(0);opacity:0", 3: "opacity:1",
                       86: f"transform:translateY({Lr:.1f}px);opacity:1",
                       92: f"transform:translateY({Lr:.1f}px);opacity:0",
                       100: f"transform:translateY({Lr:.1f}px);opacity:0"}, T, D, timing="linear")
    body += (f'<g class="{head_move}" opacity="0"><circle cx="{rx}" cy="{y0 + ch/2}" r="13" fill="{C["lav"]}" fill-opacity=".25"/>'
             f'<circle cx="{rx}" cy="{y0 + ch/2}" r="5" fill="{C["lav"]}"/></g>')
    head = (text(40, 56, "$ alembic upgrade head   # learning never finishes migrating", 15, C["dim"], "mono")
            + text(40, 86, "A roadmap, not a scoreboard — no percentages, because learning isn't a progress bar.",
                   15.5, C["muted"]))
    desc = "Learning roadmap, currently learning: " + "; ".join(f"{t}: {d}" for _, t, d in tracks)
    return (svg_open(W, H, "Learning roadmap", desc) + f"<defs>{plate_defs()}</defs>" + style_block(a)
            + plate(W, H) + head + body + "</svg>\n")


# =========================================================================== #
# 8. SIGN-OFF
# =========================================================================== #
def signoff(cfg) -> str:
    W, H = 1200, 340
    a = Anim()
    T, D = 8.0, 2.2
    mark, d = s_route(120, 46, 4.2, stroke=C["lav"], width=5)
    L = path_length(d)
    mark = mark.replace('stroke-linecap="round"/>',
                        f'stroke-linecap="round" stroke-dasharray="{L:.1f}" class="{a.draw(L, .2, 1.8)}"/>', 1)
    up = reverse_s(d)
    pk = (packet(a, d, C["cyan"], T, 4, 42, dash=34, width=6, delay=D)
          + packet(a, up, C["mag"], T, 54, 92, dash=34, width=6, delay=D))
    status = "HTTP/1.1 201 Created"
    sw = len(status) * 9.6
    caret = a.add({0: "opacity:1", 49: "opacity:1", 50: "opacity:0", 100: "opacity:0"}, 1.1, timing="linear")
    txt = (f'<g class="{a.fade_up(.6)}"><text x="420" y="104" class="mono" font-size="16" fill="{C["cyan"]}" '
           f'textLength="{sw:.0f}" lengthAdjust="spacing">{status}</text>'
           f'<rect x="{420 + sw + 6:.0f}" y="90" width="9" height="18" rx="1.5" fill="{C["cyan"]}" class="{caret}"/>'
           + text(420, 128, "Location: /collaborations/next", 13, C["dim"], "mono") + "</g>"
           + f'<g class="{a.fade_up(.85)}">' + text(420, 190, "Let's build something", 40, C["text"], "sans b") + "</g>"
           + f'<g class="{a.fade_up(1)}"><text x="420" y="240" class="sans b" font-size="40" fill="url(#tagGrad)">'
             "that works — and feels right.</text></g>"
           + f'<g class="{a.fade_up(1.2)}">'
           + text(420, 288, f"{cfg['name']}  ·  {cfg['title'].split(' · ')[0]}  ·  {cfg['tagline'].rstrip('.').lower()}",
                  17, C["muted"]) + "</g>"
           + text(W - 30, H - 20, "EOF", 11, C["dim"], "mono", "end"))
    dust = particles(a, [(980, 80, 1.4, 9), (1120, 220, 1.2, 11), (340, 300, 1.3, 10), (760, 40, 1.1, 12)])
    defs = f"""<defs>{plate_defs()}
<linearGradient id="tagGrad" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{C['cyan']}"/><stop offset="1" stop-color="{C['lav']}"/></linearGradient>
</defs>"""
    desc = (f"Closing card. The S-route mark: a packet travels from a screen down to a database and back. "
            f"Text: HTTP/1.1 201 Created. Let's build something that works — and feels right. {cfg['name']}.")
    return (svg_open(W, H, "Let's build something", desc) + defs + style_block(a) + plate(W, H)
            + dust + mark + pk + txt + "</svg>\n")


# =========================================================================== #
# README sync: the plain-text stack table always matches the schema graphic
# =========================================================================== #
AREAS = (("fundamentals", "Programming fundamentals"), ("frontend", "Frontend"),
         ("backend", "Backend & APIs"), ("data", "Databases & data modelling"),
         ("erp", "ERP"), ("tools", "Tools"))


def sync_readme(cfg) -> None:
    readme = ROOT / "README.md"
    if not readme.exists():
        return
    src = readme.read_text(encoding="utf-8")
    start = src.find("<!-- stack:start")
    end = src.find("<!-- stack:end -->")
    if start < 0 or end < 0:
        return
    head_end = src.index("-->", start) + 3
    rows = ["| Area | Practiced | Learning | Studied in theory |", "|---|---|---|---|"]
    for key, label in AREAS:
        cells = [" · ".join(n for n, s in cfg["stack"][key] if s == want) or "—"
                 for want in ("practiced", "learning", "studied")]
        rows.append(f"| {label} | " + " | ".join(cells) + " |")
    new = src[:head_end] + "\n" + "\n".join(rows) + "\n" + src[end:]
    if new != src:
        readme.write_text(new, encoding="utf-8")
        print("  README.md                    stack table refreshed")


# =========================================================================== #
def main() -> None:
    cfg = json.loads((ROOT / "profile.json").read_text(encoding="utf-8"))
    OUT.mkdir(exist_ok=True)
    print("Building assets/")
    write("hero.svg", hero(cfg))
    write("divider.svg", divider(cfg))
    write("tech-schema.svg", tech_schema(cfg))
    write("round-trip.svg", round_trip(cfg))
    write("project-student-system.svg", proj_student(cfg))
    write("project-odoo-module.svg", proj_odoo(cfg))
    write("project-fullstack-app.svg", proj_fullstack(cfg))
    write("project-database-design.svg", proj_dbdesign(cfg))
    write("mindset.svg", mindset(cfg))
    write("roadmap.svg", roadmap(cfg))
    write("signoff.svg", signoff(cfg))
    # The activity graphic is normally written by the GitHub Action; only create the
    # honest "not generated yet" placeholder if it does not exist.
    if not (OUT / "activity.svg").exists():
        write("activity.svg", activity.render(None, cfg["handle"]))
    sync_readme(cfg)


if __name__ == "__main__":
    main()
