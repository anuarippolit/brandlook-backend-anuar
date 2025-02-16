from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional
import logging
from sqlalchemy import text
from api.database import SessionLocal, Product

app = FastAPI()

# ✅ FIX: Add CORS to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow frontend to access API
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Clothing Search API"}

@app.get("/products")
def get_products(db: Session = Depends(get_db)):
    """
    Get all products.
    """
    products = db.query(Product).all()
    return {"results": products}

@app.get("/search")
def search_product(name: str, db: Session = Depends(get_db)):
    """
    Search for a product by matching words in `name` and `shop`.
    Example: "Adidas Handball" should match "Кроссовки Handball Spezial".
    """
    search_terms = name.lower().split()  # Split input into words
    products = db.query(Product).all()  # Get all products

    # Check if each word is in `name` or `shop`
    filtered_products = [
        product for product in products
        if all(
            term in product.name.lower() or term in product.shop.lower()
            for term in search_terms
        )
    ]

    return {"results": filtered_products}

@app.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    """
    Get a list of all unique categories.
    """
    categories = {cat for product in db.query(Product).all() for cat in product.category}
    return {"categories": list(categories)}

@app.get("/products/filter")
def filter_products(
    size: Optional[str] = None,
    price_min: Optional[float] = None,
    price_max: Optional[float] = None,
    brand: Optional[str] = None,
    color: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    Filter products by size, price range, brand, color, and category.
    """
    logging.info(f"Filters: size={size}, price_min={price_min}, price_max={price_max}, brand={brand}, color={color}, category={category}")

    query = db.query(Product)

    # ✅ Fix: Correct filtering for `size`
    if size:
        query = query.filter(
            text(":size IN (SELECT value FROM json_each(products.sizes))")
        ).params(size=size)

    # ✅ Fix: Correct filtering for `category`
    if category:
        query = query.filter(
            text(":category IN (SELECT value FROM json_each(products.category))")
        ).params(category=category)

    # Filter by minimum price
    if price_min:
        query = query.filter(Product.sale_price >= price_min)

    # Filter by maximum price
    if price_max:
        query = query.filter(Product.sale_price <= price_max)

    # Filter by brand (case-insensitive)
    if brand:
        query = query.filter(Product.brand.ilike(f"%{brand}%"))

    # Filter by color (case-insensitive)
    if color:
        query = query.filter(Product.color.ilike(f"%{color}%"))

    try:
        results = query.all()
        logging.info(f"Results: {results}")
        return {"results": results}
    except Exception as e:
        logging.error(f"Error during filtering: {e}")
        return {"error": str(e)}
    
@app.get("/products/{product_id}")
def get_product_by_id(product_id: int, db: Session = Depends(get_db)):
    """
    Fetch a single product by ID.
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        return {"error": "Product not found"}, 404  # Return 404 if product not found

    return product  # Return the product data
