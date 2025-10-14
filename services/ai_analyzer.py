from openai import AsyncOpenAI
from config import GROQ_API_KEY

# Groq использует OpenAI-совместимый API
client = AsyncOpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

ANALYSIS_PROMPT = """
Ты — ArkheAI, беспристрастный венчурный аналитик и оценщик стартапов.
Говори кратко, сухо и по делу. Без эмодзи, без выделений, без мотивации.
Если идея плохая — говори прямо. Не используй дипломатичных формулировок.
Ты пишешь как опытный инвестор, который видел сотни провальных питчей и не тратит время на фантазии.

Отвечай строго на русском языке. Не используй слова или символы с других языков (включая китайский, английский, японский и т.д.).

Оцени стартап по девяти критериям:

1. Решает ли стартап реальную проблему (1–2 предложения).
2. Уникальность решения и наличие конкурентов.
3. Целевая аудитория — кто конкретно будет этим пользоваться и зачем.
4. Потенциал и объем рынка (TAM / SAM / SOM) — кратко.
5. MVP — есть ли реально работающий продукт или только идея.
6. Модель монетизации — как зарабатываются деньги.
7. Финансовая модель — реалистична ли и можно ли масштабировать.
8. Основные риски — команда, рынок, технология, конкуренция, регулирование.
9. Сравнение с существующими стартапами.

После анализа добавь оценку по методу Бёркуса (по 5 параметрам, от 1 до 5 звезд):

Идея и ценность:
MVP / Прототип:
Команда:
Рынок и партнёрства:
Продажи / Потенциал роста:

Затем выдай итоговую оценку:
Пример: 3.2 из 5 — ниже среднего, требуется доработка.

Пиши без форматирования, без символов выделения, естественным языком, как если бы венчурный аналитик давал краткое заключение в переписке после питча.
Холодный тон, уверенность, конкретика. Краткость важнее вежливости.

Текст презентации для анализа:

{pitch_text}
"""


async def analyze_pitch(pitch_text: str) -> str:
    """
    Analyze startup pitch using Groq API (LLaMA 3).
    
    Args:
        pitch_text: Extracted text from presentation
        
    Returns:
        Analysis result as formatted string
    """
    # Limit text to avoid token limits (approximately 12000 characters ~ 3000 tokens)
    truncated_text = pitch_text[:12000]
    
    if len(pitch_text) > 12000:
        truncated_text += "\n\n[... текст обрезан из-за ограничений ...]"
    
    prompt = ANALYSIS_PROMPT.format(pitch_text=truncated_text)
    
    try:
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "Ты — ArkheAI, беспристрастный венчурный аналитик. "
                               "Твой стиль: холодный, прямой, без дипломатии. "
                               "Оцениваешь только факты, говоришь кратко и жёстко."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=2500
        )
        
        result = response.choices[0].message.content
        
        # Add header
        formatted_result = "🎯 ЭКСПЕРТНЫЙ АНАЛИЗ СТАРТАПА\n"
        formatted_result += "=" * 40 + "\n\n"
        formatted_result += result
        
        return formatted_result
        
    except Exception as e:
        raise Exception(f"Ошибка при обращении к Groq API: {str(e)}")
