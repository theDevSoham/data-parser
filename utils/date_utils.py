from typing import Optional

def iso8601(dt: Optional[str]) -> Optional[str]:
    """Normalize common timestamp strings to ISO8601 UTC (naive implementation)."""
    if not dt:
        return None
    try:
        # try parsing common ISO formats (very permissive)
        # Note: in prod use dateutil.parser.parse
        if dt.endswith("Z"):
            return dt
        # handle +0000 or +00:00
        if "+" in dt:
            # turn +0000 into Z if offset is 0
            # naive: assume UTC offsets -> convert to Z for storage, keep original otherwise
            base, _, offset = dt.partition("+")
            if offset.startswith("0000") or offset.startswith("00:00"):
                return base + "Z"
            return dt
        return dt
    except Exception:
        return dt