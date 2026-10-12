
from datetime import date

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class BookCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=200)
    isbn: str = Field(min_length=1, max_length=20)
    published_year: int | None = Field(default=None, ge=1000, le=2100)


class BookUpdate(BookCreate):
    pass


class MemberCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class MemberLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class StaffLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class LoanCreate(BaseModel):
    member_id: int = Field(gt=0)
    copy_id: int = Field(gt=0)


class LoanReturn(BaseModel):
    returned_at: date | None = None

    @field_validator("returned_at")
    @classmethod
    def validate_returned_at(cls, value: date | None):
        if value is not None and value > date.today():
            raise ValueError("Return date cannot be in the future.")
        return value


class AuthorCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=150)


class CopyCreate(BaseModel):
    book_id: int = Field(gt=0)
    branch_id: int = Field(gt=0)

