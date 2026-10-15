import os
import re
import html
import json
import feedparser
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

# मराठी बातम्यांसाठी RSS स्रोत
FEEDS = [
    (
        "AI आणि कृत्रिम बुद्धिमत्ता",
        "https://news.google.com/rss/search?q=AI+OR+%E0%A4%95%E0%A5%83%E0%A4%A4%E0%A5%8D%E0%A4%B0%E0%A4%BF%E0%A4%AE+%E0%A4%AC%E0%A5%81%E0%A4%A6%E0%A5%8D%E0%A4%A7%E0%A4%BF%E0%A4%AE%E0%A4%A4%E0%A5%8D%E0%A4%A4%E0%A4%BE&hl=mr-IN&gl=IN&ceid=IN:mr",
    ),
    (
        "तंत्रज्ञान",
        "https://news.google.com/rss/search?q=%E0%A4%A4%E0%A4%82%E0%A4%A4%E0%A5%8D%E0%A4%B0%E0%A4%9C%E0%A5%8D%E0%A4%9E%E0%A4%BE%E0%A4%A8&hl=mr-IN&gl=IN&ceid=IN:mr",
    ),
    (
        "भारत आणि स्टार्टअप",
        "https://news.google.com/rss/search?q=%E0%A4%AD%E0%A4%BE%E0%A4%B0%E0%A4%A4+%E0%A4%B8%E0%A5%8D%E0%A4%9F%E0%A4%BE%E0%A4%B0%E0%A5%8D%E0%A4%9F%E0%A4%85%E0%A4%AA&hl=mr-IN&gl=IN&ceid=IN:mr",
    ),
]

MAX_NEWS = 10


def clean_text(text):
    text = html.unescape(re.sub(r"<[^>]+>", " ", text or ""))
    return re.sub(r"\s+", " ", text).strip()


def parse_date(entry):
    try:
        return parsedate_to_datetime(
            entry.get("published", "")
        ).astimezone(timezone.utc)
    except Exception:
        try:
            return datetime(
                *entry.published_parsed[:6],
                tzinfo=timezone.utc
            )
        except Exception:
            return None


def collect_news():
    news = []
    seen_links = set()

    for category, feed_url in FEEDS:
        try:
            feed = feedparser.parse(feed_url)

            for entry in feed.entries:
                link = entry.get("link", "")
                title = clean_text(entry.get("title", ""))
                summary = clean_text(
                    entry.get("summary", entry.get("description", ""))
                )

                if not title or not link or link in seen_links:
                    continue

                seen_links.add(link)

                published = parse_date(entry)

                news.append({
                    "category": category,
                    "title": title,
                    "summary": summary[:500],
                    "source": entry.get("source", {}).get(
                        "title", category
                    ),
                    "link": link,
                    "published": (
                        published.isoformat() if published else ""
                    ),
                })

        except Exception as error:
            print(f"Feed error ({category}): {error}")

    news.sort(
        key=lambda item: item["published"],
        reverse=True
    )

    return news[:MAX_NEWS]


def save_news(news):
    # वेबसाइटच्या index.html ला हा JSON वाचता येईल.
    with open("news.json", "w", encoding="utf-8") as file:
        json.dump(
            news,
            file,
            ensure_ascii=False,
            indent=2
        )

    os.makedirs("output", exist_ok=True)

    today = datetime.now().strftime("%Y-%m-%d")
    markdown_path = f"output/news-digest-{today}.md"

    with open(markdown_path, "w", encoding="utf-8") as file:
        file.write(f"# दैनिक AI आणि तंत्रज्ञान बातम्या — {today}\n\n")

        for number, item in enumerate(news, start=1):
            file.write(f"## {number}. {item['title']}\n\n")
            file.write(f"**विभाग:** {item['category']}\n\n")

            if item["summary"]:
                file.write(f"{item['summary']}\n\n")

            file.write(f"[मूळ बातमी वाचा]({item['link']})\n\n")
            file.write("---\n\n")

    print(f"एकूण बातम्या: {len(news)}")
    print("वेबसाइट डेटा तयार: news.json")
    print(f"Markdown फाइल तयार: {markdown_path}")


def main():
    news = collect_news()

    if not news:
        raise SystemExit(
            "बातम्या मिळाल्या नाहीत. RSS स्रोत किंवा इंटरनेट तपासा."
        )

    save_news(news)


if __name__ == "__main__":
    main()
