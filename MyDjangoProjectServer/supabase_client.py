import os
import requests
import time
from pathlib import Path
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
        # 🔥 Generar nombre único similar a uniqid() de PHP
        nombre_original = file.name
        extension = Path(nombre_original).suffix  # Obtiene ".jpg", ".png", etc
        
        # Asegura extensión en minúsculas y evita nombres vacíos
        extension = extension.lower() if extension else '.jpg'
        
        # Genera nombre único estilo PHP uniqid(): "68ff05573d08e"
        nombre_unico = format(int(time.time() * 1000000) & 0xFFFFFFFFFFFF, 'x')
        
        # Nombre final: 68ff05573d08e.jpg
        nombre_archivo = f"{nombre_unico}{extension}"
        
        # Ruta completa: clientes/4/68ff05573d08e.jpg
        file_path = f"clientes/{client_id}/{nombre_archivo}"

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
        

def upload_comprobante_to_supabase(file, client_id):
    """
    📤 Sube un comprobante al bucket Supabase dentro de 'Comprobantes/<client_id>/'.
    """
    try:
        nombre_original = file.name
        extension = Path(nombre_original).suffix.lower() if Path(nombre_original).suffix else ".jpg"

        # 🔑 Genera nombre único
        nombre_unico = format(int(time.time() * 1000000) & 0xFFFFFFFFFFFF, 'x')
        nombre_archivo = f"{nombre_unico}{extension}"

        # 📂 Carpeta destino dentro del bucket clients
        file_path = f"Comprobantes/{client_id}/{nombre_archivo}"

        upload_url = f"{SUPABASE_URL}/storage/v1/object/{SUPABASE_BUCKET}/{file_path}"

        headers = {
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "apikey": SUPABASE_KEY,
            "Content-Type": file.content_type or "application/octet-stream",
        }

        # PUT para subir el archivo
        response = requests.put(upload_url, headers=headers, data=file.read())

        if response.status_code not in [200, 201]:
            raise Exception(f"Error {response.status_code}: {response.text}")

        # ✅ Retorna la URL pública
        public_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{file_path}"
        return public_url

    except Exception as e:
        print("❌ Error al subir comprobante:", e)
        raise e

