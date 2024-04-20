
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

class Team(TeamBase):
    team_users: List[TeamUser] = []
    questions: List[Question] = []
    ratings: List[RatingBase] = []


    class Config:
        # Используем класс Exclude, чтобы удалить поля login и password из сериализации
        exclude = {"login", "password"}

class Answer(AnswerBase):
    id: int

class Rating(RatingBase):
    id: int

class RatingType(RatingTypeBase):
    id: int





class TeamUser(BaseModel):
    surname: str
    first_name: str
    patronymic: str
    image: str
    description: str

class TeamData(BaseModel):
    team_name: str
    email: str
    login: str
    password: str
    image: str
    team_users: List[TeamUser]