from fastapi import FastAPI, HTTPException, Request, Body, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import auth
import eventos
import entradas
import reportes
from typing import List
from logger_config import logger
from typing import Optional, List
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
def list_events(
    categoria: Optional[str] = Query(None, description="Nombre exacto de la categoría"),
    dias: Optional[int] = Query(None, ge=1, le=365, description="Próximos N días"),
    estado: Optional[str] = Query(None, pattern="^(disponible|agotado)$", description="Estado"),
    q: Optional[str] = Query(None, description="Búsqueda por nombre/descr.")
):
    return eventos.get_events_filtered(categoria=categoria, dias=dias, estado=estado, q=q)

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
def registrar_venta(event_id: int, request: Request, user_id: int = Body(...), cantidad: int = Body(1)):
    """Registra una venta de entrada para el evento (resta n cupos)."""
    return entradas.registrar_venta(event_id, user_id, cantidad)

@app.post("/eventos/{event_id}/devolucion", response_model=dict)
def registrar_devolucion(event_id: int, request: Request, user_id: int = Body(...), cantidad: int = Body(1)):
    """Registra una devolución de entrada para el evento (suma n cupos)."""
    return entradas.registrar_devolucion(event_id, user_id, cantidad)

@app.get("/eventos/{event_id}/entradas_usuarios", response_model=list)
def entradas_por_usuario(event_id: int):
    """Devuelve una lista de usuarios y la cantidad de entradas que tiene cada uno para el evento."""
    conn = entradas.sqlite3.connect('../microevents.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT u.id, u.name, u.email, COALESCE(SUM(CASE WHEN tm.type='SALE' THEN tm.quantity WHEN tm.type='REFUND' THEN -tm.quantity ELSE 0 END),0) as entradas
        FROM users u
        LEFT JOIN ticket_movements tm ON tm.performed_by = u.id AND tm.event_id = ?
        GROUP BY u.id
        HAVING entradas > 0
        ORDER BY entradas DESC
    ''', (event_id,))
    data = [
        {"user_id": row[0], "name": row[1], "email": row[2], "entradas": row[3]} for row in cursor.fetchall()
    ]
    conn.close()
    return data

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response

# Gestión de resumen

@app.get("/reportes/resumen", response_model=dict)
def get_resumen():
    """Devuelve el resumen general de eventos y cupos"""
    return reportes.resumen_general()
