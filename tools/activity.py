"""Render assets/activity.svg from the profile owner's real, public contribution calendar.

Run by .github/workflows/activity.yml:
    GITHUB_TOKEN=... LOGIN=<username> python tools/activity.py

Without data (before the first workflow run) build_assets.py writes a placeholder
that says so, rather than showing invented numbers.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from svgkit import C, Anim, esc, plate, plate_defs, style_block, svg_open, text  # noqa: E402

QUERY = """query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date weekday contributionCount contributionLevel } }
      }
    }
  }
}"""

LEVEL = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}
FILL = {0: None, 1: "#2E3A8F", 2: C["blue"], 3: C["lav"], 4: C["cyan"]}


def fetch(login: str, token: str) -> dict:
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json",
                 "User-Agent": "profile-activity-svg"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.load(r)
    if payload.get("errors"):
        raise RuntimeError(payload["errors"])
    return payload["data"]["user"]["contributionsCollection"]["contributionCalendar"]


def render(cal: dict | None, handle: str) -> str:
    W, H = 1200, 310
    a = Anim()
    cell, gap = 13, 4
    pitch = cell + gap
    weeks = cal["weeks"] if cal else [{"contributionDays": [None] * 7} for _ in range(53)]
    gw = len(weeks) * pitch - gap
    x0, y0 = (W - gw) / 2 + 14, 126

    grid = ""
    months_seen = set()
    for wi, wk in enumerate(weeks):
        for slot, day in enumerate(wk["contributionDays"]):
            if day is None:  # placeholder grid: empty cells only
                di, lvl, title = slot, 0, ""
            else:
                di, lvl = day["weekday"], LEVEL.get(day["contributionLevel"], 0)
                n = day["contributionCount"]
                title = f'<title>{day["date"]}: {n} contribution{"s" if n != 1 else ""}</title>'
                m = day["date"][:7]
                if day["date"][8:] <= "07" and m not in months_seen and di == 0:
                    months_seen.add(m)
                    label = date.fromisoformat(day["date"]).strftime("%b")
                    grid += text(x0 + wi * pitch, y0 - 10, label, 11, C["dim"], "mono")
            x, y = x0 + wi * pitch, y0 + di * pitch
            fill = FILL[lvl]
            if fill:
                grid += f'<rect x="{x:.0f}" y="{y}" width="{cell}" height="{cell}" rx="3" fill="{fill}">{title}</rect>'
            else:
                grid += (f'<rect x="{x:.0f}" y="{y}" width="{cell}" height="{cell}" rx="3" fill="{C["panel2"]}" '
                         f'stroke="{C["line"]}" stroke-width=".8">{title}</rect>')
    for di, lab in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        grid += text(x0 - 10, y0 + di * pitch + 10, lab, 11, C["dim"], "mono", "end")

    # "Sequential scan": a cursor sweeps the table, column by column.
    scan = a.add({0: "transform:translateX(0);opacity:0", 4: "opacity:1",
                  90: f"transform:translateX({gw:.0f}px);opacity:1",
                  96: f"transform:translateX({gw:.0f}px);opacity:0",
                  100: f"transform:translateX({gw:.0f}px);opacity:0"}, 14, 1, timing="linear")
    grid += (f'<g class="{scan}" opacity="0"><rect x="{x0 - 3:.0f}" y="{y0 - 4}" width="{cell + 6}" '
             f'height="{7 * pitch + 4}" rx="5" fill="{C["lav"]}" fill-opacity=".12" stroke="{C["lav"]}" '
             f'stroke-opacity=".7"/></g>')

    sql = "SELECT day, contributions FROM github.activity WHERE day > now() - interval '1 year';"
    if cal:
        headline = f"{cal['totalContributions']:,} contributions in the last year"
        foot = "Public GitHub data · rendered by .github/workflows/activity.yml"
    else:
        headline = "Activity map: waiting for its first sync"
        foot = ("No data yet — the workflow fills this in once the README lives in the "
                "<username>/<username> profile repository.")
    legend = "".join(
        (f'<rect x="{1040 + i * 17}" y="{H - 44}" width="{cell}" height="{cell}" rx="3" '
         + (f'fill="{FILL[i]}"/>' if FILL[i] else f'fill="{C["panel2"]}" stroke="{C["line"]}" stroke-width=".8"/>'))
        for i in range(5))
    legend += text(1032, H - 34, "less", 11, C["dim"], "mono", "end") + text(1130, H - 34, "more", 11, C["dim"], "mono")
    body = (text(40, 50, sql, 13.5, C["dim"], "mono")
            + text(40, 84, headline, 22, C["text"], "sans b")
            + grid + text(40, H - 34, foot, 12, C["dim"], "mono") + legend)
    desc = (f"Contribution calendar for the last year: {cal['totalContributions']} contributions."
            if cal else "Placeholder: the contribution calendar has not been generated yet.")
    return (svg_open(W, H, f"{handle} — GitHub activity", desc) + f"<defs>{plate_defs()}</defs>"
            + style_block(a) + plate(W, H) + body + "</svg>\n")


def main() -> int:
    login, token = os.environ.get("LOGIN"), os.environ.get("GITHUB_TOKEN")
    if not login or not token:
        print("LOGIN and GITHUB_TOKEN are required", file=sys.stderr)
        return 2
    cal = fetch(login, token)
    out = Path(__file__).resolve().parent.parent / "assets" / "activity.svg"
    out.write_text(render(cal, login), encoding="utf-8")
    print(f"wrote {out} ({cal['totalContributions']} contributions)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
