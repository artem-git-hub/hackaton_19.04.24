import statistics
from os import name
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

from config import config

DATABASE_URL = f"postgresql://{config.db.user}:{config.db.password}@{config.db.container}:5432/{config.db.database}"

engine = create_engine(DATABASE_URL)
# Base.metadata.drop_all(bind=engine, checkfirst=True)
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

@app.get("/teams/", response_model=TeamsResponseble)
def read_teams(db: Session = Depends(get_db), token: str = Header(None)):

    if token is not None:
        current_login = get_login_from_roken(token=token)
    else:
        current_login = None
    current_team = db.query(Team).filter(Team.login == current_login).first()

    teams = db.query(Team).all()

    response = TeamsResponseble(teams=[], ranked_teams=[])

    for team in teams:
        if current_team is not None:
            rating = db.query(Rating).filter(Rating.command_slug_from == current_team.slug, Rating.command_slug_to == team.slug).first()
        else:
            rating = None
        if rating is not None:
            response.ranked_teams.append(team.slug)
        response.teams.append(TeamResponse.from_orm(team))

    return response



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


@app.post("/teams/", response_model=LoginResponse)
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

    TeamRegData = LoginResponse(token=gen_login_token(team_data.login, team_data.password), slug=team.slug)


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
        response.slug = team.slug
        return response
    else:
        raise HTTPException(status_code=400, detail="Incorrect password")









@app.get("/ratings/types/", response_model=None)
def get_rating_types():
    rating_types = [
        {
            "slug":"design", "name": "Дизайн"
        },{
            "slug": "usability", "name": "Юзабилити"
        },{
            "slug": "layout", "name": "Верстка"
        },{
            "slug": "implementation", "name": "Реализация"
        }
    ]
    return rating_types









@app.post("/ratings/{slug}", response_model=None)
def add_ratings(slug: str, rating: TeamRatings, db: Session = Depends(get_db), token: str = Header(...)):

    team = db.query(Team).filter(Team.slug == rating.command_slug).first()

    # Проверка токена аутентификации
    if not check_valid_token(login=team.login, encode_password=team.password, token=token):
        raise HTTPException(status_code=401, detail="Invalid token")
    
    if team.slug == slug:
        raise HTTPException(status_code=400, detail="Incorrect command slug")


    db_rating = Rating(command_slug_to=slug, command_slug_from=rating.command_slug)
    db.add(db_rating)

    db.commit()

    db.refresh(db_rating)  

    for rating_slug in rating.ratings.keys():
        new_rating = RatingType(mark=rating.ratings[rating_slug], rating_id=db_rating.id, slug=rating_slug)
        db.add(new_rating)
    db.commit()
    return {"detail": "Ratings added successfully"}





@app.get("/ratings/", response_model=None)
def get_rating_types(db: Session = Depends(get_db)):

    list_teams = []

    teams = db.query(Team).all()

    for team in teams:
        ratings = db.query(Rating).filter(Rating.command_slug_to == team.slug).all()

        design_marks = []
        usability_marks = []
        layout_marks = []
        implementation_marks = []

        for rating in ratings:
            rating_types = db.query(RatingType).filter(RatingType.rating_id == rating.id).all()

            for rating_type in rating_types:
                if rating_type.slug == "design":
                    design_marks.append(rating_type.mark)
                if rating_type.slug == "usability":
                    usability_marks.append(rating_type.mark)
                if rating_type.slug == "layout":
                    layout_marks.append(rating_type.mark)
                if rating_type.slug == "implementation":
                    implementation_marks.append(rating_type.mark)

        all_marks = design_marks + usability_marks + layout_marks + implementation_marks

        list_teams.append(
            {
                "command_slug": team.slug,
                "ratings": {
                    "design": round(statistics.mean(design_marks), 1) if design_marks else "-",
                    "usability": round(statistics.mean(usability_marks), 1) if usability_marks else "-",
                    "layout": round(statistics.mean(layout_marks), 1) if layout_marks else "-",
                    "implementation": round(statistics.mean(implementation_marks), 1) if implementation_marks else "-",
                },
                "mean_mark" : round(statistics.mean(all_marks), 1) if all_marks else "-",
                "sum_marks": sum(all_marks) if all_marks else 0
            }
        )

    sorted_list_teams = sorted(list_teams, key=lambda x: x["sum_marks"], reverse=True)


    return sorted_list_teams







if __name__ == "__main__":
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




