# ⚡ Быстрый старт Arkhe AI

## 🚀 За 5 минут до запуска

### 1️⃣ Получите Telegram Bot Token

```
1. Откройте @BotFather в Telegram
2. Отправьте: /newbot
3. Следуйте инструкциям
4. Скопируйте токен
```

### 2️⃣ Получите Groq API Key (БЕСПЛАТНО!)

```
1. Перейдите: https://console.groq.com
2. Войдите через GitHub
3. Создайте API Key
4. Скопируйте ключ (начинается с gsk_)
```

### 3️⃣ Настройте проект

**Windows:**
```cmd
cd d:\Arkhe_Ai
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
notepad .env
```

**Linux/Mac:**
```bash
cd /path/to/Arkhe_Ai
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
nano .env
```

### 4️⃣ Заполните .env

```env
BOT_TOKEN=ваш_токен_бота
GROQ_API_KEY=ваш_groq_ключ
LOG_LEVEL=INFO
```

### 5️⃣ Запустите бота

```bash
python bot.py
```

## ✅ Готово!

Найдите бота в Telegram и отправьте `/start`

---

## 🆘 Проблемы?

### Ошибка с зависимостями
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Ошибка с .env
```bash
# Проверьте, что файл создан
dir .env  # Windows
ls -la .env  # Linux/Mac

# Проверьте содержимое
type .env  # Windows
cat .env  # Linux/Mac
```

### Бот не отвечает
- Проверьте токен бота
- Убедитесь, что бот запущен
- Проверьте интернет

---

## 📚 Подробная документация

- [README.md](README.md) - полное описание
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - детальная инструкция
- [GROQ_SETUP.md](GROQ_SETUP.md) - всё о Groq API

## 🎯 Тестирование

1. Отправьте `/start` боту
2. Загрузите тестовую презентацию (PDF или PPTX)
3. Дождитесь анализа (~10-30 секунд)
4. Получите экспертный отчет!

---

**Приятного использования!** 🚀
