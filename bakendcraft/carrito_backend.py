from .common import precio_float
from screens.envio import calcular_envio
from .pago_backend import ubicacion_vendedor


def calcular_total(carrito):
    return sum(precio_float(p.get("precio", 0)) * p.get("cantidad", 1) for p in carrito if p is not None)


def calcular_envio_carrito(carrito, ubicacion_comprador):
    if calcular_total(carrito) <= 0:
        return 0.0, []
    return calcular_envio(carrito, ubicacion_comprador or "Panama", ubicacion_vendedor)
