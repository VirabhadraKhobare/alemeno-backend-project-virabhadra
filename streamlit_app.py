import base64
import streamlit as st
import importlib.util
from pathlib import Path
from datetime import datetime

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


def _main_ui():
    # Small CSS tweak to keep content narrow and centered for a cleaner look
    st.markdown(
        """
        <style>
        .main .block-container{ max-width: 900px; padding-left: 1rem; padding-right: 1rem; }
        @media (max-width: 800px) { .main .block-container{ padding-left: 0.5rem; padding-right: 0.5rem; } }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("Alemêno Backend — Text Summarizer")

    intro = (
        "This Streamlit front-end uses the project's ML integration to summarize text. "
        "It does not run the Flask server; it calls the same Python logic directly."
    )
    st.markdown(intro)

    examples = {
        "Short paragraph": (
            "Alemêno is an example backend used for demos. It contains an ML summarizer "
            "that can use OpenAI if a key is provided."
        ),
        "Long article": (
            "Machine learning models have transformed how we approach automation and "
            "data-driven decision making. In many cases, combining domain knowledge with "
            "powerful models yields the best results. The summarizer in this repo is a "
            "simple wrapper around OpenAI or a heuristic fallback."
        ),
    }

    # Ensure session state keys exist
    if "input_text" not in st.session_state:
        st.session_state["input_text"] = ""
    if "history" not in st.session_state:
        st.session_state["history"] = []

    def _update_example():
        # copy the selected example into the editor immediately
        sel = st.session_state.get("choice_select", "")
        if sel:
            st.session_state["input_text"] = examples.get(sel, "")

    # Sidebar - History
    st.sidebar.header("History")
    history = st.session_state.get("history", [])
    if not history:
        st.sidebar.write("No summaries yet.")
    else:
        for i, item in enumerate(history):
            with st.sidebar.expander(f"{i+1}. {item['summary'][:60]}"):
                st.write(item["summary"])
                st.write(f"Saved: {item['time']}")
                if st.button("Load into editor", key=f"load_{i}"):
                    st.session_state["input_text"] = item["text"]
                if st.button("Delete", key=f"del_{i}"):
                    history.pop(i)
                    st.session_state["history"] = history
                    st.experimental_rerun()

    # Center the main content by using three columns and placing UI in the middle one
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        # place the example selector and uploader *outside* the form so callbacks
        # (on_change) are allowed; they aren't permitted on widgets inside forms.
        top_cols = st.columns([3, 1])
        with top_cols[0]:
            choice = st.selectbox(
                "Example texts",
                ["", *examples.keys()],
                key="choice_select",
                help="Choose an example to prefill the text area",
                on_change=_update_example,
            )

        with top_cols[1]:
            uploaded = st.file_uploader("Upload a .txt file", type=["txt"]) 
            if uploaded is not None:
                try:
                    content = uploaded.read().decode("utf-8")
                    st.success("File loaded")
                    # Update the text area with uploaded content
                    st.session_state["input_text"] = content
                except Exception as e:
                    st.error(f"Could not read uploaded file: {e}")

        # Use a form to group the editor and the submit button
        with st.form(key="summarize_form"):
            # editor bound to session state so it can be updated externally
            text = st.text_area("Text to summarize", value=st.session_state.get("input_text", ""), key="input_text", height=260)

            submit = st.form_submit_button("Summarize")

        # Clear button (separate, small)
        c1, c2, c3 = st.columns([1, 1, 6])
        with c1:
            if st.button("Clear"):
                st.session_state["input_text"] = ""
                st.experimental_rerun()

        # Output area
        if submit:
            text = st.session_state.get("input_text", "")
            if not text or not text.strip():
                st.warning("Please provide text or upload a .txt file.")
            else:
                with st.spinner("Summarizing..."):
                    try:
                        summary = summarize_text(text)
                        st.success("Summary generated")
                        st.code(summary)

                        # show downloadable button and copy field
                        st.download_button("Download summary", data=summary, file_name="summary.txt", mime="text/plain")
                        st.text_area("Copy summary", value=summary, height=150)

                        # save to history (keep most recent first)
                        history = st.session_state.get("history", [])
                        history.insert(0, {"time": datetime.utcnow().isoformat(), "text": text, "summary": summary})
                        # limit history length
                        st.session_state["history"] = history[:20]
                    except Exception as e:
                        st.error(f"Error while summarizing: {e}")

    st.markdown("---")
    st.info("If you have an `OPENAI_API_KEY` set in Streamlit Cloud secrets (or in your environment), the summarizer will try the OpenAI API; otherwise it uses a simple local heuristic.")
    st.markdown("## Example Usage")
    st.write("Choose an example, or upload a .txt file, then press Summarize.")


_main_ui()
