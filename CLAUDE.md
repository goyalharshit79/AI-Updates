# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**AI Pulse** is a lightweight Python automation project that generates daily AI news/tools blog posts and publishes them via GitHub Actions. It requires no external Python dependencies (standard library only).

## Commands

```bash
# Run the post generator manually
python main.py

# Initialize the repository (one-time setup, creates GitHub repo via gh CLI)
bash init.sh
```

The GitHub Actions workflow (`.github/workflows/update.yml`) runs `python main.py` daily at midnight UTC and auto-commits the results.

## Architecture

**`main.py`** — Core entry point. The `generate_post()` function:
1. Creates a dated markdown post at `posts/{YYYY-MM-DD}-ai-tools.md`
2. Updates `index.html` to link to the latest post

**`index.html`** — Dark-themed Tailwind CSS landing page ("AI PULSE"). Currently contains hardcoded article entries; `main.py` updates it with the latest post link.

**`posts/`** — Output directory for generated markdown files. Two types: `ai-news.md` (curated news) and `ai-tools.md` (tool recommendations).

**`.github/workflows/update.yml`** — Requires `contents: write` permission to commit and push generated posts back to the repo.

## Key Notes

- Python 3.10+ required (as specified in the workflow)
- No `requirements.txt` — all imports (`json`, `os`, `datetime`) are standard library
- `init.sh` hardcodes a specific workspace path (`/home/harshit/.openclaw/workspace/ai-money-machine`) and uses the `gh` CLI — it's a one-time setup script, not for routine use
- There are no tests in this project
