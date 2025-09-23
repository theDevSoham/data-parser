from dataclasses import dataclass, field
from typing import Any, Dict, Optional

@dataclass
class Comment:
    comment_id: Optional[str]
    user_id: Optional[str]
    username: Optional[str]
    text: Optional[str]
    created_at: Optional[str]
    likes: Optional[int] = 0
    sentiment: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict)