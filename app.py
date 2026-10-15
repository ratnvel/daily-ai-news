import os
import re
import html
import feedparser
import requests
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

FEEDS = [
    ("Google News India - AI", "https://news.google.com/rss/search?q=AI+technology+India&hl=en-IN&gl=IN&ceid=IN:en"),
    ("Google News India - Technology", "https://news.google.com/rss/search?q=technology+India&hl=en-IN&gl=IN&ceid=IN:en"),
    ("Google News India - Business", "https://news.google.com/rss/search?q=startups+business+India&hl=en-IN&gl=IN&ceid=IN:en"),
]

OUT_DIR = "output"
MAX_PER_FEED = int(os.getenv("MAX_PER_FEED", "5"))
WP_URL = os.getenv("WP_URL", "").rstrip("/")
WP_USERNAME = os.getenv("WP_USERNAME", "")
WP_APP_PASSWORD = os.getenv("WP_APP_PASSWORD", "")
AUTO_PUBLISH = os.getenv("AUTO_PUBLISH", "false").lower() == "true"

def clean(s):
    s = html.unescape(re.sub(r"<[^>]+>", " ", s or ""))
    return re.sub(r"\s+", " ", s).strip()

def parse_date(entry):
    try:
        return parsedate_to_datetime(entry.get("published", "")).astimezone(timezone.utc)
    except Exception:
        try:
            return datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
        except Exception:
            return None

def collect():
    items, seen = [], set()
    for category, url in FEEDS:
        feed = feedparser.parse(url)
        for e in feed.entries[:MAX_PER_FEED]:
            link = e.get("link", "")
            title = clean(e.get("title", ""))
            summary = clean(e.get("summary", e.get("description", "")))
            key = link or title.lower()
            if not title or key in seen:
                continue
            seen.add(key)
            items.append({
                "category": category,
                "title": title,
                "summary": summary[:700],
                "link": link,
                "published": parse_date(e)
            })
    items.sort(key=lambda x: x["published"] or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
    return items

def make_article(items):
    today = datetime.now().strftime("%d %B %Y")
    lines = [
        f"# India AI & Technology News Digest — {today}",
        "",
        "> This is an automated news roundup. Read the original sources before relying on a claim. Headlines and short descriptions are attributed to their publishers; this digest does not reproduce full articles.",
        "",
    ]
    for category in sorted(set(x["category"] for x in items)):
        lines += [f"## {category}", ""]
        for x in [z for z in items if z["category"] == category]:
            lines += [f"### {x['title']}", ""]
            if x["summary"]:
                lines += [x["summary"], ""]
            if x["link"]:
                lines += [f"Source: {x['link']}", ""]
    lines += ["## Editorial note", "", "This digest was generated from public RSS feeds. Automated collection can contain errors, duplicates, or incomplete context. Verify important details and add original analysis before publishing commercially.", ""]
    return "\n".join(lines)

def publish_to_wordpress(title, content):
    if not (WP_URL and WP_USERNAME and WP_APP_PASSWORD):
        raise RuntimeError("WordPress credentials are missing. Set WP_URL, WP_USERNAME and WP_APP_PASSWORD.")
    endpoint = f"{WP_URL}/wp-json/wp/v2/posts"
    status = "publish" if AUTO_PUBLISH else "draft"
    r = requests.post(
        endpoint,
        auth=(WP_USERNAME, WP_APP_PASSWORD),
        json={"title": title, "content": content.replace("\n", "<br>"), "status": status},
        timeout=30,
    )
    r.raise_for_status()
    return r.json().get("link", "(post created)")

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    items = collect()
    if not items:
        raise SystemExit("No RSS items retrieved. Check internet or try again later.")
    content = make_article(items)
    stamp = datetime.now().strftime("%Y-%m-%d")
    path = os.path.join(OUT_DIR, f"news-digest-{stamp}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Saved {len(items)} stories to {path}")
    if WP_URL and WP_USERNAME and WP_APP_PASSWORD:
        title = f"India AI & Technology News Digest — {datetime.now().strftime('%d %B %Y')}"
        try:
            print("WordPress result:", publish_to_wordpress(title, content))
        except Exception as ex:
            print("WordPress publishing failed:", ex)
    else:
        print("WordPress not configured; generated a local Markdown draft only.")

if __name__ == "__main__":
    main()
