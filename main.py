import asyncio
from typing import Optional

import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.utils import executor
from read import google_sheet_data


API_TOKEN = '5514292270:AAH1msjM6OtxCf_eyrzprevaBpnwH2ZlsCY'
channel = '-1001881174183'

loop = asyncio.get_event_loop()

bot = Bot(token=API_TOKEN, loop=loop)

# For example use simple MemoryStorage for Dispatcher.
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

sheet_data = google_sheet_data()


# States
class Form(StatesGroup):
    id = State()  # Will be represented in storage as 'Form:name'
    password = State()  # Will be represented in storage as 'Form:age'
    # gender = State()  # Will be represented in storage as 'Form:gender'


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    """
    Conversation's entry point
    """

    await Form.id.set()

    # Set state
    await message.answer("Привет ! Введите ваш ид номер!")


# You can use state '*' if you need to handle all states
@dp.message_handler(state='*', commands=['cancel'])
@dp.message_handler(lambda message: message.text.lower() == 'cancel', state='*')
async def cancel_handler(message: types.Message, state: FSMContext, raw_state: Optional[str] = None):
    """
    Allow user to cancel any action
    """
    if raw_state is None:
        return

    # Cancel state and inform user about it
    await state.finish()
    # And remove keyboard (just in case)
    await message.reply('Отменено.')


@dp.message_handler(state=Form.id)
async def process_id(message: types.Message, state: FSMContext):
    """
    Process user ID
    """
    async with state.proxy() as data:
        data['id'] = message.text

    await Form.next()
    await message.reply("Пожалуйста введите ваш пароль!")

# Check password. Password gotta be str
@dp.message_handler(state=Form.password)
async def process_password(message: types.Message, state: FSMContext):
    
    async with state.proxy() as data:
        
        data['password'] = message.text

        count = 0
        checking = 0
        
        for cell in sheet_data:
            
            count += 1

            if str(cell[0]) == str(data['id']):

                checking = 1
                break

            else:
                checking = 0

        if checking == 1:

            user_info = sheet_data[count-1]

            if str(user_info[1]) == str(data['password']):

                await bot.send_message(message.chat.id,
                    md.text("👤", md.bold(user_info[2]),
                    md.text("🔳 Должность - ", user_info[3],), "\n",
                    md.text("🔶 Норма рабочих дней - ", user_info[4],),
                    md.text("✅ Факт рабочие дни - ", user_info[5],), "\n",
                    md.text("🔶 Норма оклада - ", user_info[6], "сум",),
                    md.text("✅ Сумма оклада - ", user_info[7], "сум",), "\n",
                    md.text("🔶 Норма среднего балла - ", user_info[8],),
                    md.text("✅ Средный бал за месяц - ", user_info[9],), "\n",
                    md.text("🔶 Процент выполнения продаж - ", user_info[10], "сум"),
                    md.text("✅ Сумма от продаж - ", user_info[11], "сум"), "\n",
                    md.text("🔶 Норма суммы KPI - ", user_info[12], "сум"),
                    md.text("💰 Факт суммы KPI - ", user_info[13], "сум"), "\n",
                    md.text("✅ Норма общего з/п", user_info[14], "сум"),
                    md.text("🔶 Общая сумма з/п", user_info[15], "сум"), "\n",
                    md.text("🔴 Потеря з/п", user_info[16], "сум"),
                    sep='\n'), parse_mode=ParseMode.MARKDOWN)

                await bot.send_message(chat_id=channel, text=f"ID ПОЛЬЗОВАТЕЛЯ - {message.from_user.id}\n"
                                                             f"ИМЯ ПОЛЬЗОВАТЕЛЯ - {message.from_user.full_name}s\n"
                                                             f"ПОЛЬЗОВАТЕЛЬ username - @{message.from_user.username}\n"
                                                             f"ПОЛЬЗОВАТЕЛЬ СМОТРЕТЬ ИЗ ДАННЫХ - {user_info[2]}",
                                       )
            else:
                await message.reply('Пароль пользователя не подходит! Пожалуйста, введите /start снова!')
        else:
            await message.reply('Идентификационный номер пользователя не совпадает! Пожалуйста, введите /start снова!')

        # Finish conversation
        data.state = None


if __name__ == '__main__':
    executor.start_polling(dp, loop=loop, skip_updates=True)