from .common import supabase


def pedidos_comprador(user):
    if not user:
        return []
    try:
        return supabase.table("pedidos").select("*").eq("comprador_id", user.id).order("created_at", desc=True).execute().data or []
    except Exception as ex:
        print("Error cargando notificaciones comprador:", ex)
        return []


def pedidos_vendedor(nombre_vendedor):
    try:
        productos = supabase.table("productos").select("nombre").eq("creador", nombre_vendedor).execute().data or []
        nombres = [p.get("nombre") for p in productos]
        todos = supabase.table("pedidos").select("*").order("created_at", desc=True).execute().data or []
        return [pedido for pedido in todos if any(item.get("nombre") in nombres for item in (pedido.get("productos") or []))]
    except Exception as ex:
        print("Error cargando notificaciones vendedor:", ex)
        return []
