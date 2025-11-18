"""
Tabla de Símbolos para el Análisis Semántico
Maneja scopes, declaraciones de variables y funciones
"""
from typing import Dict, List, Optional, Set
from enum import Enum
from dataclasses import dataclass


class SymbolKind(Enum):
    """Tipos de símbolos"""
    VARIABLE = "variable"
    CONSTANT = "constant"
    FUNCTION = "function"
    PARAMETER = "parameter"


class DataType(Enum):
    """Tipos de datos soportados"""
    NUMBER = "number"
    STRING = "string"
    BOOLEAN = "boolean"
    FUNCTION = "function"
    VOID = "void"
    UNKNOWN = "unknown"
    ERROR = "error"


@dataclass
class Symbol:
    """Representa un símbolo en la tabla"""
    name: str
    kind: SymbolKind
    data_type: DataType
    line: int
    col: int
    initialized: bool = False
    used: bool = False
    scope_level: int = 0
    # Para funciones
    param_types: Optional[List[DataType]] = None
    return_type: Optional[DataType] = None


class Scope:
    """Representa un ámbito (scope) en el programa"""
    
    def __init__(self, name: str, level: int, parent: Optional['Scope'] = None):
        self.name = name
        self.level = level
        self.parent = parent
        self.symbols: Dict[str, Symbol] = {}
        self.children: List['Scope'] = []
    
    def define(self, symbol: Symbol) -> bool:
        """
        Define un símbolo en este scope.
        Retorna False si ya existe en este scope.
        """
        if symbol.name in self.symbols:
            return False
        self.symbols[symbol.name] = symbol
        return True
    
    def lookup_local(self, name: str) -> Optional[Symbol]:
        """Busca un símbolo solo en este scope"""
        return self.symbols.get(name)
    
    def lookup(self, name: str) -> Optional[Symbol]:
        """Busca un símbolo en este scope y en los padres"""
        symbol = self.lookup_local(name)
        if symbol:
            return symbol
        if self.parent:
            return self.parent.lookup(name)
        return None
    
    def get_all_symbols(self) -> List[Symbol]:
        """Retorna todos los símbolos en este scope"""
        return list(self.symbols.values())
    
    def __repr__(self) -> str:
        return f"Scope({self.name}, level={self.level}, symbols={len(self.symbols)})"


class SymbolTable:
    """
    Tabla de símbolos con soporte para múltiples scopes anidados
    """
    
    def __init__(self):
        # Scope global
        self.global_scope = Scope("global", 0)
        self.current_scope = self.global_scope
        self.scope_counter = 0
        
        # Funciones built-in
        self._define_builtins()

    def _define_builtins(self):
        """Define funciones y constantes built-in"""
        builtins = [
            ("print", [DataType.UNKNOWN], DataType.VOID),
            ("console", [], DataType.UNKNOWN),  # Objeto console
            ("log", [DataType.UNKNOWN], DataType.VOID),  # console.log
            ("error", [DataType.UNKNOWN], DataType.VOID),  # console.error
            ("input", [], DataType.STRING),
            ("parseInt", [DataType.STRING], DataType.NUMBER),
            ("parseFloat", [DataType.STRING], DataType.NUMBER),
        ]

        for name, params, return_type in builtins:
            symbol = Symbol(
                name=name,
                kind=SymbolKind.FUNCTION,
                data_type=DataType.FUNCTION,
                line=0,
                col=0,
                initialized=True,
                used=False,
                param_types=params,
                return_type=return_type
            )
            self.global_scope.define(symbol)
    
    def enter_scope(self, name: str) -> Scope:
        """Entra a un nuevo scope (bloque, función, etc.)"""
        self.scope_counter += 1
        new_scope = Scope(name, self.current_scope.level + 1, self.current_scope)
        self.current_scope.children.append(new_scope)
        self.current_scope = new_scope
        return new_scope
    
    def exit_scope(self):
        """Sale del scope actual y regresa al padre"""
        if self.current_scope.parent:
            self.current_scope = self.current_scope.parent
    
    def define(self, symbol: Symbol) -> bool:
        """Define un símbolo en el scope actual"""
        symbol.scope_level = self.current_scope.level
        return self.current_scope.define(symbol)
    
    def lookup(self, name: str) -> Optional[Symbol]:
        """Busca un símbolo desde el scope actual hacia arriba"""
        return self.current_scope.lookup(name)
    
    def lookup_local(self, name: str) -> Optional[Symbol]:
        """Busca un símbolo solo en el scope actual"""
        return self.current_scope.lookup_local(name)
    
    def mark_used(self, name: str):
        """Marca un símbolo como usado"""
        symbol = self.lookup(name)
        if symbol:
            symbol.used = True
    
    def mark_initialized(self, name: str):
        """Marca una variable como inicializada"""
        symbol = self.lookup(name)
        if symbol:
            symbol.initialized = True
    
    def get_unused_symbols(self) -> List[Symbol]:
        """Retorna todos los símbolos no usados"""
        unused = []
        self._collect_unused(self.global_scope, unused)
        return unused
    
    def _collect_unused(self, scope: Scope, unused: List[Symbol]):
        """Recolecta símbolos no usados recursivamente"""
        for symbol in scope.get_all_symbols():
            if not symbol.used and symbol.kind != SymbolKind.FUNCTION:
                unused.append(symbol)
        for child in scope.children:
            self._collect_unused(child, unused)
    
    def get_all_symbols(self) -> List[Symbol]:
        """Retorna todos los símbolos de todos los scopes"""
        symbols = []
        self._collect_all_symbols(self.global_scope, symbols)
        return symbols
    
    def _collect_all_symbols(self, scope: Scope, symbols: List[Symbol]):
        """Recolecta todos los símbolos recursivamente"""
        symbols.extend(scope.get_all_symbols())
        for child in scope.children:
            self._collect_all_symbols(child, symbols)
    
    def print_tree(self, scope: Optional[Scope] = None, indent: int = 0) -> str:
        """Imprime el árbol de scopes y símbolos"""
        if scope is None:
            scope = self.global_scope
        
        result = "  " * indent + f"{scope.name} (level {scope.level}):\n"
        for symbol in scope.get_all_symbols():
            used_mark = "✓" if symbol.used else "✗"
            init_mark = "✓" if symbol.initialized else "✗"
            result += "  " * (indent + 1)
            result += f"{symbol.name} [{symbol.kind.value}:{symbol.data_type.value}] "
            result += f"used:{used_mark} init:{init_mark}\n"
        
        for child in scope.children:
            result += self.print_tree(child, indent + 1)
        
        return result
    
    def __repr__(self) -> str:
        return f"SymbolTable(current_scope={self.current_scope.name})"
