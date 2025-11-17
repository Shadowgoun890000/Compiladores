# Analizador Léxico, Sintáctico y Semántico LL(1)

## Descripción
Compilador completo con análisis léxico, sintáctico y semántico con interfaz gráfica que permite:
- **Análisis Léxico**: Tokenización de código fuente
- **Análisis Sintáctico**: Parsing LL(1) descendente recursivo
- **Análisis Semántico**: Verificación de tipos y tabla de símbolos
- Visualización de tokens en tabla
- Visualización del árbol de sintaxis abstracta (AST)
- Visualización del análisis semántico completo
- Exportación de tokens a PDF
- Soporte para múltiples tipos de archivo (.txt, .src, .js, .ts)

## Características

### Análisis Léxico
- Reconocimiento de palabras clave: `let`, `const`, `function`, `if`, `else`, `while`, `for`, `return`, `true`, `false`
- Operadores aritméticos: `+`, `-`, `*`, `/`, `%`
- Operadores lógicos: `&&`, `||`, `!`
- Operadores de comparación: `==`, `!=`, `<`, `<=`, `>`, `>=`
- Identificadores, números, cadenas de texto
- Comentarios de una línea (`//`)

### Análisis Sintáctico
- Parser LL(1) descendente recursivo
- Generación de árbol de sintaxis abstracta (AST)
- Soporte para:
  - Declaraciones de variables (`let`, `const`)
  - Declaraciones de funciones con parámetros
  - Estructuras de control (`if-else`, `while`, `for`)
  - Expresiones con precedencia de operadores
  - Llamadas a funciones
  - Acceso a índices y miembros
- Manejo de errores sintácticos con ubicación precisa
- Recuperación de errores

### Análisis Semántico
- **Tabla de Símbolos**:
  - Gestión de ámbitos anidados (scopes)
  - Seguimiento de variables, constantes, funciones y parámetros
  - Detección de variables no utilizadas
  - Funciones built-in: `print()`, `input()`, `parseInt()`

- **Sistema de Tipos**:
  - Tipos soportados: NUMBER, STRING, BOOLEAN, FUNCTION, VOID
  - Inferencia automática de tipos
  - Verificación de compatibilidad en operaciones
  - Propagación de tipos en expresiones

- **Verificaciones Semánticas**:
  - ❌ **Errores**: Variables no declaradas, redeclaraciones, incompatibilidad de tipos, asignación a constantes, número incorrecto de argumentos, return fuera de función
  - ⚠️ **Advertencias**: Variables no usadas, funciones no llamadas, shadowing de variables

- **Visualización**:
  - Árbol de ámbitos con todos los símbolos
  - Lista detallada de errores con ubicación
  - Lista de advertencias para mejorar el código

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

### Inicio Rápido
1. Ejecutar la interfaz gráfica:
```bash
python main.py
```

2. Cargar o escribir código:
   - Usar el botón **📂 Abrir** para cargar un archivo
   - O escribir/pegar código directamente en el editor

3. Análisis del código:
   - **🔍 Tokenizar**: Realiza análisis léxico
     - Muestra todos los tokens en la pestaña "Tokens"
     - Detecta errores léxicos (caracteres inválidos, etc.)
   
   - **🌳 Sintaxis**: Realiza análisis sintáctico
     - Primero tokeniza si no se ha hecho
     - Construye el árbol de sintaxis abstracta (AST)
     - Muestra el AST en la pestaña "AST"
     - Detecta errores sintácticos con ubicación precisa
   
   - **🔬 Semántico**: Realiza análisis semántico
     - Primero realiza análisis sintáctico si no se ha hecho
     - Construye tabla de símbolos con ámbitos anidados
     - Verifica tipos, declaraciones y uso de variables
     - Detecta errores semánticos (variables no declaradas, incompatibilidad de tipos, etc.)
     - Genera advertencias (variables no usadas, funciones no llamadas)
     - Muestra resultados en la pestaña "Semántico"

4. Exportar resultados:
   - Seleccionar tipo de exportación en el ComboBox:
     - **Tokens a PDF**: Solo la tabla de tokens
     - **AST a PDF**: Solo el árbol de sintaxis abstracta
     - **Semántico a PDF**: Solo el análisis semántico
     - **Todo a PDF**: Análisis completo (tokens + AST + semántico)
   - Hacer clic en **📄 Exportar**
   - Elegir ubicación y nombre del archivo

5. Limpieza:
   - **🧹 Limpiar**: Borra editor, tokens, AST y análisis semántico

### Flujo de Trabajo Recomendado
1. Abrir o escribir código fuente
2. Hacer clic en "Semántico" (esto ejecutará automáticamente el análisis léxico y sintáctico)
3. Revisar resultados en las tres pestañas:
   - **Tokens**: Lista de todos los tokens identificados
   - **AST**: Árbol de sintaxis abstracta generado
   - **Semántico**: Tabla de símbolos, errores y advertencias
4. Si hay errores, revisar la ubicación indicada en cada pestaña
5. Corregir errores y volver a analizar
6. Seleccionar tipo de exportación en el ComboBox (Tokens/AST/Semántico/Todo)
7. Exportar a PDF si es necesario

### Ejemplos de Archivos
El proyecto incluye varios archivos de ejemplo en la carpeta `sample/`:

- `simple.src`: Declaraciones básicas y expresiones
- `functions.src`: Declaración y uso de funciones
- `control_flow.src`: Estructuras de control (if, while, for)
- `test_completo.src`: Programa completo con múltiples características
- `errores_semanticos.src`: Ejemplos de errores semánticos comunes
- `semantica_correcta.src`: Código semánticamente válido para verificación

## Gramática LL(1)

