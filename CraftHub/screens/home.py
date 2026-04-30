import flet as ft
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supabase_client import supabase

BRAND = "#800000"
BRAND_LIGHT = "#F5E8E8"
GRIS = "#F4F4F4"
TEXTO = "#1A1A1A"
MUTED = "#888888"


def show_home(page: ft.Page, ir_bienvenida, ir_carrito=None, carrito_global=None, usuario=None):
    page.clean()

    if carrito_global is None:
        carrito_global = []

    categoria_activa = {"v": "Todos"}
    contenedor_grid = ft.Ref[ft.Column]()
    badge_carrito = ft.Ref[ft.Text]()
    loading_ref = ft.Ref[ft.Column]()
    cuerpo_ref = ft.Ref[ft.Column]()
    productos_cache = {"data": []}
    chips_refs = {}

    nombre_usuario = "User"
    if usuario and usuario.get("perfil"):
        nombre_usuario = usuario["perfil"].get("nombre", "User").split()[0]

    categorias_filtro = [
        "Todos", "Artesanía", "Joyería", "Vestir",
        "Calzado", "Instrumentos", "Accesorios", "Alimentos"
    ]

    def cargar_productos():
        try:
            resp = supabase.table("productos").select("*").execute()
            return resp.data or []
        except Exception as e:
            print("Error cargando productos:", e)
            return []

    def agregar_al_carrito(producto):
        for item in carrito_global:
            if item["nombre"] == producto["nombre"]:
                item["cantidad"] = item.get("cantidad", 1) + 1
                actualizar_badge()
                mostrar_snack(f"'{producto['nombre']}' agregado")
                return
        nuevo = dict(producto)
        nuevo["cantidad"] = 1
        carrito_global.append(nuevo)
        actualizar_badge()
        mostrar_snack(f"'{producto['nombre']}' agregado al carrito")

    def actualizar_badge():
        total = sum(p.get("cantidad", 1) for p in carrito_global)
        if badge_carrito.current:
            badge_carrito.current.value = str(total) if total > 0 else ""
            badge_carrito.current.visible = total > 0
        page.update()

    def mostrar_snack(msg):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(msg, color="white"),
            bgcolor=BRAND, duration=2000,
        )
        page.snack_bar.open = True
        page.update()

    def producto_card(p):
        nombre = p.get("nombre", "Producto")
        precio = p.get("precio", 0)
        precio_str = f"${float(precio):.2f}" if precio else "$0.00"
        categoria = p.get("categoria", "")
        origen = p.get("origen", p.get("region", "Panama"))
        color = p.get("color", "#C4A882")
        img_url = p.get("img", "")
        img_valida = img_url and img_url.startswith("http")

        return ft.Container(
            width=210, height=310,
            border_radius=14,
            bgcolor="white",
            border=ft.border.all(1, "#EEEEEE"),
            shadow=ft.BoxShadow(blur_radius=12, color="#00000010",
                                offset=ft.Offset(0, 3)),
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            content=ft.Column(
                spacing=0,
                controls=[
                    ft.Container(
                        height=160,
                        bgcolor=color,
                        content=ft.Image(
                            src=img_url if img_valida else "",
                            fit="cover",
                            width=210, height=160,
                            error_content=ft.Container(
                                bgcolor=color,
                                alignment=ft.Alignment(0, 0),
                                content=ft.Text("🎨", size=30)
                            ),
                        )
                    ),
                    ft.Container(
                        padding=ft.padding.symmetric(horizontal=12, vertical=10),
                        content=ft.Column(
                            spacing=4,
                            controls=[
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Text(nombre, size=13,
                                                weight=ft.FontWeight.BOLD,
                                                color=TEXTO),
                                        ft.Text("♡", size=16, color=MUTED),
                                    ]
                                ),
                                ft.Text(origen, size=11, color=MUTED),
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Text(precio_str, size=14,
                                                color=BRAND,
                                                weight=ft.FontWeight.BOLD),
                                        ft.Container(
                                            bgcolor=BRAND_LIGHT,
                                            border_radius=6,
                                            padding=ft.padding.symmetric(
                                                horizontal=8, vertical=3),
                                            content=ft.Text(
                                                categoria, size=10,
                                                color=BRAND,
                                                weight=ft.FontWeight.W_500)
                                        )
                                    ]
                                ),
                                ft.Container(height=4),
                                ft.Container(
                                    height=32,
                                    border_radius=8,
                                    bgcolor=BRAND,
                                    alignment=ft.Alignment(0, 0),
                                    on_click=lambda _, prod=p: agregar_al_carrito(prod),
                                    content=ft.Text(
                                        "+ Agregar al carrito",
                                        size=11, color="white",
                                        weight=ft.FontWeight.W_500
                                    )
                                )
                            ]
                        )
                    )
                ]
            )
        )

    def construir_grid(productos, filtro="Todos"):
        lista = productos if filtro == "Todos" else [
            p for p in productos if p.get("categoria", "") == filtro
        ]
        if not lista:
            return [ft.Container(
                padding=40,
                alignment=ft.Alignment(0, 0),
                content=ft.Text("No hay productos en esta categoria",
                                color=MUTED, size=14)
            )]
        filas = []
        fila_actual = []
        for i, p in enumerate(lista):
            fila_actual.append(producto_card(p))
            if len(fila_actual) == 5 or i == len(lista) - 1:
                filas.append(ft.Row(spacing=16, controls=fila_actual))
                fila_actual = []
        return filas

    def chip_filtro(cat):
        activo = cat == "Todos"
        cont = ft.Ref[ft.Container]()
        chips_refs[cat] = cont
        return ft.Container(
            ref=cont,
            border_radius=20,
            bgcolor=BRAND if activo else "white",
            border=ft.border.all(1, BRAND if activo else "#DDDDDD"),
            padding=ft.padding.symmetric(horizontal=16, vertical=8),
            on_click=lambda _, c=cat: filtrar(c),
            content=ft.Text(
                cat, size=12,
                color="white" if activo else TEXTO,
                weight=ft.FontWeight.W_500
            )
        )

    def filtrar(cat):
        for c, ref in chips_refs.items():
            if ref.current:
                es_activo = c == cat
                ref.current.bgcolor = BRAND if es_activo else "white"
                ref.current.border = ft.border.all(
                    1, BRAND if es_activo else "#DDDDDD"
                )
                ref.current.content.color = "white" if es_activo else TEXTO

        categoria_activa["v"] = cat
        if contenedor_grid.current:
            contenedor_grid.current.controls = construir_grid(
                productos_cache["data"], cat)
        page.update()

    def nav_item(emoji, texto, activo=False, accion=None):
        return ft.Container(
            border_radius=10,
            bgcolor=BRAND_LIGHT if activo else "transparent",
            padding=ft.padding.symmetric(horizontal=12, vertical=10),
            on_click=accion,
            content=ft.Row(
                spacing=10,
                controls=[
                    ft.Text(emoji, size=16),
                    ft.Text(texto, size=13,
                            color=BRAND if activo else MUTED,
                            weight=ft.FontWeight.W_500 if activo
                            else ft.FontWeight.NORMAL),
                ]
            )
        )

    total_inicial = sum(p.get("cantidad", 1) for p in carrito_global)
    badge_text = ft.Text(
        ref=badge_carrito,
        value=str(total_inicial) if total_inicial > 0 else "",
        visible=total_inicial > 0,
        size=10, color="white", weight=ft.FontWeight.BOLD
    )

    sidebar = ft.Container(
        width=220,
        bgcolor="white",
        border=ft.border.only(right=ft.BorderSide(1, "#EEEEEE")),
        padding=ft.padding.symmetric(horizontal=16, vertical=28),
        content=ft.Column(
            spacing=4,
            controls=[
                ft.Row(spacing=10, controls=[
                    ft.Container(
                        width=36, height=36,
                        border_radius=8, bgcolor=BRAND,
                        alignment=ft.Alignment(0, 0),
                        content=ft.Text("CH", color="white", size=14,
                                        weight=ft.FontWeight.BOLD)
                    ),
                    ft.Text("CraftHub", size=15,
                            weight=ft.FontWeight.BOLD, color=BRAND)
                ]),
                ft.Container(height=28),
                ft.Text("MENU", size=10, color=MUTED,
                        weight=ft.FontWeight.BOLD),
                ft.Container(height=6),
                nav_item("🏠", "Destacado", activo=True),
                nav_item("📦", "Categorias"),
                nav_item("📅", "Eventos"),
                nav_item("⭐", "Recomendaciones"),
                nav_item("❤️", "Favoritos"),
                ft.Container(height=20),
                ft.Text("CUENTA", size=10, color=MUTED,
                        weight=ft.FontWeight.BOLD),
                ft.Container(height=6),
                nav_item("👤", f"Hola, {nombre_usuario}"),
                ft.Container(
                    border_radius=10,
                    bgcolor="transparent",
                    padding=ft.padding.symmetric(horizontal=12, vertical=10),
                    on_click=lambda _: ir_carrito() if ir_carrito else None,
                    content=ft.Row(
                        spacing=10,
                        controls=[
                            ft.Text("🛒", size=16),
                            ft.Text("Mi carrito", size=13, color=MUTED),
                            ft.Container(
                                width=20, height=20,
                                border_radius=10, bgcolor=BRAND,
                                alignment=ft.Alignment(0, 0),
                                visible=total_inicial > 0,
                                content=badge_text
                            ),
                        ]
                    )
                ),
                ft.Container(height=30),
                ft.Container(
                    border_radius=12, bgcolor=BRAND_LIGHT, padding=16,
                    content=ft.Column(spacing=6, controls=[
                        ft.Text("Eres artesano?", size=12,
                                weight=ft.FontWeight.BOLD, color=BRAND),
                        ft.Text("Empieza a vender\ntus productos hoy.",
                                size=11, color=MUTED),
                        ft.Container(height=4),
                        ft.ElevatedButton(
                            "Publicar", height=34,
                            bgcolor=BRAND, color="white",
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=8),
                                elevation=0,
                            )
                        )
                    ])
                ),
                ft.Container(height=16),
                ft.TextButton(
                    "Cerrar sesion",
                    style=ft.ButtonStyle(color=MUTED),
                    on_click=lambda _: ir_bienvenida()
                )
            ]
        )
    )

    topbar = ft.Container(
        bgcolor="white",
        padding=ft.padding.symmetric(horizontal=24, vertical=12),
        border=ft.border.only(bottom=ft.BorderSide(1, "#EEEEEE")),
        content=ft.Row(
            controls=[
                ft.Container(
                    expand=True, height=38,
                    border_radius=10, bgcolor=GRIS,
                    border=ft.border.all(1, "#E8E8E8"),
                    padding=ft.padding.symmetric(horizontal=14),
                    content=ft.Row(controls=[
                        ft.Text("🔍  Buscar productos artesanales...",
                                color="#BBBBBB", size=13),
                    ])
                ),
                ft.TextButton(
                    "🛒  Carrito",
                    on_click=lambda _: ir_carrito() if ir_carrito else None
                ),
            ]
        )
    )

    loading_view = ft.Column(
        ref=loading_ref,
        visible=True,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Container(height=60),
            ft.ProgressRing(color=BRAND, width=36, height=36,
                            stroke_width=3),
            ft.Container(height=12),
            ft.Text("Cargando productos...", color=MUTED, size=13),
        ]
    )

    cuerpo = ft.Column(
        ref=cuerpo_ref,
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        visible=False,
        spacing=20,
        controls=[
            ft.Container(
                border_radius=16, bgcolor=BRAND,
                padding=ft.padding.symmetric(horizontal=32, vertical=22),
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Column(spacing=6, controls=[
                            ft.Text(f"Bienvenido, {nombre_usuario}! 👋",
                                    size=22, weight=ft.FontWeight.BOLD,
                                    color="white"),
                            ft.Text("Descubre productos artesanales unicos",
                                    size=13, color="#FFCCCC"),
                        ]),
                        ft.ElevatedButton(
                            "Ver carrito", bgcolor="white", color=BRAND,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=8),
                                elevation=0,
                            ),
                            on_click=lambda _: ir_carrito() if ir_carrito else None
                        )
                    ]
                )
            ),
            ft.Text("Explorar por categoria", size=17,
                    weight=ft.FontWeight.BOLD, color=TEXTO),
            ft.Row(
                scroll=ft.ScrollMode.AUTO, spacing=8,
                controls=[chip_filtro(c) for c in categorias_filtro]
            ),
            ft.Text("Productos destacados", size=17,
                    weight=ft.FontWeight.BOLD, color=TEXTO),
            ft.Column(ref=contenedor_grid, spacing=16, controls=[]),
            ft.Container(height=20),
        ]
    )

    page.add(
        ft.Row(
            expand=True, spacing=0,
            controls=[
                sidebar,
                ft.Column(
                    expand=True, spacing=0,
                    controls=[
                        topbar,
                        ft.Container(
                            expand=True, padding=24,
                            content=ft.Column(
                                expand=True,
                                controls=[loading_view, cuerpo]
                            )
                        )
                    ]
                )
            ]
        )
    )
    page.update()

    # Cargar desde Supabase
    productos = cargar_productos()
    productos_cache["data"] = productos
    if contenedor_grid.current:
        contenedor_grid.current.controls = construir_grid(productos)
    if loading_ref.current:
        loading_ref.current.visible = False
    if cuerpo_ref.current:
        cuerpo_ref.current.visible = True
    page.update()