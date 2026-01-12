import re
from typing import Dict, List, Optional
from openai import AsyncOpenAI
from config import OPENAI_API_KEY

# System prompt для режима дебатов (пошаговый формат)
DEBATES_SYSTEM_PROMPT = """Ты — старший партнёр венчурного фонда.
Ты проводишь пошаговые инвестиционные дебаты по стартап-презентации.

Задавай ровно один критичный вопрос за сообщение.
После каждого ответа жди следующего сообщения пользователя.
Сохраняй ответы в памяти.

После завершения серии вопросов:
— оцени качество ответов
— укажи слабые места
— предложи улучшенные формулировки на уровне инвестора

Не давай оценок до финального этапа.
Не смягчай формулировки.
Веди себя как скептический инвестор."""

# System prompt для финальной оценки
FEEDBACK_SYSTEM_PROMPT = """Ты — старший партнёр венчурного фонда.
Ты анализируешь качество ответов фаундера в инвестиционных дебатах.

Оцени:
— уровень ясности ответов
— уровень конкретики
— уровень честности

Укажи:
— где пользователь уходил от ответа
— где аргументы не выдерживают давления
— где много допущений

Для каждого слабого ответа покажи:
❌ как было
✅ как должно звучать в разговоре с инвестором

Дай одну короткую, честную фразу в конце.

Не давай инвестиционного решения.
Не стави денежную оценку.
Не хвали без причин."""

# Хранилище состояний дебатов для каждого пользователя
# Структура: {user_id: {
#   "presentation_text": str,
#   "questions": List[str],  # Вопросы от AI
#   "answers": List[str],     # Ответы пользователя
#   "question_count": int     # Счётчик вопросов
# }}
debates_states: Dict[int, Dict] = {}

# Количество вопросов в серии дебатов
DEBATES_QUESTIONS_COUNT = 5


def clean_and_prepare_text(text: str, max_length: int = 50000) -> str:
    """
    Clean and prepare text for analysis.
    Ensures text is readable and within token limits.
    
    Args:
        text: Raw extracted text
        max_length: Maximum character length
        
    Returns:
        Cleaned and prepared text
    """
    if not text or not text.strip():
        return ""
    
    # Remove excessive whitespace but preserve line breaks and structure
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'[ \t]+$', '', text, flags=re.MULTILINE)
    
    # If text is too long, keep the most important parts
    if len(text) > max_length:
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
        
        truncated_text = first_part + "\n\n[... средняя часть текста пропущена ...]\n\n" + last_part
        return truncated_text
    
    return text


def init_debates_session(user_id: int, presentation_text: str) -> None:
    """
    Инициализирует сессию дебатов для пользователя.
    
    Args:
        user_id: ID пользователя Telegram
        presentation_text: Текст презентации
    """
    cleaned_text = clean_and_prepare_text(presentation_text, max_length=50000)
    debates_states[user_id] = {
        "presentation_text": cleaned_text,
        "questions": [],
        "answers": [],
        "question_count": 0
    }


def get_debates_session(user_id: int) -> Optional[Dict]:
    """
    Получает сессию дебатов для пользователя.
    
    Args:
        user_id: ID пользователя Telegram
        
    Returns:
        Словарь с состоянием сессии или None
    """
    return debates_states.get(user_id)


def clear_debates_session(user_id: int) -> None:
    """
    Очищает сессию дебатов для пользователя.
    
    Args:
        user_id: ID пользователя Telegram
    """
    if user_id in debates_states:
        del debates_states[user_id]


def is_debates_finished(user_id: int) -> bool:
    """
    Проверяет, завершены ли дебаты (задано максимальное количество вопросов И получены все ответы).
    
    Args:
        user_id: ID пользователя Telegram
        
    Returns:
        True если дебаты завершены, False иначе
    """
    session = get_debates_session(user_id)
    if not session:
        return False
    # Дебаты завершены, когда задано 5 вопросов И получено 5 ответов
    return (session["question_count"] >= DEBATES_QUESTIONS_COUNT and 
            len(session["answers"]) >= DEBATES_QUESTIONS_COUNT)


