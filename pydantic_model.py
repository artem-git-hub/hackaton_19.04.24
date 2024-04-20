
from fastapi import UploadFile, HTTPException

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class TeamBase(BaseModel):
    name: str
    slug: str
    email: str
    icon_path: str

    class Config:
        from_attributes=True
        orm_mode = True

class TeamUserBase(BaseModel):
    surname: str
    first_name: str
    patronymic: str
    img_path: str
    description: str
    team_id: int


    job: Optional[str]
    mark_participation: Optional[int]
    difficulties: Optional[str]
    portfolio_link: Optional[str]

    class Config:
        from_attributes=True
        orm_mode = True

class QuestionBase(BaseModel):
    fio: str
    email: str
    text: str
    created_at: datetime
    updated_at: Optional[datetime]
    deleted_at: Optional[datetime]
    team_slug: str

    class Config:
        from_attributes=True
        orm_mode = True

class AnswerBase(BaseModel):
    question_id: int
    text: str
    created_at: datetime
    updated_at: Optional[datetime]
    deleted_at: Optional[datetime]

    class Config:
        from_attributes=True
        orm_mode = True

class RatingBase(BaseModel):
    team_id: int
    rating_type_id: int
    mark: int

    class Config:
        from_attributes=True
        orm_mode = True

class RatingTypeBase(BaseModel):
    name: str
    slug: str
    ord: int

    class Config:
        from_attributes=True
        orm_mode = True

# Модели для ответов на GET запросы
class TeamUser(TeamUserBase):
    id: int

class Question(QuestionBase):
    id: int
    answers: List[AnswerBase] = []



class Team(BaseModel):
    slug: str
    icon_path: str

    class Config:
        from_attributes=True
        orm_mode = True



class TeamCompleteData(BaseModel):
    name: str
    slug: str
    email: str
    icon_path: str


    team_users: List[TeamUser] = []
    questions: List[Question] = []
    ratings: List[RatingBase] = []

    class Config:
        from_attributes=True
        orm_mode = True




class Answer(AnswerBase):
    id: int

class Rating(RatingBase):
    id: int

class RatingType(RatingTypeBase):
    id: int





class TeamUser(BaseModel):
    id: int = None
    surname: str =  None
    first_name: str =  None
    patronymic: str =  None
    image: str =  None
    description: str =  None
    job: Optional[str] =  None
    mark_participation: Optional[int] =  None
    difficulties: Optional[str] =  None
    portfolio_link: Optional[str] =  None
    class Config:
        from_attributes=True

class TeamData(BaseModel):
    team_name: Optional[str] =  None
    email: Optional[str] =  None
    login: Optional[str] =  None
    password: Optional[str] =  None
    image: Optional[str] =  None
    team_users: Optional[List[TeamUser]] =  None




class LoginRequest(BaseModel):
    login: str
    password: str

class LoginResponse(BaseModel):
    token: str



class CreateCommandResponse(BaseModel):
    token: str



class TeamUserAdd(BaseModel):
    surname: str
    first_name: str
    patronymic: str
    image: str
    description: str

    job: Optional[str] =  None
    mark_participation: Optional[int] =  None
    difficulties: Optional[str] =  None
    portfolio_link: Optional[str] =  None




class TeamUserResponseble(BaseModel):
    id: int = None
    surname: str =  None
    first_name: str =  None
    patronymic: str =  None
    img_path: str =  None
    description: str =  None
    job: Optional[str] =  None
    mark_participation: Optional[int] =  None
    difficulties: Optional[str] =  None
    portfolio_link: Optional[str] =  None
    class Config:
        from_attributes=True