import unittest
import os
import logging
from pathlib import Path
from app.lexer.lexer import Lexer
from app.semantic_analyzer.ast.ast_parser_program import ASTParser

# Suppress debug logs from parser during tests
logging.getLogger().setLevel(logging.CRITICAL)


class TestASTValidPrograms(unittest.TestCase):
    """Test that all valid .platter files generate AST successfully without errors."""
    
    # Class variable to store failed tests
    failed_tests = []
    
    @classmethod
    def setUpClass(cls):
        """Set up paths for valid test programs."""
        tests_dir = Path(__file__).parent
        cls.valid_tests_dir = tests_dir / 'syntax_programs' / 'valid_tests'
        cls.platter_files = sorted(cls.valid_tests_dir.glob('*.platter'))
        
        if not cls.platter_files:
            raise ValueError(f"No .platter files found in {cls.valid_tests_dir}")
    
    def parse_ast_file(self, file_path: Path) -> tuple[bool, str]:
        """
        Parse a .platter file to AST and return (success, message).
        
        Args:
            file_path: Path to the .platter file
            
        Returns:
            (True, "AST Generated Successfully") if AST generation succeeds
            (False, error_message) if AST generation fails
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            # Lexical analysis
            lexer = Lexer(code)
            tokens = lexer.tokenize()
            
            # AST generation
            ast_parser = ASTParser(tokens)
            ast = ast_parser.parse_program()
            
            return True, "AST Generated Successfully"
            
        except Exception as e:
            return False, str(e)
    
    def test_all_valid_programs(self):
        """Test all .platter files in valid_tests directory."""
        passed_count = 0
        
        for platter_file in self.platter_files:
            with self.subTest(file=platter_file.name):
                success, message = self.parse_ast_file(platter_file)
                
                try:
                    self.assertTrue(
                        success,
                        f"Expected AST generation to succeed, but got: {message}"
                    )
                    passed_count += 1
                    
                except AssertionError as e:
                    # Store failed test information
                    with open(platter_file, 'r', encoding='utf-8') as f:
                        code = f.read()
                    
                    TestASTValidPrograms.failed_tests.append({
                        'file': platter_file.name,
                        'code': code,
                        'error': message
                    })
                    raise
    
    @classmethod
    def tearDownClass(cls):
        """Write detailed summary to file after all tests complete."""
        total_tests = len(cls.platter_files)
        passed_count = total_tests - len(cls.failed_tests)
        
        # Get the syntax_programs directory
        results_file = cls.valid_tests_dir.parent / 'tests_ast_valid_results.txt'
        
        # Write results to file
        with open(results_file, 'w', encoding='utf-8') as f:
            f.write(f"{'='*70}\n")
            f.write(f"AST GENERATION TEST SUMMARY: {passed_count}/{total_tests} tests passed\n")
            f.write(f"{'='*70}\n\n")
            
            if cls.failed_tests:
                f.write(f"FAILURES: These files should generate AST successfully but failed\n\n")
                for fail in cls.failed_tests:
                    f.write(f"[FAILED] {fail['file']}\n")
                    f.write(f"-" * 70 + "\n")
                    f.write(f"Code:\n")
                    # Print code with line numbers
                    code_lines = fail['code'].split('\n')
                    for idx, line in enumerate(code_lines, 1):
                        f.write(f"  {idx:3d} | {line}\n")
                    f.write(f"\nError Output:\n{fail['error']}\n")
                    f.write(f"{'='*70}\n\n")
            else:
                f.write("✓ All valid programs generated AST successfully!\n")
        
        # Also print summary to console
        print(f"\n{'='*70}")
        print(f"AST GENERATION TEST SUMMARY: {passed_count}/{total_tests} tests passed")
        print(f"{'='*70}")
        if cls.failed_tests:
            print(f"\n⚠ {len(cls.failed_tests)} file(s) failed to generate AST:")
            for fail in cls.failed_tests:
                print(f"  - {fail['file']}")
        print(f"\nDetailed results written to: {results_file}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
