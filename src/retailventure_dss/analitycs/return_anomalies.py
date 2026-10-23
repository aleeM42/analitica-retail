import pandas as pd
from retailventure_dss.data_access.duckdb_conn import SingletonDbConnection


def analyze_returns_and_crm_impact() -> dict:
    conn = SingletonDbConnection.get_connection()

    #  productos con devolucion (> 1.5x promedio general)
    query_productos = """
    WITH stats_devoluciones AS (
        SELECT 
            p.producto_id,
            p.nombre,
            p.categoria,
            COUNT(DISTINCT t.transaccion_id) AS total_ventas,
            COUNT(DISTINCT d.devolucion_id) AS total_devoluciones,
            SUM(d.monto_devuelto) AS total_monto_devuelto,
            (COUNT(DISTINCT d.devolucion_id)::FLOAT / NULLIF(COUNT(DISTINCT t.transaccion_id), 0)) AS tasa_devolucion
        FROM clean_productos p
        LEFT JOIN clean_transacciones t ON p.producto_id = t.producto_id
        LEFT JOIN clean_devoluciones d ON t.transaccion_id = d.transaccion_id
        GROUP BY p.producto_id, p.nombre, p.categoria
    )
    SELECT *,
           CASE WHEN tasa_devolucion > 0.20 THEN TRUE ELSE FALSE END AS es_anomalo
    FROM stats_devoluciones
    ORDER BY total_monto_devuelto DESC
    """
    df_productos = conn.execute(query_productos).fetchdf()

    #  impacto de quejas CRM no resueltas en la recompras
    query_crm = """
    WITH clientes_quejas AS (
        SELECT 
            c.cliente_id,
            COUNT(i.interaccion_id) AS total_quejas,
            SUM(CASE WHEN i.resolucion = 'No Resuelto' THEN 1 ELSE 0 END) AS quejas_no_resueltas
        FROM clean_clientes c
        JOIN clean_interacciones_crm i ON c.cliente_id = i.cliente_id
        WHERE i.tipo = 'Queja'
        GROUP BY c.cliente_id
    ),
    compras_posteriores AS (
        SELECT 
            cq.cliente_id,
            cq.quejas_no_resueltas,
            COUNT(t.transaccion_id) AS compras_totales,
            SUM(t.monto_neto) AS ingreso_generado
        FROM clientes_quejas cq
        LEFT JOIN clean_transacciones t ON cq.cliente_id = t.cliente_id
        GROUP BY cq.cliente_id, cq.quejas_no_resueltas
    )
    SELECT 
        CASE WHEN quejas_no_resueltas > 0 THEN 'Con Quejas No Resueltas' ELSE 'Sin Quejas No Resueltas' END AS grupo_crm,
        COUNT(cliente_id) AS total_clientes,
        AVG(compras_totales) AS promedio_compras,
        AVG(ingreso_generado) AS ingreso_promedio
    FROM compras_posteriores
    GROUP BY 1
    """
    df_crm_impacto = conn.execute(query_crm).fetchdf()

    return {
        "productos_anomalos": df_productos[df_productos["es_anomalo"] == True],
        "top_devoluciones": df_productos.head(10),
        "impacto_crm": df_crm_impacto,
    }


if __name__ == "__main__":
    res = analyze_returns_and_crm_impact()
    # print(res)
    print("Top Productos con Devoluciones:")
    print(
        res["top_devoluciones"][["nombre", "tasa_devolucion", "total_monto_devuelto"]]
    )
