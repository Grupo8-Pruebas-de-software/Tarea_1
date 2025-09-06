from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import auth
import eventos
import entradas
from typing import List
from datetime import date

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

# Modelos para eventos
class EventBase(BaseModel):
    name: str
    description: str
    fecha: str
    categoria: str
    precio: int
    cupos: int

class EventCreate(EventBase):
    user_id: int

class EventUpdate(EventBase):
    user_id: int

@app.post("/register")
def register(user: UserRegister):
    ok = auth.create_user(user.name, user.email, user.password)
    if not ok:
        raise HTTPException(status_code=400, detail="Email already registered")
    return {"message": "User created successfully"}


# CRUD de eventos
@app.post("/eventos", response_model=dict)
def create_event(event: EventCreate):
    event_id = eventos.create_event(event.name, event.description, event.fecha, event.categoria, event.precio, event.cupos, event.user_id)
    if not event_id:
        raise HTTPException(status_code=400, detail="Datos inválidos o fecha pasada")
    return {"message": "Evento creado", "event_id": event_id}

@app.get("/eventos", response_model=List[dict])
def list_events():
    return eventos.get_events()

@app.get("/eventos/{event_id}", response_model=dict)
def get_event(event_id: int):
    event = eventos.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    return event

@app.put("/eventos/{event_id}", response_model=dict)
def update_event(event_id: int, event: EventUpdate):
    ok = eventos.update_event(event_id, event.name, event.description, event.fecha, event.categoria, event.precio, event.cupos, event.user_id)
    if not ok:
        raise HTTPException(status_code=403, detail="No autorizado o datos inválidos")
    return {"message": "Evento actualizado"}

@app.delete("/eventos/{event_id}", response_model=dict)
def delete_event(event_id: int, user_id: int):
    ok = eventos.delete_event(event_id, user_id)
    if not ok:
        raise HTTPException(status_code=403, detail="No autorizado o evento no encontrado")
    return {"message": "Evento eliminado"}

@app.post("/login")
def login(user: UserLogin):
    uid = auth.verify_user(user.email, user.password)
    if not uid:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Login successful", "user_id": uid}


# Gestión de entradas: venta y devolución
@app.post("/eventos/{event_id}/venta", response_model=dict)
def registrar_venta(event_id: int):
    """Registra una venta de entrada para el evento (resta 1 cupo)."""
    return entradas.registrar_venta(event_id)

@app.post("/eventos/{event_id}/devolucion", response_model=dict)
def registrar_devolucion(event_id: int):
    """Registra una devolución de entrada para el evento (suma 1 cupo)."""
    return entradas.registrar_devolucion(event_id)
