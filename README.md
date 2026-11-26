# Vedra — Unified AI Search

Vedra is currently a Streamlit research prototype that combines an OpenAI-generated answer with optional SerpAPI web, image, video, and news discovery.

## Run locally

```bash
pip install -r requirements.txt
export OPENAI_API_KEY="..."
export SERPAPI_KEY="..." # optional; enables live web/media discovery
streamlit run vedra_app.py
```

For Streamlit Community Cloud, add `OPENAI_API_KEY` and optionally `SERPAPI_KEY` in the app's Secrets settings. Never commit credentials.

## Current data architecture

The current prototype is request/response based and does not persist user searches, accounts, source documents, or embeddings. A database is therefore not required for its present feature set.

A database becomes appropriate when Vedra adds persistent features such as:
- user accounts, saved searches, and preferences;
- an indexed document and source catalogue;
- ingestion jobs and processing status;
- document chunks and embeddings for retrieval-augmented generation (RAG).

At that stage, Supabase Postgres with pgvector is a reasonable option. The schema should be designed around documents, chunks, source provenance, ownership, and ingestion jobs—not the unrelated legacy `orders` and `sellers` tables currently present in the connected Supabase project.

## Privacy and provider disclosure

Search queries are sent to OpenAI for answer generation. If SerpAPI is configured, queries are also sent to SerpAPI for web and media discovery. The app does not currently store queries or answers in its own database. Provider-side processing is governed by each provider's terms and privacy settings.

## Quality and safety

- Web-grounded answers cite the returned search results and do not claim independent verification.
- If web search is unavailable, the UI labels the answer as not web-grounded.
- External URLs are restricted to HTTPS before rendering.
- API failures are reported without displaying raw exception details or secrets.
- Run helper tests with `python -m unittest discover -s tests`.
