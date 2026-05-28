import flet as ft
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supabase_client import supabase
from screens.componentes import craft_logo

BRAND = "#941515"
BRAND_DARK = "#6F0F0F"
BRAND_LIGHT = "#F7E7E7"
TEXTO = "#111111"
MUTED = "#7A7A7A"


def show_login(
    page: ft.Page,
    ir_bienvenida,
    ir_registro,
    ir_home_comprador,
    ir_home_vendedor,
    modo="Comprador",
    ir_roles=None,
):
    page.clean()
    page.window_width = 1280
    page.window_height = 800
    page.padding = 0
    page.bgcolor = "#FAFAFA"
    es_vendedor = modo == "Vendedor"

    titulo = "Ingreso vendedor" if es_vendedor else "Ingreso comprador"
    subtitulo = (
        "Administra tu taller, productos y pedidos."
        if es_vendedor else
        "Guarda favoritos, comenta y compra artesanias."
    )
    bloque_titulo = "Panel vendedor" if es_vendedor else "Cuenta comprador"
    bloque_copy = (
        "Entra con tu cuenta de vendedor para gestionar inventario, pedidos y ventas."
        if es_vendedor else
        "Entra con tu cuenta de comprador o vuelve a explorar CraftHub como visitante."
    )

    email_field = ft.TextField(
        hint_text="correo@ejemplo.com",
        height=50,
        border_radius=12,
        border_color="#DDDDDD",
        focused_border_color=BRAND,
        bgcolor="white",
        keyboard_type=ft.KeyboardType.EMAIL,
        content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
    )
    password_field = ft.TextField(
        hint_text="Contrasena",
        password=True,
        can_reveal_password=True,
        height=50,
        border_radius=12,
        border_color="#DDDDDD",
        focused_border_color=BRAND,
        bgcolor="white",
        content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
    )
    error_text = ft.Text("", color="#C1121F", size=12, visible=False)
    loading = ft.ProgressRing(width=20, height=20, stroke_width=2,
                              color=BRAND, visible=False)

    def mostrar_error(msg):
        error_text.value = msg
        error_text.visible = True
        loading.visible = False
        page.update()

    def hacer_login(e):
        email = email_field.value.strip()
        password = password_field.value.strip()

        if not email or not password:
            mostrar_error("Completa correo y contrasena.")
            return

        error_text.visible = False
        loading.visible = True
        page.update()

        try:
            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password,
            })
            user = response.user
        except Exception as ex:
            msg = str(ex)
            if "Invalid login credentials" in msg:
                mostrar_error("Correo o contrasena incorrectos.")
            elif "Email not confirmed" in msg:
                mostrar_error("Debes confirmar tu email antes de ingresar.")
            else:
                mostrar_error(f"Error: {msg}")
            return

        if not user:
            mostrar_error("No se pudo autenticar. Intenta de nuevo.")
            return

        try:
            perfil = supabase.table("perfiles").select("*").eq(
                "user_id", user.id).single().execute()
            perfil_data = perfil.data or {"nombre": email, "rol": "Comprador"}
        except Exception:
            perfil_data = {"nombre": email, "rol": "Comprador"}

        rol_real = perfil_data.get("rol", "Comprador")
        if rol_real != modo:
            loading.visible = False
            mostrar_error(
                "Esta cuenta es de vendedor. Usa el acceso de vendedor."
                if rol_real == "Vendedor"
                else "Esta cuenta es de comprador. Usa el acceso de comprador."
            )
            return

        loading.visible = False
        page.update()

        if modo == "Vendedor":
            ir_home_vendedor(user, perfil_data)
        else:
            ir_home_comprador(user, perfil_data)

    def header():
        return ft.Container(
            height=68,
            bgcolor="white",
            border=ft.border.only(bottom=ft.BorderSide(1, "#DADADA")),
            padding=ft.padding.symmetric(horizontal=34),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=34,
                        height=34,
                        alignment=ft.Alignment(0, 0),
                        on_click=lambda _: ir_roles() if ir_roles else ir_bienvenida(),
                        content=ft.Text("<", size=22, color=TEXTO),
                    ),
                    ft.Text(titulo, size=22, color=TEXTO,
                            weight=ft.FontWeight.BOLD),
                    ft.Row(spacing=6, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
                        craft_logo(34),
                        ft.Text("CRAFTHUB", size=11, color=TEXTO,
                                weight=ft.FontWeight.BOLD),
                    ]),
                ],
            ),
        )

    def role_pill():
        return ft.Container(
            border_radius=18,
            bgcolor=BRAND_LIGHT,
            border=ft.border.all(1, BRAND),
            padding=ft.padding.symmetric(horizontal=14, vertical=5),
            content=ft.Text(
                "Acceso vendedor" if es_vendedor else "Acceso comprador",
                size=11,
                color=BRAND,
                weight=ft.FontWeight.BOLD,
            ),
        )

    form_panel = ft.Container(
        width=430,
        bgcolor="white",
        border_radius=24,
        border=ft.border.all(1, "#E8E8E8"),
        padding=36,
        shadow=ft.BoxShadow(blur_radius=32, color="#00000012", offset=ft.Offset(0, 8)),
        content=ft.Column(
            spacing=12,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                craft_logo(58),
                role_pill(),
                ft.Text(titulo, size=28, color=TEXTO, weight=ft.FontWeight.BOLD),
                ft.Text(subtitulo, size=13, color=MUTED, text_align=ft.TextAlign.CENTER),
                ft.Container(height=8),
                ft.Container(width=320, content=ft.Column(spacing=8, controls=[
                    ft.Text("Correo electronico", size=12, color=TEXTO, weight=ft.FontWeight.W_600),
                    email_field,
                    ft.Text("Contrasena", size=12, color=TEXTO, weight=ft.FontWeight.W_600),
                    password_field,
                ])),
                ft.Container(width=320, content=error_text),
                ft.Container(
                    width=320,
                    height=48,
                    border_radius=24,
                    bgcolor=BRAND,
                    alignment=ft.Alignment(0, 0),
                    on_click=hacer_login,
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=10,
                        controls=[
                            loading,
                            ft.Text("Ingresar", size=15, color="white",
                                    weight=ft.FontWeight.BOLD),
                        ],
                    ),
                ),
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Text("No tienes cuenta?", size=12, color=MUTED),
                        ft.TextButton(
                            "Registrate",
                            style=ft.ButtonStyle(color=BRAND),
                            on_click=lambda _: ir_registro(modo),
                        ),
                    ],
                ),
                ft.TextButton(
                    "Explorar como visitante",
                    visible=not es_vendedor,
                    style=ft.ButtonStyle(color=MUTED),
                    on_click=lambda _: ir_home_comprador(),
                ),
            ],
        ),
    )

    visual_panel = ft.Container(
        expand=True,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        content=ft.Stack(
            controls=[
                ft.Image(
                    src="banner.png",
                    fit="cover",
                    width=float("inf"),
                    height=float("inf"),
                ),
                ft.Container(bgcolor="#000000A8"),
                ft.Container(
                    padding=56,
                    content=ft.Column(
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=18,
                        controls=[
                            craft_logo(82),
                            ft.Text(bloque_titulo, size=42, color="white",
                                    weight=ft.FontWeight.BOLD),
                            ft.Text(bloque_copy, size=16, color="#F2DADA", width=420),
                            ft.Container(
                                width=220,
                                height=42,
                                border_radius=24,
                                border=ft.border.all(1, "white"),
                                alignment=ft.Alignment(0, 0),
                                content=ft.Text(
                                    "Modo vendedor" if es_vendedor else "Modo comprador",
                                    color="white",
                                    weight=ft.FontWeight.BOLD,
                                ),
                            ),
                        ],
                    ),
                ),
            ],
        ),
    )

    page.add(
        ft.Column(
            expand=True,
            spacing=0,
            controls=[
                header(),
                ft.Row(
                    expand=True,
                    spacing=0,
                    controls=[
                        visual_panel,
                        ft.Container(
                            width=520,
                            bgcolor="#FAFAFA",
                            alignment=ft.Alignment(0, 0),
                            content=form_panel,
                        ),
                    ],
                ),
            ],
        )
    )
    page.update()
