from datetime import date
from typing import Any, Final, cast
from os import getenv
import numpy as np

from numpy import append
from pydantic import BaseModel, ValidationError
from retailventure_dss.common.types.genders import Gender
from retailventure_dss.common.types.id_format import IdFormat
from retailventure_dss.data_access.duckdb_conn import (
    SingletonDbConnection,
    create_etl_tables,
)
from retailventure_dss.etl.models.campanas_marketing import Campana
from retailventure_dss.etl.models.clientes import Cliente
from retailventure_dss.etl.models.devoluciones import Devolucion
from retailventure_dss.etl.models.interacciones_crm import Interaccion
from retailventure_dss.etl.models.productos import Productos
from retailventure_dss.etl.models.transacciones import Transacciones


import pandas as pd

from retailventure_dss.etl.models.type import RetailVentureTables

from retailventure_dss.etl.quality_report import build_quality_report, outlier_profile


_CSV_DIR: Final[str] = getenv("CSV_DIR", "./data/in")


MAPPED_CLASS_TO_FILES: Final = [
    (f"{_CSV_DIR}/productos.csv", Productos),
    (f"{_CSV_DIR}/clientes.csv", Cliente),
    (f"{_CSV_DIR}/interacciones_crm.csv", Interaccion),
    (f"{_CSV_DIR}/transacciones.csv", Transacciones),
    (f"{_CSV_DIR}/campanas_marketing.csv", Campana),
    (f"{_CSV_DIR}/devoluciones.csv", Devolucion),
]




perfiles = {}



def extract(filepath: str) -> list[dict[Any, Any]]:
    raw_data: pd.DataFrame = pd.read_csv(filepath_or_buffer=filepath)
    for entry in MAPPED_CLASS_TO_FILES:
        if filepath == entry[0]:
            filas_out, _ = outlier_profile(raw_data)
            perfiles[str(entry[1])] = {
                "celdas": int(raw_data.size),
                "nulos": int(raw_data.isna().sum().sum()),
                "filas_outlier": filas_out,
            }
    return raw_data.to_dict(orient="records")


class TransformResult:
    approved_entries: list[type[BaseModel]]
    rejected_entries: list[dict]
    nulls: int
    dups: int

    def __init__(
        self,
        approved_entries: list[type[BaseModel]],
        rejected_entries: list[dict],
        nulls,
        dups,
    ) -> None:

        self.approved_entries = approved_entries
        self.rejected_entries = rejected_entries
        self.nulls = nulls
        self.dups = dups


def transform(
    records: list[dict[Any, Any]], object_class: type[RetailVentureTables]
) -> TransformResult:
    approved_rows: list[type[BaseModel]] = []
    rejected_rows: list[dict] = []
    seen_ids = set()
    dups = 0
    nulls = 0
    for record in records:
        try:
            clean_object = object_class(**record)

            if clean_object.get_id() in seen_ids:
                raise ValueError("duplicated")
            seen_ids.add(clean_object.get_id())
            approved_rows.append(clean_object)
        except ValidationError as e:
            nulls += 1
            record["motivo_error"] = e.errors()[0]["msg"]
            rejected_rows.append(record)
        except ValueError:
            dups += 1
            record["motivo_error"] = "Valor duplicado"
            rejected_rows.append(record)

    return TransformResult(approved_rows, rejected_rows, nulls, dups)


def extract_and_transform(filepath, object_class):
    return transform(extract(filepath), object_class)


def delete_from_approved(value, data: TransformResult):
    data.approved_entries.remove(value)
    data.rejected_entries.append(value)


