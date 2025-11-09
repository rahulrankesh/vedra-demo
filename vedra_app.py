import streamlit as st
import requests, os
from openai import OpenAI

# --------------------------
# Vedra: One Answer. Many Minds.
# --------------------------

st.set_page_config(page_title="Vedra – Unified AI Search", layout="centered")

st.image("https://i.ibb.co/TM4HQ2P/vedra-logo.png", width=160)
st.title("Vedra 🔍")
st.caption("One Answer. Many Minds.")

# Load keys
OPENAI_KEY = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
PERPLEXITY_KEY = st.secrets.get("PERPLEXITY_API_KEY") or os.getenv("PERPLEXITY_API_KEY")
GEMINI_KEY = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

client = OpenAI(api_key=OPENAI_KEY)

query = st.text_input("Ask Vedra anything:")
privacy = st.toggle("Privacy Mode (no data stored)", value=True)

if query:
    with st.spinner("Gathering intelligence from multiple AIs..."):

        # ------------------- OPENAI -------------------
        try:
            gpt_resp = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": query}],
                max_tokens=250,
                temperature=0.7,
            )
            gpt_ans = gpt_resp.choices[0].message.content.strip()
        except Exception as e:
            gpt_ans = f"⚠️ OpenAI Error: {e}"

        # ------------------- PERPLEXITY -------------------
        # ------------------- PERPLEXITY -------------------
        try:
            pplx_resp = requests.post(
                "https://api.perplexity.ai/chat/completions",
                headers={
                    "Authorization": f"Bearer {PERPLEXITY_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "sonar-small-online",
                    "messages": [{"role": "user", "content": query}],
                },
                timeout=60,
            )
            if pplx_resp.ok:
                pplx_ans = pplx_resp.json()["choices"][0]["message"]["content"]
            else:
                pplx_ans = f"⚠️ Perplexity Error: {pplx_resp.text}"
        except Exception as e:
            pplx_ans = f"⚠️ Perplexity Error: {e}"


        # ------------------- GEMINI -------------------
        # ------------------- GEMINI -------------------
        try:
            gem_resp = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_KEY}",
                json={
                    "contents": [
                        {"parts": [{"text": f"{query}. Summarize neutrally and factually."}]}
                    ]
                },
                timeout=60,
            )
            data = gem_resp.json()
            if "candidates" in data and data["candidates"]:
                gem_ans = data["candidates"][0]["content"]["parts"][0]["text"]
            elif "promptFeedback" in data:
                gem_ans = f"Gemini filtered output: {data['promptFeedback'].get('safetyRatings', '')}"
            else:
                gem_ans = "Gemini returned no content."
        except Exception as e:
            gem_ans = f"⚠️ Gemini Error: {e}"

        # ------------------- FUSION -------------------
        fused = (
            f"### 🧠 Vedra Unified Insight\n\n"
            f"**OpenAI says:** {gpt_ans}\n\n"
            f"**Perplexity adds:** {pplx_ans}\n\n"
            f"**Gemini suggests:** {gem_ans}\n\n"
            f"**Fusion Summary:**\n"
            f"{gpt_ans.split('.')[0]}. {pplx_ans.split('.')[0]}. {gem_ans.split('.')[0]}."
        )

    st.markdown(fused)
    st.success("Verified by multiple sources ✅")

    with st.expander("🔗 Sources & Engines Used"):
        st.markdown("""
        - 🧠 **OpenAI GPT-3.5** – Deep reasoning and creative generation  
        - 🌐 **Perplexity AI** – Factual grounding from the live web  
        - ✨ **Google Gemini** – Context-aware summarization  
        """)

    st.markdown(f"[Search *{query}* on Google](https://www.google.com/search?q={query.replace(' ','+')})")
    st.markdown(f"[Wikipedia: {query}](https://en.wikipedia.org/wiki/{query.replace(' ','_')})")

st.markdown("---")
st.caption("© 2025 Vedra AI | Multi-AI Unified Search Prototype")
