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

RSS_FEEDS = [
    # =========================
    # GOOGLE NEWS – GERMAN (BMDS CORE)
    # =========================
    "https://news.google.com/rss/search?q=eIDAS&hl=de&gl=DE&ceid=DE:de",
    "https://news.google.com/rss/search?q=EUDI+Wallet&hl=de&gl=DE&ceid=DE:de",
    "https://news.google.com/rss/search?q=digitale+Identität+EU&hl=de&gl=DE&ceid=DE:de",
    "https://news.google.com/rss/search?q=Onlinezugangsgesetz+OZG&hl=de&gl=DE&ceid=DE:de",
    "https://news.google.com/rss/search?q=Altersverifikation+digital&hl=de&gl=DE&ceid=DE:de",
    "https://news.google.com/rss/search?q=BSI+IT-Sicherheit+Deutschland&hl=de&gl=DE&ceid=DE:de",

    # =========================
    # GOOGLE NEWS – ENGLISH (EU CONTEXT)
    # =========================
    "https://news.google.com/rss/search?q=European+Digital+Identity+Wallet&hl=en-DE&gl=DE&ceid=DE:en",
    "https://news.google.com/rss/search?q=digital+identity+EU+regulation&hl=en-DE&gl=DE&ceid=DE:en",

    # =========================
    # ORIGINAL BMDS SOURCES
    # =========================
    "https://digital-strategy.ec.europa.eu/en/news/rss.xml",
    "https://ec.europa.eu/commission/presscorner/api/rss?language=en",
    "https://www.enisa.europa.eu/newsroom/news/RSS",
    "https://www.consilium.europa.eu/en/press/press-releases/rss.xml",

    "https://www.bmi.bund.de/SiteGlobals/Functions/RSSFeed/RSSNews/RSSNews.xml",
    "https://www.bsi.bund.de/SiteGlobals/Functions/RSSFeed/RSSNews/RSSNews.xml",
    "https://www.bmwk.de/SiteGlobals/Functions/RSSFeed/RSSNews/RSSNews.xml",

    "https://netzpolitik.org/feed/",
    "https://www.handelsblatt.com/contentexport/feed/inside-digital",

    # =========================
    # MISC. SOURCES
    # =========================
    "https://www.european-identity.com/rss",
    "https://www.heise.de/newsticker/heise-atom.xml",
    "https://www.tagesspiegel.de/rss",
    "https://www.faz.net/rss/aktuell/",
    "https://www.chip.de/rss",
    "https://www.giga.de/rss",
    "https://www.t-online.de/rss",
    "https://www.express.de/rss",
    "https://www.bitkom.org/service/rss-feed",

    # =========================
    # LINKEDIN SOURCES
    # =========================
    "https://rss.app/feeds/SU0226316SotG2Ur.xml" # Official BMDS LinkedIn Page
]

# KEYWORDS
KEYWORDS = [
    "eidas",
    "eudi",
    "eudi wallet",
    "digital identity",
    "digitale identität",
    "identity wallet",

    "onlinezugangsgesetz",
    "ozg",
    "bsi",
    "registermodernisierung",

    "altersverifikation",
    "age verification",

    "trust services",
    "verifiable credentials",
    "electronic identity"
]


# =========================
# HELPERS
# =========================

def is_en_or_de(text):
    try:
        return detect(text) in ("en", "de")
    except:
        return True

def extract_keywords(text):
    text = text.lower()
    found = [k for k in KEYWORDS if k in text]
    return found

def relevance_score(found_keywords):
    return len(found_keywords)


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

        found_keywords = extract_keywords(text)
        score = relevance_score(found_keywords)

        if score < 2:
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
            "keywords": ", ".join(found_keywords),   # ✅ NEW
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
                keywords TEXT,
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
                (title, link, source, score, keywords, published_at, load_timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (link) DO NOTHING
            """, (
                a["title"], a["link"], a["source"],
                a["score"], a["keywords"], a["published_at"], a["load_timestamp"]
            ))

            if cur.rowcount > 0:
                inserted += 1

        conn.commit()

print(f"Inserted {inserted} new articles")
print(f"Deleted {deleted} old articles")