async def ask_next_question(user_id: int, user_answer: Optional[str] = None) -> str:
    """
    Задаёт следующий вопрос в дебатах.
    
    Args:
        user_id: ID пользователя Telegram
        user_answer: Ответ пользователя на предыдущий вопрос (None для первого вопроса)
        
    Returns:
        Вопрос от AI или финальная оценка
    """
    session = get_debates_session(user_id)
    if not session:
        raise ValueError("Сессия дебатов не инициализирована. Сначала загрузите презентацию.")
    
    presentation_text = session["presentation_text"]
    questions = session["questions"]
    answers = session["answers"]
    question_count = session["question_count"]
    
    # Проверка наличия API ключа
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not set. Please set OPENAI_API_KEY environment variable.")
    
    # Сохраняем ответ пользователя, если он есть (ВАЖНО: делаем это ПЕРЕД проверкой завершения)
    if user_answer:
        answers.append(user_answer)
    
    # Если дебаты завершены (все вопросы заданы и все ответы получены), возвращаем финальную оценку
    # Проверяем: если вопросов уже 5 И мы только что сохранили ответ на 5-й вопрос (теперь ответов тоже 5)
    if question_count >= DEBATES_QUESTIONS_COUNT and len(answers) >= DEBATES_QUESTIONS_COUNT:
        return await generate_final_feedback(user_id)
    
    # Создаём клиент
    client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    
    # Формируем промпт
    if question_count == 0:
        # Первый вопрос
        prompt = f"""Я изучил презентацию. Задай первый критичный вопрос по проблеме.

Текст презентации:

{presentation_text}

Задай ровно один короткий, критичный вопрос. Без подводок, без списков."""
    else:
        # Последующие вопросы
        # Формируем контекст предыдущих вопросов и ответов
        context = "Предыдущие вопросы и ответы:\n\n"
        for i, (q, a) in enumerate(zip(questions, answers), 1):
            context += f"Вопрос {i}: {q}\nОтвет: {a}\n\n"
        
        prompt = f"""Продолжай дебаты. Задай следующий критичный вопрос.

{context}

Задай ровно один короткий, критичный вопрос. Без подводок, без списков.
Не повторяй предыдущие вопросы."""
    
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": DEBATES_SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.8,
            max_tokens=300  # Короткие вопросы
        )
        
        question = response.choices[0].message.content.strip()
        
        # Сохраняем вопрос и увеличиваем счётчик
        questions.append(question)
        session["question_count"] += 1
        
        return question
        
    except Exception as e:
        raise Exception(f"Ошибка при обращении к OpenAI API: {str(e)}")


async def generate_final_feedback(user_id: int) -> str:
    """
    Генерирует финальную оценку ответов пользователя.
    
    Args:
        user_id: ID пользователя Telegram
        
    Returns:
        Финальная оценка и рекомендации
    """
    session = get_debates_session(user_id)
    if not session:
        raise ValueError("Сессия дебатов не инициализирована.")
    
    presentation_text = session["presentation_text"]
    questions = session["questions"]
    answers = session["answers"]
    
    # Проверка наличия API ключа
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not set. Please set OPENAI_API_KEY environment variable.")
    
    # Формируем контекст всех вопросов и ответов
    qa_context = "Вопросы и ответы в дебатах:\n\n"
    for i, (q, a) in enumerate(zip(questions, answers), 1):
        qa_context += f"Вопрос {i}: {q}\nОтвет: {a}\n\n"
    
    prompt = f"""Проанализируй качество ответов фаундера в инвестиционных дебатах.

Текст презентации:

{presentation_text}

{qa_context}

Дай финальную оценку в следующем формате:

1️⃣ Общая оценка ответов
Кратко: уровень ясности, уровень конкретики, уровень честности.

2️⃣ Ключевые слабости
Где пользователь уходил от ответа, где аргументы не выдерживают давления, где много допущений.

3️⃣ Улучшенные формулировки
Для каждого слабого ответа:
❌ как было
✅ как должно звучать в разговоре с инвестором

4️⃣ Общий вывод
Одна короткая, честная фраза."""
    
    client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": FEEDBACK_SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=2000  # Более длинный ответ для финальной оценки
        )
        
        feedback = response.choices[0].message.content.strip()
        return feedback
        
    except Exception as e:
        raise Exception(f"Ошибка при обращении к OpenAI API: {str(e)}")
