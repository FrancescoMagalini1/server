from fastapi import FastAPI
from pydantic import BaseModel
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_IP: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str


settings = Settings()
app = FastAPI()


@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.get("/v1/auth")
async def auth():
    return settings.DB_IP