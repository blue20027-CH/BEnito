import sys
sys.path.insert(0, '.')
from supabase_client import supabase

try:
    resp = supabase.table("productos").select("*").execute()
    print("Total productos:", len(resp.data))
    if resp.data:
        print("Primer producto:", resp.data[0])
    else:
        print("La tabla está vacía")
except Exception as e:
    print("ERROR:", e)