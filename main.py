from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import uvicorn

from api.routers.ratings import router as ratings_router
from api.routers.teams import router as teams_router


app = FastAPI()

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    app.include_router(ratings_router)
    app.include_router(teams_router)
    uvicorn.run(app, host="0.0.0.0", port=8080)
