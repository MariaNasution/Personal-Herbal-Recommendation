# FILE: backend-nusacare/rag_module.py

import json
from langchain_community.vectorstores import Chroma
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.llms import HuggingFacePipeline
from transformers import pipeline

# Import services
from gemma_model import load_fine_tuned_gemma
from rag_initialization import CHROMA_CLIENT, COLLECTION_NAME
from ipfs_service import upload_to_ipfs
from blockchain_service import record_cid, w3


# Load model HF biasa (TANPA WRAPPER)
GEMMA_MODEL, GEMMA_TOKENIZER = load_fine_tuned_gemma()

# Siapkan pipeline untuk LangChain
gemma_pipeline = pipeline(
    "text-generation",
    model=GEMMA_MODEL,
    tokenizer=GEMMA_TOKENIZER,
    max_new_tokens=512,
    temperature=0.7,
    do_sample=True,
    return_full_text=False,
)

# LangChain-compatible LLM
GEMMA_LLM = HuggingFacePipeline(pipeline=gemma_pipeline)


def generate_recommendation(context_data: dict) -> str:
    print("[RAG] generate_recommendation START")

    if not GEMMA_LLM:
        return "Sistem RAG belum siap. Model Gemma gagal dimuat."

    query_text = context_data.get("patient_query", "")
    patient_name = context_data.get("patient_name", "Pasien")
    medical_history = ", ".join(context_data.get("medical_history", []))
    patient_address = context_data.get("patient_address", "UNKNOWN_PATIENT")

    # ===============================
    # Vector Store & Retriever
    # ===============================
    vectorstore = Chroma(
        client=CHROMA_CLIENT,
        collection_name=COLLECTION_NAME
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    print("[RAG] RETRIEVER READY")

    # ===============================
    # Prompt Template (FINAL)
    # ===============================
    prompt_template = """
Anda adalah asisten medis Nusacare.

INFORMASI PASIEN:
Nama: {patient_name}
Riwayat Medis: {medical_history}

KELUHAN PASIEN:
{query_text}

KONTEKS HERBAL:
{context}

Berikan jawaban terstruktur:
1. Analisis Singkat
2. Langkah Perawatan Diri
3. Saran Herbal (Nama, Manfaat, Dosis aman)
"""

    QA_CHAIN_PROMPT = PromptTemplate(
        input_variables=["patient_name", "medical_history", "query_text", "context"],
        template=prompt_template,
    )

 # ===============================
    # Prompt Template dengan Variabel Parsial
    # ===============================
    # Kita memasukkan data pasien langsung ke template sebelum masuk ke chain
    # Ini memecah error "Extra inputs are not permitted"
    
    final_prompt = QA_CHAIN_PROMPT.partial(
        patient_name=patient_name,
        medical_history=medical_history,
        query_text=query_text
    )

    # ===============================
    # RAG Pipeline (VERSI FINAL)
    # ===============================
    qa_chain = RetrievalQA.from_chain_type(
        llm=GEMMA_LLM,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=False,
        chain_type_kwargs={
            "prompt": final_prompt  # Gunakan prompt yang sudah di-partial
        },
    )

    print("[RAG] CALLING LLM")
    # RetrievalQA sekarang hanya menerima 'query', variabel lain sudah aman di dalam prompt
    response = qa_chain.invoke({"query": query_text})
    print("[RAG] LLM FINISHED")

    recommendation_text = response.get("result", "Tidak ada rekomendasi.")

    # ===============================
    # IPFS & Blockchain
    # ===============================
    try:
        timestamp = w3.eth.get_block("latest")["timestamp"]
    except Exception:
        timestamp = "Simulasi Time"

    recommendation_data_for_ipfs = {
        "patient_address": patient_address,
        "query": query_text,
        "recommendation_text": recommendation_text,
        "timestamp": timestamp,
    }

    recommendation_cid = upload_to_ipfs(
        recommendation_data_for_ipfs,
        is_encrypted=True
    )

    if recommendation_cid:
        tx_hash = record_cid(
            user_address=patient_address,
            cid=recommendation_cid,
            data_type="RECOMMENDATION_RESULT",
        )
        print(f"[BLOCKCHAIN] CID {recommendation_cid} dicatat: {tx_hash}")

    return recommendation_text
