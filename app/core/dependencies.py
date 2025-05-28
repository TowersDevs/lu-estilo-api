from fastapi import Depends, HTTPException, status
from app.core.auth_scheme import OAuth2PasswordBearerWithCookie
from jwt import PyJWTError as JWTError
from sqlalchemy.orm import Session
from app.db.connection import SessionLocal
from app.models.user import User
from app.core.security import decode_token

oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/auth/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não autenticado",
        headers={"WWW-Authenticate": "Bearer"},
    )

    print("TOKEN:", token)

    if not token:
        print("❌ TOKEN ausente")
        raise credentials_exception

    try:
        pure_token = token.replace("Bearer ", "").strip()
        payload = decode_token(pure_token)
        print("✅ DECODE:", payload)
        if not token.startswith("Bearer "):
            print("❌ Token fora do formato esperado")
            raise credentials_exception
        email: str = payload.get("sub")
        if email is None:
            print("❌ EMAIL ausente no payload")
            raise credentials_exception
    except JWTError as e:
        print("❌ JWTError:", e)
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    print("🔎 USER:", user)

    if user is None:
        print("❌ Usuário não encontrado")
        raise credentials_exception

    print("✅ Usuário autenticado:", user.email)
    return user