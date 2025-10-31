import base64
import os
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

        /* Uploader card: target the FileUploader test id which Streamlit sets */
        div[data-testid="stFileUploader"] {
            background: rgba(255,255,255,0.02);
            padding: 12px;
            border-radius: 10px;
            border: 1px solid rgba(255,255,255,0.04);
            box-shadow: 0 6px 18px rgba(0,0,0,0.45);
            display: block;
        }

        /* Slightly tighten the caption and label spacing */
        div[data-testid="stFileUploader"] .stMarkdown, div[data-testid="stFileUploader"] .stText {
            margin: 0 0 6px 0;
        }

        /* Make the uploader full-width on small screens */
        @media (max-width: 800px) {
            div[data-testid="stFileUploader"] { width: 100% !important; }
        }

        /* Badge displayed next to uploader label */
        .uploader-badge{
            display: inline-block;
            background: rgba(255,255,255,0.03);
            color: #fff;
            font-weight: 600;
            padding: 4px 8px;
            border-radius: 8px;
            margin-right: 8px;
            font-size: 12px;
            vertical-align: middle;
            border: 1px solid rgba(255,255,255,0.06);
        }

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
    # session keys for OpenAI controls
    if "openai_key_input" not in st.session_state:
        st.session_state["openai_key_input"] = ""
    if "use_api_pref" not in st.session_state:
        st.session_state["use_api_pref"] = True

    def _update_example():
        # copy the selected example into the editor immediately
        sel = st.session_state.get("choice_select", "")
        if sel:
            st.session_state["input_text"] = examples.get(sel, "")
            # transient UI affordance: show small info that editor was updated
            st.session_state["show_info"] = f"Prefilled editor from example: {sel}"

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
    _, mid, _ = st.columns([1, 5, 1])
    with mid:
        # place the example selector above the editor
        choice = st.selectbox(
            "Example texts",
            ["", *examples.keys()],
            key="choice_select",
            help="Choose an example to prefill the text area",
            on_change=_update_example,
        )

        # If a transient info message is present, show it before the editor
        if st.session_state.get("show_info"):
            st.info(st.session_state.pop("show_info"))

        # Put uploader below the example selector and center it in a narrow column
        # so it displays vertically under the 'Example texts' label on desktop and
        # naturally stacks on small screens.
        u_left, u_mid, u_right = st.columns([1, 2, 1])
        with u_mid:
            # uploader label with a small badge (uses HTML for precise layout)
            st.markdown(
                '<div class="uploader-label"><span class="uploader-badge">📄 TXT</span> <strong>Upload a .txt file</strong></div>',
                unsafe_allow_html=True,
            )
            uploaded = st.file_uploader("", type=["txt"], key="uploader", help="Upload a plain text (.txt) file — max 200MB")
            st.caption("Accepted: .txt — max 200MB per file")
            if uploaded is not None:
                try:
                    content = uploaded.read().decode("utf-8")
                    st.success("File loaded")
                    # Update the text area with uploaded content
                    st.session_state["input_text"] = content
                    st.session_state["show_info"] = f"Loaded file: {getattr(uploaded, 'name', 'uploaded file')}"
                except Exception as e:
                    st.error(f"Could not read uploaded file: {e}")

        # Editor comes after the uploader, occupying the full width of the center column
        with st.container():
            with st.form(key="summarize_form"):
                text = st.text_area("Text to summarize", key="input_text", height=340)
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
                        # Decide which API key (if any) to use for this call.
                        use_api = st.session_state.get("use_api_pref", True)
                        if not use_api:
                            api_for_call = False
                        elif st.session_state.get("openai_key_input"):
                            api_for_call = st.session_state.get("openai_key_input")
                        else:
                            api_for_call = None

                        summary = summarize_text(text, api_key=api_for_call)
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

    # --- OpenAI key status and controls ---
    # Detect keys from environment or Streamlit secrets (if available)
    env_key = os.getenv("OPENAI_API_KEY")
    secret_key = None
    try:
        secret_key = st.secrets.get("OPENAI_API_KEY") if hasattr(st, "secrets") else None
    except Exception:
        secret_key = None

    st.header("Integration & API")
    col_status, col_controls = st.columns([3, 2])
    with col_status:
        if env_key:
            st.success("OpenAI API key detected in environment — the summarizer can use OpenAI.")
        elif secret_key:
            st.success("OpenAI API key found in Streamlit secrets — the summarizer can use OpenAI.")
        else:
            st.info("No OpenAI API key detected. The summarizer will use a local heuristic unless you provide a key for this session.")

    with col_controls:
        # session-only key input (password) — stored in session_state only
        st.text_input("Session OpenAI key", type="password", key="openai_key_input", placeholder="Paste API key to use for this session", help="This key is stored only for your current session and not persisted to files.")
        st.checkbox("Prefer OpenAI API when available", value=True, key="use_api_pref")
        if st.button("Test session key"):
            test_sample = "This is a short test sentence. Please summarize it briefly."
            api_for_test = None
            if st.session_state.get("openai_key_input"):
                api_for_test = st.session_state.get("openai_key_input")
            elif env_key or secret_key:
                api_for_test = None
            else:
                api_for_test = False
            try:
                test_out = summarize_text(test_sample, api_key=api_for_test)
                st.success("Test completed — sample summary below")
                st.write(test_out)
            except Exception as e:
                st.error(f"Test failed: {e}")

    st.markdown("## Example Usage")
    st.write("Choose an example, or upload a .txt file, then press Summarize.")


_main_ui()
