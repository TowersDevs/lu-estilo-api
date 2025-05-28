from passlib.context import CryptContext
from datetime import datetime, timedelta
import base64
import jwt
from jwt import decode as jwt_decode, exceptions as jwt_exceptions
import os

# HASH
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# JWT
SECRET_KEY = "secret-jwt-key"  # ideal: usar variável de ambiente
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    print("PAYLOAD no access_token:", to_encode)
    print("TOKEN FINAL:", jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM))
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    try:
        print("🔹 Token recebido:", token)
        decoded = jwt_decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print("✅ DECODED payload:", decoded)
        return decoded
    except jwt_exceptions.InvalidTokenError as e:
        print("❌ JWT decode error:", e)
        raise