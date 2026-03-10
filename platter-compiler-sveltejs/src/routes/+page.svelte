<script lang="ts">
	// Restored functionality: bind editor, call backend, populate lexer table, and show terminal messages
	import {
		check,
		copy,
		copy1,
		darkmode,
		darkmode1,
		darkBg,
		lightBg,
		editor,
		editor1,
		errorIcon,
		errors,
		errors1,
		favicon,
		lightmode,
		logo,
		newFile,
		newFile1,
		openFile,
		openFile1,
		refresh,
		refresh1,
		saveFile,
		saveFile1,
		synSemLexIcon,
		synSemLexIcon1,
		table,
		warning
	} from '$lib';

	import { onMount, onDestroy } from 'svelte';
	import {
		loadScript,
		loadCSS,
		readFileAsText,
		saveContent,
		copyToClipboard
	} from '$lib/utils/browser';

	export let data;

	// Logger Service for Google Apps Script webhook
	const WEBHOOK_URL = 'https://script.google.com/macros/s/AKfycbwkXRRIlnkZI2z5bXT08Lswe504TalqtJcA13CtbMZcgoH3EhYfWtJBlD4ql_hg9q4eWg/exec';
	const BATCH_DELAY = 10000; // 10 seconds

	let logBatch: any[] = [];
	let logTimer: NodeJS.Timeout | null = null;

	function addToLogBatch(logData: {
		user_id?: string;
		source_code: string;
		terminal_output: string;
		status: string;
		language: string;
		duration_ms: number;
	}) {
		logBatch.push(logData);

		// Clear existing timer
		if (logTimer) {
			clearTimeout(logTimer);
		}

		// Set new timer to send logs after 10 seconds of inactivity
		logTimer = setTimeout(() => {
			sendLogBatch();
		}, BATCH_DELAY);
	}

	async function sendLogBatch() {
		if (logBatch.length === 0) return;

		const logsToSend = [...logBatch];
		logBatch = [];

		try {
			await fetch(WEBHOOK_URL, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(logsToSend),
				mode: 'no-cors' // Required for Google Apps Script
			});
			console.log('Logs sent successfully:', logsToSend.length);
		} catch (error) {
			console.error('Failed to send logs:', error);
			// Re-add to batch if failed (optional)
			// logBatch.unshift(...logsToSend);
		}
	}

	// Send any remaining logs when component is destroyed
	onDestroy(() => {
		if (logTimer) {
			clearTimeout(logTimer);
		}
		if (logBatch.length > 0) {
			sendLogBatch();
		}
	});

	// Generate unique session ID for tracking
	function generateSessionId(): string {
		const timestamp = Date.now();
		// Create a simple hash from timestamp using base36 and add some randomness
		const hash = (timestamp + Math.random() * 1000).toString(36).substring(2, 9);
		return `user_${hash}`;
	}

	let sessionId = generateSessionId();

	// Version tracking
	let appVersion = '1.0.0';
	async function fetchVersion() {
		try {
			const response = await fetch(`${data.basePath}/version.json`);
			const versionData = await response.json();
			appVersion = `${versionData.major}.${versionData.minor}.${versionData.patch}`;
		} catch (err) {
			console.warn('Failed to fetch version:', err);
		}
	}

	let theme: 'dark' | 'light' = 'dark';
	let activeTab: 'lexical' | 'syntax' | 'semantic' = 'lexical';

	let codeInput = `sip of x = 42.2;
sip of y = 3.67;
##
chars[] of names = ["Hello Platter", "Raph", "Jieco"];
piece[][] of nums = [
	[12, 21, 2],
    [32, 2, 12]
];
##
table of yz = [
	piece  of x;
    sip of xyz;
];

prepare sip of sips() { check(topiece(y) > topiece(x)) { serve x;} instead {serve y;} }

prepare piece of pieces() {
	 serve topiece(x) + 32 / 323;
     
}

start() {
	piece of z = topiece(topiece(sips()) + pieces());
	bill(tochars(z));
    serve z;
}`;

	type Token = { type: string; value: string; line: number; col: number };
	const lexerRows: Array<{ lexeme: string; token: string }> = [];
	let tokens: Token[] = [];
	let isAnalyzing = false;

	// Pyodide integration
	let pyodide: any = null;
	let pyodideLoading = false;
	let pyodideReady = false;

	// CodeMirror integration
	let textareaEl: HTMLTextAreaElement | null = null;
	let cmInstance: any = null;
	let errorMarkers: any[] = []; // Track CodeMirror text markers for error highlighting
	let handleGlobalCtrlEnter: ((event: KeyboardEvent) => void) | null = null;
	const CTRL_ENTER_HINT_SEEN_KEY = 'platter_ctrl_enter_hint_seen_v1';

	function showFirstVisitCtrlEnterHint() {
		if (typeof window === 'undefined') return;
		try {
			if (window.localStorage.getItem(CTRL_ENTER_HINT_SEEN_KEY) === '1') return;
			window.alert('Ctrl+Enter to run TAC and interpreter');
			window.localStorage.setItem(CTRL_ENTER_HINT_SEEN_KEY, '1');
		} catch {
			// Ignore storage restrictions (private mode, blocked storage, etc.)
		}
	}

	// file input for opening .platter files
	let fileInputEl: HTMLInputElement;

	function openFileDialog() {
		normalizeCurlyQuotes();
		fileInputEl?.click();
	}

	async function handleFileInput() {
		const f = fileInputEl?.files?.[0];
		if (!f) return;
		if (!f.name || !f.name.toLowerCase().endsWith('.platter')) {
			setTerminalError('Please select a .platter file');
			fileInputEl.value = '';
			return;
		}
		try {
			const text = await readFileAsText(f);
			codeInput = text;
			if (cmInstance && typeof cmInstance.setValue === 'function') {
				cmInstance.setValue(text);
			}
			setTerminalOk(`Opened ${f.name}`);
		} catch (err) {
			setTerminalError('Failed to read file');
		} finally {
			// reset input so the same file can be selected again
			fileInputEl.value = '';
		}
	}

	// Save current editor content as a .platter file. Uses the File System Access API when available,
	// otherwise falls back to a download via an anchor element.
	async function saveFileDialog() {
		normalizeCurlyQuotes();
		const content =
			cmInstance && typeof cmInstance.getValue === 'function' ? cmInstance.getValue() : codeInput;
		try {
			const msg = await saveContent(content, 'program.platter');
			setTerminalOk(msg);
		} catch (err) {
			const msg = err instanceof Error ? err.message : 'Save cancelled or failed';
			setTerminalError(`Save failed: ${msg}`);
		}
	}

	async function initPyodide() {
		if (pyodide || pyodideLoading) return;
		pyodideLoading = true;

		try {
			// Load Pyodide from CDN
			await loadScript('https://cdn.jsdelivr.net/pyodide/v0.25.0/full/pyodide.js');
			pyodide = await (window as any).loadPyodide({
				indexURL: 'https://cdn.jsdelivr.net/pyodide/v0.25.0/full/'
			});

		// Load Python files from static directory
		const pythonFiles = [
			'/python/app/__init__.py',
			'/python/app/lexer/__init__.py',
			'/python/app/lexer/token.py',
			'/python/app/lexer/protocol.py',
			'/python/app/lexer/base.py',
			'/python/app/lexer/keywords.py',
			'/python/app/lexer/identifiers.py',
			'/python/app/lexer/numericals.py',
			'/python/app/lexer/operators.py',
			'/python/app/lexer/char_com.py',
			'/python/app/lexer/lexer.py',
			'/python/app/parser/__init__.py',
			'/python/app/parser/error_handler.py',
			'/python/app/parser/predict_set.py',
			'/python/app/parser/parser_program.py',
			'/python/app/utils/FileHandler.py',
			'/python/app/parser/first_set.py',
			'/python/app/semantic_analyzer/__init__.py',
			'/python/app/semantic_analyzer/semantic_analyzer.py',
			'/python/app/semantic_analyzer/builtin_recipes.py',
			'/python/app/semantic_analyzer/ast/__init__.py',
			'/python/app/semantic_analyzer/ast/ast_nodes.py',
			'/python/app/semantic_analyzer/ast/ast_parser_program.py',
			'/python/app/semantic_analyzer/ast/ast_reader.py',
			'/python/app/semantic_analyzer/symbol_table/__init__.py',
			'/python/app/semantic_analyzer/symbol_table/types.py',
			'/python/app/semantic_analyzer/symbol_table/symbol_table.py',
			'/python/app/semantic_analyzer/symbol_table/symbol_table_builder.py',
			'/python/app/semantic_analyzer/symbol_table/symbol_table_output.py',
			'/python/app/semantic_analyzer/semantic_passes/__init__.py',
			'/python/app/semantic_analyzer/semantic_passes/error_handler.py',
			'/python/app/semantic_analyzer/semantic_passes/type_checker.py',
			'/python/app/semantic_analyzer/semantic_passes/scope_checker.py',
			'/python/app/semantic_analyzer/semantic_passes/control_flow_checker.py',
			'/python/app/semantic_analyzer/semantic_passes/function_checker.py',
			'/python/app/intermediate_code/__init__.py',
			'/python/app/intermediate_code/tac.py',
			'/python/app/intermediate_code/quadruple.py',
			'/python/app/intermediate_code/ir_generator.py',
			'/python/app/intermediate_code/output_formatter.py',
			'/python/app/intermediate_code/optimizer.py',
			'/python/app/intermediate_code/constant_folding.py',
			'/python/app/intermediate_code/propagation.py',
			'/python/app/intermediate_code/dead_code_elimination.py',
			'/python/app/intermediate_code/algebraic_simplification.py',
			'/python/app/intermediate_code/optimizer_manager.py',
			'/python/app/intermediate_code/ir_interpreter.py',
		];

		// Fetch and write Python files to Pyodide's virtual filesystem
		for (const file of pythonFiles) {
			const response = await fetch(`${data.basePath}${file}`);
			if (!response.ok) {
				throw new Error(`Failed to load Python file: ${file} (HTTP ${response.status})`);
			}
			const content = await response.text();
			const path = file.replace('/python/', '');
				
				// Create directory structure
				const dirs = path.split('/').slice(0, -1);
				let currentPath = '';
				for (const dir of dirs) {
					currentPath += (currentPath ? '/' : '') + dir;
					try {
						pyodide.FS.mkdir(currentPath);
					} catch (e) {
						// Directory might already exist
					}
				}
				
				// Write file
				pyodide.FS.writeFile(path, content);
			}

			pyodideReady = true;
			console.log('Pyodide initialized successfully');
		} catch (err) {
			console.error('Failed to initialize Pyodide:', err);
			setTerminalError('Failed to initialize Python runtime');
		} finally {
			pyodideLoading = false;
		}
	}

	onMount(async () => {
		showFirstVisitCtrlEnterHint();

		handleGlobalCtrlEnter = (event: KeyboardEvent) => {
			const isCtrlEnter = event.ctrlKey && event.key === 'Enter';
			if (!isCtrlEnter || event.defaultPrevented || event.repeat) return;
			event.preventDefault();
			analyzeSemantic(true);
		};
		window.addEventListener('keydown', handleGlobalCtrlEnter);

		try {
			// load CodeMirror assets from CDN (lightweight integration)
			await loadCSS('https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.13/codemirror.min.css');
			// optional: a theme could be loaded here, but our overrides will ensure transparency
			await loadScript(
				'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.13/codemirror.min.js'
			);
			if (textareaEl && (window as any).CodeMirror) {
				const CM = (window as any).CodeMirror;
				
				// Define Platter syntax highlighting mode
				CM.defineMode('platter', function() {
					const keywords: Record<string, boolean> = {
						// Conditionals
						'alt': true, 'check': true, 'instead': true,
						// Logical operators
						'and': true, 'or': true, 'not': true,
						// Loops
						'order': true, 'repeat': true, 'pass': true, 'menu': true,
						'choice': true, 'stop': true, 'next': true, 'usual': true,
						// Function definition
						'prepare': true, 'start': true,
						// Return
						'serve': true, 'of': true,
						// Struct
						'table': true
					};
					
					const builtinMethods: Record<string, boolean> = {
						'append': true, 'bill': true, 'copy': true, 'cut': true, 
						'fact': true, 'matches': true, 'size': true, 'sort': true, 
						'sqrt': true, 'tochars': true, 'topiece': true, 'take': true,
						'tosip': true, 'rand': true, 'pow': true, 'remove': true,
						'reverse': true, 'search': true
					};
					
					const dataTypes: Record<string, boolean> = {
						'chars': true, 'flag': true, 'piece': true, 'sip': true
					};
					
					const booleanLiterals: Record<string, boolean> = {
						'down': true, 'up': true
					};
					
					const operators = /^(?:\+|-|\*|\/|%|>|<|=|==|>=|<=|!=|\+=|-=|\*=|\/=|%=)/;
					const delimiters = /^(?:,|\{|\}|\(|\)|\[|\]|;|:)/;
					
					return {
						token: function(stream: any, state: any) {
							// Whitespace
							if (stream.eatSpace()) return null;
							
							// Comments
							// Single line comment: # followed by space
							if (stream.match(/^#\s.*/)) return 'comment';
							
							// Multi-line comment start: ##
							if (stream.match(/^##/)) {
								if (state.inComment) {
									// End multi-line comment
									state.inComment = false;
								} else {
									// Start multi-line comment
									state.inComment = true;
								}
								return 'comment';
							}
							
							// Inside multi-line comment
							if (state.inComment) {
								// Check if ## appears on this line to end comment
								if (stream.match(/^.*?(?=##)/)) {
									// Found ##, will be handled on next token call
									return 'comment';
								} else {
									// No ## found, consume rest of line
									stream.skipToEnd();
									return 'comment';
								}
							}
							
							// String literals
							if (stream.match(/^"(?:[^"\\]|\\.)*"/)) return 'string';
							if (stream.match(/^'(?:[^'\\]|\\.)*'/)) return 'string';
							
							// Escape sequences in strings
							if (stream.match(/\\[nt'"\\]/)) return 'string-2';
							
							// Numbers
							if (stream.match(/^-?\d+\.?\d*/)) return 'number';
							
							// Operators
							if (stream.match(operators)) return 'operator';
							
							// Delimiters
							if (stream.match(delimiters)) return 'punctuation';
							
							// Keywords, types, methods, etc.
							if (stream.match(/^[a-zA-Z_]\w*/)) {
								const word: string = stream.current();
								if (keywords[word]) return 'keyword';
								if (dataTypes[word]) return 'type';
								if (booleanLiterals[word]) return 'atom';
								if (builtinMethods[word]) return 'builtin';
								return 'variable';
							}
							
							stream.next();
							return null;
						},
						startState: function() {
							return { inComment: false };
						}
					};
				});
				
				cmInstance = CM.fromTextArea(textareaEl, {
					lineNumbers: true,
					// enable soft-wrapping so long lines flow to the next visual line
					lineWrapping: true,
					viewportMargin: Infinity,
					mode: 'platter',
					extraKeys: {
						'Ctrl-Enter': function() {
							analyzeSemantic(true);
						}
					}
				});
				cmInstance.setSize('100%', '100%');
				cmInstance.on('change', () => {
					codeInput = cmInstance.getValue();
				});
			}
			// Fetch app version
			await fetchVersion();

			// Initialize Pyodide
			await initPyodide();

		} catch (err) {
			console.warn('Failed to load CodeMirror from CDN:', err);
		}
	});

	onDestroy(() => {
		if (handleGlobalCtrlEnter) {
			window.removeEventListener('keydown', handleGlobalCtrlEnter);
			handleGlobalCtrlEnter = null;
		}

		if (cmInstance && typeof cmInstance.toTextArea === 'function') {
			cmInstance.toTextArea();
			cmInstance = null;
		}
	});

	// Terminal messages
	type TermMsg = { icon?: string; text: string };
	// default to empty terminal (no messages) so termMessages.length === 0
	let termMessages: TermMsg[] = [];

	// Compute error count: treat messages that start with "Lexical OK" as non-errors (count as zero)
	$: errorCount = termMessages.filter(
		(m) =>
			!(
				typeof m.text === 'string' &&
				(m.text.startsWith('Lexical OK') || m.text.startsWith('No Syntax Error') || m.text.startsWith('Warning:'))
			)
	).length;

	function setTerminalOk(message = 'No Error') {
		termMessages = [{ icon: check, text: message }];
	}
	function setTerminalError(message: string) {
		termMessages = [{ icon: errorIcon, text: message }];
	}
	function clearTerminal() {
		termMessages = [];
	}

	function clearErrorMarkers() {
		if (cmInstance) {
			errorMarkers.forEach((marker) => marker.clear());
			errorMarkers = [];
		}
	}

	function addErrorMarkers(errors: Token[]) {
		if (!cmInstance) {
			console.warn('Cannot add error markers: CodeMirror instance not available');
			return;
		}
		console.log('addErrorMarkers called with', errors.length, 'errors');
		clearErrorMarkers();
		errors.forEach((error, index) => {
			console.log(`Adding marker ${index + 1}:`, error);
			const line = error.line - 1; // CodeMirror uses 0-based line numbers
			const col = error.col - 1; // CodeMirror uses 0-based columns
			const valueLength = error.value?.length || 1;
			// Determine CSS class based on severity (case-insensitive)
			const severity = String((error as any).severity || '').toUpperCase();
			const cssClass = severity === 'WARNING' ? 'warning-underline' : 'error-underline';
			const marker = cmInstance.markText(
				{ line, ch: col },
				{ line, ch: col + valueLength },
				{ 
					className: cssClass,
					title: (error as any).message || 'Error'
				}
			);
			errorMarkers.push(marker);
			console.log(`  [OK] Marker ${index + 1} added successfully with ${cssClass}`);
		});
		console.log(`Total ${errorMarkers.length} error markers active in editor`);
	}

	// Convert curly quotes to straight quotes in CodeMirror
	function normalizeCurlyQuotes() {
		if (!cmInstance) return;
		
		const content = cmInstance.getValue();
		
		// Replace curly quotes with straight quotes using Unicode
		const normalized = content
			.replace(/\u201C/g, '\u0022') // Left double curly quote → straight double quote
			.replace(/\u201D/g, '\u0022') // Right double curly quote → straight double quote
			.replace(/\u2018/g, '\u0027') // Left single curly quote → straight single quote
			.replace(/\u2019/g, '\u0027'); // Right single curly quote → straight single quote
		
		if (content !== normalized) {
			// Save cursor position
			const cursor = cmInstance.getCursor();
			
			// Update content
			cmInstance.setValue(normalized);
			
			// Restore cursor position
			cmInstance.setCursor(cursor);
			
			// Update codeInput to ensure it's in sync
			codeInput = normalized;
		}
	}

	async function analyzeSemantic(runTacInterpreter = false) {
		normalizeCurlyQuotes();
		const startTime = performance.now();
		let analysisStatus = 'error';
		let terminalOutput = '';

		// Run lexical analysis first, skip logging to combine outputs
		const lexicalResult = await analyzeLexical(true);

		if (termMessages.length === 1 && termMessages[0].text.startsWith('Lexical OK')) {
			clearTerminal();

			if (!pyodideReady) {
				const errorMsg = 'Python runtime not ready';
				setTerminalError(errorMsg);
				analysisStatus = 'error';
				terminalOutput = `${lexicalResult.output}\n${errorMsg}`;
			} else {
				try {
					// Set the code input in Python
					pyodide.globals.set('code_input', codeInput);
					pyodide.globals.set('run_ir_pipeline', runTacInterpreter);

					// Run AST parser and semantic analysis
					const result = await pyodide.runPythonAsync(`
import sys
import re
import json
import importlib

# Force reload of modified modules to clear cache
def _ensure_parent_packages(module_name):
    parts = module_name.split('.')
    for i in range(1, len(parts)):
        parent_name = '.'.join(parts[:i])
        if parent_name not in sys.modules:
            importlib.import_module(parent_name)


def _safe_reload(module_name):
    if module_name in sys.modules:
        try:
            _ensure_parent_packages(module_name)
            importlib.reload(sys.modules[module_name])
        except Exception as reload_err:
            print(f"[Reload Warning] {module_name}: {reload_err}")


for module_name in [
    'app.semantic_analyzer.symbol_table.types',
    'app.semantic_analyzer.symbol_table.symbol_table',
    'app.semantic_analyzer.symbol_table.symbol_table_builder',
    'app.semantic_analyzer.semantic_passes.error_handler',
    'app.semantic_analyzer.semantic_passes.scope_checker',
    'app.semantic_analyzer.semantic_passes.type_checker',
    'app.semantic_analyzer.semantic_passes.control_flow_checker',
    'app.semantic_analyzer.semantic_passes.function_checker',
    'app.semantic_analyzer.semantic_analyzer',
    'app.intermediate_code.tac',
    'app.intermediate_code.quadruple',
    'app.intermediate_code.ir_generator',
    'app.intermediate_code.output_formatter',
    'app.intermediate_code.optimizer',
    'app.intermediate_code.constant_folding',
    'app.intermediate_code.propagation',
    'app.intermediate_code.dead_code_elimination',
    'app.intermediate_code.algebraic_simplification',
    'app.intermediate_code.optimizer_manager',
    'app.intermediate_code.ir_interpreter',
]:
    _safe_reload(module_name)

from app.lexer.lexer import Lexer
from app.semantic_analyzer.ast.ast_parser_program import ASTParser
from app.semantic_analyzer.ast.ast_reader import ASTReader, print_ast
from app.semantic_analyzer import analyze_program
from app.semantic_analyzer.symbol_table import print_symbol_table
from app.semantic_analyzer.symbol_table.symbol_table_output import format_symbol_table_for_console

result = None
try:
    lexer = Lexer(code_input)
    tokens = lexer.tokenize()
    parser = ASTParser(tokens)
    ast = parser.parse_program()
    
    # Pretty print AST to console logs
    print("")
    print("="*80)
    print("AST Analysis Complete")
    print("="*80)
    print_ast(ast, format="pretty")
    
    # Run complete semantic analysis with all passes
    print("")
    print("="*80)
    print("Running Semantic Analysis (All Passes)")
    print("="*80)
    symbol_table, error_handler = analyze_program(ast)
    
    # Print symbol table with error handler
    print_symbol_table(symbol_table, error_handler)
    
    # Also create JSON representation
    reader = ASTReader(ast)
    ast_json = reader.to_json(indent=2)
    
    # Get symbol table data for console.table output
    symbol_table_data = format_symbol_table_for_console(symbol_table)
    symbol_table_json = json.dumps(symbol_table_data)
    
    # Generate IR and execute only when explicitly requested (Ctrl+Enter).
    ir_tac_text = ""
    ir_quads_text = ""
    ir_tac_optimized_text = ""
    execution_output = ""
    execution_success = False
    execution_error = ""
    execution_globals = {}
    if run_ir_pipeline:
        try: ir_gen = __import__('app.intermediate_code.ir_generator', fromlist=['IRGenerator']).IRGenerator(); tac_instructions, quad_table = ir_gen.generate(ast); formatter = __import__('app.intermediate_code.output_formatter', fromlist=['IRFormatter']).IRFormatter(); ir_tac_text = formatter.format_tac_text(tac_instructions); ir_quads_text = formatter.format_quadruples_text(quad_table); print(""); print("="*80); print("Intermediate Code (Three Address Code)"); print("="*80); print(ir_tac_text); print(""); print("="*80); print("Intermediate Code (Quadruples)"); print("="*80); print(ir_quads_text); optimizer_module = __import__('app.intermediate_code.optimizer_manager', fromlist=['OptimizerManager', 'OptimizationLevel']); OptimizerManager = optimizer_module.OptimizerManager; OptimizationLevel = optimizer_module.OptimizationLevel; optimizer = OptimizerManager(OptimizationLevel.STANDARD); optimized_tac = optimizer.optimize_tac(tac_instructions); ir_tac_optimized_text = formatter.format_tac_text(optimized_tac); print(""); print("="*80); print("Optimized IR (Three Address Code - Standard Level)"); print("="*80); print(ir_tac_optimized_text); print(""); print("="*80); print("Program Execution (IR Interpreter)"); print("="*80); run_tac = __import__('app.intermediate_code.ir_interpreter', fromlist=['run_tac']).run_tac; exec_result = run_tac(optimized_tac); execution_output = exec_result.get("output", ""); execution_success = exec_result.get("success", False); execution_error = exec_result.get("error", ""); execution_globals = exec_result.get("globals", {}); print("[Execution OK]" if execution_success else f"[Execution Error] {execution_error}"); print(execution_output if execution_success and execution_output else "(no output)" if execution_success else "")
        except Exception as ir_err: import traceback; print(f"IR generation error: {str(ir_err)}"); traceback.print_exc(); execution_output = ""; execution_success = False; execution_error = str(ir_err); execution_globals = {}
    else:
        print("")
        print("="*80)
        print("Semantic Analysis Complete (IR execution skipped)")
        print("="*80)
    
    # Check for semantic errors from error handler
    if error_handler.has_errors():
        error_list = []
        error_details = []
        error_messages = []
        warning_messages = []
        error_markers = []  # For frontend error marking

        print("")
        print("="*80)
        print("SEMANTIC ERROR DETAILS WITH POSITIONS")
        print("="*80)
        
        sorted_errors = sorted(error_handler.get_errors(), key=lambda e: 0 if getattr(e.severity, "name", "") == "ERROR" else 1)
        for err in sorted_errors:
            error_list.append(str(err))
            # Format each error with position info
            severity_label = "ERROR" if err.severity.name == "ERROR" else "WARNING"
            if severity_label == "ERROR":
                error_messages.append(err.message)
            else:
                warning_messages.append(err.message)
            position_info = f" at line {err.line}, column {err.column}" if err.line and err.column else ""
            error_details.append(f"[{severity_label}] {err.message}{position_info}")
            
            # Log position info to console
            position_log = f"Line: {err.line}, Column: {err.column}" if err.line and err.column else "Position: Unknown"
            print(f"{severity_label}: {err.message}")
            print(f"  > {position_log}")
            print(f"  > Error Code: {err.error_code or 'N/A'}")
            if err.node:
                print(f"  > Node Type: {err.node.node_type}")
            print()
            
            # Add position info for error markers if available
            if err.line and err.column:
                error_markers.append({
                    "line": err.line,
                    "col": err.column,
                    "value": err.error_code or "semantic_error",
                    "message": err.message,
                    "severity": severity_label
                })
                print(f"  [OK] Error marker added for line {err.line}, col {err.column}")
            else:
                print(f"  [SKIP] No position info available - marker not added")
        
        print("")
        print(f"Total error markers to send to frontend: {len(error_markers)}")
        print("="*80)
        
        # Build detailed message with all errors (formal formatting)
        error_count = error_handler.get_error_count()
        warning_count = error_handler.get_warning_count()
        if error_count > 0:
            detailed_message = f"Semantic analysis failed with {error_count} error(s) and {warning_count} warning(s)\\n"
        else:
            detailed_message = f"No semantic errors with {warning_count} warning(s)\\n"
        for detail in error_details:
            detailed_message += f"{detail}\\n"
        
        result = {
            "success": False, 
            "message": detailed_message,
            "ast": ast_json,
            "symbol_table": symbol_table_json,
            "ir_tac": ir_tac_text,
            "ir_quads": ir_quads_text,
            "ir_tac_optimized": ir_tac_optimized_text,
            "execution_output": execution_output,
            "execution_success": execution_success,
            "execution_error": execution_error,
            "execution_globals": json.dumps(execution_globals),
            "errors": error_list,
            "semantic_errors": json.dumps(error_messages),
            "semantic_warnings": json.dumps(warning_messages),
            "error_markers": json.dumps(error_markers)
        }
    else:
        # Check for warnings even if no errors
        warning_messages_success = []
        warning_markers_success = []
        if error_handler.has_warnings():
            for warn in error_handler.get_errors():
                if warn.severity.name == "WARNING":
                    warning_messages_success.append(warn.message)
                    if warn.line and warn.column:
                        warning_markers_success.append({
                            "line": warn.line,
                            "col": warn.column,
                            "value": warn.error_code or "semantic_warning",
                            "message": warn.message,
                            "severity": "warning"
                        })
        
        warning_msg = f" with {len(warning_messages_success)} warning(s)" if warning_messages_success else ""
        result = {
            "success": True, 
            "message": f"No semantic errors{warning_msg}",
            "ast": ast_json,
            "symbol_table": symbol_table_json,
            "ir_tac": ir_tac_text,
            "ir_quads": ir_quads_text,
            "ir_tac_optimized": ir_tac_optimized_text,
            "execution_output": execution_output,
            "execution_success": execution_success,
            "execution_error": execution_error,
            "execution_globals": json.dumps(execution_globals),
            "semantic_warnings": json.dumps(warning_messages_success),
            "error_markers": json.dumps(warning_markers_success)
        }
except SyntaxError as e:
    error_msg = str(e)
    # Try to extract line and col from error message
    match = re.search(r'line (\\d+), col (\\d+)', error_msg)
    if match:
        line = int(match.group(1))
        col = int(match.group(2))
        result = {"success": False, "message": error_msg, "error": {"line": line, "col": col, "message": error_msg}}
    else:
        result = {"success": False, "message": error_msg}
except Exception as e:
    result = {"success": False, "message": f"Semantic analysis failed: {str(e)}"}

result
				`);

				const data = result.toJs({ dict_converter: Object.fromEntries });

				if (data.success) {
					clearErrorMarkers();
					const semWarningsSuccess: string[] = data.semantic_warnings ? JSON.parse(data.semantic_warnings) : [];
					const warningMarkers = data.error_markers ? JSON.parse(data.error_markers) : [];
					if (warningMarkers.length > 0) addErrorMarkers(warningMarkers);
					const successMsgs: TermMsg[] = [];

					if (runTacInterpreter) {
						// Ctrl+Enter: show runtime-only messages and no check icon.
						if (data.execution_success) {
							if (data.execution_output) {
								for (const line of data.execution_output.split('\n')) {
									successMsgs.push({ text: line });
								}
							}
						} else if (data.execution_error) {
							successMsgs.push({ icon: errorIcon, text: `Runtime Error: ${data.execution_error}` });
						}
					} else {
						successMsgs.push({ icon: check, text: data.message || 'No semantic errors' });
						for (const msg of semWarningsSuccess) successMsgs.push({ icon: errorIcon, text: `Warning: ${msg}` });
					}

					termMessages = successMsgs;
					analysisStatus = 'success';
					terminalOutput = runTacInterpreter ? data.execution_output || data.message || '' : data.message || '';
					
					// Log AST to browser console
					if (data.ast) {
						try {
							const astObj = JSON.parse(data.ast);
							console.log('\n%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'color: #00ff00');
							console.log('%c🌳 Abstract Syntax Tree (AST)', 'color: #00ff00; font-size: 16px; font-weight: bold');
							console.log('%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'color: #00ff00');
							console.log(astObj);
							console.log('%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'color: #00ff00');
						} catch (e) {
							console.warn('Failed to parse AST JSON:', e);
						}
					}
					
					// Log Symbol Table as console.table for better display of accessed scopes
					if (data.symbol_table) {
						try {
							const symbolTableData = JSON.parse(data.symbol_table);
							console.log('\n%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'color: #00bcd4');
							console.log('%c📋 Symbol Table (Detailed View)', 'color: #00bcd4; font-size: 16px; font-weight: bold');
							console.log('%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'color: #00bcd4');
							console.table(symbolTableData);
							console.log('%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'color: #00bcd4');
						} catch (e) {
							console.warn('Failed to parse Symbol Table JSON:', e);
						}
					}

					// Log Intermediate Code (TAC)
					if (data.ir_tac) {
						console.log('\n%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'color: #ff9800');
						console.log('%c⚙️  Intermediate Code — Three Address Code (TAC)', 'color: #ff9800; font-size: 16px; font-weight: bold');
						console.log('%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'color: #ff9800');
						console.log(data.ir_tac);
						console.log('%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'color: #ff9800');
					}

					// Log Intermediate Code (Quadruples)
					if (data.ir_quads) {
						console.log('\n%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'color: #ce93d8');
						console.log('%c🔢 Intermediate Code — Quadruples', 'color: #ce93d8; font-size: 16px; font-weight: bold');
						console.log('%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'color: #ce93d8');
						console.log(data.ir_quads);
						console.log('%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'color: #ce93d8');
					}

					// Log Optimized IR (TAC)
					if (data.ir_tac_optimized) {
						console.log('\n%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'color: #80cbc4');
						console.log('%c✨ Optimized IR — Three Address Code (Standard Level)', 'color: #80cbc4; font-size: 16px; font-weight: bold');
						console.log('%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'color: #80cbc4');
						console.log(data.ir_tac_optimized);
						console.log('%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'color: #80cbc4');
					}

					if (runTacInterpreter) {
						// Log Execution Output
						const execColor = data.execution_success ? '#69f0ae' : '#ff5252';
						console.log('\n%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', `color: ${execColor}`);
						console.log(`%c▶  Program Execution (IR Interpreter)`, `color: ${execColor}; font-size: 16px; font-weight: bold`);
						console.log('%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', `color: ${execColor}`);
						if (data.execution_success) {
							console.log('%cStatus: OK ✓', 'color: #69f0ae; font-weight: bold');
							console.log(data.execution_output || '(no output)');
							if (data.execution_globals) {
								try {
									const globals = JSON.parse(data.execution_globals);
									if (Object.keys(globals).length > 0) {
										console.log('%cFinal variable state:', 'color: #69f0ae; font-weight: bold');
										console.table(globals);
									}
								} catch {
									// Ignore malformed globals payload.
								}
							}
						} else {
							console.log('%cStatus: Runtime Error ✗', 'color: #ff5252; font-weight: bold');
							console.log(data.execution_error || 'Unknown error');
						}
						console.log('%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', `color: ${execColor}`);
					}
				} else {
					// Log error markers received from backend
					console.log('\n=== SEMANTIC ERROR MARKERS DEBUG ===');
					console.log('Error markers received:', data.error_markers);
					const parsedMarkers = data.error_markers ? JSON.parse(data.error_markers) : [];
					console.log('Number of markers:', Array.isArray(parsedMarkers) ? parsedMarkers.length : 0);
					
					// Check if we have semantic errors
					if (data.errors && data.errors.length > 0) {
						clearErrorMarkers();
						
						// Add error markers if position info is available
						if (parsedMarkers.length > 0) {
						console.log('Processing error markers...');
						const semanticTokens = parsedMarkers.map((marker: any) => {
							console.log(`  Marker: Line ${marker.line}, Col ${marker.col}, Severity: ${marker.severity}, Message: ${marker.message}`);
							return {
								type: 'semantic_error',
								value: marker.value,
								line: marker.line,
								col: marker.col,
								message: marker.message,
								severity: marker.severity
							};
						});
						console.log('Semantic tokens created:', semanticTokens);
						console.log('Calling addErrorMarkers with', semanticTokens.length, 'tokens');
						addErrorMarkers(semanticTokens);
						console.log('Error markers added to editor');
					} else {
						console.log('No error markers to add (array empty or undefined)');
					}
					console.log('=== END ERROR MARKERS DEBUG ===\n');
					// Build one termMessages entry per error/warning so errorCount is accurate
					const semErrors: string[] = data.semantic_errors ? JSON.parse(data.semantic_errors) : [];
					const semWarnings: string[] = data.semantic_warnings ? JSON.parse(data.semantic_warnings) : [];
					const msgs: { icon: any; text: string }[] = [];
					for (const msg of semErrors) msgs.push({ icon: errorIcon, text: `Semantic Error: ${msg}` });
					for (const msg of semWarnings) msgs.push({ icon: errorIcon, text: `Warning: ${msg}` });
					termMessages = msgs;
					analysisStatus = 'error';
					terminalOutput = data.message;
						// Still log AST to console if available
						if (data.ast) {
							try {
								const astObj = JSON.parse(data.ast);
								console.log('\n%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'color: #ff9800');
								console.log('%c🌳 Abstract Syntax Tree (AST) - With Semantic Errors', 'color: #ff9800; font-size: 16px; font-weight: bold');
								console.log('%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'color: #ff9800');
								console.log(astObj);
								console.log('%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'color: #ff9800');
							} catch (e) {
								console.warn('Failed to parse AST JSON:', e);
							}
						}
						
						// Still log Symbol Table if available
						if (data.symbol_table) {
							try {
								const symbolTableData = JSON.parse(data.symbol_table);
								console.log('\n%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'color: #ff9800');
								console.log('%c📋 Symbol Table - With Semantic Errors', 'color: #ff9800; font-size: 16px; font-weight: bold');
								console.log('%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'color: #ff9800');
								console.table(symbolTableData);
								console.log('%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'color: #ff9800');
							} catch (e) {
								console.warn('Failed to parse Symbol Table JSON:', e);
							}
						}

						// Still log Intermediate Code (TAC) if available
						if (data.ir_tac) {
							console.log('\n%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'color: #ff9800');
							console.log('%c⚙️  Intermediate Code — Three Address Code (TAC) - With Semantic Errors', 'color: #ff9800; font-size: 16px; font-weight: bold');
							console.log('%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'color: #ff9800');
							console.log(data.ir_tac);
							console.log('%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'color: #ff9800');
						}

						// Still log Intermediate Code (Quadruples) if available
						if (data.ir_quads) {
							console.log('\n%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'color: #ce93d8');
							console.log('%c🔢 Intermediate Code — Quadruples - With Semantic Errors', 'color: #ce93d8; font-size: 16px; font-weight: bold');
							console.log('%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'color: #ce93d8');
							console.log(data.ir_quads);
							console.log('%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'color: #ce93d8');
						}

						// Still log Optimized IR if available
						if (data.ir_tac_optimized) {
							console.log('\n%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'color: #80cbc4');
							console.log('%c✨ Optimized IR — Three Address Code - With Semantic Errors', 'color: #80cbc4; font-size: 16px; font-weight: bold');
							console.log('%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'color: #80cbc4');
							console.log(data.ir_tac_optimized);
							console.log('%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'color: #80cbc4');
						}

						// Log Execution Output (even with semantic errors, may still partially run)
						if (runTacInterpreter && (data.execution_output !== undefined || data.execution_error)) {
							const execColor2 = data.execution_success ? '#69f0ae' : '#ff5252';
							console.log('\n%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', `color: ${execColor2}`);
							console.log('%c▶  Program Execution (IR Interpreter)', `color: ${execColor2}; font-size: 16px; font-weight: bold`);
							console.log('%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', `color: ${execColor2}`);
							if (data.execution_success) {
								console.log('%cStatus: OK ✓', 'color: #69f0ae; font-weight: bold');
								console.log(data.execution_output || '(no output)');
							} else {
								console.log('%cStatus: Runtime Error ✗', 'color: #ff5252; font-weight: bold');
								console.log(data.execution_error || 'Unknown error');
							}
							console.log('%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', `color: ${execColor2}`);
						}
					}
					// Handle syntax errors with line/col information
					else if (data.error && data.error.line && data.error.col) {
						// Create a token-like object for the error marker
						const errorToken = {
							type: 'Syntax Error',
							value: 'error',
							line: data.error.line,
							col: data.error.col
						};
						addErrorMarkers([errorToken]);
						const semanticError = data.message || 'Semantic analysis failed';
						setTerminalError(semanticError);
						analysisStatus = 'error';
						terminalOutput = `${lexicalResult.output}\n${semanticError}`;
					} else {
						// Generic fallback
						const semanticError = data.message || 'Semantic analysis failed';
						setTerminalError(semanticError);
						analysisStatus = 'error';
						terminalOutput = `${lexicalResult.output}\n${semanticError}`;
					}
				}
			} catch (err) {
				const msg = err instanceof Error ? err.message : 'Unknown error';
				const semanticError = `Semantic analysis failed: ${msg}`;
				const errorMessage = `${lexicalResult.output}\n${semanticError}`;
				setTerminalError(semanticError);
				analysisStatus = 'error';
				terminalOutput = errorMessage;
			}
			}
		} else if (termMessages.length > 0) {
			// Lexical errors found
			const lexicalErrors = termMessages.map(m => m.text).join('; ');
			termMessages = [
				{ icon: errorIcon, text: 'Semantic analysis not performed due to lexical errors:' },
				...termMessages
			];
			analysisStatus = 'error';
			terminalOutput = `Lexical errors: ${lexicalErrors}`;
		} else {
			const notImplMessage = 'Semantic analysis initialization failed';
			setTerminalError(notImplMessage);
			analysisStatus = 'error';
			terminalOutput = notImplMessage;
		}

		activeTab = 'semantic';

		// Log the semantic analysis
		const duration = performance.now() - startTime;
		addToLogBatch({
			user_id: sessionId,
			source_code: codeInput,
			terminal_output: terminalOutput,
			status: analysisStatus,
			language: `${runTacInterpreter ? 'semantic-ir' : 'semantic'}-v${appVersion}`,
			duration_ms: Math.round(duration)
		});
	}

	async function analyzeSyntax() {
		normalizeCurlyQuotes();
		const startTime = performance.now();
		let analysisStatus = 'error';
		let terminalOutput = '';

		// Run lexical analysis first, skip logging to combine outputs
		const lexicalResult = await analyzeLexical(true);

		if (termMessages.length === 1 && termMessages[0].text.startsWith('Lexical OK')) {
			clearTerminal();

			if (!pyodideReady) {
				const errorMsg = 'Python runtime not ready';
				setTerminalError(errorMsg);
				analysisStatus = 'error';
				terminalOutput = `${lexicalResult.output}\n${errorMsg}`;
				// Continue to logging at the end
			} else {
				try {
					// Set the code input in Python
					pyodide.globals.set('code_input', codeInput);

					// Run syntax analysis
					const result = await pyodide.runPythonAsync(`
import sys
import re
from app.lexer.lexer import Lexer
from app.parser.parser_program import Parser

result = None
try:
    lexer = Lexer(code_input)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    parser.parse_program()
    
    result = {"success": True, "message": "No Syntax Error"}
except SyntaxError as e:
    error_msg = str(e)
    # Try to extract line and col from error message
    match = re.search(r'line (\\d+), col (\\d+)', error_msg)
    if match:
        line = int(match.group(1))
        col = int(match.group(2))
        result = {"success": False, "message": error_msg, "error": {"line": line, "col": col, "message": error_msg}}
    else:
        result = {"success": False, "message": error_msg}
except Exception as e:
    result = {"success": False, "message": f"Syntax analysis failed: {str(e)}"}

result
				`);

				const data = result.toJs({ dict_converter: Object.fromEntries });

				if (data.success) {
					clearErrorMarkers();
					const syntaxMessage = data.message || 'Syntax analysis completed successfully';
					const okMessage = `${lexicalResult.output}\n${syntaxMessage}`;
					setTerminalOk(syntaxMessage);
					analysisStatus = 'success';
					terminalOutput = okMessage;
				} else {
					// Handle syntax errors with line/col information
					if (data.error && data.error.line && data.error.col) {
						// Create a token-like object for the error marker
						const errorToken = {
							type: 'Syntax Error',
							value: 'error',
							line: data.error.line,
							col: data.error.col
						};
						addErrorMarkers([errorToken]);
					}
					const syntaxError = data.message || 'Syntax analysis failed';
					const errorMessage = `${lexicalResult.output}\n${syntaxError}`;
					setTerminalError(syntaxError);
					analysisStatus = 'error';
					terminalOutput = errorMessage;
				}
			} catch (err) {
				const msg = err instanceof Error ? err.message : 'Unknown error';
				const syntaxError = `Syntax analysis failed: ${msg}`;
				const errorMessage = `${lexicalResult.output}\n${syntaxError}`;
				setTerminalError(syntaxError);
				analysisStatus = 'error';
				terminalOutput = errorMessage;
			}
		}
	} else if (termMessages.length > 0) {
			// Lexical errors found
			const lexicalErrors = termMessages.map(m => m.text).join('; ');
			termMessages = [
				{ icon: errorIcon, text: 'Syntax analysis not performed due to lexical errors:' },
				...termMessages
			];
			analysisStatus = 'error';
			terminalOutput = `Lexical errors: ${lexicalErrors}`;
		} else {
			const notImplMessage = 'Syntax analysis not yet implemented';
			setTerminalOk(notImplMessage);
			analysisStatus = 'not-implemented';
			terminalOutput = notImplMessage;
		}

		activeTab = 'syntax';

		// Log the syntax analysis
		const duration = performance.now() - startTime;
		addToLogBatch({
			user_id: sessionId,
			source_code: codeInput,
			terminal_output: terminalOutput,
			status: analysisStatus,
			language: `syntax-v${appVersion}`,
			duration_ms: Math.round(duration)
		});
	}

	async function analyzeLexical(skipLogging = false) {
		normalizeCurlyQuotes();
		activeTab = skipLogging ? activeTab : 'lexical';
		const startTime = performance.now();
		let analysisStatus = 'error';
		let terminalOutput = '';

		if (!codeInput) {
			const errorMsg = 'Editor is empty';
			setTerminalError(errorMsg);
			terminalOutput = errorMsg;
			
			// Log even for early returns
			if (!skipLogging) {
				const duration = performance.now() - startTime;
				addToLogBatch({
					user_id: sessionId,
					source_code: codeInput,
					terminal_output: terminalOutput,
					status: analysisStatus,
					language: `lexical-v${appVersion}`,
					duration_ms: Math.round(duration)
				});
			}
			return { status: analysisStatus, output: terminalOutput };
		}

		if (!pyodideReady) {
			const errorMsg = 'Python runtime not ready. Please wait...';
			setTerminalError(errorMsg);
			terminalOutput = errorMsg;
			
			// Log even for early returns
			if (!skipLogging) {
				const duration = performance.now() - startTime;
				addToLogBatch({
					user_id: sessionId,
					source_code: codeInput,
					terminal_output: terminalOutput,
					status: analysisStatus,
					language: `lexical-v${appVersion}`,
					duration_ms: Math.round(duration)
				});
			}
			return { status: analysisStatus, output: terminalOutput };
		}

		isAnalyzing = true;
		try {
			// Set the code input in Python
			pyodide.globals.set('code_input', codeInput);

			// Run lexical analysis
			const tokensProxy = await pyodide.runPythonAsync(`
from app.lexer.lexer import Lexer

lexer = Lexer(code_input)
tokenize = lexer.tokenize()
tokens = []

for token in tokenize:
    if token is None:
        break
    tokens.append({
        "type": token.type,
        "value": token.value or '\\\\0',
        "line": token.line,
        "col": token.col
    })

tokens
			`);

		// Convert Python list to JavaScript array
		const received = tokensProxy.toJs({ dict_converter: Object.fromEntries });
		// treat tokens with type starting with 'invalid' or 'exceeds' (case-insensitive) as lexical errors
		const invalidTokens = received.filter(
			(t: Token) =>
				typeof t.type === 'string' &&
				(t.type.toLowerCase().startsWith('invalid') || t.type.toLowerCase().startsWith('exceeds'))
		);
		// tokens to show in the lexer table (exclude invalids and exceeds)
		tokens = received.filter(
			(t: Token) =>
				!(
					typeof t.type === 'string' &&
					(t.type.toLowerCase().startsWith('invalid') ||
						t.type.toLowerCase().startsWith('exceeds'))
				)
		);

		// update right table
		lexerRows.length = 0;
		// Group consecutive spaces, newlines, and tabs (but reset count when invalid tokens appear)
		// We need to track position in original received array to detect when errors interrupt whitespace
		const invalidPositions = new Set(invalidTokens.map((t: Token) => `${t.line}:${t.col}:${t.value}`));

			let i = 0;
			let receivedIdx = 0;

			while (i < tokens.length) {
				const t = tokens[i];
				const tokenType = t.type.toLowerCase();

				// Check if this is a space, newline, or tab token
				if (tokenType === 'space' || tokenType === 'newline' || tokenType === 'tab') {
					let count = 1;
					let nextIdx = i + 1;

					// Count consecutive identical tokens, but stop if an invalid token was between them in original stream
					while (nextIdx < tokens.length && tokens[nextIdx].type.toLowerCase() === tokenType) {
						// Check if there's an invalid token between current and next in the original stream
						const currentToken = tokens[i + count - 1];
						const nextToken = tokens[nextIdx];

						// Simple heuristic: if line/col gap suggests something was between them, stop counting
						const hasGap =
							nextToken.line > currentToken.line + 1 ||
							(nextToken.line === currentToken.line && nextToken.col > currentToken.col + 1);

						if (hasGap) {
							// There might be an invalid token between, stop grouping
							break;
						}

						count++;
						nextIdx++;
					}

					// Add a single row with count if more than 1
					const displayToken = count > 1 ? `${t.type} (${count})` : t.type;
					lexerRows.push({ lexeme: t.value ?? '', token: displayToken });
					i += count;
				} else {
					// Regular token, add as-is
					lexerRows.push({ lexeme: t.value ?? '', token: t.type });
					i++;
				}
			}

			if (invalidTokens.length) {
				// Format error messages based on token type
				const combinedErrors: TermMsg[] = [];
				let i = 0;

				while (i < invalidTokens.length) {
					const current = invalidTokens[i];
					let errorText = '';

					if (current.type === 'Invalid Character') {
						// Format: Error at line X col Y - Invalid Character: <character>
						errorText = `Error at line ${current.line} col ${current.col} - Invalid Character: ${current.value}`;
					} else if (current.type === 'Invalid Reserved Word Delimeter') {
						// Format: Error at line X col Y - Invalid Lexeme: Invalid <RW> delimiter '<delimiter>'
						errorText = `Error at line ${current.line} col ${current.col} - Invalid Lexeme: Invalid delimiter for reserved word '${current.value}'`;
					}else if (current.type === 'Invalid Identifier') {
						// Format: Error at line X col Y - Invalid Lexeme: <RW> cannot be an identifier
						errorText = `Error at line ${current.line} col ${current.col} - Invalid Lexeme: ${current.value} cannot be an identifier`;
					} else if (current.type === 'Invalid Lexeme') {
						// Format: Error at line X col Y - Invalid Lexeme: <invalid lexeme>
						errorText = `Error at line ${current.line} col ${current.col} - Invalid Lexeme: ${current.value}`;
					} else if (current.type.toLowerCase().startsWith('exceeds')) {
						// Determine if it's an identifier or literal based on first character
						const firstChar = current.value?.charAt(0) || '';
						const isIdentifier = /[a-zA-Z_]/.test(firstChar);
						const isLiteral = /[0-9]/.test(firstChar);

						let limitType = '';
						if (isIdentifier) {
							limitType = 'id';
						} else if (isLiteral) {
							limitType = 'piece/sip literal';
						} else {
							limitType = 'value';
						}

						// Format: Error at line X col Y - Invalid Lexeme: <value> exceeds <type> limit
						errorText = `Error at line ${current.line} col ${current.col} - Invalid Lexeme: ${current.value} exceeds ${limitType} limit`;
					} else {
						// Fallback for any other error types
						errorText = `Error at line ${current.line} col ${current.col} - ${current.type}: ${current.value}`;
					}

					combinedErrors.push({
						icon: errorIcon,
						text: errorText
					});
					i += 1;
				}

				termMessages = combinedErrors;
				// Highlight errors in CodeMirror
				addErrorMarkers(invalidTokens);
					// Update status and output for errors
				analysisStatus = 'error';
				terminalOutput = combinedErrors.map(e => e.text).join('; ');
			} else {
				clearErrorMarkers();

				const okMessage = tokens.length ? `Lexical OK • ${tokens.length} token(s)` : 'No tokens produced';
				setTerminalOk(okMessage);
				analysisStatus = 'success';
				terminalOutput = okMessage;
			}
		} catch (err) {
			const msg = err instanceof Error ? err.message : 'Unknown error';
			const errorMessage = `Lexical analysis failed: ${msg}`;
			setTerminalError(errorMessage);
			analysisStatus = 'error';
			terminalOutput = errorMessage;
		} finally {
			isAnalyzing = false;

			// Log the analysis only if not called from syntax analyzer
			if (!skipLogging) {
				const duration = performance.now() - startTime;
				addToLogBatch({
					user_id: sessionId,
					source_code: codeInput,
					terminal_output: terminalOutput,
					status: analysisStatus,
					language: `lexical-v${appVersion}`,
					duration_ms: Math.round(duration)
				});
			}
		}

		// Return the result for use by syntax analyzer
		return { status: analysisStatus, output: terminalOutput };
	}

	function toggleTheme() {
		normalizeCurlyQuotes();
		theme = theme === 'dark' ? 'light' : 'dark';
	}

	async function handleCopyToClipboard() {
		normalizeCurlyQuotes();
		const content =
			cmInstance && typeof cmInstance.getValue === 'function' ? cmInstance.getValue() : codeInput;
		try {
			await copyToClipboard(content);
			setTerminalOk('Content copied to clipboard');
		} catch (err) {
			setTerminalError('Failed to copy to clipboard');
		}
	}
</script>

<div class="ide" data-theme={theme} style={`--bg-img: url(${theme === 'dark' ? darkBg : lightBg})`}>
	<!-- Top bar -->
	<header class="titlebar">
		<div class="brand">
			<img class="logo" src={logo} alt="Platter logo" />
			<a href="/cfg" target="_blank" class="name" title="View CFG Visualization">Platter IDE</a>
		</div>
		<div class="win-controls">
			<span class="dot" title="minimize"></span>
			<span class="dot" title="maximize"></span>
			<span class="dot" title="close"></span>
		</div>
	</header>

	<!-- Main grid: left workspace and right sidebar -->
	<div class="grid">
		<!-- LEFT WORKSPACE -->
		<section class="left">
			<!-- Toolbar row -->
			<div class="toolbar">
				<button class="pill {activeTab === 'lexical' ? 'active' : ''}" on:click={() => analyzeLexical()}>
					{#if theme === 'dark'}
						<img class="icon" src={synSemLexIcon} alt="Lexical Icon" />
					{:else}
						<img class="icon" src={synSemLexIcon1} alt="Light Theme Icon" />
					{/if}

					<span>Lexical</span>
				</button>
				<!-- syntax and semantic methods to be replacesrd -->
				<button class="pill {activeTab === 'syntax' ? 'active' : ''}" on:click={analyzeSyntax}>
					{#if theme === 'dark'}
						<img class="icon" src={synSemLexIcon} alt="Lexical Icon" />
					{:else}
						<img class="icon" src={synSemLexIcon1} alt="Light Theme Icon" />
					{/if}
					<span>Syntax</span>
				</button>
				<button class="pill {activeTab === 'semantic' ? 'active' : ''}" on:click={() => analyzeSemantic(false)}>
					{#if theme === 'dark'}
						<img class="icon" src={synSemLexIcon} alt="Semantic Icon" />
					{:else}
						<img class="icon" src={synSemLexIcon1} alt="Light Theme Icon" />
					{/if}
					<span>Semantic</span>
				</button>

				<div class="spacer"></div>
				<!-- replace icons based on theme -->
				<button
					class="icon-btn"
					title="refresh"
					on:click={() => {
						normalizeCurlyQuotes();
						if (cmInstance) cmInstance.setValue('');
						codeInput = '';
						clearTerminal();
						clearErrorMarkers();
						lexerRows.length = 0;
						tokens = [];
					}}
					>{#if theme === 'dark'}
						<img class="icon" src={refresh} alt="Dark Theme Icon" />
					{:else}
						<img class="icon" src={refresh1} alt="Light Theme Icon" />
					{/if}</button
				>
				<button class="icon-btn" title="copy" on:click={handleCopyToClipboard}
					>{#if theme === 'dark'}
						<img class="icon" src={copy} alt="Dark Theme Icon" />
					{:else}
						<img class="icon" src={copy1} alt="Light Theme Icon" />
					{/if}</button
				>
				<button class="icon-btn" title="Theme" on:click={toggleTheme}>
					{#if theme === 'dark'}
						<img class="icon" src={lightmode} alt="Dark Theme Icon" />
					{:else}
						<img class="icon" src={darkmode} alt="Light Theme Icon" />
					{/if}
				</button>
			</div>

			<!-- Editor canvas -->
			<div class="panel editor" style={`--editor-img: url(${theme === 'dark' ? editor : editor1})`}>
				<textarea
					class="editor-area"
					bind:this={textareaEl}
					bind:value={codeInput}
					placeholder="Write your Platter code here..."
					spellcheck="false"
				></textarea>
			</div>

			<!-- Terminal panel -->
			<div
				class="panel terminal"
				style={`--terminal-img: url(${theme === 'dark' ? errors : errors1})`}
			>
				<div class="terminal-head">
					<span class="title">Terminal</span>
					<!-- error count (ignore 'Lexical OK' messages) -->

					<div class="counter">
						<span>Errors: {errorCount} </span>
						{#if errorCount > 0}
							<img class="icon" src={warning} alt="warning" />
						{/if}
					</div>
				</div>
				<div class="terminal-body">
					{#each termMessages as e}
						<div class="trow">
							{#if e.icon}
								<img class="ticon-img" src={e.icon} alt="" />
							{/if}
							<span class="tmsg">{e.text}</span>
						</div>
					{/each}
				</div>
			</div>
		</section>

		<!-- RIGHT SIDEBAR -->
		<aside class="right">
			<div class="actions">
				<button
					class="btn"
					on:click={() => {
						normalizeCurlyQuotes();
						const newWindow = window.open(window.location.href, '_blank');
						if (newWindow) setTimeout(() => (newWindow.document.body.style.zoom = '80%'), 100);
					}}
				>
					{#if theme === 'dark'}
						<img class="icon" src={newFile} alt="Dark Theme Icon" />
					{:else}
						<img class="icon" src={newFile1} alt="Light Theme Icon" />
					{/if} <span>New Tab</span></button
				>
				<button class="btn" type="button" on:click={openFileDialog}>
					{#if theme === 'dark'}
						<img class="icon" src={openFile} alt="Dark Theme Icon" />
					{:else}
						<img class="icon" src={openFile1} alt="Light Theme Icon" />
					{/if}
					<span>Open File</span></button
				>
				<!-- hidden file input for opening .platter files -->
				<input
					type="file"
					accept=".platter"
					bind:this={fileInputEl}
					on:change={handleFileInput}
					style="display:none"
				/>
				<button class="btn" type="button" on:click={saveFileDialog}>
					{#if theme === 'dark'}
						<img class="icon" src={saveFile} alt="Dark Theme Icon" />
					{:else}
						<img class="icon" src={saveFile1} alt="Light Theme Icon" />
					{/if} <span>Save File</span></button
				>
			</div>

			<div class="panel table" style={`--table-img: url(${table})`}>
				<div class="table-title">Lexer Table</div>
				<div class="table-head">
					<div>Lexeme</div>
					<div>Token</div>
				</div>
				<div class="table-body">
					{#if lexerRows.length === 0}
						<div class="empty">No tokens yet</div>
					{:else}
						{#each lexerRows as row}
							<div class="table-row">
								<div>{row.lexeme}</div>
								<div>{row.token}</div>
							</div>
						{/each}
					{/if}
				</div>
			</div>
		</aside>
	</div>
</div>

<style>
	:global(html) {
		height: 100%;
	}

	:global(body) {
		margin: 0;
		min-height: 100%;
	}

	.ide {
		--bg: #2b2b2f;
		--bg-soft: #2f2f34;
		--ink: #f2f2f2;
		--ink-muted: #c9c9cf;
		--accent: #ffffff;
		--outline: #ffffff;
		--panel: rgba(255, 255, 255, 0.03);
		--shadow: 0 0 0 2px var(--outline) inset;
		min-height: 100vh;
		min-width: 100vw;
		/* Use Svelte-provided CSS var for image */
		background-image: var(--bg-img);
		background-size: auto;
		background-position: top left;
		background-repeat: repeat;
		background-color: #26262a; /* fallback color */
		color: var(--ink);
		font-family: 'Inter', Roboto, sans-serif;
		font-weight: 700; /* Inter bold as default, Roboto as fallback */
	}

	.ide[data-theme='light'] {
		--bg: #f7f7fb;
		--bg-soft: #fff;
		--ink: #1f1f23;
		--ink-muted: #555;
		--accent: #111;
		--outline: #111;
		background-image: var(--bg-img);
		background-color: #e8e8ed; /* fallback color for light theme */
	}

	.titlebar {
		display: flex;
		align-items: center;
		justify-content: space-between;
		background: #77787e;
		color: #fff;
		padding: 8px 12px;
		user-select: none;
		width: 100%;
		box-sizing: border-box;
	}

	.title {
		font-size: 14px;
		margin-left: 24px;
		margin-bottom: 8px;
	}
	.brand {
		display: flex;
		align-items: center;
		gap: 8px;
		font-weight: 600;
	}
	.logo {
		filter: grayscale(0.1);
		width: 30px;
		height: 30px;
		object-fit: contain;
	}
	.name {
		letter-spacing: 0.2px;
	}
	.win-controls {
		display: flex;
		gap: 8px;
	}
	.dot {
		width: 12px;
		height: 12px;
		border-radius: 999px;
		background: #cfcfd6;
		display: inline-block;
	}

	.grid {
		display: grid;
		width: 100%;
		grid-template-columns: minmax(60%, 1130px) minmax(420px, 1fr);
		gap: 16px;
		padding: 16px;
	}

	.toolbar {
		display: flex;
		width: 100%;
		align-items: center;
		gap: 8px;
		background: transparent;
		color: var(--ink);
		border-radius: 8px;
		cursor: pointer;
		margin-right: 8px;
		margin-top: 12px;
	}

	.pill {
		display: inline-flex;
		align-items: center;
		gap: 10px;
		border: 4px solid var(--outline);
		background: transparent;
		color: var(--ink);
		padding: 8px 28px;
		border-radius: 8px;
		cursor: pointer;
		box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.15) inset;
		margin-right: 8px;
	}
	.pill.active {
		background: rgba(255, 255, 255, 0.08);
	}
	.spacer {
		flex: 1;
	}
	.icon-btn {
		display: inline-flex;
		align-items: center;
		gap: 10px;
		border: 4px solid var(--outline);
		background: transparent;
		color: var(--ink);
		padding: 8px 12px;
		border-radius: 8px;
		cursor: pointer;
		box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.15) inset;
	}

	/* toolbar icon image inside buttons */
	.icon {
		width: 18px;
		height: 18px;
		object-fit: contain;
	}

	.left {
		display: flex;
		flex-direction: column;
		max-width: 1130px;
		width: 100%;
	}
	.panel {
		/* background: var(--panel); */
		border-radius: 14px;
		padding: 10px;
		border: 4px solid var(--outline);

		box-shadow: var(--shadow);
	}
	.editor {
		/* use the `editor` SVG asset for background */
		background-image: var(--editor-img);
		/* show SVG at its intrinsic size */
		background-position: left;
		background-repeat: no-repeat;
		/* keep normal panel border; do not scale image into a border */
		border: none;
		box-shadow: none;
	}
	.editor + .terminal {
		margin-top: 10px;

		border: none;
	}

	.terminal {
		width: 100%;
		background-image: var(--terminal-img);
		/* show SVG at its intrinsic size */
		background-position: left;
		background-repeat: no-repeat;
		/* keep normal panel border; do not scale image into a border */
		border: none;
		box-shadow: none;
		outline: none;
		font-family:
			ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', monospace;
		font-size: 18px;
		height: 300px;
	}

	.editor-area {
		width: 95.5%;
		height: 400px;
		background: transparent;
		color: var(--ink);
		outline: none;
		font-family:
			ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', monospace;
		font-size: 18px;
		margin-left: 30px;
		margin-top: 60px;
		margin-bottom: 80px;
		border: none;
	}

	.terminal-head {
		display: flex;
		align-items: center;
		margin-bottom: 8px;
		color: var(--ink);
		border: none;
		box-shadow: none;
	}
	.counter {
		display: flex;
		align-items: center;
		gap: 8px;
		border-radius: 10px;
		margin: 0;
		transform: scale(0.7);
		margin-left: 400px;
		margin-bottom: 6px;
	}

	.terminal-body {
		height: 200px;
		overflow: auto;
		border: 4px solid var(--outline);
		border-radius: 10px;
		padding: 8px;
		margin-left: 16px;
		border: none;
		box-shadow: none;
	}
	.trow {
		display: flex;
		gap: 8px;
		align-items: center;
		padding: 4px 2px;
		color: var(--ink);
	}
	.ticon-img {
		width: 16px;
		height: 16px;
		object-fit: contain;
	}
	.tmsg {
		white-space: pre-wrap;
	}

	.right {
		display: flex;
		width: 100%;
		flex-direction: column;
		gap: 12px;
		background: transparent;
		color: var(--ink);
		padding: 8px 12px;
		border-radius: 8px;
	}
	.actions {
		display: flex;
		gap: 12px;
		justify-content: space-between;

		margin-right: 8px;
		margin-top: 6px;
		margin-bottom: 0px;
	}
	.btn {
		flex: 24;
		display: inline-flex;
		align-items: center;
		gap: 8px;
		border: 4px solid var(--outline);
		background: transparent;
		color: var(--ink);
		padding: 8px 12px;
		border-radius: 10px;
		cursor: pointer;
		scale: 1;
	}

	.table {
		height: 856px; /* retain table height like a textarea */
		display: flex;
		flex-direction: column;
		/* use the `editor` SVG asset for background */
		/* background-image: var(--table-img); */
		/* show SVG at its intrinsic size */
		background-position: left;
		background-repeat: no-repeat;
		/* keep normal panel border; do not scale image into a border */
		border: none;
		box-shadow: none;
	}
	.table-title {
		text-align: center;
		font-weight: 700;
		margin-bottom: 8px;
		/* margin-top: 48px; */

		border: none;
		box-shadow: none;
	}
	.table-head,
	.table-row {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 6px;
		border: none;
		box-shadow: none;
		/* margin-left: 32px; */
	}
	.table-head {
		border: 4px solid var(--outline);
		border-radius: 10px;
		padding: 8px;
		font-weight: 600;
		margin-bottom: 8px;
		/* border: none;
		box-shadow: none; */
	}
	.table-body {
		border: 4px solid var(--outline);
		border-radius: 10px;
		padding: 6px;
		flex: 1; /* occupy remaining space below the head */
		min-height: 0; /* allow flex child to shrink and enable scrolling */
		overflow-y: auto;
		overflow-x: hidden;
		display: flex;
		flex-direction: column;
		gap: 6px;
		/* 
		border: none;
		box-shadow: none; */
	}
	.table-row {
		border-bottom: 1px dashed rgba(255, 255, 255, 0.4);
		padding: 6px 4px;
	}
	.empty {
		opacity: 0.7;
		text-align: center;
		padding: 12px;
	}

	@media (max-width: 1500px) {
		.left {
			zoom: 0.75;
		}
	}

	@media (max-width: 1280px) {
		.left {
			zoom: 1;
		}
		.grid {
			grid-template-columns: 1fr;
		}
	}

	/* Strong CodeMirror overrides to ensure transparency and inherit panel background
   Use !important to beat CDN-loaded CodeMirror theme CSS if present */
	:global(.CodeMirror),
	:global(.CodeMirror-scroll),
	:global(.CodeMirror-gutters),
	:global(.CodeMirror pre) {
		background: transparent !important;
		color: inherit !important;
	}

	:global(.CodeMirror) {
		height: 100% !important;
		box-shadow: none !important;
		border: none !important;
		width: 97% !important;
		height: 400px !important;
		outline: none !important;
		font-family:
			ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', monospace !important;
		/* font-size: 18px !important; */
		margin-left: 10px !important;
		margin-top: 60px !important;
		margin-bottom: 80px !important;
		border: none !important;
	}

	:global(.CodeMirror-scroll) {
		/* disable horizontal scrolling and allow wrapping */
		overflow-x: hidden !important;
		overflow-y: auto !important;
		white-space: pre-wrap !important; /* allow wrap onto next line */
	}

	/* Make gutters transparent and inherit muted color */
	/* :global(.CodeMirror-gutters) {
		background: transparent !important;
		border-right: 4px solid var(--outline) !important;
		color: var(--ink-muted) !important;
	} */

	/* Apply the panel background image to the CodeMirror root so the editor shows your SVG */
	/* :global(.panel.editor .CodeMirror) {
		background-image: var(--editor-img) !important;
		background-position: left !important;
		background-repeat: no-repeat !important;
		background-size: auto !important;
	} */

	/* Ensure preformatted code uses the monospace font and no wrapping */
	:global(.CodeMirror pre) {
		font-family:
			ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', monospace !important;
		font-size: 18px !important;
		line-height: 20px !important;
		padding: 0 8px !important;
		margin: 0 !important;
		white-space: pre-wrap !important; /* allow wrapped lines */
	}

	/* Cursor color per theme */
	:global(.ide[data-theme='dark'] .CodeMirror .CodeMirror-cursor) {
		border-left: 1px solid #ffffff !important; /* white cursor for dark theme */
	}
	:global(.ide[data-theme='light'] .CodeMirror .CodeMirror-cursor) {
		border-left: 1px solid #000000 !important; /* black cursor for light theme */
	}

	/* Base text color for dark theme */
	:global(.ide[data-theme='dark'] .CodeMirror) {
		color: #d4d4d4 !important;
	}

	/* Base text color for light theme */
	:global(.ide[data-theme='light'] .CodeMirror) {
		color: #1f1f23 !important;
	}

	/* Error underline styling */
	:global(.error-underline) {
		border-bottom: 2px solid #ff0000 !important;
		background-color: rgba(255, 0, 0, 0.1) !important;
	}

	/* Warning underline styling */
	:global(.warning-underline) {
		border-bottom: 2px solid #ffa500 !important;
		background-color: rgba(255, 165, 0, 0.08) !important;
	}

	/* Platter Language Syntax Highlighting - TypeScript-inspired colors */
	
	/* Dark theme syntax colors */
	/* Keywords (if, else, for, while, etc.) - Purple/Magenta */
	:global(.ide[data-theme='dark'] .CodeMirror .cm-keyword) {
		color: #c586c0 !important;
		font-weight: 500 !important;
	}

	/* Data types (string, number, boolean, etc.) - Teal/Cyan */
	:global(.ide[data-theme='dark'] .CodeMirror .cm-type) {
		color: #4ec9b0 !important;
	}

	/* Built-in methods/functions - Yellow */
	:global(.ide[data-theme='dark'] .CodeMirror .cm-builtin) {
		color: #dcdcaa !important;
	}

	/* Boolean literals (true, false) - Blue */
	:global(.ide[data-theme='dark'] .CodeMirror .cm-atom) {
		color: #569cd6 !important;
	}

	/* Variables and identifiers - Light blue */
	:global(.ide[data-theme='dark'] .CodeMirror .cm-variable) {
		color: #9cdcfe !important;
	}

	/* String literals - Orange/Red */
	:global(.ide[data-theme='dark'] .CodeMirror .cm-string) {
		color: #ce9178 !important;
	}

	/* Escape sequences - Yellow-orange */
	:global(.ide[data-theme='dark'] .CodeMirror .cm-string-2) {
		color: #d7ba7d !important;
	}

	/* Numbers - Light green */
	:global(.ide[data-theme='dark'] .CodeMirror .cm-number) {
		color: #b5cea8 !important;
	}

	/* Operators (+, -, *, /, etc.) - White/Light gray */
	:global(.ide[data-theme='dark'] .CodeMirror .cm-operator) {
		color: #d4d4d4 !important;
	}

	/* Punctuation (brackets, parentheses, etc.) - Light gray */
	:global(.ide[data-theme='dark'] .CodeMirror .cm-punctuation) {
		color: #d4d4d4 !important;
	}

	/* Comments - Grey */
	:global(.ide[data-theme='dark'] .CodeMirror .cm-comment) {
		color: #999999 !important;
		font-style: italic !important;
	}

	/* Light theme syntax colors - Darker colors for better contrast */
	:global(.ide[data-theme='light'] .CodeMirror .cm-keyword) {
		color: #7c00a8 !important;
		font-weight: 500 !important;
	}

	:global(.ide[data-theme='light'] .CodeMirror .cm-type) {
		color: #1a5c6f !important;
	}

	:global(.ide[data-theme='light'] .CodeMirror .cm-builtin) {
		color: #5c4a1e !important;
	}

	:global(.ide[data-theme='light'] .CodeMirror .cm-atom) {
		color: #0000cc !important;
	}

	:global(.ide[data-theme='light'] .CodeMirror .cm-variable) {
		color: #000c5a !important;
	}

	:global(.ide[data-theme='light'] .CodeMirror .cm-string) {
		color: #7d0e0e !important;
	}

	:global(.ide[data-theme='light'] .CodeMirror .cm-string-2) {
		color: #cc0000 !important;
	}

	:global(.ide[data-theme='light'] .CodeMirror .cm-number) {
		color: #07603f !important;
	}

	:global(.ide[data-theme='light'] .CodeMirror .cm-operator) {
		color: #000000 !important;
	}

	:global(.ide[data-theme='light'] .CodeMirror .cm-punctuation) {
		color: #000000 !important;
	}

	:global(.ide[data-theme='light'] .CodeMirror .cm-comment) {
		color: #666666 !important;
		font-style: italic !important;
	}
</style>
