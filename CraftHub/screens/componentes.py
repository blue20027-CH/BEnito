import flet as ft




def tabler_icon(name, size=24, color=None):
    return ft.Image(
        src=f"icons/{name}.svg",
        width=size,
        height=size,
        fit="contain",
        error_content=ft.Container(
            width=size,
            height=size,
            alignment=ft.Alignment(0, 0),
            content=ft.Text("", size=1),
        ),
    )


def craft_logo(size=40, on_click=None, bgcolor=None, radius=0):
    return ft.Container(
        width=size,
        height=size,
        border_radius=radius,
        bgcolor=bgcolor,
        alignment=ft.Alignment(0, 0),
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        on_click=on_click,
        content=ft.Image(
            src="Craft_logo.png",
            fit="contain",
            width=size,
            height=size,
            error_content=ft.Container(width=size, height=size, bgcolor=bgcolor),
        ),
    )


def craft_banner_header(title, subtitle=None, height=68, on_logo_click=None, actions=None):
    return ft.Container(
        height=height,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        content=ft.Stack(
            controls=[
                ft.Image(
                    src="banner.png",
                    fit="cover",
                    width=float("inf"),
                    height=height,
                ),
                ft.Container(bgcolor="#00000055", height=height),
                ft.Container(
                    height=height,
                    padding=ft.padding.symmetric(horizontal=24, vertical=10),
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Row(
                                spacing=10,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    craft_logo(42, on_click=on_logo_click),
                                    ft.Column(
                                        spacing=1,
                                        alignment=ft.MainAxisAlignment.CENTER,
                                        controls=[
                                            ft.Text(title, size=15, color="white", weight=ft.FontWeight.BOLD),
                                            ft.Text(subtitle, size=11, color="#F2F2F2", visible=bool(subtitle)),
                                        ],
                                    ),
                                ],
                            ),
                            ft.Row(spacing=8, controls=actions or []),
                        ],
                    ),
                ),
            ],
        ),
    )
