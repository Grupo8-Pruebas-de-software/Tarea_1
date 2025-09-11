# Tarea_1

Este proyecto implementa un sistema de gestión de microeventos con autenticación, usando **FastAPI** para el backend y **Flask** para el frontend.  
La base de datos se gestiona con **SQLite**.


## 🤝 Cómo contribuir

¡Las contribuciones son bienvenidas! Puedes abrir issues para reportar errores o sugerir mejoras, y enviar pull requests siguiendo las buenas prácticas de desarrollo.

1. Haz un fork del repositorio
2. Crea una rama para tu feature/fix (`git checkout -b mi-feature`)
3. Realiza tus cambios y haz commit (`git commit -am 'Agrega nueva funcionalidad'`)
4. Haz push a tu rama (`git push origin mi-feature`)
5. Abre un Pull Request

---


### Texto de la Licencia MIT

MIT License

Copyright (c) 2025 Grupo8-Pruebas-de-software

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

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
- Crear un evento
- Modificar un evento
- Visualizar la informacion del evento
- Eliminar un evento en especifico
- Ventas y devoluciones de entradas.
- Reportes automáticos.
- Filtrado y búsqueda de eventos.

---
