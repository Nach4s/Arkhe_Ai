# 📂 Структура проекта Arkhe AI

```
Arkhe_Ai/
│
├── 📄 bot.py                      # Главный файл запуска бота
├── ⚙️ config.py                   # Конфигурация и переменные окружения
│
├── 📁 handlers/                   # Обработчики команд и сообщений
│   ├── __init__.py
│   ├── start.py                  # Обработчик команды /start
│   └── upload.py                 # Обработчик загрузки файлов (PDF/PPTX)
│
├── 📁 services/                   # Бизнес-логика
│   ├── __init__.py
│   ├── file_parser.py            # Парсинг PDF и PPTX файлов
│   └── ai_analyzer.py            # Анализ через Groq API (LLaMA 3.3)
│
├── 📁 temp/                       # Временные файлы (создается автоматически)
│
├── 📁 venv/                       # Виртуальное окружение Python
│
├── 📋 requirements.txt            # Зависимости Python
│
├── 🔐 .env                        # Переменные окружения (НЕ в git!)
├── 📝 .env.example                # Пример файла .env
├── 🚫 .gitignore                  # Игнорируемые файлы для git
│
├── 🚀 start.bat                   # Скрипт запуска для Windows
├── 🚀 start.sh                    # Скрипт запуска для Linux/Mac
│
└── 📚 Документация/
    ├── README.md                 # Основная документация проекта
    ├── QUICKSTART.md             # Быстрый старт за 5 минут
    ├── SETUP_GUIDE.md            # Подробная инструкция по настройке
    ├── GROQ_SETUP.md             # Руководство по Groq API
    ├── CHANGELOG.md              # История изменений
    └── PROJECT_STRUCTURE.md      # Этот файл
```

## 📄 Описание ключевых файлов

### Основные файлы

| Файл | Назначение |
|------|------------|
| `bot.py` | Точка входа, инициализация бота и диспетчера |
| `config.py` | Загрузка переменных окружения и валидация |
| `.env` | Секретные ключи (BOT_TOKEN, GROQ_API_KEY) |

### Handlers (Обработчики)

| Файл | Описание |
|------|----------|
| `handlers/start.py` | Приветственное сообщение при `/start` |
| `handlers/upload.py` | Обработка загруженных PDF/PPTX файлов |

### Services (Сервисы)

| Файл | Описание |
|------|----------|
| `services/file_parser.py` | Извлечение текста из PDF (PyMuPDF) и PPTX (python-pptx) |
| `services/ai_analyzer.py` | Отправка текста в Groq API и получение анализа |

### Документация

| Файл | Для кого |
|------|----------|
| `README.md` | Общий обзор проекта |
| `QUICKSTART.md` | Новички, быстрый старт |
| `SETUP_GUIDE.md` | Подробная пошаговая настройка |
| `GROQ_SETUP.md` | Всё о получении Groq API Key |
| `CHANGELOG.md` | История версий и изменений |

### Скрипты запуска

| Файл | Платформа |
|------|-----------|
| `start.bat` | Windows (двойной клик для запуска) |
| `start.sh` | Linux/Mac (chmod +x start.sh && ./start.sh) |

## 🔄 Поток работы бота

```
1. Пользователь отправляет файл
   ↓
2. handlers/upload.py получает файл
   ↓
3. Файл скачивается в temp/
   ↓
4. services/file_parser.py извлекает текст
   ↓
5. services/ai_analyzer.py отправляет в Groq
   ↓
6. Groq возвращает анализ
   ↓
7. Результат отправляется пользователю
   ↓
8. Временный файл удаляется
```

## 🔧 Технологический стек

### Backend
- **Python 3.8+** - основной язык
- **Aiogram 3.10** - фреймворк для Telegram Bot API
- **AsyncIO** - асинхронная обработка

### AI & ML
- **Groq API** - платформа для AI
- **LLaMA 3.3 70B** - языковая модель от Meta

### Парсинг файлов
- **PyMuPDF (fitz)** - работа с PDF
- **python-pptx** - работа с PowerPoint

### Утилиты
- **python-dotenv** - управление .env
- **httpx** - HTTP клиент для API
- **openai** - OpenAI-совместимый клиент для Groq

## 📦 Зависимости

Все зависимости указаны в `requirements.txt`:

```
aiogram==3.10              # Telegram Bot Framework
python-dotenv==1.0.0       # Переменные окружения
openai>=1.40.0             # OpenAI-совместимый клиент
httpx>=0.27.0              # HTTP клиент
PyMuPDF==1.24.5            # PDF парсер
python-pptx==0.6.23        # PPTX парсер
groq==0.9.0                # Groq SDK (опционально)
```

## 🔐 Безопасность

### Файлы, которые НЕ должны быть в git:

- `.env` - содержит секретные ключи
- `venv/` - виртуальное окружение
- `temp/` - временные файлы
- `__pycache__/` - кэш Python
- `*.pyc` - скомпилированные файлы

Все они указаны в `.gitignore`

## 🚀 Команды для разработки

### Установка
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### Запуск
```bash
python bot.py
```

### Обновление зависимостей
```bash
pip install --upgrade -r requirements.txt
```

### Проверка кода
```bash
# Форматирование (опционально)
pip install black
black .

# Линтер (опционально)
pip install flake8
flake8 .
```

## 📊 Размер проекта

- **Строк кода**: ~500
- **Файлов Python**: 6
- **Зависимостей**: 7
- **Размер**: ~5 MB (без venv)

## 🤝 Вклад в проект

При добавлении новых функций:

1. Создайте новый файл в `handlers/` для новых команд
2. Создайте новый файл в `services/` для новой логики
3. Обновите `bot.py` для подключения новых роутеров
4. Обновите документацию

## 📝 Лицензия

MIT License - свободное использование для любых целей.

---

**Создано с ❤️ для стартап-сообщества**
