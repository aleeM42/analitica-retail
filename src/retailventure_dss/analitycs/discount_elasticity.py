import pandas as pd
import statsmodels.api as sm
from retailventure_dss.data_access.duckdb_conn import SingletonDbConnection


def analyze_discount_impact() -> dict:
    conn = SingletonDbConnection.get_connection()

    query = """
    SELECT 
        t.transaccion_id,
        COALESCE(c.descuento_ofrecido, t.descuento, 0.0) AS descuento,
        t.cantidad,
        t.precio_unitario,
        t.monto_neto,
        p.costo,
        (t.monto_neto - (p.costo * t.cantidad)) AS margen_bruto_dolares,
        ((t.monto_neto - (p.costo * t.cantidad)) / NULLIF(t.monto_neto, 0)) AS margen_bruto_pct
    FROM clean_transacciones t
    JOIN clean_productos p ON t.producto_id = p.producto_id
    LEFT JOIN clean_campanas_marketing c ON t.cliente_id = c.cliente_id
    WHERE t.monto_neto > 0
    """

    df = conn.execute(query).fetchdf()

    if df["descuento"].std() > 0:
        X = sm.add_constant(df["descuento"])
        y_volumen = df["cantidad"]
        y_margen = df["margen_bruto_dolares"]

        model_volumen = sm.OLS(y_volumen, X).fit()
        model_margen = sm.OLS(y_margen, X).fit()

        coef_cant = model_volumen.params["descuento"]
        coef_marg = model_margen.params["descuento"]
        pval_marg = model_margen.pvalues["descuento"]
    else:
        coef_cant, coef_marg, pval_marg = 0.0, 0.0, 1.0

    # Resumen por tramos de descuento
    df["tramo_descuento"] = pd.cut(
        df["descuento"],
        bins=[-0.01, 0.0, 0.10, 0.20, 0.30, 1.0],
        labels=["Sin Descuento", "1-10%", "11-20%", "21-30%", ">30%"],
    )

    resumen_tramos = (
        df.groupby("tramo_descuento", observed=False)
        .agg(
            total_transacciones=("transaccion_id", "count"),
            cantidad_promedio=("cantidad", "mean"),
            monto_neto_promedio=("monto_neto", "mean"),
            margen_promedio_dolares=("margen_bruto_dolares", "mean"),
            margen_promedio_pct=("margen_bruto_pct", "mean"),
        )
        .reset_index()
    )

    return {
        "resumen_tramos": resumen_tramos,
        "coef_efecto_descuento_en_cantidad": coef_cant,
        "coef_efecto_descuento_en_margen": coef_marg,
        "pvalue_margen": pval_marg,
    }


if __name__ == "__main__":
    resultado = analyze_discount_impact()
    print("--- Resumen por Tramos de Descuento ---")
    print(resultado["resumen_tramos"])
    print(
        f"\nCoeficiente Descuento -> Margen ($): {resultado['coef_efecto_descuento_en_margen']:.2f}"
    )
