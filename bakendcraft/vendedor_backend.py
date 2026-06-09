from datetime import datetime, timezone, timedelta
from .common import supabase, precio_float


def cargar_productos(nombre_vendedor):
    return supabase.table("productos").select("*").eq("creador", nombre_vendedor).execute().data or []


def cargar_pedidos(productos):
    todos = supabase.table("pedidos").select("*").execute().data or []
    nombres = [p.get("nombre") for p in productos]
    return [pedido for pedido in todos if any(item.get("nombre") in nombres for item in (pedido.get("productos") or []))]


def subtotal_vendedor(pedido, productos):
    nombres = [p.get("nombre") for p in productos]
    total = 0.0
    cantidad_total = 0
    for item in pedido.get("productos") or []:
        if item.get("nombre") in nombres:
            cantidad = int(item.get("cantidad", 1) or 1)
            total += precio_float(item.get("precio", 0)) * cantidad
            cantidad_total += cantidad
    return total, cantidad_total


def calcular_stats(pedidos, productos):
    ahora = datetime.now(timezone.utc)
    hace_7 = ahora - timedelta(days=7)
    hace_24 = ahora - timedelta(hours=24)
    semana = reciente = total = 0.0
    for pedido in pedidos:
        subtotal, _ = subtotal_vendedor(pedido, productos)
        total += subtotal
        try:
            fecha = datetime.fromisoformat((pedido.get("created_at") or "").replace("Z", "+00:00"))
            if fecha >= hace_7: semana += subtotal
            if fecha >= hace_24: reciente += subtotal
        except Exception:
            pass
    return semana, reciente, total


def actualizar_estado_pedido(pedido, productos, nuevo_estado):
    nombres = [p.get("nombre") for p in productos]
    actualizados = []
    for item in pedido.get("productos") or []:
        item_actualizado = dict(item)
        if item_actualizado.get("nombre") in nombres:
            item_actualizado["estado"] = nuevo_estado
        actualizados.append(item_actualizado)
    return supabase.table("pedidos").update({"estado": nuevo_estado, "productos": actualizados}).eq("id", pedido.get("id")).execute()


def guardar_producto(datos, producto_id=None):
    if producto_id:
        return supabase.table("productos").update(datos).eq("id", producto_id).execute()
    return supabase.table("productos").insert(datos).execute()


def eliminar_producto(producto_id):
    return supabase.table("productos").delete().eq("id", producto_id).execute()
