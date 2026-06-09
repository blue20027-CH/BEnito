from .common import supabase, precio_float
from screens.envio import calcular_envio


def ubicacion_vendedor(nombre):
    resp = supabase.table("perfiles").select("ubicacion").eq("nombre", nombre).execute()
    return resp.data[0].get("ubicacion") if resp.data else None


def calcular_subtotal(carrito):
    return sum(precio_float(p.get("precio", 0)) * p.get("cantidad", 1) for p in carrito if p is not None)


def calcular_resumen(carrito, perfil):
    subtotal = calcular_subtotal(carrito)
    if subtotal <= 0:
        return 0.0, 0.0, 0.0, []
    envio, detalle_envio = calcular_envio(carrito, perfil.get("ubicacion", "Panama"), ubicacion_vendedor)
    return subtotal, envio, subtotal + envio, detalle_envio
