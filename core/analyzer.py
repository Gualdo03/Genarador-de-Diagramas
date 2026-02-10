import os
import ast
import re
import random
from pyflowchart import Flowchart
from core.utils import sanitize_id, escape_dot_label
from core.renderer import (
    flowchart_js_to_graphviz_dot, 
    flowchart_js_to_mermaid, 
    generate_pdf_from_diagram
)

def get_dot_content(code, file_prefix="main", simplify=True, inner=True, conds_align=True):
    """Analiza código Python y devuelve nodos, enlaces y DEFINICIONES (para linkeo)"""
    all_nodes = []
    all_links = []
    definitions = {} # { "func_name": "HEAD_NODE_ID" }
    
    try:
        tree = ast.parse(code)
        
        # 1. Extraer funciones/métodos
        functions_to_process = []
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions_to_process.append(("", node.name))
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                for subnode in node.body:
                    if isinstance(subnode, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        functions_to_process.append((node.name, subnode.name))

        # 2. Código Root
        root_nodes = [n for n in tree.body if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]
        if root_nodes:
            main_code = ast.unparse(root_nodes) if hasattr(ast, 'unparse') else code
            if main_code.strip():
                fc = Flowchart.from_code(main_code, field='', inner=inner, simplify=simplify, conds_align=conds_align)
                nodes, links = flowchart_js_to_graphviz_dot(fc.flowchart(), f"{file_prefix}_ROOT")
                all_nodes.extend(nodes)
                all_links.extend(links)

        # 3. Funciones
        for class_name, func_name in functions_to_process:
            field_path = f"{class_name}.{func_name}" if class_name else func_name
            try:
                uniq = random.randint(0,9999)
                prefix = sanitize_id(f"{file_prefix}_FN_{field_path}_{uniq}")
                
                fc = Flowchart.from_code(code, field=field_path, inner=True, simplify=False, conds_align=conds_align)
                nodes, links = flowchart_js_to_graphviz_dot(fc.flowchart(), prefix)
                
                header_id = f"HEAD_{prefix}"
                header_label = escape_dot_label(f"FUNC: {field_path}", limit=60)
                all_nodes.append(f'    {header_id} [label="{header_label}", shape=component, style=filled, fillcolor="#B2EBF2"];')
                
                definitions[func_name] = header_id
                if class_name:
                    definitions[field_path] = header_id

                if nodes:
                    all_nodes.extend(nodes)
                    first_node_id = None
                    for n in nodes:
                        if 'shape=oval' in n:
                             first_node_id = n.split('[')[0].strip()
                             break
                    if not first_node_id and nodes:
                         first_node_id = nodes[0].split('[')[0].strip()
                    
                    if first_node_id:
                        all_links.append(f'    {header_id} -> {first_node_id} [style=dotted];')
                        
                all_links.extend(links)
            except:
                continue
                
    except Exception:
        try:
             flowchart = Flowchart.from_code(code, field='', inner=inner, simplify=simplify, conds_align=conds_align)
             nodes, links = flowchart_js_to_graphviz_dot(flowchart.flowchart(), f"{file_prefix}_FALLBACK")
             all_nodes.extend(nodes)
             all_links.extend(links)
        except:
             pass

    return all_nodes, all_links, definitions

def get_dot_content_generic(code, file_prefix="main", lang="java"):
    """Analizador estructurado para lenguajes basados en llaves (Java, JS, C++, etc)"""
    all_nodes = []
    all_links = []
    
    code = re.sub(r'//.*', '', code)
    code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
    
    lines = code.splitlines()
    stack = []
    last_node = None
    p = sanitize_id(file_prefix)
    
    start_id = f"{p}_start"
    all_nodes.append(f'    {start_id} [label="INICIO: {file_prefix}", shape=oval, style=filled, fillcolor="#E3F2FD"];')
    last_node = start_id

    node_count = 0
    for i, line in enumerate(lines):
        line = line.strip()
        if not line: continue
        
        node_count += 1
        current_id = f"{p}_node_{node_count}"
        
        is_if = line.startswith("if")
        is_while = line.startswith("while")
        is_for = line.startswith("for")
        is_else = "else" in line
        
        is_cond = is_if or is_while or is_for or (is_else and "if" in line)
        is_end_block = "}" in line
        
        clean_label = escape_dot_label(line, limit=50)
        
        if is_cond:
            all_nodes.append(f'    {current_id} [label="{clean_label}", shape=diamond, style=filled, fillcolor="#FFF3E0"];')
            if last_node:
                all_links.append(f'    {last_node} -> {current_id};')
            out_id = f"{p}_out_{node_count}"
            stack.append((current_id, out_id))
            last_node = current_id
            
        elif is_else and not "if" in line:
            if stack:
                cond_id, _ = stack[-1]
                all_nodes.append(f'    {current_id} [label="else", shape=rectangle, style=filled, fillcolor="#F5F5F5"];')
                all_links.append(f'    {cond_id} -> {current_id} [label="no"];')
                last_node = current_id
                
        elif is_end_block:
            if stack:
                cond_id, out_id = stack.pop()
                all_nodes.append(f'    {out_id} [label="", shape=point];')
                if last_node:
                    all_links.append(f'    {last_node} -> {out_id};')
                all_links.append(f'    {cond_id} -> {out_id} [label="no"];')
                last_node = out_id
        else:
            all_nodes.append(f'    {current_id} [label="{clean_label}", shape=rectangle];')
            if last_node:
                all_links.append(f'    {last_node} -> {current_id};')
            last_node = current_id

    end_id = f"{p}_end"
    all_nodes.append(f'    {end_id} [label="FIN", shape=oval, style=filled, fillcolor="#FFEBEE"];')
    if last_node:
        all_links.append(f'    {last_node} -> {end_id};')

    return all_nodes, all_links, {}

def get_local_dependencies(file_path, processed_files=None, project_root=None):
    if processed_files is None:
        processed_files = set()
    file_path = os.path.abspath(file_path)
    if file_path in processed_files:
        return []
    processed_files.add(file_path)
    dependencies = [file_path]
    if project_root is None:
        project_root = os.path.dirname(file_path)
    current_dir = os.path.dirname(file_path)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
            tree = ast.parse(code)
        import_info = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    import_info.append(('absolute', alias.name, None))
            elif isinstance(node, ast.ImportFrom):
                module = node.module if node.module else ''
                level = node.level
                import_info.append(('from', module, level))
        for import_type, module_name, level in import_info:
            potential_files = []
            if import_type == 'absolute' or (import_type == 'from' and level == 0):
                base_mod = module_name.split('.')[0]
                potential_files.append(os.path.join(project_root, f"{base_mod}.py"))
                pkg_dir = os.path.join(project_root, base_mod)
                if os.path.isdir(pkg_dir):
                    init_file = os.path.join(pkg_dir, "__init__.py")
                    if os.path.exists(init_file):
                        potential_files.append(init_file)
                    if '.' in module_name:
                        parts = module_name.split('.')
                        submod_path = os.path.join(project_root, *parts[:-1], f"{parts[-1]}.py")
                        potential_files.append(submod_path)
            elif import_type == 'from' and level > 0:
                base_dir = current_dir
                for _ in range(level - 1):
                    base_dir = os.path.dirname(base_dir)
                if module_name:
                    base_mod = module_name.split('.')[0]
                    potential_files.append(os.path.join(base_dir, f"{base_mod}.py"))
                else:
                    potential_files.append(os.path.join(base_dir, "__init__.py"))
            for pot_file in potential_files:
                if os.path.exists(pot_file) and pot_file not in processed_files:
                    sub_deps = get_local_dependencies(pot_file, processed_files, project_root)
                    dependencies.extend(sub_deps)
    except Exception:
        pass
    return list(dict.fromkeys(dependencies))

def generate_flowchart_from_code(input_data, output_path, simulacion=False, save_mmd=False, theme_name="default", 
                                 simplify=True, inner=True, conds_align=True, engine="graphviz"):
    if engine == "mermaid":
        code = input_data if isinstance(input_data, str) else "\n".join([c for _, c in input_data])
        try:
            flowchart = Flowchart.from_code(code, field='', inner=inner, simplify=simplify, conds_align=conds_align)
            diagram_code = flowchart_js_to_mermaid(flowchart.flowchart(), theme_name)
            return generate_pdf_from_diagram(diagram_code, output_path, simulacion, engine)
        except:
            return False

    dot_lines = [
            "digraph G {",
            "    rankdir=TB;",
            "    compound=true;",
            "    nodesep=0.5;",
            "    ranksep=0.7;",
            "    node [fontname=\"Arial\", fontsize=11, style=filled, fillcolor=white];",
            "    edge [fontname=\"Arial\", fontsize=10];",
            ""
    ]

    all_content_nodes = []
    all_content_links = []
    global_definitions = {} 

    try:
        if isinstance(input_data, str):
            nodes, links, defs = get_dot_content(input_data, "main", simplify, inner, conds_align)
            all_content_nodes.extend(nodes)
            all_content_links.extend(links)
        
        elif isinstance(input_data, list):
            for i, (fname, fcode) in enumerate(input_data):
                safe_name = sanitize_id(fname)
                prefix = f"FILE_{i}_{safe_name}"
                ext = fname.split('.')[-1].lower() if '.' in fname else 'py'
                try:
                    if ext == 'py':
                        nodes, links, defs = get_dot_content(fcode, prefix, simplify, inner, conds_align)
                    else:
                        nodes, links, defs = get_dot_content_generic(fcode, prefix, ext)
                except Exception as e:
                    nodes, links, defs = [], [], {}
                
                for func_name, node_id in defs.items():
                    if func_name not in global_definitions:
                        global_definitions[func_name] = []
                    global_definitions[func_name].append(node_id)
                
                if nodes:
                    dot_lines.append(f"    subgraph cluster_{i} {{")
                    clean_fname = escape_dot_label(fname, limit=60)
                    dot_lines.append(f'        label = "{clean_fname}";')
                    dot_lines.append('        style=filled;')
                    dot_lines.append('        color="#F5F5F5";')
                    dot_lines.append('        fontsize=14;')
                    for n in nodes:
                        dot_lines.append(f"    {n}")
                        all_content_nodes.append(n)
                    for l in links:
                        dot_lines.append(f"    {l}")
                    dot_lines.append("    }")
                    dot_lines.append('')
        
        if isinstance(input_data, str):
            dot_lines.extend(all_content_nodes)
            dot_lines.extend(all_content_links)

        dot_lines.append("}")
        diagram_code = "\n".join(dot_lines)
        return generate_pdf_from_diagram(diagram_code, output_path, simulacion, engine)
    except Exception as e:
        print(f"\n    Error procesando lógica del flowchart: {e}")
        return False
