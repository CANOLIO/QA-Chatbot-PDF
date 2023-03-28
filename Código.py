# import the modules
import os
import tkinter as tk
from tkinter import filedialog
from PyPDF2 import PdfReader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
import pickle
from langchain.chat_models import ChatOpenAI


# define the functions
def browse_pdf(pdf_entry):
    filename = filedialog.askopenfilename(title="Select a PDF", filetypes=[("PDF files", "*.pdf")])
    pdf_entry.configure(state='normal')
    pdf_entry.delete(0, tk.END)
    pdf_entry.insert(0, filename)
    pdf_entry.configure(state='disabled')

def load_pdf(file_path):
    with open(file_path, 'rb') as f:
        reader = PdfReader(f)
        raw_text = ''
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                raw_text += text
        return raw_text

def search():
    # load the embeddings
    embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))

    # create the document search engine
    file_path = pdf_entry.get()
    raw_text = load_pdf(file_path)
    text_splitter = CharacterTextSplitter(        
        separator = "\n",
        chunk_size = 1000,
        chunk_overlap  = 200,
        length_function = len,
    )
    texts = text_splitter.split_text(raw_text)
    docsearch = FAISS.from_texts(texts, embeddings)

    # load the question-answering chain
    chain = load_qa_chain(OpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"), temperature=0.3), chain_type="stuff")

    # perform the search
    query = query_entry.get()
    prompt = ""
    query_with_prompt = prompt + query # se agrega el prompt al query
    docs = docsearch.similarity_search(query_with_prompt)
    result_text.delete('1.0', tk.END)
    result_text.insert(tk.END, docs[0].page_content)
    answer = chain.run(input_documents=docs, question=query_with_prompt)
    result_text.insert(tk.END, answer)

# create the GUI window
window = tk.Tk()
window.title("Question Answering Bot")
window.geometry("600x400")

# create the widgets
pdf_label = tk.Label(window, text="Select the PDF to analyze:")
pdf_entry = tk.Entry(window, width=50, state='disabled')
pdf_button = tk.Button(window, text="Browse", command=lambda: browse_pdf(pdf_entry))
query_label = tk.Label(window, text="Enter your query:")
query_entry = tk.Entry(window, width=50)
search_button = tk.Button(window, text="Search", command=search)

result_label = tk.Label(window, text="Results:")
result_text = tk.Text(window, height=15)
# place the widgets in the window
pdf_label.pack()
pdf_entry.pack()
pdf_button.pack()
query_label.pack()
query_entry.pack()
search_button.pack()
result_label.pack()
result_text.pack()

# configure the button to call the search function
search_button.configure(command=search)

# run the main loop of the GUI
window.mainloop()
