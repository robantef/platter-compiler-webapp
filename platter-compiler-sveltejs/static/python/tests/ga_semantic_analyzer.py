import unittest
import os
import logging
from pathlib import Path
from app.lexer.lexer import Lexer
from app.semantic_analyzer.ast.ast_parser_program import ASTParser
from app.semantic_analyzer.semantic_analyzer import SemanticAnalyzer
from app.parser.parser_program import Parser

# Suppress debug logs from parser during tests
logging.getLogger().setLevel(logging.CRITICAL)


class TestSemanticAnalyzer(unittest.TestCase):
    """Test semantic analysis by comparing output with expected results."""
    
    # Class variable to store test results
    test_results = []
    
    @classmethod
    def setUpClass(cls):
        """Set up paths for semantic test programs."""
        tests_dir = Path(__file__).parent
        cls.semantic_tests_dir = tests_dir / 'semantic_programs'
        cls.source_dir = cls.semantic_tests_dir / 'source_code'
        cls.expected_dir = cls.semantic_tests_dir / 'expected'
        
        # Get all .platter files from source_code directory
        cls.platter_files = sorted(cls.source_dir.glob('*.platter'))
        
        if not cls.platter_files:
            raise ValueError(f"No .platter files found in {cls.source_dir}")
    
    def run_semantic_analysis(self, file_path: Path) -> tuple[bool, str, str]:
        """
        Run semantic analysis on a .platter file and return results.
        
        Args:
            file_path: Path to the .platter file
            
        Returns:
            (success, actual_output, error_message) tuple
            - success: True if analysis completed (even with semantic errors)
            - actual_output: The semantic analysis output
            - error_message: Any exception message if analysis failed
            
        Run syntax analysis first. If it passes, run semantic analysis.
        Returns (success, actual_output, error_message)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()

            # Lexical analysis
            lexer = Lexer(code)
            tokens = lexer.tokenize()

            # --- Syntax analysis ---
            try:
                parser = Parser(tokens)
                parser.parse_program()
            except Exception as e:
                # Syntax error: return as output, skip semantic analysis
                return True, f"{str(e)}", ""

            # --- Semantic analysis ---
            ast_parser = ASTParser(tokens)
            ast = ast_parser.parse_program()
            analyzer = SemanticAnalyzer()
            symbol_table, error_handler = analyzer.analyze(ast)

            if error_handler.has_errors() or error_handler.has_warnings():
                actual_output = error_handler.format_errors(include_warnings=True, include_info=False)
            else:
                actual_output = "No semantic errors"

            return True, actual_output, ""

        except Exception as e:
            return False, "", str(e)
        
    def test_all_semantic_programs(self):
        """Test all .platter files in semantic_programs directory."""
        passed_count = 0
        
        for platter_file in self.platter_files:
            with self.subTest(file=platter_file.name):
                # Get expected output file
                expected_file = self.expected_dir / f"{platter_file.stem}.txt"
                
                if not expected_file.exists():
                    result_info = {
                        'file': platter_file.name,
                        'status': 'NO_EXPECTED',
                        'expected': None,
                        'actual': None,
                        'error': f"Expected file not found: {expected_file.name}"
                    }
                    TestSemanticAnalyzer.test_results.append(result_info)
                    self.fail(f"Expected file not found: {expected_file.name}")
                    continue
                
                # Read expected output
                with open(expected_file, 'r', encoding='utf-8') as f:
                    expected_output = f.read().strip()
                
                # Run semantic analysis
                success, actual_output, error_msg = self.run_semantic_analysis(platter_file)
                
                if not success:
                    result_info = {
                        'file': platter_file.name,
                        'status': 'FAILED',
                        'expected': expected_output,
                        'actual': None,
                        'error': error_msg
                    }
                    TestSemanticAnalyzer.test_results.append(result_info)
                    self.fail(f"Analysis failed with exception: {error_msg}")
                    continue
                
                # Compare outputs
                actual_output = actual_output.strip()
                
                if actual_output == expected_output:
                    result_info = {
                        'file': platter_file.name,
                        'status': 'PASSED',
                        'expected': expected_output,
                        'actual': actual_output,
                        'error': None
                    }
                    passed_count += 1
                else:
                    result_info = {
                        'file': platter_file.name,
                        'status': 'MISMATCH',
                        'expected': expected_output,
                        'actual': actual_output,
                        'error': "Output does not match expected"
                    }
                
                TestSemanticAnalyzer.test_results.append(result_info)
                
                # Assert for unittest
                self.assertEqual(
                    actual_output,
                    expected_output,
                    f"\nExpected:\n{expected_output}\n\nActual:\n{actual_output}"
                )
    
    @classmethod
    def tearDownClass(cls):
        """Write detailed summary to file after all tests complete."""
        total_tests = len(cls.platter_files)
        passed_count = sum(1 for r in cls.test_results if r['status'] == 'PASSED')
        
        # Write results to file
        results_file = cls.semantic_tests_dir / 'tests_semantic_results.txt'
        
        with open(results_file, 'w', encoding='utf-8') as f:
            f.write(f"{'='*70}\n")
            f.write(f"SEMANTIC ANALYSIS TEST SUMMARY: {passed_count}/{total_tests} tests passed\n")
            f.write(f"{'='*70}\n\n")
            
            # Passed tests
            passed_tests = [r for r in cls.test_results if r['status'] == 'PASSED']
            if passed_tests:
                f.write(f"PASSED TESTS ({len(passed_tests)}):\n")
                for result in passed_tests:
                    f.write(f"  ✓ {result['file']}\n")
                f.write(f"\n")
            
            # Failed/Mismatched tests
            failed_tests = [r for r in cls.test_results if r['status'] != 'PASSED']
            if failed_tests:
                f.write(f"FAILED TESTS ({len(failed_tests)}):\n\n")
                for result in failed_tests:
                    f.write(f"[{result['status']}] {result['file']}\n")
                    f.write(f"{'-'*70}\n")
                    
                    if result['status'] == 'MISMATCH':
                        f.write(f"Expected Output:\n{result['expected']}\n\n")
                        f.write(f"Actual Output:\n{result['actual']}\n\n")
                    elif result['status'] == 'FAILED':
                        f.write(f"Error:\n{result['error']}\n\n")
                    elif result['status'] == 'NO_EXPECTED':
                        f.write(f"Error:\n{result['error']}\n\n")
                    
                    f.write(f"{'='*70}\n\n")
            else:
                f.write("✓ All semantic analysis tests passed!\n")
        
        # Also print summary to console
        print(f"\n{'='*70}")
        print(f"SEMANTIC ANALYSIS TEST SUMMARY: {passed_count}/{total_tests} tests passed")
        print(f"{'='*70}")
        if failed_tests:
            print(f"\n⚠ {len(failed_tests)} test(s) failed:")
            for result in failed_tests:
                print(f"  - {result['file']} [{result['status']}]")
        else:
            print("✓ All semantic analysis tests passed!")
        print(f"\nDetailed results written to: {results_file}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
