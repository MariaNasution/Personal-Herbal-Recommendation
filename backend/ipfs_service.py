import json
import requests
import os
from typing import Union, Dict

# Alamat API IPFS Desktop standar
IPFS_API_URL = os.getenv("IPFS_API_URL", "http://127.0.0.1:5001/api/v0")

def encrypt_data(data: dict) -> bytes:
    """Simulasi enkripsi data sebelum diunggah ke IPFS (Sesuai Bab 3.4.1)."""
    data_str = json.dumps(data)
    # Gunakan encoding utf-8 untuk konversi teks ke bytes sebelum diupload
    return data_str.encode('utf-8') 

def upload_to_ipfs(data, is_encrypted=True):
    try:
        # Konversi data ke bytes
        content = json.dumps(data).encode('utf-8')
        
        # IPFS mewajibkan file dikirim via POST multipart/form-data
        files = {
            'file': ('data.json', content, 'application/json')
        }
        
        # Panggil endpoint /add milik IPFS Desktop
        response = requests.post(f"{IPFS_API_URL}/add", files=files, timeout=10)
        
        if response.status_code == 200:
            return response.json().get('Hash')
        else:
            print(f"⚠️ IPFS RPC Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Koneksi IPFS Gagal: {e}")
        return None

def retrieve_from_ipfs(cid: str) -> Union[Dict, None]:
    """Mengunduh (retrieve) data dari IPFS berdasarkan CID."""
    if not cid:
        return None
    try:
        # Menggunakan endpoint /cat untuk mengambil isi file
        response = requests.post(f"{IPFS_API_URL}/cat?arg={cid}", timeout=10)
        if response.status_code == 200:
            return json.loads(response.text)
        return None
    except Exception as e:
        print(f"❌ Error retrieve IPFS: {e}")
        return None