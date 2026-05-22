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
CANVAS_H = int(518 * SCALE)
HEADER_H = int(58 * SCALE)


def s(value):
    return int(value * SCALE)


def show_seleccion_rol(page: ft.Page, ir_bienvenida, ir_comprador, ir_vendedor):
    page.clean()
    page.window_width = 1280
    page.window_height = 800
    page.padding = 0
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
                size=s(16),
                color="white",
                weight=ft.FontWeight.BOLD,
            ),
        )

    def rol_card(left, icono, titulo, texto, acciones):
        return ft.Container(
            left=s(left),
            top=s(82),
            width=s(355),
            height=s(400),
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
                        top=s(186),
                        width=s(292),
                        content=ft.Column(
                            spacing=s(8),
                            controls=[
                                ft.Text(
                                    titulo,
                                    size=s(24),
                                    color="white",
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Text(
                                    texto,
                                    size=s(15),
                                    color=MUTED,
                                    height=1.28,
                                ),
                            ],
                        ),
                    ),
                    ft.Container(
                        left=0,
                        top=s(304),
                        width=s(355),
                        alignment=ft.Alignment(0, 0),
                        content=ft.Column(
                            spacing=s(12),
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=acciones,
                        ),
                    ),
                ],
            ),
        )

    header = ft.Container(
        left=0,
        top=0,
        width=CANVAS_W,
        height=HEADER_H,
        bgcolor="white",
        border=ft.border.only(bottom=ft.BorderSide(1, "#D8D8D8")),
        content=ft.Stack(
            controls=[
                ft.Container(
                    left=s(20),
                    top=s(19),
                    width=s(24),
                    height=s(24),
                    alignment=ft.Alignment(0, 0),
                    on_click=lambda _: ir_bienvenida(),
                    content=tabler_icon("arrow-left", size=s(22)),
                ),
                ft.Container(
                    left=0,
                    top=s(18),
                    width=CANVAS_W,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Text(
                        "Identify your user role",
                        size=s(20),
                        color=TEXTO,
                        weight=ft.FontWeight.BOLD,
                    ),
                ),
                ft.Container(
                    left=s(779),
                    top=s(15),
                    content=ft.Row(
                        spacing=s(5),
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            craft_logo(s(33)),
                            ft.Text(
                                "CRAFTHUB",
                                size=s(9),
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
                        header,
                        rol_card(
                            77,
                            "building-store",
                            "VENDEDOR",
                            "Do you want more than just a product a story? Discover handmade creations crafted with passion on CraftHub.",
                            [
                                ft.Container(height=s(45)),
                                pill_button("Register", lambda _: ir_vendedor()),
                            ],
                        ),
                        rol_card(
                            468,
                            "shopping-bag",
                            "COMPRADOR",
                            "Do you want more than just a product a story? Discover handmade creations crafted with passion on CraftHub.",
                            [
                                pill_button("Explore", lambda _: ir_comprador(), outlined=True),
                                pill_button("Register", lambda _: ir_vendedor()),
                            ],
                        ),
                    ],
                    clip_behavior=ft.ClipBehavior.HARD_EDGE,
                ),
            ),
        )
    )
    page.update()
