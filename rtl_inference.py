"""
rtl_inference.py

Retrieves vectorized telemetry constraints and associated RTL chunks.
Passes them to a local LLM pipeline to synthesize structural hardware fixes.
"""

import json
import torch
import chromadb
from transformers import pipeline

DB_PATH = "./chroma_store"

def run_rtl_patch_synthesis():
    # 1. Setup DB Client and retrieve target context
    print("[*] Connecting to Vector Store...")
    client = chromadb.PersistentClient(path=DB_PATH)
    collection = client.get_collection(name="rtl_telemetry_vectors")
    
    # Simulating a user query regarding power optimization
    query = "Find dynamic power bottlenecks and suggest ICG insertion."
    print(f"[*] Querying Vector DB: '{query}'")
    
    results = collection.query(
        query_texts=[query],
        n_results=1
    )
    
    retrieved_log = results['documents'][0][0]
    target_module = results['metadatas'][0][0]['module_target']
    print(f"[-] Retrieved Telemetry: {retrieved_log}")
    print(f"[-] Target RTL Module: {target_module}")
    
    # 2. Load the structural AST chunk
    with open("data/ast_chunks.json", "r") as f:
        ast_data = json.load(f)
    
    raw_rtl = ast_data.get(target_module, {}).get("source_code", "")
    
    # 3. Setup LLM (Using a lightweight mock model to simulate inference)
    print("\n[*] Loading LLM Pipeline (CPU optimized for mock run)...")
    # In a real environment, this would be CodeLlama or a fine-tuned hardware model.
    # We use a tiny model here to ensure the script runs quickly on any machine.
    generator = pipeline(
        "text-generation", 
        model="Qwen/Qwen2.5-0.5B-Instruct", 
        device_map="auto" 
    )
    
    prompt = (
        "You are a Senior ASIC Engineer. Fix the following Verilog module based on the EDA tool log.\n\n"
        f"EDA Telemetry Log:\n{retrieved_log}\n\n"
        f"Original Verilog (AST Node: {target_module}):\n{raw_rtl}\n\n"
        "Task: Insert an Integrated Clock Gating (ICG) cell to resolve the high toggle rate. "
        "Output ONLY the fixed Verilog code.\n"
    )
    
    print("\n[*] Synthesizing RTL Fix...")
    
    # Generate the patch
    output = generator(prompt, max_new_tokens=150, temperature=0.1, return_full_text=False)
    
    print("\n" + "="*50)
    print("         SYNTHESIZED RTL PATCH")
    print("="*50)
    print(output[0]['generated_text'].strip())
    print("="*50)

if __name__ == "__main__":
    run_rtl_patch_synthesis()
