import os
from urllib.parse import quote_plus

import requests
import streamlit as st
from openai import OpenAI

from vedra_utils import normalise_video_result, safe_https_url

SERPAPI_URL = "https://serpapi.com/search.json"
REQUEST_TIMEOUT = 20
MAX_SOURCES = 5

st.set_page_config(page_title="Vedra – Unified AI Search", page_icon="🔎", layout="wide")


def get_secret(name: str) -> str | None:
    """Read a secret from Streamlit secrets first, then the process environment."""
    try:
        value = st.secrets.get(name)
    except Exception:
        value = None
    return value or os.getenv(name)


OPENAI_KEY = get_secret("OPENAI_API_KEY")
SERPAPI_KEY = get_secret("SERPAPI_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Header
st.title("Vedra 🔎")
st.caption("One Answer. Many Minds. — AI answers grounded in discoverable sources.")

with st.expander("Privacy and source transparency", expanded=False):
    st.write(
        "Vedra does not currently save searches or answers to its own database. "
        "When you search, your query is sent to OpenAI to generate an answer and, "
        "when SERPAPI_KEY is configured, to SerpAPI to retrieve web and media results. "
        "Those providers process requests under their own terms and privacy policies. "
        "The privacy control in the earlier prototype did not change data handling, "
        "so it has been replaced with this explicit disclosure."
    )

if not OPENAI_KEY:
    st.error(
        "OpenAI is not configured. Add OPENAI_API_KEY to the Streamlit app secrets "
        "or the deployment environment before running searches."
    )
    st.stop()

client = OpenAI(api_key=OPENAI_KEY)


def search_web(query: str) -> dict:
    if not SERPAPI_KEY:
        return {}
    try:
        response = requests.get(
            SERPAPI_URL,
            params={"engine": "google", "q": query, "api_key": SERPAPI_KEY},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        payload = response.json()
        return payload if isinstance(payload, dict) else {}
    except (requests.RequestException, ValueError):
        return {}


def search_media(query: str, vertical: str) -> dict:
    if not SERPAPI_KEY:
        return {}
    try:
        response = requests.get(
            SERPAPI_URL,
            params={
                "engine": "google",
                "q": query,
                "tbm": vertical,
                "api_key": SERPAPI_KEY,
            },
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        payload = response.json()
        return payload if isinstance(payload, dict) else {}
    except (requests.RequestException, ValueError):
        return {}


def make_answer(query: str, sources: list[dict]) -> str:
    source_context = "\n".join(
        f"[{i + 1}] {item.get('title', 'Untitled')}: {item.get('snippet', '')} "
        f"({item.get('link', '')})"
        for i, item in enumerate(sources)
    )
    if not source_context:
        source_context = "No external web snippets were available for this query."

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are Vedra, a careful research and learning assistant. "
                    "Answer clearly and directly. Distinguish established facts from "
                    "uncertainty. Use the supplied web snippets as evidence, cite them "
                    "inline as [1], [2], etc., and never claim independent verification "
                    "when the snippets do not support it. If no snippets are supplied, "
                    "say that the answer is not web-grounded."
                ),
            },
            {
                "role": "user",
                "content": f"Question: {query}\n\nWeb snippets:\n{source_context}",
            },
        ],
        temperature=0.3,
        max_tokens=900,
    )
    content = response.choices[0].message.content
    return content.strip() if content else "No answer was returned by the model."


with st.form("search_form"):
    query = st.text_input("Ask Vedra anything:", placeholder="e.g. How does UPI settlement work?")
    submitted = st.form_submit_button("Search Vedra", type="primary")

if submitted:
    query = query.strip()
    if not query:
        st.warning("Enter a question to search.")
        st.stop()

    with st.spinner("Searching sources and synthesizing an answer…"):
        web_data = search_web(query)
        organic = web_data.get("organic_results", [])
        sources = [
            item
            for item in organic
            if isinstance(item, dict) and safe_https_url(item.get("link"))
        ][:MAX_SOURCES]

        try:
            answer = make_answer(query, sources)
        except Exception:
            st.error(
                "The answer could not be generated. Check the OpenAI API configuration "
                "and account availability, then try again."
            )
            st.stop()

        image_data = search_media(query, "isch") if SERPAPI_KEY else {}
        video_data = search_media(query, "vid") if SERPAPI_KEY else {}
        news_data = search_media(query, "nws") if SERPAPI_KEY else {}

    st.subheader("Vedra's answer")
    st.markdown(answer)

    if sources:
        st.caption("Web-grounded using the following search results. These sources have not been independently fact-checked.")
        with st.expander("Web sources", expanded=True):
            for index, item in enumerate(sources, start=1):
                title = item.get("title") or item.get("link") or f"Source {index}"
                st.markdown(f"[{index}. {title}]({item['link']})")
                if item.get("snippet"):
                    st.caption(item["snippet"])
    else:
        st.info(
            "No web sources were available. This answer is generated by the AI model "
            "and is not grounded in live search results."
        )

    images = image_data.get("images_results", [])
    image_urls = [
        safe_https_url(item.get("thumbnail") or item.get("original"))
        for item in images
        if isinstance(item, dict)
    ]
    image_urls = [url for url in image_urls if url][:4]
    if image_urls:
        st.subheader("Related images")
        st.image(image_urls, use_container_width=True)

    videos = video_data.get("video_results", [])
    normalized_videos = [
        normalise_video_result(item)
        for item in videos
    ]
    normalized_videos = [item for item in normalized_videos if item]
    if normalized_videos:
        st.subheader("Related videos")
        for item in normalized_videos[:3]:
            if item.get("thumbnail"):
                st.image(item["thumbnail"], width=260)
            st.markdown(f"[{item.get('title') or 'Watch video'}]({item['link']})")
            if item.get("channel"):
                st.caption(item["channel"])

    news = news_data.get("news_results", [])
    valid_news = [
        item for item in news
        if isinstance(item, dict) and safe_https_url(item.get("link"))
    ][:3]
    if valid_news:
        st.subheader("Recent news")
        for item in valid_news:
            st.markdown(f"- [{item.get('title') or 'News article'}]({item['link']})")

    st.caption("Vedra is an AI research assistant. Check important claims against the linked original sources.")

st.divider()
st.caption("Vedra AI · Research and learning prototype")
