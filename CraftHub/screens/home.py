import flet as ft
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supabase_client import supabase
from screens.menu_perfil import abrir_menu_perfil
from screens.componentes import craft_logo, tabler_icon

BRAND = "#800000"
BRAND_LIGHT = "#F5E8E8"
GRIS = "#F4F4F4"
TEXTO = "#1A1A1A"
MUTED = "#888888"


def show_home(
    page: ft.Page,
    ir_bienvenida,
    ir_carrito=None,
    carrito_global=None,
    usuario=None,
    ir_perfil=None,
    ir_notificaciones=None,
    ir_tracking=None,
    ir_calendario=None,
):
    page.clean()

    if carrito_global is None:
        carrito_global = []

    categoria_activa = {"v": "Todos"}
    busqueda_activa = {"v": ""}
    tab_activo = {"v": "Productos"}
    contenedor_grid = ft.Ref[ft.Column]()
    loading_ref = ft.Ref[ft.Column]()
    cuerpo_ref = ft.Ref[ft.Column]()
    productos_cache = {"data": []}
    chips_refs = {}
    menu_abierto = {"v": False}
    menu_ref = ft.Ref[ft.Container]()
    tab_refs = {}

    nombre_usuario = "Visitante"
    if usuario and usuario.get("perfil"):
        nombre_usuario = usuario["perfil"].get("nombre", "User").split()[0]

    categorias_filtro = [
        "Todos", "Artesanía", "Joyería", "Vestir",
        "Calzado", "Instrumentos", "Accesorios", "Alimentos"
    ]

    BANNER_PATH = "banner.png"

    def cargar_productos():
        try:
            resp = supabase.table("productos").select("*").execute()
            return resp.data or []
        except Exception as e:
            print("Error cargando productos:", e)
            return []

    def cargar_favoritos():
        user = (usuario or {}).get("user")
        if not user:
            return []
        try:
            resp = supabase.table("favoritos").select(
                "producto_id").eq("user_id", user.id).execute()
            return [r["producto_id"] for r in (resp.data or [])]
        except Exception as e:
            print("Error cargando favoritos:", e)
            return []

    ids_favoritos = {"data": set(cargar_favoritos())}

    def agregar_al_carrito(producto):
        stock_disponible = int(producto.get("stock", 0) or 0)
        cantidad_en_carrito = 0
        for item in carrito_global:
            if item.get("nombre") == producto.get("nombre"):
                cantidad_en_carrito = item.get("cantidad", 1)
                break
        if stock_disponible == 0:
            mostrar_snack("Este producto no tiene stock disponible.")
            return
        if cantidad_en_carrito >= stock_disponible:
            mostrar_snack(f"Solo hay {stock_disponible} unidades disponibles.")
            return
        for item in carrito_global:
            if item["nombre"] == producto["nombre"]:
                item["cantidad"] = item.get("cantidad", 1) + 1
                mostrar_snack(f"'{producto['nombre']}' agregado")
                return
        nuevo = dict(producto)
        nuevo["cantidad"] = 1
        carrito_global.append(nuevo)
        mostrar_snack(f"'{producto['nombre']}' agregado al carrito")

    def toggle_favorito(producto):
        user = (usuario or {}).get("user")
        prod_id = producto.get("id")
        if not user or not prod_id:
            mostrar_snack("Debes iniciar sesion para guardar favoritos.")
            return
        try:
            if prod_id in ids_favoritos["data"]:
                supabase.table("favoritos").delete().eq(
                    "user_id", user.id).eq("producto_id", prod_id).execute()
                ids_favoritos["data"].discard(prod_id)
            else:
                supabase.table("favoritos").insert({
                    "user_id": user.id,
                    "producto_id": prod_id,
                }).execute()
                ids_favoritos["data"].add(prod_id)
            mostrar_snack("Agregado a favoritos" if prod_id in ids_favoritos["data"] else "Eliminado de favoritos")
            page.update()
        except Exception as e:
            print("Error toggle favorito:", e)

    def es_favorito(producto):
        return producto.get("id") in ids_favoritos["data"]

    def mostrar_snack(msg):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(msg, color="white"),
            bgcolor=BRAND, duration=2000,
        )
        page.snack_bar.open = True
        page.update()

    def cargar_comentarios(producto):
        try:
            producto_id = producto.get("id")
            if not producto_id:
                return []
            resp = supabase.table("comentarios").select("*").eq(
                "producto_id", producto_id).order("created_at", desc=True).limit(20).execute()
            return resp.data or []
        except Exception as ex:
            print("No se pudieron cargar comentarios:", ex)
            return []

    def guardar_comentario(producto, texto):
        if not texto.strip():
            return False
        perfil = (usuario or {}).get("perfil") or {}
        user = (usuario or {}).get("user")
        try:
            supabase.table("comentarios").insert({
                "producto_id": producto.get("id"),
                "user_id": getattr(user, "id", None) if user else None,
                "nombre": perfil.get("nombre") or "Visitante",
                "comentario": texto.strip(),
            }).execute()
            return True
        except Exception as ex:
            print("No se pudo guardar comentario:", ex)
            return False

    def abrir_producto(producto):
        comentarios_ref = ft.Ref[ft.Column]()
        campo_comentario = ft.TextField(
            hint_text="Escribe un comentario sobre este producto...",
            multiline=True, min_lines=2, max_lines=3,
            border_radius=10, focused_border_color=BRAND, bgcolor="white",
        )

        def cerrar(e=None):
            page.overlay.clear()
            page.update()

        def comentario_item(c):
            return ft.Container(
                bgcolor="#FAFAFA", border_radius=10,
                border=ft.border.all(1, "#EEEEEE"), padding=10,
                content=ft.Column(spacing=3, controls=[
                    ft.Text(c.get("nombre", "Visitante"), size=12,
                            color=TEXTO, weight=ft.FontWeight.BOLD),
                    ft.Text(c.get("comentario", ""), size=12, color=MUTED),
                ]),
            )

        def pintar_comentarios():
            comentarios = cargar_comentarios(producto)
            if comentarios_ref.current:
                comentarios_ref.current.controls = (
                    [comentario_item(c) for c in comentarios]
                    if comentarios else
                    [ft.Text("Aun no hay comentarios. Se el primero en opinar.",
                             size=12, color=MUTED)]
                )
            page.update()

        def enviar_comentario(e):
            ok = guardar_comentario(producto, campo_comentario.value or "")
            if ok:
                campo_comentario.value = ""
                pintar_comentarios()
                mostrar_snack("Comentario publicado")
            else:
                mostrar_snack("No se pudo publicar.")

        img_url = producto.get("img", "")
        precio_raw = producto.get("precio", 0)
        precio = (
            float(precio_raw) if isinstance(precio_raw, (int, float))
            else float(str(precio_raw).replace("$", "").replace(",", "") or 0)
        )

        modal = ft.Container(
            expand=True, bgcolor="#00000066",
            alignment=ft.Alignment(0, 0), on_click=cerrar,
            content=ft.Container(
                width=720, bgcolor="white", border_radius=18,
                padding=0, clip_behavior=ft.ClipBehavior.HARD_EDGE,
                content=ft.Column(
                    spacing=0, scroll=ft.ScrollMode.AUTO,
                    controls=[
                        ft.Row(
                            spacing=0,
                            vertical_alignment=ft.CrossAxisAlignment.START,
                            controls=[
                                ft.Container(
                                    width=280, height=260,
                                    bgcolor=producto.get("color", "#C4A882"),
                                    content=ft.Image(
                                        src=img_url, fit="cover",
                                        width=280, height=260,
                                        error_content=ft.Container(
                                            bgcolor=producto.get("color", "#C4A882"),
                                            alignment=ft.Alignment(0, 0),
                                            content=ft.Text("Sin imagen", color="white",
                                                            weight=ft.FontWeight.BOLD),
                                        ),
                                    ),
                                ),
                                ft.Container(
                                    expand=True, padding=24,
                                    content=ft.Column(spacing=10, controls=[
                                        ft.Row(
                                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                            controls=[
                                                ft.Text(producto.get("nombre", "Producto"),
                                                        size=22, color=TEXTO,
                                                        weight=ft.FontWeight.BOLD),
                                                ft.Container(
                                                    width=30, height=30,
                                                    border_radius=15,
                                                    bgcolor=BRAND_LIGHT,
                                                    alignment=ft.Alignment(0, 0),
                                                    on_click=cerrar,
                                                    content=tabler_icon("x", size=16),
                                                ),
                                            ],
                                        ),
                                        ft.Text(f"${precio:.2f}", size=22,
                                                color=BRAND, weight=ft.FontWeight.BOLD),
                                        ft.Text(f"Creador: {producto.get('creador', 'Artesano CraftHub')}",
                                                size=13, color=TEXTO,
                                                weight=ft.FontWeight.W_600),
                                        ft.Text(producto.get("descripcion") or "Este producto aun no tiene descripcion.",
                                                size=13, color=MUTED),
                                        ft.Row(spacing=10, controls=[
                                            ft.Container(
                                                border_radius=18, bgcolor=BRAND_LIGHT,
                                                padding=ft.padding.symmetric(horizontal=12, vertical=5),
                                                content=ft.Text(producto.get("categoria", ""),
                                                                size=11, color=BRAND,
                                                                weight=ft.FontWeight.BOLD),
                                            ),
                                            ft.Text(f"Stock: {producto.get('stock', 0)}",
                                                    size=12, color=MUTED),
                                        ]),
                                        ft.Container(
                                            height=42, border_radius=10,
                                            bgcolor=BRAND, alignment=ft.Alignment(0, 0),
                                            on_click=lambda _, prod=producto: agregar_al_carrito(prod),
                                            content=ft.Row(
                                                alignment=ft.MainAxisAlignment.CENTER,
                                                spacing=8,
                                                controls=[
                                                    tabler_icon("shopping-cart", size=18),
                                                    ft.Text("Añadir al carrito",
                                                            color="white",
                                                            weight=ft.FontWeight.BOLD),
                                                ]
                                            ),
                                        ),
                                    ]),
                                ),
                            ],
                        ),
                        ft.Container(
                            padding=24, bgcolor="#FFFFFF",
                            content=ft.Column(spacing=12, controls=[
                                ft.Text("Comentarios del producto", size=16,
                                        color=TEXTO, weight=ft.FontWeight.BOLD),
                                ft.Column(ref=comentarios_ref, spacing=8, controls=[]),
                                campo_comentario,
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.END,
                                    controls=[
                                        ft.ElevatedButton(
                                            "Publicar comentario",
                                            bgcolor=BRAND, color="white",
                                            on_click=enviar_comentario,
                                        )
                                    ],
                                ),
                            ]),
                        ),
                    ],
                ),
            ),
        )
        page.overlay.clear()
        page.overlay.append(modal)
        pintar_comentarios()

    # ── PRODUCTO CARD ────────────────────────────────────────────
    def producto_card(p):
        nombre = p.get("nombre", "Producto")
        precio = p.get("precio", 0)
        precio_str = f"${float(precio):.2f}" if precio else "$0.00"
        categoria = p.get("categoria", "")
        origen = p.get("origen", p.get("region", "Panama"))
        color = p.get("color", "#C4A882")
        img_url = p.get("img", "")
        img_valida = img_url and img_url.startswith("http")
        fav = es_favorito(p)

        return ft.Container(
            width=340, height=370,
            border_radius=16, bgcolor="white",
            border=ft.border.all(1, "#EEEEEE"),
            shadow=ft.BoxShadow(blur_radius=10, color="#00000012",
                                offset=ft.Offset(0, 3)),
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            content=ft.Column(
                spacing=0,
                controls=[
                    ft.Container(
                        height=200, bgcolor=color,
                        on_click=lambda _, prod=p: abrir_producto(prod),
                        content=ft.Stack(controls=[
                            ft.Container(
                                width=340, height=200,
                                bgcolor=color,
                                alignment=ft.Alignment(0, 0),
                                content=tabler_icon("photo", size=48) if not img_valida else ft.Container(),
                            ),
                            *([ ft.Image(
                                src=img_url, fit="cover",
                                width=340, height=200,
                            )] if img_valida else []),
                            ft.Container(
                                alignment=ft.Alignment(1, -1),
                                padding=10,
                                content=ft.Container(
                                    width=32, height=32,
                                    border_radius=16, bgcolor="white",
                                    alignment=ft.Alignment(0, 0),
                                    on_click=lambda _, prod=p: toggle_favorito(prod),
                                    shadow=ft.BoxShadow(blur_radius=4,
                                                        color="#00000020",
                                                        offset=ft.Offset(0, 2)),
                                    content=tabler_icon(
                                        "heart-filled" if fav else "heart",
                                        size=18,
                                    ),
                                )
                            ),
                        ])
                    ),
                    ft.Container(
                        padding=ft.padding.symmetric(horizontal=16, vertical=12),
                        content=ft.Column(
                            spacing=6,
                            controls=[
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Text(nombre, size=15,
                                                weight=ft.FontWeight.BOLD,
                                                color=TEXTO),
                                        tabler_icon(
                                            "heart-filled" if fav else "heart",
                                            size=16,
                                        ),
                                    ]
                                ),
                                ft.Text(origen, size=12, color=MUTED),
                                ft.TextButton(
                                    "Ver descripcion y comentarios",
                                    style=ft.ButtonStyle(color=BRAND),
                                    on_click=lambda _, prod=p: abrir_producto(prod),
                                ),
                                ft.Container(
                                    border_radius=20, bgcolor=BRAND_LIGHT,
                                    padding=ft.padding.symmetric(horizontal=10, vertical=3),
                                    content=ft.Text(categoria, size=10,
                                                    color=BRAND,
                                                    weight=ft.FontWeight.W_500)
                                ),
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                    controls=[
                                        ft.Text(precio_str, size=20,
                                                color=BRAND,
                                                weight=ft.FontWeight.BOLD),
                                        ft.Container(
                                            height=34, border_radius=10,
                                            bgcolor=BRAND,
                                            padding=ft.padding.symmetric(
                                                horizontal=14, vertical=6),
                                            on_click=lambda _, prod=p: agregar_al_carrito(prod),
                                            content=ft.Row(
                                                spacing=6,
                                                controls=[
                                                    tabler_icon("shopping-cart", size=14),
                                                    ft.Text("Añadir", size=12,
                                                            color="white",
                                                            weight=ft.FontWeight.W_500),
                                                ]
                                            )
                                        )
                                    ]
                                ),
                            ]
                        )
                    )
                ]
            )
        )

    # ── GRID ─────────────────────────────────────────────────────
    def construir_grid(productos, filtro="Todos", busqueda="", modo="Productos"):
        if modo == "Favoritos":
            lista = [p for p in productos_cache["data"]
                     if p.get("id") in ids_favoritos["data"]]
        else:
            lista = productos if filtro == "Todos" else [
                p for p in productos if p.get("categoria", "") == filtro
            ]

        if busqueda.strip():
            termino = busqueda.strip().lower()
            lista = [
                p for p in lista
                if termino in (p.get("nombre") or "").lower()
                or termino in (p.get("categoria") or "").lower()
                or termino in (p.get("origen") or "").lower()
                or termino in (p.get("region") or "").lower()
                or termino in (p.get("creador") or "").lower()
            ]

        if not lista:
            icono_nombre = "heart" if modo == "Favoritos" else "search"
            msg = ("Aun no tienes favoritos" if modo == "Favoritos"
                   else "No se encontraron productos")
            return [ft.Container(
                padding=60, alignment=ft.Alignment(0, 0),
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        tabler_icon(icono_nombre, size=40),
                        ft.Text(msg, color=MUTED, size=14),
                    ]
                )
            )]

        filas = []
        fila_actual = []
        for i, p in enumerate(lista):
            fila_actual.append(producto_card(p))
            if len(fila_actual) == 4 or i == len(lista) - 1:
                filas.append(ft.Row(spacing=20, controls=fila_actual))
                fila_actual = []
        return filas

    def actualizar_grid():
        if contenedor_grid.current:
            contenedor_grid.current.controls = construir_grid(
                productos_cache["data"],
                categoria_activa["v"],
                busqueda_activa["v"],
                tab_activo["v"],
            )
        page.update()

    def on_busqueda(e):
        busqueda_activa["v"] = e.control.value
        actualizar_grid()

    # ── CHIPS ────────────────────────────────────────────────────
    def chip_filtro(cat):
        activo = cat == "Todos"
        cont = ft.Ref[ft.Container]()
        chips_refs[cat] = cont
        return ft.Container(
            ref=cont, border_radius=20,
            bgcolor=BRAND if activo else "white",
            border=ft.border.all(1, BRAND if activo else "#DDDDDD"),
            padding=ft.padding.symmetric(horizontal=16, vertical=8),
            on_click=lambda _, c=cat: filtrar(c),
            content=ft.Text(cat, size=12,
                            color="white" if activo else TEXTO,
                            weight=ft.FontWeight.W_500)
        )

    def filtrar(cat):
        for c, ref in chips_refs.items():
            if ref.current:
                es_activo = c == cat
                ref.current.bgcolor = BRAND if es_activo else "white"
                ref.current.border = ft.border.all(
                    1, BRAND if es_activo else "#DDDDDD")
                ref.current.content.color = "white" if es_activo else TEXTO
        categoria_activa["v"] = cat
        actualizar_grid()

    # ── TABS ─────────────────────────────────────────────────────
    tabs_data = ["Productos", "Favoritos", "Tutorial", "Carrito"]

    def cambiar_tab(tab):
        tab_activo["v"] = tab
        for t, ref in tab_refs.items():
            if ref.current:
                es = t == tab
                ref.current.border = ft.border.only(
                    bottom=ft.BorderSide(2, BRAND if es else "transparent"))
                ref.current.content.color = BRAND if es else MUTED
                ref.current.content.weight = (ft.FontWeight.BOLD if es
                                              else ft.FontWeight.NORMAL)
        if tab == "Carrito" and ir_carrito:
            ir_carrito()
            return
        actualizar_grid()

    def construir_tab(tab):
        activo = tab == "Productos"
        cont = ft.Ref[ft.Container]()
        tab_refs[tab] = cont
        return ft.Container(
            ref=cont,
            padding=ft.padding.symmetric(horizontal=16, vertical=12),
            border=ft.border.only(
                bottom=ft.BorderSide(2, BRAND if activo else "transparent")),
            on_click=lambda _, t=tab: cambiar_tab(t),
            content=ft.Text(tab, size=14,
                            color=BRAND if activo else MUTED,
                            weight=ft.FontWeight.BOLD if activo else ft.FontWeight.NORMAL)
        )

    # ── MENU DESPLEGABLE ─────────────────────────────────────────
    def toggle_menu(e):
        abrir_menu_perfil(
            page, usuario,
            ir_perfil=ir_perfil,
            ir_carrito=ir_carrito,
            ir_bienvenida=ir_bienvenida,
            modo="comprador",
        )

    menu_desplegable = ft.Container(
        ref=menu_ref, visible=False,
        left=0, top=50, width=200,
        bgcolor="white", border_radius=12,
        border=ft.border.all(1, "#EEEEEE"),
        shadow=ft.BoxShadow(blur_radius=20, color="#00000020",
                            offset=ft.Offset(0, 4)),
        padding=8,
        content=ft.Column(spacing=0, controls=[
            ft.Container(
                border_radius=8,
                padding=ft.padding.symmetric(horizontal=12, vertical=10),
                on_click=lambda _: (toggle_menu(None),
                                   ir_perfil() if ir_perfil else None),
                content=ft.Row(spacing=10, controls=[
                    tabler_icon("user", size=16),
                    ft.Text("Mi perfil", size=13, color=TEXTO),
                ])
            ),
            ft.Container(
                border_radius=8,
                padding=ft.padding.symmetric(horizontal=12, vertical=10),
                on_click=lambda _: (toggle_menu(None),
                                   ir_carrito() if ir_carrito else None),
                content=ft.Row(spacing=10, controls=[
                    tabler_icon("shopping-cart", size=16),
                    ft.Text("Mi carrito", size=13, color=TEXTO),
                ])
            ),
            ft.Divider(color="#EEEEEE"),
            ft.Container(
                border_radius=8,
                padding=ft.padding.symmetric(horizontal=12, vertical=10),
                on_click=lambda _: ir_bienvenida(),
                content=ft.Row(spacing=10, controls=[
                    tabler_icon("logout", size=16),
                    ft.Text("Cerrar sesion", size=13, color="#CC0000"),
                ])
            ),
        ])
    )

    # ── HEADER ───────────────────────────────────────────────────
    header = ft.Container(
        height=60, clip_behavior=ft.ClipBehavior.HARD_EDGE,
        content=ft.Stack(controls=[
            ft.Container(
                width=float("inf"), height=60,
                content=ft.Image(
                    src=BANNER_PATH, fit="cover",
                    width=float("inf"), height=60,
                    error_content=ft.Container(bgcolor=BRAND, height=60)
                ),
                alignment=ft.Alignment(1, 1),
            ),
            ft.Container(bgcolor="#00000055", height=60),
            ft.Container(
                height=60,
                padding=ft.padding.symmetric(horizontal=20, vertical=8),
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        craft_logo(42, on_click=toggle_menu),
                        ft.Text("CRAFTHUB", size=15,
                                weight=ft.FontWeight.BOLD, color="white"),
                        ft.Row(spacing=8, controls=[
                            ft.Container(
                                width=32, height=32, border_radius=16,
                                bgcolor="#FFFFFF33",
                                alignment=ft.Alignment(0, 0),
                                content=tabler_icon("bell", size=18),
                            ),
                            ft.Container(
                                width=32, height=32, border_radius=16,
                                bgcolor="#FFFFFF33",
                                alignment=ft.Alignment(0, 0),
                                content=tabler_icon("message", size=18),
                            ),
                            ft.Container(
                                width=32, height=32, border_radius=16,
                                bgcolor="#FFFFFF33",
                                alignment=ft.Alignment(0, 0),
                                on_click=lambda _: ir_carrito() if ir_carrito else None,
                                content=tabler_icon("shopping-cart", size=18),
                            ),
                        ])
                    ]
                )
            ),
            menu_desplegable,
        ])
    )

    # ── TABS ─────────────────────────────────────────────────────
    tabs_row = ft.Container(
        bgcolor="white",
        border=ft.border.only(bottom=ft.BorderSide(1, "#EEEEEE")),
        padding=ft.padding.symmetric(horizontal=20),
        content=ft.Row(spacing=0, controls=[construir_tab(t) for t in tabs_data])
    )

    # ── BUSQUEDA + FILTROS ────────────────────────────────────────
    campo_busqueda = ft.TextField(
        hint_text="Buscar por provincia, tipo o nombre...",
        hint_style=ft.TextStyle(color="#BBBBBB", size=13),
        border_radius=24, border_color="#E8E8E8",
        focused_border_color=BRAND, bgcolor="white",
        height=44,
        content_padding=ft.padding.symmetric(horizontal=20, vertical=10),
        on_change=on_busqueda,
        prefix_icon=ft.icons.SEARCH,
    )

    barra_busqueda = ft.Container(
        padding=ft.padding.symmetric(horizontal=20, vertical=12),
        bgcolor="#FAFAFA",
        content=ft.Row(spacing=12, controls=[
            ft.Container(expand=True, content=campo_busqueda),
            ft.Container(
                height=44, border_radius=24,
                border=ft.border.all(1, "#DDDDDD"),
                bgcolor="white",
                padding=ft.padding.symmetric(horizontal=16, vertical=10),
                content=ft.Row(spacing=8, controls=[
                    tabler_icon("adjustments-horizontal", size=16),
                    ft.Text("Filtros", size=13, color=TEXTO,
                            weight=ft.FontWeight.W_500),
                ])
            ),
        ])
    )

    # ── CHIPS ─────────────────────────────────────────────────────
    chips_row = ft.Container(
        padding=ft.padding.symmetric(horizontal=20, vertical=8),
        bgcolor="#FAFAFA",
        content=ft.Row(
            scroll=ft.ScrollMode.AUTO, spacing=8,
            controls=[chip_filtro(c) for c in categorias_filtro]
        )
    )

    # ── LOADING + GRID ────────────────────────────────────────────
    loading_view = ft.Column(
        ref=loading_ref, visible=True,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Container(height=60),
            ft.ProgressRing(color=BRAND, width=36, height=36, stroke_width=3),
            ft.Container(height=12),
            ft.Text("Cargando productos...", color=MUTED, size=13),
        ]
    )

    grid_view = ft.Column(
        ref=cuerpo_ref, visible=False,
        scroll=ft.ScrollMode.AUTO, expand=True, spacing=20,
        controls=[
            ft.Container(height=8),
            ft.Column(ref=contenedor_grid, spacing=20, controls=[]),
            ft.Container(height=30),
        ]
    )

    page.add(
        ft.Column(
            expand=True, spacing=0,
            controls=[
                header, tabs_row, barra_busqueda, chips_row,
                ft.Container(
                    expand=True,
                    padding=ft.padding.symmetric(horizontal=20),
                    content=ft.Column(
                        expand=True,
                        controls=[loading_view, grid_view]
                    )
                )
            ]
        )
    )
    page.update()

    productos = cargar_productos()
    productos_cache["data"] = productos
    if contenedor_grid.current:
        contenedor_grid.current.controls = construir_grid(productos)
    if loading_ref.current:
        loading_ref.current.visible = False
    if cuerpo_ref.current:
        cuerpo_ref.current.visible = True
    page.update()
