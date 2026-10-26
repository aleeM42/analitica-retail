"""Command-line interface and orchestrator for RetailVenture DSS."""

from __future__ import annotations

import argparse
import sys
import time
from typing import Sequence


def run_etl() -> None:
    print("\n" + "=" * 65)
    print(" [1/3] A1: Extracción, Transformación y Carga (ETL) + Auditoría")
    print("=" * 65)
    t0 = time.time()
    from retailventure_dss.etl.etl import etl

    etl()
    print(f"--> ETL completado con éxito en {time.time() - t0:.2f}s")


def run_analytics() -> None:
    print("\n" + "=" * 65)
    print(" [2/3] A2, A3, A4: Modelos Analíticos y Econométricos")
    print("=" * 65)
    t0 = time.time()

    from retailventure_dss.analitycs import (
        clv_churn,
        discount_elasticity,
        fugas,
        marketing_effectiveness,
        rentabilidad,
        return_anomalies,
    )

    print("\n--- Ejecutando A2: Rentabilidad y Estacionalidad ---")
    rentabilidad.run()

    print("\n--- Ejecutando A2: Elasticidad de Descuentos (OLS Efectos Fijos) ---")
    discount_elasticity.run()

    print("\n--- Ejecutando A3: Detección de Anomalías en Devoluciones ---")
    return_anomalies.run()

    print("\n--- Ejecutando A3: Supervivencia Kaplan-Meier (Churn y CLV) ---")
    clv_churn.run()

    print("\n--- Ejecutando A3: Consolidación de Fugas a 6 Meses y Backtest ---")
    fugas.run()

    print("\n--- Ejecutando A4: Efectividad de Marketing, Logit Multivariado y ROI ---")
    marketing_effectiveness.run()

    print(f"\n--> Modelos analíticos finalizados con éxito en {time.time() - t0:.2f}s")


def run_dashboard(host: str = "127.0.0.1", port: int = 8050) -> None:
    print("\n" + "=" * 65)
    print(" [3/3] A5: Dashboard Ejecutivo Interactivo (Storytelling)")
    print("=" * 65)
    from retailventure_dss.interface.dashboard import create_app

    print(f"Servidor Dash iniciado.")
    print(f"Abrí tu navegador en: http://{host}:{port}\n")
    app = create_app()
    app.run(host=host, port=port, debug=False)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="retailventure",
        description="RetailVenture DSS: Pipeline completo de ETL, Analítica y Dashboard Ejecutivo",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--etl-only",
        action="store_true",
        help="Ejecuta únicamente el módulo ETL (A1) y termina.",
    )
    group.add_argument(
        "--analytics-only",
        action="store_true",
        help="Ejecuta únicamente los modelos analíticos (A2, A3, A4) y termina.",
    )
    group.add_argument(
        "--dashboard-only",
        action="store_true",
        help="Inicia directamente el dashboard web (A5) sin re-ejecutar ETL ni analítica.",
    )
    parser.add_argument(
        "--no-dashboard",
        action="store_true",
        help="Ejecuta ETL y analítica completa pero no inicia el servidor web.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8050,
        help="Puerto local para el dashboard de Plotly Dash (por defecto: 8050).",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host para el servidor web (por defecto: 127.0.0.1).",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    t_inicio = time.time()
    print("=" * 65)
    print("   RETAILVENTURE C.A. — DECISION SUPPORT SYSTEM (DSS)")
    print("=" * 65)

    if args.etl_only:
        run_etl()
    elif args.analytics_only:
        run_analytics()
    elif args.dashboard_only:
        run_dashboard(host=args.host, port=args.port)
    else:
        # Flujo completo por defecto
        run_etl()
        run_analytics()
        if not args.no_dashboard:
            run_dashboard(host=args.host, port=args.port)
        else:
            print(f"\nPipeline completo ejecutado en {time.time() - t_inicio:.2f}s.")


if __name__ == "__main__":
    main(sys.argv[1:])
