from aiogram import types

kb_back = [
    [
        types.KeyboardButton(text='Назад')
    ]
]

kb_choice = [
    [
        types.KeyboardButton(text='Проверить артикулы'),
        types.KeyboardButton(text='Топы продаж')
    ],
    [
        types.KeyboardButton(text='Загрузить прокси')
    ]
]

def get_kb_back():
    return types.ReplyKeyboardMarkup(keyboard=kb_back, resize_keyboard=True)


def get_kb_choice():
    return types.ReplyKeyboardMarkup(keyboard=kb_choice, resize_keyboard=True)