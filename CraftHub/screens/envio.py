import math
import unicodedata
from datetime import datetime, timedelta


PROVINCIAS = {
    "bocas del toro": {"label": "Bocas del Toro", "coord": (9.34, -82.24)},
    "chiriqui": {"label": "Chiriqui", "coord": (8.43, -82.43)},
    "cocle": {"label": "Cocle", "coord": (8.51, -80.36)},
    "colon": {"label": "Colon", "coord": (9.35, -79.90)},
    "darien": {"label": "Darien", "coord": (8.00, -77.88)},
    "herrera": {"label": "Herrera", "coord": (7.84, -80.72)},
    "los santos": {"label": "Los Santos", "coord": (7.93, -80.42)},
    "panama": {"label": "Panama", "coord": (8.98, -79.52)},
    "panama oeste": {"label": "Panama Oeste", "coord": (8.88, -79.78)},
    "veraguas": {"label": "Veraguas", "coord": (8.10, -80.97)},
    "guna yala": {"label": "Guna Yala", "coord": (9.31, -78.23)},
    "ngabe bugle": {"label": "Ngabe Bugle", "coord": (8.63, -81.74)},
    "embera wounaan": {"label": "Embera-Wounaan", "coord": (8.38, -78.10)},
    "madugandi": {"label": "Madugandi", "coord": (9.09, -78.92)},
    "wargandi": {"label": "Wargandi", "coord": (8.95, -78.31)},
}

ALIASES = {
    "panama city": "panama",
    "ciudad de panama": "panama",
    "panam": "panama",
    "panamã¡": "panama",
    "chiriquã­": "chiriqui",
    "colon": "colon",
    "colã³n": "colon",
    "cocle": "cocle",
    "coclã©": "cocle",
    "darien": "darien",
    "dariã©n": "darien",
    "bocas": "bocas del toro",
    "ngabe": "ngabe bugle",
    "ngabe-bugle": "ngabe bugle",
    "ngabe bugle": "ngabe bugle",
    "ngã¤be bugle": "ngabe bugle",
    "embera": "embera wounaan",
    "embera-wounaan": "embera wounaan",
    "emberã¡-wounaan": "embera wounaan",
}


def _limpiar(texto):
    texto = str(texto or "").strip().lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = texto.replace("-", " ").replace("_", " ")
    return " ".join(texto.split())


def normalizar_ubicacion(valor):
    texto = _limpiar(valor)
    if not texto:
        return "panama"
    if texto in ALIASES:
        return ALIASES[texto]
    if texto in PROVINCIAS:
        return texto
    for alias, provincia in ALIASES.items():
        if alias in texto:
            return provincia
    for provincia in PROVINCIAS:
        if provincia in texto:
            return provincia
    return "panama"


def nombre_provincia(valor):
    provincia = normalizar_ubicacion(valor)
    return PROVINCIAS[provincia]["label"]


def distancia_km(origen, destino):
    origen_key = normalizar_ubicacion(origen)
    destino_key = normalizar_ubicacion(destino)
    lat1, lon1 = PROVINCIAS[origen_key]["coord"]
    lat2, lon2 = PROVINCIAS[destino_key]["coord"]
    radio_tierra = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    return radio_tierra * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))


def costo_por_distancia(km, unidades=1):
    unidades = max(1, int(unidades or 1))
    base_operacion = 2.50
    costo_km = km * 0.045
    manejo = max(0, unidades - 1) * 0.75
    recargo_largo = 0
    if km > 260:
        recargo_largo = 2.50
    elif km > 160:
        recargo_largo = 1.25
    costo = base_operacion + costo_km + manejo + recargo_largo
    return round(max(3.00, min(costo, 24.00)), 2)


def estimar_entrega_horas(km, estado="pendiente"):
    estado = (estado or "pendiente").lower()
    if estado == "entregado":
        return 0
    if km <= 25:
        horas = 10
    elif km <= 80:
        horas = 24
    elif km <= 160:
        horas = 40
    elif km <= 280:
        horas = 60
    else:
        horas = 84
    if estado in ["en proceso", "procesando"]:
        horas = max(4, horas - 8)
    elif estado in ["enviado", "en camino"]:
        horas = max(2, horas - 18)
    return int(horas)


def estimar_entrega_fecha(km, estado="pendiente", inicio=None):
    horas = estimar_entrega_horas(km, estado)
    if inicio is None:
        inicio = datetime.now()
    return inicio + timedelta(hours=horas)


def progreso_por_estado(estado):
    estado = (estado or "pendiente").lower()
    if estado in ["entregado", "completado"]:
        return 1.0
    if estado in ["enviado", "en camino"]:
        return 0.68
    if estado in ["en proceso", "procesando"]:
        return 0.35
    return 0.12


def detalle_envio_vendedor(vendedor, productos, ubicacion_comprador, ubicacion_vendedor):
    unidades = sum(int(p.get("cantidad", 1) or 1) for p in productos)
    km = distancia_km(ubicacion_vendedor, ubicacion_comprador)
    costo = costo_por_distancia(km, unidades)
    return {
        "vendedor": vendedor,
        "origen": nombre_provincia(ubicacion_vendedor),
        "destino": nombre_provincia(ubicacion_comprador),
        "distancia_km": round(km, 1),
        "unidades": unidades,
        "costo": costo,
        "eta_horas": estimar_entrega_horas(km),
        "progreso": progreso_por_estado("pendiente"),
    }


def calcular_envio(carrito, ubicacion_comprador, buscar_ubicacion_vendedor=None):
    vendedores = {}
    for producto in carrito:
        if producto is None:
            continue
        vendedor = producto.get("creador") or producto.get("vendedor") or "CraftHub"
        vendedores.setdefault(vendedor, []).append(producto)

    detalles = []
    total = 0.0
    for vendedor, productos in vendedores.items():
        ubicacion_vendedor = None
        if buscar_ubicacion_vendedor:
            ubicacion_vendedor = buscar_ubicacion_vendedor(vendedor)
        ubicacion_vendedor = (
            ubicacion_vendedor
            or productos[0].get("ubicacion_vendedor")
            or productos[0].get("origen")
            or productos[0].get("region")
            or "Panama"
        )
        detalle = detalle_envio_vendedor(
            vendedor,
            productos,
            ubicacion_comprador or "Panama",
            ubicacion_vendedor,
        )
        total += detalle["costo"]
        detalles.append(detalle)

    return round(total, 2), detalles
