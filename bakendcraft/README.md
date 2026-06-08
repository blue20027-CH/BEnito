# bakendcraft

Modulos de backend separados por pantalla para CraftHub.

- home_backend.py: productos, favoritos y comentarios.
- vendedor_backend.py: productos del vendedor, pedidos, estadisticas, estados y notificaciones.
- pago_backend.py: resumen, envio, guardado de pedidos, stock y notificaciones.
- tracking_backend.py: pedidos para comprador/vendedor.
- notificaciones_backend.py: consultas de notificaciones por rol.
- auth_backend.py: login, registro, perfil y cierre de sesion.
- carrito_backend.py: calculos del carrito y envio.
- preferencias_backend.py: provincias/comarcas y categorias.
- calendario_backend.py: eventos.

Las pantallas actuales pueden ir importando estas funciones poco a poco para dejar solo UI en screens/.
