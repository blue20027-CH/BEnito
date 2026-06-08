from .common import supabase, precio_float
from screens.envio import calcular_envio


def ubicacion_vendedor(nombre):
    try:
        resp = supabase.table("perfiles").select("ubicacion").eq("nombre", nombre).execute()
        if resp.data:
            return resp.data[0].get("ubicacion")
    except Exception as ex:
        print("Error buscando ubicacion del vendedor:", ex)
    return None


def calcular_total(carrito):
    return sum(precio_float(p.get("precio", 0)) * p.get("cantidad", 1) for p in carrito if p is not None)


def calcular_envio_carrito(carrito, ubicacion_comprador):
    subtotal = calcular_total(carrito)
    if subtotal <= 0:
        return 0.0, []
    return calcular_envio(carrito, ubicacion_comprador or "Panama", ubicacion_vendedor)
