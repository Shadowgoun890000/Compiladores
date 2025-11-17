"""
Analizador Semántico
Realiza análisis semántico del AST, incluyendo:
- Verificación de declaraciones
- Verificación de tipos
- Análisis de scope
- Detección de variables no usadas
"""
from typing import List, Optional
from .ast_nodes import *
from .symbol_table import SymbolTable, Symbol, SymbolKind, DataType


class SemanticError(Exception):
    """Error de análisis semántico"""
    def __init__(self, line: int, col: int, message: str):
        self.line = line
        self.col = col
        self.message = message
        super().__init__(f"Error semántico en línea {line}, columna {col}: {message}")


class SemanticAnalyzer:
    """
    Analizador semántico que recorre el AST y verifica:
    - Declaraciones de variables y funciones
    - Uso de variables antes de declaración
    - Redeclaraciones
    - Tipos compatibles en operaciones
    - Variables no usadas
    """
    
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors: List[SemanticError] = []
        self.warnings: List[str] = []
        self.in_function = False
        self.current_function_return_type = None
    
    def analyze(self, program: Program) -> bool:
        """
        Analiza el programa y retorna True si no hay errores.
        Los errores y warnings se almacenan en self.errors y self.warnings
        """
        self.errors = []
        self.warnings = []
        
        try:
            self.visit_program(program)
            
            # Verificar variables no usadas
            self._check_unused_symbols()
            
            return len(self.errors) == 0
        
        except Exception as e:
            self.errors.append(SemanticError(0, 0, f"Error interno: {str(e)}"))
            return False
    
    def _add_error(self, line: int, col: int, message: str):
        """Agrega un error semántico"""
        self.errors.append(SemanticError(line, col, message))
    
    def _add_warning(self, line: int, col: int, message: str):
        """Agrega un warning"""
        self.warnings.append(f"Warning línea {line}, col {col}: {message}")
    
    def _check_unused_symbols(self):
        """Verifica símbolos no usados y genera warnings"""
        unused = self.symbol_table.get_unused_symbols()
        for symbol in unused:
            self._add_warning(
                symbol.line, symbol.col,
                f"{symbol.kind.value} '{symbol.name}' declarada pero no usada"
            )
    
    # ========================================================================
    # Visitors para cada tipo de nodo
    # ========================================================================
    
    def visit_program(self, node: Program):
        """Visita el programa completo"""
        for stmt in node.statements:
            self.visit_statement(stmt)
    
    def visit_statement(self, node: ASTNode):
        """Dispatcher para diferentes tipos de sentencias"""
        if isinstance(node, VarDecl):
            self.visit_var_decl(node)
        elif isinstance(node, FunctionDecl):
            self.visit_function_decl(node)
        elif isinstance(node, IfStmt):
            self.visit_if_stmt(node)
        elif isinstance(node, WhileStmt):
            self.visit_while_stmt(node)
        elif isinstance(node, ForStmt):
            self.visit_for_stmt(node)
        elif isinstance(node, ReturnStmt):
            self.visit_return_stmt(node)
        elif isinstance(node, Block):
            self.visit_block(node)
        elif isinstance(node, ExprStmt):
            self.visit_expr_stmt(node)
    
    def visit_var_decl(self, node: VarDecl):
        """Visita declaración de variable"""
        # Verificar que no exista en el scope actual
        existing = self.symbol_table.lookup_local(node.name)
        if existing:
            self._add_error(
                node.line, node.col,
                f"Variable '{node.name}' ya declarada en línea {existing.line}"
            )
            return
        
        # Inferir tipo de la inicialización
        data_type = DataType.UNKNOWN
        if node.init:
            data_type = self.visit_expression(node.init)
        
        # Crear símbolo
        kind = SymbolKind.CONSTANT if node.kind == "const" else SymbolKind.VARIABLE
        symbol = Symbol(
            name=node.name,
            kind=kind,
            data_type=data_type,
            line=node.line,
            col=node.col,
            initialized=node.init is not None
        )
        
        self.symbol_table.define(symbol)
        
        # const debe tener inicialización
        if kind == SymbolKind.CONSTANT and not node.init:
            self._add_error(
                node.line, node.col,
                f"Constante '{node.name}' debe ser inicializada"
            )
    
    def visit_function_decl(self, node: FunctionDecl):
        """Visita declaración de función"""
        # Verificar que no exista
        existing = self.symbol_table.lookup_local(node.name)
        if existing:
            self._add_error(
                node.line, node.col,
                f"Función '{node.name}' ya declarada en línea {existing.line}"
            )
            return
        
        # Crear símbolo de función
        symbol = Symbol(
            name=node.name,
            kind=SymbolKind.FUNCTION,
            data_type=DataType.FUNCTION,
            line=node.line,
            col=node.col,
            initialized=True,
            param_types=[DataType.UNKNOWN] * len(node.params),
            return_type=DataType.UNKNOWN
        )
        
        self.symbol_table.define(symbol)
        
        # Entrar a scope de función
        self.symbol_table.enter_scope(f"function_{node.name}")
        self.in_function = True
        self.current_function_return_type = DataType.UNKNOWN
        
        # Definir parámetros
        for param in node.params:
            param_symbol = Symbol(
                name=param,
                kind=SymbolKind.PARAMETER,
                data_type=DataType.UNKNOWN,
                line=node.line,
                col=node.col,
                initialized=True
            )
            if not self.symbol_table.define(param_symbol):
                self._add_error(
                    node.line, node.col,
                    f"Parámetro '{param}' duplicado en función '{node.name}'"
                )
        
        # Visitar cuerpo
        for stmt in node.body:
            self.visit_statement(stmt)
        
        # Salir de scope
        self.in_function = False
        self.current_function_return_type = None
        self.symbol_table.exit_scope()
    
    def visit_if_stmt(self, node: IfStmt):
        """Visita sentencia if"""
        # Verificar condición
        cond_type = self.visit_expression(node.condition)
        if cond_type not in [DataType.BOOLEAN, DataType.UNKNOWN, DataType.ERROR]:
            self._add_warning(
                node.line, node.col,
                f"Condición de 'if' debería ser booleana, se encontró {cond_type.value}"
            )
        
        # Visitar ramas
        if isinstance(node.then_branch, Block):
            self.symbol_table.enter_scope("if_then")
            self.visit_statement(node.then_branch)
            self.symbol_table.exit_scope()
        else:
            self.visit_statement(node.then_branch)
        
        if node.else_branch:
            if isinstance(node.else_branch, Block):
                self.symbol_table.enter_scope("if_else")
                self.visit_statement(node.else_branch)
                self.symbol_table.exit_scope()
            else:
                self.visit_statement(node.else_branch)
    
    def visit_while_stmt(self, node: WhileStmt):
        """Visita sentencia while"""
        # Verificar condición
        cond_type = self.visit_expression(node.condition)
        if cond_type not in [DataType.BOOLEAN, DataType.UNKNOWN, DataType.ERROR]:
            self._add_warning(
                node.line, node.col,
                f"Condición de 'while' debería ser booleana, se encontró {cond_type.value}"
            )
        
        # Visitar cuerpo
        if isinstance(node.body, Block):
            self.symbol_table.enter_scope("while")
            self.visit_statement(node.body)
            self.symbol_table.exit_scope()
        else:
            self.visit_statement(node.body)
    
    def visit_for_stmt(self, node: ForStmt):
        """Visita sentencia for"""
        self.symbol_table.enter_scope("for")
        
        # Init
        if node.init:
            if isinstance(node.init, VarDecl):
                self.visit_var_decl(node.init)
            else:
                self.visit_expression(node.init)
        
        # Condition
        if node.condition:
            cond_type = self.visit_expression(node.condition)
            if cond_type not in [DataType.BOOLEAN, DataType.UNKNOWN, DataType.ERROR]:
                self._add_warning(
                    node.line, node.col,
                    f"Condición de 'for' debería ser booleana"
                )
        
        # Update
        if node.update:
            self.visit_expression(node.update)
        
        # Body
        self.visit_statement(node.body)
        
        self.symbol_table.exit_scope()
    
    def visit_return_stmt(self, node: ReturnStmt):
        """Visita sentencia return"""
        if not self.in_function:
            self._add_error(
                node.line, node.col,
                "'return' solo puede usarse dentro de una función"
            )
        
        if node.value:
            self.visit_expression(node.value)
    
    def visit_block(self, node: Block):
        """Visita bloque"""
        self.symbol_table.enter_scope("block")
        for stmt in node.statements:
            self.visit_statement(stmt)
        self.symbol_table.exit_scope()
    
    def visit_expr_stmt(self, node: ExprStmt):
        """Visita sentencia de expresión"""
        self.visit_expression(node.expr)
    
    # ========================================================================
    # Expresiones
    # ========================================================================
    
    def visit_expression(self, node: ASTNode) -> DataType:
        """Visita una expresión y retorna su tipo"""
        if isinstance(node, BinaryOp):
            return self.visit_binary_op(node)
        elif isinstance(node, UnaryOp):
            return self.visit_unary_op(node)
        elif isinstance(node, Assignment):
            return self.visit_assignment(node)
        elif isinstance(node, CallExpr):
            return self.visit_call_expr(node)
        elif isinstance(node, IndexExpr):
            return self.visit_index_expr(node)
        elif isinstance(node, MemberExpr):
            return self.visit_member_expr(node)
        elif isinstance(node, Identifier):
            return self.visit_identifier(node)
        elif isinstance(node, Literal):
            return self.visit_literal(node)
        else:
            return DataType.UNKNOWN
    
    def visit_binary_op(self, node: BinaryOp) -> DataType:
        """Visita operación binaria y verifica tipos"""
        left_type = self.visit_expression(node.left)
        right_type = self.visit_expression(node.right)
        
        op = node.operator
        
        # Operadores aritméticos
        if op in ['+', '-', '*', '/', '%']:
            if left_type == DataType.NUMBER and right_type == DataType.NUMBER:
                return DataType.NUMBER
            elif left_type == DataType.UNKNOWN or right_type == DataType.UNKNOWN:
                return DataType.NUMBER
            else:
                self._add_error(
                    node.line, node.col,
                    f"Operador '{op}' requiere operandos numéricos, "
                    f"se encontró {left_type.value} y {right_type.value}"
                )
                return DataType.ERROR
        
        # Operadores de comparación
        elif op in ['<', '<=', '>', '>=']:
            return DataType.BOOLEAN
        
        # Operadores de igualdad
        elif op in ['==', '!=']:
            return DataType.BOOLEAN
        
        # Operadores lógicos
        elif op in ['&&', '||']:
            if left_type not in [DataType.BOOLEAN, DataType.UNKNOWN]:
                self._add_warning(
                    node.line, node.col,
                    f"Operando izquierdo de '{op}' debería ser booleano"
                )
            if right_type not in [DataType.BOOLEAN, DataType.UNKNOWN]:
                self._add_warning(
                    node.line, node.col,
                    f"Operando derecho de '{op}' debería ser booleano"
                )
            return DataType.BOOLEAN
        
        return DataType.UNKNOWN
    
    def visit_unary_op(self, node: UnaryOp) -> DataType:
        """Visita operación unaria"""
        operand_type = self.visit_expression(node.operand)
        
        if node.operator == '!':
            if operand_type not in [DataType.BOOLEAN, DataType.UNKNOWN]:
                self._add_warning(
                    node.line, node.col,
                    f"Operador '!' requiere operando booleano"
                )
            return DataType.BOOLEAN
        
        elif node.operator in ['-', '+']:
            if operand_type not in [DataType.NUMBER, DataType.UNKNOWN]:
                self._add_error(
                    node.line, node.col,
                    f"Operador '{node.operator}' requiere operando numérico"
                )
                return DataType.ERROR
            return DataType.NUMBER
        
        return DataType.UNKNOWN
    
    def visit_assignment(self, node: Assignment) -> DataType:
        """Visita asignación"""
        # Verificar que la variable existe
        symbol = self.symbol_table.lookup(node.name)
        if not symbol:
            self._add_error(
                node.line, node.col,
                f"Variable '{node.name}' no declarada"
            )
            return DataType.ERROR
        
        # No se puede asignar a constantes
        if symbol.kind == SymbolKind.CONSTANT:
            self._add_error(
                node.line, node.col,
                f"No se puede reasignar la constante '{node.name}'"
            )
        
        # Marcar como usada e inicializada
        self.symbol_table.mark_used(node.name)
        self.symbol_table.mark_initialized(node.name)
        
        # Verificar tipo del valor
        value_type = self.visit_expression(node.value)
        
        # Verificar compatibilidad de tipos
        if symbol.data_type != DataType.UNKNOWN and value_type != DataType.UNKNOWN:
            if symbol.data_type != value_type:
                self._add_warning(
                    node.line, node.col,
                    f"Asignación de tipo {value_type.value} a variable de tipo {symbol.data_type.value}"
                )
        
        return value_type
    
    def visit_call_expr(self, node: CallExpr) -> DataType:
        """Visita llamada a función"""
        # Visitar argumentos
        arg_types = []
        for arg in node.arguments:
            arg_types.append(self.visit_expression(arg))
        
        # Si el callee es un identificador, verificar la función
        if isinstance(node.callee, Identifier):
            symbol = self.symbol_table.lookup(node.callee.name)
            if not symbol:
                self._add_error(
                    node.line, node.col,
                    f"Función '{node.callee.name}' no declarada"
                )
                return DataType.ERROR
            
            if symbol.kind != SymbolKind.FUNCTION:
                self._add_error(
                    node.line, node.col,
                    f"'{node.callee.name}' no es una función"
                )
                return DataType.ERROR
            
            self.symbol_table.mark_used(node.callee.name)
            
            # Verificar número de argumentos
            if symbol.param_types and len(arg_types) != len(symbol.param_types):
                self._add_error(
                    node.line, node.col,
                    f"Función '{node.callee.name}' espera {len(symbol.param_types)} "
                    f"argumentos, se proporcionaron {len(arg_types)}"
                )
            
            return symbol.return_type or DataType.UNKNOWN
        
        return DataType.UNKNOWN
    
    def visit_index_expr(self, node: IndexExpr) -> DataType:
        """Visita acceso a índice"""
        self.visit_expression(node.object)
        index_type = self.visit_expression(node.index)
        
        if index_type not in [DataType.NUMBER, DataType.UNKNOWN]:
            self._add_warning(
                node.line, node.col,
                "Índice debería ser numérico"
            )
        
        return DataType.UNKNOWN
    
    def visit_member_expr(self, node: MemberExpr) -> DataType:
        """Visita acceso a miembro"""
        self.visit_expression(node.object)
        return DataType.UNKNOWN
    
    def visit_identifier(self, node: Identifier) -> DataType:
        """Visita identificador"""
        symbol = self.symbol_table.lookup(node.name)
        if not symbol:
            self._add_error(
                node.line, node.col,
                f"Variable '{node.name}' no declarada"
            )
            return DataType.ERROR
        
        # Verificar si está inicializada
        if not symbol.initialized and symbol.kind != SymbolKind.FUNCTION:
            self._add_warning(
                node.line, node.col,
                f"Variable '{node.name}' puede no estar inicializada"
            )
        
        self.symbol_table.mark_used(node.name)
        return symbol.data_type
    
    def visit_literal(self, node: Literal) -> DataType:
        """Visita literal"""
        type_map = {
            "number": DataType.NUMBER,
            "string": DataType.STRING,
            "boolean": DataType.BOOLEAN
        }
        return type_map.get(node.type, DataType.UNKNOWN)
    
    # ========================================================================
    # Reportes
    # ========================================================================
    
    def get_report(self) -> str:
        """Genera un reporte del análisis semántico"""
        report = "=" * 60 + "\n"
        report += "ANÁLISIS SEMÁNTICO\n"
        report += "=" * 60 + "\n\n"
        
        # Errores
        if self.errors:
            report += f"ERRORES ({len(self.errors)}):\n"
            report += "-" * 60 + "\n"
            for error in self.errors:
                report += f"  ❌ Línea {error.line}, Col {error.col}: {error.message}\n"
            report += "\n"
        else:
            report += "✅ No se encontraron errores semánticos\n\n"
        
        # Warnings
        if self.warnings:
            report += f"ADVERTENCIAS ({len(self.warnings)}):\n"
            report += "-" * 60 + "\n"
            for warning in self.warnings:
                report += f"  ⚠️  {warning}\n"
            report += "\n"
        
        # Tabla de símbolos
        report += "TABLA DE SÍMBOLOS:\n"
        report += "-" * 60 + "\n"
        report += self.symbol_table.print_tree()
        
        return report
