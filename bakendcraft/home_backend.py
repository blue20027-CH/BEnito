from .common import supabase


def cargar_productos():
    return supabase.table("productos").select("*").execute().data or []


def cargar_favoritos(user):
    if not user:
        return []
    return [r["producto_id"] for r in (supabase.table("favoritos").select("producto_id").eq("user_id", user.id).execute().data or [])]


def guardar_favorito(user, producto_id):
    return supabase.table("favoritos").insert({"user_id": user.id, "producto_id": producto_id}).execute()


def eliminar_favorito(user, producto_id):
    return supabase.table("favoritos").delete().eq("user_id", user.id).eq("producto_id", producto_id).execute()


def cargar_comentarios(producto_id):
    if not producto_id:
        return []
    return supabase.table("comentarios").select("*").eq("producto_id", producto_id).order("created_at", desc=True).limit(20).execute().data or []


def guardar_comentario(producto_id, user, perfil, texto):
    return supabase.table("comentarios").insert({"producto_id": producto_id, "user_id": user.id if user else None, "autor": (perfil or {}).get("nombre", "Visitante"), "texto": texto}).execute()
