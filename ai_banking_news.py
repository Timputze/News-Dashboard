import feedparser
import os
import pandas as pd 
from langdetect import detect, LangDetectException
 
# List of RSS feeds from reputable news sources
rss_feeds = [
   RSS_FEEDS = {

    # --- German Federal Government & Authorities (Primary Sources) ---
    "DE_Federal_Ministries_and_Agencies": [
        "https://www.bmi.bund.de/SiteGlobals/Functions/RSSFeed/RSSPresse/RSSPresse.xml",  # BMI / BMDS
        "https://www.bmi.bund.de/SiteGlobals/Functions/RSSFeed/RSSNews/RSSNews.xml",
        "https://www.bsi.bund.de/SiteGlobals/Functions/RSSFeed/RSSNews/RSSNews.xml",      # BSI
        "https://www.bsi.bund.de/SiteGlobals/Functions/RSSFeed/RSSPresse/RSSPresse.xml",
        "https://www.bva.bund.de/SiteGlobals/Functions/RSSFeed/RSSNews/RSSNews.xml",      # BVA
        "https://www.bmwk.de/SiteGlobals/Functions/RSSFeed/RSSNews/RSSNews.xml",          # BMWK / BMWE
        "https://www.destatis.de/DE/Presse/RSS/pressemitteilungen.xml"                   # StBA
    ],

    # --- EU Digital Identity, eIDAS 2.0, Wallet, Regulation ---
    "EU_Digital_Identity_and_Regulation": [
        "https://digital-strategy.ec.europa.eu/en/news/rss.xml",
        "https://ec.europa.eu/commission/presscorner/api/rss?language=en",
        "https://www.euractiv.com/section/digital/feed/",
        "https://www.euractiv.de/feed/",
        "https://www.politico.eu/rss/technology/",
        "https://www.politico.eu/rss/policy/"
    ],

    # --- German Politics & Digital Society (Quality Journalism) ---
    "DE_Politics_and_Digital_Policy": [
        "https://www.tagesschau.de/xml/rss2",
        "https://www.spiegel.de/politik/index.rss",
        "https://www.spiegel.de/netzwelt/index.rss",
        "https://www.faz.net/rss/aktuell/politik/",
        "https://www.faz.net/rss/aktuell/wirtschaft/digitalwirtschaft/",
        "https://www.handelsblatt.com/contentexport/feed/politik",
        "https://www.handelsblatt.com/contentexport/feed/inside-digital",
        "https://netzpolitik.org/feed/"
    ],

    # --- Cybersecurity, Trust Infrastructure, GovTech ---
    "Cybersecurity_and_GovTech": [
        "https://www.heise.de/rss/heise-security-atom.xml",
        "https://www.heise.de/rss/heise-atom.xml",
        "https://www.reuters.com/technology/rss",
        "https://www.reuters.com/world/europe/rss"
    ],

    # --- International Context (Business & Regulation Impact) ---
    "International_Business_and_Regulation_Context": [
        "https://www.ft.com/technology?format=rss",
        "https://www.ft.com/europe?format=rss",
        "https://www.axios.com/rss/technology"
    ],

    # --- Targeted Google News Queries (High Signal, Low Noise) ---
    "Targeted_Search_Feeds_eIDAS_Wallet": [
        "https://news.google.com/rss/search?q=eIDAS+2.0+European+Digital+Identity+Wallet&hl=en-DE&gl=DE&ceid=DE:en",
        "https://news.google.com/rss/search?q=Bundesministerium+digitale+Identität+Wallet&hl=de&gl=DE&ceid=DE:de",
        "https://news.google.com/rss/search?q=BSI+digitale+Identitäten+Wallet&hl=de&gl=DE&ceid=DE:de"
    ]
}

]

# Keywords to filter relevant articles
keywords = [
    "ai", "artificial intelligence", "banking", "fintech", "machine learning",
    "ai banking", "ai in finance", "artificial intelligence in banking", "fintech ai",
    "LLM", "GPT", "Meta", "Microsoft", "OpenAI", "Sam Altman", "Agentic AI",
    "Generative AI", "AI tools", "AI applications in banking", "AI trends in finance"
]

# Compute a relevance score based on keyword frequency
def compute_relevance(title, summary, keywords):
    text = (title + " " + summary).lower()
    return sum(text.count(kw.lower()) for kw in keywords)

# Detect if the article is in English or German
def is_english_or_german(text):
    try:
        lang = detect(text)
        return lang in ["en", "de"]
    except LangDetectException:
        return False

# Fetch and sort relevant news
def fetch_relevant_news(feeds, keywords):
    relevant_articles = []

    for feed_url in feeds:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            title = entry.title
            summary = entry.get("summary", "")
            if not is_english_or_german(title + " " + summary):
                continue
            score = compute_relevance(title, summary, keywords)
            if score > 0:
                relevant_articles.append({
                    "title": title,
                    "link": entry.link,
                    "source": feed.feed.get("title", "Unknown Source"),
                    "score": score
                })

    # Sort and limit to top 50
    relevant_articles.sort(key=lambda x: x["score"], reverse=True)
    return relevant_articles[:50]

# Fetch and display the news
articles = fetch_relevant_news(rss_feeds, keywords)

if articles:
    print("🔍 Top 50 AI + Banking News Articles (English/German, Sorted by Relevance):\n")
    for i, article in enumerate(articles, 1):
        print(f"{i}. {article['title']} ({article['source']})")
        print(f"   {article['link']}\n")
else:
    print("No relevant articles found.")

df = pd.DataFrame(articles)
df.to_csv("ai_banking_news.csv", index=False)

output_path = os.path.abspath("C:/Users/tputze/Downloads/Python/ai_banking_news.csv")
df.to_csv(output_path, index=False)
print(f"News saved to: {output_path}")
