import flet as ft
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (BRAND, TEXTO, MUTED,
                    separador, lado_marca, chip_seleccionable)


def personalizar(page: ft.Page, ir_login, ir_home):
    page.clean()

    provincias = [
        ["Colon", "Cocle", "Panama", "Panama Oeste", "Los Santos"],
        ["Bocas del Toro", "Veraguas", "Darien", "Chiriqui"],
        ["Herrera", "Guna Yala", "Embera-Wounaan", "Wargandi"],
    ]
    categorias = [
        ["Artesania", "Vestir", "Calzado", "Joyeria"],
        ["Accesorios", "Alimentos", "Mobiliario", "Instrumentos"],
    ]

    sel_prov = {"count": 0}
    sel_cat = {"count": 0}
    txt_prov = ft.Text("0 / 3 seleccionadas", size=12, color=MUTED)
    txt_cat = ft.Text("0 / 3 seleccionadas", size=12, color=MUTED)
    btn_ref = ft.Ref[ft.ElevatedButton]()

    def actualizar():
        ok = sel_prov["count"] >= 3 and sel_cat["count"] >= 3
        if btn_ref.current:
            btn_ref.current.bgcolor = BRAND if ok else "#CCCCCC"
            btn_ref.current.disabled = not ok
        page.update()

    def filas_chips(lista, sel_dict, txt_ref):
        return [
            ft.Row(spacing=8, controls=[
                chip_seleccionable(n, sel_dict, txt_ref, actualizar)
                for n in fila
            ])
            for fila in lista
        ]

    def bloque(titulo_txt, desc, filas, txt_conteo):
        return ft.Container(
            bgcolor="white",
            border_radius=16,
            border=ft.border.all(1, "#EEEEEE"),
            padding=24,
            content=ft.Column(spacing=10, controls=[
                ft.Text(titulo_txt, size=15,
                        weight=ft.FontWeight.BOLD, color=TEXTO),
                ft.Text(desc, size=12, color=MUTED),
                separador(4),
                *filas,
                separador(4),
                txt_conteo,
            ])
        )

    contenido = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        expand=True,
        spacing=18,
        controls=[
            ft.Row(controls=[
                ft.TextButton("< Volver",
                              style=ft.ButtonStyle(color=MUTED),
                              on_click=lambda _: ir_login())
            ]),
            ft.Text("Personaliza tu experiencia", size=26,
                    weight=ft.FontWeight.BOLD, color=TEXTO),
            ft.Text("Selecciona al menos 3 provincias y 3 categorias",
                    size=13, color=MUTED),
            separador(4),
            bloque("Provincias y comarcas",
                   "Te mostraremos productos y eventos cerca de ti",
                   filas_chips(provincias, sel_prov, txt_prov), txt_prov),
            bloque("Categorias favoritas",
                   "Te recomendaremos productos ajustados a tu estilo",
                   filas_chips(categorias, sel_cat, txt_cat), txt_cat),
            separador(8),
            ft.Row(
                alignment=ft.MainAxisAlignment.END,
                controls=[
                    ft.ElevatedButton(
                        ref=btn_ref,
                        content=ft.Text("Continuar",
                                        weight=ft.FontWeight.BOLD),
                        width=200, height=48,
                        bgcolor="#CCCCCC",
                        color="white",
                        disabled=True,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=10),
                            elevation=0,
                        ),
                        on_click=lambda _: ir_home()
                    )
                ]
            ),
            separador(20),
        ]
    )

    page.add(
        ft.Row(
            expand=True, spacing=0,
            controls=[
                lado_marca("Casi\nlisto",
                           "Cuentanos tus intereses\npara personalizar\ntu experiencia."),
                ft.Container(
                    expand=True,
                    bgcolor="#FAFAFA",
                    padding=ft.padding.symmetric(horizontal=50, vertical=30),
                    content=contenido
                )
            ]
        )
    )
    page.update()