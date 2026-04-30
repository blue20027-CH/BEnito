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
from screens.registro import registro
from screens.personalizar import personalizar
from screens.home import show_home
from screens.carrito import show_carrito
from screens.vendedor import show_vendedor


def main(page: ft.Page):
    page.title = "CraftHub"
    page.window_width = 1280
    page.window_height = 800
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.bgcolor = "#FAFAFA"

    carrito_global = []
    usuario_global = {"user": None, "perfil": None}

    def ir_bienvenida():
        show_bienvenida(page, ir_login=ir_login)

    def ir_login():
        show_login(
            page,
            ir_bienvenida=ir_bienvenida,
            ir_registro=ir_registro,
            ir_home_comprador=ir_home_comprador,
            ir_home_vendedor=ir_home_vendedor,
        )

    def ir_registro():
        registro(
            page,
            ir_login=ir_login,
            ir_home_comprador=ir_home_comprador,
            ir_home_vendedor=ir_home_vendedor,
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
        )

    def ir_home_comprador_sin_args():
        ir_home_comprador()

    def ir_home_vendedor(user=None, perfil=None):
        if user:
            usuario_global["user"] = user
            usuario_global["perfil"] = perfil
        show_vendedor(
            page,
            ir_bienvenida=ir_bienvenida,
            usuario=usuario_global,
        )

    def ir_carrito():
        show_carrito(
            page,
            ir_home=ir_home_comprador_sin_args,
            carrito_global=carrito_global,
        )

    ir_bienvenida()


ft.app(target=main)