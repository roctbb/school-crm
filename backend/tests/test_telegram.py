import pytest
import requests

from application.telegram import TelegramAPIError, TelegramBotAPI


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self.payload = payload
        self.status_code = status_code
        self.ok = status_code < 400

    def json(self):
        return self.payload


class FakeSession:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.calls = []

    def post(self, url, **kwargs):
        self.calls.append((url, kwargs))
        if self.error:
            raise self.error
        return self.response


def test_telegram_client_uses_socks5_proxy_for_api_requests():
    session = FakeSession(FakeResponse({'ok': True, 'result': {'message_id': 42}}))
    proxy_url = 'socks5h://proxy-user:proxy-password@127.0.0.1:1080'
    bot = TelegramBotAPI('test-token', proxy_url=proxy_url, session=session)

    result = bot.send_message(123, 'Test')

    assert result == {'message_id': 42}
    assert session.calls == [(
        'https://api.telegram.org/bottest-token/sendMessage',
        {
            'json': {
                'chat_id': 123,
                'text': 'Test',
                'disable_web_page_preview': True,
            },
            'proxies': {'http': proxy_url, 'https': proxy_url},
            'timeout': 35,
        },
    )]


@pytest.mark.parametrize('proxy_url', [
    'http://127.0.0.1:8080',
    'socks4://127.0.0.1:1080',
    'socks5://127.0.0.1',
    'socks5h://127.0.0.1:1080/path',
])
def test_telegram_client_rejects_invalid_socks5_proxy(proxy_url):
    with pytest.raises(ValueError, match='TELEGRAM_PROXY_URL'):
        TelegramBotAPI('test-token', proxy_url=proxy_url)


def test_telegram_client_does_not_expose_proxy_credentials_in_error():
    session = FakeSession(error=requests.exceptions.ProxyError(
        'Cannot connect to socks5h://secret-user:secret-password@127.0.0.1:1080'
    ))
    bot = TelegramBotAPI(
        'test-token',
        proxy_url='socks5h://secret-user:secret-password@127.0.0.1:1080',
        session=session,
    )

    with pytest.raises(TelegramAPIError) as error:
        bot.get_updates()

    assert str(error.value) == 'Telegram request failed: ProxyError'
    assert 'secret-user' not in str(error.value)
    assert 'secret-password' not in str(error.value)
