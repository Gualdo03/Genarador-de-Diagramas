import os
import sys
import re

def resource_path(relative_path):
    """ Obtiene la ruta absoluta del recurso, compatible con desarrollo y PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def escape_dot_label(text, limit=120):
    """Escapa caracteres para DOT y simplifica contenido pesado (ASCII Art, etc)"""
    if not text: return ""
    
    # 1. Detectar si es ASCII Art pesado (muchos espacios o caracteres repetidos)
    if "░" in text or "█" in text or "    " * 4 in text:
        return "[ Contenido Visual / ASCII Art ]"

    # 2. Limitar longitud total inicial
    if len(text) > 300:
        text = text[:297] + "..."

    # 3. Escapado base de Graphviz
    text = text.replace('\\', '\\\\').replace('"', '\\"').replace('\r', '')
    
    # 4. Procesar por líneas para legibilidad en el diagrama
    raw_lines = text.split('\n')
    processed_lines = []
    total_chars = 0
    
    for line in raw_lines:
        line = line.strip()
        if not line: continue
        
        # Limitar ancho de línea a 60 caracteres (mejor para diagramas de flujo)
        if len(line) > 60:
            line = line[:57] + "..."
            
        # FORCE ASCII: Kroki/Graphviz a veces falla con Unicode extendido en layouts complejos
        line = "".join([c if ord(c) < 128 else "?" for c in line])
        
        processed_lines.append(line)
        total_chars += len(line)
        
        # Si ya llevamos demasiado texto acumulado para un solo nodo, parar
        if total_chars > limit:
            processed_lines.append("...")
            break
            
    return "\\n".join(processed_lines)

def sanitize_id(text):
    """Limpia IDs para Graphviz (solo alfanuméricos y guiones bajos)"""
    if not text: return "id_null"
    # Reemplazar puntos y espacios por guiones bajos
    text = text.replace('.', '_').replace(' ', '_')
    # Remover cualquier caracter que no sea ASCII alfanumérico o _
    return "".join([c if (c.isalnum() and ord(c) < 128) or c == '_' else '_' for c in text])

def extract_number(name):
    match = re.search(r'\d+', name)
    if match:
        return int(match.group())
    return None

def should_process(name, nombre_base="ejercicio", numero_al_principio=False, rango_inicio=None, rango_fin=None):
    name_lower = name.lower()
    base_lower = nombre_base.lower()
    
    # 1. Verificar si contiene el nombre base
    if base_lower not in name_lower:
        return False
        
    # 2. Verificar rango de números
    number = extract_number(name)
    if number is not None:
        if rango_inicio is not None and number < rango_inicio:
            return False
        if rango_fin is not None and number > rango_fin:
            return False
    else:
        # Filtrado estricto si hay rango activado
        if rango_inicio is not None or rango_fin is not None:
            return False
            
    return True

class TextRedirector:
    """Redirige stdout a un widget de texto."""
    def __init__(self, widget, tag="stdout"):
        self.widget = widget
        self.tag = tag

    def write(self, str):
        self.widget.configure(state="normal")
        self.widget.insert("end", str, (self.tag,))
        self.widget.see("end")
        self.widget.configure(state="disabled")

    def flush(self):
        pass
