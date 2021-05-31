from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi.encoders import jsonable_encoder

from technos import models, schemas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    return pwd_context.hash(password)


def check_password(password, hash_password) -> str:
    return pwd_context.verify(password, hash_password)


def get_user(db: Session, username):
    return db.query(models.User).filter(models.User.username == username).first()


def create_user(db: Session, create: schemas.UserCreate):
    hashed_password = get_password_hash(create.password)
    db_user = models.User(
        username=create.username,
        email=create.email,
        password=hashed_password,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def pass_user(db: Session, username):
    user_value = db.query(models.User).filter(models.User.username == username).first()
    user_dict = jsonable_encoder(user_value)
    current_user = schemas.User(**user_dict)
    return current_user
