#!/usr/bin/env python3
# orchestrator_app.py
# pip install customtkinter

import os
import subprocess
import threading
import json
import customtkinter as ctk
from tkinter import messagebox, filedialog

# Tema Dark Mode com verde de destaque
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")

VALID_CREDENTIALS = {"Renan": "senha"}
SCRIPTS_DIR = os.path.join(os.getcwd(), "scripts")
CONFIG_FILE = os.path.join(os.getcwd(), "scripts_config.json")

class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🔒 Login - Orquestrador RPA")
        self.geometry("400x200")
        self.resizable(False, False)
        self.configure(fg_color="#121212")

        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self, text="Orquestrador RPA", font=ctk.CTkFont(size=24, weight="bold")).grid(row=0, column=0, pady=(20,10))
        self.user_entry = ctk.CTkEntry(self, placeholder_text="Usuário")
        self.user_entry.grid(row=1, column=0, sticky="ew", padx=40)
        self.pass_entry = ctk.CTkEntry(self, placeholder_text="Senha", show="*")
        self.pass_entry.grid(row=2, column=0, sticky="ew", padx=40, pady=(10,0))
        login_btn = ctk.CTkButton(self, text="Entrar", fg_color="#2ecc71", hover_color="#27ae60", command=self.check_login)
        login_btn.grid(row=3, column=0, pady=20)

        # Permitir Enter para login
        self.bind('<Return>', lambda event: self.check_login())

    def check_login(self):
        u = self.user_entry.get().strip()
        p = self.pass_entry.get().strip()
        if VALID_CREDENTIALS.get(u) == p:
            self.destroy()
            MainApp().mainloop()
        else:
            messagebox.showerror("Login falhou", "Credenciais inválidas!")

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🛠 Orquestrador Utilitários RPA")
        self.geometry("1000x600")
        self.minsize(800,500)
        self.configure(fg_color="#121212")

        # layout responsivo
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # carrega config
        self.config = self._load_config()

        # tabview responsiva
        tabview = ctk.CTkTabview(self)
        tabview.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        tabview.add("Scripts"); tabview.add("Logs")
        scripts_tab = tabview.tab("Scripts")
        logs_tab = tabview.tab("Logs")
        scripts_tab.grid_rowconfigure(1, weight=1);
        scripts_tab.grid_columnconfigure(0, weight=1)
        logs_tab.grid_rowconfigure(1, weight=1);
        logs_tab.grid_columnconfigure(0, weight=1)

        # Scripts tab
        ctk.CTkLabel(scripts_tab, text="Módulos Disponíveis", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, pady=(0,10))
        self.scripts_frame = ctk.CTkScrollableFrame(scripts_tab)
        self.scripts_frame.grid(row=1, column=0, sticky="nsew")
        btn_bar = ctk.CTkFrame(scripts_tab, fg_color="#1e1e1e")
        btn_bar.grid(row=2, column=0, pady=10, sticky="ew")
        btn_bar.grid_columnconfigure((0,1,2), weight=1)
        ctk.CTkButton(btn_bar, text="➕ Adicionar", fg_color="#2ecc71", hover_color="#27ae60", command=self.add_script).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(btn_bar, text="➖ Remover", fg_color="#e74c3c", hover_color="#c0392b", command=self.remove_script).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(btn_bar, text="🔄 Atualizar", fg_color="#3498db", hover_color="#2980b9", command=self.load_scripts).grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        # Logs tab
        ctk.CTkLabel(logs_tab, text="Log de Execução", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, pady=(0,10))
        self.log_text = ctk.CTkTextbox(logs_tab, state="disabled", wrap="word")
        self.log_text.grid(row=1, column=0, sticky="nsew")
        ctk.CTkButton(logs_tab, text="🗑 Limpar Log", fg_color="#e67e22", hover_color="#d35400", command=self.clear_log).grid(row=2, column=0, pady=10, sticky="e")

        self.load_scripts()

    def _load_config(self):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"manual_scripts": []}

    def _save_config(self):
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar config: {e}")

    def add_script(self):
        path = filedialog.askopenfilename(title="Adicionar Script Python", filetypes=[("Python Files", "*.py")])
        if path and path not in self.config.setdefault("manual_scripts", []):
            self.config["manual_scripts"].append(path)
            self._save_config(); self.load_scripts()

    def remove_script(self):
        # escolhe manualmente o script para remover
        path = filedialog.askopenfilename(title="Remover Script Python", initialdir=os.getcwd(), filetypes=[("Python Files", "*.py")])
        if path:
            if path in self.config.get("manual_scripts", []):
                self.config["manual_scripts"].remove(path)
                self._save_config(); self.load_scripts()
            else:
                messagebox.showwarning("Aviso", "Esse script não está na lista manual.")

    def load_scripts(self):
        for w in self.scripts_frame.winfo_children(): w.destroy()
        entries = []
        if os.path.isdir(SCRIPTS_DIR):
            for f in sorted(os.listdir(SCRIPTS_DIR)):
                if f.endswith('.py'):
                    entries.append((f, os.path.join(SCRIPTS_DIR, f)))
        for p in self.config.get("manual_scripts", []):
            if os.path.isfile(p): entries.append((os.path.basename(p), p))
        if not entries:
            ctk.CTkLabel(self.scripts_frame, text="Nenhum módulo disponível.").pack(pady=20)
            return
        for label, path in entries:
            btn = ctk.CTkButton(self.scripts_frame, text=label, corner_radius=8,
                                fg_color="#2c3e50", hover_color="#34495e",
                                command=lambda p=path, l=label: self.run_script(p, l))
            btn._path = path
            btn.pack(fill="x", pady=4, padx=6)

    def run_script(self, path, label):
        if not messagebox.askyesno("Confirmação", f"Executar '{label}'?" ): return
        self.clear_log(); threading.Thread(target=self._exec_thread, args=(path, label), daemon=True).start()

    def _exec_thread(self, path, label):
        proc = subprocess.Popen(['python', path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in proc.stdout: self.append_log(line)
        proc.wait(); status = 'sucesso' if proc.returncode == 0 else f'erro ({proc.returncode})'
        self.append_log(f"\n{label} finalizado com {status}.\n")

    def append_log(self, text):
        self.log_text.configure(state="normal")
        self.log_text.insert(ctk.END, text)
        self.log_text.see(ctk.END)
        self.log_text.configure(state="disabled")

    def clear_log(self):
        self.log_text.configure(state="normal"); self.log_text.delete('0.0', ctk.END); self.log_text.configure(state="disabled")

if __name__ == '__main__':
    LoginWindow().mainloop()