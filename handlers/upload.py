import os
import re
import uuid
import logging
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from services.file_parser import extract_text_from_file
from services.debates_service import init_debates_session, clear_debates_session, get_debates_session
from services.ai_analyzer import analyze_pitch

router = Router()
logger = logging.getLogger("arkheai")

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing special characters and using UUID.
    Preserves the file extension.
    """
    # Get file extension
    _, ext = os.path.splitext(filename)
    # Generate unique filename with UUID
    safe_name = f"{uuid.uuid4().hex}{ext}"
    return safe_name

@router.message(lambda msg: msg.document is not None)
async def handle_file(message: types.Message):
    doc = message.document
    
    # Check file extension
    if not (doc.file_name.lower().endswith('.pdf') or doc.file_name.lower().endswith('.pptx')):
        await message.answer(
            "⚠️ Пожалуйста, отправьте файл в формате PDF или PPTX."
        )
        return
    
    # Create temp directory if it doesn't exist
    temp_dir = os.path.abspath("temp")
    os.makedirs(temp_dir, exist_ok=True)
    
    # Sanitize filename to avoid issues with special characters
    safe_filename = sanitize_filename(doc.file_name)
    file_path = os.path.join(temp_dir, safe_filename)
    
    try:
        # Download file
        try:
            await message.bot.download(doc, destination=file_path)
        except Exception as e:
            await message.answer(
                f"⚠️ Ошибка при загрузке файла: {str(e)}\n\n"
                "Попробуйте загрузить файл снова."
            )
            return
        
        # Verify file was downloaded
        if not os.path.exists(file_path):
            await message.answer(
                "⚠️ Файл не был сохранён. Попробуйте загрузить файл снова."
            )
            return
        
        await message.answer(
            "📄 Презентация получена! Извлекаю текст..."
        )
        
        # Extract text from file
        try:
            text = extract_text_from_file(file_path)
        except Exception as e:
            error_message = str(e)
            # Split long error messages (Telegram limit is 4096 characters)
            if len(error_message) > 4000:
                # Split by newlines if possible
                parts = error_message.split('\n\n')
                current_part = "⚠️ Ошибка при чтении файла:\n\n"
                for part in parts:
                    if len(current_part) + len(part) + 2 > 4000:
                        await message.answer(current_part)
                        current_part = part + "\n\n"
                    else:
                        current_part += part + "\n\n"
                if current_part.strip():
                    await message.answer(current_part)
            else:
                await message.answer(
                    f"⚠️ Ошибка при чтении файла:\n\n{error_message}"
                )
            return
        
        # Validate extracted text
        if not text or len(text.strip()) < 50:
            await message.answer(
                "⚠️ Не удалось извлечь достаточно текста из файла.\n\n"
                "Возможные причины:\n"
                "• Презентация содержит только изображения (текст в картинках не извлекается)\n"
                "• Файл повреждён или имеет нестандартный формат\n"
                "• Текст слишком короткий для анализа\n\n"
                "Попробуйте загрузить файл с текстовым содержимым."
            )
            return
        
        # Log extracted text preview for debugging (first 500 chars)
        logger.info(f"Извлечено текста: {len(text)} символов")
        logger.debug(f"Превью текста (первые 500 символов):\n{text[:500]}")
        
        # Инициализируем сессию дебатов с загруженной презентацией
        user_id = message.from_user.id
        try:
            # Очищаем предыдущую сессию, если была
            clear_debates_session(user_id)
            # Инициализируем новую сессию
            init_debates_session(user_id, text)
            logger.info(f"Сессия дебатов инициализирована для пользователя {user_id}")
            
            # Предлагаем выбрать режим работы
            keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
                [
                    types.InlineKeyboardButton(text="📊 Анализ", callback_data="analyze"),
                    types.InlineKeyboardButton(text="💬 Дебаты", callback_data="debates")
                ]
            ])
            
            await message.answer(
                "✅ Презентация загружена!\n\n"
                "Выберите режим работы:",
                reply_markup=keyboard
            )
        except Exception as e:
            logger.error(f"Ошибка при инициализации сессии дебатов: {e}", exc_info=True)
            await message.answer(
                f"⚠️ Ошибка при обработке презентации: {str(e)}\n\n"
                "Попробуйте загрузить файл снова."
            )
            
    except Exception as e:
        await message.answer(
            f"⚠️ Неожиданная ошибка: {str(e)}\n\n"
            "Попробуйте загрузить файл снова или обратитесь к администратору."
        )
    finally:
        # Clean up temporary file
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass  # Ignore cleanup errors


@router.callback_query(F.data == "analyze")
async def handle_analyze_callback(callback: types.CallbackQuery):
    """Обработчик кнопки 'Анализ'."""
    await process_analyze(callback.from_user.id, callback.message, callback.answer, callback.message.edit_reply_markup)


@router.message(Command("analyze"))
async def analyze_cmd(message: types.Message):
    """Обработчик команды /analyze."""
    user_id = message.from_user.id
    
    # Получаем сохранённую презентацию
    session = get_debates_session(user_id)
    
    if not session or not session.get("presentation_text"):
        await message.answer(
            "📄 Презентация не найдена.\n\n"
            "Загрузите презентацию (PDF или PPTX), затем используйте /analyze для анализа."
        )
        return
    
    async def dummy_answer(*args, **kwargs):
        pass
    
    async def dummy_edit(*args, **kwargs):
        pass
    
    await process_analyze(user_id, message, dummy_answer, dummy_edit)


async def process_analyze(user_id: int, message: types.Message, answer_callback, edit_callback):
    """Общая функция для обработки анализа."""
    # Получаем сохранённую презентацию
    session = get_debates_session(user_id)
    
    if not session or not session.get("presentation_text"):
        await answer_callback("Презентация не найдена. Загрузите файл снова.", show_alert=True)
        return
    
    await answer_callback("Запускаю анализ...")
    try:
        await edit_callback(reply_markup=None)
    except:
        pass  # Если это не callback, просто игнорируем
    
    await message.answer("📊 Анализирую презентацию, это может занять немного времени... ⏳")
    
    try:
        presentation_text = session["presentation_text"]
        result = await analyze_pitch(presentation_text)
        
        # Split long messages if needed (Telegram limit is 4096 characters)
        if len(result) > 4000:
            parts = [result[i:i+4000] for i in range(0, len(result), 4000)]
            for part in parts:
                await message.answer(part)
        else:
            await message.answer(result)
            
    except Exception as e:
        logger.error(f"Ошибка при анализе: {e}", exc_info=True)
        await message.answer(
            f"⚠️ Ошибка при анализе: {str(e)}\n\n"
            "Проверьте настройки API или попробуйте позже."
        )


@router.callback_query(F.data == "debates")
async def handle_debates_callback(callback: types.CallbackQuery, state: FSMContext):
    """Обработчик кнопки 'Дебаты'."""
    user_id = callback.from_user.id
    
    # Получаем сохранённую презентацию
    session = get_debates_session(user_id)
    
    if not session or not session.get("presentation_text"):
        await callback.answer("Презентация не найдена. Загрузите файл снова.", show_alert=True)
        return
    
    await callback.answer("Запускаю дебаты...")
    await callback.message.edit_reply_markup(reply_markup=None)
    
    # Импортируем здесь, чтобы избежать циклических импортов
    from services.debates_service import ask_next_question
    from handlers.debates import DebatesStates
    
    await callback.message.answer("Запускаю режим дебатов...")
    
    try:
        # Задаём первый вопрос
        first_question = await ask_next_question(user_id)
        await callback.message.answer(first_question)
        
        # Переходим в состояние ожидания ответа
        await state.set_state(DebatesStates.waiting_for_answer)
    except Exception as e:
        logger.error(f"Ошибка при запуске дебатов: {e}", exc_info=True)
        await callback.message.answer(
            f"⚠️ Ошибка при запуске дебатов: {str(e)}\n\n"
            "Попробуйте использовать команду /debates"
        )
        await state.clear()