def etl():
    results = {}
    for entry in MAPPED_CLASS_TO_FILES:
        coso = extract_and_transform(*entry)
        print(entry[1])
        print(
            f"Buenos: {len(coso.approved_entries)}| Malos {len(coso.rejected_entries)}"
        )

        results[str(entry[1])] = coso

    conn = SingletonDbConnection.get_connection()
    create_etl_tables()

    conn.execute("BEGIN")
    data = cast(list[Cliente], results.get(str(Cliente)).approved_entries)

    bulk = [
        tuple(
            getattr(c, col)
            for col in (
                "cliente_id",
                "edad",
                "genero",
                "ciudad",
                "segmento",
                "fecha_registro",
                "canal_adquisicion",
            )
        )
        for c in data
    ]

    data = cast(list[Cliente], results.get(str(Cliente)).approved_entries)
    bulk = [
        tuple(
            str(v) if not isinstance(v, (int, float, bool, type(None), date)) else v
            for v in (
                getattr(c, col)
                for col in (
                    "cliente_id",
                    "edad",
                    "genero",
                    "ciudad",
                    "segmento",
                    "fecha_registro",
                    "canal_adquisicion",
                )
            )
        )
        for c in data
    ]

    print(f"Inserting in dirty {data[0].__class__}")
    conn.executemany(
        """
        INSERT INTO stg_clientes
            (cliente_id, edad, genero, ciudad, segmento, fecha_registro, canal_adquisicion)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
        bulk,
    )

    data = cast(list[Productos], results.get(str(Productos)).approved_entries)
    bulk = [
        tuple(
            str(v) if not isinstance(v, (int, float, bool, type(None), date)) else v
            for v in (
                getattr(p, col)
                for col in (
                    "producto_id",
                    "nombre",
                    "categoria",
                    "subcategoria",
                    "costo",
                    "precio_lista",
                    "margen_bruto_pct",
                )
            )
        )
        for p in data
    ]
    print(f"Inserting in dirty {data[0].__class__}")
    conn.executemany(
        """
        INSERT INTO stg_productos
            (producto_id, nombre, categoria, subcategoria,
             costo, precio_lista, margen_bruto_pct)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
        bulk,
    )

    data = cast(list[Transacciones], results.get(str(Transacciones)).approved_entries)
    bulk = [
        tuple(
            str(v) if not isinstance(v, (int, float, bool, type(None), date)) else v
            for v in (
                getattr(t, col)
                for col in (
                    "transaccion_id",
                    "cliente_id",
                    "fecha",
                    "producto_id",
                    "cantidad",
                    "precio_unitario",
                    "descuento",
                    "monto_neto",
                    "canal",
                    "metodo_pago",
                )
            )
        )
        for t in data
    ]
    print(f"Inserting in dirty {data[0].__class__}")
    conn.executemany(
        """
        INSERT INTO stg_transacciones
            (transaccion_id, cliente_id, fecha, producto_id,
             cantidad, precio_unitario, descuento, monto_neto,
             canal, metodo_pago)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        bulk,
    )

    data = cast(list[Campana], results.get(str(Campana)).approved_entries)
    bulk = [
        tuple(
            str(v) if not isinstance(v, (int, float, bool, type(None), date)) else v
            for v in (
                getattr(c, col)
                for col in (
                    "campana_id",
                    "cliente_id",
                    "tipo_campana",
                    "fecha_envio",
                    "canal_campana",
                    "abierto",
                    "convertido",
                    "descuento_ofrecido",
                )
            )
        )
        for c in data
    ]
    print(f"Inserting in dirty {data[0].__class__}")
    conn.executemany(
        """
        INSERT INTO stg_campanas_marketing
            (campana_id, cliente_id, tipo_campana, fecha_envio,
             canal_campana, abierto, convertido, descuento_ofrecido)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """,
        bulk,
    )

    data = cast(list[Interaccion], results.get(str(Interaccion)).approved_entries)
    bulk = [
        tuple(
            str(v) if not isinstance(v, (int, float, bool, type(None), date)) else v
            for v in (
                getattr(i, col)
                for col in (
                    "interaccion_id",
                    "cliente_id",
                    "tipo",
                    "fecha",
                    "canal",
                    "resolucion",
                    "tiempo_respuesta_hrs",
                )
            )
        )
        for i in data
    ]
    print(f"Inserting in dirty {data[0].__class__}")
    conn.executemany(
        """
        INSERT INTO stg_interacciones_crm
            (interaccion_id, cliente_id, tipo, fecha,
             canal, resolucion, tiempo_respuesta_hrs)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
        bulk,
    )

    data = cast(list[Devolucion], results.get(str(Devolucion)).approved_entries)
    bulk = [
        tuple(
            str(v) if not isinstance(v, (int, float, bool, type(None), date)) else v
            for v in (
                getattr(d, col)
                for col in (
                    "devolucion_id",
                    "transaccion_id",
                    "cliente_id",
                    "motivo",
                    "monto_devuelto",
                    "fecha_devolucion",
                )
            )
        )
        for d in data
    ]
    print(f"Inserting in dirty {data[0].__class__}")
    conn.executemany(
        """
        INSERT INTO stg_devoluciones
            (devolucion_id, transaccion_id, cliente_id,
             motivo, monto_devuelto, fecha_devolucion)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
        bulk,
    )
    conn.execute("COMMIT")
    conn.execute("BEGIN")

    print("Inserting in clean Cliente")
    conn.execute(
        """
            INSERT INTO clean_clientes
                (cliente_id, edad, genero, ciudad, segmento, fecha_registro, canal_adquisicion)
            SELECT cliente_id, edad, genero, ciudad, segmento, fecha_registro, canal_adquisicion
            FROM stg_clientes
            WHERE genero IN ('M', 'F', 'ND')
            AND edad >= 0
            AND fecha_registro IS NOT NULL
        """
    )

    print("Inserting in clean Productos")
    conn.execute(
        """
            INSERT INTO clean_productos
                (producto_id, nombre, categoria, subcategoria, costo, precio_lista, margen_bruto_pct)
            SELECT producto_id, nombre, categoria, subcategoria, costo, precio_lista, margen_bruto_pct
            FROM stg_productos
            WHERE costo >= 0.00
            AND precio_lista >= 0.00
            AND margen_bruto_pct >= 0.0
        """
    )

    print("Inserting in clean Campana")
    conn.execute(
        """
            INSERT INTO clean_campanas_marketing
                (campana_id, cliente_id, tipo_campana, fecha_envio,
                canal_campana, abierto, convertido, descuento_ofrecido)
            SELECT s.campana_id, s.cliente_id, s.tipo_campana, s.fecha_envio,
                s.canal_campana, s.abierto, s.convertido, s.descuento_ofrecido
            FROM stg_campanas_marketing s
            JOIN clean_clientes c ON c.cliente_id = s.cliente_id
            WHERE s.descuento_ofrecido >= 0.00
            AND s.descuento_ofrecido <= 1.00
        """
    )

    print("Inserting in clean Interaccion")
    conn.execute(
        """
            INSERT INTO clean_interacciones_crm
                (interaccion_id, cliente_id, tipo, fecha,
                canal, resolucion, tiempo_respuesta_hrs)
            SELECT s.interaccion_id, s.cliente_id, s.tipo, s.fecha,
                s.canal, s.resolucion, s.tiempo_respuesta_hrs
            FROM stg_interacciones_crm s
            JOIN clean_clientes c ON c.cliente_id = s.cliente_id
            WHERE s.tiempo_respuesta_hrs >= 0.0
        """
    )

    print("Inserting in clean Transacciones")
    conn.execute(
        """
            INSERT INTO clean_transacciones
                (transaccion_id, cliente_id, fecha, producto_id,
                cantidad, precio_unitario, descuento, monto_neto,
                canal, metodo_pago)
            SELECT s.transaccion_id, s.cliente_id, s.fecha, s.producto_id,
                s.cantidad, s.precio_unitario, s.descuento, s.monto_neto,
                s.canal, s.metodo_pago
            FROM stg_transacciones s
            JOIN clean_clientes  c ON c.cliente_id  = s.cliente_id
            JOIN clean_productos p ON p.producto_id = s.producto_id
            WHERE s.cantidad > 0
            AND s.precio_unitario >= 0.00
            AND s.descuento >= 0.000
            AND s.descuento <= 1.000
            AND s.monto_neto >= 0.00
        """
    )

    print("Inserting in clean Devolucion")
    conn.execute(
        """
            INSERT INTO clean_devoluciones
                (devolucion_id, transaccion_id, cliente_id,
                motivo, monto_devuelto, fecha_devolucion)
            SELECT s.devolucion_id, s.transaccion_id, s.cliente_id,
                s.motivo, s.monto_devuelto, s.fecha_devolucion
            FROM stg_devoluciones s
            JOIN clean_transacciones t ON t.transaccion_id = s.transaccion_id
            JOIN clean_clientes      c ON c.cliente_id     = s.cliente_id
            WHERE s.monto_devuelto >= 0.00
        """
    )

    conn.execute("COMMIT")
    print(
        "Filas en clean_clientes (prueba):",
        conn.execute("SELECT COUNT(*) FROM clean_clientes").fetchone()[0],
    )
    print(
        "Filas en clean_transacciones (prueba):",
        conn.execute("SELECT COUNT(*) FROM clean_transacciones").fetchone()[0],
    )

    modelos = [
        (Cliente, "clientes", "clean_clientes"),
        (Productos, "productos", "clean_productos"),
        (Transacciones, "transacciones", "clean_transacciones"),
        (Campana, "campanas_marketing", "clean_campanas_marketing"),
        (Interaccion, "interacciones_crm", "clean_interacciones_crm"),
        (Devolucion, "devoluciones", "clean_devoluciones"),
    ]
    datasets = []
    for modelo, nombre, tabla_clean in modelos:
        r = cast(TransformResult, results[str(modelo)])
        datasets.append({
            "nombre": nombre,
            "total": len(r.approved_entries) + len(r.rejected_entries),
            "rechazados_pydantic": len(r.rejected_entries),
            "dups": r.dups,
            "perfil": perfiles[str(modelo)],
            "filas_clean": conn.execute(f"SELECT COUNT(*) FROM {tabla_clean}").fetchone()[0],
            "rechazados": r.rejected_entries,
        })
    df_auditoria, df_errores = build_quality_report(conn, datasets)
    df_auditoria.to_csv("./data/out/reporte_calidad.csv", index=False)
    df_errores.to_csv("./data/out/errores_inconsistentes.csv", index=False)
    print(df_auditoria.to_string(index=False))

    print("Cargando capa dimensional...")
    populate_dimensional_tables()
    print("Capas dimensionales cargadas")


def populate_dimensional_tables():
    conn = SingletonDbConnection.get_connection()

    conn.execute("""
        INSERT INTO dim_cliente (
            sk_cliente, cliente_id, edad, genero, ciudad,
            segmento, fecha_registro, canal_adquisicion
        )
        SELECT 
            ROW_NUMBER() OVER (ORDER BY cliente_id) AS sk_cliente,
            cliente_id,
            edad,
            genero,
            ciudad,
            segmento,
            fecha_registro,
            canal_adquisicion
        FROM clean_clientes;
    """)

    conn.execute("""
        INSERT INTO dim_producto (
            sk_producto, producto_id, nombre, categoria,
            subcategoria, costo, precio_lista, margen_bruto_pct
        )
        SELECT 
            ROW_NUMBER() OVER (ORDER BY producto_id) AS sk_producto,
            producto_id,
            nombre,
            categoria,
            subcategoria,
            costo,
            precio_lista,
            margen_bruto_pct
        FROM clean_productos;
    """)

    conn.execute("""
        INSERT INTO dim_tiempo (
            sk_tiempo, fecha, dia, mes, nombre_mes,
            trimestre, anio, dia_semana
        )
        WITH fechas_unicas AS (
            SELECT fecha FROM clean_transacciones WHERE fecha IS NOT NULL
            UNION
            SELECT fecha_devolucion AS fecha FROM clean_devoluciones WHERE fecha_devolucion IS NOT NULL
            UNION
            SELECT fecha_envio AS fecha FROM clean_campanas_marketing WHERE fecha_envio IS NOT NULL
            UNION
            SELECT fecha FROM clean_interacciones_crm WHERE fecha IS NOT NULL
        )
        SELECT 
            CAST(STRFTIME(fecha, '%Y%m%d') AS INTEGER) AS sk_tiempo,
            fecha,
            DAY(fecha) AS dia,
            MONTH(fecha) AS mes,
            STRFTIME(fecha, '%B') AS nombre_mes,
            QUARTER(fecha) AS trimestre,
            YEAR(fecha) AS anio,
            STRFTIME(fecha, '%A') AS dia_semana
        FROM fechas_unicas
        ORDER BY fecha;
    """)

    conn.execute("""
        INSERT INTO fact_transacciones (
            sk_transaccion, sk_cliente, sk_producto, sk_tiempo,
            transaccion_id, canal, metodo_pago,
            cantidad, precio_unitario, descuento, monto_neto
        )
        SELECT 
            ROW_NUMBER() OVER (ORDER BY t.transaccion_id) AS sk_transaccion,
            dc.sk_cliente,
            dp.sk_producto,
            dt.sk_tiempo,
            t.transaccion_id,
            t.canal,
            t.metodo_pago,
            t.cantidad,
            t.precio_unitario,
            t.descuento,
            t.monto_neto
        FROM clean_transacciones t
        JOIN dim_cliente dc ON t.cliente_id = dc.cliente_id
        JOIN dim_producto dp ON t.producto_id = dp.producto_id
        JOIN dim_tiempo dt ON t.fecha = dt.fecha;
    """)

    conn.execute("""
        INSERT INTO fact_devoluciones (
            sk_devolucion, sk_cliente, sk_producto, sk_tiempo,
            devolucion_id, transaccion_id, motivo, monto_devuelto
        )
        SELECT 
            ROW_NUMBER() OVER (ORDER BY d.devolucion_id) AS sk_devolucion,
            dc.sk_cliente,
            dp.sk_producto,
            dt.sk_tiempo,
            d.devolucion_id,
            d.transaccion_id,
            d.motivo,
            d.monto_devuelto
        FROM clean_devoluciones d
        JOIN dim_cliente dc ON d.cliente_id = dc.cliente_id
        JOIN clean_transacciones t ON d.transaccion_id = t.transaccion_id
        JOIN dim_producto dp ON t.producto_id = dp.producto_id
        JOIN dim_tiempo dt ON d.fecha_devolucion = dt.fecha;
    """)

    conn.execute("""
        INSERT INTO fact_campanas_marketing (
            sk_campana_evento, sk_cliente, sk_tiempo,
            campana_id, tipo_campana, canal_campana,
            abierto, convertido, descuento_ofrecido
        )
        SELECT 
            ROW_NUMBER() OVER (ORDER BY c.campana_id, c.cliente_id) AS sk_campana_evento,
            dc.sk_cliente,
            dt.sk_tiempo,
            c.campana_id,
            c.tipo_campana,
            c.canal_campana,
            c.abierto,
            c.convertido,
            c.descuento_ofrecido
        FROM clean_campanas_marketing c
        JOIN dim_cliente dc ON c.cliente_id = dc.cliente_id
        JOIN dim_tiempo dt ON c.fecha_envio = dt.fecha;
    """)

    conn.execute("""
        INSERT INTO fact_interacciones_crm (
            sk_interaccion, sk_cliente, sk_tiempo,
            interaccion_id, tipo_interaccion, canal,
            resolucion, tiempo_respuesta_hrs
        )
        SELECT 
            ROW_NUMBER() OVER (ORDER BY i.interaccion_id) AS sk_interaccion,
            dc.sk_cliente,
            dt.sk_tiempo,
            i.interaccion_id,
            i.tipo AS tipo_interaccion,
            i.canal,
            i.resolucion,
            i.tiempo_respuesta_hrs
        FROM clean_interacciones_crm i
        JOIN dim_cliente dc ON i.cliente_id = dc.cliente_id
        JOIN dim_tiempo dt ON i.fecha = dt.fecha;
    """)


if __name__ == "__main__": etl()
