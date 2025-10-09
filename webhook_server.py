from aiogram import Bot, Dispatcher
from fastapi import FastAPI, Request
import uvicorn
import asyncio
from aiogram.types import Update

app = FastAPI()

async def handle_webhook(request: Request, dp: Dispatcher, bot: Bot):
    update_json = await request.json()
    update = Update(**update_json)
    await dp.feed_update(bot, update)
    return {"ok": True}

async def start_webhook(dp: Dispatcher, bot: Bot):
    # Додаємо маршрут для webhook
    app.add_api_route("/webhook", lambda request: handle_webhook(request, dp, bot), methods=["POST"])

    # Запускаємо uvicorn
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()