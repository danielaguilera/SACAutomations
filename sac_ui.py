from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import shutil
import os
from tkinter import filedialog
from tkcalendar import Calendar, DateEntry
from Clases.Boleta import Boleta
from Utils.Metadata import *
from Utils.GlobalFunctions import *
from PyPDF2 import PdfReader, PdfMerger
from PyPDF2.errors import PdfReadError
from Clases.SACConnector import SACConnector
from Clases.Cliente import Cliente
from Clases.AddServicioGUI import AddServicioGUI
from Clases.Servicio import Servicio
from Clases.Beneficiario import Beneficiario
from Clases.Caso import Caso
from datetime import date
from PIL import ImageTk, Image
import glob, sys, fitz

class SACUI:
    def __init__(self, master: Tk):
        
        self.sacConnector: SACConnector = SACConnector()
        self.clientes: list[Cliente] = self.sacConnector.getAllClientes()
        self.codigos: list[str] = self.sacConnector.getAllCodigos()
        self.beneficiarios: list[Beneficiario] = self.sacConnector.getAllBeneficiarios()
        self.casos: list[Caso] = []
        
        self.master = master
        self.master.title("SAC App")
        self.master.size =(30,30)
        self.master.resizable(0,0)
        
        self.thumbnailFrame = Frame(master=self.master)
        self.thumbnailFrame.pack(side=RIGHT)
        self.boletaImage = PhotoImage(file='thumbnail.png')
        self.thumbnail = Label(master=self.thumbnailFrame)
        
        self.uploadFrame = LabelFrame(master=self.master)
        self.uploadFrame.pack(expand=True, fill=BOTH)
        
        self.uploadFrame.grid_columnconfigure(1, weight=1)
        self.uploadFrame.grid_rowconfigure(1, weight=1)

        self.boletaUploadButton = Button(self.uploadFrame, text="Subir boleta SII", font=('Helvetica bold', 15), command=self.selectBoletaPDF, width=30)
        self.boletaUploadButton.grid(row=0, column=0)
        
        self.boletaResetButton = Button(self.uploadFrame, text="Reestablecer boleta", font=('Helvetica bold', 15), command=self.resetBoleta, width=30)
        self.boletaResetButton.grid(row=1, column=0)
        
        self.anexoUploadButton = Button(self.uploadFrame, text="Subir anexo", font=('Helvetica bold', 15), command=self.selectAnexoPDF, width=30)
        self.anexoUploadButton.grid(row=0, column=1)

        self.anexoResetButton = Button(self.uploadFrame, text="Reestablecer anexos", font=('Helvetica bold', 15), command=self.resetAnexos, width=30)
        self.anexoResetButton.grid(row=1, column=1)


        
        self.stateFrame = LabelFrame(master=self.master)
        self.stateFrame.pack(expand=True, fill=BOTH)
        
        Label(master=self.stateFrame, text='Datos generales: ', font=('Helvetica bold', 10, 'bold')).pack(side=TOP)
        
        self.uploadedBoletaFrame = Frame(master=self.stateFrame)
        self.uploadedBoletaFrame.pack(expand=True, fill=BOTH)
        self.uploadedBoletaLabel = Label(master=self.uploadedBoletaFrame, font=('Helvetica bold', 10), text='No se ha subido boleta')
        self.uploadedBoletaLabel.pack(side=LEFT)
        
        self.uploadedAnexosFrame = Frame(master=self.stateFrame)
        self.uploadedAnexosFrame.pack(expand=True, fill=BOTH)
        self.uploadedAnexosLabel = Label(master=self.uploadedAnexosFrame, font=('Helvetica bold', 10), text='No se han subido anexos')
        self.uploadedAnexosLabel.pack(side=LEFT)
        
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
        self.rutBeneficiarioEntry.bind("<KeyRelease>", self.findBeneficiario)
        
        self.nombreBeneficiarioFrame = Frame(master=self.stateFrame)
        self.nombreBeneficiarioFrame.pack(expand=True, fill=BOTH)
        self.nombreBeneficiarioLabel = Label(master=self.nombreBeneficiarioFrame, text='Nombre o Razón Social')
        self.nombreBeneficiarioLabel.pack(side=LEFT)
        self.nombreBeneficiarioDropdown = ttk.Combobox(master=self.nombreBeneficiarioFrame, state='readonly', values=[beneficiario.nombreBeneficiario for beneficiario in self.beneficiarios])
        self.nombreBeneficiarioDropdown.pack(side=LEFT, padx=5)
        self.nombreBeneficiarioDropdown.bind("<<ComboboxSelected>>", self.assignBeneficiario)
        
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
        
        self.gastoTotalFrame = Frame(master=self.stateFrame)
        self.gastoTotalFrame.pack(expand=True, fill=BOTH)
        self.gastoTotalLabel = Label(master=self.gastoTotalFrame, text='Total ($)')
        self.gastoTotalLabel.pack(side=LEFT)
        self.gastoTotalEntry = Entry(master=self.gastoTotalFrame)
        self.gastoTotalEntry.pack(side=LEFT, padx=5)
        
        self.casosFrame = Frame(master=self.master)
        self.casosFrame.pack(expand=True, fill=BOTH)
        Label(master=self.casosFrame, text='Asociar caso a boleta: ', font=('Helvetica bold', 10, 'bold')).pack(side=TOP)
        self.casosColumns = ['ID Mapsa', 'Estado', 'Fecha Asignación', 'Bsecs', 'RUT Deudor', 'Apellido Deudor', 'Cliente']
        self.casosTable = ttk.Treeview(master=self.casosFrame, columns=self.casosColumns, show='headings', height=5)
        for heading in self.casosColumns:
            self.casosTable.heading(heading, text=heading)
            self.casosTable.column(heading, width=100)
        self.casosTable.pack(expand=False, anchor=CENTER)
        self.casosTable.bind('<<TreeviewSelect>>', self.selectCaso)
        
        self.serviciosFrame = Frame(master=self.master)
        self.serviciosFrame.pack(expand=True, fill=BOTH)
        Label(master=self.serviciosFrame, text='Asociar servicios a boleta: ', font=('Helvetica bold', 10, 'bold')).pack(side=TOP)
        self.addedServiciosLabel = Label(master=self.master, text='No se han agregado servicios')
        self.addedServiciosLabel.pack(expand=True, fill=BOTH)
        self.serviciosColumns = ['Código', 'Nota', 'Monto']
        self.serviciosTable = ttk.Treeview(master=self.serviciosFrame, columns=self.serviciosColumns, show='headings', height=0)
        self.serviciosTable.heading('Código', text='Código')
        self.serviciosTable.heading('Nota', text='Nota')
        self.serviciosTable.heading('Monto', text='Monto')
        self.serviciosTable.pack(expand=False, fill=BOTH, anchor=CENTER)
        self.addServicioButton = Button(master=self.serviciosFrame, text='Agregar servicio', command=self.openServicioGUI)
        self.addServicioButton.pack(expand=True, fill=BOTH)
        self.deleteServicioButton = Button(master=self.serviciosFrame, text='Eliminar servicio', command=self.removeServicio)
        self.deleteServicioButton.pack(expand=True, fill=BOTH)
        
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
    def numAnexos(self) -> int:
        return len(self.anexosPaths)
    
    @property
    def servicioSum(self) -> int:
        total: int = 0
        for iid in self.serviciosTable.get_children():
            monto: int = self.serviciosTable.item(iid)['values'][2]
            total += int(monto)
        return total
    
    @property
    def addedServicios(self) -> int:
        return len(self.serviciosTable.get_children())
    
    def getMapsaCasos(self):
        idCliente: int = 0
        for cliente in self.clientes:
            if cliente.nombreCliente == self.clienteDropdown.get():
                idCliente = cliente.idCliente
        rutDeudor: str = self.rutDeudorEntry.get()
        
    def validData(self) -> bool:
        if not self.boletaPath:
            messagebox.showerror(title='Error', message='Falta agregar la boleta del SII')
            return False
        if not self.numBoletaEntry.get().isdigit():
            messagebox.showerror(title='Error', message='El número de boleta debe ser un número entero')
            return False
        if not self.rutBeneficiarioEntry.get() in [beneficiario.rutBeneficiario for beneficiario in self.beneficiarios]:
            messagebox.showerror(title='Error', message='No existe beneficiario con ese rut')
            return False
        if not self.nombreBeneficiarioDropdown.get():
            messagebox.showerror(title='Error', message='Beneficiario no identificado')
            return False
        if not self.casosTable.focus():
            messagebox.showerror(title='Error', message='Debes seleccionar un caso')
            return False
        if not self.serviciosTable.get_children():
            messagebox.showerror(title='Error', message='Debes agregar al menos 1 servicio en la boleta')
            return False
        if not self.gastoTotalEntry.get().isdigit():
            messagebox.showerror(title='Error', message='El total de la boleta debe ser un número entero')
            return False
        if int(self.gastoTotalEntry.get()) != self.servicioSum:
            messagebox.showerror(title='Error', message='El total de la boleta debe ser igual a la suma de los montos de los servicios')
            return False
        return True        
                
    def saveChanges(self):
        if not self.validData():
            return        
        dataSelected: list = self.casosTable.item(self.casosTable.focus())['values']
        idMapsa: int = dataSelected[0]
        numBoleta: int = int(self.numBoletaEntry.get())
        fechaEmision: date = self.fechaBoletaEntry.get_date()
        rutBeneficiario: str = self.rutBeneficiarioEntry.get()
        servicios: list[Servicio] = []
        for iid in self.serviciosTable.get_children():
            codigo, nota, monto = self.serviciosTable.item(iid)['values']
            servicios.append(Servicio(codigo=codigo, nota=nota, monto=monto))
        boleta: Boleta = Boleta(idMapsa=idMapsa, 
                                numBoleta=numBoleta, 
                                fechaEmision=fechaEmision, 
                                rutBeneficiario=rutBeneficiario, 
                                servicios=servicios)
        self.sacConnector.insertBoletaData(boleta=boleta)        

        
        
        numBoleta: int = int(self.numBoletaEntry.get())
        idMapsa: int = boleta.idMapsa
        if not os.path.exists(DELIVEREDDATAPATH):
            os.makedirs(DELIVEREDDATAPATH)
        if not os.path.exists(f'{DELIVEREDDATAPATH}/{numBoleta}_{idMapsa}'):
            os.makedirs(f'{DELIVEREDDATAPATH}/{numBoleta}_{idMapsa}')
        merger: PdfMerger = PdfMerger()
        for root in self.anexosPaths:
            merger.append(root)
        merger.write(f'{DELIVEREDDATAPATH}/{numBoleta}_{idMapsa}/Anexo_{numBoleta}.pdf')
        merger.close()
        shutil.copy(self.boletaPath, f'{DELIVEREDDATAPATH}/{numBoleta}_{idMapsa}/Boleta_{numBoleta}.pdf')




        messagebox.showinfo(title='Mensaje', message=f'Archivos guardados para boleta n°{numBoleta}')
        self.master.destroy()
            
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
            self.getGastoTotalFromFile()
            self.displayThumbnail()
        else:
            messagebox.showerror(title='Error', message='Archivo no válido')
            
    def displayThumbnail(self):
        zoom_x = 1.0  # horizontal zoom
        zoom_y = 1.0  # vertical zoom
        mat = fitz.Matrix(zoom_x, zoom_y)  # zoom factor 2 in each dimension

        filename = self.boletaPath
        doc = fitz.open(filename)  # open document
        for page in doc:  # iterate through the pages
            pix = page.get_pixmap(matrix=mat)  # render page to an image
            pix.save("thumbnail.png")  # store image as a PNG
            
        self.boletaImage = PhotoImage(file='thumbnail.png')
        self.thumbnail.config(image=self.boletaImage)
        self.thumbnail.pack()
    
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
            rutBeneficiario = correctRUTFormat(rutBeneficiario)
            self.rutBeneficiarioEntry.delete(0, END)
            self.rutBeneficiarioEntry.insert(0, rutBeneficiario)
            beneficiarioFound: Beneficiario = self.sacConnector.findBeneficiario(rutBeneficiario=rutBeneficiario)
            if beneficiarioFound:
                for index, beneficiario in enumerate(self.beneficiarios):
                    if beneficiario.nombreBeneficiario == beneficiarioFound.nombreBeneficiario:
                        self.nombreBeneficiarioDropdown.current(newindex=index)
                        return
            self.nombreBeneficiarioDropdown.set('Sin resultados')
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
        
    def getGastoTotalFromFile(self):
        try:
            reader: PdfReader = PdfReader(self.boletaPath)
            text: str = reader.pages[0].extract_text().strip()
            if DUARTE in text:
                total: int = int(text.split('\n')[-1][7::].replace('.',''))
            else:
                total: int = int(text.split('\n')[16][20::].replace('.',''))
            self.gastoTotalEntry.delete(0, END)
            self.gastoTotalEntry.insert(0, total)
        except Exception:
            pass
            
        
    def runSender(self):
        os.system('cmd /c python sac_sender.py') 
        
    def openServicioGUI(self):
        addServicioGUI: AddServicioGUI = AddServicioGUI(container=self)
        
    def removeServicio(self):
        if not self.serviciosTable.selection():
            return
        selectedItem = self.serviciosTable.selection()[0]
        self.serviciosTable.delete(selectedItem)
        self.serviciosTable.configure(height=self.addedServicios)
        if self.addedServicios:
            self.addedServiciosLabel.config(text=f'Servicios agregados: {self.addedServicios} - Total: ${self.servicioSum}')
        else:
            self.addedServiciosLabel.config(text='No se han agregado servicios')
    
    def addServicio(self, servicio: Servicio):
        self.serviciosTable.insert('', END, values=(servicio.codigo, servicio.nota, servicio.monto))
        self.serviciosTable.configure(height=self.addedServicios)
        self.addedServiciosLabel.config(text=f'Servicios agregados: {self.addedServicios} - Total: ${self.servicioSum}')
        
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

    def assignBeneficiario(self, key=None):
        nombreBeneficiario: str = self.nombreBeneficiarioDropdown.get()
        beneficiario: Beneficiario
        for beneficiario in self.beneficiarios:
            if beneficiario.nombreBeneficiario == nombreBeneficiario:
                self.rutBeneficiarioEntry.delete(0, END)
                self.rutBeneficiarioEntry.insert(0, beneficiario.rutBeneficiario)
                return
            
    def findBeneficiario(self, key=None):
        rutBeneficiario: str = self.rutBeneficiarioEntry.get()
        beneficiariosFound: list[Beneficiario] = self.sacConnector.getPossibleBeneficiarios(rutBeneficiario=rutBeneficiario)
        if beneficiariosFound:
            self.nombreBeneficiarioDropdown.config(values=[beneficiario.nombreBeneficiario for beneficiario in beneficiariosFound])
        else:
            self.nombreBeneficiarioDropdown.set('Sin resultados')

        

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
            
'''
TODO:

- En la carpeta DatosRecibidos agregar un archivo de texto donde se indique el numero del caso Mapsa al que se hace referencia.
- Marcar como print = True en la tabla Boletas cuando se haya generado el reporte.
- Considerar tomar solo los casos donde print = False.
- Guardar historial de reportes generados (con fecha de creación, caso Mapsa, # boleta)
- Validar user input en el frmulario
- Dejar el sacsender en una clase para poder manipularlo más fácilmente.
- IDEA: Para las boletas de DUARTE SPA se podrían subir de inmediato los gastos (y probablemente los datos del deudor -> posiblemente identificar caso Mapsa automáticamente).

'''
        

if __name__ == '__main__':
    root = Tk()
    app = SACUI(root)
    root.mainloop()