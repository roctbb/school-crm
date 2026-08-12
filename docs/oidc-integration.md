# Вход через Силаэдр CRM (OpenID Connect)

CRM работает как OpenID Provider. Внутренние сервисы — LMS, внутренняя валюта, турнирная таблица и другие — подключаются к ней как обычные OpenID Connect-клиенты.

OIDC-личность соответствует привязанному объекту CRM — ученику, учителю или в
перспективе родителю. Запись `User` используется только как учётная запись для входа
и прав доступа. Поэтому один и тот же объект сохраняет внешнюю идентичность при
изменении имени или email учётной записи.

Используется стандартный Authorization Code Flow:

- обязательный PKCE `S256`, в том числе для серверных клиентов;
- обязательные `state` и `nonce`;
- `id_token` — JWT, подписанный CRM ключом RS256;
- `access_token` и `refresh_token` — непрозрачные случайные значения;
- отдельные `client_id` и `client_secret` для каждого сервиса;
- точное сравнение всех redirect URI;
- одноразовые authorization code и ротация refresh token.
- согласие пользователя запоминается отдельно для каждого клиента и набора scopes.

Issuer для production:

```text
https://lk.silaeder.ru
```

Discovery URL:

```text
https://lk.silaeder.ru/.well-known/openid-configuration
```

Не прописывайте URL `/authorize`, `/token`, `/userinfo` и JWKS вручную. OIDC-библиотека получит их из discovery-документа.

## Создание клиента в CRM

1. Войдите в CRM с ролью `admin`.
2. Откройте меню пользователя → **Внешний вход** или адрес `/admin/oauth-clients`.
3. Нажмите **Новый клиент**.
4. Укажите понятное название и постоянный `client_id`, например `internal-lms`.
5. Для Flask-сервиса оставьте включённым **Конфиденциальный серверный клиент**.
6. Добавьте redirect URI. Он должен полностью совпадать с callback URL сервиса, включая схему, домен, порт и путь.
7. Добавьте post-logout redirect URI, если сервис поддерживает единый выход.
8. Выберите роли пользователей и scopes, которые разрешены этому сервису.
9. Сохраните клиент и сразу скопируйте `client_secret`.

`client_secret` показывается только один раз. CRM хранит только bcrypt-хэш. Если secret потерян, нажмите **Сменить secret** и обновите переменную окружения сервиса. Старый secret, активные authorization code и токены этого клиента после ротации перестанут работать.

Для production разрешены только HTTPS URI. HTTP допускается только для `localhost` и `127.0.0.1`, например:

```text
http://localhost:5000/auth/crm/callback
```

## Scopes и claims

| Scope | Что сервис получает |
| --- | --- |
| `openid` | Стабильный идентификатор привязанного объекта CRM `sub`; обязателен |
| `profile` | `name`, `preferred_username`, `object_id`, `object_type`, `crm_object` |
| `email` | `email`, `email_verified` |
| `roles` | `role` и `roles` |
| `avatar` | Стандартный claim `picture` со ссылкой на фотографию объекта |
| `offline_access` | Refresh token для долгой сессии |

Используйте `sub` как внешний идентификатор ученика/учителя/родителя. Не связывайте
профили по `object_id` или email: числовой ID локален для установки, почта может
измениться, а `sub` остаётся прежним. `object_type` содержит код типа объекта,
например `students` или `teachers`; `crm_object` содержит безопасный минимум
`id`, `type`, `name` без произвольных атрибутов CRM.

Claim `picture` появляется, только если у объекта идентичности есть видимый файловый
атрибут `photo`. Это защищённый URL: скачивайте изображение с тем же заголовком
`Authorization: Bearer ACCESS_TOKEN`. Access token должен содержать scope `avatar`.

Текущие значения ролей доступа учётной записи: `student`, `teacher`, `admin`. Тип
доменной личности берите из `object_type`, а не из роли. Для критичных операций лучше
периодически получать свежие данные через `userinfo`: роль и привязка могут измениться.

