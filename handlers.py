from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from states import Form
import aiohttp

router = Router()

users_ds = {}

# Обработчик команды /start
@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.reply("Добро пожаловать! Я ваш бот.\nВведите /help для списка команд.")

# Обработчик команды /help
@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.reply(
        "Доступные команды:\n"
        "/start - Начало работы\n"
        "/set_profile - Настройка профиля пользователя\n"
        "/log_water - Логирование воды\n"
        "/log_food - Логирование еды\n"
        "/log_workout - Логирование тренировок\n"
        "/check_progress - Прогресс по воде и калориям\n"
    )

# FSM: диалог с пользователем для внесения информации о нем
@router.message(Command("set_profile"))
async def start_form(message: Message, state: FSMContext):
    await message.reply("Введите ваш вес (в кг):")
    await state.set_state(Form.weight)

@router.message(Form.weight)
async def process_weight(message: Message, state: FSMContext):
    await state.update_data(weight=message.text)
    await message.reply("Введите ваш рост (в см):")
    await state.set_state(Form.height)

@router.message(Form.height)
async def process_height(message: Message, state: FSMContext):
    await state.update_data(height=message.text)
    await message.reply("Введите ваш возраст:")
    await state.set_state(Form.age)

@router.message(Form.age)
async def process_age(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.reply("Сколько минут активности у вас в день?")
    await state.set_state(Form.activity)

@router.message(Form.activity)
async def process_activity(message: Message, state: FSMContext):
    await state.update_data(activity=message.text)
    await message.reply("В каком городе вы находитесь?")
    await state.set_state(Form.location)

@router.message(Form.location)
async def process_location(message: Message, state: FSMContext):
    data = await state.get_data()
    print(f'data: {data}')
    weight = int(data.get("weight"))
    height = int(data.get("height"))
    age = int(data.get("age"))
    activity = int(data.get("activity"))
    location = message.text

    new_user_info = {
        "weight": weight,
        "height": height,
        "age": age,
        "activity": activity,
        "city": location,
        "water_goal": weight * 30 + 500 * int(activity)//30 + 500,
        "calorie_goal": 10 * weight + 6.25 * height - 5 * age,
        "logged_water": 0,
        "logged_calories": 0,
        "burned_calories": 0,

    }
    users_ds.update({message.from_user.id: new_user_info})
    print(f"users_ds: {users_ds}")
    await message.reply(f"Информация о пользователе записана")
    await state.clear()

# Логирование воды
@router.message(Command("log_water"))
async def log_water(message: Message, command: CommandObject):
    if command.args is None:
        await message.answer(
            "Ошибка: не переданы аргументы"
        )
        return
    
    if not command.args.isdigit():
        await message.answer(
            "Ошибка: неправильный формат ввода количества воды. Пример:\n"
            "/log_water <количество>"
        )
        return
    
    water_consumed = int(command.args)
    if water_consumed <= 0:
        await message.answer(
            "Ошибка: Количество выпитой воды должно быть больше чем 0 мл."
        )
        return
    
    if message.from_user.id not in users_ds:
        await message.answer(
            "Ошибка: Пользователь не занесен в базу данных.\n"
            "Внесите данные и повторите попытку"
        )
        return
    
    water_consumed = int(command.args)
    users_ds.get(message.from_user.id)["logged_water"] += water_consumed    

@router.message(Command("show_users"))
async def show_users(message: Message):
    await message.answer(f"users_ds: {users_ds}")

# Функция для подключения обработчиков
def setup_handlers(dp):
    dp.include_router(router)