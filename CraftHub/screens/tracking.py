import flet as ft
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supabase_client import supabase
from screens.componentes import craft_logo, tabler_icon
from screens.envio import progreso_por_estado, estimar_entrega_horas

BRAND = "#941515"
TEXT = "#1F1F1F"
MUTED = "#777777"
BORDER = "#E5DADA"
BG = "#FAFAFA"
MAP_BG = "#AFCFE0"

PIN_POS = {
    "bocas del toro": (86, 238), "chiriqui": (50, 326), "veraguas": (162, 330),
    "los santos": (214, 382), "herrera": (210, 326), "cocle": (290, 300),
    "panama oeste": (354, 284), "panama": (410, 254), "colon": (382, 206),
    "guna yala": (518, 244), "darien": (622, 350), "embera wounaan": (578, 292),
}


def _precio(valor):
    try:
        return float(valor) if isinstance(valor, (int, float)) else float(str(valor).replace("$", "").replace(",", ""))
    except Exception:
        return 0.0


def _normalizar(texto):
    texto = str(texto or "").strip().lower()
    for a, b in {"panamá": "panama", "colón": "colon", "coclé": "cocle", "darién": "darien", "chiriquí": "chiriqui", "guna": "guna yala", "emberá": "embera"}.items():
        texto = texto.replace(a, b)
    return " ".join(texto.replace("-", " ").split())


def _provincia(texto):
    limpio = _normalizar(texto)
    for key in PIN_POS:
        if key in limpio:
            return key
    if "panama city" in limpio or "ciudad de panama" in limpio:
        return "panama"
    return "panama"


def _estado_key(pedido, item=None):
    estado = item.get("estado") if item else None
    return (estado or pedido.get("estado") or "pendiente").lower()


def _estado_label(estado):
    estado = (estado or "pendiente").lower()
    if estado in ["entregado", "completado"]:
        return "Completado"
    if estado in ["enviado", "en camino"]:
        return "En camino"
    return "Procesando"


def _producto_count(pedido, nombres_vendedor=None):
    productos = pedido.get("productos") or []
    if nombres_vendedor:
        productos = [p for p in productos if p.get("nombre") in nombres_vendedor]
    return sum(int(i.get("cantidad", 1) or 1) for i in productos)


def _detalle_envio(pedido, item=None):
    datos = pedido.get("datos_pago") or {}
    detalles = datos.get("detalle_envio") or []
    vendedor = (item or {}).get("creador") or (item or {}).get("vendedor")
    if vendedor:
        for detalle in detalles:
            if detalle.get("vendedor") == vendedor:
                return detalle
    return detalles[0] if detalles else {}


def _primer_item(pedido, nombres_vendedor=None):
    productos = pedido.get("productos") or []
    if nombres_vendedor:
        productos = [p for p in productos if p.get("nombre") in nombres_vendedor]
    return productos[0] if productos else {}


def _es_vendedor(usuario):
    perfil = (usuario or {}).get("perfil") or {}
    rol = (perfil.get("rol") or perfil.get("tipo") or perfil.get("modo") or "").lower()
    return "vendedor" in rol


def _header(ir_back):
    return ft.Container(height=58, bgcolor="white", border=ft.border.only(bottom=ft.BorderSide(1, "#D6B4B4")), padding=ft.padding.symmetric(horizontal=28), content=ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[ft.Row(spacing=18, controls=[ft.Container(width=34, height=34, border_radius=17, alignment=ft.Alignment(0, 0), on_click=lambda _: ir_back(), content=tabler_icon("arrow-left", size=22)), ft.Text("Mapa de seguimiento", size=18, color=BRAND, weight=ft.FontWeight.BOLD)]), craft_logo(36)]))


def _pin(left, top, active=False):
    return ft.Container(left=left, top=top, width=26, height=26, border_radius=13, bgcolor="#111111" if active else BRAND, alignment=ft.Alignment(0, 0), shadow=ft.BoxShadow(blur_radius=8, color="#00000035", offset=ft.Offset(0, 2)), content=tabler_icon("map-pin", size=17))


