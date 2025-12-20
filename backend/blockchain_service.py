# FILE: backend-nusacare/blockchain_service.py (FINAL & LENGKAP)

from web3 import Web3
import os
import json
from dotenv import load_dotenv  # TAMBAHKAN INI


load_dotenv() 

# ------------------------------------------------------------------
# KONFIGURASI WEB3
# ------------------------------------------------------------------
WEB3_PROVIDER_URL = os.getenv("ETH_PUBLIC_INFURA_URL", "http://127.0.0.1:8545")
w3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER_URL))

# ------------------------------------------------------------------
# SMART CONTRACT
# ------------------------------------------------------------------
RAW_CONTRACT_ADDRESS = os.getenv(
    "ETH_PUBLIC_CONTRACT_ADDRESS",
    "0xC8B1De510ba7Eea1774201094EAfe8ceca9548Fa"
)

SMART_CONTRACT_ADDRESS = w3.to_checksum_address(RAW_CONTRACT_ADDRESS)

ABI_PATH = os.getenv(
    "ETH_STORAGE_CONTRACT_PATH",
    "./build/contracts/StorageHealthRecords.json"
)

with open(ABI_PATH) as f:
    CONTRACT_ABI = json.load(f)["abi"]

CONTRACT_INSTANCE = w3.eth.contract(
    address=SMART_CONTRACT_ADDRESS,
    abi=CONTRACT_ABI
)

# ------------------------------------------------------------------
# SERVICE WALLET
# ------------------------------------------------------------------
BACKEND_PRIVATE_KEY = os.getenv("ETH_PRIVATE_KEY")
# Tambahkan pengecekan manual untuk memastikan key terbaca
if not BACKEND_PRIVATE_KEY:
    print("❌ CRITICAL ERROR: ETH_PRIVATE_KEY tidak terbaca dari .env!")
BACKEND_SERVICE_ADDRESS = w3.to_checksum_address(
    os.getenv("BACKEND_SERVICE_ADDRESS", w3.eth.accounts[0])
)

# ------------------------------------------------------------------
# TRANSACTION HELPER
# ------------------------------------------------------------------
def send_transaction(tx):
    tx["nonce"] = w3.eth.get_transaction_count(BACKEND_SERVICE_ADDRESS)
    signed = w3.eth.account.sign_transaction(tx, BACKEND_PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    w3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_hash.hex()

# ------------------------------------------------------------------
# RECORD CID (USER ADDRESS, BUKAN GANACHE DEFAULT)
# ------------------------------------------------------------------
def record_cid(user_address: str, cid: str, data_type: str):
    user_checksum = w3.to_checksum_address(user_address)

    tx = CONTRACT_INSTANCE.functions.recordData(
        user_checksum,
        cid,
        data_type
    ).build_transaction({
        "from": BACKEND_SERVICE_ADDRESS,
        "gas": 300000
    })

    return send_transaction(tx)

# backend/blockchain_service.py

def record_herbal_to_blockchain(sender_address, herbal_name, cid):
    try:
        # Gunakan fungsi registerUser yang ada di contract Anda
        txn = CONTRACT_INSTANCE.functions.registerUser(
            sender_address,       # senderAddress
            herbal_name,          # name (Nama Herbal)
            "2025-12-19",         # birthDate (Dummy)
            cid,                  # homeAddress (KITA SIMPAN CID DISINI)
            "enc_key_ipfs",       # aesKey
            "pass_key_ipfs",      # passKey
            "Doctor"              # Role (Wajib "Doctor" agar diterima require contract)
        ).build_transaction({
            'from': BACKEND_SERVICE_ADDRESS,
            'nonce': w3.eth.get_transaction_count(BACKEND_SERVICE_ADDRESS),
            'gas': 1000000,
            'gasPrice': w3.eth.gas_price
        })
        
        signed_txn = w3.eth.account.sign_transaction(txn, private_key=BACKEND_PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        return w3.to_hex(tx_hash)
    except Exception as e:
        print(f"❌ Detail Error Blockchain: {e}")
        raise e

# ------------------------------------------------------------------
# CHECK ACCESS
# ------------------------------------------------------------------
def check_access(patient_address: str, caller_address: str, action: str) -> bool:
    return CONTRACT_INSTANCE.functions.checkPermission(
        w3.to_checksum_address(patient_address),
        w3.to_checksum_address(caller_address),
        action
    ).call()
