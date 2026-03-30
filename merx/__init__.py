from .balance import BalanceModule
from .client import HttpClient
from .orders import OrdersModule
from .prices import PricesModule
from .webhooks import WebhooksModule
from .types import (
    Balance,
    DepositInfo,
    Fill,
    HistoryEntry,
    HistorySummary,
    MerxError,
    Order,
    OrderPreview,
    OrderWithFills,
    PreviewMatch,
    PriceHistoryEntry,
    PricePoint,
    PriceStats,
    ProviderPrice,
    Webhook,
    Withdrawal,
)

__version__ = "0.1.0"
__all__ = [
    "MerxClient",
    "MerxError",
    "Balance",
    "DepositInfo",
    "Fill",
    "HistoryEntry",
    "HistorySummary",
    "Order",
    "OrderPreview",
    "OrderWithFills",
    "PreviewMatch",
    "PriceHistoryEntry",
    "PricePoint",
    "PriceStats",
    "ProviderPrice",
    "Webhook",
    "Withdrawal",
]


class MerxClient:
    def __init__(self, api_key: str, base_url: str = "https://merx.exchange"):
        http = HttpClient(api_key, base_url)
        self.prices = PricesModule(http)
        self.orders = OrdersModule(http)
        self.balance = BalanceModule(http)
        self.webhooks = WebhooksModule(http)
