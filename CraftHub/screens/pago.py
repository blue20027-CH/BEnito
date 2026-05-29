import flet as ft
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supabase_client import supabase
from screens.envio import calcular_envio
from screens.componentes import craft_logo, craft_banner_header, tabler_icon

BRAND = "#800000"
BRAND_LIGHT = "#F5E8E8"
TEXTO = "#1A1A1A"
MUTED = "#888888"


def show_pago(page: ft.Page, ir_home, carrito_global, usuario):
    page.clean()

    perfil = usuario.get("perfil") or {}
    user = usuario.get("user")
    metodo_activo = {"v": None}
    vista_ref = ft.Ref[ft.Column]()

    def ubicacion_vendedor(nombre):
        try:
            resp = supabase.table("perfiles").select("ubicacion").eq(
                "nombre", nombre).execute()
            if resp.data:
                return resp.data[0].get("ubicacion")
        except Exception as ex:
            print("Error buscando ubicacion del vendedor:", ex)
        return None

    def calcular_subtotal():
        total = 0
        for p in carrito_global:
            if p is None:
                continue
            precio = p.get("precio", 0)
            if isinstance(precio, (int, float)):
                precio = float(precio)
            else:
                precio = float(str(precio).replace("$", "").replace(",", ""))
            total += precio * p.get("cantidad", 1)
        return total

    def calcular_resumen():
        subtotal = calcular_subtotal()
        envio, detalle_envio = calcular_envio(
            carrito_global,
            perfil.get("ubicacion", "Panama"),
            ubicacion_vendedor,
        ) if subtotal > 0 else (0.0, [])
        return subtotal, envio, subtotal + envio, detalle_envio

    def calcular_total():
        return calcular_resumen()[2]

    def guardar_pedido(metodo, datos_pago):
        try:
            subtotal, envio, total, detalle_envio = calcular_resumen()
            productos_lista = [
                {
                    "id": p.get("id"),
                    "nombre": p.get("nombre"),
                    "precio": p.get("precio"),
                    "cantidad": p.get("cantidad", 1),
                    "creador": p.get("creador"),
                    "img": p.get("img"),
                    "categoria": p.get("categoria"),
                    "estado": "pendiente",
                }
                for p in carrito_global if p is not None
            ]
            pedido = {
                "comprador_id": user.id if user else None,
                "comprador_nombre": perfil.get("nombre", ""),
                "productos": productos_lista,
                "total": total,
                "metodo_pago": metodo,
                "estado": "pendiente",
                "direccion": perfil.get("ubicacion", ""),
                "telefono": perfil.get("telefono", ""),
                "datos_pago": {
                    **datos_pago,
                    "subtotal": subtotal,
                    "envio": envio,
                    "detalle_envio": detalle_envio,
                },
            }
            supabase.table("pedidos").insert(pedido).execute()

            # Restar stock de cada producto comprado
            for item in productos_lista:
                nombre = item.get("nombre")
                cantidad = item.get("cantidad", 1)
                try:
                    resp = supabase.table("productos").select("id, stock").eq(
                        "nombre", nombre).execute()
                    if resp.data:
                        prod = resp.data[0]
                        stock_actual = int(prod.get("stock", 0) or 0)
                        nuevo_stock = max(0, stock_actual - cantidad)
                        supabase.table("productos").update(
                            {"stock": nuevo_stock}
                        ).eq("id", prod["id"]).execute()
                        print(f"Stock de '{nombre}' actualizado: {stock_actual} -> {nuevo_stock}")
                except Exception as ex:
                    print(f"Error actualizando stock de {nombre}:", ex)
                    
                    # Enviar notificaciones a los vendedores
            vendedores_notificados = set()
            for item in productos_lista:
                creador = item.get("creador")
                if not creador or creador in vendedores_notificados:
                    continue
                try:
                    # Buscar user_id del vendedor
                    resp = supabase.table("perfiles").select(
                        "user_id").eq("nombre", creador).execute()
                    if resp.data:
                        vendedor_user_id = resp.data[0].get("user_id")
                        nombre_prod = item.get("nombre", "un producto")
                        cantidad = item.get("cantidad", 1)
                        supabase.table("notificaciones").insert({
                            "user_id": vendedor_user_id,
                            "titulo": "Nueva venta",
                            "mensaje": f"Vendiste {cantidad}x {nombre_prod}. Preparalo para enviarlo antes de 24 horas.",
                            "tipo": "venta",
                            "leida": False,
                        }).execute()
                        vendedores_notificados.add(creador)
                except Exception as ex:
                    print(f"Error enviando notificacion a {creador}:", ex)

            return True
        except Exception as ex:
            print("Error guardando pedido:", ex)
            return False

    def mostrar_exito():
        page.clean()
        page.add(
            ft.Container(
                expand=True,
                alignment=ft.Alignment(0, 0),
                bgcolor="#FAFAFA",
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=16,
                    controls=[
                        ft.Container(
                            width=80, height=80,
                            border_radius=40,
                            bgcolor=BRAND_LIGHT,
                            alignment=ft.Alignment(0, 0),
                            content=tabler_icon("check", size=42)
                        ),
                        ft.Text("Pago exitoso", size=26,
                                weight=ft.FontWeight.BOLD, color=TEXTO),
                        ft.Text("Tu pedido ha sido registrado correctamente.",
                                size=14, color=MUTED),
                        ft.Text(f"Total pagado: ${calcular_total():.2f}",
                                size=16, color=BRAND,
                                weight=ft.FontWeight.BOLD),
                        ft.Container(height=10),
                        ft.ElevatedButton(
                            "Volver al inicio",
                            bgcolor=BRAND, color="white",
                            height=48, width=220,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=12),
                                elevation=0,
                            ),
                            on_click=lambda _: (
                                carrito_global.clear(),
                                ir_home()
                            )
                        )
                    ]
                )
            )
        )
        page.update()

    # ── FORMULARIO TARJETA ───────────────────────────────────────
    def vista_tarjeta():
        campo_nombre = ft.TextField(
            label="Nombre en la tarjeta",
            border_radius=10, border_color="#DDDDDD",
            focused_border_color=BRAND, bgcolor="white",
        )
        campo_numero = ft.TextField(
            label="Numero de tarjeta",
            border_radius=10, border_color="#DDDDDD",
            focused_border_color=BRAND, bgcolor="white",
            keyboard_type=ft.KeyboardType.NUMBER,
            max_length=16,
        )
        campo_vence = ft.TextField(
            label="Fecha de vencimiento (MM/AA)",
            border_radius=10, border_color="#DDDDDD",
            focused_border_color=BRAND, bgcolor="white",
            max_length=5,
        )
        campo_cvv = ft.TextField(
            label="CVV",
            border_radius=10, border_color="#DDDDDD",
            focused_border_color=BRAND, bgcolor="white",
            password=True, max_length=4,
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        error = ft.Text("", color="#CC0000", size=12, visible=False)

        def pagar(e):
            if not campo_nombre.value.strip() or not campo_numero.value.strip():
                error.value = "Por favor completa todos los campos."
                error.visible = True
                page.update()
                return
            if len(campo_numero.value.strip()) < 16:
                error.value = "El numero de tarjeta debe tener 16 digitos."
                error.visible = True
                page.update()
                return

            datos_pago = {
                "nombre_tarjeta": campo_nombre.value.strip(),
                "ultimos_4": campo_numero.value.strip()[-4:],
                "vence": campo_vence.value.strip(),
            }
            ok = guardar_pedido("Tarjeta", datos_pago)
            if ok:
                mostrar_exito()
            else:
                error.value = "Error al procesar el pago. Intenta de nuevo."
                error.visible = True
                page.update()

        return ft.Container(
            width=560,
            bgcolor="white",
            border_radius=20,
            border=ft.border.all(1, "#EEEEEE"),
            padding=36,
            shadow=ft.BoxShadow(blur_radius=20, color="#00000010",
                                offset=ft.Offset(0, 4)),
            content=ft.Column(
                spacing=16,
                controls=[
                    ft.Row(controls=[
                        ft.Container(
                            width=32, height=32,
                            border_radius=16,
                            bgcolor=BRAND_LIGHT,
                            alignment=ft.Alignment(0, 0),
                            on_click=lambda _: mostrar_seleccion(),
                            content=tabler_icon("arrow-left", size=16)
                        ),
                    ]),
                    ft.Text("Tarjeta de debito o Credito", size=22,
                            weight=ft.FontWeight.BOLD, color=TEXTO,
                            text_align=ft.TextAlign.CENTER),
                    ft.Row(spacing=8, controls=[
                        tabler_icon("credit-card", size=20),
                        ft.Text("Visa  •  Mastercard  •  American Express",
                                size=12, color=MUTED),
                    ]),
                    ft.Divider(color="#EEEEEE"),
                    campo_nombre,
                    campo_numero,
                    ft.Row(spacing=12, controls=[
                        ft.Container(expand=True, content=campo_vence),
                        ft.Container(expand=True, content=campo_cvv),
                    ]),
                    error,
                    ft.Container(height=4),
                    ft.Container(
                        height=50,
                        border_radius=12,
                        bgcolor=BRAND,
                        alignment=ft.Alignment(0, 0),
                        on_click=pagar,
                        content=ft.Text(
                            f"Pagar ${calcular_total():.2f}",
                            color="white", size=16,
                            weight=ft.FontWeight.BOLD
                        )
                    )
                ]
            )
        )

    # ── FORMULARIO TRANSFERENCIA ─────────────────────────────────
    def vista_transferencia():
        campo_banco = ft.Dropdown(
            label="Banco",
            border_radius=10,
            border_color="#DDDDDD",
            focused_border_color=BRAND,
            options=[
                ft.dropdown.Option("Banistmo"),
                ft.dropdown.Option("Banco Nacional"),
                ft.dropdown.Option("BAC Credomatic"),
                ft.dropdown.Option("Global Bank"),
                ft.dropdown.Option("Caja de Ahorros"),
            ]
        )
        campo_titular = ft.TextField(
            label="Nombre del titular",
            border_radius=10, border_color="#DDDDDD",
            focused_border_color=BRAND, bgcolor="white",
        )
        campo_cuenta = ft.TextField(
            label="Numero de cuenta",
            border_radius=10, border_color="#DDDDDD",
            focused_border_color=BRAND, bgcolor="white",
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        campo_referencia = ft.TextField(
            label="Numero de referencia",
            border_radius=10, border_color="#DDDDDD",
            focused_border_color=BRAND, bgcolor="white",
        )
        error = ft.Text("", color="#CC0000", size=12, visible=False)

        def pagar(e):
            if not campo_banco.value or not campo_titular.value.strip():
                error.value = "Por favor completa todos los campos."
                error.visible = True
                page.update()
                return

            datos_pago = {
                "banco": campo_banco.value,
                "titular": campo_titular.value.strip(),
                "cuenta": campo_cuenta.value.strip(),
                "referencia": campo_referencia.value.strip(),
            }
            ok = guardar_pedido("Transferencia", datos_pago)
            if ok:
                mostrar_exito()
            else:
                error.value = "Error al procesar. Intenta de nuevo."
                error.visible = True
                page.update()

        return ft.Container(
            width=560,
            bgcolor="white",
            border_radius=20,
            border=ft.border.all(1, "#EEEEEE"),
            padding=36,
            shadow=ft.BoxShadow(blur_radius=20, color="#00000010",
                                offset=ft.Offset(0, 4)),
            content=ft.Column(
                spacing=16,
                controls=[
                    ft.Row(controls=[
                        ft.Container(
                            width=32, height=32,
                            border_radius=16,
                            bgcolor=BRAND_LIGHT,
                            alignment=ft.Alignment(0, 0),
                            on_click=lambda _: mostrar_seleccion(),
                            content=tabler_icon("arrow-left", size=16)
                        ),
                    ]),
                    ft.Text("Transferencia Bancaria", size=22,
                            weight=ft.FontWeight.BOLD, color=TEXTO,
                            text_align=ft.TextAlign.CENTER),
                    ft.Text("Realiza tu pago desde tu banco",
                            size=13, color=MUTED,
                            text_align=ft.TextAlign.CENTER),
                    ft.Divider(color="#EEEEEE"),
                    campo_banco,
                    campo_titular,
                    campo_cuenta,
                    campo_referencia,
                    error,
                    ft.Container(height=4),
                    ft.Container(
                        height=50,
                        border_radius=12,
                        bgcolor=BRAND,
                        alignment=ft.Alignment(0, 0),
                        on_click=pagar,
                        content=ft.Text(
                            f"Confirmar transferencia ${calcular_total():.2f}",
                            color="white", size=15,
                            weight=ft.FontWeight.BOLD
                        )
                    )
                ]
            )
        )

    # ── FORMULARIO YAPPY/PAYPAL/BANISTMO ────────────────────────
    def vista_billetera(nombre):
        campo_telefono = ft.TextField(
            label="Numero de telefono" if nombre != "PayPal" else "Correo de PayPal",
            border_radius=10, border_color="#DDDDDD",
            focused_border_color=BRAND, bgcolor="white",
            keyboard_type=ft.KeyboardType.PHONE if nombre != "PayPal"
            else ft.KeyboardType.EMAIL,
        )
        error = ft.Text("", color="#CC0000", size=12, visible=False)

        def pagar(e):
            if not campo_telefono.value.strip():
                error.value = "Por favor ingresa el dato requerido."
                error.visible = True
                page.update()
                return

            datos_pago = {
                "billetera": nombre,
                "contacto": campo_telefono.value.strip(),
            }
            ok = guardar_pedido(nombre, datos_pago)
            if ok:
                mostrar_exito()
            else:
                error.value = "Error al procesar. Intenta de nuevo."
                error.visible = True
                page.update()

        return ft.Container(
            width=560,
            bgcolor="white",
            border_radius=20,
            border=ft.border.all(1, "#EEEEEE"),
            padding=36,
            shadow=ft.BoxShadow(blur_radius=20, color="#00000010",
                                offset=ft.Offset(0, 4)),
            content=ft.Column(
                spacing=16,
                controls=[
                    ft.Row(controls=[
                        ft.Container(
                            width=32, height=32,
                            border_radius=16,
                            bgcolor=BRAND_LIGHT,
                            alignment=ft.Alignment(0, 0),
                            on_click=lambda _: mostrar_seleccion(),
                            content=tabler_icon("arrow-left", size=16)
                        ),
                    ]),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=10,
                        controls=[
                            tabler_icon("wallet", size=22),
                            ft.Text(nombre,
                            size=22, weight=ft.FontWeight.BOLD,
                                    color=TEXTO, text_align=ft.TextAlign.CENTER),
                        ],
                    ),
                    ft.Text(
                        f"Paga con tu cuenta de {nombre}",
                        size=13, color=MUTED,
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.Divider(color="#EEEEEE"),
                    campo_telefono,
                    error,
                    ft.Container(height=4),
                    ft.Container(
                        height=50,
                        border_radius=12,
                        bgcolor=BRAND,
                        alignment=ft.Alignment(0, 0),
                        on_click=pagar,
                        content=ft.Text(
                            f"Pagar ${calcular_total():.2f} con {nombre}",
                            color="white", size=15,
                            weight=ft.FontWeight.BOLD
                        )
                    )
                ]
            )
        )

    # ── SELECCION DE METODO ──────────────────────────────────────
    def mostrar_seleccion():
        if vista_ref.current:
            vista_ref.current.controls = [seleccion_view()]
        page.update()

    def mostrar_vista(vista):
        if vista_ref.current:
            vista_ref.current.controls = [vista]
        page.update()

    def opcion_metodo(icono, titulo, subtitulo, accion):
        return ft.Container(
            height=64,
            border_radius=10,
            bgcolor="white",
            border=ft.border.all(1, "#D95D5D" if "Tarjeta" in titulo else "#D6D6D6"),
            padding=ft.padding.symmetric(horizontal=22, vertical=10),
            on_click=accion,
            shadow=ft.BoxShadow(blur_radius=8, color="#00000010",
                                offset=ft.Offset(0, 3)),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Row(spacing=16, controls=[
                        ft.Container(
                            width=44, height=44,
                            border_radius=22,
                            bgcolor="#A94747",
                            alignment=ft.Alignment(0, 0),
                            content=tabler_icon(icono, size=22)
                        ),
                        ft.Column(spacing=2, controls=[
                            ft.Text(titulo, size=14,
                                    weight=ft.FontWeight.BOLD, color=TEXTO),
                            ft.Text(subtitulo, size=11, color=MUTED),
                        ])
                    ]),
                    tabler_icon("chevron-right", size=22),
                ]
            )
        )

    def billetera_btn(icono, nombre):
        return ft.Container(
            expand=True,
            height=76,
            border_radius=12,
            bgcolor="white",
            border=ft.border.all(1, "#F0B7B7" if nombre == "Banistmo" else "#E6E6E6"),
            alignment=ft.Alignment(0, 0),
            on_click=lambda _: mostrar_vista(vista_billetera(nombre)),
            shadow=ft.BoxShadow(blur_radius=8, color="#0000000D", offset=ft.Offset(0, 2)),
            content=ft.Column(
                spacing=4,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    tabler_icon(icono, size=22),
                    ft.Text(
                        nombre,
                        size=16 if nombre != "Banistmo" else 15,
                        weight=ft.FontWeight.BOLD,
                        color="#1456A7" if nombre in ["PayPal", "Banistmo"] else "#2878B8",
                    ),
                ],
            )
        )

    def seleccion_view():
        subtotal, envio, total, detalle_envio = calcular_resumen()
        return ft.Container(
            width=560,
            bgcolor=BRAND_LIGHT,
            border_radius=20,
            border=ft.border.all(1, "#EEEEEE"),
            padding=32,
            shadow=ft.BoxShadow(blur_radius=20, color="#00000010",
                                offset=ft.Offset(0, 4)),
            content=ft.Column(
                spacing=16,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text("Elige tu metodo de pago", size=22,
                            weight=ft.FontWeight.BOLD, color=BRAND,
                            text_align=ft.TextAlign.CENTER),
                    ft.Container(height=4),
                    opcion_metodo(
                        "credit-card", "Tarjeta de debito o Credito",
                        "Visa, Mastercard, American Express",
                        lambda _: mostrar_vista(vista_tarjeta())
                    ),
                    opcion_metodo(
                        "building-bank", "Transferencia Bancaria",
                        "Realiza tu pago desde tu banco",
                        lambda _: mostrar_vista(vista_transferencia())
                    ),
                    ft.Container(height=4),
                    ft.Text("O elige otra forma de pago",
                            size=12, color=MUTED),
                    ft.Row(
                        spacing=12,
                        controls=[
                            billetera_btn("wallet", "Yappy"),
                            billetera_btn("wallet", "PayPal"),
                            billetera_btn("wallet", "Banistmo"),
                        ]
                    ),
                    ft.Container(height=8),
                    ft.Container(
                        bgcolor="white",
                        border_radius=12,
                        border=ft.border.all(1, "#E7D6D6"),
                        padding=14,
                        content=ft.Column(
                            spacing=8,
                            controls=[
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Text("Subtotal", size=12, color=MUTED),
                                        ft.Text(f"${subtotal:.2f}", size=12, color=TEXTO),
                                    ],
                                ),
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Text("Envio por distancia", size=12, color=MUTED),
                                        ft.Text(f"${envio:.2f}", size=12, color=TEXTO),
                                    ],
                                ),
                            ] + [
                                ft.Text(
                                    f"{d['vendedor']}: {d['distancia_km']} km - ${d['costo']:.2f}",
                                    size=10,
                                    color=MUTED,
                                )
                                for d in detalle_envio
                            ],
                        ),
                    ),
                    ft.Text(
                        f"Total a pagar: ${total:.2f}",
                        size=14, color=BRAND,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER
                    ),
                ]
            )
        )

    # ── HEADER ───────────────────────────────────────────────────
    def seleccion_view():
        subtotal, envio, total, detalle_envio = calcular_resumen()
        return ft.Container(
            width=720,
            bgcolor="#C99191",
            padding=28,
            shadow=ft.BoxShadow(blur_radius=28, color="#0000001A", offset=ft.Offset(0, 8)),
            content=ft.Container(
                bgcolor="white",
                border=ft.border.all(1, BRAND),
                content=ft.Column(
                    spacing=0,
                    controls=[
                        ft.Container(
                            height=68,
                            bgcolor="#E8D5D5",
                            alignment=ft.Alignment(0, 0),
                            content=ft.Text("Elige tu metodo de pago", size=22, weight=ft.FontWeight.BOLD, color=BRAND),
                        ),
                        ft.Container(
                            padding=ft.padding.symmetric(horizontal=36, vertical=22),
                            content=ft.Column(
                                spacing=16,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    opcion_metodo("credit-card", "Tarjeta de debito o Credito", "Visa, Mastercard, American Express", lambda _: mostrar_vista(vista_tarjeta())),
                                    opcion_metodo("building-bank", "Transferencia Bancaria", "Realiza tu pago desde tu banco", lambda _: mostrar_vista(vista_transferencia())),
                                    ft.Container(height=10),
                                    ft.Text("O elige otra forma de pago", size=12, color=TEXTO),
                                    ft.Row(spacing=16, controls=[
                                        billetera_btn("wallet", "Yappy"),
                                        billetera_btn("wallet", "PayPal"),
                                        billetera_btn("wallet", "Banistmo"),
                                    ]),
                                    ft.Container(
                                        bgcolor="#FAFAFA",
                                        border_radius=10,
                                        border=ft.border.all(1, "#EEEEEE"),
                                        padding=12,
                                        content=ft.Column(
                                            spacing=6,
                                            controls=[
                                                ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                                                    ft.Text("Subtotal", size=12, color=MUTED),
                                                    ft.Text(f"${subtotal:.2f}", size=12, color=TEXTO),
                                                ]),
                                                ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                                                    ft.Text("Envio", size=12, color=MUTED),
                                                    ft.Text(f"${envio:.2f}", size=12, color=TEXTO),
                                                ]),
                                                ft.Divider(height=8, color="#E6E6E6"),
                                                ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                                                    ft.Text("Total", size=14, color=TEXTO, weight=ft.FontWeight.BOLD),
                                                    ft.Text(f"${total:.2f}", size=16, color=BRAND, weight=ft.FontWeight.BOLD),
                                                ]),
                                            ] + [
                                                ft.Text(f"{d['vendedor']}: {d['distancia_km']} km - ${d['costo']:.2f}", size=10, color=MUTED)
                                                for d in detalle_envio
                                            ],
                                        ),
                                    ),
                                ],
                            ),
                        ),
                    ],
                ),
            ),
        )

    header = ft.Container(
        bgcolor=BRAND,
        padding=ft.padding.symmetric(horizontal=24, vertical=14),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row(spacing=10, controls=[
                    craft_logo(36, bgcolor="white", radius=6),
                    ft.Text("Metodo de Pago", size=16,
                            weight=ft.FontWeight.BOLD, color="white"),
                ]),
                ft.TextButton(
                    "Volver",
                    style=ft.ButtonStyle(color="white"),
                    on_click=lambda _: ir_home()
                )
            ]
        )
    )

    # ── LAYOUT ───────────────────────────────────────────────────
    header = craft_banner_header(
        "Metodo de Pago",
        None,
        height=66,
        actions=[
            ft.TextButton(
                "Volver",
                style=ft.ButtonStyle(color="white"),
                on_click=lambda _: ir_home()
            )
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
                    bgcolor="#FAFAFA",
                    alignment=ft.Alignment(0, 0),
                    content=ft.Column(
                        ref=vista_ref,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.CENTER,
                        expand=True,
                        controls=[seleccion_view()]
                    )
                )
            ]
        )
    )
    page.update()
