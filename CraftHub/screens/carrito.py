import flet as ft
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BRAND = "#800000"
BRAND_LIGHT = "#F5E8E8"
TEXTO = "#1A1A1A"
MUTED = "#888888"


def show_carrito(page: ft.Page, ir_home, carrito_global):
    page.clean()

    def precio_float(p):
        if isinstance(p, (int, float)):
            return float(p)
        return float(str(p).replace("$", "").replace(",", ""))

    cantidades = {i: {"cantidad": 1} for i in range(len(carrito_global))}
    resumen_ref = ft.Ref[ft.Column]()
    lista_ref = ft.Ref[ft.Column]()

    def mostrar_confirmacion():
        def cerrar(e):
            page.overlay.clear()
            page.update()

        def confirmar(e):
            carrito_global.clear()
            page.overlay.clear()
            page.update()
            ir_home()

        dialogo = ft.AlertDialog(
            title=ft.Text("Confirmar compra",
                          weight=ft.FontWeight.BOLD, color=TEXTO),
            content=ft.Text("¿Deseas proceder con el pago?",
                            color=MUTED),
            actions=[
                ft.TextButton(
                    "Cancelar",
                    style=ft.ButtonStyle(color=MUTED),
                    on_click=cerrar
                ),
                ft.ElevatedButton(
                    "Confirmar",
                    bgcolor=BRAND, color="white",
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                        elevation=0,
                    ),
                    on_click=confirmar
                ),
            ]
        )
        page.overlay.append(dialogo)
        dialogo.open = True
        page.update()

    def calcular_total():
        subtotal = sum(
            precio_float(carrito_global[i]["precio"]) * cantidades[i]["cantidad"]
            for i in range(len(carrito_global))
            if carrito_global[i] is not None
        )
        envio = 10.0 if subtotal > 0 else 0.0
        return subtotal, envio, subtotal + envio

    def actualizar_resumen():
        subtotal, envio, total = calcular_total()
        if resumen_ref.current:
            resumen_ref.current.controls = construir_resumen(subtotal, envio, total)
        page.update()

    def eliminar(idx):
        carrito_global[idx] = None
        if lista_ref.current:
            lista_ref.current.controls = construir_lista()
        actualizar_resumen()

    def cambiar_cantidad(idx, delta):
        nueva = cantidades[idx]["cantidad"] + delta
        if nueva >= 1:
            cantidades[idx]["cantidad"] = nueva
        if lista_ref.current:
            lista_ref.current.controls = construir_lista()
        actualizar_resumen()

    def construir_item(i, p):
        if p is None:
            return ft.Container()
        precio = precio_float(p["precio"])
        cant = cantidades[i]["cantidad"]

        return ft.Container(
            border_radius=12,
            bgcolor="white",
            border=ft.border.all(1, "#EEEEEE"),
            padding=16,
            margin=ft.margin.only(bottom=12),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=90, height=90,
                        border_radius=10,
                        bgcolor=p.get("color", "#C4A882"),
                        clip_behavior=ft.ClipBehavior.HARD_EDGE,
                        content=ft.Image(
                            src=p.get("img", ""),
                            fit="cover",
                            width=90, height=90,
                            error_content=ft.Container(
                                bgcolor=p.get("color", "#C4A882")
                            )
                        )
                    ),
                    ft.Column(
                        expand=True,
                        spacing=4,
                        controls=[
                            ft.Text(p.get("nombre", ""), size=15,
                                    weight=ft.FontWeight.BOLD, color=TEXTO),
                            ft.Text(p.get("origen", p.get("region", "")),
                                    size=12, color=MUTED),
                            ft.Row(
                                spacing=8,
                                controls=[
                                    ft.Container(
                                        width=32, height=32,
                                        border_radius=16,
                                        bgcolor=BRAND_LIGHT,
                                        alignment=ft.Alignment(0, 0),
                                        on_click=lambda _, idx=i: cambiar_cantidad(idx, -1),
                                        content=ft.Text("-", size=18,
                                                        color=BRAND,
                                                        weight=ft.FontWeight.BOLD)
                                    ),
                                    ft.Text(str(cant), size=14,
                                            weight=ft.FontWeight.BOLD,
                                            color=TEXTO),
                                    ft.Container(
                                        width=32, height=32,
                                        border_radius=16,
                                        bgcolor=BRAND,
                                        alignment=ft.Alignment(0, 0),
                                        on_click=lambda _, idx=i: cambiar_cantidad(idx, 1),
                                        content=ft.Text("+", size=18,
                                                        color="white",
                                                        weight=ft.FontWeight.BOLD)
                                    ),
                                ]
                            )
                        ]
                    ),
                    ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.END,
                        spacing=8,
                        controls=[
                            ft.Text(f"${precio * cant:.2f}", size=18,
                                    weight=ft.FontWeight.BOLD, color=TEXTO),
                            ft.TextButton(
                                "x",
                                style=ft.ButtonStyle(color=MUTED),
                                on_click=lambda _, idx=i: eliminar(idx)
                            )
                        ]
                    )
                ]
            )
        )

    def construir_lista():
        items = [construir_item(i, p)
                 for i, p in enumerate(carrito_global)
                 if p is not None]
        if not items:
            return [
                ft.Container(
                    alignment=ft.Alignment(0, 0),
                    padding=60,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Text("🛒", size=48),
                            ft.Text("Tu carrito esta vacio", size=18,
                                    color=MUTED),
                            ft.ElevatedButton(
                                "Ver productos",
                                bgcolor=BRAND, color="white",
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=10)
                                ),
                                on_click=lambda _: ir_home()
                            )
                        ]
                    )
                )
            ]
        return items

    def construir_resumen(subtotal, envio, total):
        return [
            ft.Text("Resumen", size=18,
                    weight=ft.FontWeight.BOLD, color=TEXTO),
            ft.Container(height=16),
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text("Subtotal", size=13, color=MUTED),
                    ft.Text(f"${subtotal:.2f}", size=13, color=TEXTO),
                ]
            ),
            ft.Container(height=8),
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text("Envio", size=13, color=MUTED),
                    ft.Text(f"${envio:.2f}", size=13, color=TEXTO),
                ]
            ),
            ft.Container(height=12),
            ft.Divider(color="#EEEEEE"),
            ft.Container(height=12),
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text("Total", size=16,
                            weight=ft.FontWeight.BOLD, color=TEXTO),
                    ft.Text(f"${total:.2f}", size=16,
                            weight=ft.FontWeight.BOLD, color=BRAND),
                ]
            ),
            ft.Container(height=20),
            ft.ElevatedButton(
                "Realizar compra",
                width=float("inf"),
                height=50,
                bgcolor=BRAND,
                color="white",
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=10),
                    elevation=0,
                ),
                on_click=lambda _: mostrar_confirmacion()
            )
        ]

    subtotal, envio, total = calcular_total()
    items_count = sum(1 for p in carrito_global if p is not None)

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
                    ft.TextButton(
                        "<- Volver",
                        style=ft.ButtonStyle(color="white"),
                        on_click=lambda _: ir_home()
                    )
                ])
            ]
        )
    )

    tabs = ft.Container(
        bgcolor="white",
        border=ft.border.only(bottom=ft.BorderSide(1, "#EEEEEE")),
        padding=ft.padding.symmetric(horizontal=24, vertical=8),
        content=ft.Row(
            spacing=4,
            controls=[
                ft.TextButton("Productos",
                              style=ft.ButtonStyle(color=MUTED),
                              on_click=lambda _: ir_home()),
                ft.TextButton("Favoritos",
                              style=ft.ButtonStyle(color=MUTED)),
                ft.TextButton("Tutorial",
                              style=ft.ButtonStyle(color=MUTED)),
                ft.Container(
                    border_radius=20,
                    bgcolor=BRAND,
                    padding=ft.padding.symmetric(horizontal=16, vertical=6),
                    content=ft.Row(spacing=8, controls=[
                        ft.Text("Carrito", size=13, color="white",
                                weight=ft.FontWeight.W_500),
                        ft.Container(
                            width=22, height=22,
                            border_radius=11,
                            bgcolor="white",
                            alignment=ft.Alignment(0, 0),
                            content=ft.Text(str(items_count), size=11,
                                            color=BRAND,
                                            weight=ft.FontWeight.BOLD)
                        )
                    ])
                ),
            ]
        )
    )

    cuerpo = ft.Container(
        expand=True,
        padding=24,
        content=ft.Row(
            expand=True,
            spacing=24,
            vertical_alignment=ft.CrossAxisAlignment.START,
            controls=[
                ft.Container(
                    expand=True,
                    content=ft.Column(
                        ref=lista_ref,
                        scroll=ft.ScrollMode.AUTO,
                        controls=construir_lista()
                    )
                ),
                ft.Container(
                    width=300,
                    bgcolor="white",
                    border_radius=16,
                    border=ft.border.all(1, "#EEEEEE"),
                    padding=24,
                    content=ft.Column(
                        ref=resumen_ref,
                        controls=construir_resumen(subtotal, envio, total)
                    )
                )
            ]
        )
    )

    page.add(
        ft.Column(
            expand=True,
            spacing=0,
            controls=[header, tabs, cuerpo]
        )
    )
    page.update()