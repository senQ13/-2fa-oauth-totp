from app.api import users
from fastapi import FastAPI

app = FastAPI(title="Pet Projects API")
app.include_router(users.router)
