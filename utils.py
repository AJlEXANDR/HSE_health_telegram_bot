import aiohttp
from googletrans import Translator

async def translate_rus_to_eng(rus_text: str) -> str:
     async with Translator() as translator:
         translation_result = await translator.translate(rus_text, src='ru', dest='en')
         return translation_result.text
     
async def get_workout(activity: str, duration: int, api_key: str) -> int:
    base_url = 'https://api.api-ninjas.com/v1/caloriesburned?'
    params = {
        'activity': activity,
        'duration': duration
    }
    headers = {
        'X-Api-Key': api_key
    }
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url=base_url, headers=headers, params=params) as response:
                data = await response.json()
                burned_calories = data[0].get('total_calories', 0) if data else 0
        except aiohttp.ClientError as e:
            print(f'HTTP Request failed: {e}')
            return None

    return burned_calories

async def get_food_info(product_name: str) -> dict:
    base_url = "https://world.openfoodfacts.org/cgi/search.pl?"
    params = {
        'action': 'process',
        'search_terms': product_name,
        'json': 'true'
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url=base_url, params=params) as response:
                data = await response.json()
                products = data.get('products', [])
                
                if products:
                    first_product = products[0]
                    return {
                        'name': first_product.get('product_name', 'Неизвестно'),
                        'calories': first_product.get('nutriments', {}).get('energy-kcal_100g', 0)
                    }
                else:
                    raise ValueError('Информация о продукте отсутствует. Введите корректную информацию')
            
        except aiohttp.ClientError as e:
            print(f'HTTP Request failed: {e}')
            return None