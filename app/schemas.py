""" Unnesessary module """
from typing import Optional
from sqlmodel import SQLModel, Field
from pydantic import EmailStr, BaseModel


class UserWithOutId(SQLModel):
    """User model without id - base model"""
    countryCode: Optional[str]
    dateOfBirth: Optional[str]
    firstname: Optional[str]
    nickname: Optional[str] = Field(index=True)
    gender: Optional[str]
    email: Optional[EmailStr] = Field(index=True)


class User(UserWithOutId, table=True):
    """User model with id - table"""
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}
    id: int = Field(default=None, primary_key=True)


class UserEvent(BaseModel):
    action_type: str
    user_dict: dict