Аккаунт без явно привязанного объекта не может завершить OIDC-вход. При регистрации
привязка создаётся из объектного инвайта. Миграция сохраняет прежний `sub` для
однозначных связей, восстановленных по использованным инвайтам либо по единственному
объекту-владению с подходящим типом (`student` → `students`, `teacher` → `teachers`).

## Запоминание согласия

После первого подтверждения CRM запоминает разрешённые пользователем scopes для этого клиента. При следующем входе с тем же или меньшим набором scopes экран подтверждения пропускается автоматически.

Экран появится снова, если:

- клиент запросил новый scope;
- администратор изменил разрешённые scopes, роли или redirect URI клиента;
- клиент передал стандартный параметр `prompt=consent`.

Обычно добавлять `prompt=consent` не нужно. Используйте его только когда сервису требуется явное повторное подтверждение.

## Полный пример на Flask

### Зависимости

```text
Flask>=3.1,<4
Authlib>=1.7,<2
Flask-Session>=0.8,<1
redis>=5,<7
python-dotenv>=1,<2
```

### Переменные окружения

```dotenv
FLASK_SECRET_KEY=замените-на-длинное-случайное-значение
REDIS_URL=redis://localhost:6379/0

CRM_OIDC_ISSUER=https://lk.silaeder.ru
CRM_OIDC_CLIENT_ID=internal-lms
CRM_OIDC_CLIENT_SECRET=secret-который-показала-crm

# Должны быть зарегистрированы в настройках клиента CRM без изменений.
APP_BASE_URL=https://lms.example.ru
```

Не добавляйте `.env` в Git. `client_secret` должен быть доступен только backend-приложению; его нельзя передавать в браузер.

### `app.py`

```python
import os
import secrets
import time
from functools import wraps

import redis
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, session, url_for
from flask_session import Session


load_dotenv()

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ["FLASK_SECRET_KEY"],
    SESSION_TYPE="redis",
    SESSION_REDIS=redis.from_url(os.environ["REDIS_URL"]),
    SESSION_USE_SIGNER=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_SAMESITE="Lax",
)
Session(app)

issuer = os.getenv("CRM_OIDC_ISSUER", "https://lk.silaeder.ru").rstrip("/")
oauth = OAuth(app)
crm = oauth.register(
    name="crm",
    client_id=os.environ["CRM_OIDC_CLIENT_ID"],
    client_secret=os.environ["CRM_OIDC_CLIENT_SECRET"],
    server_metadata_url=f"{issuer}/.well-known/openid-configuration",
    client_kwargs={
        "scope": "openid profile email roles avatar offline_access",
        "code_challenge_method": "S256",
    },
)


def external_url(endpoint):
    base = os.environ["APP_BASE_URL"].rstrip("/")
    return f"{base}{url_for(endpoint)}"


@app.get("/login")
def login():
    # Authlib сама создаёт и проверяет state, nonce и PKCE verifier/challenge.
    return crm.authorize_redirect(external_url("crm_callback"))


@app.get("/auth/crm/callback")
def crm_callback():
    token = crm.authorize_access_token()
    # authorize_access_token проверяет state, подпись id_token, issuer,
    # audience, сроки действия и nonce по discovery/JWKS CRM.
    session["crm_token"] = dict(token)
    session["identity"] = dict(token["userinfo"])
    return redirect(url_for("profile"))


def current_token():
    token = session.get("crm_token")
    if not token:
        return None

    # Обновляем access token заранее. CRM ротирует refresh token при каждом refresh.
    if token.get("expires_at", 0) <= time.time() + 30:
        refresh_token = token.get("refresh_token")
        if not refresh_token:
            return None
        new_token = crm.fetch_access_token(
            grant_type="refresh_token",
            refresh_token=refresh_token,
        )
        # ID token нужен как hint для RP-Initiated Logout. На refresh CRM может
        # не выдавать новый ID token, поэтому сохраняем ранее проверенный.
        new_token.setdefault("id_token", token.get("id_token"))
        session["crm_token"] = dict(new_token)
        token = new_token
    return token


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_token():
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


def load_fresh_userinfo(token):
    metadata = crm.load_server_metadata()
    response = crm.get(metadata["userinfo_endpoint"], token=token)
    response.raise_for_status()
    return response.json()


@app.get("/profile")
@login_required
def profile():
    identity = load_fresh_userinfo(current_token())
    session["identity"] = identity
    return jsonify(identity)


@app.get("/logout")
def logout():
    token = session.get("crm_token") or {}
    id_token_hint = token.get("id_token")
    session.clear()
    if not id_token_hint:
        return redirect("/")

    # Authlib берёт end_session_endpoint из discovery и сохраняет state.
    return crm.logout_redirect(
        post_logout_redirect_uri=external_url("logout_callback"),
        id_token_hint=id_token_hint,
        state=secrets.token_urlsafe(32),
    )


@app.get("/auth/crm/logout/callback")
def logout_callback():
    crm.validate_logout_response()
    session.clear()
    return redirect("/")
```

