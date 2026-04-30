import sys
sys.path.insert(0, '.')
from supabase_client import supabase

try:
    r = supabase.auth.sign_in_with_password({
        'email': 'benitobarsallo7@gmail.com',
        'password': 'benito12'
    })
    print("Usuario:", r.user)
    print("Session:", r.session)
except Exception as e:
    print("ERROR:", e)
    import sys
sys.path.insert(0, '.')
from supabase_client import supabase

try:
    # Paso 1: Login
    r = supabase.auth.sign_in_with_password({
        'email': 'benitobarsallo7@gmail.com',
        'password': 'benito12'
    })
    print("Login OK, user_id:", r.user.id)

    # Paso 2: Buscar perfil
    perfil = supabase.table("perfiles").select("*").eq(
        "user_id", r.user.id).single().execute()
    print("Perfil:", perfil.data)

except Exception as e:
    print("ERROR:", e)