def _mapa(pedido, nombres_vendedor=None):
    item = _primer_item(pedido or {}, nombres_vendedor)
    detalle = _detalle_envio(pedido or {}, item)
    origen = _provincia(detalle.get("origen") or item.get("region") or item.get("ubicacion_vendedor"))
    destino = _provincia(detalle.get("destino") or (pedido or {}).get("direccion"))
    ox, oy = PIN_POS.get(origen, PIN_POS["panama"])
    dx, dy = PIN_POS.get(destino, PIN_POS["panama"])
    return ft.Container(expand=True, height=500, border_radius=12, bgcolor=MAP_BG, clip_behavior=ft.ClipBehavior.HARD_EDGE, border=ft.border.all(1, "#9AC4D8"), shadow=ft.BoxShadow(blur_radius=10, color="#00000018", offset=ft.Offset(0, 4)), content=ft.Stack(controls=[
        ft.Container(left=-10, top=214, width=704, height=184, border_radius=88, bgcolor="#EEF0E2"),
        ft.Container(left=42, top=248, width=110, height=72, border_radius=44, bgcolor="#F7F5E7"),
        ft.Container(left=132, top=270, width=170, height=94, border_radius=54, bgcolor="#F7F5E7"),
        ft.Container(left=258, top=235, width=184, height=86, border_radius=50, bgcolor="#F7F5E7"),
        ft.Container(left=410, top=208, width=160, height=70, border_radius=42, bgcolor="#F7F5E7"),
        ft.Container(left=510, top=252, width=170, height=118, border_radius=58, bgcolor="#F7F5E7"),
        ft.Container(left=56, top=306, content=ft.Text("David", size=12, color="#333333")), ft.Container(left=206, top=352, content=ft.Text("Santiago", size=12, color="#333333")),
        ft.Container(left=382, top=246, content=ft.Text("Panama City", size=12, color="#333333")), ft.Container(left=360, top=206, content=ft.Text("Colon", size=12, color="#333333")),
        ft.Container(left=534, top=312, content=ft.Text("La Palma", size=12, color="#333333")), ft.Container(left=226, top=304, content=ft.Text("Panama", size=22, color=TEXT, weight=ft.FontWeight.BOLD)),
        ft.Container(left=min(ox, dx) + 13, top=min(oy, dy) + 13, width=max(8, abs(dx - ox)), height=5, border_radius=3, bgcolor="#D6AAAA"),
        ft.Container(left=min(ox, dx) + 13, top=min(oy, dy) + 13, width=max(8, abs(dx - ox)) * progreso_por_estado(_estado_key(pedido or {}, item)), height=5, border_radius=3, bgcolor=BRAND),
        *[_pin(x, y) for x, y in PIN_POS.values()], _pin(ox, oy, True), _pin(dx, dy, False),
    ]))


def _pasos(estado_key):
    progreso = progreso_por_estado(estado_key)
    pasos = [("Procesando", 0.12, "check"), ("En camino", 0.68, "truck-delivery"), ("Entregado", 1.0, "package")]
    controles = []
    for i, (label, punto, icono) in enumerate(pasos):
        activo = progreso >= punto
        controles.append(ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8, controls=[ft.Container(width=30, height=30, border_radius=15, bgcolor="white" if activo else "#C47C7C", alignment=ft.Alignment(0, 0), content=tabler_icon(icono, size=16)), ft.Text(label, size=10, color="white", weight=ft.FontWeight.BOLD if activo else ft.FontWeight.NORMAL)]))
        if i < len(pasos) - 1:
            controles.append(ft.Container(expand=True, height=4, margin=ft.margin.only(top=14), border_radius=2, bgcolor="white" if progreso >= pasos[i + 1][1] else "#D99999"))
    return ft.Row(spacing=8, controls=controles)


