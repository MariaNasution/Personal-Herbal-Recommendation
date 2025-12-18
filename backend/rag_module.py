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
    if not GEMMA_MODEL:
        return "Sistem RAG belum siap. Model Gemma gagal dimuat."

    query_text = context_data["patient_query"]

    # Vector Store & Retriever
    vectorstore = Chroma(client=CHROMA_CLIENT, collection_name=COLLECTION_NAME)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    # Prompt TANPA tanda vital
    prompt_template = """
    Anda adalah asisten medis Nusacare. Gunakan 'INFORMASI PASIEN' dan 'KONTEKS HERBAL' di bawah ini
    untuk menjawab 'KELUHAN PASIEN' secara personal.

    INFORMASI PASIEN:
    Nama: {patient_name}
    Riwayat Medis: {medical_history}

    KELUHAN PASIEN:
    {query_text}

    KONTEKS HERBAL (Gunakan hanya informasi dari sini sebagai referensi faktual):
    {context}

    Berikan output:
    1. Analisis Singkat
    2. Langkah Perawatan Diri
    3. Saran Herbal (Nama, Manfaat, Dosis aman)
    """

    full_prompt = prompt_template.format(
        patient_name=context_data["patient_name"],
        medical_history=", ".join(context_data["medical_history"]),
        query_text=query_text,
        context="{context}",
    )

    QA_CHAIN_PROMPT = PromptTemplate.from_template(full_prompt)

    # RAG Pipeline
    qa_chain = RetrievalQA.from_chain_type(
        llm=GEMMA_LLM,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": QA_CHAIN_PROMPT},
    )

    # Eksekusi RAG
    response = qa_chain.invoke({"query": query_text})
    recommendation_text = response["result"]

    # IPFS & Blockchain
    patient_address = context_data.get("patient_address", "UNKNOWN_PATIENT")

    try:
        timestamp = w3.eth.get_block("latest")["timestamp"]
    except:
        timestamp = "Simulasi Time"

    recommendation_data_for_ipfs = {
        "patient_address": patient_address,
        "query": query_text,
        "recommendation_text": recommendation_text,
        "timestamp": timestamp,
    }

    recommendation_cid = upload_to_ipfs(
        recommendation_data_for_ipfs, is_encrypted=True
    )

    if recommendation_cid:
        tx_hash = record_cid(
            user_address=patient_address,
            cid=recommendation_cid,
            data_type="RECOMMENDATION_RESULT",
        )
        print(f"CID {recommendation_cid} dicatat di Blockchain: {tx_hash}")

    return recommendation_text
