import re
from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from states import Form
from utils import get_current_temperature, translate_rus_to_eng, get_food_data, get_workout_data
from config import NUTRIONIX_APP_ID, NUTRIONIX_API_KEY, OPENWEATHERMAP_API_KEY
from supports import calc_water_goal, calc_calorie_goal, calc_calorie_consumption, water_requierement

city_pattern = r'\b[a-zа-я][a-zа-я]*(?:-[a-zа-я][a-zа-я]*)?\b'
comp_city_patt = re.compile(city_pattern, re.IGNORECASE)

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
    if not message.text.isdigit():
        await message.answer(
            "Ошибка: неправильный формат для веса.\n"
            "Укажмите ваш вес в формате числа"
        )
        return
    else:
        await state.update_data(weight=message.text)
        await message.reply("Введите ваш рост (в см):")
        await state.set_state(Form.height)

@router.message(Form.height)
async def process_height(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer(
            "Ошибка: неправильный формат для роста.\n"
            "Укажмите ваш роста в формате числа"
        )
        return
    else:
        await state.update_data(height=message.text)
        await message.reply("Введите ваш возраст:")
        await state.set_state(Form.age)

@router.message(Form.age)
async def process_age(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer(
            "Ошибка: неправильный формат для возраста.\n"
            "Укажмите ваш возраст в формате числа"
        )
        return
    else:
        await state.update_data(age=message.text)
        await message.reply("Сколько минут активности у вас в день?")
        await state.set_state(Form.activity)

@router.message(Form.activity)
async def process_activity(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer(
            "Ошибка: неправильный формат для параметра мин. активности/день.\n"
            "Укажмите мин. активности/день возраст в формате числа"
        )
        return
    else:
        await state.update_data(activity=message.text)
        await message.reply("В каком городе вы находитесь?")
        await state.set_state(Form.location)

@router.message(Form.location)
async def process_location(message: Message, state: FSMContext):
    if comp_city_patt.match(message.text):
        data = await state.get_data()
        weight = int(data.get("weight"))
        height = int(data.get("height"))
        age = int(data.get("age"))
        activity = int(data.get("activity"))
        location = message.text

        user_loc_temp = await get_current_temperature(location, OPENWEATHERMAP_API_KEY)

        logged_water, logged_calories, burned_calories = 0, 0, 0

        new_user_info = {
            "weight": weight,
            "height": height,
            "age": age,
            "activity": activity,
            "city": location,
            "water_goal": calc_water_goal(weight, activity, user_loc_temp),
            "calorie_goal": calc_calorie_goal(weight, height, age),
            "logged_water": logged_water,
            "logged_calories": logged_calories,
            "burned_calories": burned_calories,

        }
        users_ds.update({message.from_user.id: new_user_info})
        

        await message.answer(
            "✅ Профиль успешно настроен!\n"
            f"Вес: {weight} кг\n"
            f"Рост: {height} см\n"
            f"Возраст: {age} лет\n"
            f"Активность: {activity} минут\n"
            f"Город: {location}\n"
            f"Норма воды: {calc_water_goal(weight, activity, user_loc_temp)} мл\n"
            f"Цель по калориям: {calc_calorie_goal(weight, height, age)} ккал\n"
            f"Выпито воды: {logged_water} мл\n"
            f"Потреблено калорий: {logged_calories} ккал\n"
            f"Сожжено калорий: {burned_calories} ккал\n"
        )
        await state.clear()

    else:
        await message.answer(
            "Ошибка: неправильный формат для города вашего проживания.\n"
            "Укажмите город вашего проживания в текстовом формате"
        )
        return

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
    
    users_ds.get(message.from_user.id)["logged_water"] += water_consumed

    await message.answer(
        f"Выпито {water_consumed} мл. воды\n"
        )

# Логирование еды
@router.message(Command("log_food"))
async def log_water(message: Message, command: CommandObject):
    if command.args is None:
        await message.answer(
            "Ошибка: не переданы аргументы"
        )
        return

    try:
        product, gramms = command.args.split(" ", maxsplit=1)
    except:
        await message.answer(
            "Ошибка: неправильный формат ввода количества еды. Пример:\n"
            "/log_food <еда, которую вы съели> <количество съеденной еды в граммах>"
        )
        return

    if not gramms.isdigit():
        await message.answer(
            "Ошибка: неправильный формат ввода количества еды. Пример:\n"
            "/log_food банан 123"
        )
        return
    
    gramms = int(gramms)
    if gramms <= 0:
        await message.answer(
            "Ошибка: Количество съеденной еды должно быть > 0"
        )
        return
    
    if message.from_user.id not in users_ds:
        await message.answer(
            "Ошибка: Пользователь не занесен в базу данных.\n"
            "Внесите данные и повторите попытку"
        )
        return

    product = product.lower()
    eng_product = await translate_rus_to_eng(product)
    
    product_info = await get_food_data(eng_product, 
                                       NUTRIONIX_APP_ID, 
                                       NUTRIONIX_API_KEY)
    product_cal = product_info["foods"][0]["nf_calories"]
    
    user_cons_cal = calc_calorie_consumption(product_cal, gramms)
    users_ds.get(message.from_user.id)["logged_calories"] += user_cons_cal

    await message.answer(
        f"{product} - {product_cal} ккал. на 100 г.\n"
        f"Было потреблено {user_cons_cal} ккал."
        )
    
# Логирование тренировок
@router.message(Command("log_workout"))
async def log_workout(message: Message, command: CommandObject):
    if command.args is None:
        await message.answer(
            "Ошибка: не переданы аргументы"
        )
        return

    try:
        train_type, duration = command.args.split(" ", maxsplit=1)
    except:
        await message.answer(
            "Ошибка: неправильный формат ввода тренировки. Пример:\n"
            "/log_workout <тип тренировки> <время (мин)>"
        )
        return

    if not duration.isdigit():
        await message.answer(
            "Ошибка: неправильный формат ввода времени тренировки. Пример:\n"
            "/log_workout отжимания 5"
        )
        return
    
    duration = int(duration)
    if duration <= 0:
        await message.answer(
            "Ошибка: Время тренировки должно быть > 0"
        )
        return
    
    if message.from_user.id not in users_ds:
        await message.answer(
            "Ошибка: Пользователь не занесен в базу данных.\n"
            "Внесите данные и повторите попытку"
        )
        return

    train_type = train_type.lower()
    eng_train_type = await translate_rus_to_eng(train_type)

    train_info = await get_workout_data(duration, 
                                        eng_train_type, 
                                        NUTRIONIX_APP_ID, 
                                        NUTRIONIX_API_KEY)
    burned_calories = train_info['exercises'][0]['nf_calories']
    water_needed = water_requierement(duration)
    
    users_ds.get(message.from_user.id)["burned_calories"] += burned_calories

    await message.answer(
        f"{train_type} {duration} минут - {burned_calories} ккал.\n"
        f"Дополнительно: выпейте {water_needed} мл воды."
        )
    
@router.message(Command("check_progress"))
async def check_progress(message: Message):
    if message.from_user.id not in users_ds:
        await message.answer(
            "Ошибка: Пользователь не занесен в базу данных.\n"
            "Внесите данные и повторите попытку"
        )
        return

    user_id = message.from_user.id

    water_goal = users_ds.get(user_id)["water_goal"]
    logged_water = users_ds.get(user_id)["logged_water"]
    if water_goal > logged_water:
        remaining_water = round(water_goal - logged_water)
    else:
        remaining_water = 0

    calorie_goal = users_ds.get(user_id)["calorie_goal"]
    logged_calories = round(users_ds.get(user_id)["logged_calories"])
    burned_calories = round(users_ds.get(user_id)["burned_calories"])
    calories_balance = round(logged_calories - burned_calories)

    await message.answer(
        "📊 Прогресс:\n"
        "Вода:\n"
        f"- Выпито: {logged_water} мл. из {water_goal}\n"
        f"- Осталось: {remaining_water} мл.\n"
        "\nКалории:\n"
        f"- Потреблено: {logged_calories} ккал. из {calorie_goal} ккал.\n"
        f"- Сожжено: {burned_calories} ккал.\n"
        f"- Баланс: {calories_balance} ккал."
    )

# Функция для подключения обработчиков
def setup_handlers(dp):
    dp.include_router(router)