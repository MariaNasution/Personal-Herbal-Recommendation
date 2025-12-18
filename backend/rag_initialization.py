# FILE: backend-nusacare/rag_initialization.py (Untuk inisialisasi Chroma DB)

import chromadb
# Asumsikan Anda menginstal library embedding dari HuggingFace, misalnya sentence-transformers
from sentence_transformers import SentenceTransformer 
from ipfs_service import upload_to_ipfs # Modul IPFS Anda

# Inisialisasi Klien Chroma dan Model Embedding
CHROMA_CLIENT = chromadb.Client()
EMBEDDING_MODEL = SentenceTransformer('all-MiniLM-L6-v2') # 
COLLECTION_NAME = "herbal_knowledge"

def initialize_herbal_knowledge(data_herbal_mentah: list[dict]):
    """Memproses data, menyimpan embedding di Chroma."""
    
    # 1. Simpan File Mentah di IPFS (Data Integrity)
    # Anda akan mencatat CID ke Blockchain (smart contract) [cite: 540]
    # (Logika Blockchain/Smart Contract akan ada di modul terpisah)

    # 2. Pembersihan & Normalisasi Data (sesuai Bab 3.4.3) [cite: 566]
    # ... (logika pembersihan) ...

    # 3. Pembentukan Embedding [cite: 572]
    texts = [d['text'] for d in data_herbal_mentah]
    embeddings = EMBEDDING_MODEL.encode(texts).tolist()

    # 4. Simpan ke Chroma DB [cite: 577]
    collection = CHROMA_CLIENT.get_or_create_collection(name=COLLECTION_NAME)
    collection.add(
        embeddings=embeddings,
        documents=texts,
        metadatas=data_herbal_mentah, # Menyimpan metadata penting [cite: 579]
        ids=[f"doc_{i}" for i in range(len(texts))]
    )
    print("Basis Pengetahuan Herbal berhasil diinisialisasi di Chroma.")

# Panggil fungsi ini sekali saat memulai layanan atau saat data herbal baru diunggah.