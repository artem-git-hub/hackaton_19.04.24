from urllib import response
from fastapi import FastAPI, Depends, HTTPException, Header
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
from pydantic_model import *
from pydantic_model import Team as TeamResponse, TeamUser as TeamUserResponse, Question as QuestionResponse, Answer as AnswerResponse, Rating as RatingResponse, RatingType as RatingTypeResponse, TeamBase

import uvicorn

from models import Base, Team, TeamUser, Question, Answer, Rating, RatingType
from funcs import *

from typing import List
from slugify import slugify

DATABASE_URL = "postgresql://hakaton:hakaton@hackaton_19042024_db_1:5432/hakaton"

engine = create_engine(DATABASE_URL)
Base.metadata.drop_all(bind=engine)
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



@app.get("/teams/{slug}", response_model=TeamCompleteData)
def read_team(slug: str, db: Session = Depends(get_db)):
    team = db.query(Team).filter(Team.slug == slug).first()
    if team is None:
        raise HTTPException(status_code=404, detail="Team not found")
    return TeamCompleteData.from_orm(team)



@app.post("/teams/{slug}")
def update_team(slug: str, team_update: TeamData, db: Session = Depends(get_db), token: str = Header(...)):


    # Поиск команды по слагу
    team = db.query(Team).filter(Team.slug == slug).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")


    # Проверка токена аутентификации
    if not check_valid_token(login=team.login, encode_password=team.password, token=token):
        raise HTTPException(status_code=401, detail="Invalid token")

    # Обновление данных команды
    if team_update.email is not None:
        team.email = team_update.email
    if team_update.team_name is not None:
        team.name = team_update.team_name
    if team_update.login is not None:
        team.login = team_update.login
    if team_update.image is not None:
        user_image_path = save_image_to_disk(team_update.image, team.name)
        team.icon_path = user_image_path  # Здесь должна быть логика сохранения изображения

    # Обновление данных участников команды
    for team_user_update in team_update.team_users:
        team_user = db.query(TeamUser).get(team_user_update.id)
        if not team_user:
            raise HTTPException(status_code=404, detail="Team user not found")
        if team_user_update.surname is not None:
            team_user.surname = team_user_update.surname
        if team_user_update.first_name is not None:
            team_user.first_name = team_user_update.first_name
        if team_user_update.patronymic is not None:
            team_user.patronymic = team_user_update.patronymic
        if team_user_update.description is not None:
            team_user.description = team_user_update.description
        if team_user_update.image is not None:
            user_image_path = save_image_to_disk(team_user_update.image, team.name)
            team_user.img_path = user_image_path  # Здесь должна быть логика сохранения изображения


        
        if team_user_update.job is not None:
            team_user.job = team_user_update.job
        if team_user_update.mark_participation is not None:
            team_user.mark_participation = team_user_update.mark_participation
        if team_user_update.difficulties is not None:
            team_user.difficulties = team_user_update.difficulties
        if team_user_update.portfolio_link is not None:
            team_user.portfolio_link = team_user_update.portfolio_link

    # Сохранение изменений в базе данных
    db.commit()

    return {"detail": "Team updated successfully"}




@app.post("/teams/", response_model=CreateCommandResponse)
def create_team(team_data: TeamData, db: Session = Depends(get_db)):
    # Сохраняем основное изображение команды
    team_image_path = save_image_to_disk(team_data.image, team_data.team_name)

    # Создаем новую команду
    team = Team(
        name=team_data.team_name,
        slug=slugify(team_data.team_name),
        email=team_data.email,
        login=team_data.login,
        password=encode_to_sha256(team_data.password),
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
            team_id=team.id,

            job=team_user_data.job,
            mark_participation=team_user_data.mark_participation,
            difficulties=team_user_data.difficulties,
            portfolio_link=team_user_data.portfolio_link
        )

        db.add(team_user)

    db.commit()

    TeamRegData = CreateCommandResponse

    TeamRegData.token = gen_login_token(team_data.login, team_data.password)

    return TeamRegData

@app.post("/teams/{slug}/users/", response_model=TeamUserResponseble)
def create_team_user(slug: str, team_user: TeamUserAdd, db: Session = Depends(get_db)):
    team = db.query(Team).filter(Team.slug == slug).first()
    if team is None:
        raise HTTPException(status_code=404, detail="Team not found")


    user_image_path = save_image_to_disk(team_user.image, team.name)

    new_user = TeamUser(
        surname = team_user.surname,
        first_name = team_user.first_name,
        patronymic = team_user.patronymic,
        img_path = user_image_path,
        description = team_user.description,
        team_id = team.id,

        job=team_user.job,
        mark_participation=team_user.mark_participation,
        difficulties=team_user.difficulties,
        portfolio_link=team_user.portfolio_link
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return TeamUserResponseble.from_orm(new_user)

@app.post("/login/", response_model=LoginResponse)
def create_answer(login: LoginRequest, db: Session = Depends(get_db)):
    team = db.query(Team).filter(Team.login == login.login).first()
    if team is None:
        raise HTTPException(status_code=404, detail="Team not found")
    
    current_token = gen_login_token(login=login.login, password=login.password)
    
    if check_valid_token(login=login.login, encode_password=team.password, token=current_token):
        response = LoginResponse
        response.token = current_token
        return response
    else:
        raise HTTPException(status_code=400, detail="Incorrect password")


if __name__ == "__main__":
    print("sdfsdfsdfsdf")
    uvicorn.run(app, host="0.0.0.0", port=8080)





# @app.post("/teams/{slug}/questions/", response_model=QuestionResponse)
# def create_question(slug: str, question: QuestionBase, db: Session = Depends(get_db)):
#     team = db.query(Team).filter(Team.slug == slug).first()
#     if team is None:
#         raise HTTPException(status_code=404, detail="Team not found")
#     question.team_slug = slug
#     db.add(question)
#     db.commit()
#     db.refresh(question)
#     return QuestionResponse.from_orm(question)

# @app.post("/teams/{slug}/questions/{question_id}/answers/", response_model=AnswerResponse)
# def create_answer(slug: str, question_id: int, answer: AnswerBase, db: Session = Depends(get_db)):
#     question = db.query(Question).filter(Question.id == question_id, Question.team_slug == slug).first()
#     if question is None:
#         raise HTTPException(status_code=404, detail="Question not found")
#     answer.question_id = question.id
#     db.add(answer)
#     db.commit()
#     db.refresh(answer)
#     return AnswerResponse.from_orm(answer)

