# entradas.py
# Funciones auxiliares para la gestión de ventas y devoluciones de entradas
import sqlite3
from fastapi import HTTPException

def get_evento(evento_id):
    conn = sqlite3.connect('../microevents.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, current_quota, initial_quota FROM events WHERE id = ?", (evento_id,))
    evento = cursor.fetchone()
    conn.close()
    return evento

def registrar_venta(evento_id, user_id, cantidad=1):
    if cantidad <= 0:
        raise HTTPException(status_code=400, detail="La cantidad debe ser mayor a 0")
    evento = get_evento(evento_id)
    if not evento:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    id, current_quota, _ = evento
    if cantidad > current_quota:
        raise HTTPException(status_code=400, detail="No hay suficientes cupos disponibles para este evento")
    conn = sqlite3.connect('../microevents.db')
    cursor = conn.cursor()
    # Registrar movimiento de tickets
    cursor.execute("INSERT INTO ticket_movements (event_id, type, quantity, performed_by) VALUES (?, 'SALE', ?, ?)", (evento_id, cantidad, user_id))
    # Actualizar cupos
    cursor.execute("UPDATE events SET current_quota = current_quota - ? WHERE id = ?", (cantidad, evento_id))
    conn.commit()
    conn.close()
    return {"mensaje": "Venta registrada", "current_quota": current_quota - cantidad}

def registrar_devolucion(evento_id, user_id, cantidad=1):
    if cantidad <= 0:
        raise HTTPException(status_code=400, detail="La cantidad debe ser mayor a 0")
    evento = get_evento(evento_id)
    if not evento:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    id, current_quota, initial_quota = evento
    # Validar que el usuario tenga entradas para devolver
    conn = sqlite3.connect('../microevents.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COALESCE(SUM(CASE WHEN type='SALE' THEN quantity WHEN type='REFUND' THEN -quantity ELSE 0 END),0) FROM ticket_movements WHERE event_id=? AND performed_by=?", (evento_id, user_id))
    entradas_usuario = cursor.fetchone()[0]
    if cantidad > entradas_usuario:
        conn.close()
        raise HTTPException(status_code=400, detail="No tienes suficientes entradas para devolver")
    if current_quota + cantidad > initial_quota:
        conn.close()
        raise HTTPException(status_code=400, detail="No se puede devolver más allá del cupo inicial")
    # Registrar movimiento de devolución
    cursor.execute("INSERT INTO ticket_movements (event_id, type, quantity, performed_by) VALUES (?, 'REFUND', ?, ?)", (evento_id, cantidad, user_id))
    # Actualizar cupos
    cursor.execute("UPDATE events SET current_quota = current_quota + ? WHERE id = ?", (cantidad, evento_id))
    conn.commit()
    conn.close()
    return {"mensaje": "Devolución registrada", "current_quota": current_quota + cantidad}
