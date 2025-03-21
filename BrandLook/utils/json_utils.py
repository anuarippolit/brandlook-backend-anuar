import json
import os
from sqlalchemy.orm import Session
from api.database import SessionLocal, Product

def save_to_json(data, filename='data/scraped_data.json'):
    """
    Сохраняет данные в JSON. Если файл существует, добавляет в него данные.
    """
    # Convert the relative path to an absolute path
    base_dir = os.path.dirname(os.path.abspath(__file__))  # Gets `BrandLook/utils/`
    file_path = os.path.join(base_dir, filename)

    # Ensure the `data/` folder exists before writing
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    try:
        # Проверяем, существует ли файл и содержит ли он данные
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            with open(file_path, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)  # Загружаем существующие данные
        else:
            existing_data = []  # Если файла нет или он пуст, создаём новый список
    except (json.JSONDecodeError, FileNotFoundError):
        existing_data = []  # Если файл повреждён или отсутствует, создаём пустой список

    # Добавляем новые данные в существующий JSON
    existing_data.extend(data)

    # Сохраняем обновлённые данные обратно в файл
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, indent=4, ensure_ascii=False)

    print(f"✅ Data successfully saved to {file_path}")



def load_from_json(filename='data/scraped_data.json'):
    """
    Загружает данные из JSON-файла.
    """
    if os.path.exists(filename) and os.path.getsize(filename) > 0:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []  # Если файла нет или он пуст, возвращаем пустой список

def save_to_db(data):
    """
    Сохраняет список товаров в базу данных SQLite.
    """
    db: Session = SessionLocal()
    try:
        for item in data:
            product = Product(
                shop=item.get("shop", "Unknown"),
                name=item.get("name", "No Name"),
                color=item.get("color", "Unknown Color"),
                image_url=item.get("image_url", ""),
                link=item.get("link", ""),
                sizes=item.get("sizes", []),
                brand=item.get("brand", "Unknown Brand"),
                sale_price=item.get("sale_price", 0),
                first_price=item.get("first_price", 0),
                category=item.get("category", []),
            )
            db.add(product)
        db.commit()
    finally:
        db.close()
