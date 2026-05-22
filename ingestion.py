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
    # =========================
    # GOOGLE NEWS – CLIENT SPECIFIC
    # =========================

    # LBBW
    "https://news.google.com/rss/search?q=LBBW+bank&hl=en-DE&gl=DE&ceid=DE:en",

    # Bundesagentur für Arbeit
    "https://news.google.com/rss/search?q=Bundesagentur+für+Arbeit&hl=de&gl=DE&ceid=DE:de",

    # BMW
    "https://news.google.com/rss/search?q=BMW+strategy+company&hl=en-DE&gl=DE&ceid=DE:en",

    # Daimler Truck
    "https://news.google.com/rss/search?q=Daimler+Truck+strategy&hl=en-DE&gl=DE&ceid=DE:en",

    # E.ON
    "https://news.google.com/rss/search?q=E.ON+energy+strategy&hl=en-DE&gl=DE&ceid=DE:en",

    # Aldi
    "https://news.google.com/rss/search?q=Aldi+strategy+retail&hl=en-DE&gl=DE&ceid=DE:en",

    # Capgemini
    "https://news.google.com/rss/search?q=Capgemini+consulting+strategy&hl=en-DE&gl=DE&ceid=DE:en",

    # ZF
    "https://news.google.com/rss/search?q=ZF+Group+automotive+strategy&hl=en-DE&gl=DE&ceid=DE:en",

    # =========================
    # CLIENT DIRECT SOURCES
    # =========================
    "https://www.lbbw-am.de/news/",
    "https://www.arbeitsagentur.de/presse",
    "http://feeds.feedburner.com/BmwBlog",
    "http://www.daimler.igm.de/feed/news.xml",
    "https://news.eonenergy.com/news/",
    "https://www.aldipresscentre.co.uk/",
    "https://capgemini.com/feed",
    "https://press.zf.com",

    # =========================
    # BACKUP BUSINESS SOURCES
    # =========================
    "https://feeds.reuters.com/reuters/businessNews",
    "https://feeds.bbci.co.uk/news/business/rss.xml",
    "https://www.handelsblatt.com/contentexport/feed/schlagzeilen"
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