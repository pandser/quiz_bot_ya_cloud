from  database import pool, execute_update_query, execute_select_query
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types


def generate_options_keyboard(answer_options, right_answer):
    builder = InlineKeyboardBuilder()
    for option in answer_options:
        builder.add(types.InlineKeyboardButton(
            text=option,
            callback_data="right_answer" if option == right_answer else "wrong_answer")
        )
    builder.adjust(1)
    return builder.as_markup()


async def get_question(message, user_id):
    '''Получение текущего вопроса из словаря состояний пользователя.'''

    current_question_index = await get_quiz_index(user_id)
    right_option = await get_right_option(current_question_index)
    opts = await get_options(current_question_index)
    kb = generate_options_keyboard(opts, right_option)
    question = await get_question_text(current_question_index)
    await message.answer(f"{question}", reply_markup=kb)


async def new_quiz(message):
    '''Старт нового квиза.'''

    user_id = message.from_user.id
    current_question_index = 1
    score = 0
    await update_quiz_index(user_id, current_question_index, score)
    await get_question(message, user_id)


async def get_quiz_index(user_id):
    '''Получение индекса текущего вопроса.'''

    get_user_index = f'''
        DECLARE $user_id AS Uint64;

        SELECT question_index
        FROM `quiz_state`
        WHERE user_id == $user_id;
    '''
    results = execute_select_query(pool, get_user_index, user_id=user_id)
    if len(results) == 0:
        return 0
    if results[0]['question_index'] is None:
        return 0
    return results[0]['question_index']


async def get_quiz_score(user_id):
    '''Получение количества правильных ответов.'''

    get_user_index = f'''
        DECLARE $user_id AS Uint64;

        SELECT score
        FROM `quiz_state`
        WHERE user_id == $user_id;
    '''
    results = execute_select_query(pool, get_user_index, user_id=user_id)
    if len(results) == 0:
        return 0
    if results[0]['score'] is None:
        return 0
    return results[0]['score']


async def get_question_text(question_id):
    '''Получение текста вопроса.'''

    stmt = '''
        DECLARE $question_id AS Uint64;

        SELECT question_text
        FROM `questions`
        WHERE question_id == $question_id;
    '''
    results = execute_select_query(
        pool,
        stmt,
        question_id=question_id,
    )
    if len(results) == 0:
        return 0
    if results[0]['question_text'] is None:
        return 0
    return results[0]['question_text'].decode('utf-8')


async def get_options(question_id):
    '''Получение вариантов ответа.'''

    stmt = '''
        DECLARE $question_id AS Uint64;

        SELECT option_text
        FROM `options`
        WHERE question_id == $question_id;
    '''
    results = execute_select_query(
        pool,
        stmt,
        question_id=question_id,
    )
    if len(results) == 0:
        return ['нет вариантов']
    if results[0]['option_text'] is None:
        return ['нет вариантов']
    return [result['option_text'].decode('utf-8') for result in results]


async def get_right_option(question_id):
    '''Получение правильного ответа.'''

    stmt = '''
        DECLARE $question_id AS Uint64;

        SELECT option_text
        FROM `options`
        WHERE question_id == $question_id AND right == true;
    '''
    results = execute_select_query(
        pool,
        stmt,
        question_id=question_id,
    )
    if len(results) == 0:
        return 0
    if results[0]['option_text'] is None:
        return 0
    return results[0]['option_text'].decode('utf-8')


async def get_length_quiz():
    '''Получение количества вопросов в квизе.'''

    stmt = '''
        SELECT question_id
        FROM `questions`;
    '''
    results = execute_select_query(
        pool,
        stmt,
    )
    return len(results)
    

async def update_quiz_index(user_id, question_index, score):
    '''Обновление записи в таблице.'''

    set_quiz_state = f'''
        DECLARE $user_id AS Uint64;
        DECLARE $question_index AS Uint64;
        DECLARE $score AS Uint64;

        UPSERT INTO `quiz_state` (`user_id`, `question_index`, `score`)
        VALUES ($user_id, $question_index, $score);
    '''
    execute_update_query(
        pool,
        set_quiz_state,
        user_id=user_id,
        question_index=question_index,
        score=score,
    )
    