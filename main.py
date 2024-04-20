from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
from pydantic_model import *
from pydantic_model import Team as TeamResponse, TeamUser as TeamUserResponse, Question as QuestionResponse, Answer as AnswerResponse, Rating as RatingResponse, RatingType as RatingTypeResponse, TeamBase


from models import Base, Team, TeamUser, Question, Answer, Rating, RatingType
from funcs import *

from typing import List
from slugify import slugify

DATABASE_URL = "postgresql://hakaton:hakaton@localhost:5433/hakaton"

engine = create_engine(DATABASE_URL)
# Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/teams/", response_model=List[TeamResponse])
def read_teams(db: Session = Depends(get_db)):
    teams = db.query(Team).all()
    return [TeamResponse.from_orm(team) for team in teams]

@app.get("/teams/{slug}", response_model=TeamResponse)
def read_team(slug: str, db: Session = Depends(get_db)):
    team = db.query(Team).filter(Team.slug == slug).first()
    if team is None:
        raise HTTPException(status_code=404, detail="Team not found")
    return TeamResponse.from_orm(team)

@app.post("/teams/", response_model=TeamResponse)
def create_team(team_data: TeamData, db: Session = Depends(get_db)):
    # Сохраняем основное изображение команды
    team_image_path = save_image_to_disk(team_data.image, team_data.team_name)

    # Создаем новую команду
    team = Team(
        name=team_data.team_name,
        slug=slugify(team_data.team_name),
        email=team_data.email,
        login=team_data.login,
        password=team_data.password,
        icon_path=team_image_path
    )

    # Сохраняем команду в базе данных
    db.add(team)
    db.commit()
    db.refresh(team)

    # Сохраняем изображения для участников команды
    for team_user_data in team_data.team_users:
        user_image_path = save_image_to_disk(team_user_data.image, team_data.team_name)

        team_user = TeamUser(
            surname=team_user_data.surname,
            first_name=team_user_data.first_name,
            patronymic=team_user_data.patronymic,
            img_path=user_image_path,
            description=team_user_data.description,
            team_id=team.id
        )

        db.add(team_user)

    db.commit()

    return TeamResponse.from_orm(team)

@app.post("/teams/{slug}/users/", response_model=TeamUserResponse)
def create_team_user(slug: str, team_user: TeamUserBase, db: Session = Depends(get_db)):
    team = db.query(Team).filter(Team.slug == slug).first()
    if team is None:
        raise HTTPException(status_code=404, detail="Team not found")
    team_user.team_id = team.id
    db.add(team_user)
    db.commit()
    db.refresh(team_user)
    return TeamUserResponse.from_orm(team_user)

@app.post("/teams/{slug}/questions/", response_model=QuestionResponse)
def create_question(slug: str, question: QuestionBase, db: Session = Depends(get_db)):
    team = db.query(Team).filter(Team.slug == slug).first()
    if team is None:
        raise HTTPException(status_code=404, detail="Team not found")
    question.team_slug = slug
    db.add(question)
    db.commit()
    db.refresh(question)
    return QuestionResponse.from_orm(question)

@app.post("/teams/{slug}/questions/{question_id}/answers/", response_model=AnswerResponse)
def create_answer(slug: str, question_id: int, answer: AnswerBase, db: Session = Depends(get_db)):
    question = db.query(Question).filter(Question.id == question_id, Question.team_slug == slug).first()
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    answer.question_id = question.id
    db.add(answer)
    db.commit()
    db.refresh(answer)
    return AnswerResponse.from_orm(answer)



@app.post("/login/", response_model=AnswerResponse)
def create_answer(slug: str, question_id: int, answer: AnswerBase, db: Session = Depends(get_db)):
    question = db.query(Question).filter(Question.id == question_id, Question.team_slug == slug).first()
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    answer.question_id = question.id
    db.add(answer)
    db.commit()
    db.refresh(answer)
    return AnswerResponse.from_orm(answer)