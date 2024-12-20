from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, EmailStr


class ContactBase(BaseModel):
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    email: str = Field(max_length=150)
    phone: str = Field(max_length=50)
    birthday: Optional[date]
    additional_info: Optional[str] = Field(max_length=250)


class ContactUpdate(BaseModel):
    first_name: Optional[str] = Field(max_length=50)
    last_name: Optional[str] = Field(max_length=50)
    email: Optional[EmailStr] = Field(max_length=150)
    phone: Optional[str] = Field(max_length=50)
    birthday: Optional[date]
    additional_info: Optional[str] = Field(max_length=250)


class ContactResponse(ContactBase):
    id: int
    created_at: datetime | None
    updated_at: Optional[datetime] | None

    model_config = ConfigDict(from_attributes=True)
