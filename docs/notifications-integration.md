# Telegram и API уведомлений

Личный кабинет отправляет каждое уведомление по email и, если пользователь привязал
Telegram, в Telegram-бота. Обе доставки выполняются задачами Celery через Redis.

## Настройка Telegram-бота

1. Создайте бота через `@BotFather` и получите токен.
2. Добавьте в `.env`:

   ```dotenv
   TELEGRAM_BOT_TOKEN=123456:telegram-token
   TELEGRAM_BOT_USERNAME=school_crm_bot
   # Необязательно, по умолчанию 10 минут:
   TELEGRAM_LINK_TOKEN_EXPIRES=600
   # Необязательно: SOCKS5-прокси для polling и отправки сообщений:
   TELEGRAM_PROXY_URL=socks5h://proxy-user:proxy-password@proxy.example.org:1080
   ```

   Поддерживаются схемы `socks5://` и `socks5h://`. Вариант `socks5h://`
   рекомендуется, если DNS-запросы тоже должны проходить через прокси. Специальные
   символы в логине и пароле нужно percent-encode (например, `@` как `%40`).

3. Пересоберите и запустите backend, worker и polling-бота:

   ```bash
   docker compose up -d --build backend worker telegram-bot
   ```

В webhook-режиме бот не работает: сервис `telegram-bot` постоянно вызывает
`getUpdates`. Поэтому должен работать ровно один экземпляр polling-процесса.

Пользователь открывает «Уведомления» в меню профиля, нажимает «Подключить Telegram»
и затем `Start` в боте. Одноразовая ссылка действует 10 минут; исходный токен в базе
не хранится. Команда `/stop` или кнопка «Отключить» удаляет привязку.

## Доступ внешнего сервиса

Самодостаточная инструкция, которую можно передать разработчикам интегрируемого
сервиса: [API отправки уведомлений из внешних сервисов](external-notifications-api.md).

В «Администрирование → Внешний вход» откройте конфиденциальный OIDC-клиент и включите
«Разрешить отправку уведомлений». API использует тот же `client_id` и `client_secret`,
что и OAuth. Публичным клиентам доступ не выдаётся.
Получать уведомления могут только пользователи с одной из ролей, разрешённых этому
OIDC-клиенту.

Внешний сервис получает стабильный идентификатор объекта ученика/учителя/родителя из
claim `sub` после OIDC-авторизации и передаёт его как `recipient_sub`. CRM находит
привязанную к этому объекту учётную запись и доставляет уведомление её владельцу:

```http
POST /api/external/notifications HTTP/1.1
Authorization: Basic base64(client_id:client_secret)
Content-Type: application/json
Idempotency-Key: wallet-operation-8f43d882

{
  "recipient_sub": "790be3dd-4b7a-4ab4-94ce-82d44bcfd06f",
  "title": "Начислены мотивашки",
  "message": "За победу в соревновании начислено 50 мотивашек.",
  "url": "https://wallet.example.org/operations/42"
}
```

Пример с `curl`:

```bash
curl --user 'wallet:CLIENT_SECRET' \
  -H 'Content-Type: application/json' \
  -H 'Idempotency-Key: wallet-operation-8f43d882' \
  -d '{"recipient_sub":"790be3dd-4b7a-4ab4-94ce-82d44bcfd06f","title":"Начислены мотивашки","message":"Начислено 50 мотивашек","url":"https://wallet.example.org/operations/42"}' \
  https://lk.silaeder.ru/api/external/notifications
```

Новый запрос возвращает `202`, повтор с тем же ключом и тем же телом — `200` и
`idempotent_replay: true`. Повторное использование ключа с другим телом возвращает
`409`. Заголовок `Idempotency-Key` обязателен, чтобы безопасно повторять запрос после
сетевого сбоя или ответа `503`.

Успешный ответ означает, что уведомление сохранено и поставлено в очередь. Состояние
доставки и последние ошибки каналов записываются в таблице `notifications`.
