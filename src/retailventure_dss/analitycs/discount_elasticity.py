"""A2 (parte 2): ¿los descuentos generan volumen suficiente para compensar el margen?

Ejecutar: python -m retailventure_dss.analitycs.discount_elasticity

"""

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from retailventure_dss.analitycs._base import cargar_ventas, guardar

MODULO = "descuentos"
BINS = [-0.001, 0.0, 0.05, 0.10, 0.15, 0.20, 1.0]
ETIQUETAS = ["0%", "0-5%", "5-10%", "10-15%", "15-20%", ">20%"]


def preparar(ventas: pd.DataFrame) -> pd.DataFrame:
    v = ventas.copy()
    v["tramo"] = pd.cut(v["descuento"], bins=BINS, labels=ETIQUETAS)
    v["bruto"] = v["precio_unitario"] * v["cantidad"]
    v["descuento_usd"] = v["bruto"] * v["descuento"]
    # margen que se habría obtenido SIN descuento, con la misma cantidad
    v["margen_sin_descuento"] = v["bruto"] - v["costo"] * v["cantidad"]
    return v


def resumen_por_tramo(v: pd.DataFrame) -> pd.DataFrame:
    """Compara cada tramo de descuento contra el uplift de volumen que haría falta
    para empatar el margen en dólares.

    uplift requerido = margen sin descuento / margen con descuento - 1
    (si vendo 'uplift' % más unidades con el descuento, recupero el margen que cedí).
    """
    g = v.groupby("tramo", observed=True).agg(
        transacciones=("transaccion_id", "size"),
        descuento_medio=("descuento", "mean"),
        cantidad_media=("cantidad", "mean"),
        ticket_medio=("monto_neto", "mean"),
        margen_medio=("margen", "mean"),
        margen_total=("margen", "sum"),
        descuento_usd=("descuento_usd", "sum"),
        margen_sin_desc=("margen_sin_descuento", "sum"),
    )
    g["margen_pct"] = g["margen_total"] / v.groupby("tramo", observed=True)["monto_neto"].sum()
    g["uplift_requerido_pct"] = (g["margen_sin_desc"] / g["margen_total"] - 1) * 100
    base = g.loc["0%", "cantidad_media"]
    g["uplift_observado_pct"] = (g["cantidad_media"] / base - 1) * 100
    g.loc["0%", "uplift_requerido_pct"] = 0.0
    return g.reset_index()


def efecto_sobre_volumen(v: pd.DataFrame) -> pd.DataFrame:
    """Regresión de la cantidad sobre el tramo de descuento, con efectos fijos de
    producto (compara el MISMO producto con y sin descuento) y errores robustos.

    Limitación declarada: es observacional. Se verifica abajo que el descuento no se
    asigna según el tipo de cliente o producto (balance); si se asignara en función de
    la demanda esperada, el coeficiente estaría sesgado.
    """
    modelo = smf.ols(
        "cantidad ~ C(tramo, Treatment('0%')) + C(producto_id)", data=v
    ).fit(cov_type="HC1")
    ci = modelo.conf_int()
    filas = []
    base = v.loc[v["tramo"] == "0%", "cantidad"].mean()
    for nombre in modelo.params.index:
        if nombre.startswith("C(tramo"):
            tramo = nombre.split("T.")[1].rstrip("]")
            filas.append(
                {
                    "tramo": tramo,
                    "efecto_unidades": modelo.params[nombre],
                    "ic95_inf_unidades": ci.loc[nombre, 0],
                    "ic95_sup_unidades": ci.loc[nombre, 1],
                    "efecto_pct_sobre_base": modelo.params[nombre] / base * 100,
                    "ic95_sup_pct": ci.loc[nombre, 1] / base * 100,
                    "p_valor": modelo.pvalues[nombre],
                }
            )
    return pd.DataFrame(filas)


def balance_asignacion(v: pd.DataFrame) -> pd.DataFrame:
    """¿Quién recibe descuentos? Descuento medio y % de transacciones con descuento."""
    filas = []
    for dim in ["canal", "segmento", "categoria", "metodo_pago", "canal_adquisicion"]:
        g = v.groupby(dim).agg(
            descuento_medio=("descuento", "mean"),
            pct_con_descuento=("descuento", lambda s: (s > 0).mean() * 100),
            descuento_usd=("descuento_usd", "sum"),
            bruto=("bruto", "sum"),
            margen=("margen", "sum"),
        )
        g["descuento_pct_del_bruto"] = g["descuento_usd"] / g["bruto"] * 100
        g["descuento_pct_del_margen_potencial"] = g["descuento_usd"] / (g["margen"] + g["descuento_usd"]) * 100
        g = g.reset_index().rename(columns={dim: "valor"})
        g.insert(0, "dimension", dim)
        filas.append(g)
    return pd.concat(filas, ignore_index=True)


def costo_total(v: pd.DataFrame) -> pd.DataFrame:
    total_desc = v["descuento_usd"].sum()
    return pd.DataFrame(
        [
            {
                "descuento_total_usd": total_desc,
                "pct_del_ingreso_bruto": total_desc / v["bruto"].sum() * 100,
                "margen_real_usd": v["margen"].sum(),
                "margen_potencial_sin_descuentos_usd": v["margen"].sum() + total_desc,
                "descuento_pct_del_margen_potencial": total_desc / (v["margen"].sum() + total_desc) * 100,
            }
        ]
    )


def run() -> dict[str, pd.DataFrame]:
    v = preparar(cargar_ventas())
    res = {
        "descuentos_por_tramo": resumen_por_tramo(v),
        "efecto_volumen_efectos_fijos": efecto_sobre_volumen(v),
        "quien_recibe_descuentos": balance_asignacion(v),
        "costo_total_descuentos": costo_total(v),
    }
    for nombre, df in res.items():
        guardar(df, MODULO, nombre)
    return res


if __name__ == "__main__":
    pd.set_option("display.width", 220, "display.max_columns", 30)
    for nombre, df in run().items():
        print(f"\n=== {nombre} ===")
        print(df.round(3).to_string(index=False))
