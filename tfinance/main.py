# ------------------------ Основной файл приложения ------------------------ #
# ------------- Импорт необходимых библиотек, функций, классов ------------- #
# Встроенные библиотеки.
import datetime
import logging
from pathlib import Path

from telegram import Update

# Работа с telegram-bot-api.
from telegram.ext import (
    CommandHandler,
    Application,
    ContextTypes,
)

# Работа с акциями (загрузка, вывод, проверка, игра, визуализация, рассылка).
from blast import daily, notify_assignees

# ORM (БД с данными о пользователях).
from database import Database
from exceptions import EmptyDataFrameError, WrongPeriodError
from functions import create_user
from game import game_handler, game_results
from graphics.visualize import do_stock_image
from stock import check_stock, get_all_stocks, load_stocks
from config import BOT_TOKEN, TIMEZONE

__all__ = []

# Запускаем логирование
Path("logs").mkdir(exist_ok=True)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.FileHandler(
            datetime.datetime.now(
                tz=TIMEZONE,
            ).strftime("logs/%Y-%m-%d_%H-%M-%S.log"),
            encoding="utf-8",
        ),
        logging.StreamHandler(),
    ],
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


# Получение списка необходимых акций по команде /stocks [args].
# Обработчик команды /stocks.
async def get_list_stocks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        templates = load_stocks("stocks.json")  # Загружаем список всех акций
        msg = ""
        if context.args[0].isalpha():
            for el in templates:
                if el["name"].lower().startswith(context.args[0].lower()):
                    msg += f"{el['symbol']} {el['name']}\n"
            if len(msg) > 4096:
                msg = msg[:4093] + "..."
            elif len(msg) == 0:
                msg = "Ничего не найдено."
            await update.message.reply_text(msg)
        else:
            raise ValueError
    except (IndexError, ValueError):
        await update.message.reply_text("Неверный способ ввода. /help")


# Обработчик команды /stock [stock_index].
# Визуализирует график и отправляет его в прямом порядке.
async def get_stock_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if len(context.args) not in range(1, 3):
            raise ValueError
        if len(context.args) == 1:
            context.args.append("1mo")
        await update.message.reply_photo(
            do_stock_image(context.args[0], context.args[1]),
        )
    except (IndexError, ValueError):
        await update.message.reply_text(
            "Неверный способ ввода. /stock [индекс акции] [период]."
            "Например: /stock AAPL 1m",
        )
    except WrongPeriodError:
        await update.message.reply_text(
            "Неверный период. "
            "Доступные периоды: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max",
        )
    except EmptyDataFrameError:
        await update.message.reply_text(
            "Такой акции не было найдено в данных Yahoo Finance.",
        )


# Обработчик команды /start.
# Добавляет пользователя в БД, тем самым открывая ему доступ к командам.
async def start(update: Update, _):
    user = create_user(update)
    db.add_user(user)
    await update.message.reply_text(
        f"Привет, {user.first_name}! Теперь доступ к командам открыт.\n"
        f"Введите /help для просмотра списка команд.",
    )


# Список команд.
async def help_msg(update: Update, _):
    await update.message.reply_text(
        """
/stock [stock_name] [период] - посмотреть график цены акции за период
(по умолчанию 1 месяц)
Доступные периоды: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
Например: /stock AAPL 3mo - посмотреть график цены акции Apple за 3 месяца
/stocks [буква алфавита]
Например: /stocks A - посмотреть все акции,название которых начинается с 'A'

/follow [stock_name] - добавить акцию в избранное
/unfollow [stock_name] - удалить акцию из избранного
/favourites - посмотреть список избранных акций

/daily - установить ежедневную рассылку избранных акций
/stats - посмотреть собственную статистику
/game [stock_name] - начать игру с прогнозом выбранной акции
        """,
    )


# Отправляет список любимых акций.
async def favourites(update: Update, _):
    user = create_user(update)
    stocks = db.get_favourites_stocks(user)
    if stocks and stocks[0]:
        await update.message.reply_text(", ".join(stocks[0].split()))
    else:
        await update.message.reply_text("У вас нет избранных акций")


# Возможность подписываться на другие акции.
async def follow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = create_user(update)
    if context.args and context.args[0]:
        context.args[0] = context.args[0].upper()
        if db.check_favourites_stocks(user, context.args[0]):
            await update.message.reply_text("Акция уже в избранном")
        else:
            if check_stock(context.args[0]):
                db.add_favourites_stocks(user, context.args[0])
                await update.message.reply_text("Акция добавлена в избранное")
            else:
                await update.message.reply_text("Акция не найдена")
    else:
        await update.message.reply_text(
            "Неверный способ ввода. "
            "/follow [индекс акции]. Например: /follow AAPL",
        )


# Возможность отписки от акций.
async def unfollow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = create_user(update)
    if context.args and context.args[0]:
        context.args[0] = context.args[0].upper()
        if not db.check_favourites_stocks(user, context.args[0]):
            await update.message.reply_text("Акции нет в избранном")
        else:
            db.remove_favourites_stock(user, context.args[0])
            await update.message.reply_text("Акция удалена из избранного")
    else:
        await update.message.reply_text(
            "Неверный способ ввода. /unfollow [индекс акции].",
        )


# Вывод статистики пользователя из БД.
async def stats(update: Update, _):
    user = create_user(update)
    data = db.read_info(user)
    try:
        favourites_string = ", ".join(data[1].split()) if data[1] else "Нет"
        await update.message.reply_text(
            f"""
Имя пользователя: {data[0]}
Избранные акции: {favourites_string}
Очки, заработанные в игре: {data[2]}
            """,
        )
    except TypeError:
        await update.message.reply_text(
            "Вас нет в бд, запустите команду /start чтобы исправить ошибку",
        )


def main():
    # Получение и сохранение списка всех акций в stocks.json.
    try:
        get_all_stocks()
    except Exception as e:
        logging.error(e)

    application = Application.builder().token(BOT_TOKEN).build()
    job_queue = application.job_queue

    job_queue.run_daily(
        notify_assignees,
        datetime.time(
            hour=8,
            tzinfo=TIMEZONE,
        ),
    )
    job_queue.run_daily(
        game_results,
        datetime.time(
            hour=3,
            tzinfo=TIMEZONE,
        ),
    )

    application.add_handler(game_handler)

    application.add_handler(CommandHandler("daily", daily))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_msg))
    application.add_handler(CommandHandler("favourites", favourites))
    application.add_handler(CommandHandler("follow", follow))
    application.add_handler(CommandHandler("unfollow", unfollow))
    application.add_handler(CommandHandler("stock", get_stock_image))
    application.add_handler(CommandHandler("stocks", get_list_stocks))
    application.add_handler(CommandHandler("stats", stats))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    db: Database = Database()
    main()
