import flet as ft
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from screens.componentes import craft_logo
from screens.componentes import tabler_icon

BRAND = "#800000"
BRAND_DARK = "#941515"
TEXTO = "#1A1A1A"
MUTED = "#F6F6F6"
BUTTON_GRAY = "#8F8F8F"
SCALE = 1.42
CANVAS_W = int(879 * SCALE)
CANVAS_H = int(600 * SCALE)
HEADER_H = int(48 * SCALE)


def s(value):
    return int(value * SCALE)


def show_seleccion_rol(
    page: ft.Page,
    ir_bienvenida,
    ir_comprador,
    ir_vendedor,
    ir_login_comprador=None,
    ir_registro_comprador=None,
):
    page.clean()
    page.appbar = None
    page.window_width = 1280
    page.window_height = 800
    page.padding = 0
    page.spacing = 0
    page.bgcolor = "white"

    def pill_button(texto, accion, bgcolor=BUTTON_GRAY, width=212, outlined=False):
        return ft.Container(
            width=s(width),
            height=s(34),
            border_radius=s(18),
            bgcolor="transparent" if outlined else bgcolor,
            border=ft.border.all(1, "white") if outlined else None,
            alignment=ft.Alignment(0, 0),
            on_click=accion,
            content=ft.Text(
                texto,
                size=s(13),
                color="white",
                weight=ft.FontWeight.BOLD,
            ),
        )

    def rol_card(left, icono, titulo, texto, acciones, botones_top=390):
        return ft.Container(
            left=s(left),
            top=s(20),
            width=s(355),
            height=s(450),
            border_radius=s(26),
            bgcolor="black",
            border=ft.border.all(1, "black"),
            shadow=ft.BoxShadow(
                blur_radius=s(6),
                color="#00000026",
                offset=ft.Offset(0, s(1)),
            ),
            content=ft.Stack(
                controls=[
                    ft.Container(
                        left=s(24),
                        top=s(19),
                        width=s(306),
                        height=s(156),
                        border_radius=s(7),
                        bgcolor="white",
                        alignment=ft.Alignment(0, 0),
                        content=tabler_icon(icono, size=s(98)),
                    ),
                    ft.Container(
                        left=s(31),
                        top=s(184),
                        width=s(292),
                        content=ft.Text(
                            titulo,
                            size=s(24),
                            color="white",
                            weight=ft.FontWeight.BOLD,
                        ),
                    ),
                    ft.Container(
                        left=s(31),
                        top=s(230),
                        width=s(292),
                        height=s(100),
                        content=ft.Text(
                            texto,
                            size=s(13),
                            color="white",
                            height=1.25,
                        ),
                    ),
                    ft.Container(
                        left=0,
                        top=s(botones_top),
                        width=s(355),
                        alignment=ft.Alignment(0, 0),
                        content=ft.Column(
                            spacing=s(10),
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=acciones,
                        ),
                    ),
                ],
            ),
        )

    header = ft.Container(
        width=float("inf"),
        height=s(48),
        bgcolor="white",
        border=ft.border.only(bottom=ft.BorderSide(1, "#D8D8D8")),
        content=ft.Row(
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
            controls=[
                ft.Container(
                    width=s(24),
                    height=s(24),
                    alignment=ft.Alignment(0, 0),
                    on_click=lambda _: ir_bienvenida(),
                    content=tabler_icon("arrow-left", size=s(22)),
                    margin=ft.margin.only(left=s(20)),
                ),
                ft.Container(
                    expand=True,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Text(
                        "Elige tu rol de usuario",
                        size=s(15),
                        color=TEXTO,
                        weight=ft.FontWeight.W_500,
                    ),
                ),
                ft.Container(
                    margin=ft.margin.only(right=s(20)),
                    content=ft.Row(
                        spacing=s(5),
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            craft_logo(s(28)),
                            ft.Text(
                                "CRAFTHUB",
                                size=s(12),
                                color=TEXTO,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ],
                    ),
                ),
            ],
        ),
    )

    page.add(
        ft.Column(
            spacing=0,
            expand=True,
            controls=[
                header,
                ft.Container(
                    expand=True,
                    bgcolor="white",
                    alignment=ft.Alignment(0, 0),
                    content=ft.Container(
                        width=CANVAS_W,
                        height=CANVAS_H,
                        bgcolor="white",
                        content=ft.Stack(
                            controls=[
                                rol_card(
                                    60,
                                    "building-store",
                                    "VENDEDOR",
                                    "Convierte lo que amas crear en una oportunidad. Publica tus productos, recibe pedidos y haz crecer tu taller en CraftHub.",
                                    [
                                        pill_button("Iniciar sesion", lambda _: ir_vendedor()),
                                    ],
                                    botones_top=390,
                                ),
                                rol_card(
                                    500,
                                    "shopping-bag",
                                    "COMPRADOR",
                                    "Explora artesanias panamenas hechas con pasion. Descubre historias, productos unicos y compra cuando quieras.",
                                    [
                                        pill_button("Explorar", lambda _: ir_comprador(), outlined=True),
                                        pill_button(
                                            "Iniciar sesion",
                                            lambda _: ir_login_comprador() if ir_login_comprador else ir_comprador(),
                                        ),
                                    ],
                                    botones_top=344,
                                ),
                            ],
                            clip_behavior=ft.ClipBehavior.HARD_EDGE,
                        ),
                    ),
                ),
            ],
        )
    )
    page.update()