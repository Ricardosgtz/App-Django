import os
import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "clients")

def upload_file_to_supabase(file, client_id):
    """
    Sube una imagen al bucket Supabase usando HTTP directo (modo compatible con Render).
    """
    try:
        # 🔥 CAMBIO: Agregar "clientes/" antes del client_id
        file_path = f"clientes/{client_id}/{file.name}"

        # URL de subida al bucket
        upload_url = f"{SUPABASE_URL}/storage/v1/object/{SUPABASE_BUCKET}/{file_path}"

        headers = {
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "apikey": SUPABASE_KEY,
            "Content-Type": file.content_type or "application/octet-stream",
        }

        # Usar PUT para evitar conflictos
        response = requests.put(upload_url, headers=headers, data=file.read())

        if response.status_code not in [200, 201]:
            raise Exception(f"Error {response.status_code}: {response.text}")

        # URL pública
        public_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{file_path}"
        return public_url

    except Exception as e:
        print("❌ Error al subir imagen a Supabase:", e)
        raise e