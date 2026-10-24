"""Reglas de calidad de datos (A1). Cada regla es una consulta que devuelve los IDs que la violan."""

VENTANA_INI = "2023-01-01"   # 24 meses de historia (enunciado)
VENTANA_FIN = "2024-12-31"
PLAZO_DEVOLUCION_DIAS = 30   # supuesto: máximo observado en los datos
SLA_RESPUESTA_HRS = 72       # supuesto de negocio para CRM

# (nombre_regla, sql, accion)   accion: "descartar" (la limpieza elimina la fila) o "marcar" (se conserva)
CONSISTENCIA = {
    "clientes": [
        ("Edad fuera de rango 18-100",
         "SELECT cliente_id FROM stg_clientes WHERE edad < 18 OR edad > 100", "marcar"),
    ],
    "productos": [
        ("Precio de lista menor al costo",
         "SELECT producto_id FROM stg_productos WHERE precio_lista < costo", "descartar"),
        ("margen_bruto_pct no coincide con (precio-costo)/precio",
         "SELECT producto_id FROM stg_productos "
         "WHERE ABS((precio_lista - costo) / NULLIF(precio_lista, 0) * 100 - margen_bruto_pct) > 0.2", "marcar"),
    ],
    "transacciones": [
        ("Cliente inexistente",
         "SELECT t.transaccion_id FROM stg_transacciones t "
         "LEFT JOIN stg_clientes c ON c.cliente_id = t.cliente_id WHERE c.cliente_id IS NULL", "descartar"),
        ("Producto inexistente",
         "SELECT t.transaccion_id FROM stg_transacciones t "
         "LEFT JOIN stg_productos p ON p.producto_id = t.producto_id WHERE p.producto_id IS NULL", "descartar"),
        ("Compra anterior a la fecha de registro del cliente",
         "SELECT t.transaccion_id FROM stg_transacciones t "
         "JOIN stg_clientes c ON c.cliente_id = t.cliente_id WHERE t.fecha < c.fecha_registro", "marcar"),
        ("monto_neto no coincide con cantidad*precio*(1-descuento)",
         "SELECT transaccion_id FROM stg_transacciones "
         "WHERE ABS(monto_neto - cantidad * precio_unitario * (1 - descuento)) > 0.02", "marcar"),
    ],
    "devoluciones": [
        ("Transacción de origen inexistente",
         "SELECT d.devolucion_id FROM stg_devoluciones d "
         "LEFT JOIN stg_transacciones t ON t.transaccion_id = d.transaccion_id WHERE t.transaccion_id IS NULL", "descartar"),
        ("Cliente distinto al de la transacción",
         "SELECT d.devolucion_id FROM stg_devoluciones d "
         "JOIN stg_transacciones t ON t.transaccion_id = d.transaccion_id WHERE t.cliente_id <> d.cliente_id", "descartar"),
        ("Devolución anterior a la compra",
         "SELECT d.devolucion_id FROM stg_devoluciones d "
         "JOIN stg_transacciones t ON t.transaccion_id = d.transaccion_id WHERE d.fecha_devolucion < t.fecha", "marcar"),
        ("Monto devuelto mayor al monto de la compra",
         "SELECT d.devolucion_id FROM stg_devoluciones d "
         "JOIN stg_transacciones t ON t.transaccion_id = d.transaccion_id WHERE d.monto_devuelto > t.monto_neto + 0.01", "marcar"),
    ],
    "campanas_marketing": [
        ("Cliente inexistente",
         "SELECT m.campana_id FROM stg_campanas_marketing m "
         "LEFT JOIN stg_clientes c ON c.cliente_id = m.cliente_id WHERE c.cliente_id IS NULL", "descartar"),
        ("Campaña enviada antes del registro del cliente",
         "SELECT m.campana_id FROM stg_campanas_marketing m "
         "JOIN stg_clientes c ON c.cliente_id = m.cliente_id WHERE m.fecha_envio < c.fecha_registro", "marcar"),
        ("Convertida sin haber sido abierta",
         "SELECT campana_id FROM stg_campanas_marketing WHERE convertido AND NOT abierto", "marcar"),
        ("Convertida sin ninguna compra del cliente posterior al envío",
         "SELECT m.campana_id FROM stg_campanas_marketing m WHERE m.convertido AND NOT EXISTS ("
         "SELECT 1 FROM stg_transacciones t WHERE t.cliente_id = m.cliente_id AND t.fecha >= m.fecha_envio)", "marcar"),
    ],
    "interacciones_crm": [
        ("Cliente inexistente",
         "SELECT i.interaccion_id FROM stg_interacciones_crm i "
         "LEFT JOIN stg_clientes c ON c.cliente_id = i.cliente_id WHERE c.cliente_id IS NULL", "descartar"),
        ("Interacción anterior al registro del cliente",
         "SELECT i.interaccion_id FROM stg_interacciones_crm i "
         "JOIN stg_clientes c ON c.cliente_id = i.cliente_id WHERE i.fecha < c.fecha_registro", "marcar"),
    ],
}

_FUERA = "NOT BETWEEN DATE '{ini}' AND DATE '{fin}'".format(ini=VENTANA_INI, fin=VENTANA_FIN)

# (nombre_regla, sql) -> filas "no oportunas". Productos no tiene fecha: oportunidad no aplica.
OPORTUNIDAD = {
    "clientes": [("Fecha de registro fuera de la ventana de 24 meses",
                  f"SELECT cliente_id FROM stg_clientes WHERE fecha_registro {_FUERA}")],
    "transacciones": [("Fecha fuera de la ventana de 24 meses",
                       f"SELECT transaccion_id FROM stg_transacciones WHERE fecha {_FUERA}")],
    "devoluciones": [
        ("Fecha fuera de la ventana de 24 meses",
         f"SELECT devolucion_id FROM stg_devoluciones WHERE fecha_devolucion {_FUERA}"),
        (f"Devolución después de {PLAZO_DEVOLUCION_DIAS} días de la compra",
         "SELECT d.devolucion_id FROM stg_devoluciones d JOIN stg_transacciones t "
         f"ON t.transaccion_id = d.transaccion_id WHERE (d.fecha_devolucion - t.fecha) > {PLAZO_DEVOLUCION_DIAS}"),
    ],
    "campanas_marketing": [("Fecha de envío fuera de la ventana de 24 meses",
                            f"SELECT campana_id FROM stg_campanas_marketing WHERE fecha_envio {_FUERA}")],
    "interacciones_crm": [
        ("Fecha fuera de la ventana de 24 meses",
         f"SELECT interaccion_id FROM stg_interacciones_crm WHERE fecha {_FUERA}"),
        (f"Respuesta tardía (> {SLA_RESPUESTA_HRS} h)",
         f"SELECT interaccion_id FROM stg_interacciones_crm WHERE tiempo_respuesta_hrs > {SLA_RESPUESTA_HRS}"),
    ],
}


def evaluar_reglas(conn, reglas):
    """Ejecuta las reglas y devuelve [(regla, accion, [ids])]."""
    salida = []
    for regla in reglas:
        nombre, sql = regla[0], regla[1]
        accion = regla[2] if len(regla) > 2 else "marcar"
        ids = [fila[0] for fila in conn.execute(sql).fetchall()]
        salida.append((nombre, accion, ids))
    return salida
