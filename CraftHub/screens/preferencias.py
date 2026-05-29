import flet as ft
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from screens.componentes import craft_logo, tabler_icon

BRAND = "#861616"
TEXTO = "#1A1A1A"
MUTED = "#777777"
LINE = "#B8B8B8"


PROVINCIAS = [
    ("Colon", "Colon.png"),
    ("Chiriqui", "Chiriqui.png"),
    ("Bocas del Toro", "Bocas del toro.png"),
    ("Veraguas", "Veraguas.png"),
    ("Cocle", "Cocle.png"),
    ("Panama", "Panama.png"),
    ("Panama Oeste", "Panama Oeste.png"),
    ("Los Santos", "Los santos.png"),
    ("Darien", "Darien.png"),
    ("Herrera", "Herrera.png"),
    ("Comarca Guna-Yala", "Guna Yala.png"),
    ("Comarca Ngabe-Bugle", "Ngabe Bugle.png"),
    ("Comarca Embera-Wounaan", "Emberá-Wounaan.png"),
    ("Comarca Madugandi", "Madugandi.png"),
    ("Comarca Wargandi", "Wargandi.png"),
]

CATEGORIAS = [
    ("Gastronomy", "tools-kitchen-2"),
    ("Handicrafts", "sunglasses"),
    ("Footwear", "shoe"),
    ("Jewelry", "diamond"),
    ("Textiles", "shirt"),
    ("Ceramics", "guitar-pick"),
    ("Leather", "shopping-bag"),
    ("Wood", "trees"),
]


def show_preferencias(page: ft.Page, ir_home, usuario=None, omitible=True):
    page.clean()
    page.padding = 0
    page.bgcolor = "white"

    provincias_sel = set()
    categorias_sel = set()
    refs = {}
    continuar_ref = ft.Ref[ft.Container]()

    def ok():
        return len(provincias_sel) >= 3 and len(categorias_sel) >= 3

    def actualizar():
        for nombre, ref in refs.items():
            if ref.current:
                activo = nombre in provincias_sel or nombre in categorias_sel
                ref.current.border = ft.border.all(3 if activo else 2, BRAND if activo else LINE)
                ref.current.bgcolor = "#FFF6F6" if activo else "white"
        if continuar_ref.current:
            continuar_ref.current.bgcolor = BRAND if ok() or omitible else "#BFBFBF"
        page.update()

    def toggle(nombre, grupo):
        target = provincias_sel if grupo == "provincia" else categorias_sel
        if nombre in target:
            target.remove(nombre)
        else:
            target.add(nombre)
        actualizar()

    def flag_card(nombre, archivo):
        ref = ft.Ref[ft.Container]()
        refs[nombre] = ref
        short = "".join([p[0] for p in nombre.replace("-", " ").split()[:2]]).upper()
        return ft.Container(
            ref=ref,
            width=222,
            height=78,
            border_radius=16,
            bgcolor="white",
            border=ft.border.all(2, BRAND),
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            on_click=lambda _: toggle(nombre, "provincia"),
            content=ft.Row(
                spacing=0,
                controls=[
                    ft.Container(
                        width=102,
                        height=78,
                        bgcolor="#F4F4F4",
                        alignment=ft.Alignment(0, 0),
                        content=ft.Image(
                            src=f"banderas/{archivo}",
                            width=102,
                            height=78,
                            fit="cover",
                            error_content=ft.Text(short, size=18, color=BRAND, weight=ft.FontWeight.BOLD),
                        ),
                    ),
                    ft.Container(
                        expand=True,
                        padding=ft.padding.symmetric(horizontal=10),
                        alignment=ft.Alignment(0, 0),
                        content=ft.Text(
                            nombre,
                            size=12,
                            color=BRAND,
                            weight=ft.FontWeight.BOLD,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ),
                ],
            ),
        )

    def categoria_card(nombre, icono):
        ref = ft.Ref[ft.Container]()
        refs[nombre] = ref
        return ft.Container(
            ref=ref,
            width=210,
            height=116,
            border_radius=22,
            bgcolor="white",
            border=ft.border.all(2, "#B86A6A"),
            shadow=ft.BoxShadow(blur_radius=4, color="#00000025", offset=ft.Offset(0, 3)),
            on_click=lambda _: toggle(nombre, "categoria"),
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
                controls=[
                    tabler_icon(icono, size=42),
                    ft.Text(nombre, size=20, color=BRAND, weight=ft.FontWeight.BOLD),
                ],
            ),
        )

    def section_title(text):
        return ft.Container(
            width=520,
            height=50,
            border_radius=25,
            bgcolor="white",
            border=ft.border.all(2, LINE),
            alignment=ft.Alignment(0, 0),
            content=ft.Text(text, size=18, color=BRAND, weight=ft.FontWeight.BOLD),
        )

    def rows(items, builder, per_row):
        out = []
        row = []
        for i, item in enumerate(items):
            row.append(builder(*item))
            if len(row) == per_row or i == len(items) - 1:
                out.append(ft.Row(spacing=18, controls=row))
                row = []
        return out

    def continuar(e=None):
        if ok() or omitible:
            ir_home()

    header = ft.Container(
        height=82,
        bgcolor="white",
        padding=ft.padding.symmetric(horizontal=20),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=42,
                    height=42,
                    alignment=ft.Alignment(0, 0),
                    content=tabler_icon("arrow-left", size=24),
                ),
                section_title("Select the provinces of Panama that interest you"),
                craft_logo(46),
            ],
        ),
    )

    contenido = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=22,
        controls=[
            header,
            ft.Container(
                width=1180,
                alignment=ft.Alignment(-1, 0),
                content=ft.Text("Province of interest", size=20, color=BRAND, weight=ft.FontWeight.BOLD),
            ),
            ft.Container(
                width=1240,
                border_radius=8,
                border=ft.border.all(2, LINE),
                padding=ft.padding.symmetric(horizontal=16, vertical=24),
                content=ft.Column(spacing=24, controls=rows(PROVINCIAS, flag_card, 5)),
            ),
            ft.Container(height=6),
            section_title("What types of products interest you?"),
            ft.Container(
                width=1180,
                alignment=ft.Alignment(-1, 0),
                content=ft.Text("Main interests", size=28, color=BRAND, weight=ft.FontWeight.BOLD),
            ),
            ft.Container(
                width=1180,
                border_radius=10,
                border=ft.border.all(2, LINE),
                padding=ft.padding.symmetric(horizontal=62, vertical=28),
                content=ft.Column(spacing=20, controls=rows(CATEGORIAS, categoria_card, 4)),
            ),
            ft.Row(
                width=1180,
                alignment=ft.MainAxisAlignment.END,
                controls=[
                    ft.TextButton("Omitir", visible=omitible, style=ft.ButtonStyle(color=MUTED), on_click=lambda _: ir_home()),
                    ft.Container(
                        ref=continuar_ref,
                        width=170,
                        height=44,
                        border_radius=22,
                        bgcolor="#BFBFBF",
                        alignment=ft.Alignment(0, 0),
                        on_click=continuar,
                        content=ft.Text("Continuar", size=14, color="white", weight=ft.FontWeight.BOLD),
                    ),
                ],
            ),
            ft.Container(height=28),
        ],
    )

    page.add(ft.Container(expand=True, bgcolor="white", content=contenido))
    actualizar()


def personalizar(page: ft.Page, ir_login, ir_home):
    show_preferencias(page, ir_home=ir_home, usuario=None, omitible=False)
