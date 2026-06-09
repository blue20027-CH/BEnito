from .common import supabase


def iniciar_sesion(email, password):
    return supabase.auth.sign_in_with_password({"email": email, "password": password})


def cargar_perfil(user_id):
    return supabase.table("perfiles").select("*").eq("user_id", user_id).single().execute().data
