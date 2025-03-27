from sqlalchemy import create_engine, Column, Integer, String, Float, JSON
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# Подключение к базе данных SQLite
DATABASE_URL = "sqlite:///data/products.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()  # <-- ЭТО ВАЖНО! Без этого `Base` не будет работать.

# Определяем модель данных для хранения товаров
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    shop = Column(String, index=True)
    name = Column(String, index=True)
    color = Column(String)
    image_url = Column(String)
    link = Column(String)
    sizes = Column(JSON)
    brand = Column(String, index=True)
    sale_price = Column(Float)
    first_price = Column(Float)
    category = Column(JSON)

# Создаем таблицы в БД (если они еще не созданы)
Base.metadata.create_all(bind=engine)

# import os
# from sqlalchemy import create_engine, Column, Integer, String, Float, JSON
# from sqlalchemy.orm import declarative_base, sessionmaker

# # Get the correct absolute path for the database file
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # This gets the `api/` directory
# DB_PATH = os.path.join(BASE_DIR, "data", "products.db")

# # Ensure the `data/` directory exists
# os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# DATABASE_URL = f"sqlite:///{DB_PATH}"

# engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()  # <-- This is required for table definitions.

# # Define the product model
# class Product(Base):
#     __tablename__ = "products"

#     id = Column(Integer, primary_key=True, index=True)
#     shop = Column(String, index=True)
#     name = Column(String, index=True)
#     color = Column(String)
#     image_url = Column(String)
#     link = Column(String)
#     sizes = Column(JSON)
#     brand = Column(String, index=True)
#     sale_price = Column(Float)
#     first_price = Column(Float)
#     category = Column(JSON)

# # Create the database tables (if they don't exist)
# Base.metadata.create_all(bind=engine)

