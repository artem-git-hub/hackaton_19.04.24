from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Team(Base):
    __tablename__ = 'teams'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    slug = Column(String, unique=True)
    email = Column(String)
    login = Column(String, unique=True)
    password = Column(String)
    icon_path = Column(String)
    team_users = relationship('TeamUser', backref='team')
    questions = relationship('Question', backref='team')
    ratings = relationship('Rating', backref='team')

class TeamUser(Base):
    __tablename__ = 'team_users'
    id = Column(Integer, primary_key=True)
    surname = Column(String)
    first_name = Column(String)
    patronymic = Column(String)
    img_path = Column(String)
    description = Column(String)

    job = Column(String)
    mark_participation = Column(Integer)
    difficulties = Column(String)
    portfolio_link = Column(String)

    team_id = Column(Integer, ForeignKey('teams.id'))

class Question(Base):
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True)
    fio = Column(String)
    email = Column(String)
    text = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    deleted_at = Column(DateTime)
    team_slug = Column(String, ForeignKey('teams.slug'))
    answers = relationship('Answer', backref='question')

class Answer(Base):
    __tablename__ = 'answers'
    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey('questions.id'))
    text = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    deleted_at = Column(DateTime)

class RatingType(Base):
    __tablename__ = 'rating_types'
    id = Column(Integer, primary_key=True)
    rating_id = Column(Integer, ForeignKey('ratings.id'))
    mark = Column(Integer)
    slug = Column(String)

class Rating(Base):
    __tablename__ = 'ratings'
    id = Column(Integer, primary_key=True)
    command_slug_from = Column(String)
    command_slug_to = Column(String, ForeignKey('teams.slug'))
    rating_types = relationship('RatingType', backref='rating')


