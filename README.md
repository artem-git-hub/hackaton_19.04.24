
## GET запросы:

### 1. Получение списка всех команд (`GET /teams/`)

Этот запрос возвращает список всех команд. В ответ на успешный запрос вы получите список объектов команд в формате JSON. Каждый объект команды содержит информацию о слаге команды и пути к иконке команды.

```json
[
  {
    "slug": "слаг_команды",
    "icon_path": "путь_к_иконке_команды"
  },
  ...
]
```

### 2. Получение данных о конкретной команде (`GET /teams/{slug}`)

Этот запрос возвращает данные о конкретной команде на основе её слага. В ответ на успешный запрос вы получите объект данных о команде в формате JSON. Объект содержит информацию о названии команды, слаге, электронной почте, пути к иконке команды, а также списки участников команды, вопросов и рейтингов.

```json
{
  "name": "название_команды",
  "slug": "слаг_команды",
  "email": "email@команды",
  "icon_path": "путь_к_иконке_команды",
  "team_users": [],
  "questions": [],
  "ratings": []
}
```

----


## POST запросы

### 1. Создание команды (`POST /teams/`)

Этот запрос создает новую команду. В запросе необходимо указать следующие поля в формате JSON:

```json
{
  "team_name": "Название команды",
  "email": "email@example.com",
  "login": "логин",
  "password": "пароль",
  "image": "base64 строка с изображением",
  "team_users": [
    {
      "surname": "Фамилия участника",
      "first_name": "Имя участника",
      "patronymic": "Отчество участника",
      "image": "base64 строка с изображением",
      "description": "Описание участника"
    },
    ...
  ]
}
```

В ответ на успешный запрос вы получите токен аутентификации в следующем формате:

```json
{
  "token": "ваш_токен"
}
```

### 2. Обновление команды (`POST /teams/{slug}`)

Этот запрос обновляет данные о существующей команде. В запросе необходимо указать следующие поля в формате JSON:

```json
{
  "team_name": "Новое название команды",
  "email": "new_email@example.com",
  "login": "новый_логин",
  "password": "новый_пароль",
  "image": "новая_base64_строка_с_изображением",
  "team_users": [
    {
      "id": 1,  // идентификатор участника (обязательно)
      "surname": "Новая фамилия участника",
      "first_name": "Новое имя участника",
      "patronymic": "Новое отчество участника",
      "image": "новая_base64_строка_с_изображением",
      "description": "Новое описание участника"
    },
    ...
  ]
}
```

В ответ на успешный запрос вы получите сообщение об успешном обновлении команды.

### 3. Создание участника команды (`POST /teams/{slug}/users/`)

Этот запрос создает нового участника в указанной команде. В запросе необходимо указать следующие поля в формате JSON:

```json
{
  "surname": "Фамилия участника",
  "first_name": "Имя участника",
  "patronymic": "Отчество участника",
  "image": "base64 строка с изображением",
  "description": "Описание участника"
}
```

В ответ на успешный запрос вы получите данные о созданном участнике команды.

### 4. Аутентификация и получение токена (`POST /login/`)

Этот запрос аутентифицирует пользователя на основе предоставленного логина и пароля и возвращает токен аутентификации. В запросе необходимо указать следующие поля в формате JSON:

```json
{
  "login": "ваш_логин",
  "password": "ваш_пароль"
}
```

В ответ на успешный запрос вы получите токен аутентификации в следующем формате:

```json
{
  "token": "ваш_токен"
}
```

Это полная документация по созданию запросов к вашему сервису. Помните, что при отправке изображений в формате base64 их размер может быть довольно большим, поэтому убедитесь, что ваш сервер готов обрабатывать такие запросы.