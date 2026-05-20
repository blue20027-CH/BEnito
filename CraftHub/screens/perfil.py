import flet as ft
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supabase_client import supabase
from screens.componentes import craft_logo, craft_banner_header
import base64

BRAND = "#800000"
BRAND_LIGHT = "#F5E8E8"
TEXTO = "#1A1A1A"
MUTED = "#888888"


def show_perfil(page: ft.Page, ir_home, ir_bienvenida, usuario):
    page.clean()

    perfil = usuario.get("perfil") or {}
    user = usuario.get("user")

    foto_url = {"v": perfil.get("foto", "") or ""}
    avatar_ref = ft.Ref[ft.Container]()

    def cerrar_sesion():
        try:
            supabase.auth.sign_out()
        except:
            pass
        usuario["user"] = None
        usuario["perfil"] = None
        ir_bienvenida()

    def subir_foto(e):
        if not e.files:
            return
        archivo = e.files[0]
        try:
            with open(archivo.path, "rb") as f:
                contenido = f.read()

            user_id = perfil.get("user_id") or (user.id if user else None)
            if not user_id:
                return

            nombre_archivo = f"{user_id}.jpg"

            supabase.storage.from_("avatares").upload(
                nombre_archivo,
                contenido,
                {"content-type": "image/jpeg",
                 "x-upsert": "true"}
            )

            url = supabase.storage.from_("avatares").get_public_url(
                nombre_archivo)

            supabase.table("perfiles").update(
                {"foto": url}
            ).eq("user_id", user_id).execute()

            usuario["perfil"]["foto"] = url
            foto_url["v"] = url

            if avatar_ref.current:
                avatar_ref.current.content = ft.Image(
                    src=url,
                    fit="cover",
                    width=80, height=80,
                )
            page.update()

            page.snack_bar = ft.SnackBar(
                content=ft.Text("Foto actualizada", color="white"),
                bgcolor=BRAND, duration=2000,
            )
            page.snack_bar.open = True
            page.update()

        except Exception as ex:
            print("Error subiendo foto:", ex)
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Error: {ex}", color="white"),
                bgcolor="#CC0000", duration=3000,
            )
            page.snack_bar.open = True
            page.update()

    file_picker = ft.FilePicker(on_result=subir_foto)
    page.overlay.append(file_picker)

    campo_nombre = ft.TextField(
        label="Nombre completo",
        value=perfil.get("nombre", ""),
        border_radius=10,
        border_color="#DDDDDD",
        focused_border_color=BRAND,
        bgcolor="white",
    )
    campo_telefono = ft.TextField(
        label="Telefono",
        value=str(perfil.get("telefono", "") or ""),
        border_radius=10,
        border_color="#DDDDDD",
        focused_border_color=BRAND,
        bgcolor="white",
        keyboard_type=ft.KeyboardType.PHONE,
    )
    campo_ubicacion = ft.TextField(
        label="Ubicacion",
        value=str(perfil.get("ubicacion", "") or ""),
        border_radius=10,
        border_color="#DDDDDD",
        focused_border_color=BRAND,
        bgcolor="white",
    )

    mensaje = ft.Text("", visible=False, size=13)

    def mostrar_mensaje(texto, exito=True):
        mensaje.value = texto
        mensaje.color = BRAND if exito else "#CC0000"
        mensaje.visible = True
        page.update()

    def guardar(e):
        if not campo_nombre.value.strip():
            mostrar_mensaje("El nombre no puede estar vacio.", exito=False)
            return

        datos = {
            "nombre": campo_nombre.value.strip(),
            "telefono": campo_telefono.value.strip(),
            "ubicacion": campo_ubicacion.value.strip(),
        }

        try:
            user_id = perfil.get("user_id") or (user.id if user else None)
            if not user_id:
                mostrar_mensaje("No se pudo identificar al usuario.", exito=False)
                return

            supabase.table("perfiles").update(datos).eq(
                "user_id", user_id).execute()

            usuario["perfil"].update(datos)
            mostrar_mensaje("Perfil actualizado correctamente.")
        except Exception as ex:
            mostrar_mensaje(f"Error: {ex}", exito=False)

    nombre_completo = perfil.get("nombre", "U")
    iniciales = "".join([p[0].upper() for p in nombre_completo.split()[:2]])
    rol = perfil.get("rol", "Comprador")
    craftmiles = perfil.get("craftmiles", 0) or 0
    created_at = perfil.get("created_at", "")
    fecha = created_at[:10] if created_at else "—"

    # Avatar con imagen o iniciales
    def construir_avatar():
        if foto_url["v"]:
            contenido = ft.Image(
                src=foto_url["v"],
                fit="cover",
                width=80, height=80,
            )
        else:
            contenido = ft.Text(iniciales, size=28,
                                color="white",
                                weight=ft.FontWeight.BOLD)
        return contenido

    header = ft.Container(
        bgcolor=BRAND,
        padding=ft.padding.symmetric(horizontal=24, vertical=14),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row(spacing=10, controls=[
                    craft_logo(36, bgcolor="white", radius=6),
                    ft.Text("Mi Perfil", size=15,
                            weight=ft.FontWeight.BOLD, color="white"),
                ]),
                ft.Row(spacing=8, controls=[
                    ft.TextButton(
                        "< Volver",
                        style=ft.ButtonStyle(color="white"),
                        on_click=lambda _: ir_home()
                    ),
                    ft.Container(
                        height=34,
                        border_radius=8,
                        bgcolor="white",
                        padding=ft.padding.symmetric(horizontal=14, vertical=6),
                        on_click=lambda _: cerrar_sesion(),
                        content=ft.Row(spacing=6, controls=[
                            ft.Text("🚪", size=14),
                            ft.Text("Cerrar sesion", size=13,
                                    color=BRAND, weight=ft.FontWeight.W_500),
                        ])
                    )
                ])
            ]
        )
    )

    tarjeta_superior = ft.Container(
        bgcolor="white",
        border_radius=16,
        border=ft.border.all(1, "#EEEEEE"),
        padding=28,
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Row(spacing=20, controls=[
                    # Avatar clickeable
                    ft.Stack(
                        controls=[
                            ft.Container(
                                ref=avatar_ref,
                                width=80, height=80,
                                border_radius=40,
                                bgcolor=BRAND,
                                clip_behavior=ft.ClipBehavior.HARD_EDGE,
                                alignment=ft.Alignment(0, 0),
                                on_click=lambda _: file_picker.pick_files(
                                    allow_multiple=False,
                                    allowed_extensions=["jpg", "jpeg", "png"]
                                ),
                                content=construir_avatar()
                            ),
                            ft.Container(
                                width=80, height=80,
                                alignment=ft.Alignment(1, 1),
                                content=ft.Container(
                                    width=26, height=26,
                                    border_radius=13,
                                    bgcolor=BRAND,
                                    border=ft.border.all(2, "white"),
                                    alignment=ft.Alignment(0, 0),
                                    content=ft.Text("📷", size=12)
                                )
                            )
                        ]
                    ),
                    ft.Column(spacing=6, controls=[
                        ft.Text(nombre_completo, size=20,
                                weight=ft.FontWeight.BOLD, color=TEXTO),
                        ft.Container(
                            border_radius=20,
                            bgcolor=BRAND_LIGHT,
                            padding=ft.padding.symmetric(
                                horizontal=12, vertical=4),
                            content=ft.Text(rol, size=12, color=BRAND,
                                            weight=ft.FontWeight.W_500)
                        ),
                        ft.Text(f"Miembro desde {fecha}",
                                size=11, color=MUTED),
                        ft.Text("Toca la foto para cambiarla",
                                size=10, color=MUTED),
                    ])
                ]),
                ft.Container(
                    width=140,
                    border_radius=14,
                    bgcolor=BRAND_LIGHT,
                    border=ft.border.all(1, BRAND),
                    padding=16,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=4,
                        controls=[
                            ft.Text("⭐", size=24),
                            ft.Text(str(craftmiles), size=26,
                                    weight=ft.FontWeight.BOLD, color=BRAND),
                            ft.Text("CraftMiles", size=11, color=MUTED),
                        ]
                    )
                )
            ]
        )
    )

    formulario = ft.Container(
        bgcolor="white",
        border_radius=16,
        border=ft.border.all(1, "#EEEEEE"),
        padding=28,
        content=ft.Column(
            spacing=16,
            controls=[
                ft.Text("Editar informacion", size=16,
                        weight=ft.FontWeight.BOLD, color=TEXTO),
                ft.Divider(color="#EEEEEE"),
                campo_nombre,
                ft.Row(spacing=16, controls=[
                    ft.Container(expand=True, content=campo_telefono),
                    ft.Container(expand=True, content=campo_ubicacion),
                ]),
                ft.Container(
                    bgcolor="#F9F9F9",
                    border_radius=10,
                    border=ft.border.all(1, "#EEEEEE"),
                    padding=14,
                    content=ft.Row(spacing=10, controls=[
                        ft.Text("🔒", size=16),
                        ft.Text("El rol no puede ser cambiado desde aqui.",
                                size=12, color=MUTED),
                    ])
                ),
                mensaje,
                ft.Row(
                    alignment=ft.MainAxisAlignment.END,
                    controls=[
                        ft.ElevatedButton(
                            "Guardar cambios",
                            bgcolor=BRAND, color="white",
                            height=44,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=10),
                                elevation=0,
                            ),
                            on_click=guardar
                        )
                    ]
                )
            ]
        )
    )

    def info_row(emoji, label, valor):
        return ft.Row(spacing=12, controls=[
            ft.Text(emoji, size=18),
            ft.Column(spacing=1, controls=[
                ft.Text(label, size=11, color=MUTED),
                ft.Text(str(valor) if valor else "—",
                        size=13, color=TEXTO,
                        weight=ft.FontWeight.W_500),
            ])
        ])

    info_card = ft.Container(
        bgcolor="white",
        border_radius=16,
        border=ft.border.all(1, "#EEEEEE"),
        padding=28,
        content=ft.Column(
            spacing=16,
            controls=[
                ft.Text("Resumen de cuenta", size=16,
                        weight=ft.FontWeight.BOLD, color=TEXTO),
                ft.Divider(color="#EEEEEE"),
                info_row("📍", "Ubicacion", perfil.get("ubicacion") or "—"),
                info_row("📞", "Telefono", perfil.get("telefono") or "—"),
                info_row("🎭", "Rol", rol),
                info_row("⭐", "CraftMiles", craftmiles),
                info_row("📅", "Miembro desde", fecha),
                ft.Container(height=8),
                ft.Container(
                    height=44,
                    border_radius=10,
                    bgcolor=BRAND_LIGHT,
                    border=ft.border.all(1, BRAND),
                    alignment=ft.Alignment(0, 0),
                    on_click=lambda _: cerrar_sesion(),
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=8,
                        controls=[
                            ft.Text("🚪", size=16),
                            ft.Text("Cerrar sesion", size=13,
                                    color=BRAND, weight=ft.FontWeight.BOLD),
                        ]
                    )
                )
            ]
        )
    )

    contenido = ft.Column(
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        spacing=20,
        controls=[
            tarjeta_superior,
            ft.Row(
                spacing=20,
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    ft.Container(expand=2, content=formulario),
                    ft.Container(expand=1, content=info_card),
                ]
            ),
            ft.Container(height=20),
        ]
    )

    header = craft_banner_header(
        "Mi Perfil",
        "Cuenta CraftHub",
        actions=[
            ft.TextButton(
                "< Volver",
                style=ft.ButtonStyle(color="white"),
                on_click=lambda _: ir_home()
            ),
            ft.Container(
                height=34,
                border_radius=8,
                bgcolor="white",
                padding=ft.padding.symmetric(horizontal=14, vertical=6),
                on_click=lambda _: cerrar_sesion(),
                content=ft.Row(spacing=6, controls=[
                    ft.Text("S", size=14, color=BRAND),
                    ft.Text("Cerrar sesion", size=13, color=BRAND, weight=ft.FontWeight.W_500),
                ])
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
                    padding=24,
                    bgcolor="#FAFAFA",
                    content=contenido
                )
            ]
        )
    )
    page.update()
