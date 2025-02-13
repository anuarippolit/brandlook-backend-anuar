import requests
import logging
from utils.json_utils import save_to_json  # Функция для сохранения JSON

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

FG_CATEGORIES = [320, 322, 140, 156, 410]  # Категории товаров
PAGE_LIMIT = 2  # Ограничение количества страниц

BASE_URL = "https://api.frgroup.kz/v3/catalog"

def fetch_json(url):
    """Функция делает GET-запрос и возвращает JSON."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка запроса: {e}")
        return None

def parse_product(product):
    """Функция извлекает информацию о продукте."""
    product_name = product.get("title", "No Name")

    # Цвет
    color_data = product.get("specifications", {}).get("color", {})
    color = color_data.get("title", "Unknown Color")

    # Картинка
    image_data = product.get("catalogImages", {}).get("desktop", {}).get("mainImage", {})
    image_url = image_data.get("1x", "No Image")

    # Ссылка на продукт
    product_link = product.get("url", "No Link")

    # Доступные размеры
    sizes = [size.get("sizeValue", "Unknown") for size in product.get("skusList", [])]

    # Бренд
    brand_data = product.get("specifications", {}).get("brand", {})
    brand = brand_data.get("title", "Unknown Brand")

    # Цены
    sale_price = product.get("salePrice", 0)
    first_price = product.get("firstPrice", 0)

    # Категория
    category_data = product.get("specifications", {}).get("category", {}).get("path", "")
    category = list(set(category_data.split(" / "))) if category_data else ["Unknown Category"]

    return {
        "shop": "FG group",
        "name": product_name,
        "color": color,
        "image_url": image_url,
        "link": product_link,
        "sizes": sizes,
        "brand": brand,
        "sale price": sale_price,
        "first price": first_price,
        "category": category,
    }

def parse_fg_group():
    """Функция парсит сайт FG Group и возвращает список товаров."""
    parsed_products = []

    for category in FG_CATEGORIES:
        for page_number in range(1, PAGE_LIMIT + 1):
            url = f"{BASE_URL}?expand=pagination,products,products.specifications,products.skusList,products.otherColors,products.otherColors.catalogImages,products.catalogImages&attributeValueIds[]={category}&page={page_number}"

            data = fetch_json(url)
            if not data:
                logging.warning(f"Ошибка получения данных для категории {category}, страница {page_number}")
                continue

            products = data.get("products", [])
            if not products:
                logging.info(f"На странице {page_number} нет товаров для категории {category}")
                continue

            for product in products:
                parsed_products.append(parse_product(product))

    return parsed_products
