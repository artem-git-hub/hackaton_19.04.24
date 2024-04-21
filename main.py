from fastapi import FastAPI
import uvicorn

from api.routers.ratings import router as ratings_router
from api.routers.teams import router as teams_router


app = FastAPI()


if __name__ == "__main__":
    app.include_router(ratings_router)
    app.include_router(teams_router)
    uvicorn.run(app, host="0.0.0.0", port=8080)
