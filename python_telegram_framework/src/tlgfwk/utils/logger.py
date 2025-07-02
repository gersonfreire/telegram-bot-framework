import logging
import sys
import requests

class TelegramLogHandler(logging.Handler):
    """
    A logging handler that sends logs to a Telegram chat.
    """
    def __init__(self, token, chat_id):
        super().__init__()
        self.token = token
        self.chat_id = chat_id
        self.url = f"https://api.telegram.org/bot{self.token}/sendMessage"

    def emit(self, record):
        log_entry = self.format(record)
        payload = {
            'chat_id': self.chat_id,
            'text': log_entry,
            'parse_mode': 'Markdown'
        }
        try:
            requests.post(self.url, data=payload, timeout=5)
        except requests.exceptions.RequestException as e:
            # Handle exceptions during logging to Telegram (e.g., network issues)
            # For now, we'll just print to stderr
            print(f"Error sending log to Telegram: {e}", file=sys.stderr)

def setup_logging(config):
    """
    Configures the root logger based on the provided configuration.
    """
    logging.basicConfig(
        level=logging.DEBUG if config.debug_mode else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stdout,
    )

    # Only set up Telegram handlers if debug mode is enabled
    if config.debug_mode:
        if config.log_chat_id and config.bot_token:
            telegram_handler = TelegramLogHandler(config.bot_token, config.log_chat_id)
            telegram_handler.setLevel(logging.INFO)
            formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
            telegram_handler.setFormatter(formatter)
            logging.getLogger().addHandler(telegram_handler)

        if config.traceback_chat_id and config.bot_token:
            traceback_handler = TelegramLogHandler(config.bot_token, config.traceback_chat_id)
            traceback_handler.setLevel(logging.ERROR)
            formatter = logging.Formatter('```%(asctime)s\n%(levelname)s: %(message)s\n\n%(pathname)s:%(lineno)d```')
            traceback_handler.setFormatter(formatter)
            logging.getLogger().addHandler(traceback_handler)

def get_logger(name):
    """
    Returns a logger with the specified name.
    """
    return logging.getLogger(name)