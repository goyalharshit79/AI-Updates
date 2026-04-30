#!/usr/bin/env python3
"""
Daily AI news post generator for AI Pulse blog.

Flow:
  1. Firecrawl searches for today's top AI news
  2. Gemini picks the best story and writes a full post
  3. Script creates the .md file and updates posts/index.json
  4. GitHub Actions commits and pushes (see .github/workflows/daily-post.yml)

Required env vars:
  FIRECRAWL_API_KEY
  GEMINI_API_KEY
"""

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from google import genai
from google.genai import types
from firecrawl import FirecrawlApp

REPO_ROOT = Path(__file__).parent.parent
POSTS_DIR = REPO_ROOT / "posts"
INDEX_FILE = POSTS_DIR / "index.json"

VALID_CATEGORIES = {"Models", "Tools", "Research", "Industry", "News"}

# Pages to scrape for AI news. Firecrawl returns clean markdown from each.
NEWS_URLS = [
    "https://techcrunch.com/category/artificial-intelligence/",
    "https://venturebeat.com/category/ai/",
    "https://www.theverge.com/ai-artificial-intelligence",
    "https://arstechnica.com/ai/",
    "https://www.artificialintelligence-news.com/",
]


# ---------------------------------------------------------------------------
# Step 1 — Gather raw news via Firecrawl (scrape known pages)
# ---------------------------------------------------------------------------

def gather_news(api_key: str) -> list[dict]:
    app = FirecrawlApp(api_key=api_key)
    results = []

    for url in NEWS_URLS:
        try:
            print(f"[firecrawl] scraping {url}")
            response = app.scrape_url(url, formats=["markdown"])

            # firecrawl-py v0: response is a dict with "markdown" key
            # firecrawl-py v1: response is a ScrapeResponse object
            if isinstance(response, dict):
                content = response.get("markdown") or response.get("content") or ""
                page_url = response.get("metadata", {}).get("sourceURL", url)
                title = response.get("metadata", {}).get("title", "")
            else:
                content = getattr(response, "markdown", None) or ""
                metadata = getattr(response, "metadata", None) or {}
                page_url = getattr(metadata, "source_url", None) or url
                title = getattr(metadata, "title", None) or ""

            if content:
                results.append({"url": page_url, "title": title, "markdown": content})
                print(f"[firecrawl] got {len(content)} chars from {url}")
            else:
                print(f"[firecrawl] empty response from {url}")

        except Exception as exc:
            print(f"[firecrawl] failed to scrape {url}: {exc}")

    print(f"[firecrawl] scraped {len(results)} pages total")
    return results


def format_news_for_prompt(items: list) -> str:
    parts = []
    for i, item in enumerate(items, 1):
        title = item.get("title", "")
        url = item.get("url", "")
        # Trim each page to 3000 chars so the prompt stays manageable
        body = (item.get("markdown") or "")[:3000]
        parts.append(f"[Source {i}] {title}\n{url}\n\n{body}")
    return "\n\n---\n\n".join(parts)


# ---------------------------------------------------------------------------
# Step 2 — Write the post with Gemini
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """\
You are the editor of AI Pulse, a blog for technically literate readers
covering AI news. Your job is to pick the single most newsworthy AI story
from the provided sources and write a high-quality blog post about it.

Prioritise (in order):
  1. New model releases with benchmark results
  2. Major open-source model drops
  3. Significant AI tool launches
  4. Funding rounds over $100M
  5. Regulatory/policy developments
  6. Research papers with clear real-world impact

Avoid: incremental updates, speculation without substance, duplicate coverage.

If no single story is strong enough, write a short roundup of the top 2-3 items.

Respond with ONLY a valid JSON object — no markdown fences, no commentary.
The JSON must have exactly these keys:

{
  "title":    string  (under 80 chars, sentence case, no ALL CAPS),
  "date":     string  (YYYY-MM-DD, the date of the actual news event),
  "category": string  (exactly one of: Models | Tools | Research | Industry | News),
  "tags":     array   (2-5 short specific strings, e.g. "OpenAI", "Gemini", "Reasoning"),
  "excerpt":  string  (100-180 chars, teaser — no spoilers, no full reveal),
  "readTime": string  (estimate based on ~200 wpm, e.g. "5 min"),
  "slug":     string  (YYYY-MM-DD- followed by short kebab-case topic, e.g. "2026-04-30-gemini-2-ultra"),
  "featured": boolean (true only if this is genuinely top-tier news),
  "body":     string  (the full post body in markdown — see structure below)
}

Body structure (use \\n for newlines inside the JSON string):

## [Compelling hook title]
Opening paragraph — what happened and why it matters.

## [Background title]
Brief context for readers unfamiliar with the topic.

## [Key Details title]
Specifics: benchmarks, features, pricing. Bold key numbers. Bullet lists for features.

## Why It Matters
Implications for developers, the industry, or the future of AI.

## What to Watch
One forward-looking paragraph or call to action.

---
Check out the AI tools in the sidebar to stay ahead of these developments.

Rules:
- Tone: authoritative, direct, factual. No hedging or filler phrases.
- Paragraphs: 3-5 sentences max.
- Only report what the sources actually say. Do not invent facts or numbers.
- Use present tense for current state, past tense for events that happened.
"""


