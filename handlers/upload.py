import os
import re
import uuid
import logging
from aiogram import Router, types
from services.file_parser import extract_text_from_file
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
            "📄 Презентация получена! Анализирую, это может занять немного времени... ⏳"
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
        
        # Analyze with AI
        try:
            result = await analyze_pitch(text)
        except Exception as e:
            await message.answer(
                f"⚠️ Ошибка при анализе AI: {str(e)}\n\n"
                "Проверьте настройки API или попробуйте позже."
            )
            return
        
        # Split long messages if needed (Telegram limit is 4096 characters)
        if len(result) > 4000:
            parts = [result[i:i+4000] for i in range(0, len(result), 4000)]
            for part in parts:
                await message.answer(part)
        else:
            await message.answer(result)
            
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
