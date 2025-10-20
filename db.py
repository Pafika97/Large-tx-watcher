# db.py
import aiosqlite

DB_FILE = "seen_tx.db"

async def init_db():
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS seen_tx (
            txid TEXT PRIMARY KEY,
            first_seen_ts INTEGER
        )
        """)
        await db.commit()

async def is_seen(txid: str) -> bool:
    async with aiosqlite.connect(DB_FILE) as db:
        cur = await db.execute("SELECT 1 FROM seen_tx WHERE txid = ?", (txid,))
        row = await cur.fetchone()
        return row is not None

async def mark_seen(txid: str, ts: int):
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("INSERT OR IGNORE INTO seen_tx (txid, first_seen_ts) VALUES (?, ?)", (txid, ts))
        await db.commit()
