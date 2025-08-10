# rag_store.py
import os
import json
from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
from pdfminer.high_level import extract_text

# Storage structure:
# - a JSON manifest mapping chunk_id -> metadata {filename, offset_start, offset_end, text}
# - a numpy .npy embeddings file and a faiss index (saved to disk)

MODEL_NAME = os.environ.get("SENTENCE_EMBEDDING_MODEL", "all-MiniLM-L6-v2")
EMBED_DIR = "embeddings"
MANIFEST_PATH = os.path.join(EMBED_DIR, "manifest.json")
EMBED_MATRIX_PATH = os.path.join(EMBED_DIR, "embeddings.npy")
FAISS_INDEX_PATH = os.path.join(EMBED_DIR, "faiss.index")

os.makedirs(EMBED_DIR, exist_ok=True)

def extract_text_from_pdf(path: str) -> str:
    return extract_text(path)

def chunk_text(text: str, chunk_size: int = 400, overlap: int = 80) -> List[str]:
    tokens = text.split()
    chunks = []
    i = 0
    while i < len(tokens):
        chunk = tokens[i:i+chunk_size]
        chunks.append(" ".join(chunk))
        i += chunk_size - overlap
    return chunks

def build_or_update_index(sources: List[Tuple[str, str]], model_name=MODEL_NAME):
    """
    sources: list of (source_id, path_or_text). If path endswith .pdf, we'll extract text.
    Returns: index (faiss index), manifest (dict)
    """
    model = SentenceTransformer(model_name)
    manifest = {}
    all_chunks = []
    chunk_meta = []

    for src_id, path_or_text in sources:
        if os.path.isfile(path_or_text) and path_or_text.lower().endswith(".pdf"):
            txt = extract_text_from_pdf(path_or_text)
        else:
            txt = path_or_text
        chunks = chunk_text(txt)
        for idx, chunk in enumerate(chunks):
            cid = f"{src_id}::chunk_{idx}"
            manifest[cid] = {"source": src_id, "chunk_index": idx, "text": chunk}
            all_chunks.append(chunk)
            chunk_meta.append(cid)

    embeddings = model.encode(all_chunks, convert_to_numpy=True, show_progress_bar=True)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)

    # persist
    np.save(EMBED_MATRIX_PATH, embeddings)
    faiss.write_index(index, FAISS_INDEX_PATH)
    with open(MANIFEST_PATH, "w", encoding="utf8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    return index, manifest

def load_index_and_manifest():
    if not os.path.exists(FAISS_INDEX_PATH) or not os.path.exists(MANIFEST_PATH):
        raise FileNotFoundError("Index or manifest not found. Run build_or_update_index first.")
    index = faiss.read_index(FAISS_INDEX_PATH)
    with open(MANIFEST_PATH, "r", encoding="utf8") as f:
        manifest = json.load(f)
    embeddings = np.load(EMBED_MATRIX_PATH)
    return index, manifest, embeddings
