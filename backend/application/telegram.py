from urllib.parse import urlsplit

import requests


class TelegramAPIError(Exception):
    def __init__(self, message, error_code=None):
        super().__init__(message)
        self.error_code = error_code


class TelegramBotAPI:
    def __init__(self, token, timeout=35, proxy_url=None, session=None):
        if not token:
            raise ValueError('TELEGRAM_BOT_TOKEN is not configured')
        self.base_url = f'https://api.telegram.org/bot{token}'
        self.timeout = timeout
        self.proxy_url = self._validate_proxy_url(proxy_url)
        self.proxies = None
        if self.proxy_url:
            self.proxies = {
                'http': self.proxy_url,
                'https': self.proxy_url,
            }
        self.session = session or requests.Session()

    @staticmethod
    def _validate_proxy_url(proxy_url):
        proxy_url = (proxy_url or '').strip()
        if not proxy_url:
            return None

        try:
            parsed = urlsplit(proxy_url)
            port = parsed.port
        except ValueError as error:
            raise ValueError('TELEGRAM_PROXY_URL is invalid') from error

        if parsed.scheme.lower() not in ('socks5', 'socks5h'):
            raise ValueError('TELEGRAM_PROXY_URL must use socks5:// or socks5h://')
        if not parsed.hostname or port is None:
            raise ValueError('TELEGRAM_PROXY_URL must include a host and port')
        if parsed.path not in ('', '/') or parsed.query or parsed.fragment:
            raise ValueError('TELEGRAM_PROXY_URL must not include a path, query, or fragment')
        return proxy_url

    def call(self, method, payload=None, timeout=None):
        try:
            response = self.session.post(
                f'{self.base_url}/{method}',
                json=payload or {},
                proxies=self.proxies,
                timeout=timeout or self.timeout,
            )
        except requests.RequestException as error:
            # The exception text can contain the proxy URL, including its credentials.
            raise TelegramAPIError(
                f'Telegram request failed: {error.__class__.__name__}'
            ) from error

        try:
            result = response.json()
        except ValueError as error:
            error_code = response.status_code if not response.ok else None
            raise TelegramAPIError(
                f'Telegram returned invalid JSON (HTTP {response.status_code})', error_code
            ) from error

        if not isinstance(result, dict) or not result.get('ok'):
            error_code = result.get('error_code') if isinstance(result, dict) else None
            description = result.get('description') if isinstance(result, dict) else None
            raise TelegramAPIError(
                description or 'Telegram API error', error_code or response.status_code
            )
        return result.get('result')

    def send_message(self, chat_id, text):
        return self.call('sendMessage', {
            'chat_id': chat_id,
            'text': text[:4096],
            'disable_web_page_preview': True,
        })

    def get_updates(self, offset=None, timeout=30):
        payload = {'timeout': timeout, 'allowed_updates': ['message']}
        if offset is not None:
            payload['offset'] = offset
        return self.call('getUpdates', payload, timeout=timeout + 10)

    def delete_webhook(self):
        return self.call('deleteWebhook', {'drop_pending_updates': False})
