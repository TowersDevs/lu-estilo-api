from pydantic import BaseModel, EmailStr, constr

class ClientBase(BaseModel):
    name: str
    email: EmailStr
    cpf: constr(min_length=11, max_length=14)  # aceita CPF com ou sem pontuação
    phone: str | None = None

class ClientCreate(ClientBase):
    pass

class ClientUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None

class ClientOut(ClientBase):
    id: int

    class Config:
        from_attributes = True  # pydantic v2
