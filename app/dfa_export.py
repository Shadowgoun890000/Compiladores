import os
import html
from typing import Tuple
from .regex_nfa_dfa import build_min_dfa


def export_dfa_html(out_path: str = "exports/afd.html") -> Tuple[bool, str]:
    
    try:
        # Asegurar que el directorio de salida existe
        out_dir = os.path.dirname(out_path)
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir, exist_ok=True)

        # Obtener el DFA minimizado
        dfa = build_min_dfa()
        if not dfa or not hasattr(dfa, 'state_list') or not hasattr(dfa, 'trans'):
            return False, "Error: DFA no válido o mal formado"

        # Extraer información del DFA
        n_states = len(dfa.state_list)
        accepting = []
        alphabet = set()

        # Recopilar estados de aceptación y alfabeto de forma segura
        for i, state in enumerate(dfa.state_list):
            if hasattr(state, 'accepts') and state.accepts:
                accepting.append(f"S{i}")
            if i in dfa.trans:
                alphabet.update(dfa.trans[i].keys())

        alphabet = sorted(alphabet)

        # Generar HTML con estilos mejorados
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>AFD Exportado</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: #1e1e1e;
                    color: #eee;
                    margin: 20px;
                    line-height: 1.6;
                }}
                h1 {{ 
                    color: #4fc3f7;
                    border-bottom: 2px solid #4fc3f7;
                    padding-bottom: 10px;
                }}
                table {{ 
                    border-collapse: collapse;
                    margin: 20px 0;
                    width: 100%;
                    box-shadow: 0 0 20px rgba(0,0,0,0.15);
                }}
                th, td {{ 
                    border: 1px solid #555;
                    padding: 12px;
                    text-align: center;
                }}
                th {{ 
                    background: #007acc;
                    color: white;
                    font-weight: bold;
                }}
                tr:nth-child(even) {{ background: #2a2a2a; }}
                tr:hover {{ background: #333; }}
                .accept {{ 
                    color: #81c784;
                    font-weight: bold;
                }}
                .info {{
                    background: #2a2a2a;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            <h1>Autómata Finito Determinista (AFD)</h1>
            <div class="info">
                <p><b>Estados totales:</b> {n_states}<br>
                <b>Estado inicial:</b> S{dfa.start}<br>
                <b>Estados de aceptación:</b> {' , '.join(accepting) if accepting else '—'}<br>
                <b>Alfabeto:</b> {', '.join(map(html.escape, alphabet)) if alphabet else '—'}</p>
            </div>
        """

        # Generar tabla de transiciones de forma segura
        html_content += "<table><tr><th>Estado</th>"
        html_content += "".join(f"<th>{html.escape(a)}</th>" for a in alphabet)
        html_content += "</tr>"

        for s in range(n_states):
            cls = "accept" if dfa.state_list[s].accepts else ""
            row = f"<tr><td class='{cls}'>S{s}</td>"
            
            for a in alphabet:
                # Manejar transiciones de forma segura
                dest = dfa.trans.get(s, {}).get(a, None)
                cell_content = f"S{dest}" if dest is not None else "—"
                row += f"<td>{cell_content}</td>"
            
            row += "</tr>"
            html_content += row
        
        html_content += "</table>"
        html_content += "<p style='margin-top:20px; color: #81c784;'>Archivo generado correctamente.</p></body></html>"

        # Escribir el archivo
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        return True, f"Archivo HTML generado exitosamente en: {out_path}"

    except Exception as e:
        return False, f"Error al exportar el AFD: {type(e).__name__}: {e}"
