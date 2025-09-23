from dataclasses import dataclass, asdict, field
from typing import Any, Dict, List, Optional
from .Author import Author
from .Media import Media
from .Reaction import Reaction
from .Comment import Comment 

@dataclass
class NormalizedPost:
    _id: str
    provider: str
    post_id: Optional[str]
    url: Optional[str]
    author: Author
    content_text: Optional[str]
    media: List[Media]
    metrics: Dict[str, Any]
    reactions: List[Reaction]
    comments: List[Comment]
    tags: List[str]
    created_at: Optional[str]
    fetched_at: str
    schema_version: int = 1
    canonical_hash: str = ""
    provenance: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)