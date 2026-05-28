import sys
import os
import ssl

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
        getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

import flet as ft
from screens.bienvenida import show_bienvenida
from screens.login import show_login
from screens.seleccion_rol import show_seleccion_rol
from screens.registro import registro
from screens.personalizar import personalizar
from screens.home import show_home
from screens.carrito import show_carrito
from screens.vendedor import show_vendedor
from screens.pago import show_pago
from screens.perfil import show_perfil

def main(page: ft.Page):
    page.title = "CraftHub"
    page.window.width = 1280
    page.window.height = 800
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.bgcolor = "#FAFAFA"

    carrito_global = []
    usuario_global = {"user": None, "perfil": None}

    def ir_bienvenida():
        show_bienvenida(
            page,
            ir_login=ir_seleccion_rol,
            ir_explorar=ir_seleccion_rol,
            ir_registro=ir_seleccion_rol,
        )

    def ir_seleccion_rol():
        show_seleccion_rol(
            page,
            ir_bienvenida=ir_bienvenida,
            ir_comprador=ir_home_visitante,
            ir_vendedor=lambda: ir_login("Vendedor"),
            ir_login_comprador=lambda: ir_login("Comprador"),
            ir_registro_comprador=lambda: ir_registro("Comprador"),
        )

    def ir_login(modo="Comprador"):
        show_login(
            page,
            ir_bienvenida=ir_bienvenida,
            ir_registro=ir_registro,
            ir_home_comprador=ir_home_comprador,
            ir_home_vendedor=ir_home_vendedor,
            modo=modo,
            ir_roles=ir_seleccion_rol,
        )

    def ir_registro(rol_inicial=None):
        registro(
            page,
            ir_login=ir_login,
            ir_home_comprador=ir_home_comprador,
            ir_home_vendedor=ir_home_vendedor,
            rol_inicial=rol_inicial,
        )

    def ir_personalizar():
        personalizar(page, ir_login=ir_login, ir_home=ir_home_comprador_sin_args)

    def ir_home_comprador(user=None, perfil=None):
        if user:
            usuario_global["user"] = user
            usuario_global["perfil"] = perfil
        show_home(
            page,
            ir_bienvenida=ir_bienvenida,
            ir_carrito=ir_carrito,
            carrito_global=carrito_global,
            usuario=usuario_global,
            ir_perfil=ir_perfil,
        )

    def ir_home_comprador_sin_args():
        ir_home_comprador()

    def ir_home_visitante():
        usuario_global["user"] = None
        usuario_global["perfil"] = None
        ir_home_comprador()

    def ir_home_vendedor(user=None, perfil=None):
        if user:
            usuario_global["user"] = user
            usuario_global["perfil"] = perfil
        show_vendedor(
            page,
            ir_bienvenida=ir_bienvenida,
            usuario=usuario_global,
            ir_perfil=ir_perfil,
        )

    def ir_perfil():
        show_perfil(
            page,
            ir_home=ir_home_comprador_sin_args,
            ir_bienvenida=ir_bienvenida,
            usuario=usuario_global,
        )

    def ir_pago():
        show_pago(
            page,
            ir_home=ir_home_comprador_sin_args,
            carrito_global=carrito_global,
            usuario=usuario_global,
        )

    def ir_carrito():
        show_carrito(
            page,
            ir_home=ir_home_comprador_sin_args,
            carrito_global=carrito_global,
            ir_pago=ir_pago,
            usuario=usuario_global,
        )

    ir_bienvenida()


ft.app(main, assets_dir="assets")
