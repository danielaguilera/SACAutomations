from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import shutil
import os
from tkinter import filedialog
from Utils.Metadata import *
from Utils.GlobalFunctions import *
from PyPDF2 import PdfReader, PdfMerger
from PyPDF2.errors import PdfReadError
from Clases.SACConnector import SACConnector
from Clases.Cliente import Cliente
import re

class SACUI:
    def __init__(self, master: Tk):
        
        self.sacConnector: SACConnector = SACConnector()
        self.clientes: list[Cliente] = self.sacConnector.getAllClientes()
        
        self.master = master
        self.master.title("SAC App")
        
        self.uploadFrame = LabelFrame(master=self.master)
        self.uploadFrame.pack(expand=True, fill=BOTH)

        self.boletaUploadButton = Button(self.uploadFrame, text="Subir boleta SII", width=20, height=1, font=('Helvetica bold', 26), command=self.selectBoletaPDF)
        self.boletaUploadButton.grid(row=0, column=0, sticky=NSEW, padx=5, pady=5)
        
        self.boletaResetButton = Button(self.uploadFrame, text="Reestablecer boleta", width=20, height=1, font=('Helvetica bold', 15), command=self.resetBoleta)
        self.boletaResetButton.grid(row=1, column=0, sticky=NSEW, padx=5, pady=5)
        
        self.anexoUploadButton = Button(self.uploadFrame, text="Subir anexo", width=20, height=1, font=('Helvetica bold', 26), command=self.selectAnexoPDF)
        self.anexoUploadButton.grid(row=0, column=1, sticky=NSEW, padx=5, pady=5)

        self.anexoResetButton = Button(self.uploadFrame, text="Reestablecer anexos", width=20, height=1, font=('Helvetica bold', 15), command=self.resetAnexos)
        self.anexoResetButton.grid(row=1, column=1, sticky=NSEW, padx=5, pady=5)


        
        self.stateFrame = LabelFrame(master=self.master)
        self.stateFrame.pack(expand=True, fill=BOTH)
        
        self.numBoletaFrame = Frame(master=self.stateFrame)
        self.numBoletaFrame.pack(expand=True, fill=BOTH)
        self.numBoletaLabel = Label(master=self.numBoletaFrame, text='N° Boleta')
        self.numBoletaLabel.pack(side=LEFT)
        self.numBoletaEntry = Entry(master=self.numBoletaFrame)
        self.numBoletaEntry.pack(side=LEFT, padx=5)
        
        self.fechaBoletaFrame = Frame(master=self.stateFrame)
        self.fechaBoletaFrame.pack(expand=True, fill=BOTH)
        self.fechaBoletaLabel = Label(master=self.fechaBoletaFrame, text='Fecha (dd-mm-AAAA)')
        self.fechaBoletaLabel.pack(side=LEFT) 
        self.fechaBoletaEntry = Entry(master=self.fechaBoletaFrame)
        self.fechaBoletaEntry.pack(side=LEFT, padx=5)
        
        self.rutBeneficiarioFrame = Frame(master=self.stateFrame)
        self.rutBeneficiarioFrame.pack(expand=True, fill=BOTH)
        self.rutBeneficiarioLabel = Label(master=self.rutBeneficiarioFrame, text='RUT Beneficiario')
        self.rutBeneficiarioLabel.pack(side=LEFT) 
        self.rutBeneficiarioEntry = Entry(master=self.rutBeneficiarioFrame)
        self.rutBeneficiarioEntry.pack(side=LEFT, padx=5)
        
        self.rutDeudorFrame = Frame(master=self.stateFrame)
        self.rutDeudorFrame.pack(expand=True, fill=BOTH)
        self.rutDeudorLabel = Label(master=self.rutDeudorFrame, text='RUT Deudor')
        self.rutDeudorLabel.pack(side=LEFT) 
        self.rutDeudorEntry = Entry(master=self.rutDeudorFrame)
        self.rutDeudorEntry.pack(side=LEFT, padx=5)
        
        self.nombreDeudorFrame = Frame(master=self.stateFrame)
        self.nombreDeudorFrame.pack(expand=True, fill=BOTH)
        self.nombreDeudorLabel = Label(master=self.nombreDeudorFrame, text='Nombre Deudor')
        self.nombreDeudorLabel.pack(side=LEFT) 
        self.nombreDeudorEntry = Entry(master=self.nombreDeudorFrame)
        self.nombreDeudorEntry.pack(side=LEFT, padx=5)

        self.apellidoDeudorFrame = Frame(master=self.stateFrame)
        self.apellidoDeudorFrame.pack(expand=True, fill=BOTH)
        self.apellidoDeudorLabel = Label(master=self.apellidoDeudorFrame, text='Apellido Deudor')
        self.apellidoDeudorLabel.pack(side=LEFT) 
        self.apellidoDeudorEntry = Entry(master=self.apellidoDeudorFrame)
        self.apellidoDeudorEntry.pack(side=LEFT, padx=5)
        
        self.clienteFrame =  Frame(master=self.stateFrame)
        self.clienteFrame.pack(expand=True, fill=BOTH)
        self.clienteLabel = Label(master=self.clienteFrame, text='Cliente')
        self.clienteLabel.pack(side=LEFT)
        self.clienteDropdown = ttk.Combobox(master=self.clienteFrame, state='readonly', values=[cliente.nombreCliente for cliente in self.clientes])
        self.clienteDropdown.pack(side=LEFT, padx=5)
        
        self.fileFrame = LabelFrame(master=self.master)
        self.fileFrame.pack(expand=True, fill=BOTH)
        
        self.uploadedBoletaLabel = Label(master=self.fileFrame, font=('Helvetica bold', 10), text='No se ha subido boleta')
        self.uploadedBoletaLabel.grid(row=2, column=0, sticky=W, padx=5, pady=5)
        
        self.uploadedAnexosLabel = Label(master=self.fileFrame, font=('Helvetica bold', 10), text='No se han subido anexos')
        self.uploadedAnexosLabel.grid(row=3, column=0, sticky=W, padx=5, pady=5)
        
        self.boletaPath: str = ''
        self.anexosPaths: list[str] = []
        
        self.saveFrame = LabelFrame(master=self.master)
        self.saveFrame.pack(expand=True, fill=BOTH)
        
        self.saveButton = Button(self.saveFrame, text='Guardar', width=40, height=1, font=('Helvetica bold', 20), command=self.saveChanges)
        self.saveButton.pack(expand=True, fill=BOTH)
        
        self.sendFrame = LabelFrame(master=self.master)
        self.sendFrame.pack(expand=True, fill=BOTH)
        
        self.sendButton = Button(self.saveFrame, text='Enviar reportes', width=40, height=1, font=('Helvetica bold', 20), command=self.runSender)
        self.sendButton.pack(expand=True, fill=BOTH)
        
    @property
    def numAnexos(self):
        return len(self.anexosPaths)
                
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
            merger.append(root)
        merger.write(f'{DELIVEREDDATAPATH}/{numBoleta}/Anexo_{numBoleta}.pdf')
        merger.close()
        shutil.copy(self.boletaPath, f'{DELIVEREDDATAPATH}/{numBoleta}/Boleta_{numBoleta}.pdf')
        messagebox.showinfo(title='Mensaje', message=f'Archivos guardados para boleta n°{numBoleta}')
        self.master.destroy()

    def selectBoletaPDF(self):
        filePath = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if self.fileIsPDF(filePath):
            self.boletaPath = filePath
            self.uploadedBoletaLabel.config(text='Boleta subida')
            try:
                reader: PdfReader = PdfReader(filePath)
                numberIndex: int = reader.pages[0].extract_text().find('°')
                if numberIndex == -1:
                    numberIndex = reader.pages[0].extract_text().find('º')
                subString: str = reader.pages[0].extract_text()[numberIndex::]
                endIndex: int = subString.find('\n')
                subString = subString[0: endIndex + 1]
                numBoleta = extractNumberFromText(subString)
                if numBoleta.isdigit():
                    self.numBoletaEntry.delete(0, END)
                    self.numBoletaEntry.insert(0, numBoleta)
                    messagebox.showinfo(title='Mensaje', message='Boleta subida correctamente')
                else:
                    messagebox.showerror(title='Error', message='No se pudo encontrar el número de boleta en el documento. \nPor favor, ingréselo manualmente.')
            except Exception:
                messagebox.showerror(title='Error', message='No se pudo encontrar el número de boleta en el documento. \nPor favor, ingréselo manualmente.')
        else:
            messagebox.showerror(title='Error', message='Archivo no válido')
            
    def fileIsPDF(self, filePath: str):
        try:
            PdfReader(filePath)
            return True
        except Exception:
            return False
    
    def resetBoleta(self):
        self.boletaPath = ''
        self.uploadedBoletaLabel.config(text='No se ha subido boleta')
        self.numBoletaEntry.delete(0, END)
        
    def resetAnexos(self):
        self.anexosPaths.clear()
        self.uploadedAnexosLabel.config(text='No se han subido anexos')
                
    def selectAnexoPDF(self):
        filePath = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if self.fileIsPDF(filePath):
            self.anexosPaths.append(filePath)
            messagebox.showinfo(title='Mensaje', message='Anexo agregado correctamente')
            self.uploadedAnexosLabel.config(text=f'Anexos subidos: {self.numAnexos}')
        else:
            messagebox.showerror(title='Error', message='Archivo no válido')
        
    def runSender(self):
        os.system('cmd /c start sac_sender.exe') 

root = Tk()
pdf_app = SACUI(root)
root.mainloop()