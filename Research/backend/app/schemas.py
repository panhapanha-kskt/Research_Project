from pydantic import BaseModel, Field, EmailStr


class UserCreate(BaseModel):
	name: str = Field(..., min_length=2, max_length=100)	
	email: EmailStr
	age: int = Field(..., ge=0, le=130)


class UserOut(BaseModel):
	id: int
	name: str
	email: EmailStr
	age: int


	class Config:
		orm_mode = True
