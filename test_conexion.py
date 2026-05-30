from database import supabase

try:
    response = supabase.table("recomendacion").select("*").execute()

    print("Conexión exitosa con Supabase")
    print(response.data)

except Exception as error:
    print("Error al conectar con Supabase:")
    print(error)