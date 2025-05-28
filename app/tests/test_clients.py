import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.base import Base
from app.core.dependencies import get_db
from app.models.user import User
from app.core.security import create_access_token

# Banco de dados temporário para testes
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Criar estrutura do banco
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

# Substituir dependência do banco
app.dependency_overrides[get_db] = lambda: TestingSessionLocal()

client = TestClient(app)

# Criar token de teste para autenticar as requisições
def get_auth_header():
    db = TestingSessionLocal()
    user = User(email="testuser@example.com", hashed_password="123", role="admin")
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(user.email)
    return {"Authorization": f"Bearer {token}"}

def test_create_client():
    headers = get_auth_header()
    payload = {
        "name": "Cliente Teste",
        "email": "cliente@example.com",
        "cpf": "12345678900",
        "phone": "31999999999"
    }
    response = client.post("/clients/", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "cliente@example.com"
    assert data["cpf"] == "12345678900"
