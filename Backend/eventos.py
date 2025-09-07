from datetime import date, timedelta
from typing import List, Optional
from logger_config import logger
import sqlite3

def get_db_connection():
    conn = sqlite3.connect('../microevents.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_category_id_by_name(category_name: str) -> Optional[int]:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id FROM categories WHERE name = ?', (category_name,))
    row = cur.fetchone()
    conn.close()
    return row['id'] if row else None

def create_event(name: str, description: str, fecha: str, categoria: str, precio: int, cupos: int, user_id: int) -> Optional[int]:
    if len(name) > 100 or precio < 0 or cupos < 0:
        return None
    try:
        event_date = date.fromisoformat(fecha)
        if event_date < date.today():
            return None
    except Exception:
        return None
    category_id = get_category_id_by_name(categoria)
    if not category_id:
        return None
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''INSERT INTO events (name, description, date, category_id, price, initial_quota, current_quota, created_by)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', (name, description, fecha, category_id, precio, cupos, cupos, user_id))
    conn.commit()
    event_id = cur.lastrowid
    conn.close()
    logger.info(f"Evento creado: id={event_id}, nombre='{name}', user_id={user_id}")
    return event_id

def get_events() -> List[dict]:
    conn = get_db_connection()
    events = conn.execute('''
        SELECT e.*, c.name as category_name, u.name as creator_name
        FROM events e
        JOIN categories c ON e.category_id = c.id
        JOIN users u ON e.created_by = u.id
    ''').fetchall()
    conn.close()
    return [dict(event) for event in events]

def get_event(event_id: int) -> Optional[dict]:
    conn = get_db_connection()
    event = conn.execute('''
        SELECT e.*, c.name as category_name, u.name as creator_name
        FROM events e
        JOIN categories c ON e.category_id = c.id
        JOIN users u ON e.created_by = u.id
        WHERE e.id = ?
    ''', (event_id,)).fetchone()
    conn.close()
    return dict(event) if event else None

def update_event(event_id: int, name: str, description: str, fecha: str, categoria: str, precio: int, cupos: int, user_id: int) -> bool:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT created_by, initial_quota, current_quota FROM events WHERE id = ?', (event_id,))
    row = cur.fetchone()
    if not row or row['created_by'] != user_id:
        conn.close()
        return False
    initial_quota_old = row['initial_quota']
    current_quota_old = row['current_quota']
    try:
        event_date = date.fromisoformat(fecha)
        if event_date < date.today():
            conn.close()
            return False
    except Exception:
        conn.close()
        return False
    if len(name) > 100 or precio < 0 or cupos < 0:
        conn.close()
        return False
    category_id = get_category_id_by_name(categoria)
    if not category_id:
        conn.close()
        return False
    # Solo aumentar initial_quota si cupos es mayor al valor anterior
    new_initial_quota = max(initial_quota_old, cupos)
    # Si el cupo aumenta, aumentar current_quota en la misma diferencia
    diff = new_initial_quota - initial_quota_old
    new_current_quota = current_quota_old + diff if diff > 0 else current_quota_old
    cur.execute('''UPDATE events SET name=?, description=?, date=?, category_id=?, price=?, initial_quota=?, current_quota=?, updated_at=datetime('now') WHERE id=?''',
                (name, description, fecha, category_id, precio, new_initial_quota, new_current_quota, event_id))
    conn.commit()
    conn.close()
    return True

def delete_event(event_id: int, user_id: int) -> bool:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT created_by FROM events WHERE id = ?', (event_id,))
    row = cur.fetchone()
    if not row or row['created_by'] != user_id:
        conn.close()
        return False
    cur.execute('DELETE FROM events WHERE id = ?', (event_id,))
    conn.commit()
    conn.close()
    return True

def get_categories() -> List[dict]:
    conn = get_db_connection()
    rows = conn.execute("SELECT id, name FROM categories ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def _status_sql_predicate(estado: Optional[str]) -> Optional[str]:
    if not estado:
        return None
    estado = estado.lower().strip()
    if estado == "disponible":
        # no agotado y quedan cupos
        return "(e.is_sold_out = 0 AND e.current_quota > 0)"
    if estado == "agotado":
        # marcado agotado o sin cupos
        return "(e.is_sold_out = 1 OR e.current_quota = 0)"
    return None

def get_events_filtered(
    categoria: Optional[str] = None,
    dias: Optional[int] = None,
    estado: Optional[str] = None,
    q: Optional[str] = None
) -> List[dict]:
    """
    Filtros:
      - categoria: nombre exacto de la categoría (p.ej. 'Taller')
      - dias: próximos N días (incluye hoy)
      - estado: 'disponible' o 'agotado'
      - q: keyword en name/description (LIKE)
    """
    conn = get_db_connection()
    cur = conn.cursor()

    base_sql = """
        SELECT e.*, c.name as category_name, u.name as creator_name
        FROM events e
        JOIN categories c ON e.category_id = c.id
        JOIN users u ON e.created_by = u.id
    """

    where = []
    params: list = []

    # Categoría por nombre (opcional)
    if categoria:
        where.append("c.name = ?")
        params.append(categoria)

    # Próximos N días (opcional)
    if dias and dias > 0:
        hoy = date.today()
        hasta = hoy + timedelta(days=dias)
        where.append("date(e.date) BETWEEN date(?) AND date(?)")
        params.extend([hoy.isoformat(), hasta.isoformat()])

    # Estado (opcional)
    status_pred = _status_sql_predicate(estado)
    if status_pred:
        where.append(status_pred)

    # Búsqueda por keyword (opcional)
    if q:
        like = f"%{q.lower()}%"
        where.append("(LOWER(e.name) LIKE ? OR LOWER(e.description) LIKE ?)")
        params.extend([like, like])

    sql = base_sql
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY date(e.date) ASC, e.id DESC"

    rows = cur.execute(sql, tuple(params)).fetchall()
    conn.close()
    return [dict(r) for r in rows]