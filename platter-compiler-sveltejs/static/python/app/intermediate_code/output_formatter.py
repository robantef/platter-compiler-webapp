"""
Output Formatter for Intermediate Representation

This module provides utilities to format and display TAC and Quadruples
in various output formats (text, HTML, JSON, etc.)
"""

from typing import List, Dict, Any
import json
from .tac import TACInstruction
from .quadruple import QuadrupleTable, Quadruple


class IRFormatter:
    """Formats IR output in various formats"""
    
    def __init__(self):
        self.indent = "    "
    
    def format_tac_text(self, instructions: List[TACInstruction]) -> str:
        """Format TAC instructions as plain text"""
        lines = []
        lines.append("=" * 60)
        lines.append("THREE ADDRESS CODE (TAC)")
        lines.append("=" * 60)
        lines.append("")
        
        for i, instr in enumerate(instructions):
            lines.append(f"{i:4d}: {str(instr)}")
        
        lines.append("")
        lines.append(f"Total instructions: {len(instructions)}")
        lines.append("=" * 60)
        
        return "\n".join(lines)
    
    def format_quadruples_text(self, quad_table: QuadrupleTable) -> str:
        """Format quadruples as plain text"""
        lines = []
        lines.append("=" * 60)
        lines.append("QUADRUPLES")
        lines.append("=" * 60)
        lines.append("")
        lines.append(f"{'Index':<6} {'Operator':<12} {'Arg1':<12} {'Arg2':<12} {'Result':<12}")
        lines.append("-" * 60)
        
        for i, quad in enumerate(quad_table.quadruples):
            op = quad.operator
            a1 = quad.arg1 if quad.arg1 is not None else "-"
            a2 = quad.arg2 if quad.arg2 is not None else "-"
            res = quad.result if quad.result is not None else "-"
            
            lines.append(f"{i:<6} {op:<12} {a1:<12} {a2:<12} {res:<12}")
        
        lines.append("")
        lines.append(f"Total quadruples: {len(quad_table)}")
        lines.append("=" * 60)
        
        return "\n".join(lines)
    
    def format_quadruples_readable(self, quad_table: QuadrupleTable) -> str:
        """Format quadruples in human-readable form"""
        lines = []
        lines.append("=" * 60)
        lines.append("QUADRUPLES (Readable Format)")
        lines.append("=" * 60)
        lines.append("")
        
        for i, quad in enumerate(quad_table.quadruples):
            lines.append(f"{i:4d}: {quad.to_string()}")
        
        lines.append("")
        lines.append(f"Total quadruples: {len(quad_table)}")
        lines.append("=" * 60)
        
        return "\n".join(lines)
    
    def format_both_text(self, instructions: List[TACInstruction], 
                        quad_table: QuadrupleTable) -> str:
        """Format both TAC and Quadruples side by side"""
        tac_text = self.format_tac_text(instructions)
        quad_text = self.format_quadruples_text(quad_table)
        
        return tac_text + "\n\n" + quad_text
    
    def format_tac_json(self, instructions: List[TACInstruction]) -> str:
        """Format TAC instructions as JSON"""
        data = []
        for i, instr in enumerate(instructions):
            entry = {
                "index": i,
                "type": instr.op_type,
                "instruction": str(instr)
            }
            
            # Add specific fields based on instruction type
            if hasattr(instr, 'result'):
                entry["result"] = instr.result
            if hasattr(instr, 'arg1'):
                entry["arg1"] = instr.arg1
            if hasattr(instr, 'arg2'):
                entry["arg2"] = getattr(instr, 'arg2', None)
            if hasattr(instr, 'operator'):
                entry["operator"] = instr.operator
            if hasattr(instr, 'label'):
                entry["label"] = instr.label
            
            data.append(entry)
        
        return json.dumps({"tac": data}, indent=2)
    
    def format_quadruples_json(self, quad_table: QuadrupleTable) -> str:
        """Format quadruples as JSON"""
        data = []
        for i, quad in enumerate(quad_table.quadruples):
            entry = {
                "index": i,
                "operator": quad.operator,
                "arg1": quad.arg1,
                "arg2": quad.arg2,
                "result": quad.result,
                "readable": quad.to_string()
            }
            data.append(entry)
        
        return json.dumps({"quadruples": data}, indent=2)
    
    def format_both_json(self, instructions: List[TACInstruction],
                        quad_table: QuadrupleTable) -> str:
        """Format both TAC and Quadruples as JSON"""
        tac_data = json.loads(self.format_tac_json(instructions))
        quad_data = json.loads(self.format_quadruples_json(quad_table))
        
        combined = {
            "intermediate_representation": {
                "three_address_code": tac_data["tac"],
                "quadruples": quad_data["quadruples"]
            }
        }
        
        return json.dumps(combined, indent=2)
    
    def format_html(self, instructions: List[TACInstruction],
                   quad_table: QuadrupleTable) -> str:
        """Format IR as HTML"""
        html = []
        html.append("<!DOCTYPE html>")
        html.append("<html><head>")
        html.append("<title>Platter IR - Intermediate Representation</title>")
        html.append("<style>")
        html.append("body { font-family: 'Courier New', monospace; margin: 20px; }")
        html.append("h1 { color: #333; }")
        html.append("h2 { color: #666; margin-top: 30px; }")
        html.append("table { border-collapse: collapse; width: 100%; margin: 10px 0; }")
        html.append("th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }")
        html.append("th { background-color: #4CAF50; color: white; }")
        html.append("tr:nth-child(even) { background-color: #f2f2f2; }")
        html.append(".tac-instruction { background-color: #fff3cd; }")
        html.append("</style>")
        html.append("</head><body>")
        
        html.append("<h1>Platter Intermediate Representation</h1>")
        
        # TAC section
        html.append("<h2>Three Address Code (TAC)</h2>")
        html.append("<table>")
        html.append("<tr><th>Index</th><th>Instruction</th></tr>")
        for i, instr in enumerate(instructions):
            html.append(f"<tr><td>{i}</td><td>{str(instr)}</td></tr>")
        html.append("</table>")
        
        # Quadruples section
        html.append("<h2>Quadruples</h2>")
        html.append("<table>")
        html.append("<tr><th>Index</th><th>Operator</th><th>Arg1</th><th>Arg2</th><th>Result</th><th>Readable</th></tr>")
        for i, quad in enumerate(quad_table.quadruples):
            op = quad.operator
            a1 = quad.arg1 if quad.arg1 is not None else "-"
            a2 = quad.arg2 if quad.arg2 is not None else "-"
            res = quad.result if quad.result is not None else "-"
            readable = quad.to_string()
            html.append(f"<tr><td>{i}</td><td>{op}</td><td>{a1}</td><td>{a2}</td><td>{res}</td><td>{readable}</td></tr>")
        html.append("</table>")
        
        html.append("</body></html>")
        
        return "\n".join(html)
    
    def format_statistics(self, instructions: List[TACInstruction],
                         quad_table: QuadrupleTable) -> str:
        """Generate statistics about the IR"""
        lines = []
        lines.append("=" * 60)
        lines.append("INTERMEDIATE REPRESENTATION STATISTICS")
        lines.append("=" * 60)
        lines.append("")
        
        # Count instruction types
        tac_types: Dict[str, int] = {}
        for instr in instructions:
            op_type = instr.op_type
            tac_types[op_type] = tac_types.get(op_type, 0) + 1
        
        lines.append("TAC Instruction Types:")
        for op_type, count in sorted(tac_types.items()):
            lines.append(f"  {op_type:<20} : {count:>5}")
        
        lines.append("")
        lines.append(f"Total TAC Instructions: {len(instructions)}")
        lines.append(f"Total Quadruples: {len(quad_table)}")
        
        # Count operators in quadruples
        quad_ops: Dict[str, int] = {}
        for quad in quad_table.quadruples:
            op = quad.operator
            quad_ops[op] = quad_ops.get(op, 0) + 1
        
        lines.append("")
        lines.append("Quadruple Operators:")
        for op, count in sorted(quad_ops.items()):
            lines.append(f"  {op:<20} : {count:>5}")
        
        lines.append("")
        lines.append("=" * 60)
        
        return "\n".join(lines)


