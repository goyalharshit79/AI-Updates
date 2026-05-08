#!/usr/bin/env python3
"""Generate sitemap.xml and feed.xml from posts/index.json.

Run before deploy. Idempotent — overwrites the two files at repo root.
"""
import json
import os
from datetime import datetime, timezone
from email.utils import format_datetime
from html import escape
from pathlib import Path

SITE_URL = "https://goyalharshit79.github.io/AI-Updates"
ROOT = Path(__file__).resolve().parent.parent
INDEX_JSON = ROOT / "posts" / "index.json"


def load_posts():
    with open(INDEX_JSON, encoding="utf-8") as f:
        return sorted(json.load(f).get("posts", []), key=lambda p: p.get("date", ""), reverse=True)


def write_sitemap(posts):
    today = datetime.now(timezone.utc).date().isoformat()
    static_urls = [
        ("/", today, "1.0", "daily"),
        ("/about.html", today, "0.5", "monthly"),
        ("/disclosure.html", today, "0.3", "yearly"),
        ("/privacy.html", today, "0.3", "yearly"),
    ]
    parts = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for path, lm, prio, freq in static_urls:
        parts.append(
            f"  <url><loc>{SITE_URL}{path}</loc><lastmod>{lm}</lastmod>"
            f"<changefreq>{freq}</changefreq><priority>{prio}</priority></url>"
        )
    for p in posts:
        slug = p.get("slug", "")
        date = p.get("date", today)
        parts.append(
            f"  <url><loc>{SITE_URL}/post.html?slug={slug}</loc>"
            f"<lastmod>{date}</lastmod><changefreq>monthly</changefreq>"
            f"<priority>0.8</priority></url>"
        )
    parts.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(parts) + "\n", encoding="utf-8")


def write_feed(posts):
    now = datetime.now(timezone.utc)
    items = []
    for p in posts[:30]:
        slug = p.get("slug", "")
        title = escape(p.get("title", ""))
        excerpt = escape(p.get("excerpt", ""))
        link = f"{SITE_URL}/post.html?slug={slug}"
        try:
            pub = datetime.fromisoformat(p.get("date", "")).replace(tzinfo=timezone.utc)
        except ValueError:
            pub = now
        category = escape(p.get("category", "News"))
        items.append(f"""    <item>
      <title>{title}</title>
      <link>{link}</link>
      <guid isPermaLink="true">{link}</guid>
      <pubDate>{format_datetime(pub)}</pubDate>
      <category>{category}</category>
      <description>{excerpt}</description>
    </item>""")
    feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>AI Pulse</title>
    <link>{SITE_URL}/</link>
    <atom:link href="{SITE_URL}/feed.xml" rel="self" type="application/rss+xml" />
    <description>Daily AI intelligence: model releases, tools, research, industry news.</description>
    <language>en-us</language>
    <lastBuildDate>{format_datetime(now)}</lastBuildDate>
{chr(10).join(items)}
  </channel>
</rss>
"""
    (ROOT / "feed.xml").write_text(feed, encoding="utf-8")


if __name__ == "__main__":
    posts = load_posts()
    write_sitemap(posts)
    write_feed(posts)
    print(f"Generated sitemap.xml and feed.xml ({len(posts)} posts)")
