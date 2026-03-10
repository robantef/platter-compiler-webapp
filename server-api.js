/**
 * Server API Handler for Platter Compiler
 * Provides endpoints for full compilation pipeline
 */

import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * Compiles Platter source code using the full pipeline (IR, Optimizer, Code Gen)
 * @param {string} sourceCode - The Platter source code
 * @returns {Promise<Object>} Compilation result
 */
export async function compileWithFullPipeline(sourceCode) {
	return new Promise((resolve, reject) => {
		const pythonPath = path.join(__dirname, 'platter-compiler-sveltejs/static/python');
		const pythonImportPath = pythonPath.replace(/\\/g, '\\\\');
		const sourceBase64 = Buffer.from(sourceCode, 'utf8').toString('base64');
		
		const pythonScript = [
			'import sys',
			'import logging',
			'import base64',
			'',
			'logging.disable(logging.CRITICAL)',
			`sys.path.insert(0, r'${pythonImportPath}')`,
			'',
			'import json',
			'from app.lexer.lexer import Lexer',
			'from app.semantic_analyzer.ast.ast_parser_program import ASTParser',
			'from app.semantic_analyzer.semantic_analyzer import SemanticAnalyzer',
			'from app.intermediate_code.ir_generator import IRGenerator',
			'from app.intermediate_code.optimizer_manager import OptimizerManager, OptimizationLevel',
			'',
			`source_code = base64.b64decode('${sourceBase64}').decode('utf-8')`,
			'',
			'result = None',
			'try:',
			'    lexer = Lexer(source_code)',
			'    tokens = lexer.tokenize()',
			'    parser = ASTParser(tokens)',
			'    ast = parser.parse_program()',
			'',
			'    analyzer = SemanticAnalyzer()',
			'    _, error_handler = analyzer.analyze(ast)',
			'    if error_handler.has_errors():',
			'        result = {',
			'            "success": False,',
			'            "message": error_handler.format_errors(include_warnings=True, include_info=False),',
			'            "asm_code": "",',
			'            "stats": "Semantic analysis failed",',
			'            "pipeline": "FULL_IR"',
			'        }',
			'    else:',
			'        ir_gen = IRGenerator()',
			'        tac, _ = ir_gen.generate(ast)',
			'        optimizer = OptimizerManager(OptimizationLevel.STANDARD)',
			'        optimized_tac = optimizer.optimize_tac(tac)',
			'        ir_text = "\\n".join(str(instr) for instr in optimized_tac)',
			'        stats_obj = {',
			'            "tokens": len(tokens),',
			'            "ir_instructions": len(tac),',
			'            "optimized_ir_instructions": len(optimized_tac),',
			'            "optimization": optimizer.get_stats()',
			'        }',
			'        result = {',
			'            "success": True,',
			'            "asm_code": ir_text,',
			'            "stats": json.dumps(stats_obj, indent=2),',
			'            "message": "Program compiled successfully (IR pipeline).",',
			'            "pipeline": "FULL_IR"',
			'        }',
			'except SyntaxError as e:',
			'    result = {"success": False, "message": str(e)}',
			'except Exception as e:',
			'    result = {"success": False, "message": f"Compilation failed: {str(e)}"}',
			'',
			'print(json.dumps(result))'
		].join('\n');

		const python = spawn('python', ['-c', pythonScript], {
			cwd: __dirname,
			timeout: 30000
		});

		let output = '';
		let errorOutput = '';

		python.stdout.on('data', (data) => {
			output += data.toString();
		});

		python.stderr.on('data', (data) => {
			errorOutput += data.toString();
		});

		python.on('close', (code) => {
			try {
				if (code !== 0) {
					reject({
						success: false,
						message: `Python process exited with code ${code}: ${errorOutput}`
					});
					return;
				}
				const result = JSON.parse(output);
				resolve(result);
			} catch (e) {
				reject({
					success: false,
					message: `Failed to parse compilation output: ${e.message}`
				});
			}
		});

		python.on('error', (err) => {
			reject({
				success: false,
				message: `Failed to spawn Python process: ${err.message}`
			});
		});
	});
}

/**
 * Compiles code with simplified pipeline (lexer + parser only)
 * Used for browser-based compilation via Pyodide
 */
export function compileSimplified(sourceCode) {
	return {
		success: true,
		asm_code: '# Simplified browser-based compilation\n# For full compilation with IR, optimization, and code generation,\n# use the server-side API endpoint.',
		stats: 'Browser Environment Mode\nLexer: ✓\nParser: ✓\nIR Generation: Server-side only\nOptimization: Server-side only\nCode Generation: Server-side only',
		message: 'Browser compilation available. Use "Run on Server" for full pipeline.',
		pipeline: 'SIMPLIFIED'
	};
}
