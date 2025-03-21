import requests
from bs4 import BeautifulSoup
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

BASE_URL = "https://superstep.kz/catalog/{category}-{sub_category}/?PAGEN_1={page}&bxajaxid=32ff20c93ce0fdbe79535b1238d9b6c9"
# CATEGORIES = ["zhenshchiny", "muzhchiny"]
# SUB_CATEGORIES = ["obuv", "odegda"]
CATEGORIES = ["muzhchiny"]
SUB_CATEGORIES = ["obuv"]
PAGE_LIMIT = 3

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def fetch_html(url):
    """Функция для получения HTML страницы"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")
        return None


def parse_product_card(card):
    """Парсим информацию о товаре из карточки на странице"""
    try:
        name_tag = card.select_one(".product-name a")
        name = name_tag.get_text(separator=" ", strip=True)
        link = "https://superstep.kz" + name_tag['href']

        brand = card.select_one("meta[itemprop='brand']")
        brand = brand["content"] if brand else "Unknown Brand"

        prices = card.select(".product-double-price span")
        first_price = prices[0].get_text(strip=True) if len(prices) > 0 else None
        sale_price = prices[1].get_text(strip=True) if len(prices) > 1 else None

        sizes = [a.get_text(strip=True) for a in card.select(".product-sizes a")]

        image_tag = card.select_one(".product-item-image_first")
        image_url = "https://superstep.kz" + image_tag['src'] if image_tag else "No image"

        return {
            "shop": "SuperStep",
            "name": name,
            "brand": brand,
            "link": link,
            "image_url": image_url,
            "first_price": first_price,
            "sale_price": sale_price,
            "sizes": sizes,
        }
    except Exception as e:
        logging.warning(f"Ошибка парсинга карточки: {e}")
        return None


def parse_product_details(product_url):
    """Сбор дополнительных данных с страницы товара"""
    html = fetch_html(product_url)
    if not html:
        return {}

    soup = BeautifulSoup(html, "html.parser")

    # Извлекаем категорию товара (только текст без <a> и <font>)
    category_tag = soup.select_one(".detail__info-wrapper .hidden")
    if category_tag:
        # Удаляем все теги <a> и <font>, оставляем только текст
        for unwanted_tag in category_tag.find_all(["a", "font"]):
            unwanted_tag.decompose()  # Удаляем тег
        category = category_tag.get_text(strip=True)  # Берем только текст
    else:
        category = "Не указана"

    # Извлекаем цвет товара
    color_tag = soup.select_one(".detail__info-wrapper .color")
    color = color_tag.get_text(strip=True) if color_tag else "Не указан"

    return {
        "category": category,
        "color": color,
    }


def parse_superstep():
    products = []

    for category in CATEGORIES:
        for sub_category in SUB_CATEGORIES:
            for page in range(1, PAGE_LIMIT + 1):
                url = BASE_URL.format(category=category, sub_category=sub_category, page=page)
                html = fetch_html(url)
                if not html:
                    continue

                soup = BeautifulSoup(html, "html.parser")
                cards = soup.select(".product-item-wrapper")
                logging.info(f"Найдено {len(cards)} карточек на {category}-{sub_category}, стр. {page}")

                for card in cards:
                    product = parse_product_card(card)
                    if product:
                        # Получаем дополнительные данные (категория и цвет) с каждой страницы товара
                        product_details = parse_product_details(product["link"])
                        product.update(product_details)  # Обновляем информацию о товаре
                        products.append(product)

    return products


# === ДЕБАГОВЫЙ ВЫЗОВ ===
if __name__ == "__main__":
    result = parse_superstep()
    for r in result[:5]:  # Печатаем первые 5 продуктов
        print(f"Продукт: {r}")
