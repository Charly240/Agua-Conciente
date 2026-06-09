import flet as ft
from datetime import date, datetime
import threading
import time
import random
import asyncio


def mostrar_app(page: ft.Page, usuario_actual="Usuario"):
    page.clean()

    print("Usuario recibido en app.py:", usuario_actual)

    page.title = "AguaConsciente"
    page.bgcolor = ft.Colors.GREY_50
    page.padding = 0
    page.scroll = None

    page.horizontal_alignment = ft.CrossAxisAlignment.START
    page.vertical_alignment = ft.MainAxisAlignment.START

    def alto_ventana():
        try:
            if page.height:
                return max(720, page.height)
        except Exception:
            pass

        try:
            if page.window_height:
                return max(720, page.window_height)
        except Exception:
            pass

        try:
            if page.window.height:
                return max(720, page.window.height)
        except Exception:
            pass

        return 720

    #if isinstance(usuario_actual, dict):
        #nombre_usuario = usuario_actual.get("nombre", "Usuario")
    #else:
        #nombre_usuario = usuario_actual
    if isinstance(usuario_actual, dict):
        id_usuario_actual = usuario_actual.get("id_usuario")
        nombre_usuario = usuario_actual.get("nombre", "Usuario")
        correo_usuario = usuario_actual.get("correo", "")

    else:
        id_usuario_actual = None
        nombre_usuario = usuario_actual
        correo_usuario = ""

    print("ID usuario actual:", id_usuario_actual)
    print("Nombre usuario actual:", nombre_usuario)
    print("Correo usuario actual:", correo_usuario)

    opciones_frecuencia = {
        "1 vez al día": 24 * 60 * 60,
        "2 veces al día": 12 * 60 * 60,
        "3 veces al día": 8 * 60 * 60,
    }

    estado = {
        "vista": "inicio",
        "habitos_seleccionados": set(),
        "habitos_configuracion": set(),
        "habitos_registro": [],
        "modo_registro": "auto",
        "registros": [],
        "notificaciones": [],
        "recordatorios_activos": True,
        "hilo_iniciado": False,

        "frecuencia_recordatorios": "2 veces al día",
        "intervalo_recordatorios": 12 * 60 * 60,
        "ultimo_recordatorio": time.time(),

        "ultimo_ancho": None,
        "ultimo_modo_movil": None,
    }

    try:
        from database import obtener_configuracion_recordatorio

        config_recordatorio = obtener_configuracion_recordatorio(id_usuario_actual)

        if config_recordatorio:
            estado["recordatorios_activos"] = config_recordatorio.get(
                "recordatorios_activos",
                True
            )

            estado["frecuencia_recordatorios"] = config_recordatorio.get(
                "frecuencia",
                "2 veces al día"
            )

            estado["intervalo_recordatorios"] = int(
                config_recordatorio.get("intervalo_horas", 12)
            ) * 60 * 60

            print("Configuración cargada desde Supabase:", config_recordatorio)

    except Exception as error:
        print("Error al cargar configuración de recordatorio:", error)


    dropdown_frecuencia_ref = {"control": None}

    recordatorios = [
        {
            "titulo": "Cierra la llave",
            "mensaje": "¿Ya cerraste la llave mientras te enjabonabas las manos?",
            "icono": ft.Icons.WATER_DROP,
        },
        {
            "titulo": "Cepillado responsable",
            "mensaje": "Recuerda cerrar la llave mientras te cepillas los dientes.",
            "icono": ft.Icons.WATER_DROP,
        },
        {
            "titulo": "Baño corto",
            "mensaje": "Reto del día: reduce tu tiempo de baño y ahorra agua.",
            "icono": ft.Icons.TIMER,
        },
        {
            "titulo": "Revisa fugas",
            "mensaje": "Una fuga pequeña puede desperdiciar muchos litros. Revisa tus llaves.",
            "icono": ft.Icons.BUILD,
        },
        {
            "titulo": "Evita la manguera",
            "mensaje": "Usa cubeta en lugar de manguera para lavar patios o autos.",
            "icono": ft.Icons.WATER_DROP,
        },
        {
            "titulo": "Carga completa",
            "mensaje": "Usa la lavadora con carga completa para aprovechar mejor el agua.",
            "icono": ft.Icons.CHECK_CIRCLE,
        },
    ]

    recomendaciones = [
        {
            "titulo": "Cierra la llave",
            "descripcion": "Cierra la llave mientras te cepillas los dientes o te enjabonas las manos.",
            "icono": ft.Icons.WATER_DROP,
        },
        {
            "titulo": "Baños más cortos",
            "descripcion": "Reducir el tiempo de baño ayuda a ahorrar muchos litros de agua al día.",
            "icono": ft.Icons.TIMER,
        },
        {
            "titulo": "Prevención de fugas",
            "descripcion": "Revisa llaves, tuberías y sanitarios para detectar fugas a tiempo.",
            "icono": ft.Icons.BUILD,
        },
        {
            "titulo": "Reutiliza agua",
            "descripcion": "El agua de lavar verduras puede reutilizarse para plantas o limpieza.",
            "icono": ft.Icons.RECYCLING,
        },
        {
            "titulo": "Evita desperdicio",
            "descripcion": "Usa cubeta en lugar de manguera para lavar patios, banquetas o autos.",
            "icono": ft.Icons.WATER_DROP,
        },
        {
            "titulo": "Carga completa",
            "descripcion": "Usa lavadora solo con carga completa para aprovechar mejor el agua.",
            "icono": ft.Icons.CHECK_CIRCLE,
        },
    ]

    def ancho_pantalla():
        try:
            if page.width:
                return page.width
        except Exception:
            pass

        try:
            if page.window_width:
                return page.window_width
        except Exception:
            pass

        try:
            if page.window.width:
                return page.window.width
        except Exception:
            pass

        return 1200


    def es_movil():
        return ancho_pantalla() < 1000
    
    def ancho_movil():
        ancho = ancho_pantalla()
        return max(ancho - 64, 300)


    def ancho_tarjeta_movil():
        return ancho_movil() if es_movil() else 220
    
    def cargar_habitos():
        try:
            from database import obtener_habitos

            datos = obtener_habitos()

            if datos:
                print("Hábitos cargados:", datos)
                return datos

        except Exception as error:
            print("Error al cargar hábitos:", error)

        return [
            {"id_habito": 1, "nombre_habito": "Cerrar la llave al cepillarse los dientes"},
            {"id_habito": 2, "nombre_habito": "Reducir el tiempo de baño"},
            {"id_habito": 3, "nombre_habito": "Revisar fugas"},
            {"id_habito": 4, "nombre_habito": "Reutilizar agua"},
            {"id_habito": 5, "nombre_habito": "Evitar usar manguera"},
            {"id_habito": 6, "nombre_habito": "Usar lavadora con carga completa"},
        ]


    habitos =cargar_habitos()
    
    def alto_menu():
        try:
            return max(720, page.window_height or 720)
        except Exception:
            return 720

    contenido = ft.Container(
        expand=True,
        padding=30,
        bgcolor=ft.Colors.GREY_50,
    )

    menu_lateral = ft.Container(
        width=235,
        height=alto_ventana(),
        bgcolor=ft.Colors.BLUE_700,
        padding=ft.Padding(left=18, right=18, top=25, bottom=25),
    )

    def texto_titulo(texto):
        return ft.Text(
            texto,
            size=30,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.BLUE_GREY_900,
        )

    def texto_subtitulo(texto):
        return ft.Text(
            texto,
            size=14,
            color=ft.Colors.BLUE_GREY_600,
        )

    def tarjeta(content, expand=False, width=None, height=None, padding=22, color=ft.Colors.WHITE):
        return ft.Container(
            content=content,
            expand=expand,
            width=width,
            height=height,
            padding=padding,
            bgcolor=color,
            border_radius=14,
            shadow=ft.BoxShadow(
                blur_radius=10,
                spread_radius=1,
                color=ft.Colors.BLUE_GREY_100,
            ),
        )

    def boton_principal(texto, icono, funcion, ancho=230):
        return ft.Button(
            content=texto,
            icon=icono,
            width=ancho,
            height=45,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.BLUE_600,
                color=ft.Colors.WHITE,
                shape=ft.RoundedRectangleBorder(radius=8),
            ),
            on_click=funcion,
        )

    def enviar_notificacion(titulo, mensaje, icono=ft.Icons.NOTIFICATIONS):
        hora = datetime.now().strftime("%H:%M")

        estado["notificaciones"].insert(
            0,
            {
                "titulo": titulo,
                "mensaje": mensaje,
                "hora": hora,
                "icono": icono,
            },
        )

        page.snack_bar = ft.SnackBar(
            bgcolor=ft.Colors.BLUE_700,
            content=ft.Row(
                controls=[
                    ft.Icon(icono, color=ft.Colors.WHITE),
                    ft.Column(
                        controls=[
                            ft.Text(
                                titulo,
                                color=ft.Colors.WHITE,
                                weight=ft.FontWeight.BOLD,
                                size=14,
                            ),
                            ft.Text(
                                mensaje,
                                color=ft.Colors.WHITE,
                                size=13,
                            ),
                        ],
                        spacing=2,
                    ),
                ],
                spacing=10,
            ),
        )

        page.snack_bar.open = True
        page.update()

    def mensaje(texto):
        enviar_notificacion("AguaConsciente", texto, ft.Icons.WATER_DROP)


    def iniciar_recordatorios():
        if estado["hilo_iniciado"]:
            return

        estado["hilo_iniciado"] = True

        def ciclo():
            while True:
                time.sleep(5)

                if estado["recordatorios_activos"]:
                    ahora = time.time()
                    intervalo = estado["intervalo_recordatorios"]

                    if ahora - estado["ultimo_recordatorio"] >= intervalo:
                        r = random.choice(recordatorios)

                        try:
                            enviar_notificacion(
                                r["titulo"],
                                r["mensaje"],
                                r["icono"],
                            )

                            estado["ultimo_recordatorio"] = ahora

                        except Exception as error:
                            print("Error en recordatorio automático:", error)

        hilo = threading.Thread(target=ciclo, daemon=True)
        hilo.start()

    def probar_notificacion(e=None):
        r = random.choice(recordatorios)

        enviar_notificacion(
            r["titulo"],
            r["mensaje"],
            r["icono"],
        )

        try:
            from database import programar_correo_prueba

            exito, respuesta = programar_correo_prueba(id_usuario_actual)
            print(respuesta)

            enviar_notificacion(
                "Correo de prueba programado",
                "El correo llegará cuando Supabase Cron ejecute la revisión.",
                ft.Icons.EMAIL,
            )

        except Exception as error:
            print("Error al programar correo de prueba:", error)
            enviar_notificacion(
                "Error al programar correo",
                "No se pudo programar el correo de prueba.",
                ft.Icons.ERROR,
            )

        if estado["vista"] == "seguimiento":
            vista_seguimiento()
            page.update()

    def cambiar_recordatorios(e):
        estado["recordatorios_activos"] = e.control.value

        dropdown = dropdown_frecuencia_ref.get("control")

        if dropdown is not None and dropdown.value:
            frecuencia_actual = dropdown.value
        else:
            frecuencia_actual = estado.get("frecuencia_recordatorios", "2 veces al día")

        if frecuencia_actual not in opciones_frecuencia:
            frecuencia_actual = "2 veces al día"

        intervalo_actual = opciones_frecuencia[frecuencia_actual]

        estado["frecuencia_recordatorios"] = frecuencia_actual
        estado["intervalo_recordatorios"] = intervalo_actual

        print("SWITCH - frecuencia guardada:", frecuencia_actual)
        print("SWITCH - intervalo guardado:", int(intervalo_actual / 3600))

        try:
            from database import guardar_configuracion_recordatorio

            exito, respuesta = guardar_configuracion_recordatorio(
                id_usuario_actual,
                correo_usuario,
                estado["recordatorios_activos"],
                frecuencia_actual,
                int(intervalo_actual / 3600),
            )

            print(respuesta)

        except Exception as error:
            print("Error al guardar recordatorio en Supabase:", error)

        if estado["recordatorios_activos"]:
            enviar_notificacion(
                "Recordatorios activados",
                "Te enviaremos avisos para seguir cuidando el agua.",
                ft.Icons.NOTIFICATIONS_ACTIVE,
            )
        else:
            enviar_notificacion(
                "Recordatorios desactivados",
                "Puedes volver a activarlos desde Seguimiento.",
                ft.Icons.NOTIFICATIONS_OFF,
            )

        cambiar_vista(estado["vista"])

    def cambiar_frecuencia_recordatorios(e):
        frecuencia = e.control.value

        if frecuencia not in opciones_frecuencia:
            frecuencia = "2 veces al día"

        estado["frecuencia_recordatorios"] = frecuencia
        estado["intervalo_recordatorios"] = opciones_frecuencia[frecuencia]
        estado["ultimo_recordatorio"] = time.time()

        print("DROPDOWN - frecuencia seleccionada:", frecuencia)
        print("DROPDOWN - intervalo:", int(estado["intervalo_recordatorios"] / 3600))

        try:
            from database import guardar_configuracion_recordatorio

            exito, respuesta = guardar_configuracion_recordatorio(
                id_usuario_actual,
                correo_usuario,
                estado["recordatorios_activos"],
                estado["frecuencia_recordatorios"],
                int(estado["intervalo_recordatorios"] / 3600),
            )

            print(respuesta)

        except Exception as error:
            print("Error al guardar frecuencia en Supabase:", error)

        enviar_notificacion(
            "Frecuencia actualizada",
            f"Los recordatorios por correo se enviarán: {frecuencia}.",
            ft.Icons.SCHEDULE,
        )

        cambiar_vista(estado["vista"])

    def menu_frecuencia_recordatorios():
        dropdown = ft.Dropdown(
            label="Frecuencia de recordatorios",
            value=estado["frecuencia_recordatorios"],
            width=260,
            border_radius=10,
            border_color=ft.Colors.BLUE_GREY_200,
            focused_border_color=ft.Colors.BLUE_600,
            color=ft.Colors.BLUE_GREY_900,
            options=[
                ft.dropdown.Option(opcion)
                for opcion in opciones_frecuencia.keys()
            ],
        )

        dropdown.on_change = cambiar_frecuencia_recordatorios

        dropdown_frecuencia_ref["control"] = dropdown

        return dropdown

    def obtener_estadisticas():
        try:
            from database import obtener_estadisticas_usuario

            estadisticas = obtener_estadisticas_usuario(id_usuario_actual)

            return {
                "dias": estadisticas["dias_registrados"],
                "cumplidos": estadisticas["habitos_cumplidos"],
            }

        except Exception as error:
            print("Error al cargar estadísticas desde Supabase:", error)

            return {
                "dias": 0,
                "cumplidos": 0,
            }

    def item_menu(texto, icono, vista):
        seleccionado = estado["vista"] == vista

        return ft.Container(
            padding=ft.Padding(left=14, right=14, top=12, bottom=12),
            border_radius=10,
            bgcolor=ft.Colors.WHITE if seleccionado else ft.Colors.BLUE_700,
            on_click=lambda e: cambiar_vista(vista),
            content=ft.Row(
                controls=[
                    ft.Icon(
                        icono,
                        size=20,
                        color=ft.Colors.BLUE_700 if seleccionado else ft.Colors.WHITE,
                    ),
                    ft.Text(
                        texto,
                        size=14,
                        weight=ft.FontWeight.BOLD if seleccionado else ft.FontWeight.NORMAL,
                        color=ft.Colors.BLUE_700 if seleccionado else ft.Colors.WHITE,
                    ),
                ],
                spacing=12,
            ),
        )

    def construir_menu():
        opciones_menu = ft.Column(
            controls=[
                ft.Icon(
                    ft.Icons.WATER_DROP,
                    size=32,
                    color=ft.Colors.WHITE,
                ),
                ft.Text(
                    "AguaConsciente",
                    size=22,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE,
                ),
                ft.Text(
                    "Monitoreo comunitario",
                    size=12,
                    color=ft.Colors.BLUE_100,
                ),
                ft.Container(height=25),

                item_menu("Inicio", ft.Icons.HOME, "inicio"),
                item_menu("Registro de hábitos", ft.Icons.LIST_ALT, "registro"),
                item_menu("Seguimiento", ft.Icons.SHOW_CHART, "seguimiento"),
                item_menu("Historial", ft.Icons.CALENDAR_MONTH, "historial"),
                item_menu("Recomendaciones", ft.Icons.LIGHTBULB, "recomendaciones"),
            ],
            spacing=8,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )

        boton_salir = ft.Container(
            padding=ft.Padding(left=14, right=14, top=12, bottom=12),
            border_radius=10,
            bgcolor=ft.Colors.BLUE_800,
            on_click=lambda e: cerrar_sesion(),
            content=ft.Row(
                controls=[
                    ft.Icon(
                        ft.Icons.LOGOUT,
                        size=20,
                        color=ft.Colors.WHITE,
                    ),
                    ft.Text(
                        "Cerrar sesión",
                        size=14,
                        color=ft.Colors.WHITE,
                    ),
                ],
                spacing=12,
            ),
        )

        return ft.Column(
            controls=[
                opciones_menu,
                boton_salir,
            ],
            expand=True,
            spacing=12,
        )

    def tarjeta_inicio(nombre, descripcion, icono, vista, color):
        if es_movil():
            return ft.Container(
                width=ancho_movil(),
                on_click=lambda e: cambiar_vista(vista),
                content=tarjeta(
                    height=None,
                    content=ft.Row(
                        controls=[
                            ft.Container(
                                width=58,
                                height=58,
                                border_radius=14,
                                bgcolor=color,
                                alignment=ft.Alignment(0, 0),
                                content=ft.Icon(
                                    icono,
                                    color=ft.Colors.WHITE,
                                    size=30,
                                ),
                            ),
                            ft.Column(
                                controls=[
                                    ft.Text(
                                        nombre,
                                        size=18,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.BLUE_GREY_900,
                                    ),
                                    ft.Text(
                                        descripcion,
                                        size=13,
                                        color=ft.Colors.BLUE_GREY_700,
                                    ),
                                ],
                                spacing=6,
                                expand=True,
                            ),
                        ],
                        spacing=14,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ),
            )

        return ft.Container(
            expand=True,
            on_click=lambda e: cambiar_vista(vista),
            content=tarjeta(
                height=145,
                content=ft.Column(
                    controls=[
                        ft.Container(
                            width=46,
                            height=46,
                            border_radius=10,
                            bgcolor=color,
                            content=ft.Icon(
                                icono,
                                color=ft.Colors.WHITE,
                                size=25,
                            ),
                        ),
                        ft.Text(
                            nombre,
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.BLUE_GREY_900,
                        ),
                        ft.Text(
                            descripcion,
                            size=13,
                            color=ft.Colors.BLUE_GREY_700,
                        ),
                    ],
                    spacing=10,
                ),
            ),
        )

    def banner_inicio():
        return ft.Container(
            width=ancho_movil() if es_movil() else None,
            padding=ft.Padding(
                left=24 if es_movil() else 30,
                right=24 if es_movil() else 30,
                top=28 if es_movil() else 30,
                bottom=28 if es_movil() else 30,
            ),
            border_radius=22,
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, 0),
                end=ft.Alignment(1, 0),
                colors=[
                    ft.Colors.BLUE_600,
                    ft.Colors.CYAN_400,
                ],
            ),
            content=(
                ft.Column(
                    controls=[
                        ft.Icon(
                            ft.Icons.WATER_DROP,
                            color=ft.Colors.WHITE,
                            size=52,
                        ),
                        ft.Text(
                            "AguaConsciente",
                            size=28,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE,
                        ),
                        ft.Text(
                            "Aplicación comunitaria para monitorear hábitos de ahorro de agua.",
                            size=14,
                            color=ft.Colors.BLUE_50,
                        ),
                        ft.Text(
                            "Este proyecto ayuda a registrar hábitos, consultar avances y revisar recomendaciones para cuidar el agua en la comunidad.",
                            size=14,
                            color=ft.Colors.BLUE_50,
                        ),
                    ],
                    spacing=12,
                )
                if es_movil()
                else ft.Row(
                    controls=[
                        ft.Icon(
                            ft.Icons.WATER_DROP,
                            color=ft.Colors.WHITE,
                            size=58,
                        ),
                        ft.Column(
                            controls=[
                                ft.Text(
                                    "AguaConsciente",
                                    size=32,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.WHITE,
                                ),
                                ft.Text(
                                    "Aplicación comunitaria para monitorear hábitos de ahorro de agua.",
                                    size=16,
                                    color=ft.Colors.BLUE_50,
                                ),
                                ft.Text(
                                    "Este proyecto ayuda a registrar hábitos, consultar avances y revisar recomendaciones para cuidar el agua en la comunidad.",
                                    size=15,
                                    color=ft.Colors.BLUE_50,
                                ),
                            ],
                            spacing=10,
                            expand=True,
                        ),
                    ],
                    spacing=20,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                )
            ),
        )


    def tarjeta_recordatorio_inicio():
        if es_movil():
            return tarjeta(
                width=ancho_movil(),
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Icon(
                                    ft.Icons.NOTIFICATIONS_ACTIVE
                                    if estado["recordatorios_activos"]
                                    else ft.Icons.NOTIFICATIONS_OFF,
                                    color=ft.Colors.BLUE_500
                                    if estado["recordatorios_activos"]
                                    else ft.Colors.BLUE_GREY_400,
                                    size=28,
                                ),
                                ft.Text(
                                    "Recordatorios de hábitos",
                                    size=18,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.BLUE_GREY_900,
                                    expand=True,
                                ),
                            ],
                            spacing=10,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        ft.Text(
                            "Activa los avisos para mantener tus hábitos de ahorro de agua.",
                            size=13,
                            color=ft.Colors.BLUE_GREY_600,
                        ),
                        ft.Switch(
                            label="Activos",
                            value=estado["recordatorios_activos"],
                            on_change=cambiar_recordatorios,
                        ),
                    ],
                    spacing=12,
                ),
            )

        return tarjeta(
            content=ft.Row(
                controls=[
                    ft.Icon(
                        ft.Icons.NOTIFICATIONS_ACTIVE
                        if estado["recordatorios_activos"]
                        else ft.Icons.NOTIFICATIONS_OFF,
                        color=ft.Colors.BLUE_500
                        if estado["recordatorios_activos"]
                        else ft.Colors.BLUE_GREY_400,
                        size=28,
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(
                                "Recordatorios de hábitos",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.BLUE_GREY_900,
                            ),
                            ft.Text(
                                "Activa los avisos para mantener tus hábitos de ahorro de agua.",
                                size=13,
                                color=ft.Colors.BLUE_GREY_600,
                            ),
                        ],
                        expand=True,
                        spacing=4,
                    ),
                    ft.Switch(
                        label="Activos",
                        value=estado["recordatorios_activos"],
                        on_change=cambiar_recordatorios,
                    ),
                ],
                spacing=14,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )


    def vista_inicio():
        ancho_card = ancho_movil() if es_movil() else None

        banner = ft.Container(
            width=ancho_card,
            padding=ft.Padding(
                left=24 if es_movil() else 30,
                right=24 if es_movil() else 30,
                top=28 if es_movil() else 30,
                bottom=28 if es_movil() else 30,
            ),
            border_radius=22,
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, 0),
                end=ft.Alignment(1, 0),
                colors=[
                    ft.Colors.BLUE_600,
                    ft.Colors.CYAN_400,
                ],
            ),
            shadow=ft.BoxShadow(
                blur_radius=10,
                spread_radius=1,
                color=ft.Colors.BLUE_GREY_200,
            ),
            content=(
                ft.Column(
                    controls=[
                        ft.Icon(
                            ft.Icons.WATER_DROP,
                            color=ft.Colors.WHITE,
                            size=52,
                        ),
                        ft.Text(
                            "AguaConsciente",
                            size=28,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE,
                        ),
                        ft.Text(
                            "Aplicación comunitaria para monitorear hábitos de ahorro de agua.",
                            size=14,
                            color=ft.Colors.BLUE_50,
                        ),
                        ft.Text(
                            "Este proyecto ayuda a registrar hábitos, consultar avances y revisar recomendaciones para cuidar el agua en la comunidad.",
                            size=14,
                            color=ft.Colors.BLUE_50,
                        ),
                    ],
                    spacing=12,
                )
                if es_movil()
                else ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Icon(
                                    ft.Icons.WATER_DROP,
                                    color=ft.Colors.WHITE,
                                    size=46,
                                ),
                                ft.Column(
                                    controls=[
                                        ft.Text(
                                            "AguaConsciente",
                                            size=34,
                                            weight=ft.FontWeight.BOLD,
                                            color=ft.Colors.WHITE,
                                        ),
                                        ft.Text(
                                            "Aplicación comunitaria para monitorear hábitos de ahorro de agua.",
                                            size=15,
                                            color=ft.Colors.BLUE_50,
                                        ),
                                    ],
                                    spacing=4,
                                    expand=True,
                                ),
                            ],
                            spacing=18,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        ft.Text(
                            "Este proyecto ayuda a registrar hábitos, consultar avances y revisar recomendaciones para cuidar el agua en la comunidad.",
                            size=14,
                            color=ft.Colors.BLUE_50,
                        ),
                    ],
                    spacing=18,
                )
            ),
        )

        tarjetas_inicio = (
            ft.Column(
                controls=[
                    tarjeta_inicio(
                        "Registro de hábitos",
                        "Marca los hábitos que cumpliste hoy.",
                        ft.Icons.LIST_ALT,
                        "registro",
                        ft.Colors.BLUE_500,
                    ),
                    tarjeta_inicio(
                        "Historial",
                        "Consulta registros anteriores.",
                        ft.Icons.CALENDAR_MONTH,
                        "historial",
                        ft.Colors.LIGHT_BLUE_500,
                    ),
                    tarjeta_inicio(
                        "Recomendaciones",
                        "Consejos para ahorrar agua.",
                        ft.Icons.LIGHTBULB,
                        "recomendaciones",
                        ft.Colors.CYAN_600,
                    ),
                ],
                spacing=16,
            )
            if es_movil()
            else ft.Row(
                controls=[
                    tarjeta_inicio(
                        "Registro de hábitos",
                        "Marca los hábitos que cumpliste hoy.",
                        ft.Icons.LIST_ALT,
                        "registro",
                        ft.Colors.BLUE_500,
                    ),
                    tarjeta_inicio(
                        "Historial",
                        "Consulta registros anteriores.",
                        ft.Icons.CALENDAR_MONTH,
                        "historial",
                        ft.Colors.LIGHT_BLUE_500,
                    ),
                    tarjeta_inicio(
                        "Recomendaciones",
                        "Consejos para ahorrar agua.",
                        ft.Icons.LIGHTBULB,
                        "recomendaciones",
                        ft.Colors.CYAN_600,
                    ),
                ],
                spacing=20,
            )
        )

        tarjeta_recordatorios = (
            tarjeta(
                width=ancho_card,
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Icon(
                                    ft.Icons.NOTIFICATIONS_ACTIVE
                                    if estado["recordatorios_activos"]
                                    else ft.Icons.NOTIFICATIONS_OFF,
                                    color=ft.Colors.BLUE_600
                                    if estado["recordatorios_activos"]
                                    else ft.Colors.BLUE_GREY_400,
                                    size=28,
                                ),
                                ft.Text(
                                    "Recordatorios de hábitos",
                                    size=18,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.BLUE_GREY_900,
                                    expand=True,
                                ),
                            ],
                            spacing=10,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        ft.Text(
                            "Activa o desactiva los avisos para mantener tus hábitos de ahorro de agua.",
                            size=13,
                            color=ft.Colors.BLUE_GREY_700,
                        ),
                        ft.Row(
                            controls=[
                                ft.Switch(
                                    label="Activos" if estado["recordatorios_activos"] else "Inactivos",
                                    value=estado["recordatorios_activos"],
                                    on_change=cambiar_recordatorios,
                                ),
                                ft.Button(
                                    content="Probar notificación",
                                    icon=ft.Icons.NOTIFICATIONS,
                                    on_click=probar_notificacion,
                                ),
                            ],
                            spacing=10,
                            wrap=True,
                        ),
                    ],
                    spacing=12,
                ),
            )
            if es_movil()
            else tarjeta(
                content=ft.Row(
                    controls=[
                        ft.Icon(
                            ft.Icons.NOTIFICATIONS_ACTIVE
                            if estado["recordatorios_activos"]
                            else ft.Icons.NOTIFICATIONS_OFF,
                            color=ft.Colors.BLUE_600
                            if estado["recordatorios_activos"]
                            else ft.Colors.BLUE_GREY_400,
                            size=32,
                        ),
                        ft.Column(
                            controls=[
                                ft.Text(
                                    "Recordatorios de hábitos",
                                    size=18,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.BLUE_GREY_900,
                                ),
                                ft.Text(
                                    "Activa o desactiva los avisos para mantener tus hábitos de ahorro de agua.",
                                    size=13,
                                    color=ft.Colors.BLUE_GREY_700,
                                ),
                            ],
                            spacing=4,
                            expand=True,
                        ),
                        ft.Switch(
                            value=estado["recordatorios_activos"],
                            on_change=cambiar_recordatorios,
                        ),
                        ft.Text(
                            "Activos" if estado["recordatorios_activos"] else "Inactivos",
                            size=13,
                            color=ft.Colors.BLUE_GREY_500,
                        ),
                        ft.Button(
                            content="Probar notificación",
                            icon=ft.Icons.NOTIFICATIONS,
                            on_click=probar_notificacion,
                        ),
                    ],
                    spacing=15,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            )
        )

        contenido.content = ft.Column(
            controls=[
                banner,

                ft.Text(
                    f"Hola, {nombre_usuario}",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_GREY_800,
                ),

                ft.Text(
                    "Inicio",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_GREY_900,
                ),

                tarjetas_inicio,

                tarjeta_recordatorios,
            ],
            spacing=22,
            scroll=ft.ScrollMode.AUTO,
        )

        page.update()

    def fila_habito(indice, nombre_habito):
        seleccionado = indice in estado["habitos_seleccionados"]

        return ft.Container(
            padding=ft.Padding(left=16, right=16, top=14, bottom=14),
            border_radius=10,
            bgcolor=ft.Colors.BLUE_50 if seleccionado else ft.Colors.WHITE,
            on_click=lambda e: seleccionar_habito(indice),
            content=ft.Row(
                controls=[
                    ft.Icon(
                        ft.Icons.CHECK_CIRCLE
                        if seleccionado
                        else ft.Icons.RADIO_BUTTON_UNCHECKED,
                        color=ft.Colors.BLUE_600
                        if seleccionado
                        else ft.Colors.BLUE_GREY_300,
                        size=24,
                    ),
                    ft.Text(
                        nombre_habito,
                        size=15,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_GREY_800,
                    ),
                ],
                spacing=14,
            ),
        )

    def seleccionar_habito(indice):
        if indice in estado["habitos_seleccionados"]:
            estado["habitos_seleccionados"].remove(indice)
        else:
            estado["habitos_seleccionados"].add(indice)

        vista_registro()
        page.update()

    def guardar_registro(e):
        if id_usuario_actual is None:
            mensaje("No se encontró el usuario logueado. Vuelve a iniciar sesión.")
            return

        if len(estado["habitos_seleccionados"]) == 0:
            mensaje("Selecciona al menos un hábito antes de guardar.")
            return

        mis_habitos = estado["habitos_registro"]

        ids_habitos = [
            mis_habitos[i]["id_habito"]
            for i in sorted(estado["habitos_seleccionados"])
        ]

        nombres_habitos = [
            mis_habitos[i]["nombre_habito"]
            for i in sorted(estado["habitos_seleccionados"])
        ]

        print("Guardando para usuario:", id_usuario_actual)
        print("Hábitos seleccionados:", ids_habitos)

        try:
            from database import guardar_registro_habitos

            exito, respuesta = guardar_registro_habitos(
                id_usuario_actual,
                ids_habitos
            )

            if not exito:
                mensaje(respuesta)
                return

        except Exception as error:
            mensaje(f"Error al guardar en la base de datos: {error}")
            print("Error al guardar en BD:", error)
            return

        registro_local = {
            "fecha": date.today().strftime("%d/%m/%Y"),
            "hora": datetime.now().strftime("%H:%M"),
            "habitos": nombres_habitos,
        }

        estado["registros"].append(registro_local)
        estado["habitos_seleccionados"].clear()

        enviar_notificacion(
            "Registro guardado",
            "Tus hábitos fueron guardados correctamente.",
            ft.Icons.CHECK_CIRCLE,
        )

        vista_registro()
        page.update()

    def obtener_mis_habitos():
        try:
            from database import obtener_habitos_usuario

            if id_usuario_actual is None:
                return []

            return obtener_habitos_usuario(id_usuario_actual)

        except Exception as error:
            print("Error al obtener mis hábitos:", error)
            return []


    def guardar_configuracion_habitos(e):
        if id_usuario_actual is None:
            mensaje("No se encontró el usuario logueado.")
            return

        if len(estado["habitos_configuracion"]) == 0:
            mensaje("Selecciona al menos un hábito para monitorear.")
            return

        ids_habitos = [
            habitos[i]["id_habito"]
            for i in sorted(estado["habitos_configuracion"])
        ]

        try:
            from database import guardar_habitos_usuario

            exito, respuesta = guardar_habitos_usuario(
                id_usuario_actual,
                ids_habitos
            )

            if not exito:
                mensaje(respuesta)
                return

        except Exception as error:
            mensaje(f"Error al guardar configuración: {error}")
            print("Error al guardar configuración:", error)
            return

        estado["modo_registro"] = "registrar"
        estado["habitos_configuracion"].clear()
        estado["habitos_seleccionados"].clear()

        enviar_notificacion(
            "Hábitos configurados",
            "Ahora puedes registrar tus hábitos cumplidos.",
            ft.Icons.CHECK_CIRCLE,
        )

        vista_registro()
        page.update()


    def cambiar_a_configuracion(e=None):
        estado["modo_registro"] = "configurar"
        estado["habitos_configuracion"].clear()
        estado["habitos_seleccionados"].clear()

        mis_habitos = obtener_mis_habitos()
        ids_mis_habitos = [
            int(h["id_habito"])
            for h in mis_habitos
        ]

        for i, h in enumerate(habitos):
            if int(h["id_habito"]) in ids_mis_habitos:
                estado["habitos_configuracion"].add(i)

        vista_registro()
        page.update()


    def volver_a_registro(e=None):
        estado["modo_registro"] = "registrar"
        estado["habitos_configuracion"].clear()
        estado["habitos_seleccionados"].clear()

        vista_registro()
        page.update()

    def fila_habito_configuracion(indice, nombre_habito):
        seleccionado = indice in estado["habitos_configuracion"]

        def seleccionar(e):
            if indice in estado["habitos_configuracion"]:
                estado["habitos_configuracion"].remove(indice)
            else:
                estado["habitos_configuracion"].add(indice)

            vista_registro()
            page.update()

        return ft.Container(
            padding=ft.Padding(left=16, right=16, top=14, bottom=14),
            border_radius=10,
            bgcolor=ft.Colors.BLUE_50 if seleccionado else ft.Colors.WHITE,
            on_click=seleccionar,
            content=ft.Row(
                controls=[
                    ft.Icon(
                        ft.Icons.CHECK_CIRCLE if seleccionado else ft.Icons.RADIO_BUTTON_UNCHECKED,
                        color=ft.Colors.BLUE_600 if seleccionado else ft.Colors.BLUE_GREY_300,
                        size=24,
                    ),
                    ft.Text(
                        nombre_habito,
                        size=15,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_GREY_900,
                    ),
                ],
                spacing=15,
            ),
        )
        
    def vista_registro():
        mis_habitos = obtener_mis_habitos()

        if estado["modo_registro"] == "auto":
            if len(mis_habitos) == 0:
                estado["modo_registro"] = "configurar"
            else:
                estado["modo_registro"] = "registrar"

        ancho_card = ancho_movil() if es_movil() else 720

        # MODO 1: configurar hábitos
        if estado["modo_registro"] == "configurar":
            boton_guardar_habitos = boton_principal(
                "Guardar mis hábitos",
                ft.Icons.SAVE,
                guardar_configuracion_habitos,
            )

            contenido.content = ft.Column(
                controls=[
                    texto_titulo("Registro de hábitos"),
                    texto_subtitulo(
                        "Primero selecciona los hábitos que quieres monitorear."
                    ),

                    tarjeta(
                        width=ancho_card,
                        content=ft.Column(
                            controls=[
                                (
                                    ft.Column(
                                        controls=[
                                            ft.Text(
                                                "Elige tus hábitos",
                                                size=14,
                                                color=ft.Colors.BLUE_GREY_600,
                                            ),
                                            ft.Text(
                                                f"{len(estado['habitos_configuracion'])} seleccionados",
                                                size=14,
                                                color=ft.Colors.BLUE_600,
                                            ),
                                        ],
                                        spacing=4,
                                    )
                                    if es_movil()
                                    else ft.Row(
                                        controls=[
                                            ft.Text(
                                                "Elige tus hábitos",
                                                size=14,
                                                color=ft.Colors.BLUE_GREY_600,
                                            ),
                                            ft.Text(
                                                f"{len(estado['habitos_configuracion'])} seleccionados",
                                                size=14,
                                                color=ft.Colors.BLUE_600,
                                            ),
                                        ],
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    )
                                ),

                                ft.Divider(),

                                *[
                                    fila_habito_configuracion(i, h["nombre_habito"])
                                    for i, h in enumerate(habitos)
                                ],
                            ],
                            spacing=12,
                        ),
                    ),

                    boton_guardar_habitos,
                ],
                spacing=20,
                scroll=ft.ScrollMode.AUTO,
            )

            page.update()
            return

        # MODO 2: registrar hábitos diarios
        mis_habitos = obtener_mis_habitos()
        estado["habitos_registro"] = mis_habitos

        boton_guardar_registro = boton_principal(
            "Guardar registro",
            ft.Icons.SAVE,
            guardar_registro,
        )

        boton_cambiar_habitos = ft.Button(
            content="Cambiar mis hábitos",
            icon=ft.Icons.EDIT,
            on_click=cambiar_a_configuracion,
        )

        controles_botones = (
            ft.Column(
                controls=[
                    boton_guardar_registro,
                    boton_cambiar_habitos,
                ],
                spacing=12,
            )
            if es_movil()
            else ft.Row(
                controls=[
                    boton_guardar_registro,
                    boton_cambiar_habitos,
                ],
                spacing=12,
            )
        )

        contenido.content = ft.Column(
            controls=[
                texto_titulo("Registro de hábitos"),
                texto_subtitulo(
                    "Marca los hábitos de ahorro de agua que cumpliste hoy."
                ),

                tarjeta(
                    width=ancho_card,
                    content=ft.Column(
                        controls=[
                            (
                                ft.Column(
                                    controls=[
                                        ft.Text(
                                            "Progreso de hoy",
                                            size=14,
                                            color=ft.Colors.BLUE_GREY_600,
                                        ),
                                        ft.Text(
                                            f"{len(estado['habitos_seleccionados'])} de {len(mis_habitos)} hábitos",
                                            size=14,
                                            color=ft.Colors.BLUE_600,
                                        ),
                                    ],
                                    spacing=4,
                                )
                                if es_movil()
                                else ft.Row(
                                    controls=[
                                        ft.Text(
                                            "Progreso de hoy",
                                            size=14,
                                            color=ft.Colors.BLUE_GREY_600,
                                        ),
                                        ft.Text(
                                            f"{len(estado['habitos_seleccionados'])} de {len(mis_habitos)} hábitos",
                                            size=14,
                                            color=ft.Colors.BLUE_600,
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                )
                            ),

                            ft.Divider(),

                            *[
                                fila_habito(i, h["nombre_habito"])
                                for i, h in enumerate(mis_habitos)
                            ],
                        ],
                        spacing=12,
                    ),
                ),

                controles_botones,
            ],
            spacing=20,
            scroll=ft.ScrollMode.AUTO,
        )

        page.update()

    def tarjeta_estadistica(nombre, valor, icono, color):
        return tarjeta(
            expand=True,
            height=150,
            content=ft.Column(
                controls=[
                    ft.Container(
                        width=46,
                        height=46,
                        border_radius=10,
                        bgcolor=color,
                        content=ft.Icon(
                            icono,
                            color=ft.Colors.WHITE,
                            size=24,
                        ),
                    ),
                    ft.Text(
                        str(valor),
                        size=28,
                        color=ft.Colors.BLUE_700,
                    ),
                    ft.Text(
                        nombre,
                        size=13,
                        color=ft.Colors.BLUE_GREY_700,
                    ),
                ],
                spacing=8,
            ),
        )

    def lista_notificaciones_recientes():
        columna = ft.Column(spacing=10)

        if len(estado["notificaciones"]) == 0:
            columna.controls.append(
                ft.Container(
                    padding=18,
                    border_radius=10,
                    bgcolor=ft.Colors.BLUE_50,
                    content=ft.Text(
                        "Todavía no hay notificaciones. Los recordatorios aparecerán aquí.",
                        size=14,
                        color=ft.Colors.BLUE_700,
                    ),
                )
            )
        else:
            for n in estado["notificaciones"][:6]:
                columna.controls.append(
                    ft.Container(
                        padding=16,
                        border_radius=10,
                        bgcolor=ft.Colors.WHITE,
                        content=ft.Row(
                            controls=[
                                ft.Container(
                                    width=42,
                                    height=42,
                                    border_radius=10,
                                    bgcolor=ft.Colors.BLUE_500,
                                    content=ft.Icon(
                                        n["icono"],
                                        color=ft.Colors.WHITE,
                                        size=22,
                                    ),
                                ),
                                ft.Column(
                                    controls=[
                                        ft.Text(
                                            n["titulo"],
                                            size=15,
                                            weight=ft.FontWeight.BOLD,
                                            color=ft.Colors.BLUE_GREY_900,
                                        ),
                                        ft.Text(
                                            n["mensaje"],
                                            size=13,
                                            color=ft.Colors.BLUE_GREY_700,
                                        ),
                                        ft.Text(
                                            n["hora"],
                                            size=11,
                                            color=ft.Colors.BLUE_GREY_400,
                                        ),
                                    ],
                                    spacing=2,
                                    expand=True,
                                ),
                            ],
                            spacing=12,
                        ),
                    )
                )

        return columna

    def vista_seguimiento():
        estadisticas = obtener_estadisticas()

        dias = estadisticas.get("dias", 0)
        cumplidos = estadisticas.get("cumplidos", 0)

        try:
            ancho_card = ancho_movil() if es_movil() else 720
        except Exception:
            ancho_card = 320 if es_movil() else 720

        if dias == 0:
            mensaje_progreso = tarjeta(
                width=ancho_card if es_movil() else None,
                content=ft.Text(
                    "Aún no tienes registros. Comienza a registrar tus hábitos para ver tu progreso.",
                    size=14,
                    color=ft.Colors.BLUE_700,
                ),
                color=ft.Colors.BLUE_50,
            )
        else:
            mensaje_progreso = tarjeta(
                width=ancho_card if es_movil() else None,
                content=ft.Text(
                    "Tu progreso se está calculando con base en tus registros guardados.",
                    size=14,
                    color=ft.Colors.GREEN_700,
                ),
                color=ft.Colors.GREEN_50,
            )

        if es_movil():
            tarjeta_dias = tarjeta(
                width=ancho_card,
                content=ft.Row(
                    controls=[
                        ft.Container(
                            width=58,
                            height=58,
                            border_radius=14,
                            bgcolor=ft.Colors.BLUE_500,
                            alignment=ft.Alignment(0, 0),
                            content=ft.Icon(
                                ft.Icons.CALENDAR_MONTH,
                                color=ft.Colors.WHITE,
                                size=30,
                            ),
                        ),
                        ft.Column(
                            controls=[
                                ft.Text(
                                    str(dias),
                                    size=28,
                                    color=ft.Colors.BLUE_600,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Text(
                                    "Días registrados",
                                    size=14,
                                    color=ft.Colors.BLUE_GREY_700,
                                ),
                            ],
                            spacing=2,
                            expand=True,
                        ),
                    ],
                    spacing=14,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            )

            tarjeta_cumplidos = tarjeta(
                width=ancho_card,
                content=ft.Row(
                    controls=[
                        ft.Container(
                            width=58,
                            height=58,
                            border_radius=14,
                            bgcolor=ft.Colors.CYAN_600,
                            alignment=ft.Alignment(0, 0),
                            content=ft.Icon(
                                ft.Icons.CHECK_CIRCLE,
                                color=ft.Colors.WHITE,
                                size=30,
                            ),
                        ),
                        ft.Column(
                            controls=[
                                ft.Text(
                                    str(cumplidos),
                                    size=28,
                                    color=ft.Colors.BLUE_600,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Text(
                                    "Hábitos cumplidos",
                                    size=14,
                                    color=ft.Colors.BLUE_GREY_700,
                                ),
                            ],
                            spacing=2,
                            expand=True,
                        ),
                    ],
                    spacing=14,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            )

            estadisticas_layout = ft.Column(
                controls=[
                    tarjeta_dias,
                    tarjeta_cumplidos,
                ],
                spacing=16,
            )

            encabezado_recordatorios = ft.Column(
                controls=[
                    ft.Text(
                        "Recordatorios de hábitos",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_GREY_900,
                    ),
                    ft.Row(
                        controls=[
                            ft.Switch(
                                label="Activos",
                                value=estado["recordatorios_activos"],
                                on_change=cambiar_recordatorios,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.START,
                    ),
                ],
                spacing=8,
            )

            boton_probar = ft.Button(
                content="Probar notificación",
                icon=ft.Icons.NOTIFICATIONS_ACTIVE,
                on_click=probar_notificacion,
            )

        else:
            estadisticas_layout = ft.Row(
                controls=[
                    tarjeta_estadistica(
                        "Días registrados",
                        dias,
                        ft.Icons.CALENDAR_MONTH,
                        ft.Colors.BLUE_500,
                    ),
                    tarjeta_estadistica(
                        "Hábitos cumplidos",
                        cumplidos,
                        ft.Icons.CHECK_CIRCLE,
                        ft.Colors.CYAN_600,
                    ),
                ],
                spacing=20,
            )

            encabezado_recordatorios = ft.Row(
                controls=[
                    ft.Text(
                        "Recordatorios de hábitos",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_GREY_900,
                    ),
                    ft.Switch(
                        label="Activos",
                        value=estado["recordatorios_activos"],
                        on_change=cambiar_recordatorios,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            )

            boton_probar = ft.Button(
                content="Probar notificación",
                icon=ft.Icons.NOTIFICATIONS_ACTIVE,
                on_click=probar_notificacion,
            )

        contenido.content = ft.Column(
            controls=[
                texto_titulo("Seguimiento de avances"),
                texto_subtitulo("Visualiza tu progreso en el ahorro de agua."),

                estadisticas_layout,

                mensaje_progreso,

                tarjeta(
                    width=ancho_card if es_movil() else None,
                    content=ft.Column(
                        controls=[
                            encabezado_recordatorios,

                            ft.Text(
                                "La app enviará avisos para recordar hábitos de ahorro de agua durante el uso.",
                                size=13,
                                color=ft.Colors.BLUE_GREY_600,
                            ),

                            menu_frecuencia_recordatorios(),

                            boton_probar,

                            lista_notificaciones_recientes(),
                        ],
                        spacing=15,
                    ),
                ),
            ],
            spacing=20,
            scroll=ft.ScrollMode.AUTO,
        )

        page.update()

    def vista_historial():
        try:
            from database import obtener_historial_usuario

            if id_usuario_actual is None:
                registros_bd = []
            else:
                registros_bd = obtener_historial_usuario(id_usuario_actual)

        except Exception as error:
            print("Error al cargar historial desde BD:", error)
            registros_bd = []

        ancho_card = ancho_movil() if es_movil() else 720

        if not registros_bd:
            contenido.content = ft.Column(
                controls=[
                    texto_titulo("Historial"),
                    texto_subtitulo("Consulta tus registros anteriores por fecha."),

                    tarjeta(
                        width=ancho_card,
                        color=ft.Colors.BLUE_50,
                        content=ft.Column(
                            controls=[
                                ft.Icon(
                                    ft.Icons.CALENDAR_MONTH,
                                    color=ft.Colors.BLUE_400,
                                    size=42,
                                ),
                                ft.Text(
                                    "No hay registros en el historial. Comienza a registrar tus hábitos diarios.",
                                    size=14,
                                    color=ft.Colors.BLUE_700,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=10,
                        ),
                    ),
                ],
                spacing=20,
                scroll=ft.ScrollMode.AUTO,
            )

            page.update()
            return

        registros_por_fecha = {}

        for registro in registros_bd:
            fecha = str(registro.get("fecha", "Sin fecha"))

            if fecha not in registros_por_fecha:
                registros_por_fecha[fecha] = []

            registros_por_fecha[fecha].append(registro)

        tarjetas_historial = []

        for fecha, registros_fecha in registros_por_fecha.items():
            controles_habitos = []

            for registro in registros_fecha:
                habito_data = registro.get("habito", {})

                if isinstance(habito_data, dict):
                    nombre_habito = habito_data.get(
                        "nombre_habito",
                        "Hábito no encontrado"
                    )
                else:
                    nombre_habito = str(habito_data)

                hora_registro = str(registro.get("hora") or "")[:5]

                if es_movil():
                    fila_registro = ft.Row(
                        controls=[
                            ft.Icon(
                                ft.Icons.CHECK_CIRCLE,
                                color=ft.Colors.GREEN_500,
                                size=20,
                            ),
                            ft.Column(
                                controls=[
                                    ft.Text(
                                        nombre_habito,
                                        size=14,
                                        color=ft.Colors.BLUE_GREY_700,
                                        weight=ft.FontWeight.W_500,
                                    ),
                                    ft.Text(
                                        hora_registro if hora_registro else "Sin hora",
                                        size=12,
                                        color=ft.Colors.BLUE_GREY_500,
                                    ),
                                ],
                                spacing=2,
                                expand=True,
                            ),
                        ],
                        spacing=10,
                        vertical_alignment=ft.CrossAxisAlignment.START,
                    )
                else:
                    fila_registro = ft.Row(
                        controls=[
                            ft.Icon(
                                ft.Icons.CHECK_CIRCLE,
                                color=ft.Colors.GREEN_500,
                                size=17,
                            ),
                            ft.Text(
                                nombre_habito,
                                size=13,
                                color=ft.Colors.BLUE_GREY_700,
                                expand=True,
                            ),
                            ft.Text(
                                hora_registro,
                                size=13,
                                color=ft.Colors.BLUE_GREY_600,
                            ),
                        ],
                        spacing=8,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    )

                controles_habitos.append(fila_registro)

            tarjetas_historial.append(
                tarjeta(
                    width=ancho_card,
                    content=ft.Column(
                        controls=[
                            ft.Text(
                                f"Fecha: {fecha}",
                                size=16 if es_movil() else 15,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.BLUE_700,
                            ),
                            ft.Divider(),
                            *controles_habitos,
                        ],
                        spacing=10,
                    ),
                )
            )

        contenido.content = ft.Column(
            controls=[
                texto_titulo("Historial"),
                texto_subtitulo("Consulta tus registros anteriores por fecha."),

                ft.Column(
                    controls=tarjetas_historial,
                    spacing=16 if es_movil() else 15,
                ),
            ],
            spacing=20,
            scroll=ft.ScrollMode.AUTO,
        )

        page.update()

    def tarjeta_recomendacion(titulo, descripcion, icono):
        if es_movil():
            return ft.Container(
                width=ancho_movil(),
                padding=18,
                bgcolor=ft.Colors.WHITE,
                border_radius=18,
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=18,
                    color=ft.Colors.BLUE_GREY_100,
                    offset=ft.Offset(0, 4),
                ),
                content=ft.Row(
                    controls=[
                        ft.Container(
                            width=58,
                            height=58,
                            border_radius=14,
                            bgcolor=ft.Colors.BLUE_500,
                            alignment=ft.Alignment(0, 0),
                            content=ft.Icon(
                                icono,
                                color=ft.Colors.WHITE,
                                size=30,
                            ),
                        ),
                        ft.Column(
                            controls=[
                                ft.Text(
                                    titulo,
                                    size=18,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.BLUE_GREY_900,
                                ),
                                ft.Text(
                                    descripcion,
                                    size=13,
                                    color=ft.Colors.BLUE_GREY_600,
                                ),
                            ],
                            spacing=6,
                            expand=True,
                        ),
                    ],
                    spacing=14,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
            )

        return ft.Container(
            width=190,
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=18,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=18,
                color=ft.Colors.BLUE_GREY_100,
                offset=ft.Offset(0, 4),
            ),
            content=ft.Column(
                controls=[
                    ft.Container(
                        width=60,
                        height=60,
                        border_radius=14,
                        bgcolor=ft.Colors.BLUE_500,
                        alignment=ft.Alignment(0, 0),
                        content=ft.Icon(
                            icono,
                            color=ft.Colors.WHITE,
                            size=32,
                        ),
                    ),
                    ft.Text(
                        titulo,
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_GREY_900,
                    ),
                    ft.Text(
                        descripcion,
                        size=13,
                        color=ft.Colors.BLUE_GREY_600,
                    ),
                ],
                spacing=12,
            ),
        )

    def vista_recomendaciones():
        tarjetas_movil = ft.Column(
            controls=[
                tarjeta_recomendacion(
                    recomendaciones[0]["titulo"],
                    recomendaciones[0]["descripcion"],
                    recomendaciones[0]["icono"],
                ),
                tarjeta_recomendacion(
                    recomendaciones[1]["titulo"],
                    recomendaciones[1]["descripcion"],
                    recomendaciones[1]["icono"],
                ),
                tarjeta_recomendacion(
                    recomendaciones[2]["titulo"],
                    recomendaciones[2]["descripcion"],
                    recomendaciones[2]["icono"],
                ),
                tarjeta_recomendacion(
                    recomendaciones[3]["titulo"],
                    recomendaciones[3]["descripcion"],
                    recomendaciones[3]["icono"],
                ),
                tarjeta_recomendacion(
                    recomendaciones[4]["titulo"],
                    recomendaciones[4]["descripcion"],
                    recomendaciones[4]["icono"],
                ),
                tarjeta_recomendacion(
                    recomendaciones[5]["titulo"],
                    recomendaciones[5]["descripcion"],
                    recomendaciones[5]["icono"],
                ),
            ],
            spacing=16,
        )

        tarjetas_escritorio = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        tarjeta_recomendacion(
                            recomendaciones[0]["titulo"],
                            recomendaciones[0]["descripcion"],
                            recomendaciones[0]["icono"],
                        ),
                        tarjeta_recomendacion(
                            recomendaciones[1]["titulo"],
                            recomendaciones[1]["descripcion"],
                            recomendaciones[1]["icono"],
                        ),
                        tarjeta_recomendacion(
                            recomendaciones[2]["titulo"],
                            recomendaciones[2]["descripcion"],
                            recomendaciones[2]["icono"],
                        ),
                    ],
                    spacing=20,
                ),
                ft.Row(
                    controls=[
                        tarjeta_recomendacion(
                            recomendaciones[3]["titulo"],
                            recomendaciones[3]["descripcion"],
                            recomendaciones[3]["icono"],
                        ),
                        tarjeta_recomendacion(
                            recomendaciones[4]["titulo"],
                            recomendaciones[4]["descripcion"],
                            recomendaciones[4]["icono"],
                        ),
                        tarjeta_recomendacion(
                            recomendaciones[5]["titulo"],
                            recomendaciones[5]["descripcion"],
                            recomendaciones[5]["icono"],
                        ),
                    ],
                    spacing=20,
                ),
            ],
            spacing=20,
        )

        contenido.content = ft.Column(
            controls=[
                texto_titulo("Recomendaciones"),
                texto_subtitulo(
                    "Consejos breves sobre ahorro, prevención de fugas, reutilización y reducción de desperdicio."
                ),

                tarjetas_movil if es_movil() else tarjetas_escritorio,

                ft.Container(
                    width=ancho_movil() if es_movil() else None,
                    padding=24,
                    border_radius=12,
                    gradient=ft.LinearGradient(
                        begin=ft.Alignment(-1, 0),
                        end=ft.Alignment(1, 0),
                        colors=[
                            ft.Colors.BLUE_600,
                            ft.Colors.CYAN_400,
                        ],
                    ),
                    content=ft.Column(
                        controls=[
                            ft.Text(
                                "¿Sabías que...?",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE,
                            ),
                            ft.Text(
                                "Una comunidad puede generar un gran impacto si registra y mejora sus hábitos diarios de ahorro de agua.",
                                size=14,
                                color=ft.Colors.BLUE_50,
                            ),
                        ],
                        spacing=8,
                    ),
                ),
            ],
            spacing=20,
            scroll=ft.ScrollMode.AUTO,
        )

        page.update()

    def cambiar_vista(vista):
        estado["vista"] = vista
        menu_lateral.content = construir_menu()

        if vista == "inicio":
            vista_inicio()
        elif vista == "registro":
            vista_registro()
        elif vista == "seguimiento":
            vista_seguimiento()
        elif vista == "historial":
            vista_historial()
        elif vista == "recomendaciones":
            vista_recomendaciones()

        page.update()

    def cerrar_sesion():
        estado["recordatorios_activos"] = False

        try:
            from login import mostrar_login
            mostrar_login(page)
        except Exception:
            page.clean()
            page.add(
                ft.Text(
                    "Sesión cerrada",
                    size=24,
                    color=ft.Colors.BLUE_900,
                )
            )

    def cambiar_vista_desde_barra(e):
        vistas = [
            "inicio",
            "registro",
            "seguimiento",
            "historial",
            "recomendaciones",
        ]

        vista = vistas[e.control.selected_index]
        estado["vista"] = vista
        cambiar_vista(vista)

    def barra_navegacion_movil():
        indices = {
            "inicio": 0,
            "registro": 1,
            "seguimiento": 2,
            "historial": 3,
            "recomendaciones": 4,
        }

        return ft.NavigationBar(
            selected_index=indices.get(estado["vista"], 0),
            destinations=[
                ft.NavigationBarDestination(
                    icon=ft.Icons.HOME,
                    label="Inicio",
                ),
                ft.NavigationBarDestination(
                    icon=ft.Icons.CHECKLIST,
                    label="Registro",
                ),
                ft.NavigationBarDestination(
                    icon=ft.Icons.INSIGHTS,
                    label="Avances",
                ),
                ft.NavigationBarDestination(
                    icon=ft.Icons.HISTORY,
                    label="Historial",
                ),
                ft.NavigationBarDestination(
                    icon=ft.Icons.LIGHTBULB,
                    label="Consejos",
                ),
            ],
            on_change=cambiar_vista_desde_barra,
        )

    if es_movil():
        page.navigation_bar = barra_navegacion_movil()
        page.appbar = None
        page.scroll = ft.ScrollMode.AUTO

        barra_superior_movil = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Text(
                        "AguaConsciente",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_GREY_900,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.LOGOUT,
                        icon_color=ft.Colors.RED_500,
                        tooltip="Cerrar sesión",
                        on_click=lambda e: cerrar_sesion(),
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=16, right=16, top=12, bottom=8),
        )

        layout = ft.Column(
            controls=[
                barra_superior_movil,
                ft.Container(
                    content=contenido,
                    expand=True,
                    padding=ft.Padding(
                        left=12,
                        right=12,
                        top=10,
                        bottom=110,
                    ),
                ),
            ],
            expand=True,
            spacing=0,
        )

    else:
        page.navigation_bar = None
        page.appbar = None
        page.scroll = None

        layout = ft.Row(
            controls=[
                menu_lateral,
                contenido,
            ],
            expand=True,
            spacing=0,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )

    def ajustar_tamano(e=None):
        alto = alto_ventana()
        ancho = ancho_pantalla()
        modo_movil = es_movil()

        try:
            if e and hasattr(e, "height") and e.height:
                alto = max(720, e.height)
        except Exception:
            pass

        try:
            if e and hasattr(e, "width") and e.width:
                ancho = e.width
        except Exception:
            pass

        if modo_movil:
            contenido.height = None
            contenido.width = None

            try:
                page.navigation_bar = barra_navegacion_movil()
            except Exception:
                pass

        else:
            page.navigation_bar = None

            menu_lateral.width = 235
            menu_lateral.height = alto

            contenido.height = alto
            contenido.width = None
            contenido.expand = True

            try:
                layout.expand = True
                layout.height = alto
            except Exception:
                pass

        page.update()


    async def recalcular_inicio():
        try:
            await asyncio.sleep(0.4)
            ajustar_tamano()
            cambiar_vista(estado.get("vista", "inicio"))
            page.update()

            await asyncio.sleep(0.8)
            ajustar_tamano()
            cambiar_vista(estado.get("vista", "inicio"))
            page.update()

        except Exception as error:
            print("Error al recalcular layout inicial:", error)

    page.on_resize = ajustar_tamano

    page.add(layout)

    iniciar_recordatorios()
    ajustar_tamano()
    cambiar_vista("inicio")

    page.run_task(recalcular_inicio)
