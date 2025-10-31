from typing import List, Optional


class RecursiveCharacterTextSplitter:
    """A minimal text splitter compatible with LangChain's basic behavior.

    This splitter splits text into chunks of approximately `chunk_size` with
    a configurable `chunk_overlap`. It's intentionally simple and avoids
    dependencies so Streamlit Cloud can run without installing full langchain.
    """

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200, separators: Optional[List[str]] = None):
        self.chunk_size = int(chunk_size)
        self.chunk_overlap = int(chunk_overlap)
        # separators is ignored in this minimal implementation
        self.separators = separators or ["\n\n", "\n", " ", ""]

    def split_text(self, text: str) -> List[str]:
        if text is None:
            return []
        text = text.strip()
        if not text:
            return []

        # Simple sliding-window chunking with overlap
        chunks: List[str] = []
        start = 0
        length = len(text)
        while start < length:
            end = start + self.chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            if end >= length:
                break
            start = max(0, end - self.chunk_overlap)
        return chunks

    # Some code expects `split_documents` or `split_texts`; provide a thin wrapper
    def split_documents(self, documents: List[str]) -> List[str]:
        out: List[str] = []
        for doc in documents:
            out.extend(self.split_text(doc))
        return out

    def split_texts(self, texts: List[str]) -> List[str]:
        return self.split_documents(texts)
