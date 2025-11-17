import graphviz
from IPython.display import Image, display


def create_automata_diagram():
    # Crear el grafo dirigido
    dot = graphviz.Digraph('Lexer_Automata', comment='Autómata del Analizador Léxico')
    dot.attr(rankdir='LR', size='12,8', dpi='300')
    dot.attr('node', shape='circle', fontsize='10')

    # Definir estados con sus propiedades
    states = {
        'S0': {'label': 'INICIO', 'shape': 'circle', 'color': 'blue'},
        'S1': {'label': 'ID/Keyword', 'shape': 'doublecircle', 'color': 'green'},
        'S2': {'label': 'NUM Entero', 'shape': 'doublecircle', 'color': 'green'},
        'S3': {'label': 'Punto', 'shape': 'circle', 'color': 'black'},
        'S4': {'label': 'String', 'shape': 'circle', 'color': 'black'},
        'S5': {'label': 'División', 'shape': 'circle', 'color': 'black'},
        'S6': {'label': 'Op 2 chars', 'shape': 'circle', 'color': 'black'},
        'S7': {'label': 'Operador', 'shape': 'doublecircle', 'color': 'green'},
        'S8': {'label': 'WS', 'shape': 'doublecircle', 'color': 'gray'},
        'S9': {'label': 'NUM Decimal', 'shape': 'doublecircle', 'color': 'green'},
        'S10': {'label': 'Exponente', 'shape': 'circle', 'color': 'black'},
        'S11': {'label': 'STRING', 'shape': 'doublecircle', 'color': 'green'},
        'S12': {'label': 'COMMENT', 'shape': 'doublecircle', 'color': 'gray'},
        'S13': {'label': '==,!=,<,>', 'shape': 'doublecircle', 'color': 'green'},
        'S14': {'label': '||', 'shape': 'doublecircle', 'color': 'green'},
        'S15': {'label': '&&', 'shape': 'doublecircle', 'color': 'green'},
        'S16': {'label': 'Signo Exp', 'shape': 'circle', 'color': 'black'},
        'S17': {'label': 'NUM Exp', 'shape': 'doublecircle', 'color': 'green'}
    }

    # Agregar estados al grafo
    for state, props in states.items():
        dot.node(state, props['label'], shape=props['shape'], color=props['color'])

    # Nodo inicial ficticio
    dot.node('start', '', shape='point', width='0')
    dot.edge('start', 'S0')

    # TRANSICIONES DESDE S0
    dot.edge('S0', 'S1', label='A-Z, a-z, _')
    dot.edge('S0', 'S2', label='0-9')
    dot.edge('S0', 'S3', label='"."')
    dot.edge('S0', 'S4', label='"\""')
    dot.edge('S0', 'S5', label='"/"')
    dot.edge('S0', 'S6', label='=, !, <, >, |, &')
    dot.edge('S0', 'S7', label='{ } ( ) [ ] ; , + - * %')
    dot.edge('S0', 'S8', label='espacio, \\t, \\n, \\r')

    # TRANSICIONES DESDE S1 (Identificadores)
    dot.edge('S1', 'S1', label='A-Z, a-z, 0-9, _')

    # TRANSICIONES DESDE S2 (Números enteros)
    dot.edge('S2', 'S2', label='0-9')
    dot.edge('S2', 'S9', label='"."')
    dot.edge('S2', 'S10', label='e, E')

    # TRANSICIONES DESDE S3 (Punto)
    dot.edge('S3', 'S9', label='0-9')

    # TRANSICIONES DESDE S4 (String)
    dot.edge('S4', 'S4', label='[^"\\n]')
    dot.edge('S4', 'S11', label='"\""')

    # TRANSICIONES DESDE S5 (División)
    dot.edge('S5', 'S12', label='"/"')

    # TRANSICIONES DESDE S6 (Operadores 2 chars)
    dot.edge('S6', 'S13', label='=')
    dot.edge('S6', 'S14', label='|')
    dot.edge('S6', 'S15', label='&')

    # TRANSICIONES DESDE S9 (Decimal)
    dot.edge('S9', 'S9', label='0-9')
    dot.edge('S9', 'S10', label='e, E')

    # TRANSICIONES DESDE S10 (Exponente)
    dot.edge('S10', 'S16', label='+, -')
    dot.edge('S10', 'S17', label='0-9')
    dot.edge('S16', 'S17', label='0-9')

    # TRANSICIONES DESDE S12 (Comentario)
    dot.edge('S12', 'S12', label='[^\\n]')

    # Configurar el estilo del grafo
    dot.attr('edge', fontsize='8')

    return dot


# Crear y mostrar el diagrama
print("🔄 Generando diagrama del autómata...")
automata_diagram = create_automata_diagram()

# Renderizar el diagrama
try:
    # Intentar renderizar como PNG
    automata_diagram.render('automata_lexer', format='png', cleanup=True)
    print("✅ Diagrama generado: automata_lexer.png")

    # Mostrar la imagen en el notebook
    display(Image(filename='automata_lexer.png'))

except Exception as e:
    print(f"⚠️ No se pudo generar la imagen: {e}")
    print("📝 Mostrando código DOT:")
    print(automata_diagram.source)