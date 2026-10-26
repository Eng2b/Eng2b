<!--
  GitHub profile README — Sarai Soliman
  ─────────────────────────────────────
  • Graphics in assets/ are generated. Edit profile.json, then run:  python tools/build_assets.py
    (the build also refreshes the stack table between the "stack:start/stack:end" markers below).
  • Everything in [SQUARE BRACKETS AND CAPITALS] is a placeholder that still needs real information.
  • Design notes and GitHub rendering limits: docs/DESIGN.md
  curiosity NOT NULL
-->

<div align="center">
  <img src="assets/hero.svg" width="100%" alt="Sarai Soliman — IT Engineer and Software Developer. From schema to screen: turning logic into experiences. An animated workspace shows a click on a web page travelling through an API handler to a students table and back.">
</div>

<p align="center">
  <a href="#about">About</a> ·
  <a href="#stack">Stack</a> ·
  <a href="#round-trip">Round trip</a> ·
  <a href="#showcase">Showcase</a> ·
  <a href="#mindset">Mindset</a> ·
  <a href="#learning">Learning</a> ·
  <a href="#connect">Connect</a>
</p>

<img src="assets/divider.svg" width="100%" alt="">

## About

<sub><code>01</code> — an engineering story in three acts</sub>

I'm **Sarai Soliman**, a recent IT Engineering graduate building a career in software development.
I like knowing how a system works all the way through: from the table that stores a fact to the screen where someone uses it.

**I. Understand.** I start where the problem lives — who will use the software, what they actually need, and what can go wrong.

**II. Model.** Then I give the data a shape: entities, relationships and constraints. A clear schema makes everything built on top of it simpler.

**III. Build the round trip.** From there I work on both sides — APIs that validate and protect, and interfaces that make the result feel obvious.

I'm early in my career, and I'd rather say so plainly: I'm building practical projects, reading other people's code, and getting a little better every week.
**Open to junior software development opportunities.**

<img src="assets/divider.svg" width="100%" alt="">

## Stack

<sub><code>02</code> — what I work with, modelled the way I'd model anything: as a schema</sub>

<img src="assets/tech-schema.svg" width="100%" alt="My technology stack drawn as an entity-relationship diagram: frontend, backend, data, fundamentals, ERP and tools tables, each technology marked practiced, learning or studied. A plain-text version follows.">

<details>
<summary><b>Read the schema as plain text</b></summary>
<br>

<!-- stack:start — generated from profile.json by tools/build_assets.py; edits here are overwritten -->
| Area | Practiced | Learning | Studied in theory |
|---|---|---|---|
| Programming fundamentals | C++ · C# · Object-oriented (OOP) | — | Data structures & algorithms |
| Frontend | HTML · CSS · JavaScript · Responsive design | React | — |
| Backend & APIs | Python · REST APIs | FastAPI · JWT authentication | — |
| Databases & data modelling | SQL · PostgreSQL · SQL Server · ER diagrams · Normalization | Alembic migrations | — |
| ERP | — | Odoo · Python modules | ORM concepts · ERP workflows |
| Tools | Git · GitHub · Linux · VS Code · Visual Studio · npm | — | — |
<!-- stack:end -->

*Practiced* = used hands-on in coursework or projects · *Learning* = actively learning now · *Studied* = covered in theory. These describe exposure, not expertise.

</details>

<img src="assets/divider.svg" width="100%" alt="">

## Round trip

<sub><code>03</code> — frontend, backend and database: three worlds, one request</sub>

<img src="assets/round-trip.svg" width="100%" alt="Animated architecture diagram. Frontend: the user clicks Load and skeleton rows wait. Backend: the request passes the router, JWT authentication, validation and the service layer. Database: a query joins students to majors. The JSON response flows back and the list renders real rows.">

**Interface → API request → backend logic → database query → response → updated interface.**
I'm interested in all three worlds, and especially in the seams between them — a form that sends the wrong shape, an endpoint that trusts its input, a query that returns more than it should.

<details>
<summary><b>What the diagram shows, step by step</b></summary>
<br>

1. **Event** — the user picks a filter and clicks *Load*; the list shows skeleton rows instead of freezing.
2. **Request** — `GET /api/students?major=IT` with a bearer token.
3. **Logic** — the route matches, the JWT is verified, the input is validated, business rules apply.
4. **Query** — `SELECT … FROM students JOIN majors … WHERE m.code = 'IT'`: a many-to-one relationship doing its job.
5. **Response** — `200 OK` with JSON the frontend can trust.
6. **Render** — skeleton rows become real data.

</details>

<img src="assets/divider.svg" width="100%" alt="">

## Showcase

<sub><code>04</code> — project blueprints: a card gets a link when its repository is public</sub>

