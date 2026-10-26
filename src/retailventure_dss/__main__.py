"""Module entrypoint: allows running 'python -m retailventure_dss'."""

from __future__ import annotations

import sys
from retailventure_dss.cli import main

if __name__ == "__main__":
    main(sys.argv[1:])
