from __future__ import annotations
import uuid
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any, Dict, List
from canonical import NormalizedPost, Author
from utils.hash_utils import compute_canonical_hash
from utils.date_utils import iso8601 
from .BaseAdapter import BaseAdapter

class TwitterAdapter(BaseAdapter):
    version = "twitter_v1"
    def parse(self, raw: Dict[str, Any]) -> List[NormalizedPost]:
        out: List[NormalizedPost] = []
        data = raw.get("data", [])
        fetched_at = datetime.now(timezone.utc).isoformat()
        for item in data:
            post_id = item.get("id")
            text = item.get("text")
            created_at = iso8601(item.get("created_at"))
            metrics = {}
            pm = item.get("public_metrics", {})
            metrics["likes"] = pm.get("like_count")
            metrics["shares"] = pm.get("retweet_count")
            metrics["comments"] = pm.get("reply_count")
            metrics["quotes"] = pm.get("quote_count")
            metrics["views"] = pm.get("impression_count")
            # author not in example; leave blank but keep raw in provenance
            author = Author(id=None, username=None, name=None, profile_url=None, raw={})
            canonical_hash = compute_canonical_hash("twitter", post_id, text, asdict(author))
            np = NormalizedPost(
                _id=str(uuid.uuid4()),
                provider="twitter",
                post_id=post_id,
                url=None,
                author=author,
                content_text=text,
                media=[],
                metrics=metrics,
                reactions=[],
                comments=[],
                tags=[],
                created_at=created_at,
                fetched_at=fetched_at,
                canonical_hash=canonical_hash,
                provenance={"raw": item, "adapter_version": self.version}
            )
            out.append(np)
        return out