def _pedido_card(pedido, activo=False, on_click=None, nombres_vendedor=None, vendedor=False):
    item = _primer_item(pedido, nombres_vendedor)
    detalle = _detalle_envio(pedido, item)
    estado_key = _estado_key(pedido, item)
    km = float(detalle.get("distancia_km") or 30)
    eta = int(detalle.get("eta_horas") or estimar_entrega_horas(km, estado_key))
    nombre = pedido.get("comprador_nombre") or "Cliente"
    destino = pedido.get("direccion") or detalle.get("destino") or "Destino"
    productos = _producto_count(pedido, nombres_vendedor)
    badge_bg = "#BEF2C0" if estado_key == "entregado" else "#F8E76E"
    return ft.Container(bgcolor="white", border_radius=18, border=ft.border.all(1, BRAND if activo else BORDER), clip_behavior=ft.ClipBehavior.HARD_EDGE, shadow=ft.BoxShadow(blur_radius=12, color="#00000018", offset=ft.Offset(0, 4)), on_click=on_click, content=ft.Column(spacing=0, controls=[
        ft.Container(padding=ft.padding.only(left=20, right=18, top=16, bottom=12), content=ft.Column(spacing=8, controls=[
            ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[ft.Text(nombre if vendedor else (item.get("nombre") or "Mi pedido"), size=16, color=TEXT, weight=ft.FontWeight.BOLD), ft.Text("Productos: " + str(productos), size=12, color=BRAND, weight=ft.FontWeight.BOLD)]),
            ft.Row(spacing=8, controls=[tabler_icon("map-pin", size=16), ft.Text(destino, size=12, color=TEXT, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS)]),
            ft.Container(border_radius=14, bgcolor=badge_bg, padding=ft.padding.symmetric(horizontal=12, vertical=4), content=ft.Text(_estado_label(estado_key), size=11, color=TEXT, weight=ft.FontWeight.BOLD)),
        ])),
        ft.Container(visible=activo, bgcolor=BRAND, padding=ft.padding.symmetric(horizontal=28, vertical=16), content=ft.Column(spacing=12, controls=[ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[ft.Text("Seguimiento en vivo", color="white", size=13, weight=ft.FontWeight.BOLD), ft.Text("Tiempo aprox.: " + str(eta) + " h", color="white", size=11, weight=ft.FontWeight.BOLD)]), _pasos(estado_key)])),
    ]))


def _producto_linea(item):
    cantidad = int(item.get("cantidad", 1) or 1)
    precio = _precio(item.get("precio", 0))
    return ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[ft.Row(spacing=10, controls=[tabler_icon("shopping-bag", size=16), ft.Text((item.get("nombre", "Producto") + " x" + str(cantidad)), size=12, color=TEXT)]), ft.Text("$" + format(precio * cantidad, ".2f"), size=12, color=BRAND, weight=ft.FontWeight.BOLD)])


