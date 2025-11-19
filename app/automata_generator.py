import os
import graphviz
from typing import Dict, List, Set, Tuple
from .ast_nodes import *


class AutomataGenerator:
    """
    Genera diagramas de autómatas para diferentes estructuras del código
    """

    def __init__(self):
        self.state_counter = 0
        self.transitions = []
        self.states = set()
        self.final_states = set()

    def generate_control_flow_automata(self, node: ASTNode, title: str = "Autómata de Flujo de Control") -> str:
        """
        Genera un autómata de flujo de control para una estructura del código
        """
        self.state_counter = 0
        self.transitions = []
        self.states = set()
        self.final_states = set()

        start_state = self._new_state("Inicio")
        final_state = self._new_state("Fin")
        self.final_states.add(final_state)

        # Generar el autómata según el tipo de nodo
        if isinstance(node, FunctionDecl):
            self._generate_function_automata(node, start_state, final_state)
        elif isinstance(node, IfStmt):
            self._generate_if_automata(node, start_state, final_state)
        elif isinstance(node, WhileStmt):
            self._generate_while_automata(node, start_state, final_state)
        elif isinstance(node, ForStmt):
            self._generate_for_automata(node, start_state, final_state)
        elif isinstance(node, Program):
            self._generate_program_automata(node, start_state, final_state)
        else:
            self._generate_generic_automata(node, start_state, final_state)

        return self._render_automata(title)

    def _generate_function_automata(self, node: FunctionDecl, start: str, end: str):
        """Genera autómata para una función"""
        params_state = self._new_state(f"Parámetros: {', '.join(node.params)}")
        body_start = self._new_state("Inicio Cuerpo")
        body_end = self._new_state("Fin Cuerpo")

        self._add_transition(start, params_state, f"function {node.name}")
        self._add_transition(params_state, body_start, "→")

        # Procesar cuerpo de la función
        current = body_start
        for stmt in node.body:
            next_state = self._new_state("Siguiente")
            self._process_statement(stmt, current, next_state)
            current = next_state

        self._add_transition(current, body_end, "→")
        self._add_transition(body_end, end, "return")

    def _generate_if_automata(self, node: IfStmt, start: str, end: str):
        """Genera autómata para if-else"""
        cond_state = self._new_state("Condición")
        then_start = self._new_state("Then")
        then_end = self._new_state("Fin Then")

        self._add_transition(start, cond_state, "if")
        self._add_transition(cond_state, then_start, "verdadero")

        # Procesar rama then
        self._process_statement(node.then_branch, then_start, then_end)

        if node.else_branch:
            else_start = self._new_state("Else")
            else_end = self._new_state("Fin Else")

            self._add_transition(cond_state, else_start, "falso")
            self._add_transition(then_end, end, "→")
            self._process_statement(node.else_branch, else_start, else_end)
            self._add_transition(else_end, end, "→")
        else:
            self._add_transition(cond_state, end, "falso")
            self._add_transition(then_end, end, "→")

    def _generate_while_automata(self, node: WhileStmt, start: str, end: str):
        """Genera autómata para while"""
        cond_state = self._new_state("Condición")
        body_start = self._new_state("Cuerpo")
        body_end = self._new_state("Fin Cuerpo")

        self._add_transition(start, cond_state, "while")
        self._add_transition(cond_state, body_start, "verdadero")
        self._add_transition(cond_state, end, "falso")

        # Procesar cuerpo
        self._process_statement(node.body, body_start, body_end)
        self._add_transition(body_end, cond_state, "→")  # Loop back

    def _generate_for_automata(self, node: ForStmt, start: str, end: str):
        """Genera autómata para for"""
        init_state = self._new_state("Inicialización")
        cond_state = self._new_state("Condición")
        body_start = self._new_state("Cuerpo")
        body_end = self._new_state("Fin Cuerpo")
        update_state = self._new_state("Actualización")

        self._add_transition(start, init_state, "for")

        if node.init:
            self._add_transition(init_state, cond_state, "init")
        else:
            self._add_transition(init_state, cond_state, "→")

        self._add_transition(cond_state, body_start, "verdadero")
        self._add_transition(cond_state, end, "falso")

        # Procesar cuerpo
        self._process_statement(node.body, body_start, body_end)
        self._add_transition(body_end, update_state, "→")

        if node.update:
            self._add_transition(update_state, cond_state, "update")
        else:
            self._add_transition(update_state, cond_state, "→")

    def _generate_program_automata(self, node: Program, start: str, end: str):
        """Genera autómata para el programa completo"""
        current = start

        for stmt in node.statements:
            next_state = self._new_state("Siguiente")
            self._process_statement(stmt, current, next_state)
            current = next_state

        self._add_transition(current, end, "→")

    def _generate_generic_automata(self, node: ASTNode, start: str, end: str):
        """Genera autómata genérico para cualquier nodo"""
        node_type = type(node).__name__
        middle_state = self._new_state(f"Ejecutar {node_type}")

        self._add_transition(start, middle_state, node_type)
        self._add_transition(middle_state, end, "→")

    def _process_statement(self, stmt: ASTNode, from_state: str, to_state: str):
        """Procesa una sentencia y genera sus transiciones"""
        if isinstance(stmt, Block):
            current = from_state
            for sub_stmt in stmt.statements:
                next_state = self._new_state("Bloque")
                self._process_statement(sub_stmt, current, next_state)
                current = next_state
            self._add_transition(current, to_state, "→")
        elif isinstance(stmt, IfStmt):
            self._generate_if_automata(stmt, from_state, to_state)
        elif isinstance(stmt, WhileStmt):
            self._generate_while_automata(stmt, from_state, to_state)
        elif isinstance(stmt, ForStmt):
            self._generate_for_automata(stmt, from_state, to_state)
        else:
            node_type = type(stmt).__name__
            self._add_transition(from_state, to_state, node_type)

    def _new_state(self, label: str) -> str:
        """Crea un nuevo estado"""
        state_id = f"S{self.state_counter}"
        self.states.add((state_id, label))
        self.state_counter += 1
        return state_id

    def _add_transition(self, from_state: str, to_state: str, label: str):
        """Añade una transición"""
        self.transitions.append((from_state, to_state, label))

    def _render_automata(self, title: str) -> str:
        """Renderiza el autómata usando Graphviz"""
        try:
            dot = graphviz.Digraph(comment=title)
            dot.attr(rankdir='TB')
            dot.attr(label=title)
            dot.attr(labelloc='t')

            # Añadir estados
            for state_id, label in self.states:
                if state_id in self.final_states:
                    dot.node(state_id, label, shape='doublecircle')
                else:
                    dot.node(state_id, label, shape='circle')

            # Añadir transiciones
            for from_state, to_state, label in self.transitions:
                dot.edge(from_state, to_state, label=label)

            # Guardar el archivo
            output_dir = "exports"
            os.makedirs(output_dir, exist_ok=True)
            file_path = os.path.join(output_dir, "automata")

            dot.render(file_path, format='png', cleanup=True)
            return file_path + '.png'

        except Exception as e:
            return f"Error generando autómata: {str(e)}"


