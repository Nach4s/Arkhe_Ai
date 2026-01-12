from aiogram import Router, types
from aiogram.filters import Command

router = Router()

@router.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        "👋 Привет! Я Arkhe AI.\n\n"
        "Отправь мне PDF или PPTX с презентацией стартапа, "
        "и я проведу экспертный анализ по инвестиционным критериям 💡\n\n"
        "📊 Я оцениваю:\n"
        "• Решение проблемы\n"
        "• Уникальность и конкурентов\n"
        "• Целевую аудиторию\n"
        "• Объём рынка\n"
        "• MVP и прототип\n"
        "• Монетизацию\n"
        "• Финансовую модель\n"
        "• Риски\n"
        "• Сравнение с известными стартапами\n"
        "• Оценку по методу Бёркуса\n\n"
        "💬 Также доступен режим дебатов /debates — жёсткие инвестиционные дебаты с AI-инвестором\n\n"
        "Просто загрузи файл презентации! 🚀"
    )
