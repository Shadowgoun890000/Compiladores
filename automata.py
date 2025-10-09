# [file name]: automata.py
from dataclasses import dataclass
from typing import Dict, Set, List, Optional, Tuple


@dataclass(frozen=True)
class DFAState:
    id: int
    is_accepting: bool
    token_type: Optional[str] = None
    description: str = ""


class DFATransition:
    def __init__(self):
        self.transitions: Dict[str, int] = {}
        self.default_state: Optional[int] = None

    def add_transition(self, chars: str, state_id: int):
        for char in chars:
            self.transitions[char] = state_id

    def get_next_state(self, char: str) -> Optional[int]:
        return self.transitions.get(char)


class LexerDFA:
    def __init__(self):
        self.states: List[DFAState] = []
        self.transitions: List[DFATransition] = []
        self.current_state: int = 0
        self.start_state: int = 0

    def add_state(self, is_accepting: bool = False, token_type: str = None, description: str = "") -> int:
        state_id = len(self.states)
        self.states.append(DFAState(state_id, is_accepting, token_type, description))
        self.transitions.append(DFATransition())
        return state_id

    def add_transition(self, from_state: int, to_state: int, chars: str):
        self.transitions[from_state].add_transition(chars, to_state)

    def add_keyword_transition(self, from_state: int, to_state: int):
        """Transición para caracteres de identificadores"""
        self.add_transition(from_state, to_state, "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_")

    def add_digit_transition(self, from_state: int, to_state: int):
        """Transición para dígitos"""
        self.add_transition(from_state, to_state, "0123456789")

    def add_whitespace_transition(self, from_state: int, to_state: int):
        """Transición para espacios en blanco"""
        self.add_transition(from_state, to_state, " \t\r\n")

    def reset(self):
        self.current_state = self.start_state

    def process_char(self, char: str) -> Tuple[bool, Optional[str]]:
        """Procesa un carácter y retorna (aceptación, tipo_token)"""
        transition = self.transitions[self.current_state]
        next_state = transition.get_next_state(char)

        if next_state is None:
            # No hay transición para este carácter
            current_state_info = self.states[self.current_state]
            if current_state_info.is_accepting:
                return True, current_state_info.token_type
            else:
                return False, None

        self.current_state = next_state
        current_state_info = self.states[self.current_state]

        return current_state_info.is_accepting, current_state_info.token_type


