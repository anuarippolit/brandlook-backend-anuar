from fastapi.testclient import TestClient
from api.routes import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Clothing Search API"}

def test_search():
    response = client.get("/search?name=Кроссовки")
    assert response.status_code == 200
    assert "results" in response.json()
