#!/usr/bin/env python3
"""
GUI para conversão de arquivos via Convertio API
"""
import os
import threading
import time
import requests
import customtkinter as ctk
from tkinter import filedialog, messagebox

API_BASE = "https://api.convertio.co"

class ConvertioGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Convertio Converter GUI")
        self.geometry("600x500")
        self.resizable(True, True)
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("dark-blue")

        # Frame principal
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(6, weight=1)

        row = 0
        # API Key
        ctk.CTkLabel(self, text="API Key:", anchor="w").grid(row=row, column=0, sticky="ew", padx=20, pady=(20,5))
        self.entry_api = ctk.CTkEntry(self, placeholder_text="Sua API Key Convertio")
        self.entry_api.grid(row=row+1, column=0, sticky="ew", padx=20)
        row += 2

        # Input file
        ctk.CTkLabel(self, text="Arquivo de entrada:", anchor="w").grid(row=row, column=0, sticky="ew", padx=20, pady=(10,5))
        frame_in = ctk.CTkFrame(self)
        frame_in.grid(row=row+1, column=0, sticky="ew", padx=20)
        frame_in.grid_columnconfigure(0, weight=1)
        self.entry_input = ctk.CTkEntry(frame_in, placeholder_text="Selecione um arquivo...")
        self.entry_input.grid(row=0, column=0, sticky="ew")
        ctk.CTkButton(frame_in, text="Browse", width=80, command=self.browse_input).grid(row=0, column=1, padx=(10,0))
        row += 2

        # Output format
        ctk.CTkLabel(self, text="Formato de saída:", anchor="w").grid(row=row, column=0, sticky="ew", padx=20, pady=(10,5))
        self.combo_format = ctk.CTkComboBox(self, values=["pdf","docx","xlsx","jpg","png","txt","rtf","csv"], state="readonly")
        self.combo_format.set("pdf")
        self.combo_format.grid(row=row+1, column=0, sticky="ew", padx=20)
        row += 2

        # OCR options
        self.var_ocr = ctk.BooleanVar(value=False)
        chk = ctk.CTkCheckBox(self, text="Ativar OCR", variable=self.var_ocr, command=self.toggle_ocr)
        chk.grid(row=row, column=0, sticky="w", padx=20, pady=(10,5))
        row += 1

        self.frame_ocr = ctk.CTkFrame(self)
        self.frame_ocr.grid(row=row, column=0, sticky="ew", padx=40, pady=(0,5))
        self.frame_ocr.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(self.frame_ocr, text="Langs:").grid(row=0, column=0, sticky="w")
        self.entry_langs = ctk.CTkEntry(self.frame_ocr, placeholder_text="eng,bra")
        self.entry_langs.grid(row=0, column=1, sticky="ew", padx=(5,0))
        ctk.CTkLabel(self.frame_ocr, text="Páginas:").grid(row=1, column=0, sticky="w", pady=(5,0))
        self.entry_pages = ctk.CTkEntry(self.frame_ocr, placeholder_text="1-3,5")
        self.entry_pages.grid(row=1, column=1, sticky="ew", padx=(5,0), pady=(5,0))
        self.frame_ocr.grid_remove()
        row += 1

        # Botão converter
        self.btn_convert = ctk.CTkButton(self, text="Converter", command=self.start_conversion)
        self.btn_convert.grid(row=row, column=0, pady=(15,5), padx=20)
        row += 1

        # Spinner
        self.lbl_spinner = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=20))
        self.lbl_spinner.grid(row=row, column=0, pady=(5,10))
        row += 1

        # Log
        self.logbox = ctk.CTkTextbox(self, state="disabled", wrap="word")
        self.logbox.grid(row=row, column=0, sticky="nsew", padx=20, pady=(0,20))

        self.spinner_chars = ["⏳","🔄","💫","🔃"]
        self.spin_idx = 0
        self._running = False

    def toggle_ocr(self):
        if self.var_ocr.get(): self.frame_ocr.grid()
        else: self.frame_ocr.grid_remove()

    def browse_input(self):
        p = filedialog.askopenfilename()
        if p: self.entry_input.delete(0, ctk.END); self.entry_input.insert(0, p)

    def log(self, msg):
        self.logbox.configure(state="normal")
        self.logbox.insert(ctk.END, msg + "\n")
        self.logbox.see(ctk.END)
        self.logbox.configure(state="disabled")

    def animate(self):
        if not self._running: return
        self.lbl_spinner.configure(text=self.spinner_chars[self.spin_idx % len(self.spinner_chars)])
        self.spin_idx += 1
        self.after(150, self.animate)

    def start_conversion(self):
        apikey = self.entry_api.get().strip()
        infile = self.entry_input.get().strip()
        outfmt = self.combo_format.get()
        if not apikey or not infile or not outfmt:
            messagebox.showwarning("Faltando dados", "Preencha API Key, input e formato!")
            return
        if not os.path.isfile(infile):
            messagebox.showerror("Erro", "Arquivo de entrada não encontrado.")
            return
        self.btn_convert.configure(state="disabled")
        self.logbox.configure(state="normal"); self.logbox.delete('0.0', ctk.END); self.logbox.configure(state="disabled")
        self._running = True
        self.animate()
        threading.Thread(target=self._convert_thread, args=(apikey, infile, outfmt), daemon=True).start()

    def _convert_thread(self, apikey, infile, outfmt):
        try:
            # iniciar
            self.log("Iniciando conversão...")
            data = {"apikey":apikey, "input":"upload","outputformat":outfmt}
            if self.var_ocr.get():
                opts={"ocr_enabled":True, "ocr_settings":{}}
                langs=self.entry_langs.get().strip()
                pages=self.entry_pages.get().strip()
                if langs: opts['ocr_settings']['langs']=langs.split(',')
                if pages: opts['ocr_settings']['page_nums']=pages
                data['options']=opts
            r = requests.post(f"{API_BASE}/convert", json=data)
            r.raise_for_status(); js=r.json()
            cid = js['data']['id'] if js.get('status')=='ok' else (_ for _ in ()).throw(Exception(js.get('error')))
            self.log(f"Conversion ID: {cid}")
            # upload
            fname=os.path.basename(infile)
            with open(infile,'rb') as f:
                up=requests.put(f"{API_BASE}/convert/{cid}/{fname}", data=f)
            up.raise_for_status(); self.log("Arquivo enviado...")
            # polling
            while True:
                s=requests.get(f"{API_BASE}/convert/{cid}/status", params={"apikey":apikey})
                s.raise_for_status(); st=s.json()['data']
                step=st['step']; pct=st.get('step_percent',0)
                self.log(f"[{step}] {pct}%")
                if step=='finish': break
                if step=='failed': raise Exception("Conversão falhou.")
                time.sleep(1)
            # download via URL
            url=st['output']['url']
            outpath=os.path.splitext(infile)[0]+f"_conv.{outfmt}"
            self.log(f"Baixando para {outpath}...")
            dl=requests.get(url, stream=True); dl.raise_for_status()
            with open(outpath,'wb') as f:
                for chunk in dl.iter_content(8192): f.write(chunk)
            self.log("Concluído com sucesso!")
        except Exception as e:
            self.log(f"❌ Erro: {e}")
        finally:
            self._running=False
            self.btn_convert.configure(state="normal")
            self.lbl_spinner.configure(text="")

if __name__ == '__main__':
    app = ConvertioGUI()
    app.mainloop()
