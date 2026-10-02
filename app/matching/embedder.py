from functools import lru_cache

import numpy as np
from fastembed import TextEmbedding


import os
os.environ["HF_HUB_DISABLE_XET"] = "1"          # use the regular HTTP download
os.environ["HF_HUB_DOWNLOAD_TIMEOUT"] = "600"   # longer timeout for slow networks
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"


@lru_cache(maxsize=1)
def _model() -> TextEmbedding:
    return TextEmbedding(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    cache_dir=r"D:\Document\AI AGENT\resume-matcher\models_cache",
    local_files_only=True,
    )


def embed(texts: list[str]) -> np.ndarray:
    vecs = np.array(list(_model().embed(texts)), dtype="float32")
    norms = np.linalg.norm(vecs, axis=1, keepdims=True)
    return vecs / np.clip(norms, 1e-12, None)