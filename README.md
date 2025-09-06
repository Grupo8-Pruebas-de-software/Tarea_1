# Tarea_1

Este proyecto implementa un sistema de gestión de microeventos con autenticación, usando **FastAPI** para el backend y **Flask** para el frontend.  
La base de datos se gestiona con **SQLite**.

---

## 📂 Estructura del proyecto
```
BD/
  └── init_db.py        # Script para crear la base de datos
Backend/
  ├── main.py           # API en FastAPI
  ├── auth.py           # Funciones de autenticación
  └── requirements.txt  # Dependencias del backend
Frontend/
  ├── app.py            # Frontend con Flask
  ├── templates/        # Vistas HTML (login, registro)
  └── requirements.txt  # Dependencias del frontend
microevents.db          # Base de datos SQLite (se genera al ejecutar init_db.py)
```

---

## 🚀 Configuración inicial

### 1. Crear la base de datos
Ejecutar el script:
```bash
python BD/init_db.py
```

Esto creará el archivo `microevents.db` con las tablas necesarias.

---

### 2. Preparar entornos virtuales

Se recomienda usar entornos separados para **backend** y **frontend**.

#### Backend
```bash
cd Backend
python -m venv .venv
.venv\Scripts\activate   # En Windows
pip install -r requirements.txt
```

Ejecutar:
```bash
uvicorn main:app --reload
```

Acceder a la API:
👉 http://127.0.0.1:8000/docs

---

#### Frontend
```bash
cd Frontend
python -m venv .venv
.venv\Scripts\activate   # En Windows
pip install -r requirements.txt
```

Ejecutar:
```bash
python app.py
```

Acceder a la web:
👉 http://127.0.0.1:5000

---

## 👤 Funcionalidades actuales

- Crear usuario (registro).
- Iniciar sesión con email y contraseña (encriptada).
- Validación de credenciales.

---

## 📌 Próximos pasos

- CRUD de eventos.
- Ventas y devoluciones de entradas.
- Reportes automáticos.
- Filtrado y búsqueda de eventos.
