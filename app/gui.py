import os
from PyQt6 import QtWidgets, QtGui, QtCore
from .lexer import Lexer, LexError
from .parser import Parser, ParseError
from .semantic_analyzer import SemanticAnalyzer
from .ast_nodes import ast_to_string
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


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
        
        # Botones de archivo
        self.btn_open = QtWidgets.QPushButton("📂 Abrir")
        buttons.addWidget(self.btn_open)
        
        # Separador
        buttons.addSpacing(10)
        
        # Botones de análisis
        self.btn_token = QtWidgets.QPushButton("🔍 Tokenizar")
        self.btn_parse = QtWidgets.QPushButton("🌳 Sintaxis")
        self.btn_semantic = QtWidgets.QPushButton("🔬 Semántico")
        buttons.addWidget(self.btn_token)
        buttons.addWidget(self.btn_parse)
        buttons.addWidget(self.btn_semantic)
        
        # Separador
        buttons.addSpacing(10)
        
        # ComboBox para tipo de exportación
        export_label = QtWidgets.QLabel("Exportar:")
        export_label.setStyleSheet("color: #e0e0e0; padding: 0 5px;")
        buttons.addWidget(export_label)
        
        self.export_combo = QtWidgets.QComboBox()
        self.export_combo.addItems(["Tokens a PDF", "AST a PDF", "Semántico a PDF", "Todo a PDF"])
        self.export_combo.setStyleSheet("""
            QComboBox {
                background-color: #2d2d2d;
                color: white;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
                padding: 5px 10px;
                min-width: 150px;
            }
            QComboBox:hover {
                background-color: #3c3c3c;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: url(down_arrow.png);
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                background-color: #2d2d2d;
                color: white;
                selection-background-color: #007acc;
            }
        """)
        buttons.addWidget(self.export_combo)
        
        self.btn_export = QtWidgets.QPushButton("📄 Exportar")
        buttons.addWidget(self.btn_export)
        
        # Espaciador para empujar el botón limpiar a la derecha
        buttons.addStretch()
        
        self.btn_clear = QtWidgets.QPushButton("🧹 Limpiar")
        buttons.addWidget(self.btn_clear)
        
        layout.addLayout(buttons)

        # --- Área de salida con tabs ---
        self.tabs = QtWidgets.QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #3c3c3c;
                background-color: #1e1e1e;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #ffffff;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #007acc;
            }
            QTabBar::tab:hover {
                background-color: #3c3c3c;
            }
        """)
        
        # --- Tabla de tokens ---
        self.table = QtWidgets.QTableView()
        self.tabs.addTab(self.table, "Tokens")
        
        # --- Visualización del AST ---
        self.ast_view = QtWidgets.QPlainTextEdit()
        self.ast_view.setReadOnly(True)
        self.ast_view.setStyleSheet("""
            QPlainTextEdit {
                background-color: #252526;
                color: #ffffff;
                border: 1px solid #3c3c3c;
                font-family: 'Consolas';
                font-size: 10pt;
            }
        """)
        self.tabs.addTab(self.ast_view, "AST")
        
        # --- Visualización del análisis semántico ---
        self.semantic_view = QtWidgets.QPlainTextEdit()
        self.semantic_view.setReadOnly(True)
        self.semantic_view.setStyleSheet("""
            QPlainTextEdit {
                background-color: #252526;
                color: #ffffff;
                border: 1px solid #3c3c3c;
                font-family: 'Consolas';
                font-size: 10pt;
            }
        """)
        self.tabs.addTab(self.semantic_view, "Análisis Semántico")
        
        layout.addWidget(self.tabs, 3)

        # --- Barra de estado ---
        self.status = QtWidgets.QStatusBar()
        self.setStatusBar(self.status)

        # --- Conexiones ---
        self.btn_open.clicked.connect(self.on_open)
        self.btn_token.clicked.connect(self.on_tokenize)
        self.btn_parse.clicked.connect(self.on_parse)
        self.btn_semantic.clicked.connect(self.on_semantic)
        self.btn_export.clicked.connect(self.export_to_pdf)
        self.btn_clear.clicked.connect(self.clear_all)
        
        # Variables para almacenar resultados
        self.current_tokens = None
        self.current_ast = None

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
            self.current_tokens = tokens  # Guardar para el parser
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
        self.tabs.setCurrentIndex(0)  # Mostrar tab de tokens
        self.status.showMessage(f"{len(tokens)} tokens generados", 4000)

    # ------------------------------------------------------------------
    # Analizar sintácticamente
    # ------------------------------------------------------------------
    def on_parse(self):
        # Primero tokenizar si no hay tokens
        if not self.current_tokens:
            self.on_tokenize()
            if not self.current_tokens:
                return
        
        try:
            parser = Parser(self.current_tokens)
            ast = parser.parse()
            self.current_ast = ast  # Guardar para el análisis semántico
            
            # Convertir AST a string para visualización
            ast_str = ast_to_string(ast)
            self.ast_view.setPlainText(ast_str)
            self.tabs.setCurrentIndex(1)  # Mostrar tab de AST
            
            self.status.showMessage("Análisis sintáctico completado exitosamente", 4000)
            QtWidgets.QMessageBox.information(
                self,
                "Análisis Sintáctico",
                "El código fuente es sintácticamente correcto.\n"
                "El árbol de sintaxis abstracta (AST) se muestra en la pestaña AST."
            )
            
        except ParseError as e:
            self.current_ast = None
            self.ast_view.setPlainText(f"ERROR DE SINTAXIS:\n\n{str(e)}")
            self.tabs.setCurrentIndex(1)
            QtWidgets.QMessageBox.critical(
                self, "Error Sintáctico",
                str(e)
            )
        except Exception as e:
            self.current_ast = None
            self.ast_view.setPlainText(f"ERROR INESPERADO:\n\n{str(e)}")
            self.tabs.setCurrentIndex(1)
            QtWidgets.QMessageBox.critical(self, "Error inesperado", str(e))
    
    # ------------------------------------------------------------------
    # Análisis semántico
    # ------------------------------------------------------------------
    def on_semantic(self):
        # Primero hacer parsing si no hay AST
        if not self.current_ast:
            self.on_parse()
            if not self.current_ast:
                return
        
        try:
            analyzer = SemanticAnalyzer()
            success = analyzer.analyze(self.current_ast)
            
            # Mostrar reporte
            report = analyzer.get_report()
            self.semantic_view.setPlainText(report)
            self.tabs.setCurrentIndex(2)  # Mostrar tab de análisis semántico
            
            if success and not analyzer.warnings:
                self.status.showMessage("Análisis semántico completado sin errores ni warnings", 4000)
                QtWidgets.QMessageBox.information(
                    self,
                    "Análisis Semántico",
                    "✅ El código es semánticamente correcto.\n"
                    "No se encontraron errores ni advertencias."
                )
            elif success:
                self.status.showMessage(f"Análisis semántico completado con {len(analyzer.warnings)} advertencias", 4000)
                QtWidgets.QMessageBox.warning(
                    self,
                    "Análisis Semántico",
                    f"⚠️  El código es válido pero tiene {len(analyzer.warnings)} advertencias.\n"
                    "Revisa la pestaña 'Análisis Semántico' para más detalles."
                )
            else:
                self.status.showMessage(f"Análisis semántico completado con {len(analyzer.errors)} errores", 4000)
                QtWidgets.QMessageBox.critical(
                    self,
                    "Errores Semánticos",
                    f"❌ Se encontraron {len(analyzer.errors)} errores semánticos.\n"
                    "Revisa la pestaña 'Análisis Semántico' para más detalles."
                )
            
        except Exception as e:
            error_msg = f"ERROR EN ANÁLISIS SEMÁNTICO:\n\n{str(e)}"
            self.semantic_view.setPlainText(error_msg)
            self.tabs.setCurrentIndex(2)
            QtWidgets.QMessageBox.critical(self, "Error", str(e))
    
    # ------------------------------------------------------------------
    # Limpiar todo
    # ------------------------------------------------------------------
    def clear_all(self):
        self.editor.clear()
        self.ast_view.clear()
        self.semantic_view.clear()
        self.current_tokens = None
        self.current_ast = None
        if self.table.model():
            self.table.setModel(None)
        self.status.showMessage("Todo limpiado", 2000)

    # ------------------------------------------------------------------
    # Exportar a PDF
    # ------------------------------------------------------------------
    def export_to_pdf(self):
        export_type = self.export_combo.currentText()
        
        # Verificar qué datos están disponibles
        if "Tokens" in export_type and not self.current_tokens:
            QtWidgets.QMessageBox.warning(
                self, "Advertencia",
                "No hay tokens para exportar. Primero tokeniza el código."
            )
            return
        
        if "AST" in export_type and not self.current_ast:
            QtWidgets.QMessageBox.warning(
                self, "Advertencia",
                "No hay AST para exportar. Primero analiza la sintaxis."
            )
            return
        
        if "Semántico" in export_type and self.semantic_view.toPlainText().strip() == "":
            QtWidgets.QMessageBox.warning(
                self, "Advertencia",
                "No hay análisis semántico para exportar. Primero ejecuta el análisis semántico."
            )
            return
        
        # Determinar nombre de archivo por defecto
        default_names = {
            "Tokens a PDF": "tokens.pdf",
            "AST a PDF": "ast.pdf",
            "Semántico a PDF": "analisis_semantico.pdf",
            "Todo a PDF": "analisis_completo.pdf"
        }
        
        try:
            file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
                self,
                "Guardar PDF",
                os.path.join(os.getcwd(), "exports", default_names.get(export_type, "export.pdf")),
                "Archivos PDF (*.pdf)"
            )
            
            if not file_path:
                return

            if not file_path.lower().endswith('.pdf'):
                file_path += '.pdf'
            
            # Asegurar que existe el directorio
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # Crear el documento PDF
            doc = SimpleDocTemplate(
                file_path,
                pagesize=letter,
                rightMargin=inch/2,
                leftMargin=inch/2,
                topMargin=inch,
                bottomMargin=inch/2
            )

            elements = []
            styles = getSampleStyleSheet()
            
            # Estilo para títulos
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#007acc'),
                spaceAfter=30,
                alignment=1
            )
            
            subtitle_style = ParagraphStyle(
                'CustomSubtitle',
                parent=styles['Heading2'],
                fontSize=16,
                textColor=colors.HexColor('#007acc'),
                spaceAfter=20,
                spaceBefore=20
            )

            # Exportar según el tipo seleccionado
            if export_type == "Tokens a PDF":
                elements.extend(self._export_tokens(title_style, subtitle_style))
            elif export_type == "AST a PDF":
                elements.extend(self._export_ast(title_style, subtitle_style))
            elif export_type == "Semántico a PDF":
                elements.extend(self._export_semantic(title_style, subtitle_style))
            elif export_type == "Todo a PDF":
                elements.extend(self._export_all(title_style, subtitle_style))

            # Construir el PDF
            doc.build(elements)
            
            self.status.showMessage(f"PDF exportado: {os.path.basename(file_path)}", 4000)
            QtWidgets.QMessageBox.information(
                self, "Éxito",
                f"Archivo exportado exitosamente:\n{file_path}"
            )

        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Error",
                f"No se pudo exportar el PDF:\n{str(e)}"
            )
    
    # ------------------------------------------------------------------
    # Funciones auxiliares para exportación
    # ------------------------------------------------------------------
    def _export_tokens(self, title_style, subtitle_style):
        """Exporta la tabla de tokens"""
        elements = []
        elements.append(Paragraph("Análisis Léxico - Tokens", title_style))
        elements.append(Spacer(1, 20))
        
        # Preparar datos de la tabla
        data = [TokenTableModel.HEADERS]
        model = self.table.model()
        for row in range(model.rowCount()):
            row_data = []
            for col in range(model.columnCount()):
                value = model.data(model.index(row, col), QtCore.Qt.ItemDataRole.DisplayRole)
                row_data.append(str(value))
            data.append(row_data)

        col_widths = [0.7*inch, 0.7*inch, 1.5*inch, 3*inch]
        table = Table(data, colWidths=col_widths, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#007acc')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (0, 1), (1, -1), 'CENTER'),
            ('ALIGN', (2, 1), (2, -1), 'CENTER'),
            ('ALIGN', (3, 1), (3, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#007acc')),
            ('LINEABOVE', (0, 1), (-1, 1), 2, colors.HexColor('#007acc')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(table)
        
        # Agregar resumen
        elements.append(Spacer(1, 20))
        summary_style = ParagraphStyle('Summary', parent=getSampleStyleSheet()['Normal'], fontSize=10)
        elements.append(Paragraph(f"Total de tokens: {model.rowCount()}", summary_style))
        
        return elements
    
    def _export_ast(self, title_style, subtitle_style):
        """Exporta el AST"""
        elements = []
        elements.append(Paragraph("Análisis Sintáctico - AST", title_style))
        elements.append(Spacer(1, 20))
        
        ast_text = self.ast_view.toPlainText()
        
        # Dividir en líneas y crear párrafos
        code_style = ParagraphStyle(
            'Code',
            parent=getSampleStyleSheet()['Code'],
            fontSize=9,
            fontName='Courier',
            leftIndent=0,
            spaceBefore=0,
            spaceAfter=0
        )
        
        for line in ast_text.split('\n'):
            elements.append(Paragraph(line.replace('<', '&lt;').replace('>', '&gt;'), code_style))
        
        return elements
    
    def _export_semantic(self, title_style, subtitle_style):
        """Exporta el análisis semántico"""
        elements = []
        elements.append(Paragraph("Análisis Semántico", title_style))
        elements.append(Spacer(1, 20))
        
        semantic_text = self.semantic_view.toPlainText()
        
        code_style = ParagraphStyle(
            'Code',
            parent=getSampleStyleSheet()['Code'],
            fontSize=9,
            fontName='Courier',
            leftIndent=0,
            spaceBefore=0,
            spaceAfter=0
        )
        
        for line in semantic_text.split('\n'):
            elements.append(Paragraph(line.replace('<', '&lt;').replace('>', '&gt;'), code_style))
        
        return elements
    
    def _export_all(self, title_style, subtitle_style):
        """Exporta todo el análisis completo"""
        elements = []
        elements.append(Paragraph("Análisis Completo del Compilador", title_style))
        elements.append(Spacer(1, 30))
        
        # Tokens
        if self.current_tokens:
            elements.append(Paragraph("1. Análisis Léxico", subtitle_style))
            elements.extend(self._export_tokens(None, None)[2:])  # Omitir título duplicado
            elements.append(Spacer(1, 30))
        
        # AST
        if self.current_ast:
            elements.append(Paragraph("2. Análisis Sintáctico", subtitle_style))
            elements.extend(self._export_ast(None, None)[2:])  # Omitir título duplicado
            elements.append(Spacer(1, 30))
        
        # Semántico
        if self.semantic_view.toPlainText().strip():
            elements.append(Paragraph("3. Análisis Semántico", subtitle_style))
            elements.extend(self._export_semantic(None, None)[2:])  # Omitir título duplicado
        
        return elements
