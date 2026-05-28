import flet as ft
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supabase_client import supabase
from screens.menu_perfil import abrir_menu_perfil
from screens.componentes import craft_logo
from datetime import datetime, timezone, timedelta
import threading
import tkinter as tk
from tkinter import filedialog

BRAND = "#941515"
BRAND_DARK = "#760F0F"
BRAND_LIGHT = "#FFF2F2"
TEXTO = "#232323"
MUTED = "#777777"
BORDER = "#E5DADA"
BG = "#FAFAFA"


def show_vendedor(page: ft.Page, ir_bienvenida, usuario, ir_perfil=None):
    page.clean()

    perfil = usuario.get("perfil") or {}
    nombre_vendedor = perfil.get("nombre", "Vendedor")
    tab_activo = {"v": "productos"}
    busqueda = {"v": ""}
    cuerpo_ref = ft.Ref[ft.Container]()
    tab_refs = {}

    def precio_float(valor):
        try:
            if isinstance(valor, (int, float)):
                return float(valor)
            return float(str(valor).replace("$", "").replace(",", ""))
        except Exception:
            return 0.0

    def cargar_productos():
        try:
            resp = supabase.table("productos").select("*").eq(
                "creador", nombre_vendedor).execute()
            return resp.data or []
        except Exception as ex:
            print("Error cargando productos:", ex)
            return []

    productos = cargar_productos()

    def cargar_pedidos():
        try:
            resp = supabase.table("pedidos").select("*").execute()
            todos = resp.data or []
            nombres = [p.get("nombre") for p in productos]
            resultado = []
            for pedido in todos:
                for item in pedido.get("productos") or []:
                    if item.get("nombre") in nombres:
                        resultado.append(pedido)
                        break
            return resultado
        except Exception as ex:
            print("Error cargando pedidos:", ex)
            return []

    def subtotal_vendedor(pedido):
        nombres = [p.get("nombre") for p in productos]
        total = 0.0
        cantidad_total = 0
        for item in pedido.get("productos") or []:
            if item.get("nombre") in nombres:
                cantidad = int(item.get("cantidad", 1) or 1)
                total += precio_float(item.get("precio", 0)) * cantidad
                cantidad_total += cantidad
        return total, cantidad_total

    def calcular_stats():
        pedidos = cargar_pedidos()
        ahora = datetime.now(timezone.utc)
        hace_7 = ahora - timedelta(days=7)
        hace_24 = ahora - timedelta(hours=24)
        semana = 0.0
        reciente = 0.0
        total = 0.0
        for pedido in pedidos:
            subtotal, _ = subtotal_vendedor(pedido)
            total += subtotal
            try:
                fecha = datetime.fromisoformat(
                    (pedido.get("created_at") or "").replace("Z", "+00:00"))
                if fecha >= hace_7:
                    semana += subtotal
                if fecha >= hace_24:
                    reciente += subtotal
            except Exception:
                pass
        return semana, reciente, total

    def productos_filtrados():
        termino = busqueda["v"].strip().lower()
        if not termino:
            return productos
        return [
            p for p in productos
            if termino in (p.get("nombre") or "").lower()
            or termino in (p.get("categoria") or "").lower()
        ]

    def mostrar_snack(texto):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(texto, color="white"),
            bgcolor=BRAND, duration=2000,
        )
        page.snack_bar.open = True
        page.update()

    def refrescar():
        nonlocal productos
        productos = cargar_productos()
        cambiar_tab(tab_activo["v"])

    def cargar_notificaciones():
        user = usuario.get("user")
        if not user:
            return []
        try:
            resp = supabase.table("notificaciones").select("*").eq(
                "user_id", user.id).eq("leida", False).order(
                "created_at", desc=True).execute()
            return resp.data or []
        except Exception as ex:
            print("Error cargando notificaciones:", ex)
            return []

    def marcar_leida(noti_id):
        try:
            supabase.table("notificaciones").update(
                {"leida": True}).eq("id", noti_id).execute()
        except Exception as ex:
            print("Error marcando notificacion:", ex)

    def abrir_notificaciones(e=None):
        notis = cargar_notificaciones()

        def cerrar(e=None):
            page.overlay.clear()
            page.update()

        def noti_card(n):
            return ft.Container(
                bgcolor="white", border_radius=16,
                border=ft.border.all(1, BORDER), padding=0,
                clip_behavior=ft.ClipBehavior.HARD_EDGE,
                shadow=ft.BoxShadow(blur_radius=10, color="#0000001A",
                                    offset=ft.Offset(0, 4)),
                content=ft.Column(spacing=0, controls=[
                    ft.Container(
                        bgcolor=BRAND_LIGHT,
                        padding=ft.padding.symmetric(horizontal=18, vertical=14),
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Row(spacing=10, controls=[
                                    ft.Container(
                                        width=36, height=36, border_radius=8,
                                        bgcolor=BRAND, alignment=ft.Alignment(0, 0),
                                        content=ft.Text("CH", color="white", size=12,
                                                        weight=ft.FontWeight.BOLD)
                                    ),
                                    ft.Text("CRAFTHUB", size=13, color=TEXTO,
                                            weight=ft.FontWeight.BOLD),
                                ]),
                                ft.Text((n.get("created_at") or "")[:10],
                                        size=11, color=MUTED),
                            ]
                        )
                    ),
                    ft.Container(
                        padding=20,
                        content=ft.Column(spacing=12, controls=[
                            ft.Row(spacing=16, controls=[
                                ft.Container(
                                    width=70, height=70, border_radius=35,
                                    bgcolor=BRAND, alignment=ft.Alignment(0, 0),
                                    content=ft.Text("💰", size=32)
                                ),
                                ft.Column(spacing=4, controls=[
                                    ft.Row(spacing=8, controls=[
                                        ft.Text(n.get("titulo", "Nueva venta"),
                                                size=18, weight=ft.FontWeight.BOLD,
                                                color=TEXTO),
                                        ft.Text("📢", size=16),
                                    ]),
                                    ft.Text(n.get("mensaje", ""), size=13, color=MUTED),
                                ])
                            ]),
                            ft.Container(
                                height=48, border_radius=10, bgcolor=BRAND,
                                alignment=ft.Alignment(0, 0),
                                on_click=lambda _, nid=n.get("id"): (
                                    marcar_leida(nid), cerrar(),
                                    cambiar_tab("pedidos")
                                ),
                                content=ft.Row(
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    spacing=8,
                                    controls=[
                                        ft.Text("Ver producto pendiente",
                                                color="white", size=14,
                                                weight=ft.FontWeight.BOLD),
                                        ft.Text("›", color="white", size=20),
                                    ]
                                )
                            )
                        ])
                    )
                ])
            )

        contenido = ft.Column(
            scroll=ft.ScrollMode.AUTO, spacing=16,
            controls=[noti_card(n) for n in notis] if notis else [
                ft.Container(
                    padding=60, alignment=ft.Alignment(0, 0),
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Text("🔔", size=40),
                            ft.Text("No tienes notificaciones nuevas",
                                    size=14, color=MUTED),
                        ]
                    )
                )
            ]
        )

        page.overlay.clear()
        page.overlay.append(
            ft.Container(
                expand=True, bgcolor="#00000066",
                alignment=ft.Alignment(0, 0), on_click=cerrar,
                content=ft.Container(
                    width=520, bgcolor="#F5EDED", border_radius=20, padding=24,
                    content=ft.Column(spacing=16, controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text("Notificaciones", size=20,
                                        weight=ft.FontWeight.BOLD, color=TEXTO),
                                ft.Container(
                                    width=32, height=32, border_radius=16,
                                    bgcolor=BRAND_LIGHT, alignment=ft.Alignment(0, 0),
                                    on_click=cerrar,
                                    content=ft.Text("x", color=BRAND,
                                                    weight=ft.FontWeight.BOLD)
                                )
                            ]
                        ),
                        contenido,
                    ])
                )
            )
        )
        page.update()

    # ── FORMULARIO CON UPLOAD E IMAGEN DE CAMARA ─────────────────
    def mostrar_formulario(producto_editar=None):
        es_edicion = producto_editar is not None

        def cerrar(e=None):
            page.overlay.clear()
            page.update()

        campo_nombre = ft.TextField(
            label="Nombre del producto",
            value=producto_editar.get("nombre", "") if es_edicion else "",
            border_radius=10, focused_border_color=BRAND,
        )
        campo_precio = ft.TextField(
            label="Precio",
            value=str(producto_editar.get("precio", "")) if es_edicion else "",
            border_radius=10, keyboard_type=ft.KeyboardType.NUMBER,
            focused_border_color=BRAND,
        )
        campo_stock = ft.TextField(
            label="Stock",
            value=str(producto_editar.get("stock", "0")) if es_edicion else "0",
            border_radius=10, keyboard_type=ft.KeyboardType.NUMBER,
            focused_border_color=BRAND,
        )
        campo_img = ft.TextField(
            label="URL de imagen",
            value=producto_editar.get("img", "") if es_edicion else "",
            border_radius=10, focused_border_color=BRAND,
            hint_text="Pega una URL o usa los botones de abajo",
        )
        campo_descripcion = ft.TextField(
            label="Descripcion",
            value=producto_editar.get("descripcion", "") if es_edicion else "",
            border_radius=10, multiline=True, min_lines=2, max_lines=3,
            focused_border_color=BRAND,
        )
        categorias = ["Artesania", "Joyeria", "Vestir", "Calzado",
                      "Instrumentos", "Accesorios", "Alimentos"]
        dropdown_categoria = ft.Dropdown(
            label="Categoria",
            value=producto_editar.get("categoria", "Artesania") if es_edicion else "Artesania",
            options=[ft.dropdown.Option(c) for c in categorias],
            border_radius=10, focused_border_color=BRAND,
        )
        error = ft.Text("", color="#B00020", size=12, visible=False)
        upload_status = ft.Text("", color=BRAND, size=12, visible=False)

        img_preview = ft.Container(
            width=80, height=80, border_radius=10,
            bgcolor="#F0F0F0", border=ft.border.all(1, BORDER),
            alignment=ft.Alignment(0, 0),
            content=ft.Text("🖼️", size=28),
        )

        def actualizar_preview(url):
            if url and url.startswith("http"):
                img_preview.content = ft.Image(
                    src=url, fit="cover", width=80, height=80)
            else:
                img_preview.content = ft.Text("🖼️", size=28)
            page.update()

        def on_url_change(e):
            actualizar_preview(e.control.value)

        campo_img.on_change = on_url_change

        if es_edicion and (producto_editar.get("img") or "").startswith("http"):
            img_preview.content = ft.Image(
                src=producto_editar.get("img"),
                fit="cover", width=80, height=80)

        def _subir_bytes(contenido, ext):
            nombre_archivo = f"producto_{datetime.now().strftime('%Y%m%d%H%M%S')}{ext}"
            content_type = (
                "image/jpeg" if ext in [".jpg", ".jpeg"] else
                "image/png" if ext == ".png" else "image/webp"
            )
            supabase.storage.from_("productos").upload(
                nombre_archivo, contenido,
                {"content-type": content_type, "x-upsert": "true"}
            )
            return supabase.storage.from_("productos").get_public_url(nombre_archivo)

        # ── SUBIR DESDE PC ────────────────────────────────────────
        def subir_imagen_thread():
            try:
                root = tk.Tk()
                root.withdraw()
                root.attributes("-topmost", True)
                ruta = filedialog.askopenfilename(
                    title="Selecciona una imagen",
                    filetypes=[
                        ("Imagenes", "*.jpg *.jpeg *.png *.webp"),
                        ("Todos", "*.*")
                    ]
                )
                root.destroy()
                if not ruta:
                    return
                upload_status.value = "Subiendo imagen..."
                upload_status.visible = True
                page.update()
                with open(ruta, "rb") as f:
                    contenido = f.read()
                ext = os.path.splitext(ruta)[1].lower() or ".jpg"
                url = _subir_bytes(contenido, ext)
                campo_img.value = url
                upload_status.value = "✅ Imagen subida correctamente"
                actualizar_preview(url)
                page.update()
            except Exception as ex:
                upload_status.value = f"❌ Error: {ex}"
                upload_status.visible = True
                page.update()

        def subir_imagen(e):
            threading.Thread(target=subir_imagen_thread, daemon=True).start()

        # ── CAMARA ────────────────────────────────────────────────
        def abrir_camara_thread():
            try:
                import cv2
                import tempfile

                upload_status.value = "Abriendo camara..."
                upload_status.visible = True
                page.update()

                cap = cv2.VideoCapture(0)
                if not cap.isOpened():
                    upload_status.value = "❌ No se encontro camara"
                    upload_status.visible = True
                    page.update()
                    return

                upload_status.value = "ESPACIO = capturar  |  ESC = cancelar"
                page.update()

                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    cv2.imshow("CraftHub - Camara  (ESPACIO = capturar, ESC = salir)", frame)
                    key = cv2.waitKey(1)
                    if key == 27:  # ESC
                        cap.release()
                        cv2.destroyAllWindows()
                        upload_status.value = "Camara cancelada"
                        page.update()
                        return
                    elif key == 32:  # ESPACIO
                        ruta = os.path.join(
                            tempfile.gettempdir(),
                            f"crafthub_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
                        )
                        cv2.imwrite(ruta, frame)
                        break

                cap.release()
                cv2.destroyAllWindows()

                upload_status.value = "Subiendo foto..."
                page.update()

                with open(ruta, "rb") as f:
                    contenido = f.read()

                url = _subir_bytes(contenido, ".jpg")
                campo_img.value = url
                upload_status.value = "✅ Foto tomada y subida"
                actualizar_preview(url)
                page.update()

            except ImportError:
                upload_status.value = "❌ Instala opencv: pip install opencv-python"
                upload_status.visible = True
                page.update()
            except Exception as ex:
                upload_status.value = f"❌ Error: {ex}"
                upload_status.visible = True
                page.update()

        def abrir_camara(e):
            threading.Thread(target=abrir_camara_thread, daemon=True).start()

        btn_subir = ft.Container(
            height=40, border_radius=10,
            bgcolor=BRAND_LIGHT, border=ft.border.all(1, BRAND),
            alignment=ft.Alignment(0, 0), on_click=subir_imagen,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER, spacing=8,
                controls=[
                    ft.Text("📁", size=14),
                    ft.Text("Subir imagen desde PC", size=13,
                            color=BRAND, weight=ft.FontWeight.W_500),
                ]
            ),
        )

        btn_camara = ft.Container(
            height=40, border_radius=10,
            bgcolor=BRAND_LIGHT, border=ft.border.all(1, BRAND),
            alignment=ft.Alignment(0, 0), on_click=abrir_camara,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER, spacing=8,
                controls=[
                    ft.Text("📷", size=14),
                    ft.Text("Tomar foto con camara", size=13,
                            color=BRAND, weight=ft.FontWeight.W_500),
                ]
            ),
        )

        def guardar(e):
            if not campo_nombre.value.strip() or not campo_precio.value.strip():
                error.value = "Completa el nombre y el precio."
                error.visible = True
                page.update()
                return
            try:
                datos = {
                    "nombre": campo_nombre.value.strip(),
                    "precio": float(campo_precio.value.strip()),
                    "stock": int(campo_stock.value.strip() or 0),
                    "categoria": dropdown_categoria.value,
                    "descripcion": campo_descripcion.value.strip(),
                    "img": campo_img.value.strip(),
                    "creador": nombre_vendedor,
                    "color": "#C4A882",
                }
                if es_edicion:
                    supabase.table("productos").update(datos).eq(
                        "id", producto_editar["id"]).execute()
                else:
                    supabase.table("productos").insert(datos).execute()
                cerrar()
                refrescar()
                mostrar_snack("Producto guardado correctamente")
            except Exception as ex:
                error.value = f"Error: {ex}"
                error.visible = True
                page.update()

        page.overlay.clear()
        page.overlay.append(
            ft.Container(
                expand=True, bgcolor="#00000066",
                alignment=ft.Alignment(0, 0), on_click=cerrar,
                content=ft.Container(
                    width=520, bgcolor="white", border_radius=16, padding=28,
                    content=ft.Column(
                        spacing=14, scroll=ft.ScrollMode.AUTO,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Text(
                                        "Editar producto" if es_edicion else "Nuevo producto",
                                        size=20, weight=ft.FontWeight.BOLD, color=TEXTO,
                                    ),
                                    ft.Container(
                                        width=32, height=32, border_radius=16,
                                        bgcolor=BRAND_LIGHT, alignment=ft.Alignment(0, 0),
                                        on_click=cerrar,
                                        content=ft.Text("x", color=BRAND,
                                                        weight=ft.FontWeight.BOLD),
                                    ),
                                ],
                            ),
                            error,
                            campo_nombre,
                            ft.Row(spacing=12, controls=[
                                ft.Container(expand=True, content=campo_precio),
                                ft.Container(expand=True, content=campo_stock),
                            ]),
                            dropdown_categoria,
                            ft.Row(
                                spacing=12,
                                vertical_alignment=ft.CrossAxisAlignment.START,
                                controls=[
                                    img_preview,
                                    ft.Column(expand=True, spacing=8, controls=[
                                        campo_img,
                                        btn_subir,
                                        btn_camara,
                                        upload_status,
                                    ]),
                                ]
                            ),
                            campo_descripcion,
                            ft.Row(
                                alignment=ft.MainAxisAlignment.END, spacing=12,
                                controls=[
                                    ft.OutlinedButton("Cancelar", on_click=cerrar),
                                    ft.ElevatedButton(
                                        "Guardar", bgcolor=BRAND, color="white",
                                        on_click=guardar,
                                    ),
                                ],
                            ),
                        ],
                    ),
                ),
            )
        )
        page.update()

    def eliminar_producto(pid):
        try:
            supabase.table("productos").delete().eq("id", pid).execute()
            refrescar()
            mostrar_snack("Producto eliminado")
        except Exception as ex:
            print("Error eliminando:", ex)

    def abrir_panel_vendedor(e=None):
        abrir_menu_perfil(
            page, usuario,
            ir_perfil=ir_perfil,
            ir_pedidos=lambda: cambiar_tab("pedidos"),
            ir_bienvenida=ir_bienvenida,
            on_create=lambda: mostrar_formulario(),
            modo="vendedor",
        )

    def stat_card(icono, titulo, valor, subtitulo, activo=False):
        return ft.Container(
            expand=True, height=126,
            bgcolor="white", border_radius=14,
            border=ft.border.all(2 if activo else 1, BRAND if activo else BORDER),
            padding=22,
            shadow=ft.BoxShadow(blur_radius=18, color="#0000000D",
                                offset=ft.Offset(0, 4)),
            content=ft.Row(
                spacing=18, vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=58, height=58, border_radius=10,
                        bgcolor=BRAND_LIGHT, alignment=ft.Alignment(0, 0),
                        content=ft.Text(icono, size=28, color=BRAND),
                    ),
                    ft.Column(spacing=4, controls=[
                        ft.Text(titulo, size=14, color=MUTED),
                        ft.Text(valor, size=28, weight=ft.FontWeight.BOLD,
                                color="#000000"),
                        ft.Container(
                            border_radius=8, border=ft.border.all(1, BRAND),
                            padding=ft.padding.symmetric(horizontal=10, vertical=3),
                            content=ft.Text(subtitulo, size=10, color=BRAND),
                        ),
                    ]),
                ],
            ),
        )

    def construir_tab(tab, texto):
        activo = tab_activo["v"] == tab
        ref = ft.Ref[ft.Container]()
        tab_refs[tab] = ref
        return ft.Container(
            ref=ref, border_radius=10,
            bgcolor=BRAND_LIGHT if activo else "white",
            border=ft.border.all(1, BRAND if activo else BORDER),
            padding=ft.padding.symmetric(horizontal=20, vertical=12),
            on_click=lambda _, t=tab: cambiar_tab(t),
            content=ft.Text(
                texto, size=15,
                color=BRAND if activo else TEXTO,
                weight=ft.FontWeight.BOLD if activo else ft.FontWeight.NORMAL,
            ),
        )

    def producto_card(p):
        precio = precio_float(p.get("precio", 0))
        stock = int(p.get("stock", 0) or 0)
        ventas = int(p.get("ventas", 0) or 0)
        img = p.get("img", "")

        return ft.Container(
            expand=True, height=200,
            bgcolor="white", border_radius=12,
            border=ft.border.all(1, BORDER),
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            shadow=ft.BoxShadow(blur_radius=10, color="#0000000D",
                                offset=ft.Offset(0, 3)),
            content=ft.Row(
                spacing=0,
                controls=[
                    ft.Container(
                        width=235, height=200,
                        bgcolor=p.get("color", "#C4A882"),
                        content=ft.Image(
                            src=img, fit="cover", width=235, height=200,
                            error_content=ft.Container(
                                bgcolor=p.get("color", "#C4A882"),
                                alignment=ft.Alignment(0, 0),
                                content=ft.Text("Imagen", color="white",
                                                weight=ft.FontWeight.BOLD),
                            ),
                        ),
                    ),
                    ft.Container(
                        expand=True, padding=18,
                        content=ft.Column(
                            spacing=9,
                            controls=[
                                ft.Text(
                                    p.get("nombre", "Producto"),
                                    size=18, weight=ft.FontWeight.BOLD,
                                    color=TEXTO, max_lines=1,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                                ft.Text(f"${precio:.2f}", size=20,
                                        color="#000000", weight=ft.FontWeight.BOLD),
                                ft.Row(spacing=18, controls=[
                                    ft.Text(f"Stock: {stock}", size=13, color=MUTED),
                                    ft.Text(f"Ventas: {ventas}", size=13, color=MUTED),
                                ]),
                                ft.Container(
                                    border_radius=16,
                                    bgcolor="#D8F8D2" if stock > 0 else "#FFDADA",
                                    padding=ft.padding.symmetric(horizontal=12, vertical=4),
                                    content=ft.Text(
                                        "Activo" if stock > 0 else "Agotado",
                                        size=11,
                                        color="#148C2E" if stock > 0 else "#B00020",
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                ),
                                ft.Container(expand=True),
                                ft.Row(spacing=10, controls=[
                                    ft.OutlinedButton(
                                        "Editar", height=34,
                                        style=ft.ButtonStyle(color=TEXTO),
                                        on_click=lambda _, prod=p: mostrar_formulario(prod),
                                    ),
                                    ft.OutlinedButton(
                                        "Eliminar", height=34,
                                        style=ft.ButtonStyle(color=BRAND),
                                        on_click=lambda _, pid=p.get("id"): eliminar_producto(pid),
                                    ),
                                ]),
                            ],
                        ),
                    ),
                ],
            ),
        )

    def vista_productos():
        lista = productos_filtrados()
        filas = []
        fila = []
        for i, producto in enumerate(lista):
            fila.append(producto_card(producto))
            if len(fila) == 2 or i == len(lista) - 1:
                if len(fila) == 1:
                    fila.append(ft.Container(expand=True))
                filas.append(ft.Row(spacing=20, controls=fila))
                fila = []

        if not filas:
            filas = [ft.Container(
                padding=60, alignment=ft.Alignment(0, 0),
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text("No tienes productos todavia", size=18, color=MUTED),
                        ft.Container(height=12),
                        ft.ElevatedButton(
                            "+ Nuevo producto", bgcolor=BRAND, color="white",
                            on_click=lambda _: mostrar_formulario(),
                        ),
                    ],
                )
            )]

        return ft.Column(
            expand=True, scroll=ft.ScrollMode.AUTO, spacing=18,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Column(spacing=4, controls=[
                            ft.Text("Mis productos", size=24,
                                    weight=ft.FontWeight.BOLD, color=TEXTO),
                            ft.Text("Administra inventario, imagenes y disponibilidad.",
                                    size=13, color=MUTED),
                        ]),
                        ft.ElevatedButton(
                            "+ Nuevo producto", bgcolor=BRAND, color="white",
                            height=44,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=10),
                                elevation=0),
                            on_click=lambda _: mostrar_formulario(),
                        ),
                    ],
                ),
                *filas,
                ft.Container(height=24),
            ],
        )

    def pedido_card(pedido):
        subtotal, cantidad = subtotal_vendedor(pedido)
        estado = (pedido.get("estado") or "pendiente").capitalize()
        datos_pago = pedido.get("datos_pago") or {}
        envio = float(datos_pago.get("envio") or 0)
        total = float(pedido.get("total") or (subtotal + envio))
        fecha = (pedido.get("created_at") or "")[:10] or "Sin fecha"
        productos_pedido = pedido.get("productos") or []

        def fila_producto(item):
            precio = precio_float(item.get("precio", 0))
            cantidad_item = int(item.get("cantidad", 1) or 1)
            subtotal_item = precio * cantidad_item
            return ft.Container(
                padding=ft.padding.symmetric(horizontal=12, vertical=9),
                border=ft.border.only(bottom=ft.BorderSide(1, "#EEEEEE")),
                content=ft.Row(controls=[
                    ft.Container(expand=3, content=ft.Text(
                        item.get("nombre", "Producto"), size=12, color=TEXTO)),
                    ft.Container(width=80, content=ft.Text(
                        str(cantidad_item), size=12, color=TEXTO,
                        text_align=ft.TextAlign.CENTER)),
                    ft.Container(width=100, content=ft.Text(
                        f"${precio:.2f}", size=12, color=TEXTO,
                        text_align=ft.TextAlign.RIGHT)),
                    ft.Container(width=110, content=ft.Text(
                        f"${subtotal_item:.2f}", size=12, color=BRAND,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.RIGHT)),
                ]),
            )

        return ft.Container(
            bgcolor="white", border_radius=14,
            border=ft.border.all(1, BORDER), padding=0,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            shadow=ft.BoxShadow(blur_radius=10, color="#0000000D",
                                offset=ft.Offset(0, 3)),
            content=ft.Column(spacing=0, controls=[
                ft.Container(
                    bgcolor=BRAND_LIGHT,
                    padding=ft.padding.symmetric(horizontal=18, vertical=14),
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Column(spacing=4, controls=[
                                ft.Text("Factura de pedido", size=16,
                                        color=TEXTO, weight=ft.FontWeight.BOLD),
                                ft.Text(pedido.get("comprador_nombre") or "Cliente",
                                        size=13, color=TEXTO),
                                ft.Text(pedido.get("direccion") or "Sin direccion",
                                        size=11, color=MUTED),
                            ]),
                            ft.Column(
                                horizontal_alignment=ft.CrossAxisAlignment.END,
                                spacing=4,
                                controls=[
                                    ft.Text(f"Fecha: {fecha}", size=11, color=MUTED),
                                    ft.Text(f"Metodo: {pedido.get('metodo_pago', '-')}",
                                            size=11, color=MUTED),
                                    ft.Container(
                                        border_radius=14,
                                        border=ft.border.all(1, BRAND),
                                        padding=ft.padding.symmetric(horizontal=10, vertical=3),
                                        content=ft.Text(estado, size=11, color=BRAND,
                                                        weight=ft.FontWeight.BOLD),
                                    ),
                                ]),
                        ],
                    ),
                ),
                ft.Container(
                    bgcolor="#F2F2F2",
                    padding=ft.padding.symmetric(horizontal=12, vertical=9),
                    content=ft.Row(controls=[
                        ft.Container(expand=3, content=ft.Text(
                            "Producto", size=11, weight=ft.FontWeight.BOLD, color=TEXTO)),
                        ft.Container(width=80, content=ft.Text(
                            "Cantidad", size=11, weight=ft.FontWeight.BOLD,
                            text_align=ft.TextAlign.CENTER)),
                        ft.Container(width=100, content=ft.Text(
                            "Precio", size=11, weight=ft.FontWeight.BOLD,
                            text_align=ft.TextAlign.RIGHT)),
                        ft.Container(width=110, content=ft.Text(
                            "Subtotal", size=11, weight=ft.FontWeight.BOLD,
                            text_align=ft.TextAlign.RIGHT)),
                    ]),
                ),
                ft.Column(spacing=0, controls=[
                    fila_producto(item) for item in productos_pedido
                ]),
                ft.Container(
                    padding=ft.padding.symmetric(horizontal=18, vertical=14),
                    content=ft.Column(spacing=8, controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text(f"Productos vendidos: {cantidad}",
                                        size=12, color=MUTED),
                                ft.Text(f"Subtotal: ${subtotal:.2f}",
                                        size=12, color=TEXTO, weight=ft.FontWeight.BOLD),
                            ]),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text("Envio", size=12, color=MUTED),
                                ft.Text(f"${envio:.2f}", size=12, color=BRAND,
                                        weight=ft.FontWeight.BOLD),
                            ]),
                        ft.Divider(height=8, color="#EEEEEE"),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text("Total pagado", size=15, color=TEXTO,
                                        weight=ft.FontWeight.BOLD),
                                ft.Text(f"${total:.2f}", size=18, color=BRAND,
                                        weight=ft.FontWeight.BOLD),
                            ]),
                    ]),
                ),
            ]),
        )

    def vista_pedidos():
        pedidos = cargar_pedidos()
        return ft.Column(
            expand=True, scroll=ft.ScrollMode.AUTO, spacing=14,
            controls=[
                ft.Text("Pedidos", size=24, weight=ft.FontWeight.BOLD, color=TEXTO),
                ft.Text("Seguimiento de ventas recibidas.", size=13, color=MUTED),
            ] + ([pedido_card(p) for p in pedidos] if pedidos else [
                ft.Container(padding=60, alignment=ft.Alignment(0, 0),
                             content=ft.Text("No hay pedidos todavia",
                                             color=MUTED, size=16))
            ]),
        )

    def vista_estadisticas():
        pedidos = cargar_pedidos()
        conteo = {}
        nombres = [p.get("nombre") for p in productos]
        for pedido in pedidos:
            for item in pedido.get("productos") or []:
                if item.get("nombre") in nombres:
                    conteo[item.get("nombre")] = (
                        conteo.get(item.get("nombre"), 0) +
                        int(item.get("cantidad", 1) or 1)
                    )
        ranking = sorted(conteo.items(), key=lambda x: x[1], reverse=True)[:6]
        return ft.Column(
            expand=True, scroll=ft.ScrollMode.AUTO, spacing=16,
            controls=[
                ft.Text("Estadisticas", size=24, weight=ft.FontWeight.BOLD, color=TEXTO),
                ft.Container(
                    bgcolor="white", border_radius=14,
                    border=ft.border.all(1, BORDER), padding=22,
                    content=ft.Column(
                        spacing=14,
                        controls=[
                            ft.Text("Productos mas vendidos", size=18,
                                    weight=ft.FontWeight.BOLD, color=TEXTO),
                        ] + ([
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Text(nombre, size=14, color=TEXTO),
                                    ft.Text(f"{cantidad} ventas", size=14,
                                            color=BRAND, weight=ft.FontWeight.BOLD),
                                ],
                            )
                            for nombre, cantidad in ranking
                        ] if ranking else [
                            ft.Text("No hay ventas registradas aun", color=MUTED)
                        ]),
                    ),
                ),
            ],
        )

    def cambiar_tab(tab):
        tab_activo["v"] = tab
        for t, ref in tab_refs.items():
            if ref.current:
                activo = t == tab
                ref.current.bgcolor = BRAND_LIGHT if activo else "white"
                ref.current.border = ft.border.all(1, BRAND if activo else BORDER)
                ref.current.content.color = BRAND if activo else TEXTO
                ref.current.content.weight = (ft.FontWeight.BOLD if activo
                                              else ft.FontWeight.NORMAL)
        if cuerpo_ref.current:
            if tab == "productos":
                cuerpo_ref.current.content = vista_productos()
            elif tab == "pedidos":
                cuerpo_ref.current.content = vista_pedidos()
            else:
                cuerpo_ref.current.content = vista_estadisticas()
        page.update()

    semana, reciente, total = calcular_stats()
    notis_count = len(cargar_notificaciones())

    header = ft.Container(
        height=96, clip_behavior=ft.ClipBehavior.HARD_EDGE,
        content=ft.Stack(controls=[
            ft.Container(
                alignment=ft.Alignment(0, -1),
                content=ft.Image(src="banner.png", fit="cover",
                                 width=float("inf"), height=96),
            ),
            ft.Container(bgcolor="#00000055", height=96),
            ft.Container(
                padding=ft.padding.symmetric(horizontal=28, vertical=18),
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Row(spacing=12, controls=[
                            craft_logo(44, on_click=abrir_panel_vendedor),
                            ft.Column(spacing=2, controls=[
                                ft.Text("CRAFTHUB", size=14, color="white",
                                        weight=ft.FontWeight.BOLD),
                                ft.Text("Panel vendedor", size=12, color="#F2F2F2"),
                            ]),
                        ]),
                        ft.Row(spacing=10, controls=[
                            ft.Container(
                                width=34, height=34, border_radius=17,
                                bgcolor="#FFFFFFDD", alignment=ft.Alignment(0, 0),
                                on_click=abrir_notificaciones,
                                content=ft.Stack(controls=[
                                    ft.Container(
                                        alignment=ft.Alignment(0, 0),
                                        content=ft.Text("🔔", size=18)
                                    ),
                                    ft.Container(
                                        width=14, height=14, border_radius=7,
                                        bgcolor=BRAND, alignment=ft.Alignment(1, -1),
                                        visible=notis_count > 0,
                                        content=ft.Text(str(notis_count), size=8,
                                                        color="white",
                                                        weight=ft.FontWeight.BOLD)
                                    )
                                ])
                            ),
                            ft.Container(
                                width=34, height=34, border_radius=17,
                                bgcolor="#FFFFFFDD", alignment=ft.Alignment(0, 0),
                                content=ft.Text("💬", color=BRAND,
                                                weight=ft.FontWeight.BOLD)
                            ),
                            ft.Container(
                                width=34, height=34, border_radius=17,
                                bgcolor="#FFFFFFDD", alignment=ft.Alignment(0, 0),
                                on_click=lambda _: ir_bienvenida(),
                                content=ft.Text("🚪", color=BRAND,
                                                weight=ft.FontWeight.BOLD)
                            ),
                        ]),
                    ],
                ),
            ),
        ]),
    )

    buscador = ft.Container(
        padding=ft.padding.symmetric(horizontal=28, vertical=16),
        content=ft.TextField(
            hint_text="Buscar producto...",
            height=42, border_radius=22,
            border_color="#D8D8D8", focused_border_color=BRAND,
            bgcolor="white",
            content_padding=ft.padding.symmetric(horizontal=18, vertical=9),
            on_change=lambda e: (
                busqueda.update({"v": e.control.value}),
                cambiar_tab(tab_activo["v"])
            ),
        ),
    )

    stats_row = ft.Container(
        padding=ft.padding.symmetric(horizontal=28, vertical=8),
        content=ft.Row(
            spacing=22,
            controls=[
                stat_card("/", "Esta semana", f"${semana:,.2f}", "+ ultimos 7 dias"),
                stat_card("$", "Reciente", f"${reciente:,.2f}", "Ultimas 24hr", activo=True),
                stat_card("#", "Total acumulado", f"${total:,.2f}", "Total de ventas"),
            ],
        ),
    )

    tabs = ft.Container(
        padding=ft.padding.symmetric(horizontal=28, vertical=14),
        content=ft.Row(
            spacing=10,
            controls=[
                construir_tab("productos", "Mis productos"),
                construir_tab("pedidos", "Pedidos"),
                construir_tab("estadisticas", "Estadisticas"),
            ],
        ),
    )

    page.add(
        ft.Column(
            expand=True, spacing=0,
            controls=[
                header, buscador, stats_row, tabs,
                ft.Container(
                    ref=cuerpo_ref,
                    expand=True, bgcolor=BG,
                    padding=ft.padding.symmetric(horizontal=28, vertical=10),
                    content=vista_productos(),
                ),
            ],
        )
    )
    page.update()