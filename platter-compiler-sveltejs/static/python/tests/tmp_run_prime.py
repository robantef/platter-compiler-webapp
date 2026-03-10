from app.lexer.lexer import Lexer
from app.parser.parser_program import Parser
from app.semantic_analyzer.ast.ast_parser_program import ASTParser
from app.semantic_analyzer.semantic_analyzer import SemanticAnalyzer
from app.intermediate_code.ir_generator import IRGenerator
from app.intermediate_code.optimizer_manager import OptimizerManager, OptimizationLevel
from app.intermediate_code.ir_interpreter import run_tac

source = """piece of i, n = 29;
flag of isPrime = up;

prepare piece of print(flag of isPrime) {
    check(isPrime == up) {
        bill(tochars(n) + " is prime");
    } instead {
        bill(tochars(n) + " is not prime");
    }
    serve 0;
}

start() {
    check(n <= 1) {
        isPrime = down;
    } instead {
        i = 2;
        repeat(i < n) {
            check(n % i == 0) {
                isPrime = down;
                i = n;
            } instead {
                i = i + 1;
            }
        }
    }

    print(isPrime);
}
"""

tokens = Lexer(source).tokenize()
Parser(tokens).parse_program()
ast = ASTParser(tokens).parse_program()
_, err = SemanticAnalyzer().analyze(ast)
print("HAS_ERRORS:", err.has_errors(), flush=True)
if err.has_errors():
    print(err.format_errors(include_warnings=True, include_info=False), flush=True)
else:
    tac, _ = IRGenerator().generate(ast)
    optimized_tac = OptimizerManager(OptimizationLevel.STANDARD).optimize_tac(tac)
    result = run_tac(optimized_tac)
    print("INTERPRETER_SUCCESS:", result.get("success"), flush=True)
    print("INTERPRETER_OUTPUT:", result.get("output", ""), flush=True)
    print("INTERPRETER_ERROR:", result.get("error", ""), flush=True)
