# FILE: backend-nusacare/gemma_model.py (VERSI KUANTISASI 4-BIT)

from transformers import AutoModelForCausalLM, AutoTokenizer
# Hapus atau nonaktifkan import PEFT jika Anda masih menggunakan model dasar saja
# from peft import PeftModel, PeftConfig 

# Tambahkan import yang diperlukan untuk Kuantisasi
from transformers import BitsAndBytesConfig
import torch # Diperlukan untuk mendefinisikan tipe data (dtype)

BASE_MODEL_ID = "google/gemma-2b" 
# LORA_ADAPTER_PATH = "./lora_adapters/gemma_herbal_adapter" 

def load_fine_tuned_gemma():
    """Memuat model Gemma Dasar dalam mode Kuantisasi 4-bit (Sangat Hemat RAM)."""
    try:
        print("Memuat Gemma 3 (4-bit Kuantisasi)...")
        
        # --- 1. DEFINISI KONFIGURASI KUANTISASI ---
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4", 
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=torch.bfloat16 # Atau torch.float16 jika bfloat16 tidak didukung
        )
        
        # 2. Muat Model Dasar dengan konfigurasi Kuantisasi
        tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_ID)
        
        base_model = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL_ID,
            # Argumen penting untuk mengaktifkan 4-bit kuantisasi:
            quantization_config=bnb_config,
            # Tentukan tipe data untuk menghindari memuat bobot asli yang besar
            torch_dtype=torch.bfloat16, 
            device_map="auto" # Memetakan bobot model ke GPU/CPU secara otomatis
        )
        
        # --- JIKA ANDA INGIN MENGEMBALIKAN FUNGSI LORA: ---
        # Jika Anda sudah memiliki file adapter LoRA, Anda dapat menggabungkannya
        # model = PeftModel.from_pretrained(base_model, LORA_ADAPTER_PATH)
        # return model, tokenizer
        
        print("Model Gemma (4-bit) berhasil dimuat.")
        return base_model, tokenizer
    
    except Exception as e:
        print(f"Gagal memuat model Gemma: {e}")
        return None, None