def show_tracking(page: ft.Page, usuario, ir_back, pedido=None):
    page.clean()
    user = (usuario or {}).get("user")
    perfil = (usuario or {}).get("perfil") or {}
    vendedor = _es_vendedor(usuario)
    nombre_vendedor = perfil.get("nombre", "")
    nombres_productos = []
    pedidos = []
    try:
        if vendedor and nombre_vendedor:
            productos = supabase.table("productos").select("nombre").eq("creador", nombre_vendedor).execute().data or []
            nombres_productos = [p.get("nombre") for p in productos]
            todos = supabase.table("pedidos").select("*").order("created_at", desc=True).execute().data or []
            for ped in todos:
                if any(i.get("nombre") in nombres_productos for i in (ped.get("productos") or [])):
                    pedidos.append(ped)
        elif pedido:
            pedidos = [pedido]
        elif user:
            pedidos = supabase.table("pedidos").select("*").eq("comprador_id", user.id).order("created_at", desc=True).execute().data or []
    except Exception as ex:
        print("Error cargando tracking:", ex)

    seleccionado = {"pedido": pedidos[0] if pedidos else None}
    lista_ref = ft.Ref[ft.Column]()
    mapa_ref = ft.Ref[ft.Container]()
    productos_ref = ft.Ref[ft.Column]()
    search_ref = ft.Ref[ft.TextField]()
    contador_ref = ft.Ref[ft.Row]()

    def productos_visibles(ped):
        items = ped.get("productos") or []
        return [i for i in items if i.get("nombre") in nombres_productos] if vendedor else items

    def pedidos_filtrados():
        term = ((search_ref.current.value if search_ref.current else "") or "").strip().lower()
        if not term:
            return pedidos
        return [p for p in pedidos if term in (p.get("comprador_nombre") or "").lower() or term in (p.get("direccion") or "").lower() or any(term in (i.get("nombre") or "").lower() for i in productos_visibles(p))]

    def _contador(texto, valor):
        return ft.Container(expand=True, height=28, border_radius=14, border=ft.border.all(1, BORDER), alignment=ft.Alignment(0, 0), content=ft.Text(texto + ": " + str(valor), size=10, color=BRAND if "completados" in texto else TEXT, weight=ft.FontWeight.BOLD))

    def pintar():
        actuales = pedidos_filtrados()
        actual = seleccionado["pedido"]
        if actual not in actuales:
            actual = actuales[0] if actuales else None
            seleccionado["pedido"] = actual
        if mapa_ref.current:
            mapa_ref.current.content = _mapa(actual, nombres_productos if vendedor else None) if actual else ft.Container(expand=True, alignment=ft.Alignment(0, 0), content=ft.Text("No hay pedidos para mostrar.", color=MUTED))
        if lista_ref.current:
            lista_ref.current.controls = [_pedido_card(p, activo=actual and p.get("id") == actual.get("id"), on_click=lambda _, ped=p: seleccionar(ped), nombres_vendedor=nombres_productos if vendedor else None, vendedor=vendedor) for p in actuales] or [ft.Container(padding=40, alignment=ft.Alignment(0, 0), content=ft.Text("Sin pedidos.", color=MUTED))]
        if productos_ref.current:
            productos_ref.current.controls = [_producto_linea(i) for i in productos_visibles(actual or {})]
        if contador_ref.current:
            completados = len([p for p in pedidos if (p.get("estado") or "").lower() == "entregado"])
            pendientes = max(0, len(pedidos) - completados)
            contador_ref.current.controls = [_contador("Pedidos completados", completados), _contador("Pedidos nuevos", pendientes)]
        page.update()

    def seleccionar(ped):
        seleccionado["pedido"] = ped
        pintar()

    page.add(ft.Column(expand=True, spacing=0, controls=[_header(ir_back), ft.Container(expand=True, bgcolor=BG, padding=ft.padding.all(36), content=ft.Row(spacing=28, vertical_alignment=ft.CrossAxisAlignment.START, controls=[
        ft.Container(ref=mapa_ref, expand=True, content=_mapa(seleccionado["pedido"], nombres_productos if vendedor else None) if seleccionado["pedido"] else ft.Container(expand=True, alignment=ft.Alignment(0, 0), content=ft.Text("No hay pedidos para mostrar.", color=MUTED))),
        ft.Container(width=420, content=ft.Column(spacing=14, controls=[
            ft.TextField(ref=search_ref, hint_text="Buscar...", height=40, border_radius=20, border_color="#D6B4B4", focused_border_color=BRAND, bgcolor="white",  prefix_icon=ft.Icon(ft.Icons.SEARCH), on_change=lambda _: pintar()),
            ft.Row(ref=contador_ref, spacing=12, controls=[]),
            ft.Column(ref=lista_ref, spacing=16, scroll=ft.ScrollMode.AUTO, controls=[]),
            ft.Container(bgcolor="white", border_radius=16, border=ft.border.all(1, BORDER), padding=18, content=ft.Column(spacing=10, controls=[ft.Text("Productos del pedido", size=15, color=TEXT, weight=ft.FontWeight.BOLD), ft.Column(ref=productos_ref, spacing=8, controls=[])])),
        ])),
    ]))]))
    pintar()
