from sqlalchemy import create_engine, Column, Integer, String, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///data/products.db"  # Используем SQLite

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

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

# Создаем таблицы в БД
Base.metadata.create_all(bind=engine)
