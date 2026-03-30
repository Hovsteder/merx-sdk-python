from __future__ import annotations

from .client import HttpClient
from .types import Webhook


class WebhooksModule:
    def __init__(self, http: HttpClient):
        self._http = http

    def create(self, url: str, events: list[str]) -> Webhook:
        data = self._http.post("/api/v1/webhooks", {"url": url, "events": events})
        return Webhook(
            id=data["id"],
            url=data["url"],
            events=data["events"],
            is_active=data.get("is_active", True),
            created_at=data.get("created_at", ""),
            secret=data.get("secret"),
        )

    def list(self) -> list[Webhook]:
        data = self._http.get("/api/v1/webhooks")
        return [
            Webhook(
                id=w["id"],
                url=w["url"],
                events=w["events"],
                is_active=w.get("is_active", True),
                created_at=w.get("created_at", ""),
            )
            for w in (data or [])
        ]

    def delete(self, webhook_id: str) -> bool:
        data = self._http.delete(f"/api/v1/webhooks/{webhook_id}")
        return data.get("deleted", False) if isinstance(data, dict) else False
