# MERX SDK for Python

### https://MERX.exchange

Official Python SDK for the MERX TRON resource exchange.

[![PyPI version](https://img.shields.io/pypi/v/merx-sdk)](https://pypi.org/project/merx-sdk/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](https://python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-zero-brightgreen)]()

MERX aggregates TRON energy and bandwidth providers into a single exchange with real-time pricing, automatic best-price routing, and a programmatic API. This SDK wraps the full MERX REST API in typed Python dataclasses with zero external dependencies.

---

## Install

```bash
pip install merx-sdk
```

Requires Python 3.11 or later. No external dependencies -- uses only the standard library (`urllib` + `json`).

---

## Quick Start

```python
from merx import MerxClient

client = MerxClient(api_key="your-api-key")

# 1. Check current prices from all providers
prices = client.prices.list()
for p in prices:
    print(f"{p.provider}: {p.available_energy} energy available")

# 2. Create a market order for 100,000 energy
order = client.orders.create(
    resource_type="ENERGY",
    amount=100_000,
    duration_sec=3600,
    target_address="TXyz...your-address",
)
print(f"Order {order.id} status: {order.status}")

# 3. Check your account balance
balance = client.balance.get()
print(f"TRX: {balance.trx}, USDT: {balance.usdt}")
```

---

## Modules

The `MerxClient` exposes four modules: `prices`, `orders`, `balance`, and `webhooks`. Each method returns typed dataclasses.

---

### client.prices

Real-time price data from all connected TRON resource providers.

#### `list() -> list[ProviderPrice]`

Returns current prices from every active provider.

```python
prices = client.prices.list()
for provider in prices:
    print(f"{provider.provider}:")
    print(f"  Energy available: {provider.available_energy}")
    for ep in provider.energy_prices:
        print(f"  {ep.duration_sec}s -> {ep.price_sun} SUN")
```

#### `best(resource, amount?) -> PriceHistoryEntry`

Returns the single best (cheapest) price for a given resource type.

| Parameter  | Type           | Default  | Description                          |
|------------|----------------|----------|--------------------------------------|
| `resource` | `str`          | required | `"ENERGY"` or `"BANDWIDTH"`         |
| `amount`   | `int` or `None`| `None`   | Optional minimum available amount    |

```python
best = client.prices.best("ENERGY")
print(f"Best price: {best.price_sun} SUN from {best.provider}")
```

#### `history(provider?, resource?, period?) -> list[PriceHistoryEntry]`

Returns historical price snapshots.

| Parameter  | Type           | Default | Description                                 |
|------------|----------------|---------|---------------------------------------------|
| `provider` | `str` or `None`| `None`  | Filter by provider name                     |
| `resource` | `str` or `None`| `None`  | `"ENERGY"` or `"BANDWIDTH"`                 |
| `period`   | `str`          | `"24h"` | Time range: `"1h"`, `"24h"`, `"7d"`, `"30d"` |

```python
history = client.prices.history(provider="sohu", resource="ENERGY", period="7d")
for entry in history:
    print(f"{entry.polled_at}: {entry.price_sun} SUN ({entry.available} available)")
```

#### `stats() -> PriceStats`

Returns aggregate price statistics.

```python
stats = client.prices.stats()
print(f"Best price: {stats.best_price_sun} SUN")
print(f"Average price: {stats.avg_price_sun} SUN")
print(f"Active providers: {stats.total_providers}")
print(f"Cheapest changed {stats.cheapest_changes_24h}x in 24h")
```

#### `preview(resource, amount, duration, max_price_sun?) -> OrderPreview`

Simulates an order to show which providers would fill it and at what cost, without actually placing the order.

| Parameter       | Type           | Default  | Description                            |
|-----------------|----------------|----------|----------------------------------------|
| `resource`      | `str`          | required | `"ENERGY"` or `"BANDWIDTH"`            |
| `amount`        | `int`          | required | Amount of resource to acquire           |
| `duration`      | `int`          | required | Duration in seconds                     |
| `max_price_sun` | `int` or `None`| `None`   | Maximum acceptable price per unit (SUN) |

```python
preview = client.prices.preview("ENERGY", 100_000, 3600)
if preview.best:
    print(f"Best: {preview.best.provider} at {preview.best.price_sun} SUN")
    print(f"Total cost: {preview.best.cost_trx} TRX")
for fb in preview.fallbacks:
    print(f"Fallback: {fb.provider} at {fb.price_sun} SUN")
```

---

### client.orders

Create and manage resource orders.

#### `create(resource_type, amount, duration_sec, target_address, order_type?, max_price_sun?, idempotency_key?) -> Order`

Places a new order for TRON energy or bandwidth.

| Parameter         | Type           | Default    | Description                              |
|-------------------|----------------|------------|------------------------------------------|
| `resource_type`   | `str`          | required   | `"ENERGY"` or `"BANDWIDTH"`              |
| `amount`          | `int`          | required   | Amount of resource to acquire             |
| `duration_sec`    | `int`          | required   | Duration in seconds (e.g. `3600`)         |
| `target_address`  | `str`          | required   | TRON address to receive the delegation    |
| `order_type`      | `str`          | `"MARKET"` | `"MARKET"` or `"LIMIT"`                  |
| `max_price_sun`   | `int` or `None`| `None`     | Max price per unit (required for LIMIT)   |
| `idempotency_key` | `str` or `None`| `None`     | Unique key to prevent duplicate orders    |

```python
order = client.orders.create(
    resource_type="ENERGY",
    amount=100_000,
    duration_sec=3600,
    target_address="TXyz...your-address",
    idempotency_key="order-abc-123",
)
print(f"Order {order.id}: {order.status}")
```

#### `list(limit?, offset?, status?) -> tuple[list[Order], int]`

Returns a paginated list of your orders and the total count.

| Parameter | Type           | Default | Description                                    |
|-----------|----------------|---------|------------------------------------------------|
| `limit`   | `int`          | `30`    | Number of orders to return                      |
| `offset`  | `int`          | `0`     | Number of orders to skip                        |
| `status`  | `str` or `None`| `None`  | Filter: `"PENDING"`, `"FILLED"`, `"EXPIRED"`, etc. |

```python
orders, total = client.orders.list(limit=10, status="FILLED")
print(f"Showing {len(orders)} of {total} filled orders")
for o in orders:
    print(f"  {o.id}: {o.amount} {o.resource_type} -> {o.target_address}")
```

#### `get(order_id) -> OrderWithFills`

Returns a single order with its fill details (which providers filled it and at what price).

```python
detail = client.orders.get("ord_abc123")
print(f"Order status: {detail.status}")
print(f"Total cost: {detail.total_cost_sun} SUN")
for fill in detail.fills:
    print(f"  {fill.provider}: {fill.amount} units at {fill.price_sun} SUN")
    if fill.tronscan_url:
        print(f"    TX: {fill.tronscan_url}")
```

---

### client.balance

Account balance, deposits, withdrawals, and transaction history.

#### `get() -> Balance`

Returns the current account balance.

```python
balance = client.balance.get()
print(f"TRX: {balance.trx}")
print(f"USDT: {balance.usdt}")
print(f"TRX locked in orders: {balance.trx_locked}")
```

#### `deposit_info() -> DepositInfo`

Returns your unique deposit address and memo.

```python
info = client.balance.deposit_info()
print(f"Deposit address: {info.address}")
print(f"Memo: {info.memo}")
print(f"Min deposit: {info.min_amount_trx} TRX / {info.min_amount_usdt} USDT")
```

#### `withdraw(address, amount, currency?, idempotency_key?) -> Withdrawal`

Initiates a withdrawal from your MERX account.

| Parameter         | Type           | Default | Description                           |
|-------------------|----------------|---------|---------------------------------------|
| `address`         | `str`          | required| Destination TRON address              |
| `amount`          | `int`          | required| Amount to withdraw (in SUN for TRX)   |
| `currency`        | `str`          | `"TRX"` | `"TRX"` or `"USDT"`                  |
| `idempotency_key` | `str` or `None`| `None`  | Unique key to prevent duplicates      |

```python
withdrawal = client.balance.withdraw(
    address="TXyz...destination",
    amount=10_000_000,
    currency="TRX",
    idempotency_key="withdraw-001",
)
print(f"Withdrawal {withdrawal.id}: {withdrawal.status}")
```

#### `history(period?) -> list[HistoryEntry]`

Returns transaction history (order fills, deposits, withdrawals).

| Parameter | Type  | Default | Description                               |
|-----------|-------|---------|-------------------------------------------|
| `period`  | `str` | `"30D"` | Time range: `"24h"`, `"7d"`, `"30D"`, etc. |

```python
entries = client.balance.history(period="7d")
for entry in entries:
    print(f"{entry.created_at}: {entry.resource_type} {entry.amount} ({entry.cost_sun} SUN)")
```

#### `summary() -> HistorySummary`

Returns aggregate statistics for your account history.

```python
summary = client.balance.summary()
print(f"Total orders: {summary.total_orders}")
print(f"Total energy acquired: {summary.total_energy}")
print(f"Total spent: {summary.total_spent_sun} SUN")
print(f"Average price: {summary.avg_price_sun} SUN/unit")
```

---

### client.webhooks

Register HTTP endpoints to receive real-time event notifications.

#### `create(url, events) -> Webhook`

Creates a new webhook subscription.

| Parameter | Type         | Default  | Description                                     |
|-----------|--------------|----------|-------------------------------------------------|
| `url`     | `str`        | required | HTTPS endpoint to receive POST notifications    |
| `events`  | `list[str]`  | required | Events to subscribe to (see list below)         |

Available events:
- `order.filled` -- Order has been fully filled
- `order.partial` -- Order has been partially filled
- `order.expired` -- Order expired before being filled
- `deposit.confirmed` -- Deposit has been confirmed
- `withdrawal.completed` -- Withdrawal has been sent

```python
webhook = client.webhooks.create(
    url="https://your-server.com/webhooks/merx",
    events=["order.filled", "deposit.confirmed"],
)
print(f"Webhook {webhook.id} created")
print(f"Signing secret: {webhook.secret}")
```

#### `list() -> list[Webhook]`

Returns all registered webhooks.

```python
webhooks = client.webhooks.list()
for wh in webhooks:
    print(f"{wh.id}: {wh.url} ({', '.join(wh.events)})")
```

#### `delete(webhook_id) -> bool`

Deletes a webhook. Returns `True` if the webhook was deleted.

```python
deleted = client.webhooks.delete("wh_abc123")
print(f"Deleted: {deleted}")
```

---

## Types

All return values are typed Python dataclasses. Import them directly if needed:

```python
from merx import (
    ProviderPrice,
    PricePoint,
    PriceStats,
    PriceHistoryEntry,
    Balance,
    DepositInfo,
    Order,
    OrderWithFills,
    OrderPreview,
    PreviewMatch,
    Fill,
    HistoryEntry,
    HistorySummary,
    Withdrawal,
    Webhook,
    MerxError,
)
```

### Type reference

| Type               | Fields                                                                                   |
|--------------------|------------------------------------------------------------------------------------------|
| `ProviderPrice`    | `provider`, `is_market`, `energy_prices`, `bandwidth_prices`, `available_energy`, `available_bandwidth`, `fetched_at` |
| `PricePoint`       | `duration_sec`, `price_sun`                                                              |
| `PriceStats`       | `cheapest_changes_24h`, `total_providers`, `best_price_sun`, `avg_price_sun`             |
| `PriceHistoryEntry`| `provider`, `resource_type`, `price_sun`, `available`, `is_online`, `polled_at`          |
| `Balance`          | `trx`, `usdt`, `trx_locked`, `updated_at`                                               |
| `DepositInfo`      | `address`, `memo`, `min_amount_trx`, `min_amount_usdt`                                   |
| `Order`            | `id`, `resource_type`, `order_type`, `status`, `amount`, `target_address`, `duration_sec`, `total_cost_sun`, `total_fee_sun`, `created_at`, `filled_at`, `expires_at` |
| `OrderWithFills`   | All `Order` fields + `fills: list[Fill]`                                                 |
| `Fill`             | `provider`, `amount`, `price_sun`, `cost_sun`, `tx_id`, `status`, `delegation_tx`, `verified`, `tronscan_url` |
| `OrderPreview`     | `best: PreviewMatch`, `fallbacks: list[PreviewMatch]`, `no_providers: bool`              |
| `PreviewMatch`     | `provider`, `displayName`, `price_sun`, `cost_trx`, `duration_sec`                       |
| `HistoryEntry`     | `id`, `order_id`, `provider`, `amount`, `price_sun`, `cost_sun`, `resource_type`, `created_at`, `tx_id`, `confirmed_at` |
| `HistorySummary`   | `total_orders`, `total_energy`, `total_spent_sun`, `avg_price_sun`                       |
| `Withdrawal`       | `id`, `status`, `amount`, `currency`, `address`                                          |
| `Webhook`          | `id`, `url`, `events`, `is_active`, `created_at`, `secret`                               |

---

## Error Handling

All API errors raise `MerxError` with `.code` and `.message` attributes.

```python
from merx import MerxClient, MerxError

client = MerxClient(api_key="your-api-key")

try:
    order = client.orders.create(
        resource_type="ENERGY",
        amount=100_000,
        duration_sec=3600,
        target_address="TXyz...address",
    )
except MerxError as e:
    print(f"Error code: {e.code}")
    print(f"Message: {e.message}")
    # e.code examples:
    #   "INSUFFICIENT_BALANCE" - not enough TRX/USDT
    #   "INVALID_ADDRESS"      - target address is not valid
    #   "ORDER_NOT_FOUND"      - order ID does not exist
    #   "RATE_LIMIT"           - too many requests
    #   "VALIDATION_ERROR"     - invalid parameters
```

---

## Examples

### 1. Get the cheapest energy price

```python
from merx import MerxClient

client = MerxClient(api_key="your-api-key")

best = client.prices.best("ENERGY")
print(f"Cheapest energy: {best.price_sun} SUN from {best.provider}")
print(f"Available: {best.available} units")
```

### 2. Create an energy order with idempotency

```python
from merx import MerxClient, MerxError

client = MerxClient(api_key="your-api-key")

try:
    order = client.orders.create(
        resource_type="ENERGY",
        amount=200_000,
        duration_sec=3600,
        target_address="TXyz...your-address",
        idempotency_key="my-unique-key-001",
    )
    print(f"Order created: {order.id}")
    print(f"Status: {order.status}")
except MerxError as e:
    print(f"Failed: {e.code} - {e.message}")
```

### 3. Preview order cost before buying

```python
from merx import MerxClient

client = MerxClient(api_key="your-api-key")

preview = client.prices.preview("ENERGY", 100_000, 3600)

if preview.no_providers:
    print("No providers available for this request")
elif preview.best:
    print(f"Best offer: {preview.best.provider}")
    print(f"Price: {preview.best.price_sun} SUN/unit")
    print(f"Total cost: {preview.best.cost_trx} TRX")

    if preview.fallbacks:
        print(f"\n{len(preview.fallbacks)} alternative(s):")
        for alt in preview.fallbacks:
            print(f"  {alt.provider}: {alt.price_sun} SUN ({alt.cost_trx} TRX)")
```

### 4. Check account balance and history

```python
from merx import MerxClient

client = MerxClient(api_key="your-api-key")

# Current balance
balance = client.balance.get()
print(f"Available: {balance.trx} TRX, {balance.usdt} USDT")
print(f"Locked in orders: {balance.trx_locked} TRX")

# Account summary
summary = client.balance.summary()
print(f"\nLifetime stats:")
print(f"  Orders placed: {summary.total_orders}")
print(f"  Energy acquired: {summary.total_energy}")
print(f"  Total spent: {summary.total_spent_sun} SUN")
print(f"  Average price: {summary.avg_price_sun} SUN/unit")

# Recent transactions
history = client.balance.history(period="7d")
for entry in history[:5]:
    print(f"  {entry.created_at}: {entry.resource_type} x{entry.amount}")
```

### 5. Set up a webhook for order.filled

```python
from merx import MerxClient

client = MerxClient(api_key="your-api-key")

# Create webhook
webhook = client.webhooks.create(
    url="https://your-server.com/webhooks/merx",
    events=["order.filled", "order.expired"],
)
print(f"Webhook ID: {webhook.id}")
print(f"Secret: {webhook.secret}")
print("Use the secret to verify webhook signatures.")

# List all webhooks
for wh in client.webhooks.list():
    status = "active" if wh.is_active else "inactive"
    print(f"  {wh.id}: {wh.url} [{status}]")
```

---

## Configuration

```python
from merx import MerxClient

# Production (default)
client = MerxClient(api_key="your-api-key")

# Custom base URL (for self-hosted or staging)
client = MerxClient(
    api_key="your-api-key",
    base_url="https://staging.merx.exchange",
)
```

The `api_key` is required. Obtain one from your MERX dashboard at https://merx.exchange.

The `base_url` defaults to `https://merx.exchange` and should not be changed unless you are running a custom MERX deployment or connecting to a staging environment.

---

## Requirements

- Python 3.11 or later
- Zero external dependencies

The SDK uses only Python standard library modules (`urllib.request`, `urllib.parse`, `urllib.error`, `json`, `dataclasses`). No need to install `requests`, `httpx`, or any other HTTP library.

---

## Links

- MERX Platform: https://merx.exchange
- Documentation: https://merx.exchange/docs
- API Reference: https://merx.exchange/docs/api
- JavaScript SDK: [merx-sdk on npm](https://www.npmjs.com/package/merx-sdk)
- MCP Server: [merx-mcp on npm](https://www.npmjs.com/package/merx-mcp)
- GitHub: https://github.com/Hovsteder/merx-sdk-python

---

## License

MIT License. See [LICENSE](LICENSE) for details.

Copyright 2026 MERX.
