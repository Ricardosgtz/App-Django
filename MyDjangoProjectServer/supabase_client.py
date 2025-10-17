import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Cargar variables del entorno
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "clients")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def upload_file_to_supabase(file, client_id):
    """
    Sube un archivo al bucket de Supabase y devuelve su URL pública.
    """
    try:
        file_path = f"clients/{client_id}/{file.name}"
        file_bytes = file.read()

        # Subir archivo
        res = supabase.storage.from_(SUPABASE_BUCKET).upload(file_path, file_bytes, {"upsert": True})
        if res.get("error"):
            raise Exception(res["error"]["message"])

        # Obtener URL pública
        public_url = supabase.storage.from_(SUPABASE_BUCKET).get_public_url(file_path)
        return public_url

    except Exception as e:
        print("❌ Error subiendo archivo a Supabase:", e)
        raise e
