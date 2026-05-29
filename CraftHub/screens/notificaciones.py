import flet as ft
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supabase_client import supabase
from screens.componentes import craft_banner_header, craft_logo, tabler_icon

BRAND = "#941515"
BRAND_DARK = "#760F0F"
BRAND_LIGHT = "#F4DCDC"
PINK = "#C99598"
TEXT = "#202020"
MUTED = "#777777"
BORDER = "#E7D7D7"
BG = "#FAFAFA"

ESTADOS = ["pendiente", "en proceso", "enviado", "entregado"]
PASOS = ["Preparando", "Enviado", "En camino", "Entregado"]


def _precio(valor):
    try:
        if isinstance(valor, (int, float)):
            return float(valor)
        return float(str(valor).replace("$", "").replace(",", ""))
    except Exception:
        return 0.0


def _estado_normal(valor):
    texto = (valor or "pendiente").strip().lower()
    if texto in ["preparando", "proceso", "procesando"]:
        return "en proceso"
    if texto in ["camino", "en camino"]:
        return "enviado"
    if texto not in ESTADOS:
        return "pendiente"
    return texto


def _estado_item(pedido, item):
    return _estado_normal(item.get("estado") or pedido.get("estado"))


def _paso_indice(estado):
    estado = _estado_normal(estado)
    if estado == "pendiente":
        return 0
    if estado == "en proceso":
        return 0
    if estado == "enviado":
        return 2
    return 3


def _mensaje_comprador(estado):
    estado = _estado_normal(estado)
    if estado == "pendiente":
        return "Tu pedido fue recibido"
    if estado == "en proceso":
        return "Tu pedido se esta preparando"
    if estado == "enviado":
        return "Tu pedido esta en camino"
    return "Tu pedido fue entregado"


def _mensaje_vendedor(estado):
    estado = _estado_normal(estado)
    if estado == "pendiente":
        return "Nueva venta"
    if estado == "en proceso":
        return "Pedido en preparacion"
    if estado == "enviado":
        return "Pedido enviado"
    return "Venta completada"


def _fecha_corta(valor):
    return (valor or "")[:10] or "Ahora"


def _producto_preview(item):
    img = item.get("img") or item.get("imagen") or ""
    return ft.Container(
        width=108,
        height=68,
        border_radius=4,
        bgcolor="#D9D9D9",
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        content=ft.Image(
            src=img,
            width=108,
            height=68,
            fit="cover",
            error_content=ft.Container(
                width=108,
                height=68,
                bgcolor="#D9D9D9",
                alignment=ft.Alignment(0, 0),
                content=tabler_icon("photo", size=26),
            ),
        ),
    )


def _progress_bar(estado):
    activo = _paso_indice(estado)
    controles = []
    for i, paso in enumerate(PASOS):
        completado = i <= activo
        controles.append(
            ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
                controls=[
                    ft.Container(
                        width=34,
                        height=34,
                        border_radius=17,
                        bgcolor=BRAND if completado else "white",
                        border=ft.border.all(2, "white" if completado else "#E8CACA"),
                        alignment=ft.Alignment(0, 0),
                        content=(
                            tabler_icon("check", size=17)
                            if completado
                            else tabler_icon("shopping-cart" if i == 2 else "shopping-bag", size=16)
                        ),
                    ),
                    ft.Text(
                        paso,
                        size=11,
                        color="white" if i >= 2 else BRAND_DARK,
                        weight=ft.FontWeight.W_600 if completado else ft.FontWeight.NORMAL,
                    ),
                ],
            )
        )
        if i < len(PASOS) - 1:
            controles.append(
                ft.Container(
                    expand=True,
                    height=4,
                    bgcolor=BRAND if i < activo else "#F2E3E3",
                    margin=ft.margin.only(top=15),
                )
            )
    return ft.Container(
        bgcolor=PINK,
        padding=ft.padding.only(left=26, right=26, top=14, bottom=8),
        content=ft.Row(
            spacing=0,
            vertical_alignment=ft.CrossAxisAlignment.START,
            controls=controles,
        ),
    )


def _notification_shell(card):
    return ft.Container(
        width=670,
        bgcolor=PINK,
        border_radius=20,
        padding=30,
        shadow=ft.BoxShadow(blur_radius=20, color="#00000018", offset=ft.Offset(0, 8)),
        content=card,
    )


def _empty_state(texto):
    return ft.Container(
        padding=70,
        alignment=ft.Alignment(0, 0),
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
            controls=[
                tabler_icon("bell", size=44),
                ft.Text(texto, size=16, color=MUTED, weight=ft.FontWeight.W_600),
            ],
        ),
    )


