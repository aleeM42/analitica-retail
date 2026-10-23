import numpy as np
from retailventure_dss.data_access.duckdb_conn import SingletonDbConnection

import pandas as pd


def calculate_customer_rfm_and_churn(
    reference_date: str = None,
) -> pd.DataFrame:
    conn = SingletonDbConnection.get_connection()

    if reference_date is None:
        row = conn.execute(
            "SELECT MAX(fecha)::VARCHAR FROM clean_transacciones"
        ).fetchone()
        if row and row[0]:
            reference_date = row[0]
        else:
            reference_date = "2024-12-31"  # cambiar

    query = f"""
    WITH rfm_base AS (
        SELECT 
            c.cliente_id,
            c.segmento,
            c.ciudad,
            c.canal_adquisicion,
            MIN(t.fecha) AS primera_compra,
            MAX(t.fecha) AS ultima_compra,
            COUNT(DISTINCT t.transaccion_id) AS frecuencia,
            SUM(t.monto_neto) AS valor_monetario_total,
            AVG(t.monto_neto) AS ticket_promedio,
            DATE_DIFF('day', MAX(t.fecha), DATE '{reference_date}') AS recencia_dias,
            DATE_DIFF('day', MIN(t.fecha), DATE '{reference_date}') AS antiguedad_dias
        FROM clean_clientes c
        LEFT JOIN clean_transacciones t ON c.cliente_id = t.cliente_id
        GROUP BY c.cliente_id, c.segmento, c.ciudad, c.canal_adquisicion
    )
    SELECT 
        *,
        CASE 
            WHEN recencia_dias > 180 THEN 'Churn Confirmado'
            WHEN recencia_dias > 90 THEN 'Riesgo Alto'
            WHEN recencia_dias > 45 THEN 'Riesgo Medio'
            ELSE 'Activo'
        END AS estado_cliente,
        LEAST(1.0, recencia_dias / 180.0) AS probabilidad_churn,
        CASE 
            WHEN antiguedad_dias > 0 
            THEN (frecuencia / (antiguedad_dias / 365.0)) * ticket_promedio * 0.35
            ELSE ticket_promedio * 0.35
        END AS clv_estimado_12m
    FROM rfm_base
    """

    df_rfm = conn.execute(query).fetchdf()
    return df_rfm


if __name__ == "__main__":
    df = calculate_customer_rfm_and_churn()
    print("Resumen de Clientes por Estado de Churn:")
    # print(df)
    print(df.groupby("estado_cliente")["cliente_id"].count())
