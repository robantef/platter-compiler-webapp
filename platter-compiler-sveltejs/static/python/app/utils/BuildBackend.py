"""
This should run all automation process to build the backend.
Insert more automations in the futures so we don't have a 
lot of files and automation and configurations. 
"""

from app.utils.FormatParser import main as format_parser
from app.utils.FormatASTParser import main as format_ast_parser

if __name__ == "__main__":
    # Build regular parser
    format_parser()
    print("\n" + "="*80)
    print("Skipped AST Builder, disconnected generator")
    # Build AST parser
    # print("\n" + "="*80)
    # print("Building AST Parser...")
    # print("="*80 + "\n")
    # format_ast_parser()