class LexerAutomata:
    """
    Genera el autómata del lexer basado en los patrones de tokens
    """

    @staticmethod
    def generate_lexer_automata() -> str:
        """Genera el diagrama del autómata del lexer"""
        try:
            dot = graphviz.Digraph(comment='Autómata del Lexer')
            dot.attr(rankdir='LR')
            dot.attr(label='Autómata del Analizador Léxico')
            dot.attr(labelloc='t')

            # Estados
            dot.node('start', '', shape='point')
            dot.node('S0', 'Inicio', shape='circle')
            dot.node('S1', 'ID/Keyword', shape='doublecircle')
            dot.node('S2', 'NUM Entero', shape='doublecircle')
            dot.node('S3', 'Punto', shape='circle')
            dot.node('S4', 'NUM Decimal', shape='doublecircle')
            dot.node('S5', 'Exponente', shape='circle')
            dot.node('S6', 'Signo Exp', shape='circle')
            dot.node('S7', 'NUM Exp', shape='doublecircle')
            dot.node('S8', 'String', shape='doublecircle')
            dot.node('S9', 'Operador', shape='doublecircle')
            dot.node('S10', 'WS', shape='doublecircle')

            # Transiciones
            dot.edge('start', 'S0')
            dot.edge('S0', 'S1', label='A-Z, a-z, _')
            dot.edge('S1', 'S1', label='A-Z, a-z, 0-9, _')
            dot.edge('S0', 'S2', label='0-9')
            dot.edge('S2', 'S2', label='0-9')
            dot.edge('S2', 'S3', label='.')
            dot.edge('S0', 'S3', label='.')
            dot.edge('S3', 'S4', label='0-9')
            dot.edge('S4', 'S4', label='0-9')
            dot.edge('S2', 'S5', label='e, E')
            dot.edge('S4', 'S5', label='e, E')
            dot.edge('S5', 'S6', label='+, -')
            dot.edge('S5', 'S7', label='0-9')
            dot.edge('S6', 'S7', label='0-9')
            dot.edge('S7', 'S7', label='0-9')
            dot.edge('S0', 'S8', label='"')
            dot.edge('S8', 'S8', label='[^"]')
            dot.edge('S8', 'S9', label='"')
            dot.edge('S0', 'S9', label='=, !, <, >, &, |, +, -, *, /, %')
            dot.edge('S0', 'S10', label='espacio, \\t, \\n')
            dot.edge('S10', 'S10', label='espacio, \\t, \\n')

            # Guardar archivo
            output_dir = "exports"
            os.makedirs(output_dir, exist_ok=True)
            file_path = os.path.join(output_dir, "lexer_automata")

            dot.render(file_path, format='png', cleanup=True)
            return file_path + '.png'

        except Exception as e:
            return f"Error generando autómata del lexer: {str(e)}"