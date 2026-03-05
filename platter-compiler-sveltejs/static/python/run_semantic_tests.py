import sys
import logging
sys.path.insert(0, 'd:\\Repositories\\platter-compiler-webapp\\platter-compiler-sveltejs\\static\\python')

# Suppress debug logs
logging.getLogger().setLevel(logging.CRITICAL)

import unittest
from tests.ga_semantic_analyzer import TestSemanticAnalyzer

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSemanticAnalyzer)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"Total tests: {result.testsRun}")
    print(f"Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failed: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print('='*60)
