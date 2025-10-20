# main.py
import asyncio
import os
from dotenv import load_dotenv
from db import init_db
from fetchers import ArkhamFetcher, NansenFetcher

load_dotenv()

async def main():
    await init_db()

    async def handler(tx):
        # общий обработчик, если хотите централизовать логику
        pass

    tasks = []
    if os.getenv("ARKHAM_WS_URL") and os.getenv("ARKHAM_API_KEY"):
        ark = ArkhamFetcher(handler)
        tasks.append(asyncio.create_task(ark.run()))

    if os.getenv("NANSEN_REST_URL") and os.getenv("NANSEN_API_KEY"):
        nan = NansenFetcher(handler)
        tasks.append(asyncio.create_task(nan.run()))

    if not tasks:
        print("No fetchers configured. Set ARKHAM_WS_URL/ARKHAM_API_KEY or NANSEN_REST_URL/NANSEN_API_KEY in .env")
        return

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Stopped by user")
