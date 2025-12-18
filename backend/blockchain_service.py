# FILE: backend-nusacare/blockchain_service.py (FINAL & LENGKAP - Memperbaiki Checksum Error)

from web3 import Web3
import os
import json 
from typing import Union, Dict 

# --- KONFIGURASI BLOCKCHAIN & OBJEK W3 ---

# 1. Ambil URL Provider dari .env
WEB3_PROVIDER_URL = os.getenv("ETH_PUBLIC_INFURA_URL", "http://127.0.0.1:8545")

# DEKLARASIKAN OBJEK W3 di awal agar to_checksum_address bisa digunakan
w3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER_URL)) 

# 2. Ambil Alamat Kontrak dari .env (Tanpa .lower() agar bisa di-checksum)
raw_contract_address = os.getenv(
    "ETH_PUBLIC_CONTRACT_ADDRESS", 
    "0xC8B1De510ba7Eea1774201094EAfe8ceca9548Fa" # Alamat default (sebaiknya dalam format checksum)
)
# KONVERSI KE CHECKSUM UNTUK MENGHINDARI ERROR web3.py
try:
    SMART_CONTRACT_ADDRESS = w3.to_checksum_address(raw_contract_address)
except ValueError:
    # Jika alamat mentah (raw) tidak valid sama sekali
    SMART_CONTRACT_ADDRESS = raw_contract_address
    print("WARNING: Alamat kontrak dari .env tidak dapat dikonversi ke Checksum.")


# 3. Ambil Path File ABI dari .env
ABI_PATH = os.getenv("ETH_STORAGE_CONTRACT_PATH", "./build/contracts/StorageHealthRecords.json")


# ABI (Application Binary Interface)
try:
    with open(ABI_PATH, 'r') as f:
        abi_data = json.load(f)
        CONTRACT_ABI = abi_data.get('abi', abi_data) 
except FileNotFoundError:
    CONTRACT_ABI = [] 
    print(f"WARNING: File ABI tidak ditemukan di {ABI_PATH}. Transaksi Blockchain akan gagal.")


# DEFINISIKAN VARIABEL KONFIGURASI TAMBAHAN
# Mengambil Private Key dari .env 
BACKEND_PRIVATE_KEY = os.getenv("ETH_PRIVATE_KEY", "0xSimulasiKey") 

# Alamat Service Wallet untuk mengirim transaksi. Konversi ke Checksum.
raw_service_address = os.getenv(
    "BACKEND_SERVICE_ADDRESS", 
    w3.eth.accounts[0] if w3.is_connected() and w3.eth.accounts else "0x0000000000000000000000000000000000000000"
)
try:
    BACKEND_SERVICE_ADDRESS = w3.to_checksum_address(raw_service_address)
except ValueError:
    BACKEND_SERVICE_ADDRESS = raw_service_address
    print("WARNING: Alamat layanan backend tidak dapat dikonversi ke Checksum.")


# INISIALISASI KONTRAK
try:
    if CONTRACT_ABI: 
        # Inisialisasi menggunakan alamat yang sudah di-checksum
        CONTRACT_INSTANCE = w3.eth.contract(address=SMART_CONTRACT_ADDRESS, abi=CONTRACT_ABI)
    else:
        CONTRACT_INSTANCE = None
        raise Exception(f"ABI file not found at {ABI_PATH}.") 
        
except Exception as e:
    print(f"ERROR: Gagal inisialisasi Kontrak Smart: {e}")
    CONTRACT_INSTANCE = None


# --- Fungsi send_transaction, record_cid, dan check_access tetap SAMA ---

def send_transaction(txn) -> str:
    """Fungsi pembantu untuk menandatangani dan mengirim transaksi."""
    if not w3.is_connected() or not CONTRACT_INSTANCE:
        raise Exception("Blockchain tidak terhubung atau Kontrak tidak terinisialisasi.")
    
    # Menambahkan Nonce dan Gas Estimate
    txn['nonce'] = w3.eth.get_transaction_count(BACKEND_SERVICE_ADDRESS)
    
    # Tanda tangan transaksi menggunakan Private Key Backend
    signed_txn = w3.eth.account.sign_transaction(txn, private_key=BACKEND_PRIVATE_KEY)
    
    # Kirim transaksi
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    
    # Tunggu konfirmasi (opsional, tapi disarankan untuk audit trail)
    w3.eth.wait_for_transaction_receipt(tx_hash)
    
    return tx_hash.hex()


def record_cid(user_address: str, cid: str, data_type: str) -> str:
    """Mencatat CID ke Blockchain (Audit Trail)."""
    if not CONTRACT_INSTANCE: return "ERROR: Kontrak tidak siap."
    
    try:
        # Memanggil recordData pada Smart Contract
        txn = CONTRACT_INSTANCE.functions.recordData(
            user_address, 
            cid, 
            data_type
        ).build_transaction({
            'from': BACKEND_SERVICE_ADDRESS, 
            'gas': 300000 
        })
        
        return send_transaction(txn)
        
    except Exception as e:
        print(f"Error mencatat CID ke Blockchain: {e}")
        return f"ERROR_TX: {str(e)}"


def check_access(patient_address: str, caller_address: str, action: str) -> bool:
    """Memeriksa hak akses melalui Smart Contract."""
    if not CONTRACT_INSTANCE: return False
    
    try:
        # Memanggil fungsi view checkPermission pada Smart Contract
        has_permission = CONTRACT_INSTANCE.functions.checkPermission(
            patient_address, 
            caller_address, 
            action
        ).call()
        return has_permission
    except Exception as e:
        print(f"Error cek akses: {e}")
        return False