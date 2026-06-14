"""
ast_chunker.py

Mocks a Verilog AST parser. Instead of a full lexer/parser tree, this heuristic 
uses state-tracking and regex to extract structural module boundaries.
"""

import re
import json
import os

def parse_verilog_to_ast_chunks(verilog_text: str) -> dict:
    """
    Scans raw Verilog and extracts module definitions.
    Returns a dictionary mapping module names to their raw source chunk.
    """
    ast_chunks = {}
    
    # Heuristic regex to match: module <name> ... endmodule
    # Note: This is a structural bypass. Real AST parsing requires a full state machine.
    pattern = re.compile(r'\bmodule\s+([a-zA-Z0-9_]+)[\s\S]*?\bendmodule\b', re.MULTILINE)
    
    matches = pattern.finditer(verilog_text)
    
    for match in matches:
        module_name = match.group(1)
        module_body = match.group(0)
        ast_chunks[module_name] = {
            "type": "module",
            "source_code": module_body.strip()
        }
        
    return ast_chunks

if __name__ == "__main__":
    # Mock Verilog Payload
    mock_rtl = """
    module clk_div (input clk, output reg div_clk);
        always @(posedge clk) div_clk <= ~div_clk;
    endmodule

    // Structural payload targeting ID constraints
    module payload_0 (input clk, input rst, input [7:0] data_in, output reg [7:0] data_out);
        always @(posedge clk or posedge rst) begin
            if (rst) data_out <= 8'b0;
            else data_out <= data_in;
        end
    endmodule
    """
    
    print("[*] Initializing AST parsing heuristic...")
    parsed_tree = parse_verilog_to_ast_chunks(mock_rtl)
    
    # Dump to JSON for downstream DB ingestion
    os.makedirs("data", exist_ok=True)
    with open("data/ast_chunks.json", "w") as f:
        json.dump(parsed_tree, f, indent=4)
        
    print(f"[+] Successfully extracted {len(parsed_tree)} hardware modules.")
