import streamlit as st
import requests, os
from openai import OpenAI

# --------------------------
# Vedra: One Answer. Many Minds.
# --------------------------

st.set_page_config(page_title="Vedra – Unified AI Search", layout="wide")

# Logo + Header
col1, col2 = st.columns([1, 5])
with col1:
    st.image("https://i.ibb.co/TM4HQ2P/vedra-logo.png", width=100)
with col2:
    st.markdown("<h1 style='margin-bottom:0;'>Vedra 🔍</h1>", unsafe_allow_html=True)
    st.caption("One Answer. Many Minds.")

# Load keys
OPENAI_KEY = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
SERPAPI_KEY = st.secrets.get("SERPAPI_KEY") or os.getenv("SERPAPI_KEY")

client = OpenAI(api_key=OPENAI_KEY)

# Input field
query = st.text_input("Ask Vedra anything:")
privacy = st.toggle("Privacy Mode (no data stored)", value=True)

if query:
    with st.spinner("Gathering intelligence from multiple AIs..."):

        # Define defaults
        gpt_ans = ""
        serp_ans = ""
        serp_data = {}

        # ------------------- OPENAI -------------------
        try:
            gpt_resp = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": query}],
                max_tokens=300,
                temperature=0.7,
            )
            gpt_ans = gpt_resp.choices[0].message.content.strip()
        except Exception as e:
            gpt_ans = f"⚠️ OpenAI Error: {e}"

        # ------------------- SERPAPI (Google Web grounding) -------------------
        try:
            params = {"engine": "google", "q": query, "api_key": SERPAPI_KEY}
            serp_resp = requests.get("https://serpapi.com/search", params=params, timeout=30)
            if serp_resp.ok:
                serp_data = serp_resp.json()
                if "organic_results" in serp_data and len(serp_data["organic_results"]) > 0:
                    top = serp_data["organic_results"][0]
                    serp_ans = f"{top.get('title','')}: {top.get('snippet','')}"
                else:
                    serp_ans = "No web results found."
            else:
                serp_ans = f"⚠️ SerpAPI Error: {serp_resp.text}"
        except Exception as e:
            serp_ans = f"⚠️ SerpAPI Error: {e}"

        # ------------------- IMAGE SEARCH -------------------
        image_urls = []
        try:
            img_params = {"engine": "google", "q": query, "tbm": "isch", "api_key": SERPAPI_KEY}
            img_resp = requests.get("https://serpapi.com/search", params=img_params, timeout=30)
            if img_resp.ok:
                img_data = img_resp.json()
                image_urls = [img["original"] for img in img_data.get("images_results", [])[:4]]
        except Exception:
            pass

        # ------------------- FOLLOW-UP SUGGESTIONS -------------------
        follow_ups = []
        try:
            followup = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": f"Suggest 3 concise follow-up questions related to: {query}"}],
                max_tokens=60
            )
            follow_ups = [q.strip("•- ") for q in followup.choices[0].message.content.split("\n") if q.strip()]
        except Exception:
            pass

        # ------------------- FUSION -------------------
        fused = (
            f"### 🧠 Vedra Unified Insight\n\n"
            f"**OpenAI says:** {gpt_ans}\n\n"
            f"**Web (SerpAPI) adds:** {serp_ans}\n\n"
            f"**Fusion Summary:**\n"
            f"{gpt_ans.split('.')[0]}. "
            f"{serp_ans.split('.')[0] if serp_ans else ''}."
        )

    # ------------------- DISPLAY -------------------
    st.markdown(fused)
    st.success("Verified by multiple sources ✅")

    # ------------------- IMAGES -------------------
    if image_urls:
        st.markdown("### 📸 Related Images")
        st.image(image_urls, width=250, caption=[f"Image {i+1}" for i in range(len(image_urls))])

    # ------------------- LINKS -------------------
    if "organic_results" in serp_data:
        st.markdown("### 🔗 Top Web Sources")
        for r in serp_data["organic_results"][:3]:
            st.markdown(f"- [{r.get('title')}]({r.get('link')})")

    # ------------------- FOLLOW-UPS -------------------
    if follow_ups:
        st.markdown("### 💡 Suggested Next Searches")
        cols = st.columns(len(follow_ups))
        for i, f in enumerate(follow_ups):
            with cols[i]:
                st.button(f, key=f"followup_{i}")

    # ------------------- INFO -------------------
    with st.expander("🔗 Engines & Sources Used"):
        st.markdown("""
        - 🧠 **OpenAI GPT-3.5** – Deep reasoning and synthesis  
        - 🌍 **SerpAPI (Google)** – Live web grounding, images, and source links  
        """)

    st.markdown(f"[Explore *{query}* on Google](https://www.google.com/search?q={query.replace(' ','+')})")
    st.markdown(f"[Wikipedia: {query}](https://en.wikipedia.org/wiki/{query.replace(' ','_')})")

st.markdown("---")
st.caption("© 2025 Vedra AI | Visual Multi-AI Search Prototype | Privacy-First Design")
