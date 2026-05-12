# -*- coding: utf-8 -*-

import feedparser
import psycopg
from datetime import datetime, timedelta
from langdetect import detect, LangDetectException
import os

# =========================================================
# CONFIG
# =========================================================

DB_CONFIG = os.getenv("DATABASE_URL")

NOW = datetime.now()
CUTOFF_DAYS = 30
CUTOFF_DATE = NOW - timedelta(days=CUTOFF_DAYS)
CURRENT_YEAR = NOW.year

# =========================================================
# RSS FEEDS
# =========================================================

RSS_FEEDS = [
    # --- Google News (gezielte Suche) ---
    "https://news.google.com/rss/search?q=eIDAS+Digital+Identity+Wallet&hl=en-DE&gl=DE&ceid=DE:en",
    "https://news.google.com/rss/search?q=European+Digital+Identity+Wallet&hl=en-DE&gl=DE&ceid=DE:en",
    "https://news.google.com/rss/search?q=digitale+Identit%C3%A4t+EU&hl=de&gl=DE&ceid=DE:de",

    # --- EU Institutions & Regulators (PRIMÄRQUELLEN) ---
    "https://digital-strategy.ec.europa.eu/en/news/rss.xml",
    "https://ec.europa.eu/commission/presscorner/api/rss?language=en",
    "https://www.enisa.europa.eu/newsroom/news/RSS",
    "https://www.consilium.europa.eu/en/press/press-releases/rss.xml",

    # --- German federal level ---
    "https://www.bmi.bund.de/SiteGlobals/Functions/RSSFeed/RSSNews/RSSNews.xml",
    "https://www.bsi.bund.de/SiteGlobals/Functions/RSSFeed/RSSNews/RSSNews.xml",
    "https://www.bmwk.de/SiteGlobals/Functions/RSSFeed/RSSNews/RSSNews.xml",

    # --- GovTech / Administration ---
    "https://www.govtech.com/rss",
    "https://www.oeffentliche-it.de/rss.xml",

    # --- High-signal EU policy media ---
    "https://www.euractiv.com/section/digital/feed/",
    "https://www.politico.eu/rss/digital/",
    "https://www.politico.eu/rss/technology/",
    "https://www.ft.com/europe?format=rss",

    # --- Cyber / identity specialists ---
    "https://www.darkreading.com/rss_simple.asp",
    "https://www.infosecurity-magazine.com/rss/news/",

    # --- German quality press (digital policy) ---
    "https://netzpolitik.org/feed/",
    "https://www.handelsblatt.com/contentexport/feed/inside-digital",

       # --- German mainstream & tech press (explicitly cited) ---
    "https://www.heise.de/newsticker/heise-atom.xml",          # heise.de
    "https://www.tagesspiegel.de/rss",                         # tagesspiegel.de / background
    "https://www.faz.net/rss/aktuell/",                        # faz.net
    "https://www.chip.de/rss",                                 # chip.de
    "https://www.giga.de/rss",                                 # giga.de
    "https://www.t-online.de/rss",                             # t-online.de
    "https://www.express.de/rss",                              # express.de / boerse-express

    # --- Industry & associations ---
    "https://www.bitkom.org/service/rss-feed",                 # Bitkom press releases

    #--- Linkedin feeds (via RSS.app) ---
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

    # =====================================================
    # Core EUDI / eIDAS concepts
    # =====================================================
    "eidas",
    "eidas 2.0",
    "eudi",
    "eudi wallet",
    "european digital identity",
    "european digital identity wallet",
    "digital identity wallet",
    "digitale identität",
    "digitale identität eu",
    "eu digital identity",

    # =====================================================
    # PID / identification / person data
    # =====================================================
    "pid",
    "personal identification document",
    "personal identity data",
    "identity proofing",
    "identity issuance",
    "pid issuance",
    "pid credential",
    "pid-like credential",

    # =====================================================
    # Wallet, credentials & attributes
    # =====================================================
    "wallet",
    "identity wallet",
    "verifiable credentials",
    "verifiable credential",
    "digital credentials",
    "electronic attribute",
    "attribute certificate",
    "electronic attribute certificate",
    "qualified electronic attribute",
    "qualified attribute certificate",

    # =====================================================
    # Trust, assurance & authenticity
    # =====================================================
    "trust level",
    "assurance level",
    "level of assurance",
    "loa high",
    "high assurance",
    "high trust",
    "trust level high",
    "vertrauensniveau",
    "vertrauensniveau hoch",
    "authentic source",
    "authentic source registry",
    "authentische quelle",
    "trusted source",
    "trusted issuer",
    "authoritative source",
    "authoritative registry",

    # =====================================================
    # Signatures, trust services, QEA / QES
    # =====================================================
    "qualified electronic signature",
    "qualified electronic seal",
    "qualified trust service",
    "qualified trust service provider",
    "qes",
    "qea",
    "qualified electronic attestation",
    "trust services regulation",

    # =====================================================
    # Onboarding, PIN, lifecycle, usability
    # =====================================================
    "onboarding",
    "wallet onboarding",
    "low threshold onboarding",
    "user journey",
    "eid pin",
    "einmal-pin",
    "one-time pin",
    "pin reset",
    "pin rücksetzung",
    "wallet code",
    "wallet sperrcode",
    "wallet recovery",
    "credential recovery",

    # =====================================================
    # Public sector / administration context
    # =====================================================
    "onlinezugangsgesetz",
    "ozg",
    "ozg 2.0",
    "registermodernisierung",
    "once only principle",
    "once-only principle",
    "verwaltungsdigitalisierung",
    "digitale souveränität",
    "bsi",
    "bundesministerium des innern",
    "bitkom",

    # =====================================================
    # Security / architecture (high-signal only)
    # =====================================================
    "pki",
    "public key infrastructure",
    "secure element",
    "hardware security module",
    "selective disclosure",
    "zero trust identity",

    # =====================================================
    # Adoption, readiness & rollout (very prominent)
    # =====================================================
    "activation strategy",
    "activation campaign",
    "eID activation",
    "online id function",
    "online-id function",
    "pin chaos",
    "pin problem",
    "readiness gap",
    "wallet readiness",
    "low adoption",
    "adoption barrier",

    # =====================================================
    # Age verification & Mini-Wallet
    # =====================================================
    "age verification",
    "age-verification",
    "age verification app",
    "mini-wallet",
    "mini wallet",
    "age verification wallet",

    # =====================================================
    # Media framing / problem statements
    # =====================================================
    "identity sprawl",
    "fragmented identity",
    "fragmented identity systems",
    "app jungle",
    "app zoo",
    "pin chaos",
    "lack of interoperability",

    # =====================================================
    # Trust, usability & acceptance (explicitly discussed)
    # =====================================================
    "user trust",
    "usability",
    "everyday usability",
    "interoperability",
    "privacy preserving",
    "selective data sharing",
    "encrypted local storage",

    # =====================================================
    # Strategic coupling & scope
    # =====================================================
    "digital euro",
    "cross-border identity",
    "eu-wide rollout",

    # =====================================================
    # Actors explicitly named
    # =====================================================
    "bundesdruckerei",
    "sprind",
    "youniqx",
    "t-systems",
    "eidas summit",

    # =====================================================
    # GERMAN EXTENSIONS
    # =====================================================

    # Core concepts
    "eidas verordnung",
    "eidas 2.0",
    "eudi wallet",
    "eu digitale identität",
    "eu identitätswallet",
    "digitale identität",
    "digitale identität eu",
    "digitale identitätsbörse",

    # Identity / PID
    "personenidentitätsdaten",
    "personenbezogene identitätsdaten",
    "identitätsprüfung",
    "identitätsnachweis",
    "identitätsausstellung",
    "ausstellung von identitätsdaten",

    # Wallet & credentials
    "digitale brieftasche",
    "identitätswallet",
    "nachweis",
    "digitale nachweise",
    "verifizierbare nachweise",
    "elektronische nachweise",
    "attributsnachweis",
    "elektronisches attribut",
    "qualifiziertes attribut",

    # Trust / assurance
    "vertrauensniveau",
    "vertrauensniveau hoch",
    "hohes vertrauensniveau",
    "vertrauensdienste",
    "vertrauenswürdige quelle",
    "authentische quelle",
    "vertrauenswürdiger aussteller",
    "hohe sicherheitsstufe",

    # Signatures / trust services
    "qualifizierte elektronische signatur",
    "qualifizierte elektronische signatur qes",
    "qualifizierte elektronische siegel",
    "qualifizierter vertrauensdiensteanbieter",
    "vertrauensdienst",
    "signaturgesetz",

    # Onboarding / usability
    "registrierung",
    "onboarding prozess",
    "nutzerführung",
    "pin",
    "pin zurücksetzen",
    "pin rücksetzung",
    "einmal pin",
    "sperrcode",
    "wiederherstellung",
    "zugangscode",

    # Public sector / admin
    "onlinezugangsgesetz",
    "ozg",
    "registermodernisierung",
    "once only prinzip",
    "verwaltungsdigitalisierung",
    "digitale souveränität",
    "bundesministerium des innern",
    "bundesamt für sicherheit in der informationstechnik",

    # Security / architecture
    "öffentliche schlüssel-infrastruktur",
    "pki",
    "sicheres element",
    "hardware sicherheitsmodul",
    "selektive offenlegung",
    "zero trust",
    "verschlüsselte speicherung",

    # Adoption / rollout
    "nutzung",
    "geringe nutzung",
    "niedrige adoption",
    "aktivierungsstrategie",
    "aktivierungskampagne",
    "bereitstellung",
    "einführung",
    "rollout",

    # Age verification
    "altersverifikation",
    "altersprüfung",
    "altersnachweis",
    "altersverifikations app",

    # Media framing
    "fragmentierte identität",
    "app dschungel",
    "app chaos",
    "interoperabilität fehlt",
    "mangelnde interoperabilität",

    # Usability / trust
    "benutzerfreundlichkeit",
    "alltagstauglichkeit",
    "nutzervertrauen",
    "datenschutzfreundlich",
    "datensparsamkeit",
    "selektive datenfreigabe",

    # Strategic context
    "digitaler euro",
    "grenzüberschreitende identität",
    "eu weite einführung",

    # Actors
    "bundesdruckerei",
    "t systems",
    "sprind",
    "youniqx"

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

# =========================================================
# DB WRITE (SQL Queries)
# =========================================================

with psycopg.connect(DB_CONFIG) as conn:
    with conn.cursor() as cur:

        # 1️ Ensure table exists
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

        # 2️ Enforce 30 day retention 

        cur.execute("""
            DELETE FROM news_articles
            WHERE published_at < %s
        """, (CUTOFF_DATE,))

        print(f"Deleted {cur.rowcount} old articles")


        # 3️ Insert new articles
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

        conn.commit()

print(f"Inserted {len(articles)} articles")
