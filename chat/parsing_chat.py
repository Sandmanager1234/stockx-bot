import os
from aiogram import Router, types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot import bot
from chat.kbs import get_kb_back, get_kb_choice
from parsers import check_articles, top_sells

parse = Router()

class Do(StatesGroup):
    ask_proxy_file = State()
    ask_arts_file = State()
    ask_top_userbrand = State()
    ask_top_file = State()
    upload_arts_file = State()


@parse.message(Command(commands=['start']))
async def bot_start(msg: types.Message):
    await msg.answer('Перед работой убедитесь, что на сервер загружены рабочие прокси!')
    await msg.answer('Ожидаю команду', reply_markup=get_kb_choice())


@parse.message(Do.ask_arts_file)
async def get_arts_file(msg: types.Message, state: FSMContext):
    if msg.document is not None:
        file_id = msg.document.file_id
        file_name = msg.document.file_name
        if file_name.split('.')[-1] == 'xlsx' or file_name.split('.')[-1] == 'xls':
            file = await bot.get_file(file_id)
            file_path = file.file_path
            await bot.download_file(file_path, file_name)
            await msg.answer('Файл загружен.', reply_markup=types.ReplyKeyboardRemove)
            try:
                message = await msg.answer('Начинается парсинг.')
                await upload_arts_file(msg, state, file_name, message)
            except Exception as ex:
                await message.edit_text(f'Ошибка: {ex}')
                await msg.answer('Продолжайте работу.', reply_markup=get_kb_choice())
                await state.clear()
        else:
            msg.answer(f'Неправильный формат файла. Файл должен быть в формате xlsx или xls, а не {file_name.split(".")[-1]}.') 
    elif msg.text == 'Назад':
        await msg.answer('Вы отменили загрузку файла с артикулами. Продолжайте работу.', reply_markup=get_kb_choice())
        await state.clear()
    else:
        await msg.answer('Ожидаю загрузки Excel файла.', reply_markup=get_kb_back())

async def upload_arts_file(msg: types.Message, state: FSMContext, file_name: str, my_message: types.Message):
    await check_articles.find_goods(file_name, my_message)
    await my_message.edit_text('Готово!')
    file = types.FSInputFile(file_name)
    await msg.answer_document(file)
    os.remove(file_name)
    await msg.answer('Можете продолжить работу.', reply_markup=get_kb_choice())
    await state.clear()


@parse.message(Do.ask_proxy_file)
async def get_proxy_file(msg: types.Message, state: FSMContext):
    if msg.document is not None:
        file_id = msg.document.file_id
        file_name = msg.document.file_name
        if file_name.split('.')[-1] == 'txt':
            file = await bot.get_file(file_id)
            file_path = file.file_path
            await bot.download_file(file_path, 'proxy-list.txt')
            await msg.answer('Файл успешно загружен.')
            await msg.answer('Можете продолжить работу.', reply_markup=get_kb_choice())
            await state.clear()
        else:
            msg.answer(f'Неправильный формат файла. Файл должен быть в формате txt, а не {file_name.split(".")[-1]}.')   
    elif msg.text == 'Назад':
        await msg.answer('Вы отменили загрузку файла с прокси. Продолжайте работу.', reply_markup=get_kb_choice())
        await state.clear()
    else:
        await msg.answer('Ожидаю загрузки файла с прокси.', reply_markup=get_kb_back())


@parse.message(Do.ask_top_userbrand)
async def get_top_userbrand(msg: types.Message, state: FSMContext):
    if msg.text is not None and  msg.text != 'Назад':
        await state.set_data({'userbrand': msg.text.strip()})
        try:
            message = await msg.answer('Начинается парсинг.')
            await upload_top_file(msg, state, message)
        except Exception as ex:
            await message.edit_text(f'Ошибка: {ex}')
            await msg.answer('Продолжайте работу.', reply_markup=get_kb_choice())
            await state.clear()
    elif msg.text == 'Назад':
        await msg.answer('Жду команду', reply_markup=get_kb_choice())
        await state.clear()
    else:
        await msg.answer('Введите название бренда.')

async def upload_top_file(msg: types.Message, state: FSMContext, my_message: types.Message):
    data = await state.get_data()
    await top_sells.get_top(data['userbrand'], my_message)
    await my_message.edit_text('Готово!')
    file = types.FSInputFile('top_sells.xlsx')
    await msg.answer_document(file)
    os.remove('top_sells.xlsx')
    await msg.answer('Можете продолжить работу.', reply_markup=get_kb_choice())
    await state.clear()


@parse.message()
async def wait_command(msg: types.Message, state: FSMContext):
    if msg.text == 'Проверить артикулы':
        await msg.answer('Перед работой убедитесь, что на сервер загружены рабочие прокси min = 30.')
        await msg.answer('Загрузите Excel файл с артикулами товаров.', reply_markup=get_kb_back())
        await state.set_state(Do.ask_arts_file)
    elif msg.text == 'Топы продаж':
        await msg.answer('Перед работой убедитесь, что на сервер загружены рабочие прокси min = 30.')
        await msg.answer('Введите бренд, по которому хотите собрать топы продаж.', reply_markup=get_kb_back())
        await state.set_state(Do.ask_top_userbrand)
    elif msg.text == 'Загрузить прокси':
        await msg.answer('Загрузите txt файл, где в каждой новой строке указаны прокси в следующем формате: user:pass@host:port. Min=30', reply_markup=get_kb_back())
        await state.set_state(Do.ask_proxy_file)
    else:
        await msg.answer('Ожидаю команду.', reply_markup=get_kb_choice())
