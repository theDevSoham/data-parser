from dataclasses import dataclass, field
from typing import Any, Dict, Optional

@dataclass
class Media:
    type: str
    url: Optional[str] = None
    meta: Dict[str, Any] = field(default_factory=dict)