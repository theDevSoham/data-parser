from dataclasses import dataclass
from typing import Optional

@dataclass
class Reaction:
    user_id: Optional[str]
    reaction_type: Optional[str]
    timestamp: Optional[str]