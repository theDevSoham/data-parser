from dataclasses import dataclass, field
from typing import Any, Dict, Optional

@dataclass
class Author:
    id: Optional[str] = None
    username: Optional[str] = None
    name: Optional[str] = None
    profile_url: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict)