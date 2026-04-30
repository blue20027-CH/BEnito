# screens/bienvenida.py - NUEVO (simple, sin tarjetas)
import flet as ft
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BRAND = "#800000"
BRAND_LIGHT = "#F5E8E8"

def show_bienvenida(page: ft.Page, ir_login):
    page.clean()

    page.add(
        ft.Container(
            expand=True,
            alignment=ft.Alignment(0, 0),
            bgcolor="#FAFAFA",
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=0,
                controls=[
                    ft.Container(
                        width=90, height=90,
                        border_radius=16,
                        bgcolor=BRAND,
                        alignment=ft.Alignment(0, 0),
                        content=ft.Text("CH", color="white",
                                        size=38, weight=ft.FontWeight.BOLD)
                    ),
                    ft.Container(height=16),
                    ft.Text("CRAFTHUB", size=13, color=BRAND,
                            weight=ft.FontWeight.BOLD),
                    ft.Container(height=8),
                    ft.Text("Creatividad con Propósito", size=18,
                            color="#1A1A1A", weight=ft.FontWeight.BOLD),
                    ft.Text("Artesanías panameñas únicas",
                            size=14, color="#888888"),
                    ft.Container(height=40),
                    ft.ElevatedButton(
                        "Entrar",
                        width=260, height=52,
                        bgcolor=BRAND, color="white",
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=12),
                            elevation=0,
                        ),
                        on_click=lambda _: ir_login()
                    ),
                ]
            )
        )
    )
    page.update()