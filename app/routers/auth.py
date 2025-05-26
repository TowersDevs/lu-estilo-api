from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.connection import SessionLocal
from app.schemas.user import UserCreate, UserOut
from app.schemas.user import UserLogin
from app.schemas.token import Token
from app.services import auth
from app.core.security import create_access_token, create_refresh_token, decode_token

router = APIRouter(prefix="/auth", tags=["Auth"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    return auth.register_user(user, db)

@router.post("/login", response_model=Token)
def login(form: UserLogin, db: Session = Depends(get_db)):
    user = auth.authenticate_user(form.email, form.password, db)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    
    access_token = create_access_token({"sub": user.email})
    refresh_token = create_refresh_token({"sub": user.email})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }

@router.post("/refresh-token", response_model=Token)
def refresh_token(refresh_token: str):
    try:
        payload = decode_token(refresh_token)
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Token inválido")
    except:
        raise HTTPException(status_code=401, detail="Token inválido")
    
    return {
        "access_token": create_access_token({"sub": email}),
        "refresh_token": refresh_token
    }
