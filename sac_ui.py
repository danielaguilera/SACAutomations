from tkinter import *
from tkinter import messagebox
import shutil
import os
from tkinter import filedialog
from Utils.Metadata import *
from Utils.GlobalFunctions import *
from PyPDF2 import PdfReader, PdfMerger
import re

class SACUI:
    def __init__(self, master: Tk):
        self.master = master
        self.master.title("PDF App")
        
        self.uploadFrame = LabelFrame(master=self.master, text='Upload frame')
        self.uploadFrame.pack(expand=True, fill=BOTH)

        self.boletaUploadButton = Button(self.uploadFrame, text="Subir boleta SII", width=20, height=1, font=('Helvetica bold', 26), command=self.selectBoletaPDF)
        self.boletaUploadButton.grid(row=0, column=0, sticky=NSEW, padx=5, pady=5)
        
        self.anexoUploadButton = Button(self.uploadFrame, text="Subir anexo", width=20, height=1, font=('Helvetica bold', 26), command=self.selectAnexoPDF)
        self.anexoUploadButton.grid(row=0, column=1, sticky=NSEW, padx=5, pady=5)
        
        self.stateFrame = LabelFrame(master=self.master, text="State Frame")
        self.stateFrame.pack(expand=True, fill=BOTH)
        
        self.numBoletaLabel = Label(master=self.stateFrame, text='# Boleta', font=('Helvetica bold', 15))
        self.numBoletaLabel.grid(row=0, column=0, sticky=W, padx=5, pady=5)
        
        self.numBoletaEntry = Entry(master=self.stateFrame, font=('Helvetica bold', 15))
        self.numBoletaEntry.grid(row=0, column=1, sticky=W, padx=5, pady=5)
        
        self.uploadedBoletaLabel = Label(master=self.stateFrame, font=('Helvetica bold', 15), text='')
        self.uploadedBoletaLabel.grid(row=1, column=0, sticky=W, padx=5, pady=5)
        self.uploadedBoletaLabel.grid_remove()
        
        self.uploadedAnexosLabel = Label(master=self.stateFrame, font=('Helvetica bold', 15), text='')
        self.uploadedAnexosLabel.grid(row=2, column=0, sticky=W, padx=5, pady=5)
        
        self.boletaPath: str = ''
        self.anexosPaths: list[str] = []
        
        self.saveFrame = LabelFrame(master=self.master, text='Save frame')
        self.saveFrame.pack(expand=True, fill=BOTH)
        
        self.saveButton = Button(self.saveFrame, text='Guardar', width=40, height=1, font=('Helvetica bold', 20), command=self.saveChanges)
        self.saveButton.pack(expand=True, fill=BOTH)
                
    def saveChanges(self):
        if not self.boletaPath:
            messagebox.showerror(title='Error', message='Falta agregar la boleta del SII')
            return   
        if not self.numBoletaEntry.get().isdigit():
            messagebox.showerror(title='Error', message='El número de boleta debe ser un número entero')
            return 
        numBoleta: int = int(self.numBoletaEntry.get())
        if not os.path.exists(DELIVEREDDATAPATH):
            os.makedirs(DELIVEREDDATAPATH)
        if not os.path.exists(f'{DELIVEREDDATAPATH}/{numBoleta}'):
            os.makedirs(f'{DELIVEREDDATAPATH}/{numBoleta}')
        merger: PdfMerger = PdfMerger()
        for root in self.anexosPaths:
            print(root)
            merger.append(root)
        merger.write(f'{DELIVEREDDATAPATH}/{numBoleta}/Anexo_{numBoleta}.pdf')
        merger.close()
        shutil.copy(self.boletaPath, f'{DELIVEREDDATAPATH}/{numBoleta}/Boleta_{numBoleta}.pdf')
        messagebox.showinfo(title='Mensaje', message=f'Archivos guardados para boleta n°{numBoleta}')

    def selectBoletaPDF(self):
        filePath = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if filePath:
            try:
                reader = PdfReader(filePath)
                index = reader.pages[0].extract_text().find('°')
                if index == -1:
                    index = reader.pages[0].extract_text().find('º')
                print(index)
                substring = reader.pages[0].extract_text()[index::]
                end_index = substring.find('\n')
                # numBoleta = re.search('°(.+?)\n', reader.pages[0].extract_text()).group(1).strip()
                numBoleta = extractNumberFromText(reader.pages[0].extract_text()[index: end_index + 1])
                print(numBoleta)
                if numBoleta.isdigit():
                    self.numBoletaEntry.insert(0, numBoleta)
                    messagebox.showinfo(title='Mensaje', message='Boleta subida correctamente')
                else:
                    messagebox.showerror(title='Error', message='No se pudo encontrar el número de boleta en el documento. \nPor favor, ingréselo manualmente.')
                self.boletaPath = filePath
                self.uploadedBoletaLabel.config(text=f'Boleta SII subida: {self.boletaPath}')
                self.uploadedBoletaLabel.grid()
            except Exception:
                messagebox.showerror(title='Error', message='El archivo subido no es una boleta del SII')
        else:
            messagebox.showerror(title='Error', message='Archivo no encontrado')
                
    def selectAnexoPDF(self):
        filePath = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if filePath:
            try:
                reader = PdfReader(filePath)
            except Exception:
                messagebox.showerror(title='Error', message='El archivo no es de tipo PDF')
            finally:
                self.anexosPaths.append(filePath)
                messagebox.showinfo(title='Mensaje', message='Anexo agregado correctamente')
                self.uploadedAnexosLabel.config(text='Anexos subidos: \n' + '\n'.join(self.anexosPaths))
        else:
            messagebox.showerror(title='Error', message='Archivo no encontrado')

root = Tk()
pdf_app = SACUI(root)
root.mainloop()