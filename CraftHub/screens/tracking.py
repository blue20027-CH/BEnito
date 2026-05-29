import flet as ft
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supabase_client import supabase
from screens.componentes import craft_logo, tabler_icon
from screens.envio import progreso_por_estado, estimar_entrega_horas

BRAND = "#941515"
BRAND_DARK = "#760F0F"
TEXT = "#1F1F1F"
MUTED = "#777777"
BORDER = "#E5DADA"
BG = "#FAFAFA"


def _precio(valor):
    try:
        if isinstance(valor, (int, float)):
            return float(valor)
        return float(str(valor).replace("$", "").replace(",", ""))
    except Exception:
        return 0.0


def _estado(pedido, item=None):
    estado = None
    if item:
        estado = item.get("estado")
    estado = estado or pedido.get("estado") or "pendiente"
    estado = estado.lower()
    if estado == "pendiente":
        return "Preparando"
    if estado == "en proceso":
        return "Procesando"
    if estado == "enviado":
        return "En camino"
    if estado == "entregado":
        return "Entregado"
    return estado.capitalize()


def _estado_key(pedido, item=None):
    estado = None
    if item:
        estado = item.get("estado")
    return (estado or pedido.get("estado") or "pendiente").lower()


def _producto_count(pedido):
    return sum(int(i.get("cantidad", 1) or 1) for i in (pedido.get("productos") or []))


def _primer_producto(pedido):
    productos = pedido.get("productos") or []
    return productos[0] if productos else {}


def _detalle_envio(pedido):
    datos = pedido.get("datos_pago") or {}
    detalles = datos.get("detalle_envio") or []
    return detalles[0] if detalles else {}


def _header(ir_back):
    return ft.Container(
        height=58,
        bgcolor="white",
        border=ft.border.only(bottom=ft.BorderSide(1, "#D6B4B4")),
        padding=ft.padding.symmetric(horizontal=28),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Row(spacing=18, controls=[
                    ft.Container(width=34, height=34, border_radius=17, alignment=ft.Alignment(0, 0), on_click=lambda _: ir_back(), content=tabler_icon("arrow-left", size=22)),
                    ft.Text("Seguimiento del pedido", size=18, color=BRAND, weight=ft.FontWeight.BOLD),
                ]),
                craft_logo(36),
            ],
        ),
    )


def _marker(left, top, active=False):
    return ft.Container(
        left=left,
        top=top,
        width=28,
        height=28,
        border_radius=14,
        bgcolor="#000000" if active else BRAND,
        alignment=ft.Alignment(0, 0),
        shadow=ft.BoxShadow(blur_radius=8, color="#00000035", offset=ft.Offset(0, 2)),
        content=tabler_icon("map-pin", size=18),
    )


def _mapa(pedido):
    detalle = _detalle_envio(pedido)
    progreso = progreso_por_estado(_estado_key(pedido))
    ruta_width = int(360 * progreso)
    return ft.Container(
        expand=True,
        height=500,
        border_radius=12,
        bgcolor="#B9D8E7",
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        border=ft.border.all(1, "#9AC4D8"),
        shadow=ft.BoxShadow(blur_radius=10, color="#00000018", offset=ft.Offset(0, 4)),
        content=ft.Stack(
            controls=[
                ft.Container(left=44, top=246, width=100, height=38, border_radius=20, bgcolor="#F4EEDC"),
                ft.Container(left=146, top=210, width=200, height=92, border_radius=45, bgcolor="#F4EEDC"),
                ft.Container(left=322, top=238, width=130, height=78, border_radius=35, bgcolor="#F4EEDC"),
                ft.Container(left=30, top=338, width=180, height=74, border_radius=35, bgcolor="#F4EEDC"),
                ft.Container(left=250, top=340, width=210, height=82, border_radius=38, bgcolor="#F4EEDC"),
                ft.Container(left=78, top=306, width=360, height=6, border_radius=3, bgcolor="#E7C0C0"),
                ft.Container(left=78, top=306, width=ruta_width, height=6, border_radius=3, bgcolor=BRAND),
                _marker(62, 278),
                _marker(146, 286),
                _marker(226, 255, active=True),
                _marker(314, 284),
                _marker(396, 312),
                _marker(448, 372),
                ft.Container(left=174, top=246, content=ft.Text("Panama", size=20, color=TEXT, weight=ft.FontWeight.BOLD)),
                ft.Container(left=242, top=236, content=ft.Text("Panama City", size=12, color=TEXT, weight=ft.FontWeight.BOLD)),
                ft.Container(left=322, top=424, content=ft.Text(detalle.get("destino", "Destino"), size=12, color=TEXT)),
                ft.Container(left=24, top=430, content=ft.Text(detalle.get("origen", "Origen"), size=12, color=TEXT)),
            ],
        ),
    )


