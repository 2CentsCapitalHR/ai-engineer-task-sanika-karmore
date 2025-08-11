# retriever.py
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict
from rag_store import load_index_and_manifest, MODEL_NAME
import faiss

model = SentenceTransformer(MODEL_NAME)

def retrieve(query: str, k: int = 5) -> List[Dict]:
    """
    returns list of {"chunk_id","source","chunk_index","text","score"}
    """
    index, manifest, embeddings = load_index_and_manifest()
    q_emb = model.encode([query], convert_to_numpy=True)
    D, I = index.search(q_emb, k)
    results = []
    # faiss returns distances; convert to similarity-ish (lower is closer for L2)
    for dist, idx in zip(D[0], I[0]):
        if idx < 0:
            continue
        # retrieve original chunk id via embeddings array ordering:
        # manifest keys order must match embeddings ordering -> we saved them in build function in that order.
        # to be safe, reconstruct keys list:
        keys = list(manifest.keys())
        chunk_id = keys[idx]
        m = manifest[chunk_id]
        results.append({
            "chunk_id": chunk_id,
            "source": m.get("source"),
            "chunk_index": m.get("chunk_index"),
            "text": m.get("text"),
            "score": float(dist)
        })
    return results
