import os
from datetime import date, datetime
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

load_dotenv()

SUPABASE_URL = os.getenv("https://xchwinawzjtpueuomrdp.supabase.co")
SUPABASE_KEY = os.getenv("sb_publishable_kympxAl4mI8Bq84ieW33Zg_dwxkORwlY")

if not SUPABASE_URL:
    raise ValueError("Falta SUPABASE_URL en el archivo .env")

if not SUPABASE_KEY:
    raise ValueError("Falta SUPABASE_KEY en el archivo .env")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def obtener_fecha_hora_mexico():
        ahora = datetime.now(ZoneInfo("America/Mexico_City"))

        fecha_actual = ahora.date().isoformat()
        hora_actual = ahora.strftime("%H:%M:%S")

        return fecha_actual, hora_actual

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
        fecha_actual, hora_actual = obtener_fecha_hora_mexico()

        registros = []

        for id_habito in ids_habitos:
            registros.append({
                "id_usuario": id_usuario,
                "id_habito": int(id_habito),
                "fecha": fecha_actual,
                "hora": hora_actual,
                "realizado": True,
                "observaciones": None
            })

        respuesta = (
            supabase
            .table("registro_habito")
            .insert(registros)
            .execute()
        )

        if respuesta.data:
            return True, "Registro guardado correctamente"

        return False, "No se pudieron guardar los hábitos"

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
    
def obtener_estadisticas_usuario(id_usuario):
    try:
        respuesta = (
            supabase
            .table("registro_habito")
            .select("id_registro, id_usuario, id_habito, fecha, realizado")
            .eq("id_usuario", id_usuario)
            .eq("realizado", True)
            .execute()
        )

        registros = respuesta.data if respuesta.data else []

        fechas = set()

        for r in registros:
            fecha = r.get("fecha")

            if fecha:
                fechas.add(str(fecha).split("T")[0])

        dias_registrados = len(fechas)
        habitos_cumplidos = len(registros)

        return {
            "dias_registrados": dias_registrados,
            "habitos_cumplidos": habitos_cumplidos,
        }

    except Exception as error:
        print("Error al obtener estadísticas del usuario:", error)

        return {
            "dias_registrados": 0,
            "habitos_cumplidos": 0,
        }

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
    
def guardar_configuracion_recordatorio(
    id_usuario,
    correo,
    recordatorios_activos,
    frecuencia,
    intervalo_horas
):
    try:
        ahora = datetime.now()

        datos = {
            "id_usuario": id_usuario,
            "correo": correo,
            "recordatorios_activos": recordatorios_activos,
            "frecuencia": frecuencia,
            "intervalo_horas": intervalo_horas,
            "fecha_actualizacion": ahora.isoformat(),
        }

        if recordatorios_activos:
            datos["proximo_envio"] = (ahora + timedelta(hours=intervalo_horas)).isoformat()
        else:
            datos["proximo_envio"] = None

        respuesta = (
            supabase
            .table("usuario_recordatorio")
            .upsert(datos, on_conflict="id_usuario")
            .execute()
        )

        print("Configuración de recordatorio guardada:", respuesta.data)

        if respuesta.data:
            return True, "Configuración de recordatorio guardada"

        return False, "No se pudo guardar la configuración"

    except Exception as error:
        print("Error al guardar configuración de recordatorio:", error)
        return False, f"Error al guardar configuración: {error}"
    
    
def cambiar_estado_recordatorio(id_usuario, correo, recordatorios_activos):
    try:
        from datetime import datetime, timedelta

        # Buscar configuración actual del usuario
        respuesta_actual = (
            supabase
            .table("usuario_recordatorio")
            .select("frecuencia, intervalo_horas")
            .eq("id_usuario", id_usuario)
            .limit(1)
            .execute()
        )

        if respuesta_actual.data:
            config_actual = respuesta_actual.data[0]
            frecuencia_actual = config_actual.get("frecuencia", "2 veces al día")
            intervalo_horas_actual = config_actual.get("intervalo_horas", 12)
        else:
            frecuencia_actual = "2 veces al día"
            intervalo_horas_actual = 12

        ahora = datetime.now()

        datos = {
            "id_usuario": id_usuario,
            "correo": correo,
            "recordatorios_activos": recordatorios_activos,
            "frecuencia": frecuencia_actual,
            "intervalo_horas": intervalo_horas_actual,
            "fecha_actualizacion": ahora.isoformat(),
        }

        if recordatorios_activos:
            datos["proximo_envio"] = (ahora + timedelta(hours=intervalo_horas_actual)).isoformat()
        else:
            datos["proximo_envio"] = None

        respuesta = (
            supabase
            .table("usuario_recordatorio")
            .upsert(datos, on_conflict="id_usuario")
            .execute()
        )

        print("Estado de recordatorio actualizado:", respuesta.data)

        return True, "Estado de recordatorio actualizado"

    except Exception as error:
        print("Error al cambiar estado de recordatorio:", error)
        return False, f"Error al cambiar estado: {error}"
    
    
def obtener_configuracion_recordatorio(id_usuario):
    try:
        respuesta = (
            supabase
            .table("usuario_recordatorio")
            .select("recordatorios_activos, frecuencia, intervalo_horas")
            .eq("id_usuario", id_usuario)
            .limit(1)
            .execute()
        )

        if respuesta.data:
            return respuesta.data[0]

        return None

    except Exception as error:
        print("Error al obtener configuración de recordatorio:", error)
        return None
    
def programar_correo_prueba(id_usuario):
    try:
        respuesta = (
            supabase
            .table("usuario_recordatorio")
            .update({
                "recordatorios_activos": True,
                "proximo_envio": "2000-01-01T00:00:00+00:00"
            })
            .eq("id_usuario", id_usuario)
            .execute()
        )

        print("Correo de prueba programado:", respuesta.data)

        return True, "Correo de prueba programado. Llegará cuando se ejecute el cron."

    except Exception as error:
        print("Error al programar correo de prueba:", error)
        return False, f"Error al programar correo de prueba: {error}"