import flet as ft
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from screens.componentes import craft_logo

BRAND = "#800000"


def show_bienvenida(page: ft.Page, ir_login, ir_explorar=None, ir_registro=None):
    page.clean()

    page.add(
        ft.Container(
            expand=True,
            content=ft.Stack(
                controls=[
                    
         ft.Container(
                        expand=True,
                        alignment=ft.Alignment(0, -1),
                        content=ft.Image(
                            src="banner.png",
                            fit="cover",
                            width=float("inf"),
                            height=float("inf"),
                        ),
                    ),
                
                    ft.Container(bgcolor="#00000066"),
                    ft.Container(
                        padding=ft.padding.symmetric(horizontal=56, vertical=48),
                        content=ft.Column(
                            expand=True,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Container(
                                    height=56,
                                    border_radius=12,
                                    bgcolor=BRAND,
                                    border=None,
                                    padding=ft.padding.symmetric(horizontal=22),
                                    content=ft.Row(
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                        controls=[
                                            ft.Row(spacing=10, controls=[
                                                craft_logo(34),
                                                ft.Text("CRAFTHUB", size=14, color="white",
                                                        weight=ft.FontWeight.BOLD),
                                            ]),
                                            ft.Row(spacing=44, controls=[
                                                ft.Container(
                                                    on_click=lambda _: show_bienvenida(
                                                        page, ir_login, ir_explorar, ir_registro
                                                    ),
                                                    content=ft.Text("Inicio", size=14, color="white",
                                                                    weight=ft.FontWeight.W_600),
                                                ),
                                                ft.Container(
                                                    on_click=lambda _: ir_explorar() if ir_explorar else ir_login(),
                                                    content=ft.Text("Explorar", size=14, color="white",
                                                                    weight=ft.FontWeight.W_600),
                                                ),
                                                ft.Text("Contacto", size=14, color="white",
                                                        weight=ft.FontWeight.W_600),
                                            ]),
                                            ft.Container(
                                                width=20,
                                                height=20,
                                                border_radius=20,
                                                bgcolor=BRAND,
                                                alignment=ft.Alignment(0, 0),
                                                content=ft.Text("+", size=35,  bgcolor="white",
                                                                weight=ft.FontWeight.BOLD),
                                            ),
                                        ],
                                    ),
                                ),
                                ft.Container(expand=True),
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                    controls=[
                                        craft_logo(104),
                                        ft.Container(width=28),
                                        ft.Column(spacing=8, controls=[
                                            ft.Text("CRAFTHUB", size=64, color="white",
                                                    weight=ft.FontWeight.BOLD),
                                            ft.Text("C R E A T I V I D A D   C O N   P R O P O S I T O",
                                                    size=13, color="white",
                                                    weight=ft.FontWeight.W_600),
                                        ]),
                                    ],
                                ),
                                ft.Container(height=86),
                                ft.Container(
                                    width=430,
                                    height=48,
                                    border_radius=10,
                                    bgcolor=BRAND,
                                    border=None,
                                    alignment=ft.Alignment(0, 0),
                                    on_click=lambda _: ir_explorar() if ir_explorar else ir_login(),
                                    content=ft.Text("Explorar CraftHub", size=20,
                                                    color="white",
                                                    weight=ft.FontWeight.BOLD),
                                ),
                                ft.Container(height=18),
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    spacing=6,
                                    controls=[
                                        ft.Text("¿Quieres vender o guardar tu cuenta?",
                                                size=13, color="white",
                                                weight=ft.FontWeight.W_600),
                                        ft.TextButton(
                                            "Iniciar sesion",
                                            style=ft.ButtonStyle(color="white"),
                                            on_click=lambda _: ir_login(),
                                        ),
                                        ft.TextButton(
                                            "Registrarse",
                                            style=ft.ButtonStyle(color="white"),
                                            on_click=lambda _: ir_registro() if ir_registro else ir_login(),
                                        ),
                                    ],
                                ),
                                ft.Container(expand=True),
                            ],
                        ),
                    ),
                ],
            ),
        )
    )
    page.update()
