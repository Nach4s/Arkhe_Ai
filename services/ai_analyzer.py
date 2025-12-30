import re
from openai import AsyncOpenAI
from config import OPENAI_API_KEY

ANALYSIS_PROMPT = """
Отвечай строго на языке, который используется в презентации:
- если презентация на русском — только русский,
- если презентация на английском — только английский.

Даже если текст короткий или неполный, анализируй все доступные данные. 
Выводи рекомендации, рейтинг и overall на основе того, что есть.

Ты — ArkheAI, беспристрастный венчурный аналитик и оценщик стартапов.  
Будь холодным, жёстким, профессиональным, пиши только факты.  
Не подбадривай, не мотивируй. Если стартап плохой — говори прямо, без дипломатии.  
Используй стиль венчурного инвестора, который видел сотни провальных питчей.  

Твоя задача — дать **полный, структурированный, аналитический разбор презентации стартапа**.

---

🔍 Оцени стартап по 9 критериям:

1. **Реальная проблема** — 1–2 предложения  
2. **Уникальность решения и конкуренты** — проверяй рынок и анализируй аналогичные проекты  
3. **Целевая аудитория** — кто пользуется и зачем, объём аудитории  
4. **Потенциал и объём рынка (TAM / SAM / SOM)** — кратко и понятно  
5. **MVP / Traction** — реально работающий продукт или только идея, результаты  
6. **Модель монетизации** — как зарабатываются деньги, реалистичность  
7. **Финансовая модель** — реалистична и масштабируема, unit economics, прогнозы  
8. **Основные риски** — команда, технология, конкуренция, рынок, регулирование  
9. **Сравнение с существующими стартапами** — есть ли аналоги, кто и как работает  

---

💫 **Метод Бёркуса (1–5⭐):**

- Идея и ценность  
- MVP / Прототип  
- Команда  
- Рынок и партнёрства  
- Продажи / Потенциал роста  

---

⚡ **В конце** выдай:  

1. **Overall рейтинг** — усреднённый по всем критериям и Бёркусу, например: 3.2⭐ из 5  
2. **Краткий вывод** — структурированно: сильные стороны, слабые стороны, рекомендации по улучшению, без воды.  
3. Если стартап провальный — пиши прямо:  
   “Не вижу ценности. Рынок переполнен. У проекта нет преимуществ.”  
4. Если перспективный — объясни, на чём держится сила.  
5. Дай конкретные рекомендации:  
   - Метрики и цифры, которые нужно показать инвестору  
   - Демонстрацию MVP или примеры отчётов  
   - Конкурентные таблицы  
   - Улучшение финансовой модели  

---

⚠️ **Тон и стиль:**  

- Холодный, уверенный, профессиональный  
- Кратко, по делу, структурировано  
- Не используй слова типа “возможно”, “интересно”, “может быть”  
- Таблицы и bullet points приветствуются  
- В конце обязательно **overall ⭐ рейтинг и финальный вывод**

---

📌 **Пример структуры ответа:**

**Сильные стороны:**  
1. …  
2. …  

**Слабые стороны:**  
1. …  
2. …  

**Рекомендации по улучшению:**  
1. …  
2. …  

**Метод Бёркуса:**  
- Идея: ⭐⭐⭐☆☆  
- MVP: ⭐⭐☆☆☆  
- Команда: ⭐⭐⭐⭐☆  
- Рынок: ⭐⭐☆☆☆  
- Продажи: ⭐⭐☆☆☆  

**Overall:** 3.2⭐ из 5 — ниже среднего, требуется доработка.  
**Краткий вывод:** …  

Текст презентации для анализа:

{pitch_text}
"""


def clean_and_prepare_text(text: str, max_length: int = 50000) -> str:
    """
    Clean and prepare text for analysis.
    Ensures text is readable and within token limits.
    
    Args:
        text: Raw extracted text
        max_length: Maximum character length (default ~12500 tokens for gpt-4o-mini)
        
    Returns:
        Cleaned and prepared text
    """
    if not text or not text.strip():
        return ""
    
    # Remove excessive whitespace but preserve line breaks and structure
    # Replace multiple spaces with single space, but keep newlines
    text = re.sub(r'[ \t]+', ' ', text)  # Multiple spaces/tabs to single space
    text = re.sub(r'[ \t]+$', '', text, flags=re.MULTILINE)  # Trailing spaces
    
    # If text is too long, try to keep the most important parts
    if len(text) > max_length:
        # Keep first part (usually title/intro) and last part (usually conclusion)
        # This preserves context better than simple truncation
        first_part = text[:max_length // 2]
        last_part = text[-max_length // 2:]
        
        # Try to find a good break point (end of sentence)
        last_sentence_end = max(
            last_part.rfind('. '),
            last_part.rfind('.\n'),
            last_part.rfind('! '),
            last_part.rfind('? ')
        )
        
        if last_sentence_end > 0:
            last_part = last_part[last_sentence_end + 2:]
        
        truncated_text = first_part + "\n\n[... средняя часть текста пропущена для экономии токенов ...]\n\n" + last_part
        return truncated_text
    
    return text


async def analyze_pitch(pitch_text: str) -> str:
    """
    Analyze startup pitch using OpenAI API.
    
    Args:
        pitch_text: Extracted text from presentation
        
    Returns:
        Analysis result as formatted string
    """
    # Проверка наличия API ключа
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not set. Please set OPENAI_API_KEY environment variable.")
    
    # Clean and prepare text (increased limit for better context)
    # gpt-4o-mini supports up to 128k tokens, so we can use more text
    cleaned_text = clean_and_prepare_text(pitch_text, max_length=50000)
    
    if not cleaned_text or len(cleaned_text.strip()) < 50:
        raise ValueError("Текст слишком короткий для анализа. Убедитесь, что презентация содержит достаточно информации.")
    
    prompt = ANALYSIS_PROMPT.format(pitch_text=cleaned_text)
    
    # Создаем клиент только при использовании
    client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Ты — ArkheAI, беспристрастный венчурный аналитик. "
                               "Твой стиль: холодный, прямой, без дипломатии. "
                               "Оцениваешь только факты, говоришь кратко и жёстко. "
                               "Отвечай строго на том языке, который используется в презентации."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=4000  # Increased for more detailed analysis
        )
        
        result = response.choices[0].message.content
        
        # Add header
        formatted_result = "🎯 ЭКСПЕРТНЫЙ АНАЛИЗ СТАРТАПА\n"
        formatted_result += "=" * 40 + "\n\n"
        formatted_result += result
        
        return formatted_result
        
    except Exception as e:
        raise Exception(f"Ошибка при обращении к OpenAI API: {str(e)}")
