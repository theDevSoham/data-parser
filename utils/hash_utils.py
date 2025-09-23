from typing import Any, Dict, Optional
import hashlib 

def compute_canonical_hash(provider: str, source_id: Optional[str], text: Optional[str], author: Optional[Dict[str, Any]]) -> str:
    """
    Deterministic hash used for deduplication/idempotency. Prefer provider:source_id when available.
    """
    if source_id:
        key = f"{provider}:{source_id}"
    else:
        # fallback key composed of text+author+short timestamp / uuid
        author_key = author.get("username") if author else ""
        text_part = (text or "")[:400]
        key = f"{provider}|{author_key}|{text_part}"
    h = hashlib.sha256(key.encode("utf-8")).hexdigest()
    return f"sha256:{h}"