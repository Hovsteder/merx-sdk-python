from __future__ import annotations

from typing import Optional
from urllib.parse import urlencode

from .client import HttpClient
from .types import (
    OrderPreview,
    PreviewMatch,
    PriceHistoryEntry,
    PricePoint,
    PriceStats,
    ProviderPrice,
)


def _parse_price(d: dict) -> ProviderPrice:
    return ProviderPrice(
        provider=d["provider"],
        is_market=d.get("is_market", False),
        energy_prices=[PricePoint(**p) for p in d.get("energy_prices", [])],
        bandwidth_prices=[PricePoint(**p) for p in d.get("bandwidth_prices", [])],
        available_energy=d.get("available_energy", 0),
        available_bandwidth=d.get("available_bandwidth", 0),
        fetched_at=d.get("fetched_at", 0),
    )


def _parse_history_entry(d: dict) -> PriceHistoryEntry:
    return PriceHistoryEntry(
        provider=d["provider"],
        resource_type=d["resource_type"],
        price_sun=d["price_sun"],
        available=d.get("available", 0),
        is_online=d.get("is_online", True),
        polled_at=d["polled_at"],
    )


class PricesModule:
    def __init__(self, http: HttpClient):
        self._http = http

    def list(self) -> list[ProviderPrice]:
        data = self._http.get("/api/v1/prices")
        return [_parse_price(p) for p in (data or [])]

    def best(
        self, resource: str, amount: Optional[int] = None
    ) -> PriceHistoryEntry:
        params: dict[str, str] = {"resource": resource}
        if amount:
            params["amount"] = str(amount)
        data = self._http.get(f"/api/v1/prices/best?{urlencode(params)}")
        return _parse_history_entry(data)

    def history(
        self,
        provider: Optional[str] = None,
        resource: Optional[str] = None,
        period: str = "24h",
    ) -> list[PriceHistoryEntry]:
        params: dict[str, str] = {"period": period}
        if provider:
            params["provider"] = provider
        if resource:
            params["resource"] = resource
        data = self._http.get(f"/api/v1/prices/history?{urlencode(params)}")
        return [_parse_history_entry(e) for e in (data or [])]

    def stats(self) -> PriceStats:
        data = self._http.get("/api/v1/prices/stats")
        return PriceStats(**data)

    def preview(
        self,
        resource: str,
        amount: int,
        duration: int,
        max_price_sun: Optional[int] = None,
    ) -> OrderPreview:
        params: dict[str, str] = {
            "resource": resource,
            "amount": str(amount),
            "duration": str(duration),
        }
        if max_price_sun:
            params["max_price_sun"] = str(max_price_sun)
        data = self._http.get(f"/api/v1/orders/preview?{urlencode(params)}")
        best = PreviewMatch(**data["best"]) if data.get("best") else None
        fallbacks = [PreviewMatch(**f) for f in data.get("fallbacks", [])]
        return OrderPreview(
            best=best,
            fallbacks=fallbacks,
            no_providers=data.get("no_providers", False),
        )
