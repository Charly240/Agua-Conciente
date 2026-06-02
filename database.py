import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL:
    raise ValueError("Falta SUPABASE_URL en el archivo .env")

if not SUPABASE_KEY:
    raise ValueError("Falta SUPABASE_KEY en el archivo .env")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def validar_usuario(correo_usuario, password_usuario):
    print("Entramos a Funcion validar usuario"+ correo_usuario + "password" + password_usuario )
    try:
        respuesta = (
            supabase
            .table("usuario")
            .select("id_usuario, nombre, correo, contrasena")
            .eq("nombre", correo_usuario)
            .limit(1)
            .execute()
        )

        if not respuesta.data:
            print("ENtro al if not respuesta data")
            return None

        usuario = respuesta.data[0]
        print(usuario)

        # Comparación simple porque tu tabla tiene la columna contrasena
        if usuario["contrasena"] == password_usuario:
            return {
                "id_usuario": usuario["id_usuario"],
                "nombre": usuario["nombre"],
                "correo": usuario["correo"],
            }

        return None

    except Exception as error:
        print("Error al validar usuario:", error)
        return None


def registrar_usuario(nombre, correo, contrasena):
    try:
        # Primero revisa si ya existe el correo
        existente = (
            supabase
            .table("usuario")
            .select("id_usuario")
            .eq("correo", correo)
            .limit(1)
            .execute()
        )

        if existente.data:
            return False, "Ese correo ya está registrado"

        respuesta = (
            supabase
            .table("usuario")
            .insert({
                "nombre": nombre,
                "correo": correo,
                "contrasena": contrasena,
            })
            .execute()
        )

        if respuesta.data:
            return True, "Usuario registrado correctamente"

        return False, "No se pudo registrar el usuario"

    except Exception as error:
        return False, f"Error al registrar usuario: {error}"
    
def obtener_habitos():
    try:
        respuesta = (
            supabase
            .table("habito")
            .select("id_habito, nombre_habito, descripcion, categoria, activo")
            .eq("activo", True)
            .execute()
        )

        return respuesta.data if respuesta.data else []

    except Exception as error:
        print("Error al obtener hábitos:", error)
        return []


def guardar_registro_habitos(id_usuario, ids_habitos):
    try:
        registros = []

        for id_habito in ids_habitos:
            registros.append({
                "id_usuario": id_usuario,
                "id_habito": id_habito,
                "realizado": True,
                "observaciones": None,
            })

        respuesta = (
            supabase
            .table("registro_habito")
            .insert(registros)
            .execute()
        )

        if respuesta.data:
            return True, "Registro guardado correctamente"

        return False, "No se pudo guardar el registro"

    except Exception as error:
        print("Error al guardar registro de hábitos:", error)
        return False, f"Error al guardar registro: {error}"


def obtener_historial_usuario(id_usuario):
    try:
        respuesta = (
            supabase
            .table("registro_habito")
            .select(
                "id_registro, fecha, realizado, observaciones, "
                "habito(id_habito, nombre_habito, descripcion, categoria)"
            )
            .eq("id_usuario", id_usuario)
            .execute()
        )

        return respuesta.data if respuesta.data else []

    except Exception as error:
        print("Error al obtener historial:", error)
        return []