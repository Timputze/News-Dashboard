📰 Digital Identity News Dashboard

This project is an automated news intelligence tool focused on digital identity topics such as eIDAS, EUDI Wallet, and EU digital policy.
It collects articles from curated sources, filters them based on relevance, stores them in a PostgreSQL database, and presents them in an interactive Streamlit dashboard.


🚀 Features

Aggregates news from 20+ sources (EU, government, media, LinkedIn)
Keyword-based relevance scoring (English & German)
Automatic filtering of recent articles (last 30 days)
PostgreSQL database with deduplication
Interactive dashboard with:

Source filtering
Relevance filtering
Top articles view


🏗️ Architecture

1. Ingestion (ingestion.py)

Fetches RSS feeds
Filters by language (EN/DE)
Scores relevance via keywords
Stores results in PostgreSQL

2. Database (Postgres / Neon)

Stores articles
Ensures uniqueness (by link)
Maintains rolling data window

3. Frontend (app.py)

Loads data from database
Provides interactive dashboard via Streamlit


☁️ Deployment

The app is deployed via Streamlit Cloud.

Database hosted on Neon (PostgreSQL)
Secrets managed via environment variables


📊 Data Model

Table: news_articles

title
link (unique)
source
score
published_at
load_timestamp


💡 Future Improvements

Topic clustering / tagging
Weekly summary (“Top insights”)
Trend analysis
UI improvements


👤 Author

Tim Putze
Associate Consultant

📄 License
Internal / educational use
