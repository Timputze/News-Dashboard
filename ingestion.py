# -*- coding: utf-8 -*-

import feedparser
import psycopg
from datetime import datetime, timedelta
from langdetect import detect, LangDetectException
import os

# =========================================================
# CONFIG
# =========================================================

DATABASE_URL = os.getenv("DATABASE_URL")

NOW = datetime.now()
CURRENT_YEAR = NOW.year

# =========================================================
# RSS FEEDS
# =========================================================

RSS_FEEDS = [
    "https://news.google.com/rss/search?q=eIDAS+Digital+Identity+Wallet&hl=en-DE&gl=DE&ceid=DE:en",
    "https://news.google.com/rss/search?q=European+Digital+Identity+Wallet&hl=en-DE&gl=DE&ceid=DE:en",
    "https://news.google.com/rss/search?q=digitale+Identit%C3%A4t+EU&hl=de&gl=DE&ceid=DE:de",

    "https://digital-strategy.ec.europa.eu/en/news/rss.xml",
    "https://ec.europa.eu/commission/presscorner/api/rss?language=en",
    "https://www.enisa.europa.eu/newsroom/news/RSS",
    "https://www.consilium.europa.eu/en/press/press-releases/rss.xml",

    "https://www.bmi.bund.de/SiteGlobals/Functions/RSSFeed/RSSNews/RSSNews.xml",
    "https://www.bsi.bund.de/SiteGlobals/Functions/RSSFeed/RSSNews/RSSNews.xml",
    "https://www.bmwk.de/SiteGlobals/Functions/RSSFeed/RSSNews/RSSNews.xml",

    "https://www.govtech.com/rss",
    "https://www.oeffentliche-it.de/rss.xml",

    "https://www.euractiv.com/section/digital/feed/",
    "https://www.politico.eu/rss/digital/",
    "https://www.politico.eu/rss/technology/",
    "https://www.ft.com/europe?format=rss",

    "https://www.darkreading.com/rss_simple.asp",
    "https://www.infosecurity-magazine.com/rss/news/",

    "https://netzpolitik.org/feed/",
    "https://www.handelsblatt.com/contentexport/feed/inside-digital",

    "https://www.heise.de/newsticker/heise-atom.xml",
    "https://www.tagesspiegel.de/rss",
    "https://www.faz.net/rss/aktuell/",
    "https://www.chip.de/rss",
    "https://www.giga.de/rss",
    "https://www.t-online.de/rss",
    "https://www.express.de/rss",

    "https://www.bitkom.org/service/rss-feed",

    "https://rss.app/feeds/SU0226316SotG2Ur.xml",
    "https://rss.app/feeds/mIvPBhCGQ8s8bsfc.xml",
    "https://rss.app/feeds/rbQ9pA1KN68TwFWE.xml",
    "https://rss.app/feeds/w42SPeuQZ5xC3Lfb.xml",
    "https://rss.app/feeds/QUeVxZ8GUKRvSwj9.xml"
]

# =========================================================
# KEYWORDS
# =========================================================

KEYWORDS = [
    "eidas", "eudi", "wallet", "digital identity",
    "digitale identität", "ozg", "bsi", "pki",
    "age verification", "altersverifikation",
    "trust", "credential", "adoption", "interoperability"
]

# =========================================================
# HELPERS
# =========================================================

def is_en_or_de(text):
    try:
        return detect(text) in ("en", "de")
    except LangDetectException:
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

# =========================================================
# INGESTION
# =========================================================

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

# =========================================================
# DB WRITE
# =========================================================

with psycopg.connect(DATABASE_URL) as conn:
    with conn.cursor() as cur:

        # 1. Ensure table exists
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

        # ✅ 2. CLEANUP (robust, DB-side)
        cur.execute("""
            DELETE FROM news_articles
            WHERE published_at < NOW() - INTERVAL '30 days'
        """)

        deleted_rows = cur.rowcount

        # 3. Insert new articles
        inserted = 0

        for a in articles:
            cur.execute("""
                INSERT INTO news_articles
                (title, link, source, score, published_at, load_timestamp)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (link) DO NOTHING
            """, (
                a["title"],
                a["link"],
                a["source"],
                a["score"],
                a["published_at"],
                a["load_timestamp"]
            ))

            if cur.rowcount > 0:
                inserted += 1

        conn.commit()

print(f"Inserted {inserted} new articles")
print(f"Deleted {deleted_rows} old articles")
