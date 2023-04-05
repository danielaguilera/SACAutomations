from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import shutil
import os
from tkinter import filedialog
from tkcalendar import Calendar, DateEntry
from Utils.Metadata import *
from Utils.GlobalFunctions import *
from PyPDF2 import PdfReader, PdfMerger
from PyPDF2.errors import PdfReadError
from Clases.SACConnector import SACConnector
from Clases.Cliente import Cliente
from Clases.AddServicioGUI import AddServicioGUI
from Clases.Servicio import Servicio
from Clases.Caso import Caso
from datetime import date
import re

class SACUI:
    def __init__(self, master: Tk):
        
        self.sacConnector: SACConnector = SACConnector()
        self.clientes: list[Cliente] = self.sacConnector.getAllClientes()
        self.codigos: list[str] = self.sacConnector.getAllCodigos()
        self.casos: list[Caso] = []
        
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
        self.fechaBoletaLabel = Label(master=self.fechaBoletaFrame, text='Fecha Emisión')
        self.fechaBoletaLabel.pack(side=LEFT) 
        self.fechaBoletaEntry: DateEntry = DateEntry(master=self.fechaBoletaFrame)
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
        self.rutDeudorEntry.bind("<KeyRelease>", self.populateCasos) 
        
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
        self.apellidoDeudorEntry.bind("<KeyRelease>", self.populateCasos)
        
        self.clienteFrame = Frame(master=self.stateFrame)
        self.clienteFrame.pack(expand=True, fill=BOTH)
        self.clienteLabel = Label(master=self.clienteFrame, text='Cliente')
        self.clienteLabel.pack(side=LEFT)
        self.clienteDropdown = ttk.Combobox(master=self.clienteFrame, state='readonly', values=[cliente.nombreCliente for cliente in self.clientes] + ['Ninguno'])
        self.clienteDropdown.pack(side=LEFT, padx=5)
        self.clienteDropdown.bind("<<ComboboxSelected>>", self.populateCasos)
        
        self.serviciosFrame = Frame(master=self.master)
        self.serviciosFrame.pack(expand=True, fill=BOTH)
        self.addedServiciosLabel = Label(master=self.master, text='No se han agregado servicios')
        self.addedServiciosLabel.pack(expand=True, fill=BOTH)
        self.serviciosColumns = ['Código', 'Nota', 'Monto']
        self.serviciosTable = ttk.Treeview(master=self.serviciosFrame, columns=self.serviciosColumns, show='headings', height=0)
        self.serviciosTable.heading('Código', text='Código')
        self.serviciosTable.heading('Nota', text='Nota')
        self.serviciosTable.heading('Monto', text='Monto')
        self.serviciosTable.pack(expand=True, fill=BOTH, anchor=CENTER)
        self.addServicioButton = Button(master=self.serviciosFrame, text='Agregar servicio', command=self.openServicioGUI)
        self.addServicioButton.pack(expand=True, fill=BOTH)
        self.deleteServicioButton = Button(master=self.serviciosFrame, text='Eliminar servicio', command=self.removeServicio)
        self.deleteServicioButton.pack(expand=True, fill=BOTH)
        
        
        
        
        
        
        self.fileFrame = LabelFrame(master=self.master)
        self.fileFrame.pack(expand=True, fill=BOTH)
        
        self.uploadedBoletaLabel = Label(master=self.fileFrame, font=('Helvetica bold', 10), text='No se ha subido boleta')
        self.uploadedBoletaLabel.grid(row=2, column=0, sticky=W, padx=5, pady=5)
        
        self.uploadedAnexosLabel = Label(master=self.fileFrame, font=('Helvetica bold', 10), text='No se han subido anexos')
        self.uploadedAnexosLabel.grid(row=3, column=0, sticky=W, padx=5, pady=5)
        
        self.casosFrame = Frame(master=self.master)
        self.casosFrame.pack(expand=True, fill=BOTH)
        
        self.casosColumns = ['ID Mapsa', 'Estado', 'Fecha Asignación', 'Bsecs', 'RUT Deudor', 'Apellido Deudor', 'Cliente']
        self.casosTable = ttk.Treeview(master=self.casosFrame, columns=self.casosColumns, show='headings', height=5)
        for heading in self.casosColumns:
            self.casosTable.heading(heading, text=heading)
        self.casosTable.pack(expand=True, fill=BOTH, anchor=CENTER)
        self.casosTable.bind('<<TreeviewSelect>>', self.selectCaso)
        
        self.boletaPath: str = ''
        self.anexosPaths: list[str] = []
        
        self.saveFrame = LabelFrame(master=self.master)
        self.saveFrame.pack(expand=True, fill=BOTH)
        
        self.saveButton = Button(self.saveFrame, text='Guardar', width=40, height=1, font=('Helvetica bold', 20), command=self.getMapsaCasos)
        self.saveButton.pack(expand=True, fill=BOTH)
        
        self.sendFrame = LabelFrame(master=self.master)
        self.sendFrame.pack(expand=True, fill=BOTH)
        
        self.sendButton = Button(self.saveFrame, text='Enviar reportes', width=40, height=1, font=('Helvetica bold', 20), command=self.runSender)
        self.sendButton.pack(expand=True, fill=BOTH)
        
    @property
    def numAnexos(self):
        return len(self.anexosPaths)
    
    def getMapsaCasos(self):
        idCliente: int = 0
        for cliente in self.clientes:
            if cliente.nombreCliente == self.clienteDropdown.get():
                idCliente = cliente.idCliente
        rutDeudor: str = self.rutDeudorEntry.get()
        print(self.sacConnector.getPossibleMapsaCasos(idCliente=idCliente, rutDeudor=rutDeudor))
                
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

    # def selectBoletaPDF(self):
    #     filePath = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    #     if self.fileIsPDF(filePath):
    #         self.boletaPath = filePath
    #         self.uploadedBoletaLabel.config(text='Boleta subida')
    #         try:
    #             reader: PdfReader = PdfReader(filePath)
    #             numberIndex: int = reader.pages[0].extract_text().find('°')
    #             if numberIndex == -1:
    #                 numberIndex = reader.pages[0].extract_text().find('º')
    #             subString: str = reader.pages[0].extract_text()[numberIndex::]
    #             endIndex: int = subString.find('\n')
    #             subString = subString[0: endIndex + 1]
    #             numBoleta = extractNumberFromText(subString)
    #             if numBoleta.isdigit():
    #                 self.numBoletaEntry.delete(0, END)
    #                 self.numBoletaEntry.insert(0, numBoleta)
    #                 messagebox.showinfo(title='Mensaje', message='Boleta subida correctamente')
    #             else:
    #                 messagebox.showerror(title='Error', message='No se pudo encontrar el número de boleta en el documento. \nPor favor, ingréselo manualmente.')
    #         except Exception:
    #             messagebox.showerror(title='Error', message='No se pudo encontrar el número de boleta en el documento. \nPor favor, ingréselo manualmente.')
    #     else:
    #         messagebox.showerror(title='Error', message='Archivo no válido')
            
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
            
    def selectBoletaPDF(self):
        filePath = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if self.fileIsPDF(filePath):
            self.boletaPath = filePath
            messagebox.showinfo(title='Mensaje', message='Boleta subida correctamente')
            self.uploadedBoletaLabel.config(text=f'Boleta subida')
            self.getNumeroBoletaFromFile()
            self.getRUTBeneficiarioFromFile()
            self.getFechaFromFile()
        else:
            messagebox.showerror(title='Error', message='Archivo no válido')
    
    def getNumeroBoletaFromFile(self):
        try:
            reader: PdfReader = PdfReader(self.boletaPath)
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
        except Exception:
            pass
        
    def getRUTBeneficiarioFromFile(self):
        try:
            reader: PdfReader = PdfReader(self.boletaPath)
            text: str = reader.pages[0].extract_text().strip()
            if DUARTE in text:
                rutBeneficiario: str = text.split('\n')[14].split(':')[2].replace(' ', '').strip()
            else:
                rutBeneficiario: str = text.split('\n')[3][5::].strip()
            self.rutBeneficiarioEntry.delete(0, END)
            self.rutBeneficiarioEntry.insert(0, rutBeneficiario)
        except Exception:
            pass
        
    def getFechaFromFile(self):
        try:
            reader: PdfReader = PdfReader(self.boletaPath)
            text: str = reader.pages[0].extract_text().strip()
            if DUARTE in text:
                fechaEmisionString: str = text.split('\n')[19][15::].strip()
            else:
                fechaEmisionString: str = text.split('\n')[9][7::].strip()
            fechaEmision: date = getDateFromSpanishFormat(stringDate=fechaEmisionString)
            self.fechaBoletaEntry.set_date(date=fechaEmision)
        except Exception:
            pass
            
        
    def runSender(self):
        os.system('cmd /c start sac_sender.exe') 
        
    def openServicioGUI(self):
        addServicioGUI: AddServicioGUI = AddServicioGUI(container=self)
        
    def removeServicio(self):
        selectedItem = self.serviciosTable.selection()[0]
        self.serviciosTable.delete(selectedItem)
        self.serviciosTable.configure(height=len(self.serviciosTable.get_children()))
    
    def addServicio(self, servicio: Servicio):
        self.serviciosTable.insert('', END, values=(servicio.codigo, servicio.nota, servicio.monto))
        self.serviciosTable.configure(height=len(self.serviciosTable.get_children()))
        
    def populateCasos(self, key=None):
        if len(self.casosTable.selection()) > 0:
            self.casosTable.selection_remove(self.casosTable.selection()[0])
        rutDeudor: str = self.rutDeudorEntry.get()
        selectedClienteName: str = self.clienteDropdown.get()
        idCliente: int | None = None
        if selectedClienteName:
            cliente: Cliente
            for cliente in self.clientes:
                if cliente.nombreCliente == selectedClienteName:
                    idCliente = cliente.idCliente
                    break
        apellidoDeudor: str = self.apellidoDeudorEntry.get()
        self.casos = self.sacConnector.getPossibleMapsaCasos(rutDeudor=rutDeudor, idCliente=idCliente, apellidoDeudor=apellidoDeudor)
        caso: Caso
        self.casosTable.delete(*self.casosTable.get_children())
        for caso in self.casos:
            self.casosTable.insert('', END, values=(caso.idMapsa, caso.nombreEstado, caso.fechaAsignado, caso.bsecs, caso.rutDeudor, caso.apellidoDeudor, caso.nombreCliente))

    def selectCaso(self, key=None):
        dataSelected: list = self.casosTable.item(self.casosTable.focus())['values']
        if dataSelected:
            rutDeudor: str = dataSelected[4]
            apellidoDeudor: str = dataSelected[5]
            nombreDeudor: str = self.sacConnector.getDeudorName(rutDeudor=rutDeudor)
            nombreCliente: str = dataSelected[6]
            indexCliente: int = ([cliente.nombreCliente for cliente in self.clientes] + ['Ninguno']).index(nombreCliente)
            self.clienteDropdown.current(newindex=indexCliente)
            self.rutDeudorEntry.delete(0, END)
            self.rutDeudorEntry.insert(0, rutDeudor)
            self.nombreDeudorEntry.delete(0, END)
            self.nombreDeudorEntry.insert(0, nombreDeudor)
            self.apellidoDeudorEntry.delete(0, END)
            self.apellidoDeudorEntry.insert(0, apellidoDeudor)
        

if __name__ == '__main__':
    root = Tk()
    pdf_app = SACUI(root)
    root.mainloop()