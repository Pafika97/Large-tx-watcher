# notifier.py
import requests
import os
import time

TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")

TG_API = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"

def send_telegram_message(text: str, parse_mode="HTML"):
    """Простая функция отправки сообщения в Telegram."""
    payload = {
        "chat_id": TG_CHAT_ID,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": True,
    }
    r = requests.post(TG_API, json=payload, timeout=10)
    r.raise_for_status()
    return r.json()

def format_alert(tx):
    """
    tx: dict with keys:
      - txid, chain, from_addr, to_addr, asset_symbol, amount, amount_decimal, usd_value, timestamp, extra
    """
    ts = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(tx.get("timestamp", int(time.time()))))
    text = (
        f"\u26a0\ufe0f <b>Large transfer detected</b>\n"
        f"<b>Value (USD):</b> ${tx['usd_value']:,}\n"
        f"<b>Tx:</b> <code>{tx['txid']}</code>\n"
        f"<b>Chain:</b> {tx.get('chain')}\n"
        f"<b>Asset:</b> {tx.get('asset_symbol')} ({tx.get('amount_decimal')})\n"
        f"<b>From:</b> {tx.get('from_addr')}\n"
        f"<b>To:</b> {tx.get('to_addr')}\n"
        f"<b>When (UTC):</b> {ts}\n"
    )
    if tx.get("extra"):
        text += f"\n<code>{tx['extra']}</code>"
    return text
