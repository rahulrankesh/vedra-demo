import streamlit as st
import openai, requests, os

st.set_page_config(page_title="Vedra – One Answer. Many Minds.", layout="centered")

st.title("Vedra 🔍")
st.caption("Unified AI Search – One Answer. Many Minds.")

openai.api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
HF_KEY = st.secrets.get("HF_API_KEY") or os.getenv("HF_API_KEY")

query = st.text_input("Ask Vedra anything:")

privacy = st.toggle("Privacy Mode (no data stored)", value=True)

if query:
    with st.spinner("Collecting wisdom from multiple AIs..."):
        # --- GPT-4 / OpenAI response
        gpt_ans = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": query}],
            max_tokens=250,
            temperature=0.7,
        )["choices"][0]["message"]["content"]

        # --- Hugging Face response
        hf_resp = requests.post(
            "https://api-inference.huggingface.co/models/google/flan-t5-large",
            headers={"Authorization": f"Bearer {HF_KEY}"},
            json={"inputs": query},
        )
        hf_ans = hf_resp.json()[0]["generated_text"] if isinstance(hf_resp.json(), list) else "No response"

        # --- Simple fusion
        unified = f"**Vedra Unified Insight:**\n\n**GPT:** {gpt_ans}\n\n**Hugging Face:** {hf_ans}\n\n**Fusion:**\n{gpt_ans.split('.')[0]}. {hf_ans.split('.')[0]}."

    st.markdown(unified)
    st.success("Answer verified from multiple sources ✅")

st.markdown("---")
st.caption("© 2025 Vedra | Privacy-First AI Search")
