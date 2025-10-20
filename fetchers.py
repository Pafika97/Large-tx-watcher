# fetchers.py
import os
import asyncio
import json
import time
from decimal import Decimal
from utils import token_amount_to_decimal, usd_value_from_amount
from notifier import send_telegram_message, format_alert
from db import is_seen, mark_seen

THRESHOLD_USD = Decimal(os.getenv("THRESHOLD_USD", "10000000"))
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "15"))

# --- Arkham WebSocket example (pseudo) ---
import websockets

class ArkhamFetcher:
    def __init__(self, handler):
        self.ws_url = os.getenv("ARKHAM_WS_URL")
        self.api_key = os.getenv("ARKHAM_API_KEY")
        self.handler = handler

    async def run(self):
        async for _ in self._connect_loop():
            pass

    async def _connect_loop(self):
        while True:
            try:
                headers = {}
                if self.api_key:
                    headers["Authorization"] = f"Bearer {self.api_key}"
                async with websockets.connect(self.ws_url, extra_headers=headers, max_size=None) as ws:
                    # Пример подписки: уточните по документации Arkham
                    # await ws.send(json.dumps({"type": "subscribe", "filter":"large_txs"}))
                    async for msg in ws:
                        try:
                            data = json.loads(msg)
                        except Exception:
                            continue
                        await self._process_msg(data)
            except Exception as e:
                print("Arkham WS error:", e)
                await asyncio.sleep(5)

    async def _process_msg(self, data):
        txid = data.get("txid")
        if not txid:
            return
        if await is_seen(txid):
            return

        decimals = data.get("decimals", 18)
        amount_decimal = token_amount_to_decimal(str(data.get("amount", "0")), int(decimals))
        usd_value = Decimal(str(data.get("usd_value"))) if data.get("usd_value") else usd_value_from_amount(data.get("asset_symbol", "ethereum"), amount_decimal)

        if usd_value >= THRESHOLD_USD:
            tx_obj = {
                "txid": txid,
                "chain": data.get("chain"),
                "from_addr": data.get("from"),
                "to_addr": data.get("to"),
                "asset_symbol": data.get("asset_symbol"),
                "amount_decimal": str(amount_decimal),
                "usd_value": int(usd_value),
                "timestamp": int(data.get("timestamp", time.time())),
                "extra": (json.dumps(data)[:1000] if isinstance(data, dict) else str(data)[:1000]),
            }
            try:
                send_telegram_message(format_alert(tx_obj))
                await mark_seen(txid, int(time.time()))
            except Exception as e:
                print("Notifier error:", e)

# --- Nansen REST polling example (pseudo) ---
import requests

class NansenFetcher:
    def __init__(self, handler):
        self.rest_url = os.getenv("NANSEN_REST_URL")
        self.api_key = os.getenv("NANSEN_API_KEY")
        self.handler = handler

    async def run(self):
        while True:
            try:
                await self.poll_once()
            except Exception as e:
                print("Nansen poll error:", e)
            await asyncio.sleep(POLL_INTERVAL)

    async def poll_once(self):
        headers = {}
        if self.api_key:
            headers["x-api-key"] = self.api_key
        params = {"limit": 200}  # пример
        r = requests.get(self.rest_url, headers=headers, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        txs = data.get("txs", data if isinstance(data, list) else [])
        for d in txs:
            await self._process_tx(d)

    async def _process_tx(self, d):
        txid = d.get("txid")
        if not txid:
            return
        if await is_seen(txid):
            return

        decimals = d.get("decimals", 18)
        amount_decimal = token_amount_to_decimal(str(d.get("amount", "0")), int(decimals))
        usd_value = Decimal(str(d.get("usd_value"))) if d.get("usd_value") else usd_value_from_amount(d.get("asset_symbol", "ethereum"), amount_decimal)

        if usd_value >= THRESHOLD_USD:
            tx_obj = {
                "txid": txid,
                "chain": d.get("chain"),
                "from_addr": d.get("from"),
                "to_addr": d.get("to"),
                "asset_symbol": d.get("asset_symbol"),
                "amount_decimal": str(amount_decimal),
                "usd_value": int(usd_value),
                "timestamp": int(d.get("timestamp", time.time())),
                "extra": (json.dumps(d)[:1000] if isinstance(d, dict) else str(d)[:1000]),
            }
            try:
                send_telegram_message(format_alert(tx_obj))
                await mark_seen(txid, int(time.time()))
            except Exception as e:
                print("Notifier error:", e)
