import asyncio
import logging
from parsers.adidas_scraper import parse_adidas
from parsers.lamoda_scraper import parse_lamoda
from parsers.fg_group_scraper import parse_fg_group
from utils.json_utils import save_to_json, save_to_db

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

async def run_scrapers():
    logging.info("🔄 Запуск парсеров...")

    tasks = [
        asyncio.to_thread(parse_adidas),
        asyncio.to_thread(parse_lamoda),
        asyncio.to_thread(parse_fg_group),
    ]

    results = await asyncio.gather(*tasks)

    # Объединяем данные
    all_data = []
    for data in results:
        if data:
            all_data.extend(data)

    if all_data:
        save_to_json(all_data)
        logging.info("✅ Данные успешно сохранены в JSON.")
        save_to_db(all_data)
        logging.info("✅ Данные успешно сохранены в SQLite БД.")
    else:
        logging.warning("⚠ Парсеры не собрали данные!")

if __name__ == "__main__":
    asyncio.run(run_scrapers())
