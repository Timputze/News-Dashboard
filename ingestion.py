# -*- coding: utf-8 -*-

import feedparser
import psycopg
from datetime import datetime, timedelta
from langdetect import detect, LangDetectException
import os

DATABASE_URL = os.getenv("DATABASE_URL")

NOW = datetime.utcnow()
CUTOFF_DAYS = 30
CUTOFF_DATE = NOW - timedelta(days=CUTOFF_DAYS)
CURRENT_YEAR = NOW.year

# FEEDS
RSS_FEEDS = [
    # LBBW
    "https://www.lbbw-am.de/news/",
    "https://www.lbbw.de/group/news-and-service/media-center/media-center/media-center_7vvkby89r_e.html",

    # BA
    "https://www.arbeitsagentur.de/presse",
    "https://www.arbeitsagentur.de/en/press/press-archive",

    # BMW
    "https://www.press.bmwgroup.com/global",
    "http://feeds.feedburner.com/BmwBlog",

    # Daimler Truck
    "https://www.daimlertruck.com/en/newsroom",
    "http://www.daimler.igm.de/feed/news.xml",

    # E.ON
    "https://news.eonenergy.com/news/",
    "https://www.eon.com/en/about-us/media/press-release.html",

    # Aldi
    "https://corporate.aldi.us/newsroom",
    "https://www.aldipresscentre.co.uk/",

    # Capgemini
    "https://capgemini.com/feed",
    "https://www.capgemini.com/news/press-releases/",

    # ZF
    "https://press.zf.com",

    # General
    "https://feeds.reuters.com/reuters/businessNews",
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://www.handelsblatt.com/contentexport/feed/schlagzeilen",
]

# =========================
# KEYWORDS
# =========================

KEYWORDS = [
    "enterprise model",
    "operating model",
    "business model",
    "target operating model",
    "growth strategy",
    "market expansion",
    "cost optimization",
    "efficiency",
    "productivity",
    "digital transformation",
    "AI strategy",
    "AI",
    "supply chain",
    "logistics",
    "margin optimization",
    "organizational design",
    "governance",
    "service delivery model",
    "kpi",
    "performance",
]

# =========================
# HELPERS
# =========================

def is_en_or_de(text):
    try:
        return detect(text) in ("en", "de")
    except:
        return True

def relevance_score(text):
    text = text.lower()
    return sum(text.count(k) for k in KEYWORDS)

def extract_published_datetime(entry):
    if entry.get("published_parsed"):
        return datetime(*entry.published_parsed[:6])
    if entry.get("updated_parsed"):
        return datetime(*entry.updated_parsed[:6])
    return None

# =========================
# INGESTION
# =========================

articles = []

for feed_url in RSS_FEEDS:
    feed = feedparser.parse(feed_url)

    for entry in feed.entries:
        title = entry.get("title", "")
        summary = entry.get("summary", "")
        text = f"{title} {summary}"

        if not is_en_or_de(text):
            continue

        score = relevance_score(text)
        if score == 0:
            continue

        published_at = extract_published_datetime(entry)
        if not published_at:
            continue

        if published_at < CUTOFF_DATE:
            continue

        if published_at.year < CURRENT_YEAR:
            continue

        articles.append({
            "title": title,
            "link": entry.get("link", ""),
            "source": feed.feed.get("title", "Unknown"),
            "score": score,
            "published_at": published_at,
            "load_timestamp": NOW
        })

# =========================
# DB WRITE
# =========================

with psycopg.connect(DATABASE_URL) as conn:
    with conn.cursor() as cur:

        cur.execute("""
            CREATE TABLE IF NOT EXISTS news_articles (
                id SERIAL PRIMARY KEY,
                title TEXT,
                link TEXT UNIQUE,
                source TEXT,
                score INT,
                published_at TIMESTAMP NOT NULL,
                load_timestamp TIMESTAMP
            )
        """)

        # CLEANUP
        cur.execute("""
            DELETE FROM news_articles
            WHERE published_at < (CURRENT_TIMESTAMP - INTERVAL '30 days')::timestamp
        """)

        deleted = cur.rowcount
        inserted = 0

        for a in articles:
            cur.execute("""
                INSERT INTO news_articles
                (title, link, source, score, published_at, load_timestamp)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (link) DO NOTHING
            """, (
                a["title"], a["link"], a["source"],
                a["score"], a["published_at"], a["load_timestamp"]
            ))

            if cur.rowcount > 0:
                inserted += 1

        conn.commit()

print(f"Inserted {inserted} new articles")
print(f"Deleted {deleted} old articles")