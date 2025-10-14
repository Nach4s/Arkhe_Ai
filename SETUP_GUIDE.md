# 🚀 Пошаговое руководство по настройке Arkhe AI

## Шаг 1: Получение Telegram Bot Token

1. Откройте Telegram и найдите [@BotFather](https://t.me/botfather)
2. Отправьте команду `/newbot`
3. Введите имя бота (например: `Arkhe AI`)
4. Введите username бота (например: `arkhe_ai_bot`)
5. Скопируйте полученный токен (формат: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

## Шаг 2: Получение Groq API Key (БЕСПЛАТНО! ⚡)

1. Перейдите на [console.groq.com](https://console.groq.com)
2. Нажмите "Sign in" и войдите через GitHub
3. Перейдите в раздел [API Keys](https://console.groq.com/keys)
4. Нажмите "Create API Key"
5. Скопируйте ключ (формат: `gsk_...`)
6. ✅ **Никаких платежей!** Groq полностью бесплатен и быстрее GPT-4

## Шаг 3: Установка Python

Убедитесь, что у вас установлен Python 3.8 или выше:

```bash
python --version
```

Если Python не установлен, скачайте его с [python.org](https://www.python.org/downloads/)

## Шаг 4: Настройка проекта

### Windows:

```cmd
# Перейдите в директорию проекта
cd d:\Arkhe_Ai

# Создайте виртуальное окружение
python -m venv venv

# Активируйте виртуальное окружение
venv\Scripts\activate

# Установите зависимости
pip install -r requirements.txt

# Создайте файл .env
copy .env.example .env

# Откройте .env в блокноте и заполните данные
notepad .env
```

### Linux/Mac:

```bash
# Перейдите в директорию проекта
cd /path/to/Arkhe_Ai

# Создайте виртуальное окружение
python3 -m venv venv

# Активируйте виртуальное окружение
source venv/bin/activate

# Установите зависимости
pip install -r requirements.txt

# Создайте файл .env
cp .env.example .env

# Откройте .env в редакторе
nano .env
```

## Шаг 5: Заполнение .env файла

Откройте файл `.env` и заполните:

```env
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
LOG_LEVEL=INFO
```

## Шаг 6: Запуск бота

```bash
python bot.py
```

Вы должны увидеть:

```
2024-10-13 21:41:00 - __main__ - INFO - Starting Arkhe AI bot...
2024-10-13 21:41:01 - __main__ - INFO - Bot is ready. Starting polling...
```

## Шаг 7: Тестирование

1. Откройте Telegram
2. Найдите вашего бота по username
3. Отправьте `/start`
4. Загрузите тестовую презентацию (PDF или PPTX)
5. Дождитесь анализа

## 🔧 Решение проблем

### Ошибка: "BOT_TOKEN is not set"

**Решение**: Убедитесь, что файл `.env` создан и содержит корректный токен.

### Ошибка: "GROQ_API_KEY is not set"

**Решение**: 
- Проверьте правильность API ключа Groq в файле `.env`
- Убедитесь, что ключ начинается с `gsk_`
- Groq полностью бесплатен, баланс не требуется!

### Ошибка: "No module named 'aiogram'"

**Решение**: 
```bash
pip install -r requirements.txt
```

### Бот не отвечает в Telegram

**Решение**:
- Проверьте, что бот запущен (в консоли должно быть "Bot is ready")
- Убедитесь, что токен бота правильный
- Проверьте интернет-соединение

### Ошибка при парсинге PDF/PPTX

**Решение**:
- Убедитесь, что файл не поврежден
- Проверьте, что файл содержит текст (не только изображения)
- Попробуйте другой файл

## 📊 Мониторинг работы

Бот логирует все действия в консоль. Уровень логирования можно изменить в `.env`:

- `DEBUG` - максимально подробные логи
- `INFO` - стандартные логи (рекомендуется)
- `WARNING` - только предупреждения и ошибки
- `ERROR` - только ошибки

## 🔄 Обновление зависимостей

```bash
pip install --upgrade -r requirements.txt
```

## 🛑 Остановка бота

Нажмите `Ctrl+C` в консоли, где запущен бот.

## 📱 Деплой на сервер (опционально)

Для постоянной работы бота рекомендуется развернуть его на сервере:

### Варианты деплоя:

1. **VPS** (DigitalOcean, AWS, Hetzner)
2. **PythonAnywhere** (бесплатный тариф)
3. **Heroku** (с платным тарифом)
4. **Railway.app**

### Пример для Linux сервера:

```bash
# Установите screen для фоновой работы
sudo apt install screen

# Создайте новую сессию
screen -S arkhe_bot

# Запустите бота
python bot.py

# Отключитесь от сессии: Ctrl+A, затем D
# Вернуться к сессии: screen -r arkhe_bot
```

## ✅ Готово!

Ваш бот Arkhe AI готов к работе! 🎉

Если возникли проблемы, создайте issue в репозитории.
