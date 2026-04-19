# AGENT.md — AI Pulse Operating Instructions

This file is the operating manual for the OpenClaw agent managing the AI Pulse blog at `goyalharshit79.github.io/AI-Updates`. Read this before making any changes to the repository.

---

## Your Job

You maintain this blog by:
1. Adding new blog posts about AI news, model releases, tools, and research
2. Keeping `posts/index.json` up to date (the manifest the site reads)
3. Updating affiliate links in `affiliates.json` when new URLs are provided
4. Never touching HTML, CSS, or JS unless explicitly instructed

---

## How to Add a New Post

### Step 1 — Create the markdown file

Create a file at: `posts/YYYY-MM-DD-short-slug.md`

Use this exact frontmatter template at the top of every file:

```
---
title: "Your Post Title Here"
date: "YYYY-MM-DD"
category: "Models"
tags: ["Tag1", "Tag2", "Tag3"]
excerpt: "One or two sentence summary. This appears on post cards and in search results."
readTime: "4 min"
featured: false
---

Your markdown content starts here...
```

**Frontmatter rules:**
- `title`: Keep under 80 characters. Sentence case, not ALL CAPS.
- `date`: ISO format `YYYY-MM-DD`. Use the actual date of the news, not today.
- `category`: Exactly one of: `Models` | `Tools` | `Research` | `Industry` | `News`
- `tags`: 2–5 tags. Short, specific. Examples: `"OpenAI"`, `"Claude 4"`, `"Cursor"`, `"Open Source"`
- `excerpt`: 1–2 sentences, 100–180 characters. No spoilers — this is a teaser.
- `readTime`: Estimate based on word count (~200 words/min). Format: `"X min"`
- `featured`: Set `true` for only the 3 most important recent posts. Featured posts appear in the top hero grid on the homepage. Unfeature older posts when adding new featured ones.

### Step 2 — Update the post manifest

Open `posts/index.json` and add your new post object to the **top** of the `posts` array (newest first).

```json
{
  "slug": "YYYY-MM-DD-your-short-slug",
  "title": "Your Post Title",
  "date": "YYYY-MM-DD",
  "category": "Models",
  "tags": ["Tag1", "Tag2", "Tag3"],
  "excerpt": "One or two sentence summary matching the frontmatter.",
  "readTime": "4 min",
  "featured": false
}
```

**Important**: The `slug` must exactly match the filename without `.md`. If your file is `posts/2026-01-15-gpt-5-launch.md`, the slug is `2026-01-15-gpt-5-launch`.

### Step 3 — Commit and push

```bash
git add posts/YYYY-MM-DD-your-slug.md posts/index.json
git commit -m "content: add post - Your Post Title"
git push
```

GitHub Actions will automatically deploy to GitHub Pages after push.

---

## Post Writing Guidelines

### Structure
Use this general structure for every post:
1. **Opening paragraph** — What happened and why it matters (hook)
2. **Background/What is it** — Brief context for readers unfamiliar with the topic
3. **Key details** — The specifics: benchmarks, features, architecture, pricing
4. **Why it matters** — Implications for developers, the industry, or the future
5. **What to watch** — Forward-looking point or call to action
6. **Closing line** — Optional affiliate nudge or CTA (see examples in existing posts)

### Tone
- Authoritative but accessible. Assume a technically literate reader, not a PhD.
- Direct. No unnecessary hedging or filler phrases.
- Factual. Don't speculate as fact. Clearly mark predictions as such.
- Present tense for current state, past tense for events that have happened.

### Markdown formatting
- Use `##` for main sections, `###` for subsections
- Use **bold** for key terms and important numbers
- Use bullet lists for feature enumerations; numbered lists for ordered steps
- Use `> blockquotes` for notable quotes from industry figures
- Keep paragraphs short (3–5 sentences). Long paragraphs discourage reading.
- End with `---` and a brief affiliate nudge sentence pointing to the sidebar

### What to write about
**Always newsworthy:**
- New model releases (GPT, Claude, Gemini, Llama, Mistral, etc.)
- Significant benchmark results or capability demonstrations
- Major AI tool launches (especially coding, productivity, creative)
- Funding rounds over $100M in AI
- Regulatory developments affecting AI use
- Open-source model releases with notable performance
- Research papers with clear real-world implications

**Generally avoid:**
- Incremental minor updates (e.g., GPT-4o gets slightly faster)
- Speculation without substance
- Duplicate coverage of events already posted

---

## Managing Featured Posts

At any time, exactly 0–3 posts should have `"featured": true` in `posts/index.json`. Featured posts appear in the prominent 3-column grid at the top of the homepage.

When adding a new featured post:
1. Set the new post's `"featured": true`
2. Find the oldest currently-featured post and change it to `"featured": false`
3. Update both the `.md` frontmatter file AND the `index.json` entry

---

## Updating Affiliate Links

All affiliate links are stored in `affiliates.json`. The site loads this file automatically — you never need to touch the HTML.

### Format
```json
{
  "id": "unique-id",
  "name": "Display Name",
  "description": "Short description under 60 chars",
  "url": "https://your-actual-affiliate-url",
  "icon": "🔤",
  "bg": "rgba(R,G,B,0.12)",
  "category": "Tools"
}
```

**`category`** determines which sidebar section it appears in:
- `"Tools"` → shows in "AI Tools" section
- Any other value → shows in "Learn AI" section

### To update a URL
Open `affiliates.json`, find the entry by `id`, replace the `url` value. That's it.

### To add a new affiliate
Add a new object to the `affiliates` array. Use a unique `id`. Suggested icon backgrounds:
- Purple tools: `rgba(139,92,246,0.12)`
- Cyan tools: `rgba(34,211,238,0.12)`
- Green tools: `rgba(16,185,129,0.12)`
- Pink tools: `rgba(236,72,153,0.12)`
- Amber (books/courses): `rgba(245,158,11,0.12)`

---

## File Structure Reference

```
/
├── index.html          ← Main page (DO NOT EDIT)
├── post.html           ← Post reader (DO NOT EDIT)
├── affiliates.json     ← Affiliate link config (edit to update links)
├── AGENT.md            ← This file
├── CLAUDE.md           ← Claude Code guidance
├── assets/
│   ├── css/style.css   ← Styles (DO NOT EDIT)
│   └── js/
│       ├── app.js      ← Homepage JS (DO NOT EDIT)
│       └── post.js     ← Post page JS (DO NOT EDIT)
└── posts/
    ├── index.json      ← Post manifest (EDIT to add posts)
    └── *.md            ← Individual post files (CREATE new ones)
```

---

## GitHub Actions Deployment

Deployment is fully automatic. Any push to `main` triggers the GitHub Actions workflow (`.github/workflows/deploy.yml`) which deploys to GitHub Pages. No manual steps needed after `git push`.

If deployment fails:
1. Check the Actions tab on GitHub for error details
2. Common issues: malformed JSON in `index.json`, broken frontmatter in `.md` files
3. Fix the issue, commit, and push again

---

## Quality Checklist Before Every Push

- [ ] Slug in `index.json` exactly matches the `.md` filename (without `.md`)
- [ ] `date` in frontmatter matches `date` in `index.json`
- [ ] `excerpt` is between 80–200 characters
- [ ] Category is one of the 5 allowed values
- [ ] Post has at least 3 sections with `##` headings
- [ ] No more than 3 posts have `"featured": true` in `index.json`
- [ ] `index.json` is valid JSON (no trailing commas)
