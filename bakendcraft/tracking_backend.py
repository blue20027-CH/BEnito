from .common import supabase


def pedidos_comprador(user):
    if not user: return []
    return supabase.table("pedidos").select("*").eq("comprador_id", user.id).order("created_at", desc=True).execute().data or []


def pedidos_vendedor(nombre_vendedor):
    productos = supabase.table("productos").select("nombre").eq("creador", nombre_vendedor).execute().data or []
    nombres = [p.get("nombre") for p in productos]
    todos = supabase.table("pedidos").select("*").order("created_at", desc=True).execute().data or []
    return [p for p in todos if any(i.get("nombre") in nombres for i in (p.get("productos") or []))], nombres