def _pasos(estado_key):
    pasos = [("Preparando", 0.12), ("En camino", 0.68), ("Entregado", 1.0)]
    progreso = progreso_por_estado(estado_key)
    controles = []
    for i, (label, punto) in enumerate(pasos):
        activo = progreso >= punto
        controles.append(
            ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=7,
                controls=[
                    ft.Container(
                        width=28,
                        height=28,
                        border_radius=14,
                        bgcolor="white" if activo else "#C49A9A",
                        alignment=ft.Alignment(0, 0),
                        content=tabler_icon("shopping-cart" if i == 1 else "shopping-bag", size=15),
                    ),
                    ft.Text(label, size=10, color="white", weight=ft.FontWeight.W_600 if activo else ft.FontWeight.NORMAL),
                ],
            )
        )
        if i < len(pasos) - 1:
            controles.append(ft.Container(expand=True, height=4, border_radius=2, bgcolor="white" if progreso >= pasos[i + 1][1] else "#C49A9A", margin=ft.margin.only(top=12)))
    return ft.Row(spacing=0, controls=controles)


def _pedido_card(pedido, activo=False, on_click=None):
    producto = _primer_producto(pedido)
    detalle = _detalle_envio(pedido)
    estado_key = _estado_key(pedido, producto)
    km = float(detalle.get("distancia_km") or 30)
    eta = int(detalle.get("eta_horas") or estimar_entrega_horas(km, estado_key))
    total = _precio(pedido.get("total", 0))
    return ft.Container(
        bgcolor="white",
        border_radius=18,
        border=ft.border.all(1, BRAND if activo else BORDER),
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        shadow=ft.BoxShadow(blur_radius=12, color="#00000012", offset=ft.Offset(0, 4)),
        on_click=on_click,
        content=ft.Column(
            spacing=0,
            controls=[
                ft.Container(
                    padding=ft.padding.symmetric(horizontal=22, vertical=16),
                    content=ft.Column(
                        spacing=7,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Text(pedido.get("comprador_nombre") or "Mi pedido", size=16, color=TEXT, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"Productos: {_producto_count(pedido)}", size=12, color=BRAND, weight=ft.FontWeight.BOLD),
                                ],
                            ),
                            ft.Row(spacing=8, controls=[tabler_icon("map-pin", size=16), ft.Text(pedido.get("direccion") or detalle.get("destino", "Destino"), size=12, color=TEXT)]),
                            ft.Row(spacing=10, controls=[
                                ft.Container(border_radius=14, bgcolor="#F8E76E" if estado_key != "entregado" else "#BEF2C0", padding=ft.padding.symmetric(horizontal=12, vertical=4), content=ft.Text(_estado(pedido, producto), size=11, color=TEXT)),
                                ft.Text(f"ETA: {eta} h", size=11, color=MUTED),
                                ft.Text(f"${total:.2f}", size=12, color=BRAND, weight=ft.FontWeight.BOLD),
                            ]),
                        ],
                    ),
                ),
                ft.Container(
                    visible=activo,
                    bgcolor=BRAND,
                    padding=ft.padding.symmetric(horizontal=28, vertical=16),
                    content=ft.Column(
                        spacing=12,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Text("Tracking en vivo", color="white", size=13, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"{detalle.get('distancia_km', '0')} km", color="white", size=11),
                                ],
                            ),
                            _pasos(estado_key),
                        ],
                    ),
                ),
            ],
        ),
    )


