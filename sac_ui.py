import tkinter as tk
from tkinter import filedialog
import shutil
import os

class PDFApp:
    def __init__(self, master):
        self.master = master
        master.title("PDF App")

        # Button to open file dialog
        self.select_button = tk.Button(master, text="Select PDF", command=self.select_pdf)
        self.select_button.pack()

    def select_pdf(self):
        # Show file dialog to select PDF file
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        
        if file_path:
            # Copy PDF file to specified location
            destination = "C:/pdf_files/"  # Replace with desired destination path
            shutil.copy2(file_path, destination)
            
            # Display success message
            message = "File copied to " + destination
            self.success_label = tk.Label(self.master, text=message)
            self.success_label.pack()

root = tk.Tk()
pdf_app = PDFApp(root)
root.mainloop()