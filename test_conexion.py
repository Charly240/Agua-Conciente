from database import supabase

def probar_consulta():
    print("--- INICIANDO PRUEBA DE CONEXIÓN Y DATOS ---")
    
    try:
        # 1. Probar lectura de la tabla de usuarios
        print("\n1. Consultando tabla 'usuario'...")
        res_usuarios = supabase.table("usuario").select("*").execute()
        print(f"Resultado 'usuario': {res_usuarios.data}")
        
        if len(res_usuarios.data) == 0:
            print("⚠️ AVISO: La tabla 'usuario' regresó una lista vacía [].")
            print("Esto suele significar que Row Level Security (RLS) está activo en Supabase y te falta agregar una 'Policy' de lectura.")
        else:
            print(f"✅ Éxito: Se encontraron {len(res_usuarios.data)} usuarios.")

        # 2. Probar buscar un usuario específico (Carlos)
        print("\n2. Buscando específicamente a 'carlos'...")
        res_carlos = supabase.table("usuario").select("*").or_("correo.ilike.carlos,nombre.ilike.carlos").execute()
        print(f"Resultado búsqueda 'carlos': {res_carlos.data}")

        # 3. Probar lectura de otra tabla
        print("\n3. Consultando tabla 'recomendacion'...")
        res_recom = supabase.table("recomendacion").select("*").execute()
        print(f"Resultado 'recomendacion': {res_recom.data}")

    except Exception as error:
        print("\n❌ ERROR CRÍTICO:")
        print(error)

if __name__ == "__main__":
    probar_consulta()