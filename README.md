📰 Digital Identity News Dashboard
Overview
This project is an automated news aggregation and analysis tool focused on digital identity, including topics such as eIDAS, EUDI Wallet, and related EU policy developments.
It collects articles from a wide range of sources (EU institutions, German government, media, LinkedIn), filters them based on relevance, stores them in a PostgreSQL database, and visualizes them in an interactive dashboard using Streamlit.

🚀 Features
Automated RSS ingestion from 20+ high-quality sources
Keyword-based relevance scoring (EN + DE)
Language filtering (English & German)
30-day rolling data retention
PostgreSQL storage with deduplication
Interactive Streamlit dashboard:
Filter by source
Filter by relevance score
Browse latest articles

🏗️ Architecture
1.Ingestion Script
Fetches RSS feeds
Filters & scores articles
Writes to PostgreSQL
2.Database (Postgres)
Stores articles
Ensures uniqueness via URL
Maintains rolling 30-day window
3.Frontend (Streamlit)
Reads from database
Displays interactive dashboard
