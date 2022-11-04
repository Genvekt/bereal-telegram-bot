import logging
from config import settings
from bot import dp, executor, bereal_bot
from functools import partial


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
