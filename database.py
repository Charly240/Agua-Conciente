import os
from datetime import date, datetime
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
    try:
        correo_usuario = correo_usuario.strip().lower()
        password_usuario = password_usuario.strip()

        respuesta = (
            supabase
            .table("usuario")
            .select("id_usuario, nombre, correo, contrasena")
            .eq("correo", correo_usuario)
            .limit(1)
            .execute()
        )

        if not respuesta.data:
            print("No se encontró usuario con ese correo")
            return None

        usuario = respuesta.data[0]

        if usuario["contrasena"] == password_usuario:
            return {
                "id_usuario": usuario["id_usuario"],
                "nombre": usuario["nombre"],
                "correo": usuario["correo"],
            }

        print("Contraseña incorrecta")
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

        # Fecha y hora tomadas del dispositivo donde se ejecuta la app
        fecha_actual = date.today().isoformat()
        hora_actual = datetime.now().strftime("%H:%M:%S")

        for id_habito in ids_habitos:
            registros.append({
                "id_usuario": id_usuario,
                "id_habito": id_habito,
                "fecha": fecha_actual,
                "hora": hora_actual,
                "realizado": True,
                "observaciones": None,
            })

        if not registros:
            return False, "Selecciona al menos un hábito"

        respuesta = (
            supabase
            .table("registro_habito")
            .insert(registros)
            .execute()
        )

        print("Registro guardado en BD:", respuesta.data)

        if respuesta.data:
            return True, "Registro guardado correctamente"

        return False, "No se pudo guardar el registro"

    except Exception as error:
        print("Error al guardar registro de hábitos:", error)
        return False, f"Error al guardar registro: {error}"

def obtener_historial_usuario(id_usuario):
    try:
        respuesta_registros = (
            supabase
            .table("registro_habito")
            .select("id_registro, id_usuario, id_habito, fecha, hora, realizado, observaciones")
            .eq("id_usuario", id_usuario)
            .order("fecha", desc=True)
            .order("hora", desc=True)
            .execute()
        )

        registros = respuesta_registros.data if respuesta_registros.data else []

        respuesta_habitos = (
            supabase
            .table("habito")
            .select("id_habito, nombre_habito, descripcion, categoria")
            .execute()
        )

        habitos = respuesta_habitos.data if respuesta_habitos.data else []

        mapa_habitos = {}

        for h in habitos:
            try:
                mapa_habitos[int(h["id_habito"])] = h
            except Exception:
                pass

        for registro in registros:
            try:
                id_habito = int(registro["id_habito"])
            except Exception:
                id_habito = registro["id_habito"]

            registro["habito"] = mapa_habitos.get(
                id_habito,
                {
                    "id_habito": id_habito,
                    "nombre_habito": "Hábito no encontrado",
                    "descripcion": "",
                    "categoria": "",
                }
            )

        return registros

    except Exception as error:
        print("Error al obtener historial:", error)
        return []

def guardar_habitos_usuario(id_usuario, ids_habitos):
    try:
        supabase.table("usuario_habito").delete().eq("id_usuario", id_usuario).execute()

        registros = []

        for id_habito in ids_habitos:
            registros.append({
                "id_usuario": id_usuario,
                "id_habito": id_habito,
                "activo": True,
            })

        if not registros:
            return False, "Selecciona al menos un hábito"

        respuesta = (
            supabase
            .table("usuario_habito")
            .insert(registros)
            .execute()
        )

        if respuesta.data:
            return True, "Hábitos configurados correctamente"

        return False, "No se pudieron guardar los hábitos"

    except Exception as error:
        print("Error al guardar hábitos del usuario:", error)
        return False, f"Error al guardar hábitos: {error}"


def obtener_habitos_usuario(id_usuario):
    try:
        respuesta_relaciones = (
            supabase
            .table("usuario_habito")
            .select("id_habito")
            .eq("id_usuario", id_usuario)
            .eq("activo", True)
            .execute()
        )

        relaciones = respuesta_relaciones.data if respuesta_relaciones.data else []

        ids_habitos = [
            int(r["id_habito"])
            for r in relaciones
        ]

        if not ids_habitos:
            return []

        respuesta_habitos = (
            supabase
            .table("habito")
            .select("id_habito, nombre_habito, descripcion, categoria, activo")
            .eq("activo", True)
            .execute()
        )

        habitos = respuesta_habitos.data if respuesta_habitos.data else []

        habitos_usuario = [
            h for h in habitos
            if int(h["id_habito"]) in ids_habitos
        ]

        return habitos_usuario

    except Exception as error:
        print("Error al obtener hábitos del usuario:", error)
        return []