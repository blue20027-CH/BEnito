from .common import supabase


def actualizar_perfil(user_id, datos):
    return supabase.table("perfiles").update(datos).eq("user_id", user_id).execute()


def cerrar_sesion():
    return supabase.auth.sign_out()
