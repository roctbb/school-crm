import re
import uuid
from urllib.parse import urlsplit

from application.helpers.exceptions import LogicException


IDEMPOTENCY_KEY_PATTERN = re.compile(r'^[A-Za-z0-9._:-]{8,128}$')


def validate_external_notification(data, idempotency_key):
    if not isinstance(data, dict):
        raise LogicException('Тело запроса должно быть объектом JSON.', 422)

    unknown_fields = set(data) - {'recipient_sub', 'title', 'message', 'url'}
    if unknown_fields:
        raise LogicException(
            f'Неизвестные поля: {", ".join(sorted(unknown_fields))}.', 422
        )

    if not isinstance(idempotency_key, str) or not IDEMPOTENCY_KEY_PATTERN.fullmatch(
        idempotency_key
    ):
        raise LogicException(
            'Заголовок Idempotency-Key обязателен (8–128 символов: буквы, цифры, . _ : -).',
            422,
        )

    recipient_sub = data.get('recipient_sub')
    try:
        recipient_sub = str(uuid.UUID(recipient_sub))
    except (ValueError, TypeError, AttributeError):
        raise LogicException('recipient_sub должен быть UUID из OIDC claim sub.', 422, 'recipient_sub')

    title = data.get('title')
    if (
        not isinstance(title, str)
        or not title.strip()
        or len(title.strip()) > 200
        or '\r' in title
        or '\n' in title
    ):
        raise LogicException('title должен быть строкой от 1 до 200 символов.', 422, 'title')

    message = data.get('message')
    if not isinstance(message, str) or not message.strip() or len(message.strip()) > 10000:
        raise LogicException('message должен быть строкой от 1 до 10000 символов.', 422, 'message')

    url = data.get('url')
    if url is not None:
        if not isinstance(url, str) or not url.strip() or len(url.strip()) > 2000:
            raise LogicException('url должен быть непустой строкой до 2000 символов.', 422, 'url')
        url = url.strip()
        parsed = urlsplit(url)
        is_local_http = parsed.scheme == 'http' and parsed.hostname in {'localhost', '127.0.0.1'}
        if (
            (parsed.scheme != 'https' and not is_local_http)
            or not parsed.netloc
            or parsed.username
            or parsed.password
        ):
            raise LogicException(
                'url должен быть абсолютным HTTPS URL; HTTP разрешён только для localhost.',
                422,
                'url',
            )

    return {
        'recipient_sub': recipient_sub,
        'title': title.strip(),
        'message': message.strip(),
        'url': url,
    }
