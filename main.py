"""Root entrypoint to run RetailVenture DSS.

Uso:
    python main.py                 # Ejecuta ETL + Analítica + Dashboard
    python main.py --dashboard-only # Inicia solo el Dashboard web
    python main.py --help          # Muestra todas las opciones
"""

from __future__ import annotations

import sys
from retailventure_dss.cli import main

if __name__ == "__main__":
    main(sys.argv[1:])
