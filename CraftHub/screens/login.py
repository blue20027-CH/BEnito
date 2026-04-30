import flet as ft
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supabase_client import supabase

BRAND = "#800000"
BRAND_LIGHT = "#F5E8E8"
TEXTO = "#1A1A1A"
MUTED = "#888888"


def logo(size=40):
    return ft.Container(
        width=size, height=size,
        border_radius=8,
        bgcolor=BRAND,
        alignment=ft.Alignment(0, 0),
        content=ft.Text("CH", color="white",
                        size=int(size // 2.2),
                        weight=ft.FontWeight.BOLD)
    )


def separador(h=20):
    return ft.Container(height=h)


def lado_marca(titulo_txt, subtitulo_txt):
    return ft.Container(
        width=380,
        bgcolor=BRAND,
        padding=50,
        content=ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=12,
            controls=[
                logo(60),
                separador(24),
                ft.Text(titulo_txt, size=38,
                        weight=ft.FontWeight.BOLD, color="white"),
                ft.Text(subtitulo_txt, size=15, color="#FFB3B3"),
            ]
        )
    )


def show_login(page: ft.Page, ir_bienvenida, ir_registro, ir_home_comprador, ir_home_vendedor):
    page.clean()

    email_field = ft.TextField(
        hint_text="correo@ejemplo.com",
        height=48,
        border_radius=10,
        border_color="#DDDDDD",
        focused_border_color=BRAND,
        bgcolor="white",
        content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
        keyboard_type=ft.KeyboardType.EMAIL,
    )

    password_field = ft.TextField(
        hint_text="••••••••",
        password=True,
        can_reveal_password=True,
        height=48,
        border_radius=10,
        border_color="#DDDDDD",
        focused_border_color=BRAND,
        bgcolor="white",
        content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
    )

    error_text = ft.Text("", color="#CC0000", size=12, visible=False)
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
            mostrar_error("Por favor completa todos los campos.")
            return

        error_text.visible = False
        loading.visible = True
        page.update()

        # Paso 1: autenticar usuario
        user = None
        try:
            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            user = response.user
        except Exception as ex:
            msg = str(ex)
            if "Invalid login credentials" in msg:
                mostrar_error("Email o contrasena incorrectos.")
            elif "Email not confirmed" in msg:
                mostrar_error("Debes confirmar tu email antes de ingresar.")
            else:
                mostrar_error(f"Error: {msg}")
            return

        if not user:
            mostrar_error("No se pudo autenticar. Intenta de nuevo.")
            return

        # Paso 2: buscar perfil (si falla igual va al home como comprador)
        perfil_data = {"nombre": email, "rol": "Comprador"}
        try:
            perfil = supabase.table("perfiles").select("*").eq(
                "user_id", user.id).single().execute()
            if perfil.data:
                perfil_data = perfil.data
        except Exception:
            pass

        loading.visible = False
        page.update()

        # Paso 3: navegar segun rol
        rol = perfil_data.get("rol", "Comprador")
        if rol == "Vendedor":
            ir_home_vendedor(user, perfil_data)
        else:
            ir_home_comprador(user, perfil_data)

    form = ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=0,
        controls=[
            ft.Row(controls=[
                ft.TextButton("< Volver",
                              style=ft.ButtonStyle(color=MUTED),
                              on_click=lambda _: ir_bienvenida())
            ]),
            separador(10),
            logo(50),
            separador(8),
            ft.Text("Ingresar", size=26,
                    weight=ft.FontWeight.BOLD, color=TEXTO),
            separador(4),
            ft.Text("Accede a tu cuenta de CraftHub",
                    size=13, color=MUTED),
            separador(24),
            ft.Container(
                width=280,
                content=ft.Column(spacing=6, controls=[
                    ft.Text("Correo electronico", size=13,
                            weight=ft.FontWeight.W_500, color=TEXTO),
                    email_field,
                    separador(4),
                    ft.Text("Contrasena", size=13,
                            weight=ft.FontWeight.W_500, color=TEXTO),
                    password_field,
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
                on_click=hacer_login,
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                    controls=[
                        loading,
                        ft.Text("Ingresar", color="white",
                                size=15, weight=ft.FontWeight.BOLD),
                    ]
                )
            ),
            separador(16),
            ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Text("No tienes cuenta?", size=13, color=MUTED),
                    ft.TextButton(
                        "Registrate",
                        style=ft.ButtonStyle(color=BRAND),
                        on_click=lambda _: ir_registro()
                    ),
                ]
            ),
        ]
    )

    panel = ft.Container(
        width=420,
        bgcolor="white",
        border_radius=20,
        border=ft.border.all(1, "#EEEEEE"),
        padding=40,
        content=form,
        shadow=ft.BoxShadow(
            blur_radius=30,
            color="#00000010",
            offset=ft.Offset(0, 4)
        )
    )

    page.add(
        ft.Row(
            expand=True, spacing=0,
            controls=[
                lado_marca("Bienvenido\nde vuelta",
                           "Tu comunidad artesanal\nte espera."),
                ft.Container(
                    expand=True,
                    bgcolor="#FAFAFA",
                    alignment=ft.Alignment(0, 0),
                    content=panel
                )
            ]
        )
    )
    page.update()