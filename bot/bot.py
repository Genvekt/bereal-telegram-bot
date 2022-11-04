import asyncio
from datetime import datetime, timezone
from typing import Dict

from aiogram import Bot, Dispatcher, types, executor

from emoji_list import get_random_emoji
from config import settings
from asyncio import Task
import random

bot = Bot(token=settings.telegram_api_token)
dp = Dispatcher(bot)

class BerealBot:
    def __init__(self):
        self._members = {
            "-1001391606769": {
                "@genvekt",
                "@pkotoff",
                "@loaferCH",
                "@diomidov",
                "@alxv_nikitos"
            },
            "264844670": {
                "@genvekt"
            }
        }
        self._tasks: Dict[str, Task] = {}
        self._start_hour = 7
        self._stop_hour = 17
        self._job_proba = 0.5
        self._job_min_interval = 10 #60 * 60 * 3 # min three hours between task
        self._job_retry_interval = 5 #60 * 30 # min time to retry task on failure

    async def start(self, chat_id):
        if chat_id not in self._members:
            await bot.send_message(
                chat_id=chat_id,
                text="Я не умею работать с этим чатом, пока."
            )
            return

        if chat_id not in self._tasks:
            self._tasks[chat_id] = asyncio.create_task(
                self._job(chat_id=chat_id)
            )
        await bot.send_message(
            chat_id=chat_id,
            text="BerealBot запущен. Отправь /stop_bereal если нужно меня остановить."
        )

    async def stop(self, chat_id):
        if chat_id in self._tasks:
            self._tasks[chat_id].cancel()
            self._tasks.pop(chat_id)

        await bot.send_message(
            chat_id=chat_id,
            text="BerealBot остановлен. Отправь /start_bereal чтобы запустить меня."
        )

    async def trigger(self, chat_id):
        if chat_id not in self._tasks:
            await bot.send_message(
                chat_id=chat_id,
                text="BerealBot остановлен. Отправь /start_bereal чтобы запустить меня снова."
            )
            return

        now = datetime.now(timezone.utc)
        if now.hour < self._start_hour or now.hour >= self._stop_hour:
            await bot.send_message(
                chat_id=chat_id,
                text="Я пока не могу потревожить участников, попробуй позже."
            )
            return

        await self.notify(chat_id=chat_id)

    async def notify(self, chat_id):
        if chat_id in self._members:
            message = (
                " ".join(self._members[chat_id]) +
                " как дела? " +
                get_random_emoji() +
                get_random_emoji() +
                get_random_emoji()
            )
            await bot.send_message(
                chat_id=chat_id,
                text=message
            )

    async def _job(self, chat_id):
        try:
            probability = self._job_proba
            while True:
                now = datetime.now(timezone.utc)
                if now.hour < self._start_hour or now.hour >= self._stop_hour:
                    await asyncio.sleep(60*30)
                    continue

                dice_roll = random.random()
                # Success
                if dice_roll <= probability:
                    # Return initial probability and sleep min interval
                    await self.notify(chat_id=chat_id)
                    probability = self._job_proba
                    await asyncio.sleep(self._job_min_interval)
                # Failure
                else:
                    # Increase probability and wait small interval
                    probability += 0.1
                    await asyncio.sleep(self._job_retry_interval)

        except asyncio.CancelledError:
            pass

bereal_bot = BerealBot()

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """This handler will be called when user sends `/start`"""
    await message.reply("Hi!\nI'm BerealBot!")

@dp.message_handler(commands=['start_bereal'])
async def start_bereal(message: types.Message):
    """Creates periodic tasks for chat."""
    await bereal_bot.start(chat_id=str(message.chat.id))

@dp.message_handler(commands=['stop_bereal'])
async def start_bereal(message: types.Message):
    """Creates periodic tasks for chat."""
    await bereal_bot.stop(chat_id=str(message.chat.id))

@dp.message_handler(commands=['trigger'])
async def trigger(message: types.Message):
    """Creates periodic tasks for chat."""
    await bereal_bot.trigger(chat_id=str(message.chat.id))