```
Program     -> StmtList
StmtList    -> Stmt StmtList | ε
Stmt        -> VarDecl | FunDecl | IfStmt | WhileStmt | ForStmt 
             | ReturnStmt | Block | ExprStmt

VarDecl     -> (let | const) ID (= Expr)? ;
FunDecl     -> function ID ( ParamList? ) Block
IfStmt      -> if ( Expr ) Stmt (else Stmt)?
WhileStmt   -> while ( Expr ) Stmt
ForStmt     -> for ( ForInit ; ForCond ; ForIter ) Stmt
ReturnStmt  -> return Expr? ;
Block       -> { StmtList }
ExprStmt    -> Expr ;

Expr        -> Assignment
Assignment  -> LogicalOr (= Assignment)?
LogicalOr   -> LogicalAnd (|| LogicalAnd)*
LogicalAnd  -> Equality (&& Equality)*
Equality    -> Relational ((== | !=) Relational)*
Relational  -> Additive ((< | <= | > | >=) Additive)*
Additive    -> Multiplicative ((+ | -) Multiplicative)*
Multiplicative -> Unary ((* | / | %) Unary)*
Unary       -> (! | - | +) Unary | Postfix
Postfix     -> Primary (Call | Index | Member)*
Primary     -> ID | NUM | STRING | true | false | ( Expr )
```

## Estructura de Archivos
```
lexico_ll1/
├── app/                      # Módulos principales
│   ├── gui.py               # Interfaz gráfica con 3 pestañas
│   ├── lexer.py             # Analizador léxico
│   ├── parser.py            # Analizador sintáctico LL(1)
│   ├── semantic_analyzer.py # Analizador semántico
│   ├── symbol_table.py      # Tabla de símbolos con ámbitos
│   ├── tokens.py            # Definición de tokens
│   ├── ast_nodes.py         # Nodos del AST (15 tipos)
│   └── dfa_export.py        # Exportación a PDF
├── exports/                 # Archivos exportados (PDFs)
├── sample/                  # Ejemplos de código
│   ├── simple.src           # Declaraciones básicas
│   ├── functions.src        # Funciones y recursión
│   ├── control_flow.src     # Estructuras de control
│   ├── test_completo.src    # Ejemplo completo
│   ├── errores_semanticos.src   # Errores semánticos para pruebas
│   └── semantica_correcta.src   # Código semánticamente válido
└── main.py                  # Punto de entrada
```

## Ejemplos
La carpeta `sample/` contiene varios ejemplos para probar el analizador:

### simple.src
Declaraciones básicas y expresiones aritméticas
```javascript
let x = 10;
let y = 20;
const z = x + y * 2;
```

### functions.src
Declaraciones de funciones y recursión
```javascript
function factorial(n) {
    if (n == 0) {
        return 1;
    } else {
        return n * factorial(n - 1);
    }
}
```

### control_flow.src
Estructuras de control y expresiones lógicas
```javascript
if (x > y) {
    let mayor = x;
} else {
    let mayor = y;
}

while (contador < 10) {
    contador = contador + 1;
}

for (let i = 0; i < 5; i = i + 1) {
    let cuadrado = i * i;
}
```

### errores_semanticos.src
Ejemplos de errores semánticos comunes para validar el analizador
```javascript
// Variable no declarada
let x = indefinida + 5;

// Redeclaración
let y = 10;
let y = 20;

// Incompatibilidad de tipos
let suma = 10 + "texto";

// Constante reasignada
const pi = 3.14;
pi = 3.1416;
```

### semantica_correcta.src
Código semánticamente válido con funciones, tipos y ámbitos correctos
```javascript
function calcular(a, b) {
    let resultado = a + b;
    return resultado;
}

let valor1 = 10;
let valor2 = 20;
let total = calcular(valor1, valor2);
print(total);
```

## Notas
- El analizador es sensible a mayúsculas/minúsculas
- Soporta comentarios de una línea (`//`)
- Detecta errores léxicos, sintácticos y semánticos con ubicación precisa
- El parser implementa recuperación de errores
- La tabla de símbolos maneja ámbitos anidados correctamente
- El sistema de tipos incluye inferencia automática
- Detecta variables y funciones no utilizadas

## Análisis Implementados
✅ **Análisis Léxico**: Tokenización completa con detección de errores léxicos  
✅ **Análisis Sintáctico**: Parser LL(1) con generación de AST  
✅ **Análisis Semántico**: Tabla de símbolos, verificación de tipos y ámbitos  

## Posibles Mejoras Futuras
El proyecto puede complementarse con:

1. **Generación de Código**
   - Código intermedio de tres direcciones
   - Generación de código máquina o bytecode
   - Máquina virtual para ejecutar el código
   - Optimización de código (eliminación de código muerto, propagación de constantes)

2. **Características Adicionales del Lenguaje**
   - Soporte para arrays y objetos literales
   - Clases y herencia
   - Funciones anónimas y closures
   - Operador ternario (`? :`)
   - Comentarios multilínea (`/* */`)
   - Destructuring de arrays y objetos
   - Operadores de incremento/decremento (`++`, `--`)

3. **Visualización Mejorada**
   - Visualización gráfica interactiva del AST
   - Resaltado de sintaxis en el editor
   - Autocompletado de código inteligente
   - Depuración paso a paso con breakpoints
   - Coloreado de errores y advertencias en el código

4. **Exportación y Reportes**
   - Exportar AST a JSON/XML
   - Exportar tabla de símbolos a Excel
   - Generar reporte completo de análisis en PDF
   - Métricas de código (complejidad ciclomática, líneas de código, etc.)

5. **Optimización y Rendimiento**
   - Análisis de flujo de datos
   - Detección de código inalcanzable
   - Advertencias sobre posibles errores de lógica
   - Sugerencias de optimización
   - Métricas de complejidad del código
   - Análisis de cobertura de pruebas
