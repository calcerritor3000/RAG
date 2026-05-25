import os
import uuid
from dataclasses import dataclass
from typing import List

import certifi
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

# Corrige errores SSL al descargar modelos de HuggingFace (comun en Windows/centros educativos)
os.environ.setdefault("SSL_CERT_FILE", certifi.where())
os.environ.setdefault("REQUESTS_CA_BUNDLE", certifi.where())


@dataclass
class RAGConfig:
    collection_name: str = "docs"
    embedding_model: str = "all-MiniLM-L6-v2"
    chunk_size: int = 700
    overlap: int = 120
    top_k: int = 4


class RAGCore:
    def __init__(self, config: RAGConfig | None = None) -> None:
        self.config = config or RAGConfig()
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self._collection = None
        self._embedding_fn = None

    @property
    def embedding_fn(self):
        if self._embedding_fn is None:
            self._embedding_fn = SentenceTransformerEmbeddingFunction(
                model_name=self.config.embedding_model
            )
        return self._embedding_fn

    @property
    def collection(self):
        if self._collection is None:
            self._collection = self.client.get_or_create_collection(
                name=self.config.collection_name,
                embedding_function=self.embedding_fn,
            )
        return self._collection

    def _chunk_text(self, text: str) -> List[str]:
        clean = " ".join(text.split())
        chunks = []
        i = 0
        while i < len(clean):
            chunk = clean[i : i + self.config.chunk_size]
            if chunk.strip():
                chunks.append(chunk)
            i += self.config.chunk_size - self.config.overlap
        return chunks

    def ingest_text(self, text: str, source_name: str) -> int:
        chunks = self._chunk_text(text)
        ids = [str(uuid.uuid4()) for _ in chunks]
        metadatas = [{"source": source_name, "idx": i} for i, _ in enumerate(chunks)]
        self.collection.add(ids=ids, documents=chunks, metadatas=metadatas)
        return len(chunks)

    def search(self, question: str) -> List[dict]:
        results = self.collection.query(
            query_texts=[question],
            n_results=self.config.top_k,
            include=["documents", "distances", "metadatas"],
        )
        docs = results.get("documents", [[]])[0]
        distances = results.get("distances", [[]])[0]
        metas = results.get("metadatas", [[]])[0]

        chunks = []
        for idx, doc in enumerate(docs):
            score = 1 - float(distances[idx]) if idx < len(distances) else None
            chunks.append(
                {
                    "chunk": doc,
                    "source": metas[idx].get("source") if idx < len(metas) and metas[idx] else None,
                    "similarity": round(score, 4) if score is not None else None,
                }
            )
        return chunks
