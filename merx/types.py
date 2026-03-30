from dataclasses import dataclass
from typing import Optional


class MerxError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


@dataclass
class PricePoint:
    duration_sec: int
    price_sun: int


@dataclass
class ProviderPrice:
    provider: str
    is_market: bool
    energy_prices: list[PricePoint]
    bandwidth_prices: list[PricePoint]
    available_energy: int
    available_bandwidth: int
    fetched_at: int


@dataclass
class Balance:
    trx: float
    usdt: float
    trx_locked: float
    updated_at: Optional[str] = None


@dataclass
class Order:
    id: str
    resource_type: str
    order_type: str
    status: str
    amount: int
    target_address: str
    duration_sec: int
    total_cost_sun: Optional[int] = None
    total_fee_sun: Optional[int] = None
    created_at: str = ""
    filled_at: Optional[str] = None
    expires_at: Optional[str] = None


@dataclass
class Fill:
    provider: str
    amount: int
    price_sun: int
    cost_sun: int
    tx_id: Optional[str] = None
    status: str = ""
    delegation_tx: Optional[str] = None
    verified: bool = False
    tronscan_url: Optional[str] = None


@dataclass
class OrderWithFills(Order):
    fills: list[Fill] = None  # type: ignore[assignment]

    def __post_init__(self):
        if self.fills is None:
            self.fills = []


@dataclass
class HistoryEntry:
    id: str
    order_id: str
    provider: str
    amount: int
    price_sun: int
    cost_sun: int
    resource_type: str
    created_at: str
    tx_id: Optional[str] = None
    confirmed_at: Optional[str] = None


@dataclass
class HistorySummary:
    total_orders: int
    total_energy: int
    total_spent_sun: int
    avg_price_sun: float


@dataclass
class DepositInfo:
    address: str
    memo: str
    min_amount_trx: float
    min_amount_usdt: float


@dataclass
class Withdrawal:
    id: str
    status: str
    amount: int
    currency: str
    address: str


@dataclass
class PreviewMatch:
    provider: str
    displayName: str
    price_sun: int
    cost_trx: str
    duration_sec: int


@dataclass
class OrderPreview:
    best: Optional[PreviewMatch]
    fallbacks: list[PreviewMatch]
    no_providers: bool


@dataclass
class PriceStats:
    cheapest_changes_24h: int
    total_providers: int
    best_price_sun: int
    avg_price_sun: int


@dataclass
class PriceHistoryEntry:
    provider: str
    resource_type: str
    price_sun: int
    available: int
    is_online: bool
    polled_at: str


@dataclass
class Webhook:
    id: str
    url: str
    events: list[str]
    is_active: bool
    created_at: str
    secret: Optional[str] = None
