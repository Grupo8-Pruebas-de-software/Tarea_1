import sqlite3
import os
from logger_config import logger

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "microevents.db")
DB_PATH = os.path.abspath(DB_PATH)

def resumen_general():
    """Devuelve un resumen con:
    - total_eventos: total de eventos registrados
    - total_cupos: suma de todos los cupos disponibles
    - eventos_agotados: cantidad de eventos con cupos = 0
    """
    try:
        with sqlite3.connect(DB_PATH) as con:
            cur = con.cursor()
            cur.execute("""
                SELECT
                    COUNT(*) AS total_eventos,
                    COALESCE(SUM(current_quota), 0) AS total_cupos,
                    SUM(CASE WHEN current_quota = 0 THEN 1 ELSE 0 END) AS eventos_agotados
                FROM events
            """)
            row = cur.fetchone()
            resumen = {
                "total_eventos": row[0],
                "total_cupos": row[1],
                "eventos_agotados": row[2]
            }
            logger.info(f"Reporte general consultado: {resumen}")
            return resumen
    except Exception as e:
        logger.error(f"Error al generar resumen general: {e}")
        return {"total_eventos": 0, "total_cupos": 0, "eventos_agotados": 0}
