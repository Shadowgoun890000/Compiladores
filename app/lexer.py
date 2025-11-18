import re
from .tokens import KEYWORDS, OPERATORS, TOKEN_NAME, Token, LexError

RE_STRING = r'"[^"\n]*"'
RE_TEMPLATE_STRING = r'`([^`\\]|\\.)*`'
RE_NUM    = r'(?:\d+\.\d+(?:[eE][+-]?\d+)?|\d+(?:[eE][+-]?\d+)?|\.\d+(?:[eE][+-]?\d+)?)'
RE_ID     = r'[A-Za-z_][A-Za-z_0-9]*'
RE_WS     = r'[ \t\r\n]+'

class Lexer:
    def __init__(self, src:str):
        self.src=src; self.i=0; self.line=1; self.col=1; self.n=len(src)

    def eof(self): return self.i>=self.n
    def peek(self,k=0): 
        j=self.i+k; return self.src[j] if j<self.n else ""
    def get(self):
        """Obtiene el carácter actual y avanza (similar a advance(1))"""
        if self.eof():
            return ""
        ch = self.src[self.i]
        self.advance(1)
        return ch
    def advance(self,c=1):
        for _ in range(c):
            ch=self.src[self.i]; self.i+=1
            if ch=="\n": self.line+=1; self.col=1
            else: self.col+=1

    def _m(self,pat): 
        m=re.match(pat, self.src[self.i:]); 
        return m.group(0) if m else None

    def _skip(self):
        while True:
            m=self._m(RE_WS)
            if m: self.advance(len(m)); continue
            if self.src[self.i:self.i+2]=="//":
                while not self.eof() and self.peek()!="\n": self.advance()
                continue
            break

    def tokenize(self):
        toks=[]
        while not self.eof():
            self._skip()
            if self.eof(): break
            L,C=self.line,self.col

            if self.peek() == '`':
                template_content = []
                self.advance()  # Consumir backtick inicial
                start_line, start_col = self.line, self.col

                while not self.eof() and self.peek() != '`':
                    if self.peek() == '$' and self.peek(1) == '{':
                        # Token de inicio de interpolación
                        toks.append(Token("TEMPLATE_START", "${", self.line, self.col))
                        self.advance(2)
                        # Parsear expresión dentro de ${}
                        # Esto requiere lógica adicional
                    else:
                        # Accumular contenido del template
                        ch = self.get()
                        template_content.append(ch)

                if self.peek() == '`':
                    self.advance()
                else:
                    raise LexError(L, C, "Template string no cerrado")

                continue
            if self.peek()=='"':
                m=self._m(RE_STRING)
                if not m: raise LexError(L,C,self.src[self.i:self.i+20])
                toks.append(Token("STRING",m,L,C)); self.advance(len(m)); continue

            m=self._m(RE_NUM)
            if m: toks.append(Token("NUM",m,L,C)); self.advance(len(m)); continue

            m=self._m(RE_ID)
            if m:
                t=KEYWORDS.get(m,"ID")
                toks.append(Token(t,m,L,C)); self.advance(len(m)); continue

            op=None
            for o in sorted(OPERATORS, key=lambda s:(-len(s), s)):
                if self.src.startswith(o,self.i): op=o; break
            if op:
                toks.append(Token(TOKEN_NAME[op], op, L, C)); self.advance(len(op)); continue

            raise LexError(L,C,self.peek())
        toks.append(Token("EOF","EOF", self.line, self.col))
        return toks
