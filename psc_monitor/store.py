import json
from pathlib import Path

import numpy as np

DEFAULT_PATH = Path("data/baseline.json")


def save_baseline(path, url, backend, embedding, text_hash):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        "url": url, "backend": backend, "text_sha256": text_hash,
        "embedding": embedding.tolist(),
    }))


def load_baseline(path):
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"لا يوجد baseline في {path} — شغّل المرحلة الأولى أولًا.")
    d = json.loads(path.read_text())
    d["embedding"] = np.array(d["embedding"])
    return d
