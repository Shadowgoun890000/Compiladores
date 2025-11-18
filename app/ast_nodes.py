"""
Clases para representar nodos del Árbol de Sintaxis Abstracta (AST)
"""
from dataclasses import dataclass
from typing import List, Optional


# ============================================================================
# Nodo base
# ============================================================================
@dataclass
class ASTNode:
    """Clase base para todos los nodos del AST"""
    pass


# ============================================================================
# Programa y declaraciones
# ============================================================================
@dataclass
class Program(ASTNode):
    """Nodo raíz del programa"""
    statements: List[ASTNode]
    line: int = 0
    col: int = 0


@dataclass
class VarDecl(ASTNode):
    """Declaración de variable: let/const x = expr"""
    kind: str  # "let" o "const"
    name: str
    init: Optional[ASTNode] = None
    line: int = 0
    col: int = 0


@dataclass
class FunctionDecl(ASTNode):
    """Declaración de función: function name(params) { body }"""
    name: str
    params: List[str]
    body: List[ASTNode]
    line: int = 0
    col: int = 0


@dataclass
class ClassDecl(ASTNode):
    """Declaración de clase: class Name { body }"""
    name: str
    body: List[ASTNode]
    line: int = 0
    col: int = 0


# ============================================================================
# Sentencias de control
# ============================================================================
@dataclass
class IfStmt(ASTNode):
    """Sentencia if: if (condition) then_branch else else_branch"""
    condition: ASTNode
    then_branch: ASTNode
    else_branch: Optional[ASTNode] = None
    line: int = 0
    col: int = 0


@dataclass
class WhileStmt(ASTNode):
    """Sentencia while: while (condition) body"""
    condition: ASTNode
    body: ASTNode
    line: int = 0
    col: int = 0


@dataclass
class ForStmt(ASTNode):
    """Sentencia for: for (init; condition; update) body"""
    body: ASTNode
    init: Optional[ASTNode] = None
    condition: Optional[ASTNode] = None
    update: Optional[ASTNode] = None
    line: int = 0
    col: int = 0


@dataclass
class ReturnStmt(ASTNode):
    """Sentencia return: return expr"""
    value: Optional[ASTNode] = None
    line: int = 0
    col: int = 0


@dataclass
class ThrowStmt(ASTNode):
    """Sentencia throw: throw expr"""
    value: ASTNode
    line: int = 0
    col: int = 0


@dataclass
class Block(ASTNode):
    """Bloque de código: { statements }"""
    statements: List[ASTNode]
    line: int = 0
    col: int = 0


@dataclass
class ExprStmt(ASTNode):
    """Sentencia de expresión"""
    expr: ASTNode
    line: int = 0
    col: int = 0


# ============================================================================
# Expresiones
# ============================================================================
@dataclass
class BinaryOp(ASTNode):
    """Operación binaria: left op right"""
    operator: str
    left: ASTNode
    right: ASTNode
    line: int = 0
    col: int = 0


@dataclass
class UnaryOp(ASTNode):
    """Operación unaria: op operand"""
    operator: str
    operand: ASTNode
    line: int = 0
    col: int = 0


@dataclass
class Assignment(ASTNode):
    """Asignación: name = value"""
    name: str
    value: ASTNode
    line: int = 0
    col: int = 0


@dataclass
class CallExpr(ASTNode):
    """Llamada a función: callee(args)"""
    callee: ASTNode
    arguments: List[ASTNode]
    line: int = 0
    col: int = 0


@dataclass
class NewExpr(ASTNode):
    """Expresión new: new ClassName(args)"""
    class_name: str
    arguments: List[ASTNode]
    line: int = 0
    col: int = 0


@dataclass
class IndexExpr(ASTNode):
    """Acceso a índice: object[index]"""
    object: ASTNode
    index: ASTNode
    line: int = 0
    col: int = 0


@dataclass
class MemberExpr(ASTNode):
    """Acceso a miembro: object.member"""
    object: ASTNode
    member: str
    line: int = 0
    col: int = 0


# ============================================================================
# Literales y primitivas
# ============================================================================
@dataclass
class Identifier(ASTNode):
    """Identificador: variable name"""
    name: str
    line: int = 0
    col: int = 0


@dataclass
class Literal(ASTNode):
    """Literal: número, string, booleano"""
    value: any
    type: str  # "number", "string", "boolean"
    line: int = 0
    col: int = 0


# ============================================================================
# Manejo de Try-Catch
# ============================================================================
@dataclass
class TryStmt(ASTNode):
    """Sentencia try-catch: try { } catch (error) { }"""
    try_block: Block
    catch_param: Optional[str] = None
    catch_block: Optional[Block] = None
    finally_block: Optional[Block] = None
    line: int = 0
    col: int = 0


