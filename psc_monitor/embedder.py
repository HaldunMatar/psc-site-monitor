import hashlib
import re

import numpy as np

DIM = 1024


def _hash_embed(text: str) -> np.ndarray:
    """تضمين محلي حتمي: n-grams للكلمات والأحرف يُجزَّأ إلى متجه ثابت الطول (يعمل مع العربية)."""
    vec = np.zeros(DIM, dtype=np.float64)
    words = re.findall(r"\w+", text.lower())
    feats = list(words) + [f"{a} {b}" for a, b in zip(words, words[1:])]
    compact = " ".join(words)
    feats += [compact[i:i + 4] for i in range(max(len(compact) - 3, 0))]
    for f in feats:
        h = int.from_bytes(hashlib.md5(f.encode()).digest()[:8], "big")
        vec[h % DIM] += 1.0 if (h >> 63) == 0 else -1.0
    return vec


_sbert = None


def _sbert_embed(text: str) -> np.ndarray:
    global _sbert
    if _sbert is None:
        from sentence_transformers import SentenceTransformer
        _sbert = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    return np.asarray(_sbert.encode(text), dtype=np.float64)


def embed(text: str, backend: str = "hash") -> np.ndarray:
    if backend == "hash":
        v = _hash_embed(text)
    elif backend == "sbert":
        v = _sbert_embed(text)
    else:
        raise ValueError(f"backend غير معروف: {backend}")
    n = np.linalg.norm(v)
    return v / n if n else v


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / ((np.linalg.norm(a) * np.linalg.norm(b)) or 1.0))
