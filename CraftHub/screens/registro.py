import flet as ft
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supabase_client import supabase
from screens.componentes import craft_logo

BRAND = "#800000"
BRAND_LIGHT = "#F5E8E8"
TEXTO = "#1A1A1A"
MUTED = "#888888"


def logo(size=40):
    return craft_logo(size)


def separador(h=20):
    return ft.Container(height=h)


def registro(page: ft.Page, ir_login, ir_home_comprador, ir_home_vendedor):
    page.clean()

    # Estado del rol seleccionado
    rol_sel = {"v": None}
    card_comprador_ref = ft.Ref[ft.Container]()
    card_vendedor_ref = ft.Ref[ft.Container]()
    error_text = ft.Text("", color="#CC0000", size=12, visible=False)
    loading = ft.ProgressRing(width=20, height=20, stroke_width=2,
                              color=BRAND, visible=False)

    nombre_field = ft.TextField(
        hint_text="Tu nombre completo",
        height=48, border_radius=10,
        border_color="#DDDDDD", focused_border_color=BRAND,
        bgcolor="white",
        content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
    )
    email_field = ft.TextField(
        hint_text="correo@ejemplo.com",
        height=48, border_radius=10,
        border_color="#DDDDDD", focused_border_color=BRAND,
        bgcolor="white",
        keyboard_type=ft.KeyboardType.EMAIL,
        content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
    )
    telefono_field = ft.TextField(
        hint_text="6000-0000",
        height=48, border_radius=10,
        border_color="#DDDDDD", focused_border_color=BRAND,
        bgcolor="white",
        keyboard_type=ft.KeyboardType.PHONE,
        content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
    )
    ubicacion_field = ft.TextField(
        hint_text="Ciudad, Provincia",
        height=48, border_radius=10,
        border_color="#DDDDDD", focused_border_color=BRAND,
        bgcolor="white",
        content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
    )
    password_field = ft.TextField(
        hint_text="Mínimo 6 caracteres",
        password=True, can_reveal_password=True,
        height=48, border_radius=10,
        border_color="#DDDDDD", focused_border_color=BRAND,
        bgcolor="white",
        content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
    )
    confirm_field = ft.TextField(
        hint_text="Repite tu contraseña",
        password=True, can_reveal_password=True,
        height=48, border_radius=10,
        border_color="#DDDDDD", focused_border_color=BRAND,
        bgcolor="white",
        content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
    )

    def seleccionar_rol(rol):
        rol_sel["v"] = rol
        if card_comprador_ref.current and card_vendedor_ref.current:
            card_comprador_ref.current.border = ft.border.all(
                2 if rol == "Comprador" else 1,
                BRAND if rol == "Comprador" else "#EEEEEE"
            )
            card_comprador_ref.current.bgcolor = (
                BRAND_LIGHT if rol == "Comprador" else "white"
            )
            card_vendedor_ref.current.border = ft.border.all(
                2 if rol == "Vendedor" else 1,
                BRAND if rol == "Vendedor" else "#EEEEEE"
            )
            card_vendedor_ref.current.bgcolor = (
                BRAND_LIGHT if rol == "Vendedor" else "white"
            )
        page.update()

    def card_rol(ref, emoji, titulo, desc, rol):
        return ft.Container(
            ref=ref,
            width=130, height=110,
            border_radius=12,
            bgcolor="white",
            border=ft.border.all(1, "#EEEEEE"),
            padding=12,
            on_click=lambda _: seleccionar_rol(rol),
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=6,
                controls=[
                    ft.Text(emoji, size=24),
                    ft.Text(titulo, size=13,
                            weight=ft.FontWeight.BOLD, color=TEXTO),
                    ft.Text(desc, size=10, color=MUTED,
                            text_align=ft.TextAlign.CENTER),
                ]
            )
        )

    def mostrar_error(msg):
        error_text.value = msg
        error_text.visible = True
        loading.visible = False
        page.update()

    def hacer_registro(e):
        nombre = nombre_field.value.strip()
        email = email_field.value.strip()
        telefono = telefono_field.value.strip()
        ubicacion = ubicacion_field.value.strip()
        password = password_field.value.strip()
        confirm = confirm_field.value.strip()

        if not all([nombre, email, password, confirm]):
            mostrar_error("Por favor completa los campos obligatorios.")
            return
        if not rol_sel["v"]:
            mostrar_error("Selecciona si eres Comprador o Vendedor.")
            return
        if password != confirm:
            mostrar_error("Las contraseñas no coinciden.")
            return
        if len(password) < 6:
            mostrar_error("La contraseña debe tener al menos 6 caracteres.")
            return

        error_text.visible = False
        loading.visible = True
        page.update()

        try:
            # Crear usuario en Supabase Auth
            response = supabase.auth.sign_up({
                "email": email,
                "password": password,
            })

            user = response.user
            if not user:
                mostrar_error("No se pudo crear la cuenta. Intenta de nuevo.")
                return

            # Crear perfil en la tabla perfiles
            supabase.table("perfiles").insert({
                "user_id": user.id,
                "nombre": nombre,
                "telefono": telefono,
                "ubicacion": ubicacion,
                "rol": rol_sel["v"],
                "craftmiles": 0,
            }).execute()

            loading.visible = False
            page.update()

            perfil_data = {
                "nombre": nombre,
                "telefono": telefono,
                "ubicacion": ubicacion,
                "rol": rol_sel["v"],
                "craftmiles": 0,
            }

            if rol_sel["v"] == "Vendedor":
                ir_home_vendedor(user, perfil_data)
            else:
                ir_home_comprador(user, perfil_data)

        except Exception as ex:
            msg = str(ex)
            if "already registered" in msg or "already been registered" in msg:
                mostrar_error("Este correo ya tiene una cuenta. Inicia sesión.")
            elif "invalid" in msg.lower() and "email" in msg.lower():
                mostrar_error("El correo no es válido.")
            else:
               mostrar_error(f"Error: {msg}")

    form = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=0,
        controls=[
            ft.Row(controls=[
                ft.TextButton("← Ya tengo cuenta",
                              style=ft.ButtonStyle(color=MUTED),
                              on_click=lambda _: ir_login())
            ]),
            separador(8),
            logo(44),
            separador(6),
            ft.Text("Crear cuenta", size=24,
                    weight=ft.FontWeight.BOLD, color=TEXTO),
            separador(4),
            ft.Text("Únete a la comunidad artesanal de Panamá",
                    size=12, color=MUTED),
            separador(20),

            # Selección de rol
            ft.Text("Soy...", size=13,
                    weight=ft.FontWeight.W_500, color=TEXTO),
            separador(8),
            ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=16,
                controls=[
                    card_rol(card_comprador_ref, "🛍️",
                             "Comprador", "Compro\nartesanías", "Comprador"),
                    card_rol(card_vendedor_ref, "🏪",
                             "Vendedor", "Vendo mis\ncreaciones", "Vendedor"),
                ]
            ),
            separador(20),

            # Campos
            ft.Container(
                width=280,
                content=ft.Column(spacing=8, controls=[
                    ft.Text("Nombre completo *", size=12,
                            weight=ft.FontWeight.W_500, color=TEXTO),
                    nombre_field,
                    ft.Text("Correo electrónico *", size=12,
                            weight=ft.FontWeight.W_500, color=TEXTO),
                    email_field,
                    ft.Text("Teléfono", size=12,
                            weight=ft.FontWeight.W_500, color=TEXTO),
                    telefono_field,
                    ft.Text("Ubicación", size=12,
                            weight=ft.FontWeight.W_500, color=TEXTO),
                    ubicacion_field,
                    ft.Text("Contraseña *", size=12,
                            weight=ft.FontWeight.W_500, color=TEXTO),
                    password_field,
                    ft.Text("Confirmar contraseña *", size=12,
                            weight=ft.FontWeight.W_500, color=TEXTO),
                    confirm_field,
                ])
            ),
            separador(8),
            ft.Container(width=280, content=error_text),
            separador(16),
            ft.Container(
                width=280, height=48,
                border_radius=10,
                bgcolor=BRAND,
                alignment=ft.Alignment(0, 0),
                on_click=hacer_registro,
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                    controls=[
                        loading,
                        ft.Text("Crear cuenta", color="white",
                                size=15, weight=ft.FontWeight.BOLD),
                    ]
                )
            ),
            separador(20),
        ]
    )

    page.add(
        ft.Row(
            expand=True, spacing=0,
            controls=[
                ft.Container(
                    width=380,
                    bgcolor=BRAND,
                    padding=50,
                    content=ft.Column(
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=16,
                        controls=[
                            logo(60),
                            separador(20),
                            ft.Text("Únete a\nCraftHub", size=38,
                                    weight=ft.FontWeight.BOLD, color="white"),
                            ft.Text("La plataforma de\nartesanías panameñas.",
                                    size=15, color="#FFB3B3"),
                            separador(20),
                            ft.Container(
                                bgcolor="#ffffff20",
                                border_radius=12,
                                padding=16,
                                content=ft.Column(spacing=8, controls=[
                                    ft.Text("✓  Gratis para compradores",
                                            size=12, color="white"),
                                    ft.Text("✓  Vende sin comisión inicial",
                                            size=12, color="white"),
                                    ft.Text("✓  Gana CraftMiles",
                                            size=12, color="white"),
                                ])
                            ),
                        ]
                    )
                ),
                ft.Container(
                    expand=True,
                    bgcolor="#FAFAFA",
                    alignment=ft.Alignment(0, 0),
                    padding=ft.padding.symmetric(horizontal=40, vertical=20),
                    content=ft.Container(
                        width=420,
                        bgcolor="white",
                        border_radius=20,
                        border=ft.border.all(1, "#EEEEEE"),
                        padding=ft.padding.symmetric(horizontal=40, vertical=24),
                        shadow=ft.BoxShadow(
                            blur_radius=30,
                            color="#00000010",
                            offset=ft.Offset(0, 4)
                        ),
                        content=form
                    )
                )
            ]
        )
    )
    page.update()
