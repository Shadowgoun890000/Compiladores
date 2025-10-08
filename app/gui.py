import os
from PyQt6 import QtWidgets, QtGui, QtCore
from .lexer import Lexer, LexError
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.units import inch


class TokenTableModel(QtCore.QAbstractTableModel):
    HEADERS = ["LINE", "COL", "TOKEN", "LEXEME"]

    def __init__(self, tokens):
        super().__init__()
        self.tokens = tokens

    def rowCount(self, parent=None):
        return len(self.tokens)

    def columnCount(self, parent=None):
        return 4

    def data(self, index, role):
        if not index.isValid():
            return None
        t = self.tokens[index.row()]
        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            return [t.line, t.col, t.type, t.lexeme][index.column()]
        if role == QtCore.Qt.ItemDataRole.FontRole and index.column() == 3:
            return QtGui.QFont("Consolas")
        return None

    def headerData(self, section, orientation, role):
        if role != QtCore.Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == QtCore.Qt.Orientation.Horizontal:
            return self.HEADERS[section]
        return section + 1


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Analizador Léxico LL(1)")
        self.resize(1000, 700)
        self.setStyleSheet("""
            QMainWindow { background-color: #1e1e1e; color: #e0e0e0; }
            QPlainTextEdit {
                background-color: #252526; color: #ffffff;
                border: 1px solid #3c3c3c; border-radius: 6px;
                font-family: 'Consolas'; font-size: 11pt;
            }
            QPushButton {
                background-color: #007acc; color: white;
                border-radius: 6px; padding: 6px 12px;
            }
            QPushButton:hover { background-color: #0095ff; }
            QTableView {
                background-color: #1e1e1e; color: white;
                selection-background-color: #007acc;
                border-radius: 6px;
            }
            QMessageBox { background-color: #1e1e1e; color: white; }
        """)

        # --- Layout principal ---
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        layout = QtWidgets.QVBoxLayout(central)

        # --- Editor ---
        self.editor = QtWidgets.QPlainTextEdit()
        self.editor.setPlaceholderText("Pega o escribe código fuente aquí…")
        layout.addWidget(self.editor, 2)

        # --- Botones ---
        buttons = QtWidgets.QHBoxLayout()
        self.btn_open = QtWidgets.QPushButton("📂 Abrir")
        self.btn_token = QtWidgets.QPushButton("🔍 Tokenizar")
        self.btn_export = QtWidgets.QPushButton("� Exportar a PDF")
        self.btn_clear = QtWidgets.QPushButton("🧹 Limpiar")
        for b in [self.btn_open, self.btn_token, self.btn_export, self.btn_clear]:
            buttons.addWidget(b)
        layout.addLayout(buttons)

        # --- Tabla ---
        self.table = QtWidgets.QTableView()
        layout.addWidget(self.table, 3)

        # --- Barra de estado ---
        self.status = QtWidgets.QStatusBar()
        self.setStatusBar(self.status)

        # --- Conexiones ---
        self.btn_open.clicked.connect(self.on_open)
        self.btn_token.clicked.connect(self.on_tokenize)
        self.btn_export.clicked.connect(self.export_to_pdf)
        self.btn_clear.clicked.connect(lambda: self.editor.clear())

    # ------------------------------------------------------------------
    # Abrir archivo fuente
    # ------------------------------------------------------------------
    def on_open(self):
        try:
            path, _ = QtWidgets.QFileDialog.getOpenFileName(
                self, "Abrir fuente", "", "Archivos de texto (*.txt *.src *.js *.ts);;Todos (*)"
            )
            if not path:
                return
            with open(path, "r", encoding="utf-8") as f:
                self.editor.setPlainText(f.read())
            self.status.showMessage(f"Archivo cargado: {os.path.basename(path)}", 4000)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"No se pudo abrir el archivo:\n{e}")

    # ------------------------------------------------------------------
    # Tokenizar texto
    # ------------------------------------------------------------------
    def on_tokenize(self):
        src = self.editor.toPlainText()
        lex = Lexer(src)
        try:
            tokens = lex.tokenize()
        except LexError as e:
            QtWidgets.QMessageBox.critical(
                self, "Error léxico",
                f"Línea {e.line}, Columna {e.col}\nLexema: {e.lexeme}"
            )
            return
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error inesperado", str(e))
            return

        model = TokenTableModel(tokens)
        self.table.setModel(model)
        self.table.resizeColumnsToContents()
        self.status.showMessage(f"{len(tokens)} tokens generados", 4000)

    # ------------------------------------------------------------------
    # Exportar a PDF
    # ------------------------------------------------------------------
    def export_to_pdf(self):
        if not hasattr(self.table, 'model') or not self.table.model():
            QtWidgets.QMessageBox.warning(
                self, 
                "Advertencia",
                "No hay tokens para exportar. Primero tokeniza el código fuente."
            )
            return

        try:
            # Pedir al usuario dónde guardar el archivo
            file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
                self,
                "Guardar PDF",
                os.path.join(os.getcwd(), "tokens.pdf"),
                "Archivos PDF (*.pdf)"
            )
            
            if not file_path:
                return

            # Asegurarse de que el archivo termine en .pdf
            if not file_path.lower().endswith('.pdf'):
                file_path += '.pdf'

            # Crear el documento PDF con márgenes personalizados
            doc = SimpleDocTemplate(
                file_path,
                pagesize=letter,
                rightMargin=inch/2,
                leftMargin=inch/2,
                topMargin=inch,
                bottomMargin=inch/2
            )

            # Preparar los elementos del documento
            elements = []

            # Agregar título
            from reportlab.platypus import Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#007acc'),
                spaceAfter=30,
                alignment=1  # Centrado
            )
            elements.append(Paragraph("Análisis de Tokens", title_style))
            elements.append(Spacer(1, 20))

            # Preparar los datos de la tabla
            data = [TokenTableModel.HEADERS]  # Encabezados
            model = self.table.model()
            for row in range(model.rowCount()):
                row_data = []
                for col in range(model.columnCount()):
                    value = model.data(model.index(row, col), QtCore.Qt.ItemDataRole.DisplayRole)
                    row_data.append(str(value))
                data.append(row_data)

            # Calcular anchos de columna
            col_widths = [0.7*inch, 0.7*inch, 1.5*inch, 3*inch]  # Personalizado para cada columna

            # Crear la tabla con anchos personalizados
            table = Table(data, colWidths=col_widths, repeatRows=1)

            # Estilo elaborado para la tabla
            table.setStyle(TableStyle([
                # Encabezados
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#007acc')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                
                # Contenido
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('ALIGN', (0, 1), (1, -1), 'CENTER'),  # Centrar LINE y COL
                ('ALIGN', (2, 1), (2, -1), 'CENTER'),  # Centrar TOKEN
                ('ALIGN', (3, 1), (3, -1), 'LEFT'),    # Alinear LEXEME a la izquierda
                
                # Bordes y espaciado
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#007acc')),
                ('LINEABOVE', (0, 1), (-1, 1), 2, colors.HexColor('#007acc')),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 12),
                ('RIGHTPADDING', (0, 0), (-1, -1), 12),
                
                # Filas alternadas
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
                
                # Estilo condicional para tokens especiales
                ('TEXTCOLOR', (2, 1), (2, -1), colors.HexColor('#007acc')),  # Color especial para tokens
            ]))

            elements.append(table)

            # Agregar pie de página
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=8,
                textColor=colors.grey,
                alignment=1,
                spaceBefore=30
            )
            elements.append(Spacer(1, 20))
            elements.append(Paragraph(f"Generado el {QtCore.QDateTime.currentDateTime().toString('dd/MM/yyyy HH:mm:ss')}", footer_style))

            # Construir el documento
            doc.build(elements)

            self.status.showMessage(f"Tokens exportados a: {file_path}", 4000)
            QtWidgets.QMessageBox.information(
                self,
                "Exportación completada",
                f"Los tokens han sido exportados exitosamente a:\n{file_path}"
            )

        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self,
                "Error de exportación",
                f"No se pudo exportar los tokens:\n{str(e)}"
            )
