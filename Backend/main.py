from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import auth

app = FastAPI()

# CORS para que el frontend pueda consumir el backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserRegister(BaseModel):
    name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

@app.post("/register")
def register(user: UserRegister):
    ok = auth.create_user(user.name, user.email, user.password)
    if not ok:
        raise HTTPException(status_code=400, detail="Email already registered")
    return {"message": "User created successfully"}

@app.post("/login")
def login(user: UserLogin):
    uid = auth.verify_user(user.email, user.password)
    if not uid:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Login successful", "user_id": uid}
