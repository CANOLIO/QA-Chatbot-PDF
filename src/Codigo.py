import os
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
import pdfplumber
import google.generativeai as genai
from typing import Dict, Optional

class PDFChatbotApp:
    # Diccionario de traducciones como atributo de clase
    translations = {
        "español": {
            "title": "QA Chatbot con Gemini",
            "api_key": "API Key de Gemini:",
            "select_pdf": "Selecciona un archivo PDF:",
            "browse": "Buscar...",
            "question": "Pregunta:",
            "search": "Buscar respuesta",
            "response": "Respuesta:",
            "theme": "Modo oscuro",
            "language": "Idioma:"
        },
        "english": {
            "title": "QA Chatbot with Gemini",
            "api_key": "Gemini API Key:",
            "select_pdf": "Select a PDF file:",
            "browse": "Browse...",
            "question": "Question:",
            "search": "Search Answer",
            "response": "Response:",
            "theme": "Dark Mode",
            "language": "Language:"
        }
    }

    def __init__(self):
        # Configuración inicial
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        
        # Inicializar la aplicación
        self.app = ctk.CTk()
        self.app.geometry("750x650")
        self.app.wm_title("QA-Chatbot-PDF")
        
        # Variables de estado
        self.current_language = tk.StringVar(value="español")
        
        # Inicializar la interfaz
        self._init_ui()
        
    def _init_ui(self):
        """Inicializa todos los componentes de la interfaz de usuario."""
        self._create_top_controls()
        self._create_api_key_section()
        self._create_pdf_section()
        self._create_query_section()
        self._create_result_section()
        
    def _create_top_controls(self):
        """Crea los controles superiores (idioma y tema)."""
        frame = ctk.CTkFrame(self.app)
        frame.pack(pady=10, fill="x", padx=15)
        
        # Selector de idioma
        lang_label = ctk.CTkLabel(frame, text=self._get_translation("language"))
        lang_label.pack(side="left", padx=(0, 5))
        
        lang_selector = ctk.CTkOptionMenu(
            frame, 
            values=["español", "english"],
            variable=self.current_language,
            command=self._update_language
        )
        lang_selector.pack(side="left")
        
        # Switch de tema
        self.theme_switch = ctk.CTkSwitch(
            frame, 
            text=self._get_translation("theme"),
            command=self._toggle_theme
        )
        self.theme_switch.pack(side="right", padx=(5, 0))
        
    def _create_api_key_section(self):
        """Crea la sección para ingresar la API key."""
        self.api_key_label = ctk.CTkLabel(self.app, text=self._get_translation("api_key"))
        self.api_key_label.pack(pady=(15, 5))
        
        self.api_key_entry = ctk.CTkEntry(self.app, width=500)
        self.api_key_entry.pack()
        
    def _create_pdf_section(self):
        """Crea la sección para seleccionar el PDF."""
        self.pdf_label = ctk.CTkLabel(self.app, text=self._get_translation("select_pdf"))
        self.pdf_label.pack(pady=(15, 5))
        
        pdf_frame = ctk.CTkFrame(self.app)
        pdf_frame.pack(pady=5)
        
        self.pdf_entry = ctk.CTkEntry(pdf_frame, width=400, state="disabled")
        self.pdf_entry.pack(side="left", padx=(0, 10))
        
        self.browse_button = ctk.CTkButton(
            pdf_frame, 
            text=self._get_translation("browse"),
            command=lambda: self._browse_pdf()
        )
        self.browse_button.pack(side="right")
        
    def _create_query_section(self):
        """Crea la sección para ingresar la pregunta."""
        self.query_label = ctk.CTkLabel(self.app, text=self._get_translation("question"))
        self.query_label.pack(pady=(15, 5))
        
        self.query_entry = ctk.CTkEntry(self.app, width=500)
        self.query_entry.pack()
        
        self.search_button = ctk.CTkButton(
            self.app, 
            text=self._get_translation("search"),
            command=self._search
        )
        self.search_button.pack(pady=20)
        
    def _create_result_section(self):
        """Crea la sección para mostrar los resultados."""
        self.result_label = ctk.CTkLabel(self.app, text=self._get_translation("response"))
        self.result_label.pack(pady=(10, 5))
        
        self.result_text = ctk.CTkTextbox(
            self.app, 
            height=250, 
            width=700, 
            font=("Segoe UI", 12), 
            wrap="word"
        )
        self.result_text.pack(padx=10, pady=(0, 20))
        
    def _get_translation(self, key: str) -> str:
        """Obtiene la traducción para una clave específica."""
        lang = self.current_language.get()
        return self.translations[lang][key]
        
    def _update_language(self, _):
        """Actualiza el idioma de la interfaz."""
        lang = self.current_language.get()
        self.api_key_label.configure(text=self._get_translation("api_key"))
        self.pdf_label.configure(text=self._get_translation("select_pdf"))
        self.browse_button.configure(text=self._get_translation("browse"))
        self.query_label.configure(text=self._get_translation("question"))
        self.search_button.configure(text=self._get_translation("search"))
        self.result_label.configure(text=self._get_translation("response"))
        self.theme_switch.configure(text=self._get_translation("theme"))
        
    def _toggle_theme(self):
        """Alterna entre modo claro y oscuro."""
        current = ctk.get_appearance_mode()
        new_theme = "Light" if current == "Dark" else "Dark"
        ctk.set_appearance_mode(new_theme)
        
    def _configure_gemini(self, api_key: Optional[str] = None) -> genai.GenerativeModel:
        """Configura el modelo de Gemini."""
        if not api_key:
            api_key = os.environ.get("GEMINI_API_KEY")
        genai.configure(api_key=api_key)
        return genai.GenerativeModel('gemini-1.5-pro')
        
    def _load_pdf(self, file_path: str) -> str:
        """Carga y extrae el texto de un archivo PDF."""
        raw_text = ''
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        raw_text += text
            return raw_text
        except Exception as e:
            raise Exception(f"Error al cargar el PDF: {str(e)}")
            
    def _browse_pdf(self):
        """Abre el diálogo para seleccionar un archivo PDF."""
        filename = filedialog.askopenfilename(
            title=self._get_translation("select_pdf"),
            filetypes=[("PDF files", "*.pdf")]
        )
        if filename:
            self.pdf_entry.configure(state='normal')
            self.pdf_entry.delete(0, tk.END)
            self.pdf_entry.insert(0, filename)
            self.pdf_entry.configure(state='readonly')
            
    def _search(self):
        """Realiza la búsqueda y muestra los resultados."""
        file_path = self.pdf_entry.get()
        query = self.query_entry.get()
        api_key = self.api_key_entry.get()

        if not file_path or not query:
            self._show_error("Por favor selecciona un PDF y escribe una pregunta.")
            return

        try:
            model = self._configure_gemini(api_key)
            context_text = self._load_pdf(file_path)

            prompt = f"""
            Actúa como un experto en comprensión lectora de documentos. 
            A continuación, se muestra el texto del documento:
            -----
            {context_text}
            -----
            Basado solamente en ese contenido, responde la siguiente pregunta de forma clara, detallada y en el idioma original de la pregunta: 
            '{query}'
            """

            response = model.generate_content(prompt)
            self._display_response(response.text)

        except Exception as e:
            self._show_error(f"Error: {str(e)}")
            
    def _display_response(self, response_text: str):
        """Muestra la respuesta formateada en el widget de texto."""
        self.result_text.delete('1.0', tk.END)
        text_widget = self.result_text._textbox
        bold_tag = "bold"
        text_widget.tag_configure(bold_tag, font=("Segoe UI", 12, "bold"))

        parts = response_text.split("**")
        for i, part in enumerate(parts):
            if i % 2 == 0:
                text_widget.insert(tk.END, part)
            else:
                start_index = text_widget.index(tk.END)
                text_widget.insert(tk.END, part)
                end_index = text_widget.index(tk.END)
                text_widget.tag_add(bold_tag, start_index, end_index)
                
    def _show_error(self, message: str):
        """Muestra un mensaje de error en el widget de texto."""
        self.result_text.delete('1.0', tk.END)
        self.result_text.insert(tk.END, message)
        
    def run(self):
        """Inicia la aplicación."""
        self._update_language(None)
        self.app.mainloop()

if __name__ == "__main__":
    app = PDFChatbotApp()
    app.run() 