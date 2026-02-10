# 📊 Flowchart Generator 3000
> Modern desktop application to automatically generate flowcharts from Python source code
![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)
## ✨ Features
- 🎨 **Modern graphical interface** using CustomTkinter
- 📁 **Recursive processing** of folders and subfolders
- 🔍 **Smart filtering** by name and numeric range
- 🎯 **Multiple rendering engines**:
  - **Graphviz** - Detailed diagrams with full AST analysis
  - **Mermaid** - Simplified diagrams
- 🌐 **Cloud generation** using Kroki.io (no local installations required)
- 📦 **Auto-detection of dependencies** between Python files
- 🎨 **Colored diagrams** with different shapes depending on block type
- 🔄 **Simulation mode** to preview without generating files
- 📂 **Automatic folder opening** when finished
## 🖼️ Screenshot
The application features an intuitive interface divided into two tabs:
- **Home**: Diagram configuration and generation
- **Terminal**: Real-time process visualization
## 📋 Requirements
### Python Dependencies
requests
Pillow
pyflowchart
customtkinter
### Operating System
- **Windows** (tested and optimized)
- Linux/Mac (compatible but not fully tested)
## 🚀 Installation
### Option 1: Use the executable (Windows)
1. Download `generador_diagramas3000.exe`
2. Make sure the file `imagen.ico` is in the same folder (optional, for the icon)
3. Run the .exe
### Option 2: Run from source code
1. Clone this repository:
git clone https://github.com/tu-usuario/generador-diagrama.git
cd generador-diagrama
2. Install dependencies:
pip install -r requirements.txt
3. Run the application:
python generador_diagramas3000.py
## 📖 Usage
### Step by Step
1. **Select folder**: Click on "Browse" and select the folder with your Python files
2. **Configure filters** (optional):
   - **Name filter**: e.g. "exercise" to process only files containing that word
   - **Range filter**: Enable to process only files numbered within a specific range
3. **Configure options**:
   - **Rendering engine**: Graphviz (more detailed) or Mermaid (simpler)
   - **Extensions**: Default is "py", you can add more separated by commas
   - **Search subfolders**: Recursively process the entire structure
4. **Generate**: Click on "GENERATE DIAGRAMS"
5. **Check the terminal**: Monitor progress in the "Terminal" tab
### Usage Examples
#### Generate diagrams for all Python files in a folder
Folder: C:\MyProject
Name Filter: (empty)
Engine: Graphviz (More detail)
## 🔧 Technical Features
### Code Analysis
- **Modular Architecture**: Code organized into modules (`core`, `gui`) to ease maintenance and extension.
- **AST Parsing**: Analyzes Python code structure using the `ast` module
- **Function detection**: Automatically identifies functions, methods, and classes
- **Flow analysis**: Detects conditions, loops, I/O operations, etc.
- **Dependency auto-discovery**: Finds local imports and includes them in the diagram
### Detected Block Types
| Type | Shape | Color |
| Start/End | Oval | Light blue / Soft red |
| Operation | Rectangle | Yellow |
| Input/Output | Parallelogram | Light green |
| Condition | Diamond | Light orange |
| Subroutine | Component | Light purple |
### Current Limitations
⚠️ **IMPORTANT**: This program is optimized for **Python (.py)**. Although it allows configuring other extensions, the advanced analysis engine (pyflowchart + AST) only understands Python syntax. For other languages, it uses a generic structured parser.
**Support:**
- **Python**: Full analysis (AST + pyflowchart).
- **Java, C++, JS, PHP**: Basic flow analysis based on control structures.
## 🛠️ Project Structure
Genarador Diagrama/
│
├── generador_diagramas3000.py
├── core/
│   ├── analyzer.py
│   ├── renderer.py
│   └── utils.py
├── gui/
│   └── app.py
├── Otros/
│   ├── imagen.ico
│   ├── imagen.png
│   └── generador_diagramas3000.spec
├── requirements.txt
└── README.md
## 🤝 Contributions
Contributions are welcome. If you want to add support for other programming languages, consider:
1. Implementing language-specific parsers
2. Adapting the AST analysis logic
3. Maintaining compatibility with the current interface
## 📝 License
This project is licensed under the MIT License. See the `LICENSE` file for more details.
## 🐛 Known Issues
- The current .exe is outdated (compiled on 02/06, code updated on 02/08)
- The global function linker between files is disabled to avoid overly complex diagrams
- Very large files may cause timeouts with Kroki.io (120-second limit)
## 📧 Contact
To report bugs or suggest improvements, open an issue on GitHub.
---
**Made with ❤️ using Python and a strong desire to save time**
