import flet as ft


def mostrar_login(page: ft.Page):
    page.clean()

    modo_registro = {"activo": False}

    def estilo_campo():
        return {
            "width": 300,
            "border_radius": 12,
            "text_style": ft.TextStyle(color=ft.Colors.BLACK),
            "label_style": ft.TextStyle(color=ft.Colors.BLUE_GREY_700),
            "cursor_color": ft.Colors.BLACK,
            "border_color": ft.Colors.BLUE_GREY_300,
            "focused_border_color": ft.Colors.BLUE_600,
        }

    def abrir_app(nombre_usuario):
        from app import mostrar_app
        mostrar_app(page, nombre_usuario)

    def registrar_en_bd(nombre, correo, contrasena):
        try:
            from database import registrar_usuario

            resultado = registrar_usuario(nombre, correo, contrasena)

            if isinstance(resultado, tuple):
                exito = resultado[0]
                mensaje = resultado[1] if len(resultado) > 1 else "Registro procesado"
                return exito, mensaje

            if resultado is True:
                return True, "Usuario registrado correctamente"

            return False, "No se pudo registrar el usuario"

        except TypeError:
            try:
                from database import registrar_usuario

                resultado = registrar_usuario(correo, contrasena)

                if isinstance(resultado, tuple):
                    exito = resultado[0]
                    mensaje = resultado[1] if len(resultado) > 1 else "Registro procesado"
                    return exito, mensaje

                if resultado is True:
                    return True, "Usuario registrado correctamente"

                return False, "No se pudo registrar el usuario"

            except Exception as error:
                return False, f"Error al registrar: {error}"

        except Exception as error:
            return False, f"Error al registrar: {error}"

    def validar_en_bd(correo, contrasena):
        print("Funcion entro validar en bd y el usuario y contraseña son:"+ correo + "y la contraseña es" + contrasena)
        #breakpoint()
        try:
            from database import validar_usuario
            print("Sí se importó validar_usuario desde database.py")

            usuario = validar_usuario(correo, contrasena)
            print(usuario)

            if usuario:
                return usuario

            return None

        except Exception as error:
            print("Error en login.py al validar usuario:", error)
            return None

    def mostrar_formulario():
        page.clean()

        es_registro = modo_registro["activo"]

        nombre = ft.TextField(
            label="Nombre completo",
            prefix_icon=ft.Icons.PERSON,
            visible=es_registro,
            **estilo_campo()
        )

        correo = ft.TextField(
            label="Correo electrónico",
            prefix_icon=ft.Icons.EMAIL,
            keyboard_type=ft.KeyboardType.EMAIL,
            **estilo_campo()
        )

        contrasena = ft.TextField(
            label="Contraseña",
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.Icons.LOCK,
            **estilo_campo()
        )

        confirmar_contrasena = ft.TextField(
            label="Confirmar contraseña",
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.Icons.LOCK,
            visible=es_registro,
            **estilo_campo()
        )

        mensaje = ft.Text("", size=14)

        def cambiar_modo(e):
            modo_registro["activo"] = not modo_registro["activo"]
            mostrar_formulario()

        def entrar_modo_prueba(e):
            abrir_app("Usuario de prueba")

        def accion_principal(e):
            correo_usuario = correo.value.strip().lower()
            password_usuario = contrasena.value.strip()
            print("El Usuario es:"+ correo_usuario + "la contraseña es:" + password_usuario)
            if correo_usuario == "" or password_usuario == "":
                mensaje.value = "Llena todos los campos"
                mensaje.color = ft.Colors.RED
                page.update()
                return

            if es_registro:
                nombre_usuario = nombre.value.strip()
                confirmar = confirmar_contrasena.value.strip()

                if nombre_usuario == "":
                    mensaje.value = "Escribe tu nombre completo"
                    mensaje.color = ft.Colors.RED

                elif confirmar == "":
                    mensaje.value = "Confirma tu contraseña"
                    mensaje.color = ft.Colors.RED

                elif password_usuario != confirmar:
                    mensaje.value = "Las contraseñas no coinciden"
                    mensaje.color = ft.Colors.RED

                else:
                    exito, respuesta = registrar_en_bd(
                        nombre_usuario,
                        correo_usuario,
                        password_usuario,
                    )

                    mensaje.value = respuesta

                    if exito:
                        mensaje.color = ft.Colors.GREEN
                        nombre.value = ""
                        correo.value = ""
                        contrasena.value = ""
                        confirmar_contrasena.value = ""
                    else:
                        mensaje.color = ft.Colors.RED

            else:
                usuario_db = validar_en_bd(correo_usuario, password_usuario)

                if usuario_db:
                    abrir_app(usuario_db.get("nombre", correo_usuario))
                    return
                else:
                    mensaje.value = "Correo o contraseña incorrectos"
                    mensaje.color = ft.Colors.RED

            page.update()

        tarjeta_login = ft.Container(
            width=390,
            padding=35,
            border_radius=22,
            bgcolor=ft.Colors.WHITE,
            shadow=ft.BoxShadow(
                blur_radius=20,
                spread_radius=2,
                color=ft.Colors.BLUE_GREY_200,
            ),
            content=ft.Column(
                controls=[
                    ft.Icon(
                        ft.Icons.APP_REGISTRATION if es_registro else ft.Icons.WATER_DROP,
                        size=70,
                        color=ft.Colors.BLUE,
                    ),

                    ft.Text(
                        "Crear cuenta" if es_registro else "Agua Consciente",
                        size=30,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_900,
                    ),

                    ft.Text(
                        "Regístrate para cuidar el agua"
                        if es_registro
                        else "Inicia sesión para continuar",
                        size=14,
                        color=ft.Colors.BLUE_GREY_600,
                    ),

                    nombre,
                    correo,
                    contrasena,
                    confirmar_contrasena,

                    mensaje,

                    ft.Button(
                        content="Registrarse" if es_registro else "Iniciar sesión",
                        icon=ft.Icons.CHECK if es_registro else ft.Icons.LOGIN,
                        width=300,
                        height=42,
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.BLUE_600,
                            color=ft.Colors.WHITE,
                            shape=ft.RoundedRectangleBorder(radius=10),
                        ),
                        on_click=accion_principal,
                    ),

                    ft.TextButton(
                        content="Ya tengo cuenta"
                        if es_registro
                        else "¿No tienes cuenta? Regístrate",
                        on_click=cambiar_modo,
                    ),

                    ft.TextButton(
                        content="Entrar como prueba",
                        on_click=entrar_modo_prueba,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15,
            ),
        )

        page.add(
            ft.Container(
                expand=True,
                alignment=ft.Alignment(0, 0),
                bgcolor=ft.Colors.BLUE_GREY_50,
                content=tarjeta_login,
            )
        )

    mostrar_formulario()