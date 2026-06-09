from datetime import datetime
from .common import supabase


def subir_imagen_producto(contenido, ext):
    nombre_archivo = f"producto_{datetime.now().strftime('%Y%m%d%H%M%S')}{ext}"
    content_type = "image/jpeg" if ext in [".jpg", ".jpeg"] else "image/png" if ext == ".png" else "image/webp"
    supabase.storage.from_("productos").upload(nombre_archivo, contenido, {"content-type": content_type, "x-upsert": "true"})
    return supabase.storage.from_("productos").get_public_url(nombre_archivo)
