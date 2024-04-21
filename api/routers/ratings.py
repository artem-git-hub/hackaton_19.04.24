import statistics
from db.db import get_db
from fastapi import APIRouter, Depends, HTTPException, Header
from misc.token_actions import check_valid_token
from sqlalchemy.orm import Session
from pydantic_models.models import *

from db.models import Team, Rating, RatingType

router = APIRouter()



@router.get("/ratings/types/", response_model=None)
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



@router.post("/ratings/{slug}", response_model=None)
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


@router.get("/ratings/", response_model=None)
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
