from storage import Storage, ValkeyDedupeStorage
from adapter import BaseAdapter, TwitterAdapter, FacebookAdapter
from typing import Dict, Any, Tuple

class ParserService:
    def __init__(self, storage: Storage, dedupe: ValkeyDedupeStorage):
        self._storage = storage
        self._dedupe = dedupe
        self.adapters = {
            "twitter": TwitterAdapter(),
            "facebook": FacebookAdapter()
        }

    def register_adapter(self, provider: str, adapter: BaseAdapter) -> None:
        self.adapters[provider] = adapter

    def process_raw(self, provider: str, raw_payload: Dict[str, Any]) -> Tuple[int, int]:
        """
        Returns (inserted_count, skipped_count)
        """
        adapter = self.adapters.get(provider)
        if not adapter:
            raise ValueError(f"No adapter registered for provider '{provider}'")
        normalized_posts = adapter.parse(raw_payload)
        inserted = 0
        skipped = 0
        for post in normalized_posts:
            key = post.canonical_hash
            print("Haha: ", key)
            ok = self._dedupe.claim(key)
            if not ok:
                skipped += 1
                continue
            # here we can optionally perform lightweight enrichment like language detection
            doc = post.to_dict()
            # storage upsert (idempotent by canonical_hash)
            self._storage.upsert_post(doc)
            inserted += 1
        return inserted, skipped