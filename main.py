import logging
import sys

from aiogram import Bot, Dispatcher, types, F
import pyodbc
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.methods import DeleteWebhook
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from config import TOKEN_API, SQL_SERVER
import asyncio
from commands import add_request, finding_amb
class RequestState(StatesGroup):
    wait_name = State()
    wait_text = State()
    checking = State()

storage = MemoryStorage()
bot =Bot(token=TOKEN_API)
dp = Dispatcher(storage=storage)

all_requests = list()

conn = pyodbc.connect(SQL_SERVER)

@dp.message(Command("start"))
async def help_cmd(message: types.Message, state: FSMContext):
    await bot.send_message(chat_id=message.from_user.id, text="Напишите ФИО (пример: Иванов Иван Иванович):", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(RequestState.wait_name)

@dp.message(Command("check"))
async def help_cmd(message: types.Message, state: FSMContext):
    if len(all_requests) != 0:
        ikb = types.ReplyKeyboardMarkup(keyboard=all_requests, resize_keyboard=True)
        await bot.send_message(chat_id=message.from_user.id, text="Выберить заявку, исходя из текста заявки:", reply_markup=ikb)
        await state.set_state(RequestState.checking)

#@dp.message(RequestState.checking)
#async def qr_cmd(message: types.Message, state: FSMContext):
#    res =
#    if len(message.text.split(" ")) != 3:
#        await bot.send_message(chat_id=message.from_user.id, text="Неправильно написано ФИО!! Давайте попробуем еще раз", reply_markup=types.ReplyKeyboardRemove())
#        await bot.send_message(chat_id=message.from_user.id, text="Напишите ФИО (пример: Иванов Иван Иванович):")
#        await state.set_state(RequestState.wait_name)

@dp.message(RequestState.wait_name)
async def qr_cmd(message: types.Message, state: FSMContext):
    if len(message.text.split(" ")) != 3:
        await bot.send_message(chat_id=message.from_user.id, text="Неправильно написано ФИО!! Давайте попробуем еще раз", reply_markup=types.ReplyKeyboardRemove())
        await bot.send_message(chat_id=message.from_user.id, text="Напишите ФИО (пример: Иванов Иван Иванович):")
        await state.set_state(RequestState.wait_name)
    else:
        await state.update_data(name=message.text)
        await bot.send_message(chat_id=message.from_user.id, text="Напишите Текст заявки:", reply_markup=types.ReplyKeyboardRemove())
        await state.set_state(RequestState.wait_text)
    
@dp.message(RequestState.wait_text)
async def qr_cmd(message: types.Message, state: FSMContext):
    await state.update_data(textt=message.text)
    btn = types.KeyboardButton(text=message.text)
    all_requests.append([btn])
    doc_data = await state.get_data()
    await bot.send_message(chat_id=message.from_user.id, text="Отправляю" , reply_markup=types.ReplyKeyboardRemove())
    try:
        await add_request(doc_data['name'], doc_data['textt'])
        await bot.send_message(chat_id=message.from_user.id, text="Успешно!!!")
    except Exception as e:
        await bot.send_message(chat_id=message.from_user.id, text=str(e))


async def main() -> None:
    await bot(DeleteWebhook(drop_pending_updates=True))
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
