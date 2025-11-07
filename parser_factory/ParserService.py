from storage import Storage, ValkeyDedupeStorage
from adapter import BaseAdapter, TwitterAdapter, FacebookAdapter
from typing import Dict, Any, Tuple
from config.Config import SOCIAL_AUTHENTICATOR_URL
import requests

class ParserService:
    def __init__(self, storage: Storage, dedupe: ValkeyDedupeStorage):
        self._storage = storage
        self._dedupe = dedupe
        self._users_data = None
        self.adapters = {
            "twitter": TwitterAdapter(),
            "facebook": FacebookAdapter()
        }

    def register_adapter(self, provider: str, adapter: BaseAdapter) -> None:
        self.adapters[provider] = adapter

    def process_raw(self, provider: str, raw_payload: Dict[str, Any], app_token: str) -> Tuple[int, int]:
        """
        Returns (inserted_count, skipped_count)
        """

        users_data = self._get_user_details(app_token=app_token)

        adapter = self.adapters.get(provider)
        if not adapter:
            raise ValueError(f"No adapter registered for provider '{provider}'")
        normalized_posts = adapter.parse(raw_payload, users_data)
        inserted = 0
        skipped = 0
        for post in normalized_posts:
            key = post.canonical_hash
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
    
    def _get_user_details(self, app_token: str):
        """
        Fetches user details from the social authenticator service using the given app token.
        Returns normalized user details with only the relevant fields.
        """
        try:
            url = f"{SOCIAL_AUTHENTICATOR_URL.rstrip('/')}/get_user"
            headers = {"Authorization": f"Bearer {app_token}"}
            print(app_token)

            response = requests.get(url, headers=headers)
            response.raise_for_status()

            data = response.json()
            claims = data.get("claims", {})

            normalized_details = {
                "provider": claims.get("provider"),
                "social_id": claims.get("social_id"),
                "social_token": claims.get("social_token"),
                "name": claims.get("name"),
                "email": claims.get("email"),
                "sub": claims.get("sub"),
            }

            print(f"Retrieved user details for provider: {normalized_details['provider']}")
            return normalized_details

        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch user details: {e}")
        except Exception as e:
            raise Exception(f"Error while processing user details: {e}")