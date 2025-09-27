import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.parser import run_parser

async def start_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(run_parser, 'interval', minutes=15)
    scheduler.start()

    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("Синхронізацію зупинено.")
        scheduler.shutdown()