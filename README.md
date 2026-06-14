# Hardware-Aware AST RAG Pipeline (HARP)

**HARP** is an experimental, retrieval-augmented generation (RAG) pipeline designed to bridge the semantic gap between raw RTL (Register-Transfer Level) code and downstream EDA tool telemetry (e.g., Synopsys Power Compiler logs, PrimeTime timing reports). 

Standard LLMs fundamentally misunderstand hardware; they treat structural Verilog as procedural software. HARP solves this by enforcing a strict Abstract Syntax Tree (AST) boundary constraint during the embedding phase, ensuring that vector retrieval is highly localized to specific hardware modules, power domains, and clock trees.

## Architecture Overview

The pipeline executes a deterministic, three-stage physical data journey:

1. **AST Slicing (The Parser):** Slices raw `.v` or `.sv` files into modular, context-isolated chunks based on structural boundaries (`module`/`endmodule`).
2. **Telemetry Embedding (The Database):** Ingests raw physical synthesis logs (power, timing, DRC violations) and embeds them into a vector space. These vectors are strictly mapped to their corresponding RTL module chunks via metadata constraints in ChromaDB.
3. **RTL Synthesis (The LLM Generator):** Retrieves the precise structural chunk and its associated EDA bottleneck, piping them into a generative model to synthesize cycle-accurate, structurally valid RTL patches (e.g., localized clock gating, combinational logic flattening).

## Tech Stack

* **Core Logic:** Python 3.10+
* **Vector Engine:** ChromaDB
* **Embeddings:** HuggingFace `all-MiniLM-L6-v2` (SentenceTransformers)
* **LLM Inference:** HuggingFace `transformers`, PyTorch
* **Data Processing:** NumPy, Pandas

## Quick Start

1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`
3. Execute the pipeline:
   ```bash
   python ast_chunker.py          # Generate RTL structural boundaries
   python vector_db_manager.py    # Vectorize and map EDA telemetry
   python rtl_inference.py        # Synthesize RTL patches
