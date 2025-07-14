# converter_app.py
# pip install pandas openpyxl xlwt python-docx docx2pdf pdf2docx

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import pandas as pd
import xlwt
from docx import Document
from docx2pdf import convert as docx2pdf_convert
from pdf2docx import Converter as PDF2DOCXConverter

class SplashScreen:
    def __init__(self, parent):
        self.root = tk.Toplevel(parent)
        self.root.overrideredirect(True)
        # centraliza a janela
        w, h = 400, 200
        sw = parent.winfo_screenwidth()
        sh = parent.winfo_screenheight()
        x = int((sw - w) / 2)
        y = int((sh - h) / 2)
        self.root.geometry(f"{w}x{h}+{x}+{y}")
        lbl = tk.Label(self.root, text="BANG TOP CONVERTER", font=("Helvetica", 24, "bold"))
        lbl.pack(expand=True)
        self.spinner_label = tk.Label(self.root, text="", font=("Helvetica", 14))
        self.spinner_label.pack()
        self.chars = ["|", "/", "-", "\\"]
        self.idx = 0
        self.running = True
        self.animate()
        # fecha após 2.5s
        self.root.after(2500, self.close)

    def animate(self):
        if not self.running:
            return
        self.spinner_label.config(text=self.chars[self.idx % len(self.chars)])
        self.idx += 1
        self.root.after(100, self.animate)

    def close(self):
        self.running = False
        self.root.destroy()

class ConverterApp:
    def __init__(self, root):
        self.root = root
        root.title("Bang Top Converter")
        root.geometry("500x300")
        style = ttk.Style()
        style.theme_use("clam")
        frm = ttk.Frame(root, padding=20)
        frm.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frm, text="Escolha a conversão:", font=("Arial", 12)).pack(anchor=tk.W)
        self.opt = ttk.Combobox(frm, values=[
            "CSV → XLSX",
            "CSV → DOCX",
            "DOCX → PDF",
            "XLSX → XLS",
            "XLS → XLSX",
            "PDF → DOCX"
        ], state="readonly")
        self.opt.current(0)
        self.opt.pack(fill=tk.X, pady=5)

        ttk.Button(frm, text="Selecionar arquivo", command=self.select_input).pack(fill=tk.X, pady=2)
        ttk.Button(frm, text="Selecionar destino", command=self.select_output).pack(fill=tk.X, pady=2)

        self.input_path = ""
        self.output_path = ""

        self.btn = ttk.Button(frm, text="Converter", command=self.start)
        self.btn.pack(fill=tk.X, pady=10)

        self.spinner = ttk.Label(frm, text="", font=("Arial", 14))
        self.chars = ["🔄", "⏳", "💫", "🔃"]
        self.idx = 0

    def select_input(self):
        path = filedialog.askopenfilename()
        if path:
            self.input_path = path

    def select_output(self):
        ext = self.get_ext()
        path = filedialog.asksaveasfilename(defaultextension=ext, filetypes=[("*"+ext, "*"+ext)])
        if path:
            self.output_path = path

    def get_ext(self):
        return {
            "CSV → XLSX": ".xlsx",
            "CSV → DOCX": ".docx",
            "DOCX → PDF": ".pdf",
            "XLSX → XLS": ".xls",
            "XLS → XLSX": ".xlsx",
            "PDF → DOCX": ".docx"
        }[self.opt.get()]

    def start(self):
        if not self.input_path or not self.output_path:
            messagebox.showwarning("Ops", "Selecione input e output antes!")
            return
        self.btn.config(state=tk.DISABLED)
        self.spinner.pack()
        threading.Thread(target=self.run).start()
        self.animate()

    def animate(self):
        if self.btn['state'] == tk.NORMAL:
            self.spinner.config(text="")
            return
        self.spinner.config(text=self.chars[self.idx % len(self.chars)])
        self.idx += 1
        self.root.after(150, self.animate)

    def run(self):
        try:
            fn = self.opt.get()
            mapper = {
                "CSV → XLSX": self.csv_to_xlsx,
                "CSV → DOCX": self.csv_to_docx,
                "DOCX → PDF": self.docx_to_pdf,
                "XLSX → XLS": self.xlsx_to_xls,
                "XLS → XLSX": self.xls_to_xlsx,
                "PDF → DOCX": self.pdf_to_docx
            }
            mapper[fn]()
            messagebox.showinfo("Sucesso", "Convertido com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", str(e))
        finally:
            self.btn.config(state=tk.NORMAL)

    def csv_to_xlsx(self):
        df = pd.read_csv(self.input_path)
        df.to_excel(self.output_path, index=False)

    def csv_to_docx(self):
        df = pd.read_csv(self.input_path)
        doc = Document()
        tbl = doc.add_table(rows=1, cols=len(df.columns))
        for i, col in enumerate(df.columns): tbl.cell(0, i).text = col
        for row in df.values:
            cells = tbl.add_row().cells
            for i, val in enumerate(row): cells[i].text = str(val)
        doc.save(self.output_path)

    def docx_to_pdf(self):
        docx2pdf_convert(self.input_path, self.output_path)

    def xlsx_to_xls(self):
        df = pd.read_excel(self.input_path)
        wb = xlwt.Workbook()
        ws = wb.add_sheet('Sheet1')
        for i, row in enumerate(df.values):
            for j, val in enumerate(row): ws.write(i, j, val)
        wb.save(self.output_path)

    def xls_to_xlsx(self):
        df = pd.read_excel(self.input_path)
        df.to_excel(self.output_path, index=False)

    def pdf_to_docx(self):
        cv = PDF2DOCXConverter(self.input_path)
        cv.convert(self.output_path)
        cv.close()

if __name__ == '__main__':
    root = tk.Tk()
    SplashScreen(root)
    # inicia app após splash
    root.after(2600, lambda: ConverterApp(root))
    root.mainloop()
