import logging
import signal
import time

from application import create_app
from application.helpers.exceptions import LogicException
from application.methods import connect_telegram, disconnect_telegram_chat
from application.telegram import TelegramAPIError, TelegramBotAPI


logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger('telegram_bot')
running = True


def stop(_signum, _frame):
    global running
    running = False


def handle_message(bot, message):
    chat = message.get('chat') or {}
    sender = message.get('from') or {}
    chat_id = chat.get('id')
    text = (message.get('text') or '').strip()
    if not chat_id or chat.get('type') != 'private' or not text:
        return

    parts = text.split(maxsplit=1)
    command = parts[0].split('@', 1)[0].lower()
    if command == '/start':
        if len(parts) != 2:
            bot.send_message(
                chat_id,
                'Откройте настройки личного кабинета и нажмите «Подключить Telegram».',
            )
            return
        try:
            with app.app_context():
                connect_telegram(
                    parts[1], chat_id, sender.get('username'), sender.get('first_name')
                )
            bot.send_message(
                chat_id,
                'Telegram подключён. Теперь уведомления личного кабинета будут приходить сюда.',
            )
        except LogicException as error:
            bot.send_message(chat_id, error.message)
    elif command == '/stop':
        with app.app_context():
            disconnected = disconnect_telegram_chat(chat_id)
        bot.send_message(
            chat_id,
            'Telegram отключён от личного кабинета.' if disconnected
            else 'Этот Telegram не был подключён к личному кабинету.',
        )
    else:
        bot.send_message(
            chat_id,
            'Я доставляю уведомления из личного кабинета. Команда /stop отключает их.',
        )


def poll():
    token = app.config.get('TELEGRAM_BOT_TOKEN')
    if not token:
        logger.warning('TELEGRAM_BOT_TOKEN is not configured; polling is disabled')
        while running:
            time.sleep(60)
        return
    timeout = app.config['TELEGRAM_POLL_TIMEOUT']
    bot = TelegramBotAPI(
        token,
        timeout=timeout + 10,
        proxy_url=app.config.get('TELEGRAM_PROXY_URL'),
    )
    bot.delete_webhook()
    offset = None
    logger.info('Telegram bot polling started')
    while running:
        try:
            for update in bot.get_updates(offset=offset, timeout=timeout):
                offset = update['update_id'] + 1
                try:
                    handle_message(bot, update.get('message') or {})
                except Exception:
                    logger.exception('Failed to process Telegram update %s', update.get('update_id'))
        except TelegramAPIError:
            logger.exception('Telegram polling request failed')
            time.sleep(5)


app, _celery = create_app()


if __name__ == '__main__':
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    poll()
