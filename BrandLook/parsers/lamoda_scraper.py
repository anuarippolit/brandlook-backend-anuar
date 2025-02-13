import requests
import logging
from utils.json_utils import save_to_json  # Функция для сохранения JSON

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

LAMODA_URLS = [
    {
        "base_url": "https://www.lamoda.kz/c/355/clothes-zhenskaya-odezhda/",
        "params": "?sitelink=topmenuW&l=2&page=",
        "json_param": "&json=1",
        "category": "Одежда",
    }
]

PAGE_LIMIT = 2  # Количество страниц для парсинга


def fetch_json(url):
    """Функция делает GET-запрос и возвращает JSON."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка запроса: {e}")
        return None


def parse_product(product, category):
    """Функция извлекает информацию о продукте."""
    parsed_products = []

    product_name = product.get("name", "No Name")
    brand = product.get("brand", {}).get("name", "Unknown Brand")
    sku = product.get("sku", "Unknown SKU")
    seo_tail = product.get("seo_tail", "")
    product_link = f"https://www.lamoda.kz/p/{sku}/{seo_tail}/"

    # Изображение
    image_url = product.get("gallery", [None])[0]
    image_url = f"https://a.lmcdn.ru/img600x866{image_url}" if image_url else "No Image"

    # Доступные размеры
    sizes = [size.get("size", "") for size in product.get("sizes", []) if size.get("is_available", False)]

    # Цены
    prices = product.get("prices", [])
    first_price = prices[0].get("price", 0) if prices else 0
    sale_price = prices[-1].get("price", 0) if prices else 0

    # Категории
    categories = [category, product_name.split(" ")[0]]

    # Цвета
    colors = product.get("colors", {})

    # Создаем запись для каждого цвета
    for color_name in colors.values():
        parsed_products.append({
            "shop": "Lamoda",
            "name": product_name,
            "color": color_name,
            "image_url": image_url,
            "link": product_link,
            "sizes": sizes,
            "brand": brand,
            "sale price": sale_price,
            "first price": first_price,
            "category": categories,
        })

    return parsed_products


def parse_lamoda():
    """Функция парсит сайт Lamoda и возвращает список товаров."""
    parsed_products = []

    for source in LAMODA_URLS:
        base_url = source["base_url"]
        params = source["params"]
        json_param = source["json_param"]
        category = source["category"]

        for page in range(1, PAGE_LIMIT + 1):
            url = f"{base_url}{params}{page}{json_param}"

            data = fetch_json(url)
            if not data:
                logging.warning(f"Не удалось получить данные с {url}")
                continue

            products = data.get("payload", {}).get("products", [])
            if not products:
                logging.info(f"На странице {page} нет товаров")
                continue

            for product in products:
                parsed_products.extend(parse_product(product, category))

    return parsed_products