def create_lexer_automata() -> LexerDFA:
    """Crea el autómata completo para el lexer"""
    dfa = LexerDFA()

    # Definir todos los estados
    S0 = dfa.add_state(False, None, "Estado inicial")
    S1 = dfa.add_state(True, "ID", "Identificador/Keyword")
    S2 = dfa.add_state(True, "NUM", "Número entero")
    S3 = dfa.add_state(False, None, "Punto o operador DOT")
    S4 = dfa.add_state(False, None, "String en proceso")
    S5 = dfa.add_state(False, None, "División o comentario")
    S6 = dfa.add_state(False, None, "Operadores de 2 caracteres")
    S7 = dfa.add_state(True, "OPERATOR", "Operadores de 1 carácter")
    S8 = dfa.add_state(True, "WS", "Whitespace")
    S9 = dfa.add_state(True, "NUM", "Número decimal")
    S10 = dfa.add_state(False, None, "Exponente")
    S11 = dfa.add_state(True, "STRING", "String completo")
    S12 = dfa.add_state(True, "COMMENT", "Comentario")
    S13 = dfa.add_state(True, "OPERATOR", "Operadores ==, !=, <=, >=")
    S14 = dfa.add_state(True, "OPERATOR", "Operador ||")
    S15 = dfa.add_state(True, "OPERATOR", "Operador &&")
    S16 = dfa.add_state(False, None, "Signo exponente")
    S17 = dfa.add_state(True, "NUM", "Número con exponente")

    dfa.start_state = S0

    # Transiciones desde S0 (Estado inicial)
    dfa.add_keyword_transition(S0, S1)  # Letras y _ → Identificadores
    dfa.add_digit_transition(S0, S2)  # Dígitos → Números
    dfa.add_transition(S0, S3, ".")  # Punto → Decimal o DOT
    dfa.add_transition(S0, S4, "\"")  # Comilla → String
    dfa.add_transition(S0, S5, "/")  # Slash → División o comentario
    dfa.add_whitespace_transition(S0, S8)  # Espacios → Whitespace

    # Operadores desde S0
    dfa.add_transition(S0, S6, "=!<>|&")  # Operadores de 2 chars
    dfa.add_transition(S0, S7, "{}()[];,+*-%")  # Operadores de 1 char

    # Transiciones desde S1 (Identificadores)
    dfa.add_keyword_transition(S1, S1)
    dfa.add_digit_transition(S1, S1)

    # Transiciones desde S2 (Números enteros)
    dfa.add_digit_transition(S2, S2)
    dfa.add_transition(S2, S9, ".")  # Punto → Decimal
    dfa.add_transition(S2, S10, "eE")  # e/E → Exponente

    # Transiciones desde S3 (Punto)
    dfa.add_digit_transition(S3, S9)  # Dígito después de punto → Decimal

    # Transiciones desde S4 (String)
    dfa.add_transition(S4, S4, "".join(chr(i) for i in range(32, 127) if chr(i) not in ['"', '\n', '\\']))
    dfa.add_transition(S4, S11, "\"")  # Comilla de cierre → String completo

    # Transiciones desde S5 (División)
    dfa.add_transition(S5, S12, "/")  # Doble slash → Comentario

    # Transiciones desde S6 (Operadores de 2 chars)
    dfa.add_transition(S6, S13, "=")  # = después de =!<> → ==, !=, <=, >=
    dfa.add_transition(S6, S14, "|")  # | después de | → ||
    dfa.add_transition(S6, S15, "&")  # & después de & → &&

    # Transiciones desde S9 (Decimal)
    dfa.add_digit_transition(S9, S9)
    dfa.add_transition(S9, S10, "eE")  # e/E → Exponente

    # Transiciones desde S10 (Exponente)
    dfa.add_transition(S10, S16, "+-")  # Signo del exponente
    dfa.add_digit_transition(S10, S17)  # Dígito directo en exponente
    dfa.add_digit_transition(S16, S17)  # Dígito después de signo exponente

    # Transiciones desde S12 (Comentario)
    dfa.add_transition(S12, S12, "".join(chr(i) for i in range(32, 127) if chr(i) != '\n'))

    return dfa


class AutomataLexer:
    def __init__(self):
        self.dfa = create_lexer_automata()
        self.buffer = ""
        self.current_line = 1
        self.current_col = 1
        self.start_line = 1
        self.start_col = 1

    def tokenize(self, source_code: str) -> List[Tuple[str, str, int, int]]:
        """Tokeniza el código fuente usando el autómata"""
        tokens = []
        self.dfa.reset()
        self.buffer = ""
        self.current_line = 1
        self.current_col = 1

        i = 0
        n = len(source_code)

        while i < n:
            char = source_code[i]
            self.start_line = self.current_line
            self.start_col = self.current_col

            # Actualizar posición
            if char == '\n':
                self.current_line += 1
                self.current_col = 1
            else:
                self.current_col += 1

            # Procesar carácter con el autómata
            is_accepting, token_type = self.dfa.process_char(char)

            if is_accepting:
                # Verificar si es un keyword
                lexeme = self.buffer + char
                final_token_type = self._get_token_type(lexeme, token_type)

                tokens.append((final_token_type, lexeme, self.start_line, self.start_col))

                # Reiniciar para el próximo token
                self.buffer = ""
                self.dfa.reset()
            else:
                self.buffer += char

            i += 1

        # Procesar último token si queda en buffer
        if self.buffer and self.dfa.states[self.dfa.current_state].is_accepting:
            token_type = self.dfa.states[self.dfa.current_state].token_type
            final_token_type = self._get_token_type(self.buffer, token_type)
            tokens.append((final_token_type, self.buffer, self.start_line, self.start_col))

        # Agregar EOF
        tokens.append(("EOF", "EOF", self.current_line, self.current_col))

        return tokens

    def _get_token_type(self, lexeme: str, detected_type: str) -> str:
        """Determina el tipo final del token (keywords, operadores específicos)"""
        if detected_type == "ID":
            # Verificar si es keyword
            keywords = {
                "let": "LET", "const": "CONST", "function": "FUNCTION",
                "if": "IF", "else": "ELSE", "while": "WHILE", "for": "FOR",
                "return": "RETURN", "true": "TRUE", "false": "FALSE"
            }
            return keywords.get(lexeme, "ID")

        elif detected_type == "OPERATOR":
            # Mapear operadores específicos
            operator_map = {
                "==": "EQEQ", "!=": "NEQ", "<=": "LE", ">=": "GE",
                "||": "OR", "&&": "AND", "=": "ASSIGN", "<": "LT", ">": "GT",
                "+": "PLUS", "-": "MINUS", "*": "STAR", "/": "SLASH",
                "%": "PERCENT", "!": "BANG", "{": "LBRACE", "}": "RBRACE",
                "(": "LPAREN", ")": "RPAREN", "[": "LBRACK", "]": "RBRACK",
                ";": "SEMI", ",": "COMMA", ".": "DOT"
            }
            return operator_map.get(lexeme, "OPERATOR")

        return detected_type


