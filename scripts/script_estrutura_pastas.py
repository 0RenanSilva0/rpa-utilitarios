import os
import tkinter as tk
from tkinter import filedialog, scrolledtext
from rich.console import Console
from rich.tree import Tree
from rich.text import Text
from rich import print as rich_print
from io import StringIO

# Console virtual pra capturar output formatado do Rich
class RichCapture:
    def __init__(self):
        self.buffer = StringIO()
        self.console = Console(file=self.buffer, force_terminal=True, width=100)

    def get_output(self):
        return self.buffer.getvalue()

def build_tree(directory: str, tree: Tree):
    try:
        entries = sorted(os.listdir(directory))
        for entry in entries:
            path = os.path.join(directory, entry)
            if os.path.isdir(path):
                subtree = tree.add(f"[bold blue][📁] {entry}")
                build_tree(path, subtree)
            else:
                size = os.path.getsize(path)
                tree.add(f"[green][📄] {entry}[/] - {size / 1024:.2f} KB")
    except PermissionError:
        tree.add("[red]Acesso negado[/]")

def browse_and_display(text_widget: scrolledtext.ScrolledText):
    folder_selected = filedialog.askdirectory(title="Selecione a pasta para escanear")

    if not folder_selected:
        text_widget.insert(tk.END, "Nenhuma pasta foi selecionada.\n")
        return

    tree = Tree(f"[bold magenta][📁 ROOT] {os.path.basename(folder_selected)}")
    build_tree(folder_selected, tree)

    # Captura e exibe o conteúdo com formatação Rich
    capture = RichCapture()
    capture.console.print(tree)
    output = capture.get_output()

    text_widget.delete("1.0", tk.END)
    text_widget.insert(tk.END, f"📂 Estrutura da pasta: {folder_selected}\n\n")
    text_widget.insert(tk.END, output)

def main():
    root = tk.Tk()
    root.title("Visualizador de Estrutura de Pastas")
    root.geometry("800x600")

    frame = tk.Frame(root)
    frame.pack(pady=10)

    btn = tk.Button(frame, text="Selecionar Pasta", command=lambda: browse_and_display(text_area), font=("Arial", 12))
    btn.pack()

    text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Courier", 10))
    text_area.pack(expand=True, fill="both", padx=10, pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
