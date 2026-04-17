# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**AI Pulse** is a fully static AI news blog hosted on GitHub Pages. It has no build step — all files are served directly. The site is managed by an OpenClaw agent that adds new posts; Claude Code handles structural changes and new feature development.

## Commands

```bash
# No build process. Serve locally for development:
python -m http.server 8080
# or
npx serve .
```

The GitHub Actions workflow (`.github/workflows/deploy.yml`) auto-deploys to GitHub Pages on every push to `main`.

## Architecture

**Static-only, JS-rendered**: `index.html` and `post.html` are static shells. JavaScript fetches `posts/index.json` (post manifest) at runtime and dynamically renders cards. Individual post pages fetch the `.md` file and render it via `marked.js` (CDN).

**`posts/index.json`** — The single source of truth for what posts exist. Every `.md` file in `posts/` must have a corresponding entry here. The JS does not auto-discover files.

**`affiliates.json`** — Sidebar affiliate links. Loaded by `app.js` at runtime. Edit to add/update affiliate URLs. Split into `category: "Tools"` (AI tools section) and any other value (Learn AI section).

**`assets/js/app.js`** — Homepage: canvas animation, post card rendering, category filtering, search overlay, affiliate loading, stats.

**`assets/js/post.js`** — Post page: frontmatter parsing, markdown rendering, TOC generation, reading progress bar, related posts.

**`assets/css/style.css`** — Full design system. Uses CSS custom properties (`--void`, `--primary`, `--accent`, etc.) defined in `:root`. Purple/violet dark theme with glassmorphism and particle canvas background.

## Post Format

Posts are markdown files in `posts/` with YAML frontmatter:

```markdown
---
title: "Post Title"
date: "YYYY-MM-DD"
category: "Models"
tags: ["Tag1", "Tag2"]
excerpt: "One sentence shown on cards."
readTime: "4 min"
featured: false
---

Content here...
```

Categories: `Models` | `Tools` | `Research` | `Industry` | `News`

## OpenClaw Agent

The day-to-day content management is handled by an OpenClaw agent following `AGENT.md`. That file contains complete instructions for adding posts and updating affiliate links. Claude Code should not add content posts — focus on structural/design changes when asked.

## Key Notes

- `.nojekyll` in root prevents GitHub Pages from running Jekyll processing
- `marked.js` is loaded from CDN in `post.html` only — not available on the index page
- The neural network canvas uses `requestAnimationFrame` and scales particle count to `window.innerWidth * window.innerHeight / 13000`
- All color tokens are in `style.css :root` — change the theme by editing those variables
- No `package.json`, no `node_modules`, no build tooling — pure HTML/CSS/JS