def generate_post(api_key: str, news_text: str, today: str) -> dict:
    client = genai.Client(api_key=api_key)

    user_message = f"Today's date: {today}\n\nNEWS SOURCES:\n\n{news_text}"

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=user_message,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
            temperature=0.4,
        ),
    )

    raw = response.text.strip()

    # Strip accidental markdown fences just in case
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    post = json.loads(raw)
    return post


# ---------------------------------------------------------------------------
# Step 3 — Write files
# ---------------------------------------------------------------------------

def load_index() -> dict:
    with open(INDEX_FILE) as f:
        return json.load(f)


def save_index(data: dict) -> None:
    with open(INDEX_FILE, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def slug_exists(index_data: dict, slug: str) -> bool:
    return any(p["slug"] == slug for p in index_data["posts"])


def enforce_featured_limit(index_data: dict, new_featured: bool) -> dict:
    """Keep at most 3 featured posts. If new post is featured, unfeature the oldest."""
    if not new_featured:
        return index_data
    currently_featured = [p for p in index_data["posts"] if p.get("featured")]
    if len(currently_featured) >= 3:
        oldest = currently_featured[-1]
        for p in index_data["posts"]:
            if p["slug"] == oldest["slug"]:
                p["featured"] = False
        md_path = POSTS_DIR / f"{oldest['slug']}.md"
        if md_path.exists():
            content = md_path.read_text()
            content = re.sub(r"^featured: true", "featured: false", content, count=1, flags=re.MULTILINE)
            md_path.write_text(content)
        print(f"[index] unfeatured old post: {oldest['slug']}")
    return index_data


def write_markdown(post: dict) -> Path:
    slug = post["slug"]
    tags_json = json.dumps(post["tags"])
    featured = str(post.get("featured", False)).lower()

    frontmatter = (
        f'---\n'
        f'title: "{post["title"]}"\n'
        f'date: "{post["date"]}"\n'
        f'category: "{post["category"]}"\n'
        f'tags: {tags_json}\n'
        f'excerpt: "{post["excerpt"]}"\n'
        f'readTime: "{post["readTime"]}"\n'
        f'featured: {featured}\n'
        f'---\n\n'
    )

    md_path = POSTS_DIR / f"{slug}.md"
    md_path.write_text(frontmatter + post["body"].strip() + "\n")
    return md_path


def update_index(index_data: dict, post: dict) -> None:
    entry = {
        "slug":     post["slug"],
        "title":    post["title"],
        "date":     post["date"],
        "category": post["category"],
        "tags":     post["tags"],
        "excerpt":  post["excerpt"],
        "readTime": post["readTime"],
        "featured": post.get("featured", False),
    }
    index_data["posts"].insert(0, entry)
    save_index(index_data)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate(post: dict) -> list[str]:
    errors = []
    if not post.get("title") or len(post["title"]) > 80:
        errors.append("title missing or over 80 chars")
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", post.get("date", "")):
        errors.append("date not in YYYY-MM-DD format")
    if post.get("category") not in VALID_CATEGORIES:
        errors.append(f"category '{post.get('category')}' not in {VALID_CATEGORIES}")
    if not (2 <= len(post.get("tags", [])) <= 5):
        errors.append("tags must have 2-5 items")
    excerpt_len = len(post.get("excerpt", ""))
    if not (80 <= excerpt_len <= 200):
        errors.append(f"excerpt length {excerpt_len} not in 80-200 range")
    if not re.match(r"^\d{4}-\d{2}-\d{2}-.+$", post.get("slug", "")):
        errors.append("slug must start with YYYY-MM-DD-")
    if not post.get("body") or post["body"].count("##") < 3:
        errors.append("body must have at least 3 ## sections")
    return errors


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    firecrawl_key = os.environ.get("FIRECRAWL_API_KEY")
    gemini_key = os.environ.get("GEMINI_API_KEY")

    if not firecrawl_key:
        print("ERROR: FIRECRAWL_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    if not gemini_key:
        print("ERROR: GEMINI_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # 1. Gather news
    news_items = gather_news(firecrawl_key)
    if not news_items:
        print("ERROR: No news gathered from Firecrawl. Exiting.", file=sys.stderr)
        sys.exit(1)

    news_text = format_news_for_prompt(news_items)

    # 2. Generate post (retry once on parse failure)
    post = None
    for attempt in (1, 2):
        try:
            print(f"[gemini] generating post (attempt {attempt})...")
            post = generate_post(gemini_key, news_text, today)
            break
        except (json.JSONDecodeError, KeyError) as exc:
            print(f"[gemini] parse error on attempt {attempt}: {exc}", file=sys.stderr)
            if attempt == 2:
                sys.exit(1)

    # 3. Validate
    errors = validate(post)
    if errors:
        print(f"[validate] post failed validation:\n  " + "\n  ".join(errors), file=sys.stderr)
        sys.exit(1)

    # 4. Check for duplicate slug
    index_data = load_index()
    if slug_exists(index_data, post["slug"]):
        print(f"[index] slug '{post['slug']}' already exists — nothing to do.")
        sys.exit(0)

    # 5. Write files
    index_data = enforce_featured_limit(index_data, post.get("featured", False))
    md_path = write_markdown(post)
    print(f"[write] created {md_path.relative_to(REPO_ROOT)}")

    update_index(index_data, post)
    print(f"[index] added '{post['slug']}' to posts/index.json")

    print(f"\nDone. Post: {post['title']}")


if __name__ == "__main__":
    main()
