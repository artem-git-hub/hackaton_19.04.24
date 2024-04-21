from fastapi import APIRouter, Depends, HTTPException, Header
from misc.encode_sha256 import encode_to_sha256
from misc.save_image import save_image_to_disk
from misc.token_actions import check_valid_token, gen_login_token, get_login_from_token
import psycopg2
import sqlalchemy
from sqlalchemy.orm import Session
from pydantic_models.models import *
from pydantic_models.models import Team as TeamResponse

from db.db import get_db
from db.models import Base, Team, TeamUser, Rating

from slugify import slugify

router = APIRouter()


@router.get("/teams/", response_model=TeamsResponseble)
def read_teams(db: Session = Depends(get_db), token: str = Header(None)):

    if token is not None:
        current_login = get_login_from_token(token=token)
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



@router.get("/teams/{slug}", response_model=TeamCompleteData)
def read_team(slug: str, db: Session = Depends(get_db)):
    team = db.query(Team).filter(Team.slug == slug).first()

    if team is None:
        raise HTTPException(status_code=404, detail="Команда не найдена")
    return TeamCompleteData.from_orm(team)


@router.post("/teams/{slug}")
def update_team(slug: str, team_update: TeamData, db: Session = Depends(get_db), token: str = Header(...)):


    # Поиск команды по слагу
    team = db.query(Team).filter(Team.slug == slug).first()
    if not team:
        raise HTTPException(status_code=404, detail="Команда не найдена")


    # Проверка токена аутентификации
    if not check_valid_token(login=team.login, encode_password=team.password, token=token):
        raise HTTPException(status_code=401, detail="Не правильный токен")

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
            raise HTTPException(status_code=404, detail="Пользователь не найден")
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

    return {"detail": "Команда успешно обновлена"}


@router.post("/teams/", response_model=LoginResponse)
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
    try:
        db.add(team)
        db.commit()
        db.refresh(team)
    except sqlalchemy.exc.IntegrityError as e:
        raise HTTPException(status_code=400, detail="Логин (или имя) уже существует")
    except Exception:
        raise HTTPException(status_code=400, detail="Ошибка в запросе")

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


@router.post("/teams/{slug}/users/", response_model=TeamUserResponseble)
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

@router.post("/login/", response_model=LoginResponse)
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
