import streamlit as st
from app.ml.integration import summarize_text

st.set_page_config(page_title="Alemêno Backend - Summarizer", layout="centered")

st.title("Alemêno Backend — Text Summarizer")
st.markdown("This Streamlit front-end uses the project's ML integration to summarize text. It does not run the Flask server; it calls the same Python logic directly.")

text = st.text_area("Paste text to summarize", height=240)

col1, col2 = st.columns([1, 1])
with col1:
    if st.button("Summarize"):
        if not text.strip():
            st.warning("Please paste some text first.")
        else:
            with st.spinner("Summarizing..."):
                try:
                    summary = summarize_text(text)
                    st.success("Summary generated")
                    st.text_area("Summary", value=summary, height=200)
                except Exception as e:
                    st.error(f"Error while summarizing: {e}")
with col2:
    if st.button("Clear"):
        st.experimental_rerun()

st.markdown("---")
st.markdown("If you have an `OPENAI_API_KEY` set in the Streamlit Cloud secrets, the summarizer will try the OpenAI API; otherwise it uses a simple local heuristic.")

st.markdown("## Example")
st.write("Paste a few paragraphs of text and click Summarize to see a short summary.")
