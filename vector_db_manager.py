"""
vector_db_manager.py

Initializes local ChromaDB. Ingests mock Synopsys power telemetry, 
embeds it using HuggingFace MiniLM, and maps it to specific RTL chunks.
"""

import json
import chromadb
from sentence_transformers import SentenceTransformer

DB_PATH = "./chroma_store"

def init_db_and_ingest():
    print("[*] Initializing SentenceTransformer (all-MiniLM-L6-v2)...")
    # Using a fast, lightweight embedding model for telemetry logs
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    
    print("[*] Initializing ChromaDB client...")
    client = chromadb.PersistentClient(path=DB_PATH)
    
    # Drop existing collection for clean run
    try:
        client.delete_collection(name="rtl_telemetry_vectors")
    except:
        pass
        
    collection = client.create_collection(name="rtl_telemetry_vectors")
    
    # Mock Synopsys Power Compiler Telemetry
    telemetry_logs = [
        {
            "id": "log_001",
            "module_ref": "payload_0",
            "log_text": "Warning: High dynamic power consumption detected on register bank. Toggle rate exceeds 90% on clk_net without adequate clock gating constraints."
        },
        {
            "id": "log_002",
            "module_ref": "clk_div",
            "log_text": "Info: Setup time violation margin tight (-0.02ns). Consider buffering."
        }
    ]
    
    print("[*] Embedding physical design telemetry...")
    texts = [log["log_text"] for log in telemetry_logs]
    embeddings = embedding_model.encode(texts).tolist()
    
    # Map logs strictly to their AST module boundaries via metadata
    metadatas = [{"module_target": log["module_ref"]} for log in telemetry_logs]
    ids = [log["id"] for log in telemetry_logs]
    
    collection.add(
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas,
        ids=ids
    )
    
    print(f"[+] Ingested {len(texts)} telemetry vectors into ChromaDB.")

if __name__ == "__main__":
    init_db_and_ingest()
