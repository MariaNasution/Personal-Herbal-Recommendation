# FILE: backend-nusacare/ipfs_service.py

import json
import requests
import os
from typing import Union, Dict # Untuk kompatibilitas tipe hint

# Asumsi Anda menggunakan IPFS Gateway lokal
IPFS_API_URL = os.getenv("IPFS_API_URL", "http://127.0.0.1:5001/api/v0") 

# [cite_start]Simulasikan Enkripsi AES 256 bit (sesuai kebutuhan non-fungsional [cite: 391])
def encrypt_data(data: dict) -> bytes:
    """Simulasi enkripsi data sebelum diunggah ke IPFS."""
    data_str = json.dumps(data)
    # WARNING: Implementasi enkripsi AES 256 bit NYATA harus ditambahkan di sini
    return data_str.encode('utf-8') 

def upload_to_ipfs(data: dict, is_encrypted: bool = False) -> str:
    """Mengunggah data ke IPFS dan mengembalikan CID."""
    try:
        if is_encrypted:
            content = encrypt_data(data)
        else:
            content = json.dumps(data).encode('utf-8')

        files = {'file': content}
        response = requests.post(f"{IPFS_API_URL}/add", files=files)
        
        if response.status_code == 200:
            result = response.json()
            return result['Hash'] # CID (Content Identifier)
        else:
            raise Exception(f"Gagal unggah ke IPFS: {response.text}")
    
    except Exception as e:
        print(f"Error IPFS: {e}")
        return ""

def retrieve_from_ipfs(cid: str) -> Union[Dict, None]:
    """Mengunduh (retrieve) data dari IPFS berdasarkan CID."""
    try:
        response = requests.post(f"{IPFS_API_URL}/cat?arg={cid}")
        if response.status_code == 200:
            # Di sini seharusnya ada logika dekripsi
            return json.loads(response.text)
        else:
            return None
    except Exception as e:
        print(f"Error retrieve IPFS: {e}")
        return None