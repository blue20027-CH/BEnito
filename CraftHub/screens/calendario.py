import flet as ft
from screens.componentes import craft_logo, tabler_icon

BRAND = "#941515"
TEXT = "#1F1F1F"
MUTED = "#777777"
BORDER = "#E2CFCF"
BG = "#FAFAFA"

EVENTOS = [
    {"dia": 9, "titulo": "Feria artesanal de Panama", "lugar": "Centro de Convenciones, Panama", "hora": "9 de abril - 4:00 p. m.", "imagen": "eventos/Panama.png", "cupos": 18, "tipo": "Feria"},
    {"dia": 13, "titulo": "Exhibicion de molas", "lugar": "Centro cultural, Guna Yala", "hora": "13 de abril - 12:30 p. m.", "imagen": "eventos/Guna-Yala.png", "cupos": 8, "tipo": "Exhibicion"},
    {"dia": 24, "titulo": "Taller de ceramica y alfareria", "lugar": "Casa de la Cultura, Cocle", "hora": "24 de abril - 10:00 a. m.", "imagen": "eventos/Cocle.png", "cupos": 12, "tipo": "Taller"},
]


def _header(ir_back):
    return ft.Container(
        height=58, bgcolor="white",
        border=ft.border.only(bottom=ft.BorderSide(1, "#D6B4B4")),
        padding=ft.padding.symmetric(horizontal=28),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Row(spacing=18, controls=[
                    ft.Container(width=34, height=34, border_radius=17, alignment=ft.Alignment(0, 0), on_click=lambda _: ir_back(), content=tabler_icon("arrow-left", size=22)),
                    ft.Text("Calendario de eventos", size=18, color=BRAND, weight=ft.FontWeight.BOLD),
                ]),
                craft_logo(36),
            ],
        ),
    )


def _selector(label, activo=False):
    return ft.Container(height=28, width=112, border_radius=14, bgcolor=BRAND if activo else "white", border=ft.border.all(1, BRAND), alignment=ft.Alignment(0, 0), content=ft.Text(label, size=10, color="white" if activo else BRAND, weight=ft.FontWeight.BOLD if activo else ft.FontWeight.NORMAL))


def _dia(numero, activo=False, tenue=False):
    return ft.Container(width=42, height=36, border_radius=6, bgcolor=BRAND if activo else ("#F5F5F5" if tenue else "transparent"), alignment=ft.Alignment(0, 0), content=ft.Text(str(numero), size=12, color="white" if activo else ("#BBBBBB" if tenue else TEXT), weight=ft.FontWeight.BOLD if activo else ft.FontWeight.NORMAL))


def _calendar_grid():
    controles = []
    dias = ["Do", "Lu", "Ma", "Mi", "Ju", "Vi", "Sa"]
    controles.append(ft.Row(alignment=ft.MainAxisAlignment.SPACE_AROUND, controls=[ft.Container(width=42, alignment=ft.Alignment(0, 0), content=ft.Text(d, size=10, color=MUTED)) for d in dias]))
    semanas = [["", "", "", 1, 2, 3, 4], [5, 6, 7, 8, 9, 10, 11], [12, 13, 14, 15, 16, 17, 18], [19, 20, 21, 22, 23, 24, 25], [26, 27, 28, 29, 30, 1, 2]]
    destacados = {9, 13, 24}
    for semana in semanas:
        fila = []
        for d in semana:
            fila.append(ft.Container(width=42, height=36) if d == "" else _dia(d, activo=d in destacados, tenue=d in [1, 2] and semana[-1] == 2))
        controles.append(ft.Row(alignment=ft.MainAxisAlignment.SPACE_AROUND, controls=fila))
    return ft.Column(spacing=16, controls=controles)


