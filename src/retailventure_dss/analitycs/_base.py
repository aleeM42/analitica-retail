"""Utilidades compartidas por los módulos de análisis (A2 y A3).

Todos los análisis leen de las tablas `clean_*` del warehouse DuckDB y escriben sus
resultados como CSV en `data/out/resultados/<modulo>/` (carpeta configurable con la
variable de entorno RESULTS_DIR).
"""

from os import getenv
from pathlib import Path

import pandas as pd

from retailventure_dss.data_access.duckdb_conn import SingletonDbConnection

RESULTS_DIR = Path(getenv("RESULTS_DIR", "./data/out/resultados"))

# La ventana de observación del dataset es 2023-01-01 a 2024-12-31 (24 meses, 731 días).
INICIO_VENTANA = pd.Timestamp("2023-01-01")
FIN_VENTANA = pd.Timestamp("2024-12-31")
DIAS_VENTANA = (FIN_VENTANA - INICIO_VENTANA).days + 1


def cargar_ventas() -> pd.DataFrame:
    """Una fila por transacción, enriquecida con producto, cliente y devolución.

    Columnas calculadas:
      - margen: monto_neto - costo * cantidad (margen bruto real, ya con descuento).
      - monto_devuelto / devuelta: 0 / False si la transacción no tuvo devolución.
      - costo_devuelto: costo de la mercancía devuelta, prorrateado por la fracción
        devuelta del monto (sirve para el escenario donde la mercancía se recupera).
    """
    conn = SingletonDbConnection.get_connection()
    df = conn.execute(
        """
        SELECT
            t.transaccion_id, t.cliente_id, t.producto_id,
            t.fecha::DATE AS fecha, t.cantidad,
            t.precio_unitario::DOUBLE AS precio_unitario,
            t.descuento::DOUBLE AS descuento,
            t.monto_neto::DOUBLE AS monto_neto,
            t.canal, t.metodo_pago,
            p.categoria, p.subcategoria,
            p.costo::DOUBLE AS costo, p.precio_lista::DOUBLE AS precio_lista,
            c.segmento, c.canal_adquisicion, c.ciudad, c.fecha_registro,
            COALESCE(d.monto_devuelto, 0)::DOUBLE AS monto_devuelto,
            d.devolucion_id IS NOT NULL AS devuelta,
            d.motivo, d.fecha_devolucion::DATE AS fecha_devolucion
        FROM clean_transacciones t
        JOIN clean_productos p USING (producto_id)
        JOIN clean_clientes  c USING (cliente_id)
        LEFT JOIN clean_devoluciones d USING (transaccion_id)
        """
    ).fetchdf()
    df["fecha"] = pd.to_datetime(df["fecha"])
    df["fecha_devolucion"] = pd.to_datetime(df["fecha_devolucion"])
    df["margen"] = df["monto_neto"] - df["costo"] * df["cantidad"]
    frac = (df["monto_devuelto"] / df["monto_neto"]).where(df["monto_neto"] > 0, 0.0)
    df["costo_devuelto"] = df["costo"] * df["cantidad"] * frac
    return df


def cargar_clientes() -> pd.DataFrame:
    conn = SingletonDbConnection.get_connection()
    df = conn.execute("SELECT * FROM clean_clientes").fetchdf()
    df["fecha_registro"] = pd.to_datetime(df["fecha_registro"])
    return df


def cargar_crm() -> pd.DataFrame:
    conn = SingletonDbConnection.get_connection()
    df = conn.execute("SELECT * FROM clean_interacciones_crm").fetchdf()
    df["fecha"] = pd.to_datetime(df["fecha"])
    return df


def guardar(df: pd.DataFrame, modulo: str, nombre: str) -> Path:
    carpeta = RESULTS_DIR / modulo
    carpeta.mkdir(parents=True, exist_ok=True)
    ruta = carpeta / f"{nombre}.csv"
    df.to_csv(ruta, index=False)
    return ruta
