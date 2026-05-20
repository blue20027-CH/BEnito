import math

PROVINCIAS = {
    "bocas del toro": (9.34, -82.24),
    "cocle": (8.51, -80.36),
    "colon": (9.35, -79.90),
    "colón": (9.35, -79.90),
    "chiriqui": (8.43, -82.43),
    "chiriquí": (8.43, -82.43),
    "darien": (8.00, -77.88),
    "darién": (8.00, -77.88),
    "herrera": (7.84, -80.72),
    "los santos": (7.93, -80.42),
    "panama": (8.98, -79.52),
    "panamá": (8.98, -79.52),
    "panama oeste": (8.88, -79.78),
    "panamá oeste": (8.88, -79.78),
    "veraguas": (8.10, -80.97),
}


def normalizar_ubicacion(valor):
    texto = (valor or "").strip().lower()
    for provincia in PROVINCIAS:
        if provincia in texto:
            return provincia
    return "panama"


def distancia_km(origen, destino):
    lat1, lon1 = PROVINCIAS[normalizar_ubicacion(origen)]
    lat2, lon2 = PROVINCIAS[normalizar_ubicacion(destino)]
    radio = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    return radio * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))


def costo_por_distancia(km):
    if km <= 25:
        return 3.0
    if km <= 80:
        return 5.0
    if km <= 160:
        return 8.0
    if km <= 280:
        return 12.0
    return 16.0


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
        km = distancia_km(ubicacion_comprador, ubicacion_vendedor)
        costo = costo_por_distancia(km)
        total += costo
        detalles.append(
            {
                "vendedor": vendedor,
                "origen": ubicacion_vendedor,
                "destino": ubicacion_comprador or "Panama",
                "distancia_km": round(km, 1),
                "costo": costo,
            }
        )

    return round(total, 2), detalles
