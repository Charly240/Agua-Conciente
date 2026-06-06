import flet as ft
from datetime import date, datetime
import threading
import time
import random


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
            if page.window_height:
                return page.window_height
        except Exception:
            pass

        try:
            if page.window.height:
                return page.window.height
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
    }


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

        if estado["vista"] == "seguimiento":
            vista_seguimiento()
            page.update()

    def cambiar_frecuencia_recordatorios(e):
        frecuencia = e.control.value

        estado["frecuencia_recordatorios"] = frecuencia
        estado["intervalo_recordatorios"] = opciones_frecuencia[frecuencia]
        estado["ultimo_recordatorio"] = time.time()

        enviar_notificacion(
            "Frecuencia actualizada",
            f"Los recordatorios ahora se enviarán: {frecuencia}.",
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

        return dropdown

    def obtener_estadisticas():
        dias = len(estado["registros"])
        cumplidos = sum(len(r["habitos"]) for r in estado["registros"])
        puntos = cumplidos * 10

        if dias == 0:
            avance = 0
        else:
            avance = int((cumplidos / (dias * len(habitos))) * 100)

        return dias, cumplidos, puntos, avance

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
    def cambiar_recordatorios(e):
        estado["recordatorios_activos"] = e.control.value

        if estado["recordatorios_activos"]:
            enviar_notificacion(
                "Recordatorios activados",
                "Te avisaremos para seguir cuidando el agua.",
                ft.Icons.NOTIFICATIONS_ACTIVE,
            )
        else:
            enviar_notificacion(
                "Recordatorios desactivados",
                "Puedes volver a activarlos cuando quieras.",
                ft.Icons.NOTIFICATIONS_OFF,
            )

        cambiar_vista(estado["vista"])

    def vista_inicio():
        contenido.content = ft.Column(
            controls=[
                ft.Container(
                    padding=30,
                    border_radius=14,
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
                    content=ft.Column(
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
                                    ),
                                ],
                                spacing=15,
                            ),
                            ft.Text(
                                "Este proyecto ayuda a registrar hábitos, consultar avances y revisar recomendaciones para cuidar el agua en la comunidad.",
                                size=14,
                                color=ft.Colors.BLUE_50,
                            ),
                        ],
                        spacing=18,
                    ),
                ),

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

                ft.Row(
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
                ),

                tarjeta(
                    content=ft.Row(
                        controls=[
                            ft.Icon(
                                ft.Icons.NOTIFICATIONS_ACTIVE
                                if estado["recordatorios_activos"]
                                else ft.Icons.NOTIFICATIONS_OFF,
                                color=ft.Colors.BLUE_600,
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
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                ),
            ],
            spacing=22,
            scroll=ft.ScrollMode.AUTO,
        )

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

        # MODO 1: configurar hábitos
        if estado["modo_registro"] == "configurar":
            contenido.content = ft.Column(
                controls=[
                    texto_titulo("Registro de hábitos"),
                    texto_subtitulo(
                        "Primero selecciona los hábitos que quieres monitorear."
                    ),

                    tarjeta(
                        width=720,
                        content=ft.Column(
                            controls=[
                                ft.Row(
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

                    boton_principal(
                        "Guardar mis hábitos",
                        ft.Icons.SAVE,
                        guardar_configuracion_habitos,
                    ),
                ],
                spacing=20,
                scroll=ft.ScrollMode.AUTO,
            )

            page.update()
            return

        # MODO 2: registrar hábitos diarios
        mis_habitos = obtener_mis_habitos()
        estado["habitos_registro"] = mis_habitos

        contenido.content = ft.Column(
            controls=[
                texto_titulo("Registro de hábitos"),
                texto_subtitulo(
                    "Marca los hábitos de ahorro de agua que cumpliste hoy."
                ),

                tarjeta(
                    width=720,
                    content=ft.Column(
                        controls=[
                            ft.Row(
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

                ft.Row(
                    controls=[
                        boton_principal(
                            "Guardar registro",
                            ft.Icons.SAVE,
                            guardar_registro,
                        ),

                        ft.Button(
                            content="Cambiar mis hábitos",
                            icon=ft.Icons.EDIT,
                            on_click=cambiar_a_configuracion,
                        ),
                    ],
                    spacing=12,
                ),
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
        dias, cumplidos, puntos, avance = obtener_estadisticas()

        if dias == 0:
            texto_avance = (
                "Aún no tienes registros. Comienza a registrar tus hábitos para ver tu progreso."
            )
        else:
            texto_avance = (
                f"Has registrado {dias} día(s), cumplido {cumplidos} hábito(s) "
                f"y acumulado {puntos} puntos de ahorro."
            )

        contenido.content = ft.Column(
            controls=[
                texto_titulo("Seguimiento de avances"),
                texto_subtitulo("Visualiza tu progreso en el ahorro de agua."),

                ft.Row(
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
                        tarjeta_estadistica(
                            "Puntos de ahorro",
                            puntos,
                            ft.Icons.STAR,
                            ft.Colors.LIGHT_BLUE_600,
                        ),
                        tarjeta_estadistica(
                            "Avance general",
                            f"{avance}%",
                            ft.Icons.SHOW_CHART,
                            ft.Colors.DEEP_PURPLE_400,
                        ),
                    ],
                    spacing=20,
                ),

                tarjeta(
                    color=ft.Colors.BLUE_50,
                    content=ft.Text(
                        texto_avance,
                        size=14,
                        color=ft.Colors.BLUE_700,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ),

                tarjeta(
                    content=ft.Column(
                        controls=[
                            ft.Row(
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
                            ),
                            ft.Text(
                                "La app enviará avisos para recordar hábitos de ahorro de agua durante el uso.",
                                size=13,
                                color=ft.Colors.BLUE_GREY_600,
                            ),

                            menu_frecuencia_recordatorios(),

                            ft.Button(
                                content="Probar notificación",
                                icon=ft.Icons.NOTIFICATIONS_ACTIVE,
                                on_click=probar_notificacion,
                            ),
                            lista_notificaciones_recientes(),
                        ],
                        spacing=15,
                    ),
                ),
            ],
            spacing=20,
            scroll=ft.ScrollMode.AUTO,
        )

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

        if not registros_bd:
            contenido.content = ft.Column(
                controls=[
                    texto_titulo("Historial"),
                    texto_subtitulo("Consulta tus registros anteriores por fecha."),
                    tarjeta(
                        width=720,
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
                nombre_habito = registro.get("habito", {}).get(
                    "nombre_habito",
                    "Hábito no encontrado"
                )

                hora_registro = str(registro.get("hora") or "")[:5]

                if hora_registro:
                    texto_habito = f"{nombre_habito}  •  {hora_registro}"
                else:
                    texto_habito = nombre_habito

                controles_habitos.append(
                    ft.Row(
                        controls=[
                            ft.Icon(
                                ft.Icons.CHECK_CIRCLE,
                                color=ft.Colors.GREEN_500,
                                size=17,
                            ),
                            ft.Text(
                                texto_habito,
                                size=13,
                                color=ft.Colors.BLUE_GREY_700,
                            ),
                        ],
                        spacing=8,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    )
                )

            tarjetas_historial.append(
                tarjeta(
                    expand=True,
                    content=ft.Column(
                        controls=[
                            ft.Text(
                                f"Fecha: {fecha}",
                                size=15,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.BLUE_700,
                            ),
                            ft.Divider(),
                            *controles_habitos,
                        ],
                        spacing=8,
                    ),
                )
            )

        contenido.content = ft.Column(
            controls=[
                texto_titulo("Historial"),
                texto_subtitulo("Consulta tus registros anteriores por fecha."),
                ft.Column(
                    controls=tarjetas_historial,
                    spacing=15,
                ),
            ],
            spacing=20,
            scroll=ft.ScrollMode.AUTO,
        )

        page.update()

    def tarjeta_recomendacion(rec):
        return tarjeta(
            expand=True,
            height=185,
            content=ft.Column(
                controls=[
                    ft.Container(
                        width=48,
                        height=48,
                        border_radius=10,
                        bgcolor=ft.Colors.BLUE_500,
                        content=ft.Icon(
                            rec["icono"],
                            color=ft.Colors.WHITE,
                            size=24,
                        ),
                    ),
                    ft.Text(
                        rec["titulo"],
                        size=17,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_GREY_900,
                    ),
                    ft.Text(
                        rec["descripcion"],
                        size=13,
                        color=ft.Colors.BLUE_GREY_700,
                    ),
                ],
                spacing=12,
            ),
        )

    def vista_recomendaciones():
        contenido.content = ft.Column(
            controls=[
                texto_titulo("Recomendaciones"),
                texto_subtitulo(
                    "Consejos breves sobre ahorro, prevención de fugas, reutilización y reducción de desperdicio."
                ),

                ft.Row(
                    controls=[
                        tarjeta_recomendacion(recomendaciones[0]),
                        tarjeta_recomendacion(recomendaciones[1]),
                        tarjeta_recomendacion(recomendaciones[2]),
                    ],
                    spacing=20,
                ),

                ft.Row(
                    controls=[
                        tarjeta_recomendacion(recomendaciones[3]),
                        tarjeta_recomendacion(recomendaciones[4]),
                        tarjeta_recomendacion(recomendaciones[5]),
                    ],
                    spacing=20,
                ),

                ft.Container(
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

        try:
            if e and hasattr(e, "height") and e.height:
                alto = e.height
        except Exception:
            pass

        menu_lateral.height = alto
        page.update()

    page.on_resize = ajustar_tamano

    page.add(layout)

    iniciar_recordatorios()
    ajustar_tamano()
    cambiar_vista("inicio")
