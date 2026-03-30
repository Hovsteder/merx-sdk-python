from __future__ import annotations

from typing import Optional

from .client import HttpClient
from .types import Balance, DepositInfo, HistoryEntry, HistorySummary, Withdrawal


def _parse_history(d: dict) -> HistoryEntry:
    return HistoryEntry(
        id=d["id"],
        order_id=d.get("order_id", ""),
        provider=d.get("provider", ""),
        amount=d.get("amount", 0),
        price_sun=d.get("price_sun", 0),
        cost_sun=d.get("cost_sun", 0),
        resource_type=d.get("resource_type", "ENERGY"),
        created_at=d.get("created_at", ""),
        tx_id=d.get("tx_id"),
        confirmed_at=d.get("confirmed_at"),
    )


class BalanceModule:
    def __init__(self, http: HttpClient):
        self._http = http

    def get(self) -> Balance:
        data = self._http.get("/api/v1/balance")
        return Balance(
            trx=data.get("trx", 0),
            usdt=data.get("usdt", 0),
            trx_locked=data.get("trx_locked", 0),
            updated_at=data.get("updated_at"),
        )

    def deposit_info(self) -> DepositInfo:
        data = self._http.get("/api/v1/deposit/info")
        return DepositInfo(
            address=data["address"],
            memo=data["memo"],
            min_amount_trx=data.get("min_amount_trx", 0),
            min_amount_usdt=data.get("min_amount_usdt", 0),
        )

    def withdraw(
        self,
        address: str,
        amount: int,
        currency: str = "TRX",
        idempotency_key: Optional[str] = None,
    ) -> Withdrawal:
        payload = {"address": address, "amount": amount, "currency": currency}
        headers = {}
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        data = self._http.post("/api/v1/withdraw", payload, headers or None)
        return Withdrawal(
            id=data["id"],
            status=data["status"],
            amount=data["amount"],
            currency=data["currency"],
            address=data["address"],
        )

    def history(self, period: str = "30D") -> list[HistoryEntry]:
        data = self._http.get(f"/api/v1/history?period={period}")
        return [_parse_history(e) for e in (data or [])]

    def summary(self) -> HistorySummary:
        data = self._http.get("/api/v1/history/summary")
        return HistorySummary(
            total_orders=data.get("total_orders", 0),
            total_energy=data.get("total_energy", 0),
            total_spent_sun=data.get("total_spent_sun", 0),
            avg_price_sun=data.get("avg_price_sun", 0),
        )