# [file name]: automata_visualizer.py
def export_automata_dot(dfa: LexerDFA, filename: str = "automata.dot"):
    """Exporta el autómata a formato DOT para Graphviz"""
    dot_content = ["digraph DFA {", "  rankdir=LR;", "  node [shape=circle];"]

    # Estado inicial
    dot_content.append(f'  __start__ [shape=point];')
    dot_content.append(f'  __start__ -> S{dfa.start_state};')

    # Estados
    for state in dfa.states:
        shape = "doublecircle" if state.is_accepting else "circle"
        label = f"S{state.id}\\n{state.description}"
        if state.token_type:
            label += f"\\nToken: {state.token_type}"
        dot_content.append(f'  S{state.id} [shape={shape}, label="{label}"];')

    # Transiciones
    for from_state, transition in enumerate(dfa.transitions):
        # Agrupar transiciones por estado destino
        transitions_by_dest = {}
        for char, to_state in transition.transitions.items():
            transitions_by_dest.setdefault(to_state, []).append(char)

        for to_state, chars in transitions_by_dest.items():
            # Simplificar la etiqueta para caracteres consecutivos
            if len(chars) > 5:
                # Agrupar rangos
                sorted_chars = sorted(chars)
                ranges = []
                start = end = sorted_chars[0]

                for char in sorted_chars[1:] + [None]:
                    if char and ord(char) == ord(end) + 1:
                        end = char
                    else:
                        if ord(end) - ord(start) >= 2:
                            ranges.append(f"{start}-{end}")
                        elif ord(end) - ord(start) == 1:
                            ranges.extend([start, end])
                        else:
                            ranges.append(start)
                        if char:
                            start = end = char
                        else:
                            break

                label = ",".join(ranges[:3]) + ("..." if len(ranges) > 3 else "")
            else:
                label = ",".join(chars)

            dot_content.append(f'  S{from_state} -> S{to_state} [label="{label}"];')

    dot_content.append("}")

    with open(filename, 'w', encoding='utf-8') as f:
        f.write("\n".join(dot_content))

    print(f"Autómata exportado a {filename}")
    print("Puedes visualizarlo con: dot -Tpng automata.dot -o automata.png")


# [file name]: test_automata.py
def test_automata():
    """Prueba el autómata con código de ejemplo"""
    lexer = AutomataLexer()

    test_code = '''
let x = 42;
const name = "hello";
function add(a, b) {
    return a + b;
}
if (x <= 100) {
    x = x * 2.5e-3;
}
// This is a comment
'''

    print("=== PRUEBA DEL AUTÓMATA ===")
    print("Código de prueba:")
    print(test_code)
    print("\nTokens encontrados:")
    print("-" * 60)

    tokens = lexer.tokenize(test_code)

    for token_type, lexeme, line, col in tokens:
        if token_type not in ["WS", "COMMENT"]:  # Filtrar whitespace y comentarios
            print(f"Linea {line:2d}, Col {col:2d}: {token_type:10} '{lexeme}'")

    # Exportar autómata
    export_automata_dot(lexer.dfa)


if __name__ == "__main__":
    test_automata()