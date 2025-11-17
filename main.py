from PyQt6 import QtWidgets
from app.gui import MainWindow
import sys
from automata import AutomataLexer, export_automata_dot

def main():
    print("=== ANALIZADOR LÉXICO CON AUTÓMATA ===")

    # Crear el autómata
    lexer = AutomataLexer()
    print("✅ Autómata creado exitosamente")
    print(f"   - Estados: {len(lexer.dfa.states)}")
    print(f"   - Transiciones: {sum(len(t.transitions) for t in lexer.dfa.transitions)}")

    # Exportar visualización
    export_automata_dot(lexer.dfa, "lexer_automata.dot")
    print("✅ Archivo DOT generado: lexer_automata.dot")

    # Probar con ejemplos
    examples = [
        'let x = 123;',
        'if (x >= 10) { return "hello"; }',
        'const pi = 3.1416e-10;',
        '// comentario\nfunction test() {}'
    ]

    for i, code in enumerate(examples, 1):
        print(f"\n--- Ejemplo {i} ---")
        print(f"Código: {code}")
        tokens = lexer.tokenize(code)
        for tok_type, lexeme, line, col in tokens:
            if tok_type not in ["WS", "COMMENT", "EOF"]:
                print(f"  {tok_type:8} '{lexeme}'")

    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
