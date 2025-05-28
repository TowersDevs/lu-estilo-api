from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.client import Client
from app.schemas.client import ClientCreate

def create_client(db: Session, client_data: ClientCreate) -> Client:
    # Verificar se email já existe
    if db.query(Client).filter(Client.email == client_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado"
        )
    
    # Verificar se CPF já existe
    if db.query(Client).filter(Client.cpf == client_data.cpf).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CPF já cadastrado"
        )

    new_client = Client(**client_data.dict())
    db.add(new_client)
    db.commit()
    db.refresh(new_client)
    return new_client
