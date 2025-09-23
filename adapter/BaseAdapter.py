from typing import Protocol, Dict, Any, List
from canonical import NormalizedPost

class BaseAdapter(Protocol):
    def parse(self, raw: Dict[str, Any]) -> List[NormalizedPost]:
        ...
