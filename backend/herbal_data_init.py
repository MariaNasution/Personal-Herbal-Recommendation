# herbal_data_init.py

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
import os

# --- Data Awal Basis Pengetahuan Herbal (Ganti dengan data riil Anda nanti) ---
HERBAL_KNOWLEDGE = [
    {"name": "Jahe", "manfaat": "Meredakan mual, muntah, dan menghangatkan badan.", "kontraindikasi": "Tidak disarankan bagi penderita tukak lambung akut atau yang mengonsumsi pengencer darah.", "keywords": "mual, flu, hangat"},
    {"name": "Kunyit", "manfaat": "Anti-inflamasi, membantu meredakan nyeri sendi dan asam lambung ringan.", "kontraindikasi": "Dosis tinggi dapat mengganggu pengencer darah dan batu empedu.", "keywords": "radang, sendi, asam lambung, anti-inflamasi"},
    {"name": "Minyak Kelapa", "manfaat": "Membantu menstabilkan gula darah dan sumber energi cepat.", "kontraindikasi": "Tinggi lemak jenuh, batasi konsumsi untuk pasien kolesterol tinggi.", "keywords": "gula darah, diet, energi, kolesterol"}
]

COLLECTION_NAME = "herbal_knowledge_collection"
MODEL_NAME = "all-MiniLM-L6-v2" # Model embedding (Bab 3.4.3)

def initialize_chroma_db():
    """Memuat data herbal ke Chroma DB."""
    
    print("Initializing Chroma DB in ./chroma_db_store...")
    client = chromadb.PersistentClient(path="./chroma_db_store")
    
    # 1. Pilih Model Embedding menggunakan adapter ChromaDB
    embedding_function = SentenceTransformerEmbeddingFunction(model_name=MODEL_NAME)
    print("Embedding Model Initialized.")
        
    # 2. Buat atau Dapatkan Collection
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_function
    )

    if collection.count() == 0:
        print(f"Memuat {len(HERBAL_KNOWLEDGE)} dokumen herbal baru...")
        
        documents = []
        metadatas = []
        ids = []
        
        for i, item in enumerate(HERBAL_KNOWLEDGE):
            doc_text = f"Nama: {item['name']}. Manfaat: {item['manfaat']}. Kontraindikasi: {item['kontraindikasi']}. Kata Kunci: {item['keywords']}"
            documents.append(doc_text)
            metadatas.append({"name": item['name'], "keywords": item['keywords']})
            ids.append(f"doc_{i}")

        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        print("Pemuatan data selesai. Database Chroma siap digunakan.")
    else:
        print(f"Chroma DB sudah berisi {collection.count()} dokumen. Melewatkan pemuatan data.")
        
    return client

if __name__ == "__main__":
    initialize_chroma_db()