# ============================================================================
# Utilidades para imprimir el AST
# ============================================================================
def ast_to_string(node: ASTNode, indent: int = 0) -> str:
    """Convierte un nodo AST a una representación en string legible"""
    prefix = "  " * indent

    if isinstance(node, Program):
        result = f"{prefix}Program:\n"
        for stmt in node.statements:
            result += ast_to_string(stmt, indent + 1)
        return result

    elif isinstance(node, VarDecl):
        result = f"{prefix}VarDecl({node.kind} {node.name})\n"
        if node.init:
            result += ast_to_string(node.init, indent + 1)
        return result

    elif isinstance(node, FunctionDecl):
        params = ", ".join(node.params)
        result = f"{prefix}FunctionDecl({node.name}({params}))\n"
        for stmt in node.body:
            result += ast_to_string(stmt, indent + 1)
        return result

    elif isinstance(node, ClassDecl):
        result = f"{prefix}ClassDecl({node.name})\n"
        for stmt in node.body:
            result += ast_to_string(stmt, indent + 1)
        return result

    elif isinstance(node, IfStmt):
        result = f"{prefix}IfStmt:\n"
        result += f"{prefix}  Condition:\n"
        result += ast_to_string(node.condition, indent + 2)
        result += f"{prefix}  Then:\n"
        result += ast_to_string(node.then_branch, indent + 2)
        if node.else_branch:
            result += f"{prefix}  Else:\n"
            result += ast_to_string(node.else_branch, indent + 2)
        return result

    elif isinstance(node, WhileStmt):
        result = f"{prefix}WhileStmt:\n"
        result += f"{prefix}  Condition:\n"
        result += ast_to_string(node.condition, indent + 2)
        result += f"{prefix}  Body:\n"
        result += ast_to_string(node.body, indent + 2)
        return result

    elif isinstance(node, ForStmt):
        result = f"{prefix}ForStmt:\n"
        if node.init:
            result += f"{prefix}  Init:\n"
            result += ast_to_string(node.init, indent + 2)
        if node.condition:
            result += f"{prefix}  Condition:\n"
            result += ast_to_string(node.condition, indent + 2)
        if node.update:
            result += f"{prefix}  Update:\n"
            result += ast_to_string(node.update, indent + 2)
        result += f"{prefix}  Body:\n"
        result += ast_to_string(node.body, indent + 2)
        return result

    elif isinstance(node, ReturnStmt):
        result = f"{prefix}ReturnStmt:\n"
        if node.value:
            result += ast_to_string(node.value, indent + 1)
        return result

    elif isinstance(node, ThrowStmt):
        result = f"{prefix}ThrowStmt:\n"
        if node.value:
            result += ast_to_string(node.value, indent + 1)
        return result

    elif isinstance(node, Block):
        result = f"{prefix}Block:\n"
        for stmt in node.statements:
            result += ast_to_string(stmt, indent + 1)
        return result

    elif isinstance(node, ExprStmt):
        result = f"{prefix}ExprStmt:\n"
        result += ast_to_string(node.expr, indent + 1)
        return result

    elif isinstance(node, BinaryOp):
        result = f"{prefix}BinaryOp({node.operator})\n"
        result += ast_to_string(node.left, indent + 1)
        result += ast_to_string(node.right, indent + 1)
        return result

    elif isinstance(node, UnaryOp):
        result = f"{prefix}UnaryOp({node.operator})\n"
        result += ast_to_string(node.operand, indent + 1)
        return result

    elif isinstance(node, Assignment):
        result = f"{prefix}Assignment({node.name})\n"
        result += ast_to_string(node.value, indent + 1)
        return result

    elif isinstance(node, CallExpr):
        result = f"{prefix}CallExpr:\n"
        result += f"{prefix}  Callee:\n"
        result += ast_to_string(node.callee, indent + 2)
        if node.arguments:
            result += f"{prefix}  Args:\n"
            for arg in node.arguments:
                result += ast_to_string(arg, indent + 2)
        return result

    elif isinstance(node, NewExpr):
        result = f"{prefix}NewExpr(new {node.class_name})\n"
        if node.arguments:
            result += f"{prefix}  Args:\n"
            for arg in node.arguments:
                result += ast_to_string(arg, indent + 2)
        return result

    elif isinstance(node, IndexExpr):
        result = f"{prefix}IndexExpr:\n"
        result += ast_to_string(node.object, indent + 1)
        result += ast_to_string(node.index, indent + 1)
        return result

    elif isinstance(node, MemberExpr):
        result = f"{prefix}MemberExpr(.{node.member})\n"
        result += ast_to_string(node.object, indent + 1)
        return result

    elif isinstance(node, Identifier):
        return f"{prefix}Identifier({node.name})\n"

    elif isinstance(node, Literal):
        return f"{prefix}Literal({node.type}: {node.value})\n"

    else:
        return f"{prefix}{type(node).__name__}\n"