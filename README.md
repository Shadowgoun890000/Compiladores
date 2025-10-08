# Analizador Léxico LL(1)

## Descripción
Analizador léxico con interfaz gráfica que permite:
- Tokenización de código fuente
- Visualización de tokens en tabla
- Exportación de tokens a PDF
- Soporte para múltiples tipos de archivo (.txt, .src, .js, .ts)

## Requisitos del Sistema

### Software Base
- Python 3.10 o superior
- pip (gestor de paquetes de Python)
- Git (opcional, para control de versiones)

### Dependencias Principales
- **PyQt6**: Framework para la interfaz gráfica
  - PyQt6-Qt6: Componentes Qt
  - PyQt6-sip: Bindings Python
- **reportlab**: Generación de documentos PDF

### Dependencias de Desarrollo
- **black**: Formateador de código Python
- **pylint**: Análisis estático de código
- **pytest**: Framework de pruebas unitarias

## Extensiones Recomendadas para VS Code
1. **Python** (ms-python.python)
   - Soporte completo para Python
   - IntelliSense y depuración

2. **Pylance** (ms-python.vscode-pylance)
   - Análisis estático mejorado
   - Autocompletado inteligente

3. **Python Test Explorer** (littlefoxteam.vscode-python-test-adapter)
   - Interfaz visual para pruebas
   - Ejecución y depuración de pruebas

4. **Error Lens** (usernamehw.errorlens)
   - Visualización mejorada de errores
   - Diagnósticos en línea

5. **Git Graph** (mhutchie.git-graph)
   - Visualización del historial de Git
   - Gestión de ramas y commits

## Instalación

### 1. Preparación del Entorno
```bash
# Clonar el repositorio (opcional)
git clone <url-del-repositorio>
cd lexico_ll1

# Crear y activar entorno virtual (recomendado)
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate # Linux/Mac
```

### 2. Instalación de Dependencias
```bash
# Actualizar pip
python -m pip install --upgrade pip

# Instalar dependencias
pip install -r requirements.txt

# Instalar dependencias de desarrollo (opcional)
pip install black pylint pytest
```

## Uso
1. Ejecutar la interfaz gráfica:
```bash
python main.py
```

2. Funcionalidades:
   - 📂 **Abrir**: Cargar archivo fuente
   - 🔍 **Tokenizar**: Analizar el código y mostrar tokens
   - 📄 **Exportar a PDF**: Guardar tabla de tokens en PDF
   - 🧹 **Limpiar**: Borrar el editor

## Estructura de Archivos
```
lexico_ll1/
├── app/               # Módulos principales
│   ├── gui.py        # Interfaz gráfica
│   ├── lexer.py      # Analizador léxico
│   └── tokens.py     # Definición de tokens
├── exports/          # Archivos exportados
├── sample/           # Ejemplos de código
└── main.py          # Punto de entrada
```

## Ejemplos
La carpeta `sample/` contiene varios ejemplos de código fuente para probar el analizador:
- JavaScript
- TypeScript
- Código fuente personalizado (.src)

## Notas
- El analizador es sensible a mayúsculas/minúsculas
- Soporta comentarios de una línea y multilínea
- Detecta errores léxicos y muestra su ubicación