def _card_comprador(pedido, item, ir_tracking=None):
    estado = _estado_item(pedido, item)
    cantidad = int(item.get("cantidad", 1) or 1)
    precio = _precio(item.get("precio", 0))
    nombre = item.get("nombre", "Producto")

    def abrir_tracking(e=None):
        if ir_tracking:
            ir_tracking(pedido)

    card = ft.Container(
        bgcolor="white",
        border_radius=16,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        content=ft.Column(
            spacing=0,
            controls=[
                ft.Container(
                    height=62,
                    bgcolor="white",
                    padding=ft.padding.symmetric(horizontal=28, vertical=12),
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row(spacing=8, controls=[craft_logo(32), ft.Text("CRAFTHUB", size=11, color=TEXT, weight=ft.FontWeight.BOLD)]),
                            ft.Row(spacing=14, controls=[ft.Text("Ahora", size=13, color=TEXT), tabler_icon("dots-vertical", size=20)]),
                        ],
                    ),
                ),
                ft.Container(
                    bgcolor=PINK,
                    padding=ft.padding.symmetric(horizontal=38, vertical=14),
                    content=ft.Row(
                        spacing=34,
                        controls=[
                            ft.Container(
                                width=132,
                                height=132,
                                border_radius=66,
                                bgcolor="#E32429",
                                alignment=ft.Alignment(0, 0),
                                content=tabler_icon("truck-delivery", size=58),
                            ),
                            ft.Column(
                                expand=True,
                                spacing=8,
                                controls=[
                                    ft.Text(_mensaje_comprador(estado), size=24, color=TEXT, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"Tu compra de {nombre} ya fue actualizada", size=13, color=TEXT),
                                    ft.Text(f"Llega aprox. el {_fecha_corta(pedido.get('created_at'))}", size=13, color=TEXT),
                                ],
                            ),
                        ],
                    ),
                ),
                _progress_bar(estado),
                ft.Container(
                    padding=ft.padding.symmetric(horizontal=42, vertical=12),
                    content=ft.Row(
                        spacing=28,
                        controls=[
                            _producto_preview(item),
                            ft.Column(
                                spacing=4,
                                controls=[
                                    ft.Text(nombre, size=17, color=TEXT, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"Cantidad: {cantidad}", size=11, color=MUTED),
                                    ft.Text(f"${precio * cantidad:.2f}", size=17, color=TEXT, weight=ft.FontWeight.BOLD),
                                ],
                            ),
                        ],
                    ),
                ),
                ft.Container(
                    margin=ft.margin.only(left=22, right=22, bottom=12),
                    height=52,
                    border_radius=8,
                    bgcolor=BRAND,
                    alignment=ft.Alignment(0, 0),
                    on_click=abrir_tracking,
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=18,
                        controls=[
                            ft.Text("Ver seguimiento", color="white", size=16, weight=ft.FontWeight.BOLD),
                            tabler_icon("chevron-right", size=22),
                        ],
                    ),
                ),
            ],
        ),
    )
    return _notification_shell(card)


def _card_vendedor(pedido, item, leida=False, on_open=None):
    estado = _estado_item(pedido, item)
    cantidad = int(item.get("cantidad", 1) or 1)
    precio = _precio(item.get("precio", 0))
    nombre = item.get("nombre", "Producto")

    card_bg = "#EFEFEF" if leida else "white"
    soft_bg = "#D8D8D8" if leida else PINK

    card = ft.Container(
        bgcolor=card_bg,
        border_radius=16,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        content=ft.Column(
            spacing=0,
            controls=[
                ft.Container(
                    height=62,
                    bgcolor=card_bg,
                    padding=ft.padding.symmetric(horizontal=28, vertical=12),
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row(spacing=8, controls=[craft_logo(32), ft.Text("CRAFTHUB", size=11, color=TEXT, weight=ft.FontWeight.BOLD)]),
                            ft.Row(spacing=14, controls=[ft.Text("Ahora", size=13, color=TEXT), tabler_icon("dots-vertical", size=20)]),
                        ],
                    ),
                ),
                ft.Container(
                    bgcolor=soft_bg,
                    padding=ft.padding.symmetric(horizontal=38, vertical=14),
                    content=ft.Row(
                        spacing=34,
                        controls=[
                            ft.Container(
                                width=132,
                                height=132,
                                border_radius=66,
                                bgcolor="#B42328" if not leida else "#A8A8A8",
                                alignment=ft.Alignment(0, 0),
                                content=tabler_icon("cash", size=58),
                            ),
                            ft.Column(
                                expand=True,
                                spacing=8,
                                controls=[
                                    ft.Text(_mensaje_vendedor(estado), size=24, color=TEXT, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"Vendiste {nombre}", size=13, color=TEXT, weight=ft.FontWeight.W_600),
                                    ft.Text(f"Cliente: {pedido.get('comprador_nombre') or 'Cliente'}", size=12, color=TEXT),
                                    ft.Text("Preparalo para enviarlo antes de 24 horas", size=12, color=TEXT),
                                ],
                            ),
                        ],
                    ),
                ),
                _progress_bar(estado),
                ft.Container(
                    padding=ft.padding.symmetric(horizontal=42, vertical=12),
                    content=ft.Row(
                        spacing=28,
                        controls=[
                            _producto_preview(item),
                            ft.Column(
                                spacing=4,
                                controls=[
                                    ft.Text(nombre, size=17, color=TEXT, weight=ft.FontWeight.BOLD),
                                    ft.Text(f"Pedido #{pedido.get('id', '-')}", size=11, color=MUTED),
                                    ft.Text(f"${precio * cantidad:.2f}", size=17, color=TEXT, weight=ft.FontWeight.BOLD),
                                ],
                            ),
                            ft.Container(expand=True),
                            ft.Container(
                                border_radius=2,
                                bgcolor="#D9AAAA",
                                padding=ft.padding.symmetric(horizontal=16, vertical=10),
                                content=ft.Text("Pago aprobado", size=12, color=BRAND, weight=ft.FontWeight.BOLD),
                            ),
                        ],
                    ),
                ),
                ft.Container(
                    margin=ft.margin.only(left=22, right=22, bottom=12),
                    height=52,
                    border_radius=8,
                    bgcolor=BRAND if not leida else "#A8A8A8",
                    alignment=ft.Alignment(0, 0),
                    on_click=on_open,
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=18,
                        controls=[
                            ft.Text("Ver pedido pendiente", color="white", size=16, weight=ft.FontWeight.BOLD),
                            tabler_icon("chevron-right", size=22),
                        ],
                    ),
                ),
            ],
        ),
    )
    return _notification_shell(card)


