from dataclasses import dataclass

NON_TERMINALS = [
    "Program","StmtList","Stmt","Block","VarDecl","VarKind","VarDeclList","VarDeclListTail",
    "VarInit","InitOpt","FunDecl","ParamListOpt","ParamList","ParamListTail","IfStmt","ElseOpt",
    "WhileStmt","ForStmt","ForInit","ForCond","ForIter","ReturnStmt","ExprStmt","Expr","Assign",
    "AssignTail","Or","OrTail","And","AndTail","Eq","EqTail","Rel","RelTail","Add","AddTail",
    "Mul","MulTail","Unary","Postfix","PostfixTail","Primary","ArgListOpt","ArgList","ArgListTail"
]

KEYWORDS = {
    "let":"LET","const":"CONST","function":"FUNCTION",
    "if":"IF","else":"ELSE","while":"WHILE","for":"FOR",
    "return":"RETURN","true":"TRUE","false":"FALSE",
}

OPERATORS = [
    "===","!==","==","!=","*=","+=","-=",
    "<=", ">=", "||", "&&","{","}","(",
    ")","[","]",";",":","'","`",",",".",
    "=","<",">","+","-","*","/","%","!","${"
]

TOKEN_NAME = {
    "{":"LBRACE","}":"RBRACE","(":"LPAREN",")":"RPAREN","[":"LBRACK","]":"RBRACK",
    ";":"SEMI","'":"APOSTROPHE",",":"COMMA",".":"DOT",":":"COLON","`":"BACKTICK",
    "===":"STRICT_EQ","!==":"STRICT_NEQ","=":"ASSIGN","==":"EQEQ","!=":"NEQ","*=":"MUL_ASSIGN",
    "-=":"SUB_ASSIGN","+=":"ADD_ASSIGN","<":"LT","<=":"LE",">":"GT",">=":"GE","||":"OR",
    "&&":"AND","+":"PLUS","-":"MINUS","*":"STAR","/":"SLASH","%":"PERCENT","!":"BANG",
    "${":"TEMPLATE_START"
}

@dataclass(frozen=True)
class Token:
    type: str
    lexeme: str
    line: int
    col: int

class LexError(Exception):
    def __init__(self, line:int, col:int, lexeme:str):
        super().__init__(f"Error léxico en línea {line}, columna {col}: {lexeme!r}")
        self.line=line; self.col=col; self.lexeme=lexeme
