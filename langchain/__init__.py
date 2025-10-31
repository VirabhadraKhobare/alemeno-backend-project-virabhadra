# Minimal shim for `langchain` to satisfy simple imports used in lightweight Streamlit deployments.
# This is NOT a full implementation of LangChain. It provides a small
# `RecursiveCharacterTextSplitter` compatible API used by many simple apps.

__all__ = ["text_splitter"]
