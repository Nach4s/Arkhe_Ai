import logging
from aiogram import Router, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from services.debates_service import (
    init_debates_session,
    get_debates_session,
    clear_debates_session,
    ask_next_question,
    is_debates_finished
)

router = Router()
logger = logging.getLogger("arkheai")


class DebatesStates(StatesGroup):
    """Состояния FSM для режима дебатов."""
    waiting_for_answer = State()  # Ожидание ответа пользователя


@router.message(Command("debates"))
async def debates_cmd(message: types.Message, state: FSMContext):
    """
    Обработчик команды /debates.
    Запускает режим дебатов, если презентация уже загружена.
    """
    user_id = message.from_user.id
    
    # Проверяем, есть ли загруженная презентация
    session = get_debates_session(user_id)
    
    if not session:
        await message.answer(
            "📄 Для начала дебатов сначала загрузите презентацию (PDF или PPTX).\n\n"
            "Отправьте файл презентации, затем введите /debates для начала дебатов."
        )
        return
    
    # Проверяем, не завершены ли уже дебаты
    if is_debates_finished(user_id):
        await message.answer(
            "Дебаты уже завершены. Загрузите новую презентацию для начала новых дебатов."
        )
        return
    
    # Начинаем дебаты
    try:
        await message.answer("Запускаю режим дебатов...")
        
        # Задаём первый вопрос
        first_question = await ask_next_question(user_id)
        
        # Отправляем первый вопрос
        await message.answer(first_question)
        
        # Переходим в состояние ожидания ответа
        await state.set_state(DebatesStates.waiting_for_answer)
        
    except Exception as e:
        logger.error(f"Ошибка при запуске дебатов: {e}", exc_info=True)
        await message.answer(
            f"Ошибка при запуске дебатов: {str(e)}\n\n"
            "Попробуйте загрузить презентацию заново и повторить команду /debates."
        )
        await state.clear()


@router.message(
    StateFilter(DebatesStates.waiting_for_answer),
    F.text,
    ~F.text.startswith('/')
)
async def handle_debates_answer(message: types.Message, state: FSMContext):
    """
    Обработчик ответов пользователя в режиме дебатов.
    Срабатывает только в состоянии waiting_for_answer.
    """
    user_id = message.from_user.id
    user_answer = message.text.strip()
    
    # Проверяем, есть ли активная сессия дебатов
    session = get_debates_session(user_id)
    
    if not session:
        await message.answer("Сессия дебатов не найдена. Введите /debates для начала.")
        await state.clear()
        return
    
    # Проверяем, не завершены ли уже дебаты
    if is_debates_finished(user_id):
        await message.answer("Дебаты уже завершены.")
        await state.clear()
        return
    
    # Продолжаем дебаты
    try:
        # Показываем индикатор печати
        await message.bot.send_chat_action(message.chat.id, "typing")
        
        # Задаём следующий вопрос (или получаем финальную оценку)
        next_response = await ask_next_question(user_id, user_answer)
        
        # Отправляем ответ AI
        await message.answer(next_response)
        
        # Если дебаты завершены, автоматически останавливаем дебаты
        if is_debates_finished(user_id):
            # Автоматически очищаем сессию и состояние (эквивалент /stop)
            clear_debates_session(user_id)
            await state.clear()
            # Сообщение о завершении уже отправлено в финальной оценке
        # Иначе остаёмся в состоянии ожидания ответа
        
    except Exception as e:
        logger.error(f"Ошибка при продолжении дебатов: {e}", exc_info=True)
        await message.answer(
            f"Ошибка при обработке ответа: {str(e)}\n\n"
            "Попробуйте ответить ещё раз или введите /debates для перезапуска."
        )


@router.message(Command("end_debates", "stop"))
async def end_debates_cmd(message: types.Message, state: FSMContext):
    """
    Обработчик команд /end_debates и /stop.
    Завершает режим дебатов и очищает сессию.
    """
    user_id = message.from_user.id
    
    session = get_debates_session(user_id)
    
    if not session:
        await message.answer("Активная сессия дебатов не найдена.")
        await state.clear()
        return
    
    clear_debates_session(user_id)
    await state.clear()
    await message.answer(
        "Режим дебатов завершён.\n\n"
        "Для начала новых дебатов загрузите презентацию и введите /debates."
    )
