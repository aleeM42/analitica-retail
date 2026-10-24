import pandas as pd

from retailventure_dss.etl.quality_rules import (
    CONSISTENCIA,
    OPORTUNIDAD,
    evaluar_reglas,
)


def outlier_profile(df: pd.DataFrame) -> tuple[int, dict[str, int]]:
    """IQR por columna numérica continua. Devuelve (filas con algún outlier, detalle por columna).

    Cuenta FILAS (no celdas) y omite columnas binarias/discretas (<= 10 valores) o con IQR = 0.
    """
    cols = [c for c in df.select_dtypes(include=["number"]).columns if df[c].dtype != bool]
    marca = pd.Series(False, index=df.index)
    detalle: dict[str, int] = {}
    for col in cols:
        q1, q3 = df[col].quantile([0.25, 0.75])
        iqr = q3 - q1
        if iqr == 0 or df[col].nunique() <= 10:  # binarias/discretas (p. ej. cantidad 1-5) no se evalúan con IQR
            continue
        fuera = (df[col] < q1 - 1.5 * iqr) | (df[col] > q3 + 1.5 * iqr)
        if fuera.any():
            detalle[col] = int(fuera.sum())
            marca |= fuera
    return int(marca.sum()), detalle


def build_quality_report(conn, datasets: list[dict]):
    """datasets: [{nombre, total, rechazados_pydantic, dups, perfil, filas_clean, rechazados}]"""
    auditoria, errores = [], []

    for ds in datasets:
        nombre, total, perfil = ds["nombre"], ds["total"], ds["perfil"]

        # Errores de formato/tipo rechazados por pydantic (ya traían motivo)
        for fila in ds["rechazados"]:
            errores.append(
                {"dataset": nombre, "dimension": "validez/unicidad", "regla": fila.get("motivo_error", "?"),
                 "id": next(iter(fila.values())), "accion": "descartado"}
            )

        # Consistencia
        malos_cons: set = set()
        for regla, accion, ids in evaluar_reglas(conn, CONSISTENCIA.get(nombre, [])):
            malos_cons.update(ids)
            errores += [{"dataset": nombre, "dimension": "consistencia", "regla": regla,
                         "id": i, "accion": accion} for i in ids]

        # Oportunidad (None = no aplica, p. ej. productos no tiene fechas)
        reglas_op = OPORTUNIDAD.get(nombre)
        malos_op: set = set()
        for regla, accion, ids in evaluar_reglas(conn, reglas_op or []):
            malos_op.update(ids)
            errores += [{"dataset": nombre, "dimension": "oportunidad", "regla": regla,
                         "id": i, "accion": accion} for i in ids]

        completitud = (perfil["celdas"] - perfil["nulos"]) / perfil["celdas"] * 100
        unicidad = (total - ds["dups"]) / total * 100
        consistencia = (total - ds["rechazados_pydantic"] - len(malos_cons)) / total * 100
        oportunidad = (total - len(malos_op)) / total * 100 if reglas_op else None

        auditoria.append({
            "dataset": nombre,
            "total_filas": total,
            "celdas_nulas": perfil["nulos"],
            "duplicados_por_id": ds["dups"],
            "filas_con_outliers": perfil["filas_outlier"],
            "outliers_%": round(perfil["filas_outlier"] / total * 100, 2),
            "completitud_%": round(completitud, 2),
            "unicidad_%": round(unicidad, 2),
            "consistencia_%": round(consistencia, 2),
            "oportunidad_%": None if oportunidad is None else round(oportunidad, 2),
            "filas_descartadas": total - ds["filas_clean"],
            "filas_marcadas": len(malos_cons | malos_op),
        })

    return pd.DataFrame(auditoria), pd.DataFrame(errores)