def _producto_linea(item):
    cantidad = int(item.get("cantidad", 1) or 1)
    precio = _precio(item.get("precio", 0))
    return ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        controls=[
            ft.Row(spacing=10, controls=[tabler_icon("shopping-bag", size=16), ft.Text(f"{item.get('nombre', 'Producto')} x{cantidad}", size=12, color=TEXT)]),
            ft.Text(f"${precio * cantidad:.2f}", size=12, color=BRAND, weight=ft.FontWeight.BOLD),
        ],
    )


def show_tracking(page: ft.Page, usuario, ir_back, pedido=None):
    page.clean()
    user = (usuario or {}).get("user")
    pedidos = []
    if pedido:
        pedidos = [pedido]
    elif user:
        try:
            pedidos = supabase.table("pedidos").select("*").eq("comprador_id", user.id).order("created_at", desc=True).execute().data or []
        except Exception as ex:
            print("Error cargando tracking:", ex)

    seleccionado = {"pedido": pedidos[0] if pedidos else None}
    lista_ref = ft.Ref[ft.Column]()
    mapa_ref = ft.Ref[ft.Container]()
    productos_ref = ft.Ref[ft.Column]()

    def pintar():
        actual = seleccionado["pedido"]
        if mapa_ref.current:
            mapa_ref.current.content = _mapa(actual) if actual else ft.Container()
        if lista_ref.current:
            lista_ref.current.controls = [
                _pedido_card(p, activo=p.get("id") == actual.get("id"), on_click=lambda _, ped=p: seleccionar(ped))
                for p in pedidos
            ]
        if productos_ref.current:
            productos_ref.current.controls = [_producto_linea(i) for i in (actual.get("productos") or [])] if actual else []
        page.update()

    def seleccionar(ped):
        seleccionado["pedido"] = ped
        pintar()

    page.add(
        ft.Column(
            expand=True,
            spacing=0,
            controls=[
                _header(ir_back),
                ft.Container(
                    expand=True,
                    bgcolor=BG,
                    padding=ft.padding.all(28),
                    content=(
                        ft.Row(
                            spacing=28,
                            vertical_alignment=ft.CrossAxisAlignment.START,
                            controls=[
                                ft.Container(ref=mapa_ref, expand=True, content=_mapa(seleccionado["pedido"])) if seleccionado["pedido"] else ft.Container(expand=True, alignment=ft.Alignment(0, 0), content=ft.Text("Aun no tienes pedidos para seguir.", color=MUTED)),
                                ft.Container(
                                    width=420,
                                    content=ft.Column(
                                        spacing=16,
                                        controls=[
                                            ft.Container(
                                                height=46,
                                                border_radius=22,
                                                bgcolor="white",
                                                border=ft.border.all(1, BORDER),
                                                padding=ft.padding.symmetric(horizontal=16),
                                                content=ft.Row(spacing=10, controls=[tabler_icon("search", size=18), ft.Text("Buscar pedido...", size=12, color=MUTED)]),
                                            ),
                                            ft.Column(ref=lista_ref, spacing=16, controls=[_pedido_card(p, activo=i == 0, on_click=lambda _, ped=p: seleccionar(ped)) for i, p in enumerate(pedidos)]),
                                            ft.Container(
                                                bgcolor="white",
                                                border_radius=16,
                                                border=ft.border.all(1, BORDER),
                                                padding=18,
                                                content=ft.Column(
                                                    spacing=10,
                                                    controls=[
                                                        ft.Text("Productos comprados", size=15, color=TEXT, weight=ft.FontWeight.BOLD),
                                                        ft.Column(ref=productos_ref, spacing=8, controls=[_producto_linea(i) for i in ((seleccionado["pedido"] or {}).get("productos") or [])]),
                                                    ],
                                                ),
                                            ),
                                        ],
                                    ),
                                ),
                            ],
                        )
                    ),
                ),
            ],
        )
    )
    page.update()
