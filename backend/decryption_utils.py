# decryption_utils.py
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# Kunci AES (key_hex) berasal dari address user pada Blockchain
# IV (Initialization Vector) berasal dari file .env: AES_IV=d22c4c5f36c63a9f4ab656c989e5bfe5

def decrypt_data_aes_256_cbc(encrypted_data_b64, key_hex, iv):
    """
    Melakukan dekripsi AES-256-CBC terhadap data medis.
    
    Args:
        encrypted_data_b64 (str): Konten file terenkripsi dari IPFS (dalam format Base64).
        key_hex (str): Kunci AES (32 bytes / 256 bits) dalam format HEX, dari address user.
        iv (bytes): Initialization Vector (IV) (16 bytes / 128 bits).
        
    Returns:
        str: Data yang sudah didekripsi (plaintext).
    """
    try:
        # 1. Konversi Kunci dan Data
        # Kunci harus 32 byte. Ubah dari 64 karakter Hex menjadi bytes.
        key = bytes.fromhex(key_hex)
        
        # Data terenkripsi di-decode dari Base64 (sesuai cara Node.js menyimpannya)
        encrypted_data = base64.b64decode(encrypted_data_b64)

        # 2. Inisialisasi Cipher (Menggunakan mode CBC sesuai konfigurasi AES_ALGORITHM)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        
        # 3. Dekripsi dan Unpad
        # Data yang didekripsi kemudian di-unpad (misalnya PKCS7)
        decrypted_padded_data = cipher.decrypt(encrypted_data)
        decrypted_data = unpad(decrypted_padded_data, AES.block_size)
        
        return decrypted_data.decode('utf-8')
    
    except ValueError as ve:
        # Menangkap error jika kunci salah ukuran, IV salah, atau padding tidak valid
        return f"DECRYPTION_FAILED: Pastikan Kunci (Key) dan IV benar. Error: {ve}"
    except Exception as e:
        return f"DECRYPTION_ERROR: {e}"