<!--
  HOW TO PUBLISH A REAL PROJECT CARD
  1. Push the project to a public repository.
  2. Replace every [PLACEHOLDER] in its card below with the real sentence, stack and link.
  3. In profile.json set its status to "live", run python tools/build_assets.py
     (the dashed "blueprint" tag on the illustration becomes a solid "live" tag).
  Delete any card whose project does not exist and that you don't plan to publish.
-->

<table>
<tr>
<td width="50%" valign="top">

<img src="assets/project-student-system.svg" width="100%" alt="Illustration: a Student class diagram beside a list running create, read, update and delete operations.">

**Student Management System** <code>blueprint</code><br>
<sub>[PLACEHOLDER — the problem it solves]<br>
Scope: CRUD · OOP · database integration · validation<br>
Stack: [PLACEHOLDER e.g. C# · SQL Server]<br>
Repo: [ADD REPOSITORY LINK]</sub>

</td>
<td width="50%" valign="top">

<img src="assets/project-odoo-module.svg" width="100%" alt="Illustration: an Odoo module's file tree beside a kanban board where a record moves from Draft to Confirmed to Done.">

**Odoo Custom Module** <code>blueprint</code><br>
<sub>[PLACEHOLDER — the business workflow it supports]<br>
Scope: models · ORM relations · views & menus · workflow<br>
Stack: Python · Odoo · XML<br>
Repo: [ADD REPOSITORY LINK]</sub>

</td>
</tr>
<tr>
<td width="50%" valign="top">

<img src="assets/project-fullstack-app.svg" width="100%" alt="Illustration: UI, API and database layers with a request travelling down and a response travelling up, and a JWT token being verified.">

**Full-Stack Web Application** <code>blueprint</code><br>
<sub>[PLACEHOLDER — who uses it, and for what]<br>
Scope: frontend · REST API · database · auth<br>
Stack: [PLACEHOLDER e.g. JavaScript · FastAPI · PostgreSQL]<br>
Repo: [ADD REPOSITORY LINK]</sub>

</td>
<td width="50%" valign="top">

<img src="assets/project-database-design.svg" width="100%" alt="Illustration: a wide table with repeated values is normalized into students, courses and enrollments tables.">

**Database Design Project** <code>blueprint</code><br>
<sub>[PLACEHOLDER — the domain it models]<br>
Scope: ER model · schema · normalization · constraints<br>
Stack: [PLACEHOLDER e.g. PostgreSQL]<br>
Repo: [ADD REPOSITORY LINK]</sub>

</td>
</tr>
</table>

<img src="assets/divider.svg" width="100%" alt="">

## Mindset

<sub><code>05</code> — how I work, logged the way I'd log anything</sub>

<img src="assets/mindset.svg" width="100%" alt="Engineering principles as a git log. Understand the problem before writing code. Design the data before the features. Write code someone else can read. Validate assumptions and handle errors. Ship something practical, then improve it.">

<img src="assets/divider.svg" width="100%" alt="">

## Learning

<sub><code>06</code> — currently learning: a direction, not a score</sub>

<img src="assets/roadmap.svg" width="100%" alt="Learning roadmap, no percentages: frontend craft; reliable backend APIs; database design and SQL; software architecture fundamentals; Odoo and ERP concepts; testing and engineering practice.">

<img src="assets/divider.svg" width="100%" alt="">

## Activity

<sub><code>07</code> — real public data, redrawn daily by a GitHub Action</sub>

<img src="assets/activity.svg" width="100%" alt="GitHub contribution calendar for the last twelve months.">

<!--
  OPTIONAL: most-used languages from github-readme-stats (public instance; rate-limited at times,
  self-hosting on Vercel is the reliable option). Replace YOUR_USERNAME, then remove these comment markers.

<p align="center">
  <img height="150" alt="Most used languages in my public repositories" src="https://github-readme-stats.vercel.app/api/top-langs/?username=YOUR_USERNAME&layout=compact&hide_border=true&bg_color=0A0E1F&title_color=B7A5FF&text_color=BFC3EA">
</p>
-->

<img src="assets/divider.svg" width="100%" alt="">

## Connect

<sub><code>08</code> — the response you were waiting for</sub>

I'm looking for a junior software development role where I can learn from a strong team and contribute from the first week.
If that sounds like your team — or you just want to talk about schemas — I'd like to hear from you.

**Email** · [ADD PROFESSIONAL EMAIL] &nbsp;&nbsp; **LinkedIn** · [ADD LINKEDIN URL] &nbsp;&nbsp; **GitHub** · [github.com/Eng2b](https://github.com/Eng2b) &nbsp;&nbsp; **Portfolio** · [ADD PORTFOLIO URL — or delete]

<img src="assets/signoff.svg" width="100%" alt="HTTP/1.1 201 Created. Let's build something that works — and feels right. Sarai Soliman, IT Engineer.">
