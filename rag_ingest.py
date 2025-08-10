# rag_ingest.py
"""
RAG ingestion helpers.
This module shows how to:
- extract text from PDFs (e.g., Data Sources.pdf)
- chunk text
- compute embeddings using sentence-transformers or OpenAI
- build a FAISS index for retrieval

NOTE: you must supply your embedding model API key if using OpenAI. Here I show an example with sentence-transformers locally.
"""
from pdfminer.high_level import extract_text
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
from typing import List

def extract_text_from_pdf(path: str) -> str:
    return extract_text(path)

def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> List[str]:
    tokens = text.split()
    chunks = []
    i = 0
    while i < len(tokens):
        chunk = tokens[i:i+chunk_size]
        chunks.append(" ".join(chunk))
        i += chunk_size - overlap
    return chunks

def build_faiss_index(chunks: List[str], model_name: str = "all-MiniLM-L6-v2"):
    model = SentenceTransformer(model_name)
    embeddings = model.encode(chunks, show_progress_bar=True, convert_to_numpy=True)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    return index, embeddings