def _event_card(evento, invertido=False, vendedor=False):
    imagen = ft.Container(width=150, height=102, border_radius=8, border=ft.border.all(8, BRAND), clip_behavior=ft.ClipBehavior.HARD_EDGE, content=ft.Image(src=evento["imagen"], fit="cover", width=150, height=102, error_content=ft.Container(bgcolor="#EFEFEF", alignment=ft.Alignment(0, 0), content=tabler_icon("photo", size=28))))
    info = ft.Container(expand=True, padding=ft.padding.symmetric(horizontal=10, vertical=8), content=ft.Column(spacing=7, controls=[
        ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[ft.Text(evento["titulo"], size=12, color=TEXT, weight=ft.FontWeight.BOLD, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS), ft.Text(evento["tipo"], size=9, color=BRAND, weight=ft.FontWeight.BOLD)]),
        ft.Row(spacing=8, controls=[tabler_icon("map-pin", size=14), ft.Text(evento["lugar"], size=10, color=TEXT, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS)]),
        ft.Row(spacing=8, controls=[tabler_icon("calendar", size=14), ft.Text(evento["hora"], size=10, color=TEXT)]),
        ft.Text("Puestos disponibles: " + str(evento["cupos"]), size=10, color=MUTED),
        ft.Row(spacing=10, controls=[ft.Container(width=74, height=22, border_radius=11, bgcolor="#C9C9C9", alignment=ft.Alignment(0, 0), content=ft.Text("Asistir", size=9, color=TEXT, weight=ft.FontWeight.BOLD)), ft.Container(width=96, height=22, border_radius=11, border=ft.border.all(1, "#C9C9C9"), alignment=ft.Alignment(0, 0), content=ft.Text("Reservar puesto" if vendedor else "Me interesa", size=9, color=TEXT, weight=ft.FontWeight.BOLD))]),
    ]))
    return ft.Container(height=124, border_radius=14, bgcolor="white", border=ft.border.all(1, BRAND), padding=8, shadow=ft.BoxShadow(blur_radius=8, color="#00000012", offset=ft.Offset(0, 3)), content=ft.Row(spacing=10, controls=([info, imagen] if invertido else [imagen, info])))


def show_calendario(page: ft.Page, ir_back, usuario=None):
    page.clean()
    perfil = (usuario or {}).get("perfil") or {}
    rol = (perfil.get("rol") or perfil.get("tipo") or "").lower()
    vendedor = "vendedor" in rol
    page.add(ft.Column(expand=True, spacing=0, controls=[
        _header(ir_back),
        ft.Container(expand=True, bgcolor=BG, padding=ft.padding.all(34), content=ft.Row(spacing=34, vertical_alignment=ft.CrossAxisAlignment.START, controls=[
            ft.Container(width=620, bgcolor="white", border_radius=14, border=ft.border.all(1, BORDER), padding=20, shadow=ft.BoxShadow(blur_radius=10, color="#00000012", offset=ft.Offset(0, 3)), content=ft.Column(spacing=22, controls=[
                ft.Text("No te pierdas ningun momento de la comunidad artesanal.", size=14, color=TEXT, weight=ft.FontWeight.BOLD),
                ft.Row(alignment=ft.MainAxisAlignment.SPACE_AROUND, controls=[_selector("Dia"), _selector("Semana"), _selector("Mes", True), _selector("Ano")]),
                ft.Row(spacing=10, controls=[ft.Container(width=28, height=28, border_radius=14, alignment=ft.Alignment(0, 0), content=tabler_icon("arrow-left", size=16)), ft.Container(expand=True, height=36, border_radius=8, border=ft.border.all(1, "#E6E6E6"), padding=ft.padding.symmetric(horizontal=12), alignment=ft.Alignment(-1, 0), content=ft.Text("Abril", size=12, color=TEXT)), ft.Container(expand=True, height=36, border_radius=8, border=ft.border.all(1, "#E6E6E6"), padding=ft.padding.symmetric(horizontal=12), alignment=ft.Alignment(-1, 0), content=ft.Text("2026", size=12, color=TEXT)), ft.Container(width=28, height=28, border_radius=14, alignment=ft.Alignment(0, 0), content=ft.Text(">", size=18, color=TEXT))]),
                ft.Container(border_radius=8, border=ft.border.all(1, "#EEEEEE"), padding=24, content=_calendar_grid()),
            ])),
            ft.Container(expand=True, content=ft.Column(spacing=18, controls=[_event_card(e, invertido=i % 2 == 1, vendedor=vendedor) for i, e in enumerate(EVENTOS)])),
        ])),
    ]))
    page.update()
