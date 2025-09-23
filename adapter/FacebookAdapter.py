from __future__ import annotations
import uuid
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any, Dict, List
from canonical import NormalizedPost, Author, Media
from utils.hash_utils import compute_canonical_hash
from utils.date_utils import iso8601 
from .BaseAdapter import BaseAdapter

class FacebookAdapter(BaseAdapter):
    version = "facebook_v1"
    def parse(self, raw: Dict[str, Any]) -> List[NormalizedPost]:
        out: List[NormalizedPost] = []
        data = raw.get("data", [])
        fetched_at = datetime.now(timezone.utc).isoformat()
        for item in data:
            post_id = item.get("id")
            created_at = iso8601(item.get("created_time"))
            url = item.get("permalink_url")
            # content / message may be under "message" or "story" etc.
            text = item.get("message") or item.get("story") or None
            # attachments mapping:
            media = []
            attachments = item.get("attachments", {}).get("data", [])
            for a in attachments:
                mtype = a.get("media_type") or a.get("type") or "link"
                media_url = a.get("url") or a.get("media", {}).get("url")
                media.append(Media(type=mtype, url=media_url))
            # reactions summary and comments summary
            metrics = {}
            reactions_summary = item.get("reactions", {}).get("summary", {})
            metrics["likes"] = reactions_summary.get("total_count", 0)
            comments_summary = item.get("comments", {}).get("summary", {})
            metrics["comments"] = comments_summary.get("total_count", 0)
            metrics["shares"] = item.get("shares", {}).get("count", 0) if item.get("shares") else 0
            # build author if present in raw (facebook often includes 'from' on comment objects; posts may not have easily)
            author = Author(id=None, username=None, name=None, profile_url=None, raw={})
            canonical_hash = compute_canonical_hash("facebook", post_id, text, asdict(author))
            np = NormalizedPost(
                _id=str(uuid.uuid4()),
                provider="facebook",
                post_id=post_id,
                url=url,
                author=author,
                content_text=text,
                media=media,
                metrics=metrics,
                reactions=[],  # reactions data may be paged; store summary in metrics and expand later
                comments=[],  # comments data is often nested; we leave for enrichment
                tags=[],
                created_at=created_at,
                fetched_at=fetched_at,
                canonical_hash=canonical_hash,
                provenance={"raw": item, "adapter_version": self.version}
            )
            out.append(np)
        return out