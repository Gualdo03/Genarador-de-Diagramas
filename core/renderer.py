import requests
import re
from core.utils import sanitize_id, escape_dot_label

def flowchart_js_to_mermaid(flowchart_code, theme_name="default"):
    """Convierte flowchart.js a Mermaid (legacy, usar Graphviz para más detalle)"""
    lines = flowchart_code.splitlines()
    mermaid_lines = []
    
    # Inject Theme if not default
    if theme_name and theme_name != "default":
        mermaid_lines.append(f"%%{{init: {{'theme': '{theme_name}'}} }}%%")
        
    mermaid_lines.append("graph TD")
    
    # Regex patterns to parse flowchart.js syntax
    node_pattern = re.compile(r'(\w+)=>(\w+):\s*(.*)')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Parse Nodes
        match_node = node_pattern.match(line)
        if match_node:
            nid, ntype, ntext = match_node.groups()
            ntext = ntext.replace('"', "'") 
            
            if ntype == 'start' or ntype == 'end':
                mermaid_lines.append(f'    {nid}(["{ntext}"])')
            elif ntype == 'operation':
                mermaid_lines.append(f'    {nid}["{ntext}"]')
            elif ntype == 'inputoutput':
                mermaid_lines.append(f'    {nid}[/"{ntext}"/]')
            elif ntype == 'subroutine':
                mermaid_lines.append(f'    {nid}[["{ntext}"]]')
            elif ntype == 'condition':
                mermaid_lines.append(f'    {nid}{{"{ntext}"}}')
            else:
                mermaid_lines.append(f'    {nid}["{ntext}"]')
            continue
            
        # Parse Links
        if "->" in line:
            parts = line.split("->")
            for i in range(len(parts) - 1):
                src = parts[i].strip()
                dst = parts[i+1].strip()
                
                condition = ""
                if "(" in src and src.endswith(")"):
                    if "(yes)" in src:
                        condition = "|yes|"
                        src = src.replace("(yes)", "")
                    elif "(no)" in src:
                        condition = "|no|"
                        src = src.replace("(no)", "")
                
                if condition:
                    mermaid_lines.append(f'    {src} -->{condition} {dst}')
                else:
                    mermaid_lines.append(f'    {src} --> {dst}')

    return "\n".join(mermaid_lines)

def flowchart_js_to_graphviz_dot(flowchart_code, prefix=""):
    """Convierte flowchart.js a Graphviz DOT manejando bloques multi-línea"""
    lines = flowchart_code.splitlines()
    nodes_dot = []
    links_dot = []
    
    node_pattern = re.compile(r'^(\w+)=>(\w+):\s*(.*)')
    
    current_node = None
    node_definitions = {} # nid -> {type, text}

    # Fase 1: Recolectar definiciones de nodos (corrigiendo cortes de splitlines)
    for line in lines:
        if "=>" in line and not line.strip().startswith("//") and "->" not in line:
            match = node_pattern.match(line)
            if match:
                nid, ntype, ntext = match.groups()
                current_node = nid
                node_definitions[nid] = {"type": ntype, "text": ntext}
                continue
        
        # Si no empieza por ID=> y hay un nodo activo, es continuación de texto
        if current_node and "->" not in line:
            node_definitions[current_node]["text"] += "\n" + line.strip()
            
    # Fase 2: Generar DOT para nodos
    node_types = {
        'start': 'oval', 'end': 'oval', 'operation': 'rectangle',
        'inputoutput': 'parallelogram', 'condition': 'diamond', 'subroutine': 'component'
    }
    
    for nid, ndata in node_definitions.items():
        raw_id = f"{prefix}_{nid}" if prefix else nid
        full_id = sanitize_id(raw_id)
        shape = node_types.get(ndata['type'], 'rectangle')
        label = escape_dot_label(ndata['text'])
        
        color = "#FFF9C4" # Default yellow
        if ndata['type'] == 'start': color = "#E3F2FD"
        elif ndata['type'] == 'end': color = "#FFEBEE"
        elif ndata['type'] == 'inputoutput': color = "#E8F5E9"
        elif ndata['type'] == 'condition': color = "#FFF3E0"
        elif ndata['type'] == 'subroutine': color = "#F3E5F5"
        
        nodes_dot.append(f'    {full_id} [label="{label}", shape={shape}, style=filled, fillcolor="{color}"];')
    
    # Parsear conexiones
    for line in lines:
        line = line.strip()
        if not line or "->" not in line:
            continue
            
        # Procesar cadenas de conexiones
        parts = line.split("->")
        for i in range(len(parts) - 1):
            src_raw = parts[i].strip()
            dst_raw = parts[i+1].strip()
            
            edge_label = ""
            # Detectar condiciones (yes/no) y eliminar direcciones (left/right)
            if "(" in src_raw and src_raw.endswith(")"):
                # Extraer contenido entre paréntesis
                paren_content = src_raw[src_raw.index("(")+1:src_raw.rindex(")")]
                
                # Buscar yes o no en el contenido
                if "yes" in paren_content.lower():
                    edge_label = ' [label="yes", color="#4CAF50", fontcolor="#4CAF50"]'
                elif "no" in paren_content.lower():
                    edge_label = ' [label="no", color="#F44336", fontcolor="#F44336"]'
                
                # Eliminar todo el paréntesis
                src_node = src_raw[:src_raw.index("(")].strip()
            else:
                src_node = src_raw
            
            # Aplicar prefijo y sanitizar IDs
            full_src = sanitize_id(f"{prefix}_{src_node}" if prefix else src_node)
            full_dst = sanitize_id(f"{prefix}_{dst_raw}" if prefix else dst_raw)
            
            links_dot.append(f'    {full_src} -> {full_dst}{edge_label};')
            
    return nodes_dot, links_dot

def generate_pdf_from_diagram(diagram_code, output_path, simulacion=False, engine="graphviz"):
    """Genera PDF desde código de diagrama usando Kroki.io (Optimizado para Proyectos Grandes)"""
    if simulacion:
        print(f"    [SIMULACIÓN] Generando PDF en: {output_path}")
        return True

    # Usar endpoint PDF directo para mejor calidad y menor carga de memoria local
    url = f"https://kroki.io/{engine}/pdf"
    
    print(f"    [DEBUG] Enviando {len(diagram_code)} chars a Kroki (endpoint /pdf)...")
    
    final_dot = "".join([c if (ord(c) < 128 and ord(c) >= 32) or c in '\n\r\t' else '?' for c in diagram_code])
    
    headers = {
        'Content-Type': 'text/plain; charset=utf-8',
        'X-Kroki-Optimize': 'true'
    }
    
    try:
        response = requests.post(url, data=final_dot.encode('utf-8'), headers=headers, timeout=120) 
        
        if response.status_code == 200:
            try:
                with open(output_path, "wb") as f:
                    f.write(response.content)
                return True
            except Exception as f_err:
                 print(f"    [!] Error guardando archivo PDF: {f_err}")
                 return False
        else:
            print(f"    [!] Kroki returned status {response.status_code}")
            debug_path = output_path + ".debug.dot"
            try:
                with open(debug_path, "w", encoding="utf-8") as f:
                    f.write(diagram_code)
                print(f"    [DEBUG] Código del diagrama guardado en: {debug_path}")
            except: pass
            return False
            
    except Exception as e:
        print(f"    [!] Error de conexión con Kroki: {e}")
        return False
