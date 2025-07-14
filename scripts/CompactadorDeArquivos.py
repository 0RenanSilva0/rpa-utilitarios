#!/usr/bin/env python3
"""
Zip/Unzip Automatizado com GUI em CustomTkinter

Funcionalidades:
 - Compactar uma pasta em .zip
 - Descompactar um .zip em pasta de destino

Uso:
  python zip_unzip_app.py

UI limpa, com seleção de arquivos/pastas, spinner e log em tempo real
"""
import os
import threading
import zipfile
import customtkinter as ctk
from tkinter import filedialog, messagebox

# Configura tema CustomTkinter
ctk.set_appearance_mode("System")  # System, Light, Dark
ctk.set_default_color_theme("green")  # blue, dark-blue, green

class ZipUnzipApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Zip/Unzip Automático")
        self.geometry("600x450")
        self.minsize(500, 400)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(8, weight=1)

        # Modo: Compactar ou Descompactar
        ctk.CTkLabel(self, text="Modo:", anchor="w").grid(row=0, column=0, sticky="ew", padx=20, pady=(20,5))
        self.mode_combo = ctk.CTkComboBox(self, values=["Compactar (Zip)", "Descompactar (Unzip)"], state="readonly")
        self.mode_combo.set("Compactar (Zip)")
        self.mode_combo.grid(row=1, column=0, sticky="ew", padx=20)

        # Input
        ctk.CTkLabel(self, text="Arquivo/Pasta de entrada:", anchor="w").grid(row=2, column=0, sticky="ew", padx=20, pady=(15,5))
        frame_in = ctk.CTkFrame(self)
        frame_in.grid(row=3, column=0, sticky="ew", padx=20)
        frame_in.grid_columnconfigure(0, weight=1)
        self.entry_input = ctk.CTkEntry(frame_in, placeholder_text="Selecione pasta ou arquivo...")
        self.entry_input.grid(row=0, column=0, sticky="ew")
        ctk.CTkButton(frame_in, text="Browse", width=80, command=self.browse_input).grid(row=0, column=1, padx=(10,0))

        # Output
        ctk.CTkLabel(self, text="Destino:", anchor="w").grid(row=4, column=0, sticky="ew", padx=20, pady=(15,5))
        frame_out = ctk.CTkFrame(self)
        frame_out.grid(row=5, column=0, sticky="ew", padx=20)
        frame_out.grid_columnconfigure(0, weight=1)
        self.entry_output = ctk.CTkEntry(frame_out, placeholder_text="Selecione destino (arquivo zip ou pasta)...")
        self.entry_output.grid(row=0, column=0, sticky="ew")
        ctk.CTkButton(frame_out, text="Browse", width=80, command=self.browse_output).grid(row=0, column=1, padx=(10,0))

        # Botões de ação (Executar e Iniciar)
        btn_frame = ctk.CTkFrame(self)
        btn_frame.grid(row=6, column=0, pady=(20,10), padx=20, sticky="ew")
        btn_frame.grid_columnconfigure((0,1), weight=1)
        self.btn_execute = ctk.CTkButton(btn_frame, text="Executar", command=self.start_process)
        self.btn_execute.grid(row=0, column=0, padx=(0,10), sticky="ew")
        self.btn_start = ctk.CTkButton(btn_frame, text="Iniciar", fg_color="#2ECC71", hover_color="#27AE60", command=self.start_process)
        self.btn_start.grid(row=0, column=1, sticky="ew")

        # Spinner
        self.spinner_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=24))
        self.spinner_label.grid(row=7, column=0, pady=(0,10))
        self._running = False
        self._spinner_chars = ["⏳","🔄","💫","🔃"]
        self._spin_idx = 0

        # Log
        self.logbox = ctk.CTkTextbox(self, state="disabled", wrap="word")
        self.logbox.grid(row=8, column=0, sticky="nsew", padx=20, pady=(0,20))

    def browse_input(self):
        mode = self.mode_combo.get()
        if mode.startswith("Compactar"):
            sel = filedialog.askdirectory(title="Selecione Pasta para Compactar")
        else:
            sel = filedialog.askopenfilename(title="Selecione Arquivo ZIP", filetypes=[("ZIP files","*.zip")])
        if sel:
            self.entry_input.delete(0, ctk.END)
            self.entry_input.insert(0, sel)

    def browse_output(self):
        mode = self.mode_combo.get()
        if mode.startswith("Compactar"):
            path = filedialog.asksaveasfilename(defaultextension=".zip", filetypes=[("ZIP files","*.zip")], title="Salvar arquivo ZIP como")
            if path:
                self.entry_output.delete(0, ctk.END)
                self.entry_output.insert(0, path)
        else:
            folder = filedialog.askdirectory(title="Selecione pasta de destino para extrair")
            if folder:
                self.entry_output.delete(0, ctk.END)
                self.entry_output.insert(0, folder)

    def log(self, msg):
        self.logbox.configure(state="normal")
        self.logbox.insert(ctk.END, msg + "\n")
        self.logbox.see(ctk.END)
        self.logbox.configure(state="disabled")

    def animate(self):
        if not self._running:
            self.spinner_label.configure(text="")
            return
        self.spinner_label.configure(text=self._spinner_chars[self._spin_idx % len(self._spinner_chars)])
        self._spin_idx += 1
        self.after(150, self.animate)

    def start_process(self):
        inp = self.entry_input.get().strip()
        out = self.entry_output.get().strip()
        mode = self.mode_combo.get()
        if not inp or not out:
            messagebox.showwarning("Dados incompletos", "Preencha entrada e destino!")
            return
        # Desabilita botões
        self.btn_execute.configure(state="disabled")
        self.btn_start.configure(state="disabled")
        self.logbox.configure(state="normal"); self.logbox.delete('0.0', ctk.END); self.logbox.configure(state="disabled")
        self._running = True
        self.animate()
        threading.Thread(target=self._process_thread, args=(mode, inp, out), daemon=True).start()

    def _process_thread(self, mode, inp, out):
        try:
            if mode.startswith("Compactar"):
                self.log(f"Compactando '{inp}' em '{out}'...")
                with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as zf:
                    for root, dirs, files in os.walk(inp):
                        for file in files:
                            abs_path = os.path.join(root, file)
                            rel_path = os.path.relpath(abs_path, inp)
                            zf.write(abs_path, rel_path)
                self.log("Compactação concluída!")
            else:
                self.log(f"Descompactando '{inp}' em '{out}'...")
                with zipfile.ZipFile(inp, 'r') as zf:
                    zf.extractall(out)
                self.log("Descompactação concluída!")
        except Exception as e:
            self.log(f"❌ Erro: {e}")
        finally:
            self._running = False
            self.btn_execute.configure(state="normal")
            self.btn_start.configure(state="normal")

if __name__ == '__main__':
    app = ZipUnzipApp()
    app.mainloop()