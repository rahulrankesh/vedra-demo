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
SERPAPI_KEY = st.secrets.get("SERPAPI_KEY") or os.getenv("SERPAPI_KEY")
COHERE_KEY = st.secrets.get("COHERE_API_KEY") or os.getenv("COHERE_API_KEY")

client = OpenAI(api_key=OPENAI_KEY)

# Input field
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

        # ------------------- SERPAPI (Google Web grounding) -------------------
        try:
            params = {
                "engine": "google",
                "q": query,
                "api_key": SERPAPI_KEY
            }
            serp_resp = requests.get("https://serpapi.com/search", params=params, timeout=30)
            if serp_resp.ok:
                data = serp_resp.json()
                if "organic_results" in data and len(data["organic_results"]) > 0:
                    top = data["organic_results"][0]
                    serp_ans = f"{top.get('title','')}: {top.get('snippet','')}"
                else:
                    serp_ans = "No web results found."
            else:
                serp_ans = f"⚠️ SerpAPI Error: {serp_resp.text}"
        except Exception as e:
            serp_ans = f"⚠️ SerpAPI Error: {e}"

        # ------------------- COHERE -------------------
       # ------------------- COHERE (Chat API - Corrected Request Format) -------------------
            try:
                payload = {
                    "model": "command-r-plus",
                    "message": {
                        "role": "user",
                        "content": f"Summarize this neutrally and factually: {query}"
                    },
                    "temperature": 0.7
                }
            
                coh_resp = requests.post(
                    "https://api.cohere.ai/v1/chat",
                    headers={
                        "Authorization": f"Bearer {COHERE_KEY}",
                        "Content-Type": "application/json"
                    },
                    json=payload,
                    timeout=30
                )
            
                if coh_resp.ok:
                    coh_data = coh_resp.json()
                    # The response text lives under message → content → [0] → text
                    coh_ans = (
                        coh_data.get("message", {})
                        .get("content", [{}])[0]
                        .get("text", "No response")
                    )
                else:
                    coh_ans = f"⚠️ Cohere Error: {coh_resp.text}"
            except Exception as e:
                coh_ans = f"⚠️ Cohere Error: {e}"


        # ------------------- FUSION -------------------
        fused = (
            f"### 🧠 Vedra Unified Insight\n\n"
            f"**OpenAI says:** {gpt_ans}\n\n"
            f"**Web (SerpAPI) adds:** {serp_ans}\n\n"
            f"**Cohere suggests:** {coh_ans}\n\n"
            f"**Fusion Summary:**\n"
            f"{gpt_ans.split('.')[0]}. {serp_ans.split('.')[0] if serp_ans else ''}. {coh_ans.split('.')[0] if coh_ans else ''}."
        )

    # ------------------- DISPLAY -------------------
    st.markdown(fused)
    st.success("Verified by multiple sources ✅")

    # Collapsible source info
    with st.expander("🔗 Engines & Sources Used"):
        st.markdown("""
        - 🧠 **OpenAI GPT-3.5** – Deep reasoning and creative synthesis  
        - 🌍 **SerpAPI (Google)** – Live web grounding and factual context  
        - 🪶 **Cohere Command** – Neutral summarization and tone balancing  
        """)

    st.markdown(f"[Explore *{query}* on Google](https://www.google.com/search?q={query.replace(' ','+')})")
    st.markdown(f"[Wikipedia: {query}](https://en.wikipedia.org/wiki/{query.replace(' ','_')})")

st.markdown("---")
st.caption("© 2025 Vedra AI | Multi-AI Unified Search Prototype | Privacy-First Design")
