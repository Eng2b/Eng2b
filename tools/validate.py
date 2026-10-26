"""Check the README and its SVGs against what GitHub can actually render.

    python tools/validate.py

Exits non-zero on errors. Placeholders are reported as a to-do list, not errors.
"""
from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NS = "{http://www.w3.org/2000/svg}"
MAX_KB = 60

# Things that silently break (or are stripped) inside a GitHub <img>.
FORBIDDEN = [
    (r"<script", "scripts never run in an <img> SVG"),
    (r"<foreignObject", "foreignObject renders inconsistently (Safari, GitHub mobile)"),
    (r"\son[a-z]+\s*=", "event handlers never fire in an <img> SVG"),
    (r"@import", "external CSS is blocked in an <img> SVG"),
    (r"(?:href|src)\s*=\s*[\"']https?:", "external resources are blocked in an <img> SVG"),
    (r"url\(\s*[\"']?https?:", "external resources are blocked in an <img> SVG"),
    (r"<(?:animate|animateTransform|animateMotion|set)\b",
     "SMIL ignores prefers-reduced-motion; use CSS keyframes"),
]


def check_svg(path: Path) -> list[str]:
    errs = []
    src = path.read_text(encoding="utf-8")
    try:
        root = ET.fromstring(src)
    except ET.ParseError as e:
        return [f"{path.name}: not well-formed XML ({e})"]
    if root.tag != f"{NS}svg":
        errs.append(f"{path.name}: root element is not <svg>")
    for a in ("viewBox", "width", "height"):
        if a not in root.attrib:
            errs.append(f"{path.name}: missing {a}")
    if root.find(f"{NS}title") is None or root.find(f"{NS}desc") is None:
        errs.append(f"{path.name}: missing <title>/<desc> for accessibility")
    for pat, why in FORBIDDEN:
        if re.search(pat, src, re.I):
            errs.append(f"{path.name}: {why}")
    if "@keyframes" in src and "prefers-reduced-motion" not in src:
        errs.append(f"{path.name}: animated but has no prefers-reduced-motion rule")
    ids = re.findall(r'\sid="([^"]+)"', src)
    for ref in set(re.findall(r'url\(#([^)]+)\)', src)):
        if ref not in ids:
            errs.append(f"{path.name}: references missing #{ref}")
    kb = len(src.encode()) / 1024
    if kb > MAX_KB:
        errs.append(f"{path.name}: {kb:.0f} KB is heavy for a README image (limit {MAX_KB} KB)")
    return errs


def check_readme(path: Path) -> tuple[list[str], list[str]]:
    errs, todo = [], []
    md = path.read_text(encoding="utf-8")
    visible = re.sub(r"<!--.*?-->", "", md, flags=re.S)

    for src in re.findall(r'<img[^>]+src="([^"]+)"', visible) + re.findall(r"!\[[^\]]*\]\(([^)]+)\)", visible):
        if src.startswith(("http://", "https://")):
            errs.append(f"README: remote image {src} — keep remote images commented until configured")
        elif not (ROOT / src).exists():
            errs.append(f"README: image not found: {src}")
    for tag in re.findall(r"<img[^>]*>", visible):
        if "alt=" not in tag:
            errs.append(f"README: <img> without alt: {tag[:60]}")

    def slug(h):
        return re.sub(r"\s", "-", re.sub(r"[^\w\- ]", "", h.strip().lower()))
    anchors = {slug(h) for h in re.findall(r"^#{1,6}\s+(.+)$", visible, re.M)}
    for a in re.findall(r'href="#([^"]+)"', visible):
        if a not in anchors:
            errs.append(f"README: navigation link #{a} has no matching heading")

    levels = [len(h) for h in re.findall(r"^(#{1,6})\s", visible, re.M)]
    for prev, cur in zip(levels, levels[1:]):
        if cur > prev + 1:
            errs.append("README: heading level skips (e.g. ## then ####)")

    for i, line in enumerate(md.splitlines(), 1):
        for ph in re.findall(r"\[(?:PLACEHOLDER |ADD )[^\]]*\]", line):
            todo.append(f"README.md:{i}  {ph}")
    return errs, todo


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")  # Windows consoles default to cp1252
    errors = []
    svgs = sorted((ROOT / "assets").glob("*.svg"))
    for p in svgs:
        errors += check_svg(p)
    e, todo = check_readme(ROOT / "README.md")
    errors += e

    print(f"Checked {len(svgs)} SVGs and README.md")
    if errors:
        print("\nERRORS")
        print("\n".join(f"  ✗ {x}" for x in errors))
    else:
        print("  ✓ no errors")
    if todo:
        print(f"\nPLACEHOLDERS TO FILL IN ({len(todo)})")
        print("\n".join(f"  • {t}" for t in todo))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
