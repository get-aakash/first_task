from typing import Optional
from sqlalchemy.orm import Session
from technos.database import SessionLocal, engine
from fastapi import FastAPI, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.security.oauth2 import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import technos.models as _models
import technos.schemas as _schemas
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
import technos.crud as _crud

app = FastAPI()

SECRET_KEY = "ae532ea5a66ef6d50d6458d9d72f115c5dfe59b1e6e0c58cdb0724d27b67ed33"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

_models.Base.metadata.create_all(bind=engine)


def get_user():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@app.post("/token", response_model=_schemas.Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_user)
):
    user_value = _crud.get_user(db, form_data.username)
    username = user_value.username
    password = user_value.password
    verify_password = _crud.check_password(form_data.password, password)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username is incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not verify_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="password is incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"user": username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_user)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("user")
        if username is None:
            raise credentials_exception
        token_data = _schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    current_user = _crud.pass_user(db, username=token_data.username)
    print(current_user)
    if current_user is None:
        raise credentials_exception
    return current_user


@app.get("/get_user/", response_model=_schemas.User)
def view_user_profile(current_user: _schemas.User = Depends(get_current_user)):
    return current_user


@app.post("/create_newuser/", response_model=_schemas.UserBase)
def create_newuser(user: _schemas.UserCreate, db: Session = Depends(get_user)):
    return _crud.create_user(db, user)
