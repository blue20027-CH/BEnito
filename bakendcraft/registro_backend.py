from .common import supabase


def registrar_usuario(email, password):
    return supabase.auth.sign_up({"email": email, "password": password})


def crear_perfil(datos):
    return supabase.table("perfiles").insert(datos).execute()
