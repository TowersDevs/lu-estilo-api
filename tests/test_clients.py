import os
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.base import Base
from app.core.dependencies import get_db
from app.models.user import User
from app.core.security import create_access_token

# Remove o banco anterior para evitar conflitos
TEST_DB_FILE = "./test.db"
if os.path.exists(TEST_DB_FILE):
    os.remove(TEST_DB_FILE)

# Banco de dados de testes com SQLite
SQLALCHEMY_DATABASE_URL = f"sqlite:///{TEST_DB_FILE}"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Cria estrutura das tabelas ANTES da execução dos testes
Base.metadata.create_all(bind=engine)

# Substitui dependência do banco na app
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

# Criar token de teste para autenticar as requisições
def get_auth_header():
    db = TestingSessionLocal()

    # Verifica se o usuário já existe
    user = db.query(User).filter_by(email="testuser@example.com").first()

    if not user:
        user = User(
            name="Usuário Teste",
            email="testuser@example.com",
            hashed_password="123",
            role="admin"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    token = create_access_token({"sub": user.email})
    return {"Authorization": f"Bearer {token}"}

def test_create_client():
    headers = get_auth_header()
    unique_id = str(uuid.uuid4())[:8]
    payload = {
        "name": f"Cliente {unique_id}",
        "email": f"cliente{unique_id}@example.com",
        "cpf": f"12345678{unique_id[:3]}",
        "phone": "31999999999"
    }
    response = client.post("/clients/", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == payload["email"]
    assert data["cpf"] == payload["cpf"]

def test_list_clients():
    headers = get_auth_header()

    # Criar cliente único
    unique_id = str(uuid.uuid4())[:8]
    payload = {
        "name": f"Cliente {unique_id}",
        "email": f"cliente{unique_id}@example.com",
        "cpf": f"98765432{unique_id[:3]}",
        "phone": "31988888888"
    }

    # Criar cliente e garantir que foi salvo
    response_create = client.post("/clients/", json=payload, headers=headers)
    assert response_create.status_code == 200

    # Agora listar
    response = client.get(f"/clients?name={payload['name']}", headers=headers)
    assert response.status_code == 200
    data = response.json()

    print("📋 Clientes retornados:", data)  # Ajuda no debug
    assert len(data) == 1
    assert data[0]["email"] == payload["email"]


def test_duplicate_cpf():
    headers = get_auth_header()
    unique_id = str(uuid.uuid4())[:8]
    cpf = f"99999999{unique_id[:3]}"

    payload = {
        "name": f"Cliente 1 {unique_id}",
        "email": f"cliente1_{unique_id}@example.com",
        "cpf": cpf,
        "phone": "31999999999"
    }
    # Primeiro cliente – deve funcionar
    response1 = client.post("/clients/", json=payload, headers=headers)
    assert response1.status_code == 200

    # Segundo cliente – mesmo CPF, deve falhar
    payload["email"] = f"cliente2_{unique_id}@example.com"  # muda só o e-mail
    payload["name"] = f"Cliente 2 {unique_id}"

    response2 = client.post("/clients/", json=payload, headers=headers)
    assert response2.status_code == 400
    assert "cpf" in response2.json()["detail"].lower()

def test_update_client():
    headers = get_auth_header()

    # Criar cliente original
    unique_id = str(uuid.uuid4())[:8]
    payload = {
        "name": f"Cliente {unique_id}",
        "email": f"cliente{unique_id}@example.com",
        "cpf": f"12312312{unique_id[:3]}",
        "phone": "31999999999"
    }

    response_create = client.post("/clients/", json=payload, headers=headers)
    assert response_create.status_code == 200
    client_id = response_create.json()["id"]

    # Dados atualizados
    updated_payload = {
        "name": "Cliente Atualizado",
        "email": payload["email"],  # Email e CPF continuam iguais
        "cpf": payload["cpf"],
        "phone": "31911111111"
    }

    response_update = client.put(f"/clients/{client_id}", json=updated_payload, headers=headers)
    assert response_update.status_code == 200
    updated_data = response_update.json()

    assert updated_data["name"] == "Cliente Atualizado"
    assert updated_data["phone"] == "31911111111"

def test_delete_client():
    headers = get_auth_header()

    # Criar cliente para deletar
    unique_id = str(uuid.uuid4())[:8]
    payload = {
        "name": f"Cliente {unique_id}",
        "email": f"clientedel{unique_id}@example.com",
        "cpf": f"55555555{unique_id[:3]}",
        "phone": "31977777777"
    }

    response_create = client.post("/clients/", json=payload, headers=headers)
    assert response_create.status_code == 200
    client_id = response_create.json()["id"]

    # Deletar
    response_delete = client.delete(f"/clients/{client_id}", headers=headers)
    assert response_delete.status_code == 200

    # Verificar se cliente foi removido
    response_list = client.get("/clients/", headers=headers)
    assert response_list.status_code == 200
    data = response_list.json()

    assert all(c["id"] != client_id for c in data)