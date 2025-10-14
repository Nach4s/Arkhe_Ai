import os
from aiogram import Router, types
from services.file_parser import extract_text_from_file
from services.ai_analyzer import analyze_pitch

router = Router()

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
    os.makedirs("temp", exist_ok=True)
    
    file_path = f"temp/{doc.file_name}"
    
    try:
        # Download file
        await message.bot.download(doc, destination=file_path)
        
        await message.answer(
            "📄 Презентация получена! Анализирую, это может занять немного времени... ⏳"
        )
        
        # Extract text from file
        text = extract_text_from_file(file_path)
        
        if not text or len(text.strip()) < 50:
            await message.answer(
                "⚠️ Не удалось извлечь достаточно текста из файла. "
                "Убедитесь, что презентация содержит текстовую информацию."
            )
            return
        
        # Analyze with AI
        result = await analyze_pitch(text)
        
        # Split long messages if needed (Telegram limit is 4096 characters)
        if len(result) > 4000:
            parts = [result[i:i+4000] for i in range(0, len(result), 4000)]
            for part in parts:
                await message.answer(part)
        else:
            await message.answer(result)
            
    except Exception as e:
        await message.answer(
            f"⚠️ Ошибка при анализе: {str(e)}\n\n"
            "Попробуйте загрузить файл снова или обратитесь к администратору."
        )
    finally:
        # Clean up temporary file
        if os.path.exists(file_path):
            os.remove(file_path)
