from .common import supabase


def login(email, password):
    return supabase.auth.sign_in_with_password({"email": email, "password": password})


def registrar(email, password):
    return supabase.auth.sign_up({"email": email, "password": password})


def crear_perfil(datos):
    return supabase.table("perfiles").insert(datos).execute()


def cargar_perfil(user_id):
    return supabase.table("perfiles").select("*").eq("user_id", user_id).single().execute().data


def actualizar_perfil(user_id, datos):
    return supabase.table("perfiles").update(datos).eq("user_id", user_id).execute()


def cerrar_sesion():
    return supabase.auth.sign_out()
