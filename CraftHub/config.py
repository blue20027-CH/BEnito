import flet as ft

BRAND = "#800000"
BRAND_LIGHT = "#F5E8E8"
GRIS = "#F4F4F4"
TEXTO = "#1A1A1A"
MUTED = "#888888"

PRODUCTOS = [
    {"nombre": "Mola Kuna", "precio": "$45.00", "categoria": "Artesanía",
     "region": "Guna Yala", "color": "#C4A882",
     "img": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=300&q=80"},
    {"nombre": "Sombrero Pintao", "precio": "$80.00", "categoria": "Vestir",
     "region": "Los Santos", "color": "#A0856A",
     "img": "https://images.unsplash.com/photo-1521369909029-2afed882baee?w=300&q=80"},
    {"nombre": "Vasija de Barro", "precio": "$35.00", "categoria": "Artesanía",
     "region": "Coclé", "color": "#7A6250",
     "img": "https://images.unsplash.com/photo-1565193566173-7a0ee3dbe261?w=300&q=80"},
    {"nombre": "Collar Emberá", "precio": "$55.00", "categoria": "Joyería",
     "region": "Darién", "color": "#B8956A",
     "img": "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=300&q=80"},
    {"nombre": "Tejido Ngäbe", "precio": "$60.00", "categoria": "Vestir",
     "region": "Chiriquí", "color": "#8B6F47",
     "img": "https://images.unsplash.com/photo-1558769132-cb1aea458c5e?w=300&q=80"},
    {"nombre": "Cesta de Palma", "precio": "$28.00", "categoria": "Artesanía",
     "region": "Veraguas", "color": "#D4A96A",
     "img": "https://images.unsplash.com/photo-1590736704728-f4730bb30770?w=300&q=80"},
    {"nombre": "Talla en Tagua", "precio": "$22.00", "categoria": "Artesanía",
     "region": "Colón", "color": "#C8A97E",
     "img": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=300&q=80"},
    {"nombre": "Pulsera de Chaquira", "precio": "$15.00", "categoria": "Joyería",
     "region": "Bocas del Toro", "color": "#A67C52",
     "img": "https://images.unsplash.com/photo-1611591437281-460bfbe1220a?w=300&q=80"},
    {"nombre": "Pollera Típica", "precio": "$150.00", "categoria": "Vestir",
     "region": "Herrera", "color": "#E8C9A0",
     "img": "https://images.unsplash.com/photo-1603189343302-e603f7add05a?w=300&q=80"},
    {"nombre": "Máscara Ritual", "precio": "$40.00", "categoria": "Artesanía",
     "region": "Darién", "color": "#8B7355",
     "img": "https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?w=300&q=80"},
    {"nombre": "Aretes de Coral", "precio": "$30.00", "categoria": "Joyería",
     "region": "Guna Yala", "color": "#CC8866",
     "img": "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=300&q=80"},
    {"nombre": "Hamaca Artesanal", "precio": "$95.00", "categoria": "Mobiliario",
     "region": "Los Santos", "color": "#B8A090",
     "img": "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=300&q=80"},
    {"nombre": "Flauta de Caña", "precio": "$25.00", "categoria": "Instrumentos",
     "region": "Chiriquí", "color": "#9E8A6E",
     "img": "https://images.unsplash.com/photo-1507838153414-b4b713384a76?w=300&q=80"},
    {"nombre": "Bolso de Fibra", "precio": "$38.00", "categoria": "Accesorios",
     "region": "Coclé", "color": "#C4956A",
     "img": "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=300&q=80"},
    {"nombre": "Cerámica Pintada", "precio": "$48.00", "categoria": "Artesanía",
     "region": "Panamá", "color": "#D4845A",
     "img": "https://images.unsplash.com/photo-1519638399535-1b036603ac77?w=300&q=80"},
    {"nombre": "Tapiz de Algodón", "precio": "$70.00", "categoria": "Vestir",
     "region": "Veraguas", "color": "#A08060",
     "img": "https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=300&q=80"},
]


def logo(size=40):
    return ft.Container(
        width=size, height=size,
        border_radius=8,
        bgcolor=BRAND,
        alignment=ft.Alignment(0, 0),
        content=ft.Text("CH", color="white",
                        size=size // 2.2,
                        weight=ft.FontWeight.BOLD)
    )

def separador(h=20):
    return ft.Container(height=h)

def boton_primario(texto, ancho=280, alto=48, accion=None):
    return ft.ElevatedButton(
        texto, width=ancho, height=alto,
        bgcolor=BRAND, color="white",
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10),
            elevation=0,
        ),
        on_click=accion
    )

def boton_secundario(texto, ancho=280, alto=48, accion=None):
    return ft.OutlinedButton(
        texto, width=ancho, height=alto,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=10),
            side=ft.BorderSide(1, "#CCCCCC"),
        ),
        on_click=accion
    )

def campo(hint, password=False):
    return ft.TextField(
        hint_text=hint,
        password=password,
        can_reveal_password=password,
        height=48,
        border_radius=10,
        border_color="#DDDDDD",
        focused_border_color=BRAND,
        bgcolor="white",
        content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
    )

def panel(contenido, ancho=460):
    return ft.Container(
        width=ancho,
        bgcolor="white",
        border_radius=20,
        border=ft.border.all(1, "#EEEEEE"),
        padding=40,
        content=contenido,
        shadow=ft.BoxShadow(
            blur_radius=30,
            color="#00000010",
            offset=ft.Offset(0, 4)
        )
    )

def lado_marca(titulo_txt, subtitulo_txt, extra=None):
    controls = [
        logo(60),
        separador(24),
        ft.Text(titulo_txt, size=38,
                weight=ft.FontWeight.BOLD, color="white"),
        ft.Text(subtitulo_txt, size=15, color="#FFB3B3"),
    ]
    if extra:
        controls += [separador(20), extra]
    return ft.Container(
        width=380,
        bgcolor=BRAND,
        padding=50,
        content=ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=12,
            controls=controls
        )
    )

def chip_seleccionable(nombre, sel_dict, texto_ref, accion):
    seleccionado = {"v": False}
    cont = ft.Ref[ft.Container]()

    def toggle(e):
        seleccionado["v"] = not seleccionado["v"]
        sel_dict["count"] += 1 if seleccionado["v"] else -1
        texto_ref.value = f"{sel_dict['count']} / 3 seleccionadas"
        cont.current.bgcolor = BRAND_LIGHT if seleccionado["v"] else "white"
        cont.current.border = ft.border.all(
            2 if seleccionado["v"] else 1,
            BRAND if seleccionado["v"] else "#E0E0E0"
        )
        accion()

    return ft.Container(
        ref=cont,
        height=38,
        border_radius=19,
        bgcolor="white",
        border=ft.border.all(1, "#E0E0E0"),
        padding=ft.padding.symmetric(horizontal=16, vertical=8),
        on_click=toggle,
        content=ft.Text(nombre, size=12,
                        text_align=ft.TextAlign.CENTER,
                        color=TEXTO, weight=ft.FontWeight.W_500)
    )