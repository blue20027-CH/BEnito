import flet as ft
from screens.componentes import craft_logo, tabler_icon

BRAND = "#941515"
TEXT = "#1F1F1F"
MUTED = "#777777"
BORDER = "#E2CFCF"
BG = "#FAFAFA"


EVENTOS = [
    {
        "dia": 9,
        "titulo": "Feria de ceramica artesanal",
        "lugar": "Casco Antiguo",
        "hora": "Abril 9 - 4:00 PM",
        "tipo": "Feria",
    },
    {
        "dia": 13,
        "titulo": "Exhibicion de molas",
        "lugar": "Colon 2000 Duty Free Mall",
        "hora": "Abril 11 - 12:30 PM",
        "tipo": "Expo",
    },
    {
        "dia": 24,
        "titulo": "Taller de alfareria",
        "lugar": "Centro de Arte y Cultura",
        "hora": "Abril 13 - 10:00 AM",
        "tipo": "Workshop",
    },
]


def _header(ir_back):
    return ft.Container(
        height=58,
        bgcolor="white",
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
    return ft.Container(
        height=32,
        width=118,
        border_radius=16,
        bgcolor=BRAND if activo else "white",
        border=ft.border.all(1, BRAND),
        alignment=ft.Alignment(0, 0),
        content=ft.Text(label, size=11, color="white" if activo else BRAND, weight=ft.FontWeight.BOLD if activo else ft.FontWeight.NORMAL),
    )


def _dia(numero, activo=False, tenue=False):
    return ft.Container(
        width=42,
        height=36,
        border_radius=6,
        bgcolor=BRAND if activo else ("#F5F5F5" if tenue else "transparent"),
        alignment=ft.Alignment(0, 0),
        content=ft.Text(str(numero), size=12, color="white" if activo else ("#BBBBBB" if tenue else TEXT), weight=ft.FontWeight.BOLD if activo else ft.FontWeight.NORMAL),
    )


def _calendar_grid():
    controles = []
    dias = ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"]
    controles.append(
        ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_AROUND,
            controls=[ft.Container(width=42, alignment=ft.Alignment(0, 0), content=ft.Text(d, size=10, color=MUTED)) for d in dias],
        )
    )
    semanas = [
        ["", "", "", 1, 2, 3, 4],
        [5, 6, 7, 8, 9, 10, 11],
        [12, 13, 14, 15, 16, 17, 18],
        [19, 20, 21, 22, 23, 24, 25],
        [26, 27, 28, 29, 30, 1, 2],
    ]
    destacados = {9, 13, 24}
    for semana in semanas:
        fila = []
        for d in semana:
            if d == "":
                fila.append(ft.Container(width=42, height=36))
            else:
                fila.append(_dia(d, activo=d in destacados, tenue=d in [1, 2] and semana[-1] == 2))
        controles.append(ft.Row(alignment=ft.MainAxisAlignment.SPACE_AROUND, controls=fila))
    return ft.Column(spacing=16, controls=controles)


def _event_card(evento, invertido=False):
    imagen = ft.Container(
        width=150,
        height=102,
        border_radius=8,
        border=ft.border.all(8, BRAND),
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        content=ft.Image(src="banner.png", fit="cover", width=150, height=102),
    )
    info = ft.Container(
        expand=True,
        padding=ft.padding.symmetric(horizontal=10, vertical=8),
        content=ft.Column(
            spacing=8,
            controls=[
                ft.Text(evento["titulo"], size=13, color=TEXT, weight=ft.FontWeight.BOLD),
                ft.Row(spacing=8, controls=[tabler_icon("map-pin", size=15), ft.Text(evento["lugar"], size=11, color=TEXT)]),
                ft.Row(spacing=8, controls=[tabler_icon("calendar", size=15), ft.Text(evento["hora"], size=11, color=TEXT)]),
                ft.Row(spacing=10, controls=[
                    ft.Container(width=80, height=24, border_radius=12, bgcolor="#C9C9C9", alignment=ft.Alignment(0, 0), content=ft.Text("Ir", size=10, color=TEXT, weight=ft.FontWeight.BOLD)),
                    ft.Container(width=80, height=24, border_radius=12, border=ft.border.all(1, "#C9C9C9"), alignment=ft.Alignment(0, 0), content=ft.Text("Reservar", size=10, color=TEXT, weight=ft.FontWeight.BOLD)),
                ]),
            ],
        ),
    )
    return ft.Container(
        height=124,
        border_radius=14,
        bgcolor="white",
        border=ft.border.all(1, BRAND),
        padding=8,
        shadow=ft.BoxShadow(blur_radius=8, color="#00000012", offset=ft.Offset(0, 3)),
        content=ft.Row(spacing=10, controls=([info, imagen] if invertido else [imagen, info])),
    )


def show_calendario(page: ft.Page, ir_back):
    page.clean()
    page.add(
        ft.Column(
            expand=True,
            spacing=0,
            controls=[
                _header(ir_back),
                ft.Container(
                    expand=True,
                    bgcolor=BG,
                    padding=ft.padding.all(34),
                    content=ft.Row(
                        spacing=34,
                        vertical_alignment=ft.CrossAxisAlignment.START,
                        controls=[
                            ft.Container(
                                width=620,
                                bgcolor="white",
                                border_radius=14,
                                border=ft.border.all(1, BORDER),
                                padding=20,
                                shadow=ft.BoxShadow(blur_radius=10, color="#00000012", offset=ft.Offset(0, 3)),
                                content=ft.Column(
                                    spacing=22,
                                    controls=[
                                        ft.Text("No te pierdas ningun momento de la comunidad artesanal.", size=14, color=TEXT, weight=ft.FontWeight.BOLD),
                                        ft.Row(alignment=ft.MainAxisAlignment.SPACE_AROUND, controls=[_selector("Dia"), _selector("Semana"), _selector("Mes", True), _selector("Ano")]),
                                        ft.Row(spacing=10, controls=[
                                            ft.Container(width=28, height=28, border_radius=14, alignment=ft.Alignment(0, 0), content=tabler_icon("arrow-left", size=16)),
                                            ft.Container(expand=True, height=36, border_radius=8, border=ft.border.all(1, "#E6E6E6"), padding=ft.padding.symmetric(horizontal=12), alignment=ft.Alignment(-1, 0), content=ft.Text("Abril", size=12, color=TEXT)),
                                            ft.Container(expand=True, height=36, border_radius=8, border=ft.border.all(1, "#E6E6E6"), padding=ft.padding.symmetric(horizontal=12), alignment=ft.Alignment(-1, 0), content=ft.Text("2026", size=12, color=TEXT)),
                                            ft.Container(width=28, height=28, border_radius=14, alignment=ft.Alignment(0, 0), content=ft.Text(">", size=18, color=TEXT)),
                                        ]),
                                        ft.Container(
                                            border_radius=8,
                                            border=ft.border.all(1, "#EEEEEE"),
                                            padding=24,
                                            content=_calendar_grid(),
                                        ),
                                    ],
                                ),
                            ),
                            ft.Container(
                                expand=True,
                                content=ft.Column(
                                    spacing=18,
                                    controls=[_event_card(e, invertido=i % 2 == 1) for i, e in enumerate(EVENTOS)],
                                ),
                            ),
                        ],
                    ),
                ),
            ],
        )
    )
    page.update()
