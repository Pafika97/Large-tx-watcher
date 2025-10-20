# utils.py
import requests
from decimal import Decimal, getcontext

# Устанавливаем достаточную точность
getcontext().prec = 36

COINGECKO_SIMPLE_PRICE = "https://api.coingecko.com/api/v3/simple/price"

def fetch_price_usd(symbol: str) -> Decimal:
    """Получить цену в USD для токена (по ID CoinGecko)."""
    try:
        params = {"ids": symbol.lower(), "vs_currencies": "usd"}
        r = requests.get(COINGECKO_SIMPLE_PRICE, params=params, timeout=8)
        r.raise_for_status()
        data = r.json()
        if data and symbol.lower() in data and "usd" in data[symbol.lower()]:
            return Decimal(str(data[symbol.lower()]["usd"]))
    except Exception:
        pass
    return Decimal("0")

def token_amount_to_decimal(raw_amount: str, decimals: int) -> Decimal:
    """Преобразуем сырой amount (строка-инт) с учётом decimals в Decimal."""
    a = Decimal(raw_amount)
    denom = Decimal(10) ** Decimal(decimals)
    return a / denom

def usd_value_from_amount(symbol: str, amount_decimal: Decimal, price_override: Decimal=None) -> Decimal:
    """USD value = price * amount_decimal (округление до центов)."""
    price = price_override if price_override is not None else fetch_price_usd(symbol)
    return (price * amount_decimal).quantize(Decimal("0.01"))
