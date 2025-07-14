#!/usr/bin/env python3
"""
Chat Notifier GUI

Envie notificações para Slack, Discord ou Telegram via Webhook/Token.

Funcionalidades:
 - Seleção de serviço (Slack/Discord/Telegram)
 - Configuração de URL/Token/Chat ID
 - Area para digitar mensagem
 - Envio com spinner e log em tempo real

Uso:
  python chat_notifier_app.py
"""
import threading
import requests
import customtkinter as ctk
from tkinter import messagebox

# Configuração de tema
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("dark-blue")

class ChatNotifierApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Chat Notifier")
        self.geometry("600x500")
        self.minsize(550, 450)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(6, weight=1)

        # Serviço
        ctk.CTkLabel(self, text="Serviço:", anchor="w").grid(row=0, column=0, sticky="ew", padx=20, pady=(20,5))
        self.combo_service = ctk.CTkComboBox(self, values=["Slack Webhook", "Discord Webhook", "Telegram Bot"], state="readonly")
        self.combo_service.set("Slack Webhook")
        self.combo_service.grid(row=1, column=0, sticky="ew", padx=20)
        self.combo_service.bind("<<ComboboxSelected>>", lambda _: self.update_fields())

        # Campo de configuração dinâmica
        self.frame_config = ctk.CTkFrame(self)
        self.frame_config.grid(row=2, column=0, sticky="ew", padx=20, pady=(10,5))
        self.frame_config.grid_columnconfigure(1, weight=1)

        # Slack & Discord: Webhook URL
        self.lbl_url = ctk.CTkLabel(self.frame_config, text="Webhook URL:")
        self.lbl_url.grid(row=0, column=0, sticky="w")
        self.entry_url = ctk.CTkEntry(self.frame_config, placeholder_text="https://.../webhook")
        self.entry_url.grid(row=0, column=1, sticky="ew", padx=(5,0))

        # Telegram: Token and Chat ID
        self.lbl_token = ctk.CTkLabel(self.frame_config, text="Bot Token:")
        self.entry_token = ctk.CTkEntry(self.frame_config, placeholder_text="123456:ABC-DEF..." )
        self.lbl_chat = ctk.CTkLabel(self.frame_config, text="Chat ID:")
        self.entry_chat = ctk.CTkEntry(self.frame_config, placeholder_text="-1001234567890")

        # Mensagem
        ctk.CTkLabel(self, text="Mensagem:", anchor="w").grid(row=3, column=0, sticky="ew", padx=20, pady=(10,5))
        self.text_msg = ctk.CTkTextbox(self, height=100, wrap="word")
        self.text_msg.grid(row=4, column=0, sticky="nsew", padx=20)

        # Botão enviar
        self.btn_send = ctk.CTkButton(self, text="Enviar Notificação", command=self.start_send)
        self.btn_send.grid(row=5, column=0, pady=(15,5), padx=20, sticky="ew")

        # Spinner e log
        self.spinner = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=20))
        self.spinner.grid(row=6, column=0, pady=(5,10))
        self.logbox = ctk.CTkTextbox(self, state="disabled", wrap="word")
        self.logbox.grid(row=7, column=0, sticky="nsew", padx=20, pady=(0,20))
        self.grid_rowconfigure(7, weight=1)

        self._running = False
        self._spinner_chars = ["⏳","🔄","💫","🔃"]
        self._spin_idx = 0

        self.update_fields()

    def update_fields(self):
        service = self.combo_service.get()
        # limpando frame
        for widget in self.frame_config.winfo_children():
            widget.grid_forget()
        if service in ["Slack Webhook", "Discord Webhook"]:
            self.lbl_url.grid(row=0, column=0, sticky="w")
            self.entry_url.grid(row=0, column=1, sticky="ew", padx=(5,0))
        else:  # Telegram
            self.lbl_token.grid(row=0, column=0, sticky="w")
            self.entry_token.grid(row=0, column=1, sticky="ew", padx=(5,0))
            self.lbl_chat.grid(row=1, column=0, sticky="w", pady=(5,0))
            self.entry_chat.grid(row=1, column=1, sticky="ew", padx=(5,0), pady=(5,0))

    def log(self, msg):
        self.logbox.configure(state="normal")
        self.logbox.insert(ctk.END, msg + "\n")
        self.logbox.see(ctk.END)
        self.logbox.configure(state="disabled")

    def animate(self):
        if not self._running:
            self.spinner.configure(text="")
            return
        self.spinner.configure(text=self._spinner_chars[self._spin_idx % len(self._spinner_chars)])
        self._spin_idx += 1
        self.after(150, self.animate)

    def start_send(self):
        msg = self.text_msg.get('0.0', ctk.END).strip()
        if not msg:
            messagebox.showwarning("Vazio", "Digite uma mensagem para enviar.")
            return
        service = self.combo_service.get()
        if service in ["Slack Webhook","Discord Webhook"]:
            url = self.entry_url.get().strip()
            if not url:
                messagebox.showwarning("Faltando URL", "Informe o Webhook URL.")
                return
            cfg = {'service': service, 'url': url, 'message': msg}
        else:
            token = self.entry_token.get().strip()
            chat_id = self.entry_chat.get().strip()
            if not token or not chat_id:
                messagebox.showwarning("Faltando dados", "Informe Token e Chat ID.")
                return
            cfg = {'service': service, 'token': token, 'chat_id': chat_id, 'message': msg}

        self.btn_send.configure(state="disabled")
        self.logbox.configure(state="normal"); self.logbox.delete('0.0', ctk.END); self.logbox.configure(state="disabled")
        self._running = True; self.animate()
        threading.Thread(target=self._send_thread, args=(cfg,), daemon=True).start()

    def _send_thread(self, cfg):
        try:
            svc = cfg['service']
            self.log(f"Enviando para {svc}...")
            if svc in ["Slack Webhook","Discord Webhook"]:
                payload = {'text': cfg['message']} if svc=='Slack Webhook' else {'content': cfg['message']}
                r = requests.post(cfg['url'], json=payload)
            else:
                # Telegram
                url = f"https://api.telegram.org/bot{cfg['token']}/sendMessage"
                payload = {'chat_id': cfg['chat_id'], 'text': cfg['message']}
                r = requests.post(url, data=payload)
            r.raise_for_status()
            self.log("Mensagem enviada com sucesso!")
        except Exception as e:
            self.log(f"❌ Erro: {e}")
        finally:
            self._running = False
            self.btn_send.configure(state="normal")

if __name__ == '__main__':
    app = ChatNotifierApp()
    app.mainloop()
