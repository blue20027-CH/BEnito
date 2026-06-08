from .common import supabase


def es_vendedor(usuario):
    perfil = (usuario or {}).get("perfil") or {}
    rol = (perfil.get("rol") or perfil.get("tipo") or perfil.get("modo") or "").lower()
    return "vendedor" in rol


def productos_del_vendedor(nombre_vendedor):
    if not nombre_vendedor:
        return []
    try:
        return supabase.table("productos").select("nombre").eq("creador", nombre_vendedor).execute().data or []
    except Exception as ex:
        print("Error cargando productos de vendedor:", ex)
        return []


def pedidos_comprador(user):
    if not user:
        return []
    try:
        return supabase.table("pedidos").select("*").eq("comprador_id", user.id).order("created_at", desc=True).execute().data or []
    except Exception as ex:
        print("Error cargando pedidos de comprador:", ex)
        return []


def pedidos_vendedor(nombre_vendedor):
    productos = productos_del_vendedor(nombre_vendedor)
    nombres = [p.get("nombre") for p in productos]
    try:
        todos = supabase.table("pedidos").select("*").order("created_at", desc=True).execute().data or []
        return [p for p in todos if any(i.get("nombre") in nombres for i in (p.get("productos") or []))], nombres
    except Exception as ex:
        print("Error cargando pedidos de vendedor:", ex)
        return [], nombres