# Convenience functions
def format_tac(instructions: List[TACInstruction], format_type: str = "text") -> str:
    """
    Format TAC instructions.
    
    Args:
        instructions: List of TAC instructions
        format_type: "text", "json", or "html"
    """
    formatter = IRFormatter()
    if format_type == "json":
        return formatter.format_tac_json(instructions)
    else:
        return formatter.format_tac_text(instructions)


def format_quadruples(quad_table: QuadrupleTable, format_type: str = "text",
                     readable: bool = True) -> str:
    """
    Format quadruples.
    
    Args:
        quad_table: Quadruple table
        format_type: "text", "json", or "html"
        readable: If True, use readable format; otherwise use tabular
    """
    formatter = IRFormatter()
    if format_type == "json":
        return formatter.format_quadruples_json(quad_table)
    elif readable:
        return formatter.format_quadruples_readable(quad_table)
    else:
        return formatter.format_quadruples_text(quad_table)


def format_ir(instructions: List[TACInstruction], quad_table: QuadrupleTable,
             format_type: str = "text") -> str:
    """
    Format both TAC and Quadruples.
    
    Args:
        instructions: List of TAC instructions
        quad_table: Quadruple table
        format_type: "text", "json", or "html"
    """
    formatter = IRFormatter()
    if format_type == "json":
        return formatter.format_both_json(instructions, quad_table)
    elif format_type == "html":
        return formatter.format_html(instructions, quad_table)
    else:
        return formatter.format_both_text(instructions, quad_table)
