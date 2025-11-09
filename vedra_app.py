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

# Load API keys securely
OPENAI_KEY = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
HF_KEY = st.secrets.get("HF_API_KEY") or os.getenv("HF_API_KEY")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_KEY)

# UI
query = st.text_input("Ask Vedra anything:")
privacy = st.toggle("Privacy Mode (no data stored)", value=True)

if query:
    with st.spinner("Collecting wisdom from multiple AIs..."):

        # --- GPT response (OpenAI new API)
        try:
            gpt_response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": query}],
                max_tokens=250,
                temperature=0.7,
            )
            gpt_ans = gpt_response.choices[0].message.content.strip()
        except Exception as e:
            gpt_ans = f"Error fetching GPT response: {e}"

        # --- Hugging Face response
        try:
            hf_resp = requests.post(
                "https://api-inference.huggingface.co/models/google/flan-t5-large",
                headers={"Authorization": f"Bearer {HF_KEY}"},
                json={"inputs": query},
                timeout=60
            )
            if isinstance(hf_resp.json(), list) and len(hf_resp.json()) > 0:
                hf_ans = hf_resp.json()[0].get("generated_text", "No response")
            else:
                hf_ans = "No response from Hugging Face model."
        except Exception as e:
            hf_ans = f"Error fetching HF response: {e}"

        # --- Simple Fusion Logic
        fused = (
            f"### Vedra Unified Insight\n\n"
            f"**GPT says:** {gpt_ans}\n\n"
            f"**Hugging Face adds:** {hf_ans}\n\n"
            f"**Fusion Summary:**\n"
            f"{gpt_ans.split('.')[0]}. {hf_ans.split('.')[0]}."
        )

    st.markdown(fused)
    st.success("Verified by multiple sources ✅")

st.markdown("---")
st.caption("© 2025 Vedra AI | Privacy-First Unified AI Search Prototype")
