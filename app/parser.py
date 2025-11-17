"""
Analizador Sintáctico LL(1) Descendente Recursivo
Implementa la gramática definida en tokens.py
"""
from typing import List, Optional
from .tokens import Token
from .ast_nodes import *


class ParseError(Exception):
    """Error de análisis sintáctico"""
    def __init__(self, token: Token, message: str):
        self.token = token
        self.message = message
        super().__init__(
            f"Error sintáctico en línea {token.line}, columna {token.col}: "
            f"{message}\nToken: {token.type} '{token.lexeme}'"
        )


class Parser:
    """
    Analizador sintáctico LL(1) descendente recursivo
    
    Gramática LL(1) simplificada:
    
    Program     -> StmtList
    StmtList    -> Stmt StmtList | ε
    Stmt        -> VarDecl | FunDecl | IfStmt | WhileStmt | ForStmt 
                 | ReturnStmt | Block | ExprStmt
    Block       -> { StmtList }
    VarDecl     -> VarKind ID InitOpt ;
    VarKind     -> let | const
    InitOpt     -> = Expr | ε
    FunDecl     -> function ID ( ParamListOpt ) Block
    ParamListOpt-> ParamList | ε
    ParamList   -> ID ParamListTail
    ParamListTail-> , ID ParamListTail | ε
    IfStmt      -> if ( Expr ) Stmt ElseOpt
    ElseOpt     -> else Stmt | ε
    WhileStmt   -> while ( Expr ) Stmt
    ForStmt     -> for ( ForInit ; ForCond ; ForIter ) Stmt
    ForInit     -> VarDecl | ExprStmt | ε
    ForCond     -> Expr | ε
    ForIter     -> Expr | ε
    ReturnStmt  -> return Expr ;
    ExprStmt    -> Expr ;
    
    Expr        -> Assign
    Assign      -> Or AssignTail
    AssignTail  -> = Assign | ε
    Or          -> And OrTail
    OrTail      -> || And OrTail | ε
    And         -> Eq AndTail
    AndTail     -> && Eq AndTail | ε
    Eq          -> Rel EqTail
    EqTail      -> (== | !=) Rel EqTail | ε
    Rel         -> Add RelTail
    RelTail     -> (< | <= | > | >=) Add RelTail | ε
    Add         -> Mul AddTail
    AddTail     -> (+ | -) Mul AddTail | ε
    Mul         -> Unary MulTail
    MulTail     -> (* | / | %) Unary MulTail | ε
    Unary       -> (! | - | +) Unary | Postfix
    Postfix     -> Primary PostfixTail
    PostfixTail -> ( ArgListOpt ) PostfixTail 
                 | [ Expr ] PostfixTail 
                 | . ID PostfixTail 
                 | ε
    Primary     -> ID | NUM | STRING | TRUE | FALSE | ( Expr )
    ArgListOpt  -> ArgList | ε
    ArgList     -> Expr ArgListTail
    ArgListTail -> , Expr ArgListTail | ε
    """
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.current = tokens[0] if tokens else None
    
    # ========================================================================
    # Utilidades básicas
    # ========================================================================
    
    def peek(self, offset: int = 0) -> Token:
        """Mira el token en la posición actual + offset"""
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return self.tokens[-1]  # EOF
    
    def advance(self) -> Token:
        """Avanza al siguiente token y retorna el actual"""
        token = self.current
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
            self.current = self.tokens[self.pos]
        return token
    
    def check(self, *types: str) -> bool:
        """Verifica si el token actual es de alguno de los tipos dados"""
        return self.current.type in types
    
    def match(self, *types: str) -> Optional[Token]:
        """Si el token actual coincide, lo consume y retorna; sino retorna None"""
        if self.check(*types):
            return self.advance()
        return None
    
    def expect(self, *types: str) -> Token:
        """Espera uno de los tipos dados, consume y retorna; sino lanza error"""
        if self.check(*types):
            return self.advance()
        expected = " o ".join(types)
        raise ParseError(
            self.current,
            f"Se esperaba {expected}, se encontró {self.current.type}"
        )
    
    def synchronize(self):
        """Sincronización de errores: avanza hasta encontrar un punto de recuperación"""
        self.advance()
        while not self.check("EOF"):
            if self.peek(-1).type == "SEMI":
                return
            if self.check("LET", "CONST", "FUNCTION", "IF", "WHILE", "FOR", "RETURN"):
                return
            self.advance()
    
    # ========================================================================
    # Punto de entrada
    # ========================================================================
    
    def parse(self) -> Program:
        """Punto de entrada del parser"""
        try:
            statements = self.parse_stmt_list()
            return Program(statements=statements)
        except ParseError as e:
            raise e
    
    # ========================================================================
    # Declaraciones y sentencias
    # ========================================================================
    
    def parse_stmt_list(self) -> List[ASTNode]:
        """StmtList -> Stmt StmtList | ε"""
        statements = []
        while not self.check("EOF", "RBRACE"):
            try:
                stmt = self.parse_stmt()
                if stmt:
                    statements.append(stmt)
            except ParseError as e:
                print(f"Error: {e}")
                self.synchronize()
        return statements
    
    def parse_stmt(self) -> Optional[ASTNode]:
        """Stmt -> VarDecl | FunDecl | IfStmt | WhileStmt | ForStmt | ReturnStmt | Block | ExprStmt"""
        if self.check("LET", "CONST"):
            return self.parse_var_decl()
        elif self.check("FUNCTION"):
            return self.parse_fun_decl()
        elif self.check("IF"):
            return self.parse_if_stmt()
        elif self.check("WHILE"):
            return self.parse_while_stmt()
        elif self.check("FOR"):
            return self.parse_for_stmt()
        elif self.check("RETURN"):
            return self.parse_return_stmt()
        elif self.check("LBRACE"):
            return self.parse_block()
        elif self.check("SEMI"):
            self.advance()  # Statement vacío
            return None
        else:
            return self.parse_expr_stmt()
    
    def parse_var_decl(self) -> VarDecl:
        """VarDecl -> VarKind ID InitOpt ;"""
        kind_token = self.expect("LET", "CONST")
        kind = kind_token.lexeme
        name_token = self.expect("ID")
        name = name_token.lexeme
        
        init = None
        if self.match("ASSIGN"):
            init = self.parse_expr()
        
        self.expect("SEMI")
        return VarDecl(kind=kind, name=name, init=init, 
                      line=kind_token.line, col=kind_token.col)
    
    def parse_fun_decl(self) -> FunctionDecl:
        """FunDecl -> function ID ( ParamListOpt ) Block"""
        func_token = self.expect("FUNCTION")
        name_token = self.expect("ID")
        name = name_token.lexeme
        
        self.expect("LPAREN")
        params = self.parse_param_list_opt()
        self.expect("RPAREN")
        
        body_block = self.parse_block()
        
        return FunctionDecl(name=name, params=params, body=body_block.statements,
                          line=func_token.line, col=func_token.col)
    
    def parse_param_list_opt(self) -> List[str]:
        """ParamListOpt -> ParamList | ε"""
        if self.check("ID"):
            return self.parse_param_list()
        return []
    
    def parse_param_list(self) -> List[str]:
        """ParamList -> ID ParamListTail"""
        params = []
        params.append(self.expect("ID").lexeme)
        
        while self.match("COMMA"):
            params.append(self.expect("ID").lexeme)
        
        return params
    
    def parse_if_stmt(self) -> IfStmt:
        """IfStmt -> if ( Expr ) Stmt ElseOpt"""
        if_token = self.expect("IF")
        self.expect("LPAREN")
        condition = self.parse_expr()
        self.expect("RPAREN")
        
        then_branch = self.parse_stmt()
        
        else_branch = None
        if self.match("ELSE"):
            else_branch = self.parse_stmt()
        
        return IfStmt(condition=condition, then_branch=then_branch, 
                     else_branch=else_branch, line=if_token.line, col=if_token.col)
    
    def parse_while_stmt(self) -> WhileStmt:
        """WhileStmt -> while ( Expr ) Stmt"""
        while_token = self.expect("WHILE")
        self.expect("LPAREN")
        condition = self.parse_expr()
        self.expect("RPAREN")
        body = self.parse_stmt()
        
        return WhileStmt(condition=condition, body=body,
                        line=while_token.line, col=while_token.col)
    
    def parse_for_stmt(self) -> ForStmt:
        """ForStmt -> for ( ForInit ; ForCond ; ForIter ) Stmt"""
        for_token = self.expect("FOR")
        self.expect("LPAREN")
        
        # Init
        init = None
        if self.check("LET", "CONST"):
            init = self.parse_var_decl()
        elif not self.check("SEMI"):
            init = self.parse_expr()
            self.expect("SEMI")
        else:
            self.expect("SEMI")
        
        # Condition
        condition = None
        if not self.check("SEMI"):
            condition = self.parse_expr()
        self.expect("SEMI")
        
        # Update
        update = None
        if not self.check("RPAREN"):
            update = self.parse_expr()
        self.expect("RPAREN")
        
        body = self.parse_stmt()
        
        return ForStmt(init=init, condition=condition, update=update, body=body,
                      line=for_token.line, col=for_token.col)
    
    def parse_return_stmt(self) -> ReturnStmt:
        """ReturnStmt -> return Expr ;"""
        return_token = self.expect("RETURN")
        value = None
        if not self.check("SEMI"):
            value = self.parse_expr()
        self.expect("SEMI")
        
        return ReturnStmt(value=value, line=return_token.line, col=return_token.col)
    
    def parse_block(self) -> Block:
        """Block -> { StmtList }"""
        lbrace = self.expect("LBRACE")
        statements = self.parse_stmt_list()
        self.expect("RBRACE")
        
        return Block(statements=statements, line=lbrace.line, col=lbrace.col)
    
    def parse_expr_stmt(self) -> ExprStmt:
        """ExprStmt -> Expr ;"""
        expr = self.parse_expr()
        self.expect("SEMI")
        return ExprStmt(expr=expr, line=expr.line, col=expr.col)
    
    # ========================================================================
    # Expresiones (precedencia de operadores)
    # ========================================================================
    
    def parse_expr(self) -> ASTNode:
        """Expr -> Assign"""
        return self.parse_assign()
    
    def parse_assign(self) -> ASTNode:
        """Assign -> Or AssignTail"""
        expr = self.parse_or()
        
        if self.match("ASSIGN"):
            # Debe ser un identificador
            if not isinstance(expr, Identifier):
                raise ParseError(self.current, "Lado izquierdo inválido en asignación")
            value = self.parse_assign()
            return Assignment(name=expr.name, value=value, line=expr.line, col=expr.col)
        
        return expr
    
    def parse_or(self) -> ASTNode:
        """Or -> And OrTail"""
        left = self.parse_and()
        
        while self.match("OR"):
            op = self.peek(-1).lexeme
            right = self.parse_and()
            left = BinaryOp(operator=op, left=left, right=right, 
                          line=left.line, col=left.col)
        
        return left
    
    def parse_and(self) -> ASTNode:
        """And -> Eq AndTail"""
        left = self.parse_eq()
        
        while self.match("AND"):
            op = self.peek(-1).lexeme
            right = self.parse_eq()
            left = BinaryOp(operator=op, left=left, right=right,
                          line=left.line, col=left.col)
        
        return left
    
    def parse_eq(self) -> ASTNode:
        """Eq -> Rel EqTail"""
        left = self.parse_rel()
        
        while self.match("EQEQ", "NEQ"):
            op = self.peek(-1).lexeme
            right = self.parse_rel()
            left = BinaryOp(operator=op, left=left, right=right,
                          line=left.line, col=left.col)
        
        return left
    
    def parse_rel(self) -> ASTNode:
        """Rel -> Add RelTail"""
        left = self.parse_add()
        
        while self.match("LT", "LE", "GT", "GE"):
            op = self.peek(-1).lexeme
            right = self.parse_add()
            left = BinaryOp(operator=op, left=left, right=right,
                          line=left.line, col=left.col)
        
        return left
    
    def parse_add(self) -> ASTNode:
        """Add -> Mul AddTail"""
        left = self.parse_mul()
        
        while self.match("PLUS", "MINUS"):
            op = self.peek(-1).lexeme
            right = self.parse_mul()
            left = BinaryOp(operator=op, left=left, right=right,
                          line=left.line, col=left.col)
        
        return left
    
    def parse_mul(self) -> ASTNode:
        """Mul -> Unary MulTail"""
        left = self.parse_unary()
        
        while self.match("STAR", "SLASH", "PERCENT"):
            op = self.peek(-1).lexeme
            right = self.parse_unary()
            left = BinaryOp(operator=op, left=left, right=right,
                          line=left.line, col=left.col)
        
        return left
    
    def parse_unary(self) -> ASTNode:
        """Unary -> (! | - | +) Unary | Postfix"""
        if self.match("BANG", "MINUS", "PLUS"):
            op_token = self.peek(-1)
            op = op_token.lexeme
            operand = self.parse_unary()
            return UnaryOp(operator=op, operand=operand, 
                          line=op_token.line, col=op_token.col)
        
        return self.parse_postfix()
    
    def parse_postfix(self) -> ASTNode:
        """Postfix -> Primary PostfixTail"""
        expr = self.parse_primary()
        
        while True:
            if self.match("LPAREN"):
                # Llamada a función
                args = self.parse_arg_list_opt()
                self.expect("RPAREN")
                expr = CallExpr(callee=expr, arguments=args,
                              line=expr.line, col=expr.col)
            
            elif self.match("LBRACK"):
                # Acceso a índice
                index = self.parse_expr()
                self.expect("RBRACK")
                expr = IndexExpr(object=expr, index=index,
                               line=expr.line, col=expr.col)
            
            elif self.match("DOT"):
                # Acceso a miembro
                member_token = self.expect("ID")
                expr = MemberExpr(object=expr, member=member_token.lexeme,
                                line=expr.line, col=expr.col)
            
            else:
                break
        
        return expr
    
    def parse_primary(self) -> ASTNode:
        """Primary -> ID | NUM | STRING | TRUE | FALSE | ( Expr )"""
        if self.match("ID"):
            token = self.peek(-1)
            return Identifier(name=token.lexeme, line=token.line, col=token.col)
        
        if self.match("NUM"):
            token = self.peek(-1)
            value = float(token.lexeme) if '.' in token.lexeme else int(token.lexeme)
            return Literal(value=value, type="number", line=token.line, col=token.col)
        
        if self.match("STRING"):
            token = self.peek(-1)
            # Quitar comillas
            value = token.lexeme[1:-1]
            return Literal(value=value, type="string", line=token.line, col=token.col)
        
        if self.match("TRUE", "FALSE"):
            token = self.peek(-1)
            value = token.lexeme == "true"
            return Literal(value=value, type="boolean", line=token.line, col=token.col)
        
        if self.match("LPAREN"):
            expr = self.parse_expr()
            self.expect("RPAREN")
            return expr
        
        raise ParseError(self.current, f"Expresión esperada, se encontró {self.current.type}")
    
    def parse_arg_list_opt(self) -> List[ASTNode]:
        """ArgListOpt -> ArgList | ε"""
        if self.check("RPAREN"):
            return []
        return self.parse_arg_list()
    
    def parse_arg_list(self) -> List[ASTNode]:
        """ArgList -> Expr ArgListTail"""
        args = []
        args.append(self.parse_expr())
        
        while self.match("COMMA"):
            args.append(self.parse_expr())
        
        return args
