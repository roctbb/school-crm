# Ограничение запросов авторизации

Для входа, регистрации и восстановления пароля используются два уровня лимитов:

- основной лимит по HMAC-хэшу нормализованного email, инвайта или reset token;
- высокий аварийный лимит по IP для защиты от массовой ротации идентификаторов.

Поэтому ученики, выходящие в интернет через единый школьный IP, не расходуют общую
короткую квоту. Успешные входы вообще не учитываются в IP-лимите входа.

Значения по умолчанию:

| Маршрут | Основной ключ | Основной лимит | IP-лимит |
| --- | --- | --- | --- |
| `POST /api/login` | email | `10/minute; 50/hour` только для ответов `401` | `2000/hour` только для ответов `401` |
| `POST /api/signup` | invite | `20/hour` | `1000/hour` |
| `POST /api/password/email` | email | `3/hour` | `500/hour` |
| `POST /api/password/reset` | reset token | `10/hour` | `500/hour` |

Все значения можно переопределить переменными окружения:

```dotenv
AUTH_LOGIN_IP_RATE_LIMIT=2000 per hour
AUTH_LOGIN_EMAIL_RATE_LIMIT=10 per minute; 50 per hour
AUTH_SIGNUP_IP_RATE_LIMIT=1000 per hour
AUTH_SIGNUP_INVITE_RATE_LIMIT=20 per hour
AUTH_PASSWORD_EMAIL_IP_RATE_LIMIT=500 per hour
AUTH_PASSWORD_EMAIL_RATE_LIMIT=3 per hour
AUTH_PASSWORD_RESET_IP_RATE_LIMIT=500 per hour
AUTH_PASSWORD_RESET_TOKEN_RATE_LIMIT=10 per hour
```

Счётчики production хранятся в Redis по адресу `RATELIMIT_STORAGE_URI`.

## Reverse proxy

`request.remote_addr` восстанавливается из `X-Forwarded-For` через `ProxyFix`.
По умолчанию приложение доверяет одному ближайшему reverse proxy:

```dotenv
TRUSTED_PROXY_COUNT=1
```

В предоставленном `compose.yml` используется значение `2`: внешний reverse proxy на
хосте и nginx-контейнер проекта. Если схема развёртывания отличается, укажите точное
число proxy в цепочке. Не завышайте это значение: иначе клиент сможет подставить
собственный адрес в `X-Forwarded-For` и обойти IP-лимит. Backend не должен быть
доступен из интернета напрямую.
