import chromadb
import uuid
from chromadb.utils import embedding_functions

# 1. Inisialisasi Model Embedding (Sesuai Bab 3.4.3)
huggingface_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name='all-MiniLM-L6-v2'
)

# 2. Hubungkan ke folder chroma_db_store Anda
# Ini memastikan data herbal yang diinput Dokter tersimpan secara persisten
CHROMA_CLIENT = chromadb.PersistentClient(path="./chroma_db_store")
COLLECTION_NAME = "herbal_knowledge"

def add_to_chroma(herbal_data: dict):
    """
    Menambahkan data herbal terstruktur dari Dokter Herbal ke Vector Store.
    """
    collection = CHROMA_CLIENT.get_or_create_collection(
        name=COLLECTION_NAME, 
        embedding_function=huggingface_ef
    )

    # Susun konten naratif untuk proses RAG (Retrieve)
    text_content = (
        f"Tanaman: {herbal_data['name']}. "
        f"Manfaat: {herbal_data['benefit']}. "
        f"Dosis: {herbal_data['dosage']}. "
        f"Kontraindikasi: {herbal_data.get('contraindication', 'Tidak ada')}."
    )

    # Simpan ke Chroma DB dengan metadata lengkap
    collection.add(
        documents=[text_content],
        metadatas=[{
            "name": herbal_data['name'], 
            "source": "Expert_Input",
            "wallet": herbal_data.get('herbalist_wallet', 'unknown')
        }],
        ids=[f"herbal_{uuid.uuid4().hex}"] # ID unik untuk setiap entry
    )
    print(f"✅ [CHROMA] Data {herbal_data['name']} berhasil di-embed ke chroma_db_store.")