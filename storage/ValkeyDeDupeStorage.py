# storage/ValkeyDedupeStorage.py
from typing import Optional
import valkey  # pip install valkey
import os


class ValkeyDedupeStorage:
    """
    Deduplication store backed by Valkey (Redis).
    Uses SETNX (SET with NX) for atomic insert and optional TTL.
    """

    def __init__(
        self,
        host: str = None,
        port: int = None,
        db: int = 0,
        ttl_seconds: Optional[int] = 7 * 24 * 3600,  # default: 7 days
    ):
        host = host or os.getenv("VALKEY_HOST", "localhost")
        port = port or int(os.getenv("VALKEY_PORT", "6379"))

        self._client = valkey.Valkey(host=host, port=port, db=db)
        self._ttl = ttl_seconds
        self._client.flushall()

    def claim(self, canonical_hash: str) -> bool:
        """
        Attempt to claim a hash.
        Returns True if this is the first time we've seen it.
        Returns False if it's already claimed.
        """
        try:
            if self._ttl:
                # NX ensures only first writer wins, EX sets TTL
                result = self._client.set(canonical_hash, "1", ex=self._ttl, nx=True)
            else:
                result = self._client.set(canonical_hash, "1", nx=True)

            return result is True
        except Exception as e:
            raise RuntimeError(f"Valkey claim failed: {e}")

    def exists(self, canonical_hash: str) -> bool:
        """Check if a hash already exists."""
        try:
            return bool(self._client.exists(canonical_hash))
        except Exception as e:
            raise RuntimeError(f"Valkey exists check failed: {e}")

    def release(self, canonical_hash: str) -> None:
        """Optionally remove a hash (if you want to allow reprocessing)."""
        try:
            self._client.delete(canonical_hash)
        except Exception as e:
            raise RuntimeError(f"Valkey release failed: {e}")
