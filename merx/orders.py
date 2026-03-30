from __future__ import annotations

from typing import Optional
from urllib.parse import urlencode

from .client import HttpClient
from .types import Fill, Order, OrderWithFills


def _parse_order(d: dict) -> Order:
    return Order(
        id=d["id"],
        resource_type=d["resource_type"],
        order_type=d.get("order_type", "MARKET"),
        status=d["status"],
        amount=d["amount"],
        target_address=d.get("target_address", ""),
        duration_sec=d.get("duration_sec", 0),
        total_cost_sun=d.get("total_cost_sun"),
        total_fee_sun=d.get("total_fee_sun"),
        created_at=d.get("created_at", ""),
        filled_at=d.get("filled_at"),
        expires_at=d.get("expires_at"),
    )


def _parse_fill(d: dict) -> Fill:
    return Fill(
        provider=d["provider"],
        amount=d["amount"],
        price_sun=d["price_sun"],
        cost_sun=d["cost_sun"],
        tx_id=d.get("tx_id"),
        status=d.get("status", ""),
        delegation_tx=d.get("delegation_tx"),
        verified=d.get("verified", False),
        tronscan_url=d.get("tronscan_url"),
    )


class OrdersModule:
    def __init__(self, http: HttpClient):
        self._http = http

    def create(
        self,
        resource_type: str,
        amount: int,
        duration_sec: int,
        target_address: str,
        order_type: str = "MARKET",
        max_price_sun: Optional[int] = None,
        idempotency_key: Optional[str] = None,
    ) -> Order:
        payload: dict = {
            "resource_type": resource_type,
            "order_type": order_type,
            "amount": amount,
            "duration_sec": duration_sec,
            "target_address": target_address,
        }
        if max_price_sun is not None:
            payload["max_price_sun"] = max_price_sun
        headers = {}
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        data = self._http.post("/api/v1/orders", payload, headers or None)
        return _parse_order(data)

    def list(
        self, limit: int = 30, offset: int = 0, status: Optional[str] = None
    ) -> tuple[list[Order], int]:
        params: dict[str, str] = {"limit": str(limit), "offset": str(offset)}
        if status:
            params["status"] = status
        data = self._http.get(f"/api/v1/orders?{urlencode(params)}")
        orders = [_parse_order(o) for o in data.get("orders", [])]
        return orders, data.get("total", 0)

    def get(self, order_id: str) -> OrderWithFills:
        data = self._http.get(f"/api/v1/orders/{order_id}")
        fills = [_parse_fill(f) for f in data.get("fills", []) or []]
        return OrderWithFills(
            id=data["id"],
            resource_type=data["resource_type"],
            order_type=data.get("order_type", "MARKET"),
            status=data["status"],
            amount=data["amount"],
            target_address=data.get("target_address", ""),
            duration_sec=data.get("duration_sec", 0),
            total_cost_sun=data.get("total_cost_sun"),
            total_fee_sun=data.get("total_fee_sun"),
            created_at=data.get("created_at", ""),
            filled_at=data.get("filled_at"),
            expires_at=data.get("expires_at"),
            fills=fills,
        )
