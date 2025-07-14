# orchestrator_app.py
# pip install customtkinter

import os
import subprocess
import threading
import customtkinter as ctk
from tkinter import messagebox, filedialog
import json

# Configura tema
ctk.set_appearance_mode("System")  # System, Light, Dark
ctk.set_default_color_theme("dark-blue")  # blue, dark-blue, green

# Credenciais (altere conforme necessário)
VALID_CREDENTIALS = {"Renan": "senha"}

# Diretório de scripts e arquivo de configuração
SCRIPTS_DIR = os.path.join(os.getcwd(), "scripts")
CONFIG_FILE = os.path.join(os.getcwd(), "scripts_config.json")

class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Login - Orquestrador RPA")
        self.geometry("400x200")
        self.resizable(False, False)

        ctk.CTkLabel(self, text="Orquestrador de Utilitários RPA", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(20,10))
        self.user_entry = ctk.CTkEntry(self, placeholder_text="Usuário")
        self.user_entry.pack(fill="x", padx=40, pady=(0,5))
        self.pass_entry = ctk.CTkEntry(self, placeholder_text="Senha", show="*")
        self.pass_entry.pack(fill="x", padx=40, pady=(0,20))
        ctk.CTkButton(self, text="Entrar", width=120, command=self.check_login).pack(pady=(0,10))

    def check_login(self):
        user = self.user_entry.get().strip()
        pwd = self.pass_entry.get().strip()
        if VALID_CREDENTIALS.get(user) == pwd:
            self.destroy()
            MainApp().mainloop()
        else:
            messagebox.showerror("Erro de Login", "Credenciais inválidas.")

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Orquestrador RPA Utilitários")
        self.geometry("1000x600")
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure((0,1), weight=1)

        # carrega config
        self.config = self._load_config()

        # Header
        header = ctk.CTkFrame(self)
        header.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=10, pady=5)
        header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(header, text="Selecione um Módulo", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, sticky="w")
        # Placeholder user info or logout

        # Left panel: scripts list
        menu = ctk.CTkFrame(self)
        menu.grid(row=1, column=0, sticky="nsew", padx=(10,5), pady=5)
        menu.grid_rowconfigure(1, weight=1)
        menu.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(menu, text="Módulos Disponíveis", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, pady=(0,10))
        self.scripts_scroll = ctk.CTkScrollableFrame(menu)
        self.scripts_scroll.grid(row=1, column=0, sticky="nsew")

        btn_frame = ctk.CTkFrame(menu)
        btn_frame.grid(row=2, column=0, pady=(10,0))
        ctk.CTkButton(btn_frame, text="Adicionar", width=100, command=self.add_script).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Atualizar", width=100, command=self.load_scripts).pack(side="left", padx=5)

        # Right panel: log output
        log_panel = ctk.CTkFrame(self)
        log_panel.grid(row=1, column=1, sticky="nsew", padx=(5,10), pady=5)
        log_panel.grid_rowconfigure(1, weight=1)
        log_panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(log_panel, text="Log de Execução", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, sticky="w", pady=(0,10))
        self.log_text = ctk.CTkTextbox(log_panel, state="disabled", wrap="word")
        self.log_text.grid(row=1, column=0, sticky="nsew")
        ctk.CTkButton(log_panel, text="Limpar Log", width=100, command=self.clear_log).grid(row=2, column=0, sticky="e", pady=(10,0))

        self.load_scripts()

    def _load_config(self):
        if os.path.isfile(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {"manual_scripts": []}
        return {"manual_scripts": []}

    def _save_config(self):
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar configuração: {e}")

    def add_script(self):
        path = filedialog.askopenfilename(title="Adicionar Script Python", filetypes=[("Python", "*.py")])
        if path:
            if path not in self.config.get("manual_scripts", []):
                self.config.setdefault("manual_scripts", []).append(path)
                self._save_config()
                messagebox.showinfo("Sucesso", f"'{os.path.basename(path)}' adicionado.")
            else:
                messagebox.showinfo("Info", "Script já está na lista.")
            self.load_scripts()

    def load_scripts(self):
        # limpa
        for widget in self.scripts_scroll.winfo_children():
            widget.destroy()
        entries = []
        # scripts da pasta
        if os.path.isdir(SCRIPTS_DIR):
            for f in sorted(os.listdir(SCRIPTS_DIR)):
                if f.endswith('.py'):
                    entries.append({'label': f, 'path': os.path.join(SCRIPTS_DIR, f)})
        # scripts manuais
        for p in self.config.get("manual_scripts", []):
            if os.path.isfile(p):
                entries.append({'label': os.path.basename(p), 'path': p})
        if not entries:
            ctk.CTkLabel(self.scripts_scroll, text="Nenhum módulo disponível.").pack(pady=10)
            return
        for entry in entries:
            btn = ctk.CTkButton(self.scripts_scroll, text=entry['label'], height=40,
                                command=lambda e=entry: self.run_script(e))
            btn.pack(fill="x", pady=5, padx=5)

    def run_script(self, entry):
        if not messagebox.askyesno("Confirmação", f"Executar '{entry['label']}'?"):
            return
        self.clear_log()
        threading.Thread(target=self._execute_script, args=(entry,), daemon=True).start()

    def _execute_script(self, entry):
        cmd = ['python', entry['path']]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in proc.stdout:
            self._append_log(line)
        proc.wait()
        status = "sucesso" if proc.returncode == 0 else f"erro ({proc.returncode})"
        self._append_log(f"\n{entry['label']} finalizado com {status}.\n")

    def _append_log(self, text):
        self.log_text.configure(state="normal")
        self.log_text.insert(ctk.END, text)
        self.log_text.see(ctk.END)
        self.log_text.configure(state="disabled")

    def clear_log(self):
        self.log_text.configure(state="normal")
        self.log_text.delete('0.0', ctk.END)
        self.log_text.configure(state="disabled")

if __name__ == '__main__':
    LoginWindow().mainloop()
