import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import PyPDF2

class Application(tk.Frame):
    def __init__(self, master: tk.Tk = None):
        super().__init__(master)
        self.master = master
        self.master.title("PDF File Menu")
        self.master.geometry("300x200")

        # Create a label for the file list
        self.label = tk.Label(self.master, text="Drop PDF files here")
        self.label.pack(fill=tk.BOTH, expand=True)

        # Allow the label to accept drops
        self.label.bind("<Button-1>", self.browse_file)
        self.label.bind("<B1-Motion>", self.drag)
        self.label.bind("<ButtonRelease-1>", self.drop)
        
        # Initialize the file list
        self.files = []

    def browse_file(self, event=None):
        # Open a file dialog to browse for PDF files
        filetypes = [('PDF files', '*.pdf')]
        filenames = filedialog.askopenfilenames(filetypes=filetypes)

        # Add the selected files to the file list
        for filename in filenames:
            self.files.append(filename)

        # Update the label with the current file list
        self.update_label()

    def drag(self, event=None):
        # Highlight the label during a drag
        self.label.config(bg="#D9D9D9")

    def drop(self, event=None):
        # Unhighlight the label after a drop
        self.label.config(bg="white")
        print('Dropped')

    def update_label(self):
        # Update the label with the current file list
        text = "PDF files:\n"
        for filename in self.files:
            text += "- " + filename + "\n"
        self.label.config(text=text)

root = tk.Tk()
app = Application(master=root)
app.mainloop()
    