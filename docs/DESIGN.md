# The Round Trip: design notes

Profile README for **Sarai Soliman**, IT Engineer.
Tagline: **From schema to screen.** Supporting line: *Turning logic into experiences.*

## 1. Concept

Every feature, however small, is a round trip: someone touches an interface, a request crosses an API, logic runs, a database answers, and the response changes what the person sees. The profile is built around that journey, because it is exactly the range Sarai is interested in (frontend, backend, databases) and it shows engineering understanding instead of just stating it.

The "living digital workshop" from the brief became the hero's workspace: a page, a handler and a table, wired together and working.

### Signature motif: the S-route

The letter **S** (for Sarai Soliman) is drawn as a request route. Its top end is a small **screen** and its bottom end is a **database cylinder**. A packet runs down it (the request) and back up it (the response). It appears:

- next to the `whoami` prompt in the hero,
- at the centre of every section divider, where a packet comes in along the hairline, climbs the S and leaves on the other side,
- full-size in the sign-off, where it runs the complete round trip.

### Original details that belong to the same system

| Detail | Where | Why it fits |
|---|---|---|
| Stack drawn as an **ER diagram** with crow's-foot relations | `tech-schema.svg` | Database thinking applied to herself. Each skill row has a status column (`practiced / learning / studied`), so honesty is built into the schema. |
| Hub table `engineer` with `curiosity NOT NULL` and `growth AUTO_INCREMENT` | `tech-schema.svg` | Easter egg: personality expressed as constraints. |
| Principles as `git log --reverse` with hex-word hashes `c0ffee1 · da7aba5 · 5ca1ab1 · 7e57ed0 · feedbac` | `mindset.svg` | Easter egg: coffee, database, scalable, tested, feedback. |
| Learning as **migrations**: `alembic upgrade head  # learning never finishes migrating` | `roadmap.svg` | A roadmap with no percentages, by design. |
| Activity calendar framed as a **sequential scan** of a table | `activity.svg` | Real data, same visual language. |
| `HTTP/1.1 201 Created` · `Location: /collaborations/next` | `signoff.svg` | The closing "response". 201 means something new was created. |
| Skeleton rows that turn into real rows | `round-trip.svg` | Motion that teaches: a loading state, not just decoration. |

## 2. Visual system

| Token | Hex | Role |
|---|---|---|
| Midnight navy | `#0A0E1F` | plate background |
| Deep indigo | `#121741` | plate gradient end, code panels |
| Glass panel | `#151B42` / `#1B2253` | panels and header bands |
| Electric blue | `#4F7BFF` | buttons, primary action |
| Lavender | `#B7A5FF` | identity, structure, "learning" |
| Cyan | `#5BE1F0` | **request** / data moving toward the database, "practiced" |
| Magenta | `#FF74C0` | **response** moving back toward the person (used sparingly) |
| Mid-tone | `#6B74B3` | dividers on transparent backgrounds; readable on both GitHub themes |

Colour has meaning everywhere: **cyan travels down (request), magenta travels back (response)**.

**Type:** system fonts only, because an SVG inside `<img>` cannot load web fonts. Sans: Segoe UI / SF Pro / Helvetica stack. Mono: JetBrains Mono / Cascadia / SF Mono / Consolas stack. Layouts leave slack for width differences between those fonts, and `textLength` is used where a caret must sit exactly after a string.

**Surfaces:** dark rounded "instrument plates" with a 24px dot grid, two soft radial glows and a lavender top-edge highlight. On GitHub's light theme they read as deliberate cards. Dividers are transparent with mid-tone strokes.

## 3. Motion

| Section | What moves | What it means |
|---|---|---|
| Hero | intro: prompt types, name rises, panels settle, code lines appear. Loop (9 s): *Load* ripples, request runs UI → code → DB, rows scan, response returns, UI rows flash | the whole profile in one sentence |
| Dividers | packet along the hairline and through the S | progress through the system |
| Stack | tables rise in sequence, relations draw, packets travel the foreign keys; "learning" glyphs breathe | connections between skills |
| Round trip (12 s) | six synchronised steps with a live stepper and caption | how a request actually works |
| Projects | CRUD chips act on rows · a record moves across kanban stages · token verified, packet through layers · a wide table normalises into three | each project's core idea |
| Mindset | commit graph draws; a packet pings each commit | a process, in order |
| Learning | a `head` marker walks the migration chain | ongoing, not finished |
| Sign-off | the S draws itself; full round trip on it | closure |

