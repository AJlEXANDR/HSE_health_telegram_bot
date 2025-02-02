import aiohttp
from googletrans import Translator

async def get_current_temperature(city, weather_api_key):
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': city,
        'appid': weather_api_key,
        'units': 'metric'
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url=base_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data['main']['temp']
                else:
                    print(f"Ошибка HTTP: {response.status}")
                    return None
        except aiohttp.ClientError as e:
            print(f"Ошибка HTTP при получении информации о погоде: {e}")
            return None
        except Exception as err:
            print(f"Произошла ошибка: {err}")
            return None

async def translate_rus_to_eng(rus_text: str) -> str:
     async with Translator() as translator:
         translation_result = await translator.translate(rus_text, src='ru', dest='en')
         return translation_result.text

async def get_food_data(product_name, app_id, nutrionix_api_key):
    base_url = "https://trackapi.nutritionix.com/v2/natural/nutrients"
    headers = {
        "x-app-id": app_id,
        "x-app-key": nutrionix_api_key,
        "Content-Type": "application/json",
    }
    query = f"100 grams of {product_name}"
    data = {"query": query}
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url=base_url, headers=headers, json=data) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"Ошибка HTTP: {response.status}")
                    return None
        except aiohttp.ClientError as e:
            print(f"Ошибка HTTP при получении информации о еде: {e}")
            return None
        except Exception as err:
            print(f"Произошла ошибка: {err}")
            return None
        
async def get_workout_data(duration, workout_type, app_id, nutrionix_api_key):
    base_url = "https://trackapi.nutritionix.com/v2/natural/exercise"
    headers = {
        "x-app-id": app_id,
        "x-app-key": nutrionix_api_key,
        "Content-Type": "application/json",
    }
    query = f"{duration} min {workout_type}"
    data = {"query": query}
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url=base_url, headers=headers, json=data) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"Ошибка HTTP: {response.status}")
                    return None
        except aiohttp.ClientError as e:
            print(f"Ошибка HTTP при получении информации о еде: {e}")
            return None
        except Exception as err:
            print(f"Произошла ошибка: {err}")
            return None