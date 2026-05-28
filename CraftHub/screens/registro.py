import flet as ft
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supabase_client import supabase
from screens.componentes import craft_logo, tabler_icon

BRAND = "#941515"
TEXTO = "#1A1A1A"
MUTED = "#8A8A8A"

def registro(page: ft.Page, ir_login, ir_home_comprador, ir_home_vendedor, rol_inicial=None):
    page.clean()
    page.appbar = None
    page.update()
    rol_sel = {"v": None}
    error_text = ft.Text("", color="#CC0000", size=12, visible=False)
    loading = ft.ProgressRing(width=20, height=20, stroke_width=2,
                              color=BRAND, visible=False)

    nombre_field = ft.TextField(
        hint_text="Tu nombre completo",
        height=48,
        border_radius=10,
        border_color="#DDDDDD",
        focused_border_color=BRAND,
        bgcolor="white",
        content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
    )
    email_field = ft.TextField(
        hint_text="correo@ejemplo.com",
        height=48,
        border_radius=10,
        border_color="#DDDDDD",
        focused_border_color=BRAND,
        bgcolor="white",
        keyboard_type=ft.KeyboardType.EMAIL,
        content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
    )
    telefono_field = ft.TextField(
        hint_text="6000-0000",
        height=48,
        border_radius=10,
        border_color="#DDDDDD",
        focused_border_color=BRAND,
        bgcolor="white",
        keyboard_type=ft.KeyboardType.PHONE,
        content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
    )
    ubicacion_field = ft.TextField(
        hint_text="Ciudad, Provincia",
        height=48,
        border_radius=10,
        border_color="#DDDDDD",
        focused_border_color=BRAND,
        bgcolor="white",
        content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
    )
    password_field = ft.TextField(
        hint_text="Minimo 6 caracteres",
        password=True,
        can_reveal_password=True,
        height=48,
        border_radius=10,
        border_color="#DDDDDD",
        focused_border_color=BRAND,
        bgcolor="white",
        content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
    )
    confirm_field = ft.TextField(
        hint_text="Repite tu contrasena",
        password=True,
        can_reveal_password=True,
        height=48,
        border_radius=10,
        border_color="#DDDDDD",
        focused_border_color=BRAND,
        bgcolor="white",
        content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
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
            mostrar_error("Selecciona si eres comprador o vendedor.")
            return
        if password != confirm:
            mostrar_error("Las contrasenas no coinciden.")
            return
        if len(password) < 6:
            mostrar_error("La contrasena debe tener al menos 6 caracteres.")
            return

        error_text.visible = False
        loading.visible = True
        page.update()

        try:
            response = supabase.auth.sign_up({
                "email": email,
                "password": password,
            })
            user = response.user
            if not user:
                mostrar_error("No se pudo crear la cuenta. Intenta de nuevo.")
                return

            supabase.table("perfiles").insert({
                "user_id": user.id,
                "nombre": nombre,
                "telefono": telefono,
                "ubicacion": ubicacion,
                "rol": rol_sel["v"],
            }).execute()

            loading.visible = False
            perfil_data = {
                "nombre": nombre,
                "telefono": telefono,
                "ubicacion": ubicacion,
                "rol": rol_sel["v"],
            }

            if rol_sel["v"] == "Vendedor":
                ir_home_vendedor(user, perfil_data)
            else:
                ir_home_comprador(user, perfil_data)

        except Exception as ex:
            msg = str(ex)
            if "already registered" in msg or "already been registered" in msg:
                mostrar_error("Este correo ya tiene una cuenta. Inicia sesion.")
            elif "invalid" in msg.lower() and "email" in msg.lower():
                mostrar_error("El correo no es valido.")
            else:
                mostrar_error(f"Error: {msg}")

    def label(texto):
        return ft.Text(texto, size=12, weight=ft.FontWeight.W_600, color=TEXTO)

    def mostrar_formulario(rol):
        rol_sel["v"] = rol
        page.clean()
        page.add(
            ft.Column(
                expand=True,
                spacing=0,
                controls=[
                    header("Crear cuenta", lambda _: mostrar_roles()),
                    ft.Container(
                        expand=True,
                        bgcolor="#FAFAFA",
                        alignment=ft.Alignment(0, 0),
                        padding=ft.padding.symmetric(horizontal=28, vertical=18),
                        content=ft.Container(
                            width=500,
                            bgcolor="white",
                            border_radius=20,
                            border=ft.border.all(1, "#EEEEEE"),
                            padding=ft.padding.symmetric(horizontal=46, vertical=24),
                            shadow=ft.BoxShadow(
                                blur_radius=28,
                                color="#00000012",
                                offset=ft.Offset(0, 6),
                            ),
                            content=ft.Column(
                                scroll=ft.ScrollMode.AUTO,
                                spacing=8,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    ft.Row(
                                        alignment=ft.MainAxisAlignment.CENTER,
                                        controls=[
                                            craft_logo(52),
                                            ft.Container(width=8),
                                            ft.Text(
                                                "VENDEDOR" if rol == "Vendedor" else "COMPRADOR",
                                                size=22,
                                                color=BRAND,
                                                weight=ft.FontWeight.BOLD,
                                            ),
                                        ],
                                    ),
                                    ft.Text(
                                        "Completa tus datos para crear tu cuenta CraftHub.",
                                        size=12,
                                        color=MUTED,
                                        text_align=ft.TextAlign.CENTER,
                                    ),
                                    ft.Container(height=10),
                                    ft.Container(width=360, content=ft.Column(spacing=7, controls=[
                                        label("Nombre completo *"),
                                        nombre_field,
                                        label("Correo electronico *"),
                                        email_field,
                                        label("Telefono"),
                                        telefono_field,
                                        label("Ubicacion"),
                                        ubicacion_field,
                                        label("Contrasena *"),
                                        password_field,
                                        label("Confirmar contrasena *"),
                                        confirm_field,
                                        error_text,
                                    ])),
                                    ft.Container(height=8),
                                    ft.Container(
                                        width=360,
                                        height=48,
                                        border_radius=12,
                                        bgcolor=BRAND,
                                        alignment=ft.Alignment(0, 0),
                                        on_click=hacer_registro,
                                        content=ft.Row(
                                            alignment=ft.MainAxisAlignment.CENTER,
                                            spacing=10,
                                            controls=[
                                                loading,
                                                ft.Text(
                                                    "Crear cuenta",
                                                    color="white",
                                                    size=15,
                                                    weight=ft.FontWeight.BOLD,
                                                ),
                                            ],
                                        ),
                                    ),
                                    ft.TextButton(
                                        "Ya tengo cuenta",
                                        style=ft.ButtonStyle(color=MUTED),
                                        on_click=lambda _, r=rol: ir_login(r),
                                    ),
                                ],
                            ),
                        ),
                    ),
                ],
            )
        )
        page.update()

    def header(titulo, back_action):
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
                        on_click=back_action,
                        content=ft.Text("<", size=22, color="#111111"),
                    ),
                    ft.Text(
                        titulo,
                        size=21,
                        color="#0A0A0A",
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Row(spacing=6, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
                        craft_logo(34),
                        ft.Text("CRAFTHUB", size=11, color="#111111",
                                weight=ft.FontWeight.BOLD),
                    ]),
                ],
            ),
        )

    def icon_box(icon_name):
        return ft.Container(
            height=178,
            bgcolor="white",
            border_radius=8,
            alignment=ft.Alignment(0, 0),
            content=tabler_icon(icon_name, size=104, color=BRAND),
        )

    def role_card(tipo, titulo, descripcion, icon_name, show_explore=False):
        rol = "Vendedor" if tipo == "seller" else "Comprador"
        es_vendedor = rol == "Vendedor"
        return ft.Container(
            width=400,
            height=450,
            bgcolor="black",
            border_radius=30,
            padding=28,
            shadow=ft.BoxShadow(blur_radius=10, color="#00000035", offset=ft.Offset(0, 4)),
            content=ft.Column(
                spacing=14,
                controls=[
                    icon_box(icon_name),
                    ft.Text(titulo, size=26, color="white", weight=ft.FontWeight.BOLD),
                    ft.Text(descripcion, size=16, color="white", height=1.28),
                    ft.Container(expand=True),
                    ft.Container(
                        height=40,
                        border_radius=24,
                        border=ft.border.all(1, "white"),
                        alignment=ft.Alignment(0, 0),
                        visible=show_explore,
                        on_click=lambda _: ir_home_comprador(),
                        content=ft.Text("Explorar", size=16, color="white",
                                        weight=ft.FontWeight.BOLD),
                    ),
                    ft.Container(
                        height=40,
                        border_radius=24,
                        bgcolor="#9B9B9B",
                        alignment=ft.Alignment(0, 0),
                        on_click=(
                            (lambda _: ir_login("Vendedor"))
                            if es_vendedor else
                            (lambda _: mostrar_formulario("Comprador"))
                        ),
                        content=ft.Text("Iniciar sesion" if es_vendedor else "Registrarse", size=16, color="white",
                                        weight=ft.FontWeight.BOLD),
                    ),
                ],
            ),
        )

    def mostrar_roles():
        page.clean()
        page.add(
            ft.Column(
                expand=True,
                spacing=0,
                controls=[
                    header("Elige tu rol de usuario", lambda _: ir_login("Comprador")),
                    ft.Container(
                        expand=True,
                        bgcolor="white",
                        padding=ft.padding.only(left=82, right=66, top=24, bottom=36),
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                role_card(
                                    "seller",
                                    "VENDEDOR",
                                    "Convierte lo que amas crear en una oportunidad. Publica tus productos y recibe pedidos en CraftHub.",
                                    "building-store",
                                ),
                                role_card(
                                    "buyer",
                                    "COMPRADOR",
                                    "Explora artesanias panamenas hechas con pasion. Descubre productos unicos y compra cuando quieras.",
                                    "shopping-bag",
                                    show_explore=True,
                                ),
                            ],
                        ),
                    ),
                ],
            )
        )
        page.update()

    if rol_inicial:
        mostrar_formulario(rol_inicial)
    else:
        mostrar_roles()