Rules: CSS `@keyframes` only (no SMIL), loops of 4.5 s or longer, nothing flashes, easing `cubic-bezier(.5,0,.25,1)` for travel and `(.2,.7,.2,1)` for entrances.

**Static fallback:** every animated element's base style is its meaningful final state (real rows, all checks ticked, normalized tables, summary caption). `@media (prefers-reduced-motion: reduce)` turns all animation off and leaves that state. This was verified by rendering each SVG with animations disabled.

## 4. GitHub rendering: what works and what doesn't

README images are shown through `<img>` (proxied by camo for remote URLs; relative paths are served from the repo). Inside an `<img>`, an SVG is a sealed document.

| Technique | Status in GitHub READMEs | Used? |
|---|---|---|
| CSS `@keyframes` in an embedded `<style>` | Works in Chrome, Firefox, Safari and the GitHub mobile apps' web views | **Yes**: all motion |
| `prefers-reduced-motion` inside the SVG | Honoured by modern browsers | **Yes** |
| `stroke-dashoffset` packets / line drawing | Robust everywhere. Lengths are computed by the build script, not via `pathLength` | **Yes** |
| SMIL (`<animate>`, `<animateMotion>`) | Works, but ignores reduced-motion | No (the validator rejects it) |
| `<foreignObject>` (HTML inside SVG) | Inconsistent, especially Safari | No |
| SVG filters (blur, glow) | Work, but cost CPU on every animated frame | No: glows are gradients and wide translucent strokes |
| `<script>`, `onclick`, hover, links inside the SVG | Never run in `<img>` | No: nothing is interactive, and nothing pretends to be |
| Web fonts, external images or CSS in the SVG | Blocked | No |
| CSS on elements that also have a `transform` attribute | CSS would override it | Avoided: wrapper `<g>` elements carry the animations |
| `<picture>` + `prefers-color-scheme` | Supported in README HTML | Not needed: plates are theme-neutral |
| HTML `width`, `align`, `valign` and `<details>` | Allowed by GitHub's sanitizer | Yes |
| `style=` attributes and `<style>` in the README itself | Stripped | Not used |

Not verifiable locally: GitHub's exact sanitizer output and camo caching. Remote images (like readme-stats) can be cached for hours. Relative assets update as soon as you push.

**Mobile:** images scale to the column width (about 350px on a phone). Small text inside wide SVGs becomes decorative at that size, so everything essential is also in Markdown: the About text, the plain-text stack table in `<details>`, the step-by-step list under the diagram, and alt text on every image.

## 5. Honesty rules applied

- Skill status is three categories, with no percentages or proficiency scores. **The current statuses in `profile.json` are conservative defaults and need Sarai's review.**
- Node.js is omitted (no verified experience). Alembic and DSA are qualified.
- Project cards are labelled `blueprint`, with explicit `[PLACEHOLDER]` text and no links, until real repositories exist.
- Activity data comes only from the GitHub API for the repository owner. Before the first run, the graphic says it is waiting, and shows no invented data.
- The workflow only runs in a `<username>/<username>` repository, so it can never render someone else's activity.

## 6. Maintenance

```
profile.json             text and statuses used inside the SVGs (edit this)
tools/build_assets.py    generates assets/*.svg and syncs the README stack table
tools/svgkit.py          shared tokens, plate, packets, S-route, path lengths
tools/activity.py        contribution calendar → assets/activity.svg (run by the Action)
tools/validate.py        checks SVGs + README for GitHub compatibility, lists placeholders
preview/index.html       local preview: README or asset gallery, dark/light, desktop/mobile
.github/workflows/activity.yml   daily activity refresh (profile repo only)
```

```
python tools/build_assets.py     # after editing profile.json
python tools/validate.py         # before every push
python -m http.server 8765       # then open http://localhost:8765/preview/
```

Python 3.9+ and the standard library only.
