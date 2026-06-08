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


def calcular_subtotal(carrito):
    return sum(precio_float(p.get("precio", 0)) * p.get("cantidad", 1) for p in carrito if p is not None)


def calcular_resumen(carrito, perfil):
    subtotal = calcular_subtotal(carrito)
    if subtotal <= 0:
        return 0.0, 0.0, 0.0, []
    envio, detalle_envio = calcular_envio(carrito, perfil.get("ubicacion", "Panama"), ubicacion_vendedor)
    return subtotal, envio, subtotal + envio, detalle_envio


def guardar_pedido(carrito, usuario, metodo, datos_pago):
    perfil = usuario.get("perfil") or {}
    user = usuario.get("user")
    subtotal, envio, total, detalle_envio = calcular_resumen(carrito, perfil)
    productos_lista = [{
        "id": p.get("id"), "nombre": p.get("nombre"), "precio": p.get("precio"),
        "cantidad": p.get("cantidad", 1), "creador": p.get("creador"), "img": p.get("img"),
        "categoria": p.get("categoria"), "estado": "pendiente",
    } for p in carrito if p is not None]
    pedido = {
        "comprador_id": user.id if user else None,
        "comprador_nombre": perfil.get("nombre", ""),
        "productos": productos_lista,
        "total": total,
        "metodo_pago": metodo,
        "estado": "pendiente",
        "direccion": perfil.get("ubicacion", ""),
        "telefono": perfil.get("telefono", ""),
        "datos_pago": {**datos_pago, "subtotal": subtotal, "envio": envio, "detalle_envio": detalle_envio},
    }
    supabase.table("pedidos").insert(pedido).execute()
    actualizar_stock_y_notificar(productos_lista)
    return pedido


def actualizar_stock_y_notificar(productos_lista):
    vendedores_notificados = set()
    for item in productos_lista:
        nombre = item.get("nombre")
        cantidad = item.get("cantidad", 1)
        resp = supabase.table("productos").select("id, stock").eq("nombre", nombre).execute()
        if resp.data:
            prod = resp.data[0]
            stock_actual = int(prod.get("stock", 0) or 0)
            supabase.table("productos").update({"stock": max(0, stock_actual - cantidad)}).eq("id", prod["id"]).execute()
        creador = item.get("creador")
        if creador and creador not in vendedores_notificados:
            resp = supabase.table("perfiles").select("user_id").eq("nombre", creador).execute()
            if resp.data:
                supabase.table("notificaciones").insert({
                    "user_id": resp.data[0].get("user_id"),
                    "titulo": "Nueva venta",
                    "mensaje": f"Vendiste {cantidad}x {nombre}. Preparalo para enviarlo antes de 24 horas.",
                    "tipo": "venta",
                    "leida": False,
                }).execute()
                vendedores_notificados.add(creador)
