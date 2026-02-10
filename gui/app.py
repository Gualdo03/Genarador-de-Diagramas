import os
import sys
import threading
import platform
import subprocess
import customtkinter as ctk
from tkinter import filedialog
from core.utils import resource_path, extract_number, should_process, TextRedirector
from core.analyzer import generate_flowchart_from_code

def open_folder(path):
    try:
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
    except Exception as e:
        print(f"Error abriendo carpeta: {e}")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Generador de Diagramas de Flujo")
        self.geometry("1000x800")
        
        # Configurar Icono
        icon_path = resource_path("imagen.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception as e:
                print(f"No se pudo cargar el icono: {e}")

        
        # Configuración de Grid Principal
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # creamos el TabView
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        self.tab_inicio = self.tabview.add("Inicio")
        self.tab_terminal = self.tabview.add("Terminal")
        
        # Configurar grids de las pestañas
        self.tab_inicio.grid_columnconfigure(1, weight=1)
        self.tab_terminal.grid_columnconfigure(0, weight=1)
        self.tab_terminal.grid_rowconfigure(0, weight=1)

        # ====================
        # PESTAÑA INICIO
        # ====================

        # --- Fila 0: Carpeta ---
        self.label_path = ctk.CTkLabel(self.tab_inicio, text="Carpeta a Escanear:")
        self.label_path.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        self.entry_path = ctk.CTkEntry(self.tab_inicio, placeholder_text="Selecciona una carpeta...")
        self.entry_path.grid(row=0, column=1, padx=20, pady=(20, 10), sticky="ew")
        
        self.btn_browse = ctk.CTkButton(self.tab_inicio, text="Examinar", command=self.browse_folder)
        self.btn_browse.grid(row=0, column=2, padx=20, pady=(20, 10))

        # --- Fila 1: Configuración Básica ---
        self.frame_config = ctk.CTkFrame(self.tab_inicio)
        self.frame_config.grid(row=1, column=0, columnspan=3, padx=20, pady=10, sticky="ew")
        
        # Grid para organizar elementos dentro del frame
        self.frame_config.grid_columnconfigure(1, weight=1)
        self.frame_config.grid_columnconfigure(3, weight=1)

        # Fila superior: Filtro y Switch
        self.label_base_filter = ctk.CTkLabel(self.frame_config, text="Filtro por Nombre (opcional):")
        self.label_base_filter.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        
        self.entry_base = ctk.CTkEntry(self.frame_config, placeholder_text="ej: ejercicio")
        self.entry_base.insert(0, "") # Default vacío para procesar todo
        self.entry_base.grid(row=0, column=1, padx=10, pady=(10, 5), sticky="ew")

        self.switch_num_pos = ctk.CTkSwitch(self.frame_config, text="El archivo comienza con número")
        self.switch_num_pos.grid(row=0, column=2, columnspan=2, padx=20, pady=(10, 5), sticky="w")

        # Fila inferior: Nombre salida
        self.label_output_name = ctk.CTkLabel(self.frame_config, text="Nombre de los archivos creados:")
        self.label_output_name.grid(row=1, column=0, padx=10, pady=(5, 5), sticky="w")
        
        self.entry_output = ctk.CTkEntry(self.frame_config)
        self.entry_output.insert(0, "Diagrama") 
        self.entry_output.grid(row=1, column=1, padx=10, pady=(5, 5), sticky="ew")

        # Motor de Renderizado
        self.label_engine = ctk.CTkLabel(self.frame_config, text="Motor de Renderizado:")
        self.label_engine.grid(row=2, column=0, padx=10, pady=(5, 10), sticky="w")
        
        self.combo_engine = ctk.CTkComboBox(self.frame_config, values=["Graphviz (Más detalle)", "Mermaid (Más simple)"], width=200)
        self.combo_engine.set("Graphviz (Más detalle)")
        self.combo_engine.grid(row=2, column=1, padx=10, pady=(5, 10), sticky="w")

        # Extensiones
        self.label_ext = ctk.CTkLabel(self.frame_config, text="Extensiones (separadas por coma):")
        self.label_ext.grid(row=3, column=0, padx=10, pady=(5, 10), sticky="w")

        self.entry_ext = ctk.CTkEntry(self.frame_config)
        self.entry_ext.insert(0, "py")
        self.entry_ext.grid(row=3, column=1, padx=10, pady=(5, 10), sticky="ew")

        # --- Fila 2: Rangos ---
        self.frame_rango = ctk.CTkFrame(self.tab_inicio)
        self.frame_rango.grid(row=2, column=0, columnspan=3, padx=20, pady=10, sticky="ew")

        # Switch a la izquierda
        self.switch_use_rango = ctk.CTkSwitch(self.frame_rango, text="Activar Filtro Rango")
        self.switch_use_rango.pack(side="left", padx=10, pady=10)
        self.switch_use_rango.deselect() # Iniciar desactivado

        self.label_rango = ctk.CTkLabel(self.frame_rango, text="Rango:")
        self.label_rango.pack(side="left", padx=5)

        self.entry_start = ctk.CTkEntry(self.frame_rango, width=80, placeholder_text="Inicio")
        self.entry_start.insert(0, "91")
        self.entry_start.pack(side="left", padx=5)

        self.label_dash = ctk.CTkLabel(self.frame_rango, text="-")
        self.label_dash.pack(side="left", padx=5)

        self.entry_end = ctk.CTkEntry(self.frame_rango, width=80, placeholder_text="Fin")
        self.entry_end.insert(0, "120")
        self.entry_end.pack(side="left", padx=5)

        # --- Fila 3: Opciones Extra ---
        self.frame_opts = ctk.CTkFrame(self.tab_inicio)
        self.frame_opts.grid(row=3, column=0, columnspan=3, padx=20, pady=10, sticky="ew")

        # Columna 1 de opciones
        self.switch_recursive = ctk.CTkSwitch(self.frame_opts, text="Buscar también en subcarpetas")
        self.switch_recursive.pack(side="top", anchor="w", padx=20, pady=5)
        self.switch_recursive.select()

        self.switch_sim = ctk.CTkSwitch(self.frame_opts, text="Modo Simulación (No generar archivos)")
        self.switch_sim.pack(side="top", anchor="w", padx=20, pady=5)
        
        self.switch_open = ctk.CTkSwitch(self.frame_opts, text="Abrir carpeta al finalizar")
        self.switch_open.select()
        self.switch_open.pack(side="top", anchor="w", padx=20, pady=5)


        # --- Fila 4: Botón Acción ---
        self.btn_run = ctk.CTkButton(self.tab_inicio, text="GENERAR DIAGRAMAS", height=50, font=("Roboto", 16, "bold"), command=self.start_process_thread)
        self.btn_run.grid(row=4, column=0, columnspan=3, padx=20, pady=20, sticky="ew")

        # ====================
        # PESTAÑA TERMINAL
        # ====================
        self.textbox_log = ctk.CTkTextbox(self.tab_terminal, font=("Consolas", 12))
        self.textbox_log.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.textbox_log.configure(state="disabled")

        self.btn_clear = ctk.CTkButton(self.tab_terminal, text="Limpiar Terminal", command=self.clear_log)
        self.btn_clear.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        # Redirigir stdout
        sys.stdout = TextRedirector(self.textbox_log)

    def clear_log(self):
        self.textbox_log.configure(state="normal")
        self.textbox_log.delete("1.0", "end")
        self.textbox_log.configure(state="disabled")

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.entry_path.delete(0, "end")
            self.entry_path.insert(0, folder)
            self.detect_range(folder)

    def detect_range(self, folder):
        try:
            files_found = []
            all_detected_exts = set()
            is_recursive = self.switch_recursive.get()
            
            if is_recursive:
                for root, dirs, files in os.walk(folder):
                    for f in files:
                        if '.' in f:
                            ext = f.split('.')[-1].lower()
                            if ext in ['py', 'java', 'js', 'cpp', 'c', 'h', 'cs', 'php', 'html', 'css', 'ts', 'txt']:
                                all_detected_exts.add(ext)
                                files_found.append(f)
            else:
                for f in os.listdir(folder):
                    if os.path.isfile(os.path.join(folder, f)) and '.' in f:
                        ext = f.split('.')[-1].lower()
                        if ext in ['py', 'java', 'js', 'cpp', 'c', 'h', 'cs', 'php', 'html', 'css', 'ts', 'txt']:
                            all_detected_exts.add(ext)
                            files_found.append(f)

            if all_detected_exts:
                new_ext_str = ", ".join(sorted(list(all_detected_exts)))
                self.entry_ext.delete(0, "end")
                self.entry_ext.insert(0, new_ext_str)
                print(f"Extensiones detectadas automáticamente: {new_ext_str}")

            nums = []
            for name in files_found:
                n = extract_number(name)
                if n is not None:
                    nums.append(n)
            
            if nums:
                min_n = min(nums)
                max_n = max(nums)
                self.entry_start.delete(0, "end")
                self.entry_start.insert(0, str(min_n))
                self.entry_end.delete(0, "end")
                self.entry_end.insert(0, str(max_n))
                print(f"Rango detectado: {min_n} - {max_n}")
            else:
                self.entry_start.delete(0, "end")
                self.entry_end.delete(0, "end")

        except Exception as e:
            print(f"Error detectando contenido de la carpeta: {e}")


    def start_process_thread(self):
        self.btn_run.configure(state="disabled", text="Procesando...")
        thread = threading.Thread(target=self.run_process)
        thread.start()

    def run_process(self):
        try:
            target_dir = self.entry_path.get().strip()
            if not target_dir:
                 target_dir = os.path.dirname(os.path.abspath(__file__))
            
            nombre_base = self.entry_base.get().strip()
            output_name_user = self.entry_output.get().strip()
            if not output_name_user: output_name_user = "Diagrama"

            num_pos = self.switch_num_pos.get()
            simulacion = self.switch_sim.get()
            abrir_final = self.switch_open.get()
            recursivo = self.switch_recursive.get()
            
            theme = "default"
            simplify_mode = False 
            
            engine_choice = self.combo_engine.get()
            engine = "graphviz" if "Graphviz" in engine_choice else "mermaid"
            
            inner_mode = True  
            conds_align_mode = True  

            r_inicio = None
            r_fin = None
            use_rango_filter = self.switch_use_rango.get()

            if use_rango_filter:
                try:
                    val_s = self.entry_start.get().strip()
                    val_e = self.entry_end.get().strip()
                    if val_s: r_inicio = int(val_s)
                    if val_e: r_fin = int(val_e)
                except ValueError:
                    print("Error: Los rangos deben ser números enteros.")
                    self.reset_button()
                    return

            print("\n--- INICIANDO PROCESO ---")
            print(f"Carpeta: {target_dir}")
            print(f"Config: Base='{nombre_base}', Rango={r_inicio}-{r_fin}, Simulación={simulacion}")

            if not os.path.exists(target_dir):
                print(f"Error: La carpeta '{target_dir}' no existe.")
                self.reset_button()
                return

            candidate_files = []

            if "." in nombre_base:
                _, autodetect_ext = os.path.splitext(nombre_base)
                if autodetect_ext:
                    clean_ext = autodetect_ext.replace(".", "")
                    try:
                        self.entry_ext.delete(0, "end")
                        self.entry_ext.insert(0, clean_ext)
                    except: pass
            
            ext_str = self.entry_ext.get().strip()
            valid_exts = tuple(f".{e.strip().replace('.', '')}" for e in ext_str.split(',') if e.strip())
            if not valid_exts: valid_exts = ('.py',)

            if recursivo:
                for root, dirs, files in os.walk(target_dir):
                     for file in files:
                         if file.lower().endswith(valid_exts):
                             candidate_files.append(os.path.join(root, file))
            else:
                 if os.path.exists(target_dir):
                     for file in os.listdir(target_dir):
                         if file.lower().endswith(valid_exts):
                            candidate_files.append(os.path.join(target_dir, file))

            valid_files = []
            for f_path in candidate_files:
                f_name = os.path.basename(f_path)
                if f_name == "generador_diagramas3000.py":
                    continue
                if should_process(f_name, nombre_base, num_pos, r_inicio, r_fin):
                    valid_files.append(f_path)
            
            try:
                valid_files.sort(key=lambda x: extract_number(os.path.basename(x)) if extract_number(os.path.basename(x)) is not None else x)
            except:
                valid_files.sort()

            grouped_by_dir = {}
            for vf in valid_files:
                parent = os.path.dirname(vf)
                if parent not in grouped_by_dir:
                    grouped_by_dir[parent] = []
                grouped_by_dir[parent].append(vf)
            
            processed_count = 0
            success_count = 0
            abs_target_dir = os.path.abspath(target_dir)

            if not valid_files:
                 print("No se encontraron archivos que coincidan con los criterios.")
            else:
                for folder, seed_files in grouped_by_dir.items():
                    processed_in_this_folder = set()
                    for seed in seed_files:
                        if seed in processed_in_this_folder: continue
                        seed_name = os.path.basename(seed)
                        seed_dir = os.path.dirname(seed)
                        
                        project_bundle = [seed]  
                        try:
                            for item in os.listdir(seed_dir):
                                item_path = os.path.join(seed_dir, item)
                                if os.path.isdir(item_path):
                                    for subfile in os.listdir(item_path):
                                        if subfile.lower().endswith(valid_exts):
                                            subfile_path = os.path.join(item_path, subfile)
                                            if subfile_path not in project_bundle:
                                                project_bundle.append(subfile_path)
                        except: pass
                        
                        n = extract_number(seed_name)
                        if n is not None:
                            out_name = f"{output_name_user} {n}.pdf"
                        else:
                            base_no_ext = os.path.splitext(seed_name)[0]
                            out_name = f"{output_name_user}_{base_no_ext}.pdf"
                        
                        data_payload = []
                        for py_file in project_bundle:
                             try:
                                with open(py_file, 'r', encoding='utf-8') as f:
                                    fname = os.path.basename(py_file)
                                    fcode = f.read()
                                    if fcode.strip():
                                        data_payload.append((fname, fcode))
                             except: pass

                        if not data_payload: continue
                        
                        output_pdf_path = os.path.join(folder, out_name)
                        try:
                            result = generate_flowchart_from_code(data_payload, output_pdf_path, simulacion, save_mmd=False, theme_name=theme, 
                                                           simplify=simplify_mode, inner=inner_mode, conds_align=conds_align_mode, engine=engine)
                            if result:
                                print(f"    [ÉXITO] Hecho -> {out_name}")
                                success_count += 1
                            else:
                                print(f"    [ERROR] Falló la generación ({out_name}).")
                            processed_count += 1
                        except: pass
                        
                        for b_file in project_bundle:
                            processed_in_this_folder.add(b_file)

            if abrir_final and not simulacion:
                open_folder(target_dir)
        except Exception as e:
            print(f"\nERROR CRÍTICO: {e}")
        finally:
            self.reset_button()

    def reset_button(self):
        self.btn_run.configure(state="normal", text="GENERAR DIAGRAMAS")