def _items_de_vendedor(pedido, nombres_productos):
    nombres = set(nombres_productos)
    return [item for item in (pedido.get("productos") or []) if item.get("nombre") in nombres]


def show_notificaciones_comprador(page: ft.Page, usuario, ir_home, ir_tracking=None):
    page.clean()
    user = (usuario or {}).get("user")

    pedidos = []
    if user:
        try:
            resp = supabase.table("pedidos").select("*").eq("comprador_id", user.id).order("created_at", desc=True).execute()
            pedidos = resp.data or []
        except Exception as ex:
            print("Error cargando notificaciones comprador:", ex)

    cards = []
    for pedido in pedidos:
        for item in pedido.get("productos") or []:
            cards.append(_card_comprador(pedido, item, ir_tracking))

    header = craft_banner_header(
        "Notificaciones",
        None,
        height=70,
        on_logo_click=ir_home,
        actions=[
            ft.Container(width=34, height=34, border_radius=17, bgcolor="#FFFFFF33", alignment=ft.Alignment(0, 0), content=tabler_icon("bell", size=18)),
        ],
    )

    page.add(
        ft.Column(
            expand=True,
            spacing=0,
            controls=[
                header,
                ft.Container(
                    expand=True,
                    bgcolor=BG,
                    alignment=ft.Alignment(0, -1),
                    padding=ft.padding.only(top=16, bottom=28),
                    content=ft.Column(
                        scroll=ft.ScrollMode.AUTO,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=18,
                        controls=cards if cards else [_empty_state("Aun no tienes notificaciones de pedidos.")],
                    ),
                ),
            ],
        )
    )
    page.update()


def show_notificaciones_vendedor(page: ft.Page, usuario, ir_vendedor, ir_pedidos=None):
    page.clean()
    perfil = (usuario or {}).get("perfil") or {}
    nombre = perfil.get("nombre", "Vendedor")
    vistas = usuario.setdefault("notificaciones_vendedor_vistas", set())

    productos = []
    pedidos = []
    try:
        productos = supabase.table("productos").select("nombre").eq("creador", nombre).execute().data or []
        nombres = [p.get("nombre") for p in productos]
        todos = supabase.table("pedidos").select("*").order("created_at", desc=True).execute().data or []
        for pedido in todos:
            if _items_de_vendedor(pedido, nombres):
                pedidos.append(pedido)
    except Exception as ex:
        print("Error cargando notificaciones vendedor:", ex)
        nombres = []

    def abrir_pedido(pid):
        vistas.add(str(pid))
        if ir_pedidos:
            ir_pedidos()
        else:
            ir_vendedor()

    cards = []
    for pedido in pedidos:
        pid = str(pedido.get("id"))
        leida = pid in vistas
        for item in _items_de_vendedor(pedido, nombres):
            cards.append(_card_vendedor(pedido, item, leida, on_open=lambda _, p=pedido: abrir_pedido(p.get("id"))))

    header = craft_banner_header(
        "Notificaciones",
        None,
        height=70,
        on_logo_click=ir_vendedor,
        actions=[
            ft.Container(width=34, height=34, border_radius=17, bgcolor="#FFFFFF33", alignment=ft.Alignment(0, 0), content=tabler_icon("bell", size=18)),
        ],
    )

    page.add(
        ft.Column(
            expand=True,
            spacing=0,
            controls=[
                header,
                ft.Container(
                    expand=True,
                    bgcolor=BG,
                    alignment=ft.Alignment(0, -1),
                    padding=ft.padding.only(top=16, bottom=28),
                    content=ft.Column(
                        scroll=ft.ScrollMode.AUTO,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=18,
                        controls=cards if cards else [_empty_state("Aun no hay ventas nuevas.")],
                    ),
                ),
            ],
        )
    )
    page.update()
