from typing import Optional
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from pydantic import BaseModel
from technos.database import Base


class User(Base):
    __tablename__ = "user"

    email = Column(String(20), nullable=False)
    username = Column(String, primary_key=True, index=True)
    password = Column(String(20), nullable=False)
