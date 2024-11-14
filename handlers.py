from aiogram import types, F, Router
from aiogram.filters import Command
from aiogram.filters.command import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from service import (
    get_length_quiz,
    get_right_option,
    get_question,
    get_quiz_index,
    get_quiz_score,
    new_quiz,
    update_quiz_index,
)


router = Router()


@router.callback_query(F.data == "right_answer")
async def right_answer(callback: types.CallbackQuery):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
    await callback.message.answer("Верно!")
    current_question_index = await get_quiz_index(callback.from_user.id)
    score = await get_quiz_score(callback.from_user.id)
    current_question_index += 1
    score += 1
    await update_quiz_index(callback.from_user.id, current_question_index, score)
    if current_question_index <= await get_length_quiz():
        await get_question(callback.message, callback.from_user.id)
    else:
        await callback.message.answer(
            f'Это был последний вопрос. Квиз завершен! '
            f'Вы набрали {score} балов из 10'
        )

  
@router.callback_query(F.data == "wrong_answer")
async def wrong_answer(callback: types.CallbackQuery):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
    current_question_index = await get_quiz_index(callback.from_user.id)
    score = await get_quiz_score(callback.from_user.id)
    correct_option = await get_right_option(current_question_index)
    await callback.message.answer(
        f'Неправильно. Правильный ответ: {correct_option}'
    )
    current_question_index += 1
    await update_quiz_index(
        callback.from_user.id,
        current_question_index,
        score,
    )
    if current_question_index <= await get_length_quiz():
        await get_question(callback.message, callback.from_user.id)
    else:
        await callback.message.answer(
            f'Это был последний вопрос. Квиз завершен! '
            f'Вы набрали {score} балов из 10'
        )


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Начать игру"))
    await message.answer_photo(
        types.FSInputFile('/function/storage/bot_media/quiz-python.png'),
    )
    await message.answer(
        "Добро пожаловать в квиз!",
        reply_markup=builder.as_markup(resize_keyboard=True),
    )


@router.message(F.text=="Начать игру")
@router.message(Command("quiz"))
async def cmd_quiz(message: types.Message):
    await message.answer(f"Давайте начнем квиз!")
    await new_quiz(message)
