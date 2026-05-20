import flet as ft
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supabase_client import supabase

BRAND = "#800000"
BRAND_DARK = "#9E1414"
BRAND_LIGHT = "#F5E8E8"
TEXTO = "#1A1A1A"
MUTED = "#9A9A9A"


def abrir_menu_perfil(
    page: ft.Page,
    usuario,
    ir_perfil=None,
    ir_carrito=None,
    ir_pedidos=None,
    ir_bienvenida=None,
    on_create=None,
    modo="comprador",
):
    perfil = (usuario or {}).get("perfil") or {}
    user = (usuario or {}).get("user")

    nombre = perfil.get("nombre") or "Usuario CraftHub"
    email = (
        perfil.get("email")
        or getattr(user, "email", None)
        or (user.get("email") if isinstance(user, dict) else None)
        or "craft@crafthub.com"
    )
    rol = (perfil.get("rol") or modo or "Comprador").capitalize()
    foto = perfil.get("foto") or ""
    iniciales = "".join([p[0].upper() for p in nombre.split()[:2]]) or "CH"

    panel_ref = ft.Ref[ft.Container]()

    def cerrar(e=None):
        if panel_ref.current in page.overlay:
            page.overlay.remove(panel_ref.current)
        page.update()

    def navegar(callback):
        cerrar()
        if callback:
            callback()

    def cerrar_sesion(e=None):
        try:
            supabase.auth.sign_out()
        except Exception:
            pass
        if usuario is not None:
            usuario["user"] = None
            usuario["perfil"] = None
        navegar(ir_bienvenida)

    def avatar():
        contenido = (
            ft.Image(src=foto, fit="cover", width=118, height=118)
            if foto
            else ft.Text(iniciales, size=34, weight=ft.FontWeight.BOLD, color="white")
        )
        return ft.Container(
            width=124,
            height=124,
            border_radius=62,
            padding=3,
            bgcolor=BRAND,
            content=ft.Container(
                width=118,
                height=118,
                border_radius=59,
                clip_behavior=ft.ClipBehavior.HARD_EDGE,
                bgcolor=BRAND_LIGHT,
                alignment=ft.Alignment(0, 0),
                content=contenido,
            ),
        )

    def menu_item(icono, texto, callback=None, activo=False):
        return ft.Container(
            height=46,
            border_radius=12,
            bgcolor=BRAND if activo else None,
            padding=ft.padding.symmetric(horizontal=18),
            on_click=lambda _: navegar(callback) if callback else None,
            content=ft.Row(
                spacing=14,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text(icono, size=18, color="white" if activo else BRAND),
                    ft.Text(
                        texto,
                        size=13,
                        color="white" if activo else TEXTO,
                        weight=ft.FontWeight.BOLD if activo else ft.FontWeight.W_600,
                    ),
                ],
            ),
        )

    if modo == "vendedor":
        opciones = [
            menu_item("[]", "Mis productos", None),
            menu_item("+", "Create", on_create, activo=True),
            menu_item("##", "Studio", None),
            menu_item("≡", "Orders", ir_pedidos),
            menu_item("@", "Suppliers", None),
        ]
    else:
        opciones = [
            menu_item("P", "Mi perfil", ir_perfil),
            menu_item("+", "Explorar", None, activo=True),
            menu_item("C", "Carrito", ir_carrito),
            menu_item("≡", "Pedidos", ir_pedidos),
            menu_item("*", "CraftMiles", ir_perfil),
        ]

    panel = ft.Container(
        width=260,
        height=float("inf"),
        bgcolor="#F7F7F7",
        border_radius=ft.border_radius.only(top_right=24, bottom_right=24),
        shadow=ft.BoxShadow(blur_radius=22, color="#00000022", offset=ft.Offset(4, 0)),
        padding=ft.padding.only(left=18, right=18, top=16, bottom=18),
        content=ft.Column(
            expand=True,
            spacing=0,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.END,
                    controls=[
                        ft.Container(
                            width=30,
                            height=30,
                            border_radius=15,
                            alignment=ft.Alignment(0, 0),
                            on_click=cerrar,
                            content=ft.Text("<", size=16, color=TEXTO, weight=ft.FontWeight.BOLD),
                        )
                    ],
                ),
                ft.Container(
                    alignment=ft.Alignment(0, 0),
                    content=avatar(),
                ),
                ft.Container(height=14),
                ft.Text(nombre, size=13, color=TEXTO, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                ft.Container(height=6),
                ft.Text(email, size=12, color=MUTED, text_align=ft.TextAlign.CENTER),
                ft.Container(height=28),
                ft.Column(spacing=10, controls=opciones),
                ft.Container(expand=True),
                ft.Container(
                    height=44,
                    border_radius=12,
                    padding=ft.padding.symmetric(horizontal=12),
                    on_click=cerrar_sesion,
                    content=ft.Row(
                        spacing=12,
                        controls=[
                            ft.Text("->", size=16, color=MUTED),
                            ft.Text("Sign Out", size=13, color=BRAND_DARK),
                        ],
                    ),
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )

    overlay = ft.Container(
        ref=panel_ref,
        expand=True,
        bgcolor="#00000022",
        alignment=ft.Alignment(-1, 0),
        content=panel,
    )

    page.overlay.append(overlay)
    page.update()
