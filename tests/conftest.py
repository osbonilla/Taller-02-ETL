"""
conftest.py
-----------
Agrega el directorio `python/` (raiz de los modulos de la aplicacion) al
sys.path, para poder escribir `from extractors.csv_extractor import ...`
tanto en los tests como dentro de los contenedores Docker (donde
`python/` se copia como WORKDIR /app), sin duplicar codigo ni instalar un
paquete editable adicional.
"""

import sys
from pathlib import Path

PYTHON_DIR = Path(__file__).resolve().parent.parent / "python"
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))
