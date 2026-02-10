# 📊 Generador de Diagramas de Flujo 3000

> Aplicación de escritorio moderna para generar automáticamente diagramas de flujo a partir de código fuente Python

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)

## ✨ Características

- 🎨 **Interfaz gráfica moderna** usando CustomTkinter
- 📁 **Procesamiento recursivo** de carpetas y subcarpetas
- 🔍 **Filtrado inteligente** por nombre y rango numérico
- 🎯 **Múltiples motores de renderizado**:
  - **Graphviz** - Diagramas detallados con análisis AST completo
  - **Mermaid** - Diagramas simplificados
- 🌐 **Generación en la nube** usando Kroki.io (no requiere instalaciones locales)
- 📦 **Auto-detección de dependencias** entre archivos Python
- 🎨 **Diagramas coloreados** con distintas formas según el tipo de bloque
- 🔄 **Modo simulación** para previsualizar sin generar archivos
- 📂 **Apertura automática** de carpeta al finalizar

## 🖼️ Captura de Pantalla

La aplicación cuenta con una interfaz intuitiva dividida en dos pestañas:
- **Inicio**: Configuración y generación de diagramas
- **Terminal**: Visualización del proceso en tiempo real

## 📋 Requisitos

### Dependencias Python

```
requests
Pillow
pyflowchart
customtkinter
```

### Sistema Operativo

- **Windows** (probado y optimizado)
- Linux/Mac (compatible pero no completamente probado)

## 🚀 Instalación

### Opción 1: Usar el ejecutable (Windows)

1. Descarga `generador_diagramas3000.exe`
2. Asegúrate de tener el archivo `imagen.ico` en la misma carpeta (opcional, para el icono)
3. Ejecuta el .exe

### Opción 2: Ejecutar desde el código fuente

1. Clona este repositorio:
```bash
git clone https://github.com/tu-usuario/generador-diagrama.git
cd generador-diagrama
```

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

3. Ejecuta la aplicación:
```bash
python generador_diagramas3000.py
```

## 📖 Uso

### Paso a Paso

1. **Selecciona carpeta**: Haz clic en "Examinar" y selecciona la carpeta con tus archivos Python
2. **Configura filtros** (opcional):
   - **Filtro por nombre**: Ej. "ejercicio" para procesar solo archivos que contengan esa palabra
   - **Filtro por rango**: Activar para procesar solo archivos numerados en un rango específico
3. **Configura opciones**:
   - **Motor de renderizado**: Graphviz (más detallado) o Mermaid (más simple)
   - **Extensiones**: Por defecto "py", puedes agregar más separadas por coma
   - **Buscar en subcarpetas**: Procesa recursivamente toda la estructura
4. **Genera**: Haz clic en "GENERAR DIAGRAMAS"
5. **Revisa el terminal**: Observa el progreso en la pestaña "Terminal"

### Ejemplos de Uso

#### Generar diagramas de todos los archivos Python en una carpeta

```
Carpeta: C:\MiProyecto
Filtro por Nombre: (vacío)
Motor: Graphviz (Más detalle)
```

## 🔧 Características Técnicas


### Análisis de Código

- **Arquitectura Modular**: Código organizado en módulos (`core`, `gui`) para facilitar el mantenimiento y la extensión.
- **Parsing AST**: Analiza la estructura del código Python usando el módulo `ast`
- **Detección de funciones**: Identifica funciones, métodos y clases automáticamente
- **Análisis de flujo**: Detecta condiciones, bucles, operaciones I/O, etc.
- **Auto-discovery de dependencias**: Encuentra imports locales y los incluye en el diagrama

### Tipos de Bloques Detectados

| Tipo | Forma | Color |
|------|-------|-------|
| Inicio/Fin | Óvalo | Azul claro / Rojo suave |
| Operación | Rectángulo | Amarillo |
| Entrada/Salida | Paralelogramo | Verde claro |
| Condición | Rombo | Naranja claro |
| Subrutina | Componente | Púrpura claro |

### Limitaciones Actuales

⚠️ **IMPORTANTE**: Este programa está optimizado para **Python (.py)**. Aunque permite configurar otras extensiones, el motor de análisis avanzado (pyflowchart + AST) solo entiende sintaxis Python. Para otros lenguajes, utiliza un parser estructurado genérico.

**Soporte:**
- **Python**: Análisis completo (AST + pyflowchart).
- **Java, C++, JS, PHP**: Análisis de flujo básico basado en estructuras de control.


## 🛠️ Estructura del Proyecto

```
Genarador Diagrama/
│
├── generador_diagramas3000.py      # Punto de entrada principal
│
├── core/                           # Motor lógico del programa
│   ├── analyzer.py                 # Análisis de código y detección de lógica
│   ├── renderer.py                 # Conversión a DOT/Mermaid y renderizado PDF
│   └── utils.py                    # Utilidades de sistema y procesamiento de texto
│
├── gui/                            # Interfaz Gráfica
│   └── app.py                      # Definición de la ventana y lógica de la UI
│
├── Otros/
│   ├── imagen.ico                  # Icono de la aplicación
│   ├── imagen.png                  # Logo para documentación
│   └── generador_diagramas3000.spec # Configuración PyInstaller
│
├── requirements.txt                # Dependencias Python
└── README.md                       # Documentación
```

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Si deseas agregar soporte para otros lenguajes de programación, considera:

1. Implementar parsers específicos para cada lenguaje
2. Adaptar la lógica de análisis AST
3. Mantener la compatibilidad con la interfaz actual

## 📝 Licencia

Este proyecto está bajo licencia MIT. Consulta el archivo `LICENSE` para más detalles.

## 🐛 Problemas Conocidos

- El .exe actual está desactualizado (compilado el 06/02, código actualizado el 08/02)
- El enlazador global de funciones entre archivos está desactivado para evitar diagramas muy complejos
- Archivos muy grandes pueden causar timeouts con Kroki.io (límite de 120 segundos)

## 📧 Contacto

Para reportar bugs o sugerir mejoras, abre un issue en GitHub.

---

**Hecho con ❤️ usando Python y muchas ganas de ahorrar tiempo**
