from fastapi import FastAPI, HTTPException
from pydantic_settings import BaseSettings
from pydantic import BaseModel
import bcrypt
from sqlmodel import Field, Session, SQLModel, create_engine, select
from biscuit_auth import BiscuitBuilder, PrivateKey

class Settings(BaseSettings):
    DB_IP: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    BISCUIT_PRIVATE_KEY: str
    BISCUIT_PUBLIC_KEY: str

class LoginCredentials(BaseModel):
    email: str
    password: str


settings = Settings()

class Users(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str
    surname: str
    email: str = Field(unique=True)
    password: str

app = FastAPI()

DATABASE_URL = f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_IP}:{settings.DB_PORT}/{settings.DB_NAME}"

engine = create_engine(DATABASE_URL)

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.post("/v1/auth")
async def auth(credentials: LoginCredentials):
    with Session(engine) as session:
        statement = select(Users).where(Users.email == credentials.email)
        user = session.exec(statement).first()
        if user is None:
            raise HTTPException(status_code=400)
        check = bcrypt.checkpw(password=credentials.password.encode(), hashed_password=user.password.encode())
        if not check:
            raise HTTPException(status_code=400)
        private_key = PrivateKey.from_hex(settings.BISCUIT_PRIVATE_KEY)
        builder = BiscuitBuilder("""
            user({user_id});
        """, {'user_id': user.id})
        builder.set_root_key_id(1)
        token = builder.build(private_key)
        token_string: str = token.to_base64()
        return {"token": token_string}