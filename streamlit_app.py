import base64
import streamlit as st
import importlib.util
from pathlib import Path

# Try to import the integration module normally (works in local dev).
# If that triggers package-level imports (Flask/SQLAlchemy) which aren't
# available in the Streamlit Cloud runtime, fall back to loading the module
# directly from its file so we avoid executing `app/__init__.py`.
try:
    from app.ml.integration import summarize_text  # type: ignore
except Exception:
    integration_path = Path(__file__).resolve().parent / "app" / "ml" / "integration.py"
    spec = importlib.util.spec_from_file_location("app_ml_integration", str(integration_path))
    integration = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(integration)  # type: ignore
    summarize_text = integration.summarize_text


st.set_page_config(page_title="Alemêno Backend - Summarizer", layout="centered")

st.title("Alemêno Backend — Text Summarizer")
st.markdown(
    "This Streamlit front-end uses the project's ML integration to summarize text. "
    "It does not run the Flask server; it calls the same Python logic directly."
)

examples = {
    "Short paragraph": (
        "Alemêno is an example backend used for demos. It contains an ML summarizer "
        "that can use OpenAI if a key is provided."
    ),
    "Long article": (
        "Machine learning models have transformed how we approach automation and "
        "data-driven decision making. In many cases, combining domain knowledge with "
        "powerful models yields the best results. The summarizer in this repo is a "
        "simple wrapper around OpenAI or a heuristic fallback. It serves as a minimal "
        "example for integration and deployment."
    ),
}


col_ex, col_action = st.columns([3, 1])
with col_ex:
    choice = st.selectbox(
        "Example texts", ["", *examples.keys()], help="Choose an example to prefill the text area"
    )
    if choice:
        text = st.text_area("Text to summarize", value=examples[choice], height=220)
    else:
        text = st.text_area("Text to summarize", height=220)

with col_action:
    uploaded = st.file_uploader("Upload a .txt file", type=["txt"])
    if uploaded is not None:
        try:
            content = uploaded.read().decode("utf-8")
            st.success("File loaded")
            text = content
        except Exception as e:
            st.error(f"Could not read uploaded file: {e}")


if st.button("Summarize"):
    if not text or not text.strip():
        st.warning("Please provide text or upload a .txt file.")
    else:
        with st.spinner("Summarizing..."):
            try:
                summary = summarize_text(text)
                st.success("Summary generated")
                st.code(summary)

                # copy to clipboard button (Streamlit doesn't support clipboard directly;
                # provide a clickable text area + download)
                st.text_area("Copy summary", value=summary, height=150)

                # provide download link
                b = summary.encode("utf-8")
                b64 = base64.b64encode(b).decode()
                href = f"data:file/text;base64,{b64}"
                st.markdown(f"[Download summary]({href})")
            except Exception as e:
                st.error(f"Error while summarizing: {e}")


if st.button("Clear"):
    st.experimental_rerun()


st.markdown("---")
st.markdown(
    "If you have an `OPENAI_API_KEY` set in Streamlit Cloud secrets (or in your environment), "
    "the summarizer will try the OpenAI API; otherwise it uses a simple local heuristic."
)

st.markdown("## Example Usage")
st.write("Choose an example, or upload a .txt file, then press Summarize.")
