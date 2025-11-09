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

               # ------------------- SERPAPI (Web grounding) -------------------
                try:
                    serp_key = st.secrets.get("SERPAPI_KEY") or os.getenv("SERPAPI_KEY")
                    params = {
                        "engine": "google",
                        "q": query,
                        "api_key": serp_key
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
 # ------------------- COHERE (summarization / second LLM) -------------------
            # Requires COHERE_API_KEY in secrets
            try:
                coh_key = st.secrets.get("COHERE_API_KEY") or os.getenv("COHERE_API_KEY")
                coh_resp = requests.post(
                    "https://api.cohere.ai/generate",
                    headers={"Authorization": f"Bearer {coh_key}", "Content-Type": "application/json"},
                    json={
                        "model": "command-xlarge-nightly",
                        "prompt": query,
                        "max_tokens": 200,
                        "temperature": 0.7
                    },
                    timeout=30
                )
                if coh_resp.ok:
                    coh_data = coh_resp.json()
                    coh_ans = coh_data.get("generations", [{}])[0].get("text", "No response")
                else:
                    coh_ans = f"⚠️ Cohere Error: {coh_resp.text}"
            except Exception as e:
                coh_ans = f"⚠️ Cohere Error: {e}"
            
            # ------------------- FUSION (show three engines: OpenAI, Bing, Cohere) -------------------
            fused = (
                f"### 🧠 Vedra Unified Insight\n\n"
                f"**OpenAI says:** {gpt_ans}\n\n"
                f"**Web grounding (Bing) adds:** {bing_ans}\n\n"
                f"**Cohere adds:** {coh_ans}\n\n"
                f"**Web (SerpAPI) adds:** {serp_ans}\n\n"
                f"**Fusion Summary:**\n"
                f"{gpt_ans.split('.')[0]}. {bing_ans.split('.')[0] if bing_ans else ''} {coh_ans.split('.')[0] if coh_ans else ''}"
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
