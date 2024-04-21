from dataclasses import dataclass
from environs import Env


@dataclass
class DbData:
    password: str = None
    user: str = None
    database: str = None
    container: str = None





@dataclass
class Config:
    db: DbData


def load_config(path: str = None):
    env = Env()
    env.read_env(path)

    config = Config(
        db=DbData(
            database=env.str("POSTGRES_DB"),
            user=env.str("POSTGRES_USER"),
            password=env.str("POSTGRES_PASSWORD"),
            container=env.str("POSTGRES_CONTAINER")
        ),
    )
    return config

config = load_config("./.env")