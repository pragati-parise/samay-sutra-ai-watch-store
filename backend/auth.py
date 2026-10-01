import os
from datetime import datetime, timedelta, timezone
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from .database import get_db
from .models import User
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer(auto_error=False); SECRET = os.getenv("JWT_SECRET_KEY", "change-this-in-production"); ALGORITHM = "HS256"
def hash_password(password): return pwd_context.hash(password)
def verify_password(password, hashed): return pwd_context.verify(password, hashed)
def create_token(user): return jwt.encode({"sub": str(user.id), "exp": datetime.now(timezone.utc) + timedelta(days=7)}, SECRET, algorithm=ALGORITHM)
def current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    if not credentials: raise HTTPException(401, "Please log in to continue.")
    try: user_id = int(jwt.decode(credentials.credentials, SECRET, algorithms=[ALGORITHM])["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError): raise HTTPException(401, "Invalid or expired token.")
    user = db.get(User, user_id)
    if not user: raise HTTPException(401, "User no longer exists.")
    return user
def admin_user(user: User = Depends(current_user)):
    if not user.is_admin: raise HTTPException(403, "Admin access is required.")
    return user
