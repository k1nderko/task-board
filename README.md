# Kanban Board - Прототип веб-приложения

Прототип канбан-доски с тремя колонками: To Do, In Progress, Done. Приложение поддерживает отображение общего списка задач для нескольких пользователей с синхронизацией в реальном времени через WebSocket.

## Технологии

### Backend
- **Python 3.8+**
- **FastAPI** - современный веб-фреймворк для создания API
- **WebSocket** - для синхронизации в реальном времени
- **Pydantic** - для валидации данных
- **Uvicorn** - ASGI сервер
- **SQLAlchemy** - ORM для работы с базой данных
- **SQLite** - встроенная база данных
- **aiosqlite** - асинхронная поддержка SQLite

### Frontend
- **Vue 3** - прогрессивный JavaScript фреймворк
- **TypeScript** - типизированный JavaScript
- **Composition API** - новый API Vue 3
- **Vite** - быстрый сборщик

## Функциональность

- ✅ Отображение трех колонок: To Do, In Progress, Done
- ✅ Добавление новых задач
- ✅ Удаление задач
- ✅ Перемещение задач между колонками (drag-and-drop)
- ✅ Синхронизация в реальном времени между пользователями
- ✅ Адаптивный дизайн
- ✅ Индикатор статуса подключения

## Установка и запуск

### Backend

1. Перейдите в папку backend:
```bash
cd backend
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Запустите сервер:
```bash
python main.py
```

Сервер будет доступен по адресу: http://localhost:8000

**Примечание**: При первом запуске автоматически создается SQLite база данных `kanban.db` с необходимыми таблицами.

### Frontend

1. Перейдите в папку frontend:
```bash
cd frontend
```

2. Установите зависимости:
```bash
npm install
```

3. Запустите сервер разработки:
```bash
npm run dev
```

Приложение будет доступно по адресу: http://localhost:5173

## API Endpoints

### REST API
- `GET /tasks` - получить все задачи
- `POST /tasks` - создать новую задачу
- `GET /tasks/{task_id}` - получить задачу по ID
- `PUT /tasks/{task_id}` - обновить задачу
- `DELETE /tasks/{task_id}` - удалить задачу

### WebSocket
- `WS /ws` - WebSocket соединение для синхронизации

### Документация API
- `GET /docs` - Swagger UI документация
- `GET /redoc` - ReDoc документация
- `GET /openapi.json` - OpenAPI спецификация

## Структура проекта

```
task-board/
├── backend/
│   ├── main.py              # Основной файл FastAPI приложения
│   ├── database.py          # Конфигурация базы данных
│   ├── crud.py             # CRUD операции для БД
│   ├── requirements.txt     # Зависимости Python
│   └── kanban.db           # SQLite база данных (создается автоматически)
├── frontend/
│   ├── src/
│   │   ├── components/      # Vue компоненты
│   │   ├── services/        # API сервисы
│   │   ├── types/          # TypeScript типы
│   │   ├── App.vue         # Главный компонент
│   │   ├── main.ts         # Точка входа
│   │   └── style.css       # Стили
│   ├── index.html          # HTML шаблон
│   ├── package.json        # Зависимости Node.js
│   ├── tsconfig.json       # Конфигурация TypeScript
│   └── vite.config.ts      # Конфигурация Vite
├── start-backend.bat       # Скрипт запуска backend
├── start-frontend.bat      # Скрипт запуска frontend
└── README.md               # Документация
```

## Особенности реализации

### Backend
- Асинхронная обработка запросов с FastAPI
- WebSocket соединения для real-time синхронизации
- SQLite база данных с SQLAlchemy ORM
- Автоматическое создание таблиц при запуске
- CORS настройки для работы с фронтендом
- Валидация данных с Pydantic
- Автоматическая документация API (Swagger/OpenAPI)

### Frontend
- Composition API Vue 3
- TypeScript для типизации
- Drag-and-drop функциональность
- Адаптивный дизайн
- Автоматическое переподключение WebSocket
- Обработка ошибок и состояний загрузки

## Использование

### Веб-интерфейс
1. Откройте приложение в браузере по адресу http://localhost:5173
2. Добавьте новую задачу в колонку "To Do"
3. Перетащите задачу в другую колонку для изменения статуса
4. Удалите задачу, нажав кнопку "Delete"
5. Все изменения синхронизируются между пользователями в реальном времени

### API Документация
1. Откройте Swagger UI по адресу http://localhost:8000/docs
2. Изучите доступные эндпоинты
3. Протестируйте API прямо из браузера
4. Используйте ReDoc по адресу http://localhost:8000/redoc для альтернативного просмотра документации
