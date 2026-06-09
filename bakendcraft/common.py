import sys
from pathlib import Path

CRAFT_ROOT = Path(__file__).resolve().parents[1] / "CraftHub"
if str(CRAFT_ROOT) not in sys.path:
    sys.path.insert(0, str(CRAFT_ROOT))

from supabase_client import supabase


def precio_float(valor):
    try:
        if isinstance(valor, (int, float)):
            return float(valor)
        return float(str(valor).replace("$", "").replace(",", ""))
    except Exception:
        return 0.0
