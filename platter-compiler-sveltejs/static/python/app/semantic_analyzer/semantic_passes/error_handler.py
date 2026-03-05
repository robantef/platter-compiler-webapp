"""
Semantic Error Handling for Platter Language
Centralized error collection and reporting for all semantic analysis passes
"""

from app.semantic_analyzer.ast.ast_nodes import ASTNode
from typing import List, Optional
from enum import Enum


class ErrorSeverity(Enum):
    """Severity levels for semantic errors"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class SemanticError:
    """Represents a semantic error with context information"""
    
    def __init__(self, message: str, node: Optional[ASTNode] = None, 
                 severity: ErrorSeverity = ErrorSeverity.ERROR, 
                 error_code: Optional[str] = None):
        self.message = message
        self.node = node
        self.severity = severity
        self.error_code = error_code
        # Extract position info if available
        self.line = getattr(node, 'line', None) if node else None
        self.column = getattr(node, 'column', None) if node else None
    
    def __repr__(self):
        severity_str = f"[{self.severity.value.upper()}]"
        code_str = f" [{self.error_code}]" if self.error_code else ""
        location_str = ""
        if self.line is not None:
            location_str = f" at line {self.line}"
            if self.column is not None:
                location_str += f", column {self.column}"
        return f"{severity_str}{code_str} {self.message}{location_str}"
    
    def __str__(self):
        return repr(self)


class SemanticErrorHandler:
    """Centralized error handler for all semantic analysis passes"""
    
    def __init__(self):
        self.errors: List[SemanticError] = []
        self._error_counts = {
            ErrorSeverity.ERROR: 0,
            ErrorSeverity.WARNING: 0,
            ErrorSeverity.INFO: 0
        }
    
    def add_error(self, message: str, node: Optional[ASTNode] = None, 
                  error_code: Optional[str] = None):
        """Add an error"""
        error = SemanticError(message, node, ErrorSeverity.ERROR, error_code)
        self.errors.append(error)
        self._error_counts[ErrorSeverity.ERROR] += 1
    
    def add_warning(self, message: str, node: Optional[ASTNode] = None,
                    error_code: Optional[str] = None):
        """Add a warning"""
        error = SemanticError(message, node, ErrorSeverity.WARNING, error_code)
        self.errors.append(error)
        self._error_counts[ErrorSeverity.WARNING] += 1
    
    def add_info(self, message: str, node: Optional[ASTNode] = None,
                 error_code: Optional[str] = None):
        """Add an informational message"""
        error = SemanticError(message, node, ErrorSeverity.INFO, error_code)
        self.errors.append(error)
        self._error_counts[ErrorSeverity.INFO] += 1
    
    def has_errors(self) -> bool:
        """Check if there are any errors (not warnings or info)"""
        return self._error_counts[ErrorSeverity.ERROR] > 0
    
    def has_warnings(self) -> bool:
        """Check if there are any warnings"""
        return self._error_counts[ErrorSeverity.WARNING] > 0
    
    def get_error_count(self) -> int:
        """Get number of errors"""
        return self._error_counts[ErrorSeverity.ERROR]
    
    def get_warning_count(self) -> int:
        """Get number of warnings"""
        return self._error_counts[ErrorSeverity.WARNING]
    
    def get_info_count(self) -> int:
        """Get number of info messages"""
        return self._error_counts[ErrorSeverity.INFO]
    
    def get_errors(self, severity: Optional[ErrorSeverity] = None) -> List[SemanticError]:
        """Get errors filtered by severity"""
        if severity is None:
            return self.errors
        return [e for e in self.errors if e.severity == severity]
    
    def clear(self):
        """Clear all errors"""
        self.errors.clear()
        for severity in self._error_counts:
            self._error_counts[severity] = 0
    
    def format_errors(self, include_warnings: bool = True, include_info: bool = False) -> str:
        """Format all errors as a string"""
        if not self.errors:
            return "No errors"
        
        # Sort errors by severity: ERROR first, then WARNING, then INFO
        sorted_errors = sorted(self.errors, key=lambda e: 0 if e.severity == ErrorSeverity.ERROR else (1 if e.severity == ErrorSeverity.WARNING else 2))
        
        lines = []
        for error in sorted_errors:
            if error.severity == ErrorSeverity.ERROR:
                lines.append(str(error))
            elif error.severity == ErrorSeverity.WARNING and include_warnings:
                lines.append(str(error))
            elif error.severity == ErrorSeverity.INFO and include_info:
                lines.append(str(error))
        
        if not lines:
            return "No errors"
        
        return "\n".join(lines)
    
    def print_summary(self):
        """Print error summary"""
        error_count = self.get_error_count()
        warning_count = self.get_warning_count()
        info_count = self.get_info_count()
        
        print("\n" + "=" * 60)
        print("SEMANTIC ANALYSIS SUMMARY")
        print("=" * 60)
        print(f"Errors: {error_count}")
        print(f"Warnings: {warning_count}")
        print(f"Info: {info_count}")
        print("=" * 60)
        
        if self.errors:
            print("\n" + self.format_errors(include_warnings=True, include_info=True))
    
    def __repr__(self):
        return (f"SemanticErrorHandler(errors={self.get_error_count()}, "
                f"warnings={self.get_warning_count()}, "
                f"info={self.get_info_count()})")


# Error code constants for common semantic errors
class ErrorCodes:
    """Standard error codes for semantic analysis"""
    # Scope/Symbol Table errors (E0XX)
    DUPLICATE_SYMBOL = "E001"
    UNDEFINED_SYMBOL = "E002"
    SHADOWING_SYMBOL = "W001"
    
    # Type errors (E1XX)
    TYPE_MISMATCH = "E101"
    UNDEFINED_TYPE = "E102"
    INVALID_CAST = "E103"
    INCOMPATIBLE_TYPES = "E104"
    INVALID_OPERATION = "E105"
    INVALID_ASSIGNMENT_TARGET = "E106"
    DIVISION_BY_ZERO = "E107"
    
    # Array/Table errors (E2XX)
    INVALID_ARRAY_ACCESS = "E201"
    INVALID_TABLE_ACCESS = "E202"
    UNDEFINED_FIELD = "E203"
    INVALID_DIMENSION = "E204"
    ARRAY_OUT_OF_BOUNDS = "E205"
    DUPLICATE_FIELD = "E206"
    RECURSIVE_TYPE = "E207"
    FORWARD_REFERENCE = "E208"
    
    # Recipe errors (E3XX)
    UNDEFINED_RECIPE = "E301"
    FLAVOR_COUNT_MISMATCH = "E302"  # argument count
    FLAVOR_TYPE_MISMATCH = "E303"  # argument type
    INVALID_SERVE_TYPE = "E304"  # return type
    MISSING_SERVE = "E305"  # missing return
    REDEFINED_BUILTIN = "E306"  # redefining built-in recipe
    
    # Control flow errors (E4XX)
    STOP_OUTSIDE_LOOP = "E401"  # break outside loop
    NEXT_OUTSIDE_LOOP = "E402"  # continue outside loop
    SERVE_OUTSIDE_RECIPE = "E403"  # return outside function
    UNREACHABLE_CODE = "E404"  # unreachable code
    
    # Usage warnings (W1XX)
    UNINITIALIZED_INGREDIENT = "W101"  # uninitialized variable
    UNUSED_INGREDIENT = "W102"  # unused variable