В настройках этого клиента в CRM должны быть зарегистрированы ровно такие адреса:

```text
Redirect URI:
https://lms.example.ru/auth/crm/callback

Post-logout Redirect URI:
https://lms.example.ru/auth/crm/logout/callback
```

Если Flask находится за reverse proxy, настройте доверие к forwarded-заголовкам только от своего proxy либо, как в примере, собирайте внешние callback URL из фиксированного `APP_BASE_URL`. Иначе библиотека может отправить URI с внутренним `http`/host, который CRM справедливо отклонит.

## Что сохранять в базе сервиса

Минимальная локальная запись доменной личности обычно выглядит так:

```text
oidc_issuer       https://lk.silaeder.ru
oidc_subject      0aa1f478-...-...
name              Иван Иванов
object_type       students
email             user@example.ru
role              student
last_login_at     ...
```

Уникальный ключ должен быть составным: `(oidc_issuer, oidc_subject)`. Если сервис работает только с одной CRM, достаточно уникального `oidc_subject`.

Токены храните только на сервере, желательно в зашифрованном хранилище или server-side session. Никогда не пишите authorization code, `client_secret`, access token, refresh token или полный ID token в логи.

## Время жизни

- authorization code: 5 минут, используется один раз;
- access token: 15 минут;
- ID token: 15 минут;
- refresh token: 30 дней, ротируется при использовании.

`offline_access` нужен только сервисам с долгой сессией. Если он не запрошен, CRM не выдаёт refresh token.

## Частые ошибки

### `invalid_redirect_uri` или «Некорректный redirect_uri»

Проверьте полное совпадение URI. Эти адреса различаются:

```text
https://lms.example.ru/auth/callback
https://lms.example.ru/auth/callback/
```

### `invalid_grant`

Authorization code уже использован/истёк, не совпал redirect URI или не прошла проверка PKCE. Начните вход заново; не повторяйте обмен того же code.

### `invalid_client`

Проверьте `client_id`, `client_secret` и что клиент включён в CRM. После ротации secret старое значение больше не работает.

### Пользователю отказано до экрана подтверждения

Его роль не входит в список разрешённых ролей клиента или сервис запросил scope, который администратор не разрешил.

### Refresh перестал работать

CRM ротирует refresh token. После успешного refresh обязательно атомарно сохраните новый токен целиком. Старый refresh token повторно использовать нельзя.

## Endpoint-справка

| Назначение | Endpoint |
| --- | --- |
| Discovery | `https://lk.silaeder.ru/.well-known/openid-configuration` |
| Authorization | `https://lk.silaeder.ru/oauth/authorize` |
| Token | `https://lk.silaeder.ru/api/oauth/token` |
| UserInfo | `https://lk.silaeder.ru/api/oauth/userinfo` |
| JWKS | `https://lk.silaeder.ru/api/oauth/jwks` |
| Revocation | `https://lk.silaeder.ru/api/oauth/revoke` |
| RP-Initiated Logout | `https://lk.silaeder.ru/oauth/logout` |

Для интеграции всё равно используйте discovery, а не эту таблицу: так библиотека автоматически получает актуальные endpoint и алгоритмы подписи.
