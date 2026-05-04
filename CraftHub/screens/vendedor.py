import flet as ft
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supabase_client import supabase

BRAND = "#800000"
BRAND_LIGHT = "#F5E8E8"
TEXTO = "#1A1A1A"
MUTED = "#888888"


def show_vendedor(page: ft.Page, ir_bienvenida, usuario):
    page.clean()

    perfil = usuario.get("perfil") or {}
    nombre_vendedor = perfil.get("nombre", "Vendedor")

    def cargar_productos():
        try:
            resp = supabase.table("productos").select("*").eq(
                "creador", nombre_vendedor).execute()
            return resp.data or []
        except:
            return []

    productos = cargar_productos()
    grid_ref = ft.Ref[ft.Column]()

    def precio_float(p):
        if isinstance(p, (int, float)):
            return float(p)
        return float(str(p).replace("$", "").replace(",", ""))

    def total_ventas():
        return sum(precio_float(p.get("precio", 0)) *
                   int(p.get("ventas", 0) or 0) for p in productos)

    def ventas_semana():
        return total_ventas() * 0.035

    def ventas_recientes():
        return total_ventas() * 0.015

    def actualizar_grid():
        if grid_ref.current:
            grid_ref.current.controls = construir_grid()
        page.update()

    def mostrar_formulario(producto_editar=None):
        es_edicion = producto_editar is not None
        dialogo_ref = {"obj": None}

        def cerrar(e=None):
            if dialogo_ref["obj"]:
                dialogo_ref["obj"].open = False
            page.overlay.clear()
            page.update()

        campo_nombre = ft.TextField(
            label="Nombre del producto",
            value=producto_editar.get("nombre", "") if es_edicion else "",
            border_radius=10,
            border_color="#DDDDDD",
            focused_border_color=BRAND,
        )
        campo_precio = ft.TextField(
            label="Precio (USD)",
            value=str(producto_editar.get("precio", "")) if es_edicion else "",
            border_radius=10,
            border_color="#DDDDDD",
            focused_border_color=BRAND,
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        campo_stock = ft.TextField(
            label="Stock disponible",
            value=str(producto_editar.get("stock", "0")) if es_edicion else "0",
            border_radius=10,
            border_color="#DDDDDD",
            focused_border_color=BRAND,
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        campo_descripcion = ft.TextField(
            label="Descripcion",
            value=producto_editar.get("descripcion", "") if es_edicion else "",
            border_radius=10,
            border_color="#DDDDDD",
            focused_border_color=BRAND,
            multiline=True,
            min_lines=2,
            max_lines=3,
        )
        campo_img = ft.TextField(
            label="URL de imagen",
            value=producto_editar.get("img", "") if es_edicion else "",
            border_radius=10,
            border_color="#DDDDDD",
            focused_border_color=BRAND,
        )

        categorias = [
            "Artesania", "Joyeria", "Vestir",
            "Mobiliario", "Instrumentos", "Accesorios", "Alimentos"
        ]
        dropdown_categoria = ft.Dropdown(
            label="Categoria",
            value=producto_editar.get("categoria", "Artesania") if es_edicion else "Artesania",
            border_radius=10,
            border_color="#DDDDDD",
            focused_border_color=BRAND,
            options=[ft.dropdown.Option(c) for c in categorias],
        )

        mensaje_error = ft.Text(
            value="", visible=False,
            color="#CC0000", size=12,
        )

        def guardar(e):
            nombre = campo_nombre.value.strip()
            precio_txt = campo_precio.value.strip()
            stock_txt = campo_stock.value.strip()

            if not nombre or not precio_txt:
                mensaje_error.value = "Nombre y precio son obligatorios"
                mensaje_error.visible = True
                page.update()
                return

            try:
                precio = float(precio_txt)
                stock = int(stock_txt) if stock_txt else 0
            except ValueError:
                mensaje_error.value = "Precio y stock deben ser numeros"
                mensaje_error.visible = True
                page.update()
                return

            datos = {
                "nombre": nombre,
                "precio": precio,
                "stock": stock,
                "categoria": dropdown_categoria.value,
                "descripcion": campo_descripcion.value.strip(),
                "img": campo_img.value.strip(),
                "creador": nombre_vendedor,
                "color": "#C4A882",
            }

            try:
                if es_edicion:
                    supabase.table("productos").update(datos).eq(
                        "id", producto_editar["id"]).execute()
                else:
                    supabase.table("productos").insert(datos).execute()

                productos[:] = cargar_productos()
                actualizar_grid()
                cerrar()

                page.snack_bar = ft.SnackBar(
                    content=ft.Text("Producto guardado", color="white"),
                    bgcolor=BRAND, duration=2000,
                )
                page.snack_bar.open = True
                page.update()

            except Exception as ex:
                mensaje_error.value = f"Error: {ex}"
                mensaje_error.visible = True
                page.update()

        dialogo = ft.AlertDialog(
            modal=True,
            title=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text(
                        "Editar producto" if es_edicion else "Nuevo producto",
                        size=18, weight=ft.FontWeight.BOLD, color=TEXTO
                    ),
                    ft.Container(
                        width=30, height=30,
                        border_radius=15,
                        bgcolor=BRAND_LIGHT,
                        alignment=ft.Alignment(0, 0),
                        on_click=cerrar,
                        content=ft.Text("x", size=14, color=BRAND,
                                        weight=ft.FontWeight.BOLD)
                    )
                ]
            ),
            content=ft.Container(
                width=480,
                height=420,
                content=ft.Column(
                    scroll=ft.ScrollMode.AUTO,
                    spacing=12,
                    controls=[
                        mensaje_error,
                        campo_nombre,
                        ft.Row(spacing=12, controls=[
                            ft.Container(expand=True, content=campo_precio),
                            ft.Container(expand=True, content=campo_stock),
                        ]),
                        dropdown_categoria,
                        campo_descripcion,
                        campo_img,
                    ]
                )
            ),
            actions=[
                ft.TextButton(
                    "Cancelar",
                    style=ft.ButtonStyle(color=MUTED),
                    on_click=cerrar
                ),
                ft.ElevatedButton(
                    "Guardar",
                    bgcolor=BRAND, color="white",
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                        elevation=0,
                    ),
                    on_click=guardar
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        dialogo_ref["obj"] = dialogo
        page.overlay.clear()
        page.overlay.append(dialogo)
        dialogo.open = True
        page.update()

    def stat_card(emoji, titulo, valor, subtitulo, activo=False):
        return ft.Container(
            expand=True,
            height=120,
            border_radius=14,
            bgcolor="white",
            border=ft.border.all(
                2 if activo else 1,
                BRAND if activo else "#EEEEEE"
            ),
            padding=20,
            content=ft.Column(
                spacing=4,
                controls=[
                    ft.Row(spacing=10, controls=[
                        ft.Container(
                            width=36, height=36,
                            border_radius=8,
                            bgcolor=BRAND_LIGHT,
                            alignment=ft.Alignment(0, 0),
                            content=ft.Text(emoji, size=18)
                        ),
                        ft.Text(titulo, size=12, color=MUTED),
                    ]),
                    ft.Text(f"${valor:,.2f}", size=26,
                            weight=ft.FontWeight.BOLD, color=TEXTO),
                    ft.Container(
                        border_radius=20,
                        bgcolor=BRAND_LIGHT,
                        padding=ft.padding.symmetric(horizontal=10, vertical=3),
                        content=ft.Text(subtitulo, size=10, color=BRAND)
                    )
                ]
            )
        )

    def producto_card(p):
        precio = precio_float(p.get("precio", 0))
        stock = p.get("stock", 0) or 0
        ventas = p.get("ventas", 0) or 0

        return ft.Container(
            border_radius=14,
            bgcolor="white",
            border=ft.border.all(1, "#EEEEEE"),
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            content=ft.Row(
                spacing=0,
                controls=[
                    ft.Container(
                        width=130, height=110,
                        bgcolor=p.get("color", "#C4A882"),
                        content=ft.Image(
                            src=p.get("img", ""),
                            fit="cover",
                            width=130, height=110,
                            error_content=ft.Container(
                                bgcolor=p.get("color", "#C4A882"),
                                alignment=ft.Alignment(0, 0),
                                content=ft.Text("📷", size=24)
                            )
                        )
                    ),
                    ft.Container(
                        expand=True,
                        padding=14,
                        content=ft.Column(
                            spacing=4,
                            controls=[
                                ft.Text(p.get("nombre", ""), size=14,
                                        weight=ft.FontWeight.BOLD,
                                        color=TEXTO),
                                ft.Text(f"${precio:.2f}", size=16,
                                        color=BRAND,
                                        weight=ft.FontWeight.BOLD),
                                ft.Text(
                                    f"Stock: {stock}    Ventas: {ventas}",
                                    size=11, color=MUTED
                                ),
                                ft.Row(spacing=8, controls=[
                                    ft.OutlinedButton(
                                        "Editar",
                                        height=32,
                                        style=ft.ButtonStyle(
                                            color=TEXTO,
                                            shape=ft.RoundedRectangleBorder(
                                                radius=8),
                                            side=ft.BorderSide(1, "#CCCCCC")
                                        ),
                                        on_click=lambda _, prod=p:
                                            mostrar_formulario(prod)
                                    ),
                                    ft.OutlinedButton(
                                        "Eliminar",
                                        height=32,
                                        style=ft.ButtonStyle(
                                            color="#CC0000",
                                            shape=ft.RoundedRectangleBorder(
                                                radius=8),
                                            side=ft.BorderSide(1, "#FFCCCC")
                                        ),
                                        on_click=lambda _, pid=p.get("id"):
                                            eliminar_producto(pid)
                                    ),
                                ])
                            ]
                        )
                    )
                ]
            )
        )

    def eliminar_producto(pid):
        try:
            supabase.table("productos").delete().eq("id", pid).execute()
            productos[:] = cargar_productos()
            actualizar_grid()
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Producto eliminado", color="white"),
                bgcolor=BRAND, duration=2000,
            )
            page.snack_bar.open = True
            page.update()
        except Exception as e:
            print("Error eliminando:", e)

    def construir_grid():
        if not productos:
            return [
                ft.Container(
                    padding=40,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Text("📦", size=40),
                            ft.Text("No tienes productos aun",
                                    size=16, color=MUTED),
                            ft.Container(height=12),
                            ft.ElevatedButton(
                                "+ Agregar primer producto",
                                bgcolor=BRAND, color="white",
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=10),
                                    elevation=0,
                                ),
                                on_click=lambda _: mostrar_formulario()
                            )
                        ]
                    )
                )
            ]
        filas = []
        fila = []
        for i, p in enumerate(productos):
            fila.append(ft.Container(expand=True, content=producto_card(p)))
            if len(fila) == 2 or i == len(productos) - 1:
                if len(fila) == 1:
                    fila.append(ft.Container(expand=True))
                filas.append(ft.Row(spacing=16, controls=fila))
                fila = []
        return filas

    header = ft.Container(
        bgcolor=BRAND,
        padding=ft.padding.symmetric(horizontal=24, vertical=14),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row(spacing=10, controls=[
                    ft.Container(
                        width=36, height=36,
                        border_radius=6,
                        bgcolor="white",
                        alignment=ft.Alignment(0, 0),
                        content=ft.Text("CH", color=BRAND, size=14,
                                        weight=ft.FontWeight.BOLD)
                    ),
                    ft.Text("CRAFTHUB", size=14,
                            weight=ft.FontWeight.BOLD, color="white"),
                ]),
                ft.Row(spacing=8, controls=[
                    ft.Container(
                        width=32, height=32,
                        border_radius=16,
                        bgcolor="white",
                        alignment=ft.Alignment(0, 0),
                        content=ft.Text("🔔", size=14)
                    ),
                    ft.Container(
                        width=32, height=32,
                        border_radius=16,
                        bgcolor="white",
                        alignment=ft.Alignment(0, 0),
                        content=ft.Text("💬", size=14)
                    ),
                    ft.Container(
                        width=32, height=32,
                        border_radius=16,
                        bgcolor="white",
                        alignment=ft.Alignment(0, 0),
                        on_click=lambda _: ir_bienvenida(),
                        content=ft.Text("🚪", size=14)
                    ),
                ])
            ]
        )
    )

    stats = ft.Container(
        padding=ft.padding.symmetric(horizontal=24, vertical=16),
        content=ft.Row(
            spacing=16,
            controls=[
                stat_card("📈", "Esta Semana", ventas_semana(), "+12.5%"),
                stat_card("💲", "Reciente", ventas_recientes(),
                          "Ultimas 24hr", activo=True),
                stat_card("📊", "Total Acumulado",
                          total_ventas(), "Total de ventas"),
            ]
        )
    )

    tabs = ft.Container(
        padding=ft.padding.symmetric(horizontal=24, vertical=8),
        content=ft.Row(
            spacing=4,
            controls=[
                ft.Container(
                    border_radius=20,
                    bgcolor=BRAND_LIGHT,
                    border=ft.border.all(1, BRAND),
                    padding=ft.padding.symmetric(horizontal=16, vertical=8),
                    content=ft.Text("Mis Productos", size=13,
                                    color=BRAND,
                                    weight=ft.FontWeight.W_500)
                ),
                ft.Container(
                    border_radius=20,
                    bgcolor="white",
                    border=ft.border.all(1, "#EEEEEE"),
                    padding=ft.padding.symmetric(horizontal=16, vertical=8),
                    content=ft.Text("Pedidos", size=13, color=MUTED)
                ),
                ft.Container(
                    border_radius=20,
                    bgcolor="white",
                    border=ft.border.all(1, "#EEEEEE"),
                    padding=ft.padding.symmetric(horizontal=16, vertical=8),
                    content=ft.Text("Estadisticas", size=13, color=MUTED)
                ),
            ]
        )
    )

    cuerpo = ft.Container(
        expand=True,
        padding=ft.padding.symmetric(horizontal=24, vertical=8),
        content=ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=16,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text("Mis productos", size=20,
                                weight=ft.FontWeight.BOLD, color=TEXTO),
                        ft.ElevatedButton(
                            "+ Nuevo producto",
                            bgcolor=BRAND, color="white",
                            height=40,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=10),
                                elevation=0,
                            ),
                            on_click=lambda _: mostrar_formulario()
                        )
                    ]
                ),
                ft.Column(
                    ref=grid_ref,
                    spacing=12,
                    controls=construir_grid()
                ),
                ft.Container(height=20),
            ]
        )
    )

    page.add(
        ft.Column(
            expand=True,
            spacing=0,
            controls=[header, stats, tabs, cuerpo]
        )
    )
    page.update()