from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import shutil
import os
from tkinter import filedialog
from Clases.Boleta import Boleta
from Clases.FileGrouper import FileGrouper
from Clases.PDFGenerator import PDFGenerator
from Clases.ReporteData import ReporteData
from Clases.Destinatario import Destinatario
from Utils.Metadata import *
from Utils.GlobalFunctions import *
from PyPDF2 import PdfFileReader, PdfReader, PdfMerger
from PyPDF2.errors import PdfReadError
from Clases.SACConnector import SACConnector
from Clases.Cliente import Cliente
from Clases.AddServicioGUI import AddServicioGUI
from Clases.Servicio import Servicio
from Clases.Beneficiario import Beneficiario
from Clases.Caso import Caso
from Clases.ReportManager import ReportManager
from Clases.SACSenderJob import SACSenderJob
from datetime import date
from PIL import ImageTk, Image
import glob, sys, fitz
import re

class App:
    def __init__(self):
        
        self.sacConnector: SACConnector = SACConnector()
        self.clientes: list[Cliente] = self.sacConnector.getAllClientes()
        self.codigos: list[str] = self.sacConnector.getAllCodigos()
        self.beneficiarios: list[Beneficiario] = self.sacConnector.getAllBeneficiarios()
        self.destinatarios: list[Destinatario] = self.sacConnector.getAllDestinatarios()
        self.casos: list[Caso] = []
        
        self.master = Tk()
        self.master.title("SAC App")
        self.master.resizable(0,0)
        
        self.topFrame = Frame(master=self.master)
        self.topFrame.pack(expand=True, fill=BOTH)
        
        self.thumbnailFrame = Frame(master=self.master)
        self.thumbnailFrame.pack(side=RIGHT)
        self.boletaImage = None
        self.thumbnail = Label(master=self.thumbnailFrame)
        
        self.stateFrame = LabelFrame(master=self.master)
        self.stateFrame.pack(expand=True, fill=BOTH)
        
        Label(master=self.stateFrame, text='Datos generales: ', font=('Helvetica bold', 10, 'bold')).pack(side=TOP)
        
        self.uploadedBoletaFrame = Frame(master=self.stateFrame)
        self.uploadedBoletaFrame.pack(expand=True, fill=BOTH)
        self.uploadedBoletaLabel = Label(master=self.uploadedBoletaFrame, font=('Helvetica bold', 10), text='No se ha subido boleta')
        self.uploadedBoletaLabel.pack(side=LEFT)
        self.boletaUploadButton = Button(self.uploadedBoletaFrame, text="Subir boleta/factura", command=self.selectBoletaPDF)
        self.boletaUploadButton.pack(side=LEFT, padx=10)
        self.boletaResetButton = Button(self.uploadedBoletaFrame, text="Quitar boleta", command=self.clearForm)
        self.boletaResetButton.pack(side=LEFT, padx=10)
        
        self.uploadedAnexosFrame = Frame(master=self.stateFrame)
        self.uploadedAnexosFrame.pack(expand=True, fill=BOTH)
        self.uploadedAnexosLabel = Label(master=self.uploadedAnexosFrame, font=('Helvetica bold', 10), text='No se han subido anexos')
        self.uploadedAnexosLabel.pack(side=LEFT)
        self.anexoUploadButton = Button(self.uploadedAnexosFrame, text="Subir anexo", command=self.selectAnexoPDF)
        self.anexoUploadButton.pack(side=LEFT, padx=10)
        self.anexosResetButton = Button(self.uploadedAnexosFrame, text="Quitar anexos", command=self.resetAnexos)
        self.anexosResetButton.pack(side=LEFT, padx=10)
        
        self.numBoletaFrame = Frame(master=self.stateFrame)
        self.numBoletaFrame.pack(expand=True, fill=BOTH)
        self.numBoletaLabel = Label(master=self.numBoletaFrame, text='N° Boleta')
        self.numBoletaLabel.pack(side=LEFT)
        self.numBoletaEntry = Entry(master=self.numBoletaFrame)
        self.numBoletaEntry.pack(side=LEFT, padx=5)
        
        self.fechaBoletaFrame = Frame(master=self.stateFrame)
        self.fechaBoletaFrame.pack(expand=True, fill=BOTH)
        self.fechaBoletaLabel = Label(master=self.fechaBoletaFrame, text='Fecha Emisión (dd-mm-AAAA)')
        self.fechaBoletaLabel.pack(side=LEFT) 
        self.fechaBoletaEntry: Entry = Entry(master=self.fechaBoletaFrame)
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
        self.nombreBeneficiarioDropdown = ttk.Combobox(master=self.nombreBeneficiarioFrame, state='readonly', values=[beneficiario.nombreBeneficiario for beneficiario in self.beneficiarios], width=40)
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
        self.clienteDropdown.bind("<<ComboboxSelected>>", self.clienteSelectionEvent)
        
        self.gastoTotalFrame = Frame(master=self.stateFrame)
        self.gastoTotalFrame.pack(expand=True, fill=BOTH)
        self.gastoTotalLabel = Label(master=self.gastoTotalFrame, text='Total ($)')
        self.gastoTotalLabel.pack(side=LEFT)
        self.gastoTotalEntry = Entry(master=self.gastoTotalFrame)
        self.gastoTotalEntry.pack(side=LEFT, padx=5)
        
        self.destinatarioFrame = Frame(master=self.stateFrame)
        self.destinatarioFrame.pack(expand=True, fill=BOTH)
        self.destinatarioLabel = Label(master=self.destinatarioFrame, text='Se envía a:')
        self.destinatarioLabel.pack(side=LEFT)
        self.destinatarioDropdown = ttk.Combobox(master=self.destinatarioFrame, state='readonly', values=[destinatario.nombreDestinatario for destinatario in self.destinatarios])
        self.destinatarioDropdown.pack(side=LEFT, padx=5)
        
        self.casosFrame = Frame(master=self.master)
        self.casosFrame.pack(expand=True, fill=BOTH)
        Label(master=self.casosFrame, text='Asociar caso a boleta: ', font=('Helvetica bold', 10, 'bold')).pack(side=TOP)
        self.casosColumns = ['ID Mapsa', 'Estado', 'Fecha Asignación', 'Bsecs', 'RUT Deudor', 'Apellido Deudor', 'Cliente']
        self.casosTable = ttk.Treeview(master=self.casosFrame, columns=self.casosColumns, show='headings', height=3)
        for heading in self.casosColumns:
            self.casosTable.heading(heading, text=heading)
            self.casosTable.column(heading, width=100)
        self.casosTable.pack(expand=True, fill=BOTH, anchor=CENTER)
        self.casosTable.bind('<<TreeviewSelect>>', self.selectCaso)
        
        self.serviciosFrame = Frame(master=self.master)
        self.serviciosFrame.pack(expand=True, fill=BOTH)
        Label(master=self.serviciosFrame, text='Asociar servicios a boleta: ', font=('Helvetica bold', 10, 'bold')).pack(side=TOP)
        self.serviciosColumns = ['Código', 'Nota', 'Monto']
        self.serviciosTable = ttk.Treeview(master=self.serviciosFrame, columns=self.serviciosColumns, show='headings', height=3)
        self.serviciosTable.heading('Código', text='Código')
        self.serviciosTable.heading('Nota', text='Nota')
        self.serviciosTable.heading('Monto', text='Monto')
        self.serviciosTable.pack(expand=True, fill=BOTH, anchor=CENTER)
        self.addServicioButton = Button(master=self.serviciosFrame, text='Agregar servicio', command=self.openServicioGUI)
        self.addServicioButton.pack(expand=True, fill=BOTH)
        self.deleteServicioButton = Button(master=self.serviciosFrame, text='Eliminar servicio', command=self.removeServicio)
        self.deleteServicioButton.pack(expand=True, fill=BOTH)
        
        self.boletaPath: str = ''
        self.anexosPaths: list[str] = []
        
        self.saveFrame = LabelFrame(master=self.master)
        self.saveFrame.pack(expand=True, fill=BOTH)
        
        self.saveButton = Button(self.saveFrame, text='Guardar', width=40, height=1, font=('Helvetica bold', 10), command=self.saveChanges)
        self.saveButton.pack(expand=True, fill=BOTH)
        
        self.sendFrame = LabelFrame(master=self.master)
        self.sendFrame.pack(expand=True, fill=BOTH)
        
        self.sendButton = Button(self.saveFrame, text='Enviar reportes', width=40, height=1, font=('Helvetica bold', 10), command=self.runSender)
        self.sendButton.pack(expand=True, fill=BOTH)
        
        self.manageReportsButton = Button(self.saveFrame, text='Ver reportes a enviar', font=('Helvetica bold', 10), command=self.runReportManager)
        self.manageReportsButton.pack(expand=True, fill=BOTH)
        
        self.clearFormButton = Button(self.saveFrame, text='Borrar formulario', font=('Helvetica bold', 10), command=self.clearForm)
        self.clearFormButton.pack(expand=True, fill=BOTH)
        
        self.master.mainloop()
        
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
    
    def runReportManager(self):
        if not os.path.exists(DELIVEREDDATAPATH):
            messagebox.showerror(title='ERROR', message='No se han cargado boletas para enviar.\nNo hay nada que mostrar.')
            return
        reportManager: ReportManager = ReportManager(container=self)
        
    def validData(self) -> bool:
        if not self.boletaPath:
            messagebox.showerror(title='Error', message='Falta agregar la boleta/factura')
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
        if not self.destinatarioDropdown.get():
            messagebox.showerror(title='Error', message='Falta escoger un destinatario')
            return False
        if self.boletaAlreadyGenerated():
            messagebox.showerror(title='Error', message=f'Ya existe un reporte para la boleta # {self.numBoletaEntry.get()}')
            return False
        return True     
    
    def boletaAlreadyGenerated(self):
        numBoleta: int = int(self.numBoletaEntry.get())
        return bool(self.sacConnector.getBoletaData(numBoleta=numBoleta))
                
    def saveChanges(self):
        if not self.validData():
            return        
        dataSelected: list = self.casosTable.item(self.casosTable.focus())['values']
        idMapsa: int = dataSelected[0]
        numBoleta: int = int(self.numBoletaEntry.get())
        fechaEmision: date = datetime.strptime(self.fechaBoletaEntry.get(), '%d-%m-%Y').date()
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
        if not os.path.exists(f'{DELIVEREDDATAPATH}/{self.destinatarioDropdown.get()}/{numBoleta}_{idMapsa}'):
            os.makedirs(f'{DELIVEREDDATAPATH}/{self.destinatarioDropdown.get()}/{numBoleta}_{idMapsa}')
        merger: PdfMerger = PdfMerger()
        for root in self.anexosPaths:
            merger.append(root)
        if self.anexosPaths:
            merger.write(f'{DELIVEREDDATAPATH}/{self.destinatarioDropdown.get()}/{numBoleta}_{idMapsa}/Anexo_{numBoleta}.pdf')
        merger.close()
        shutil.copy(self.boletaPath, f'{DELIVEREDDATAPATH}/{self.destinatarioDropdown.get()}/{numBoleta}_{idMapsa}/Boleta_{numBoleta}.pdf')
        self.generateReport()
        self.saveDeudorName()
        self.saveParams()
        self.generateUnifiedDocument()
        messagebox.showinfo(title='Mensaje', message=f'Archivos guardados para boleta n°{numBoleta}')
        self.clearForm()
        
    def generateUnifiedDocument(self):
        for nombreDestinatario in os.listdir(path=f'{DELIVEREDDATAPATH}'):
            pdfMerger: PdfMerger = PdfMerger()
            for path in os.listdir(path=f'{DELIVEREDDATAPATH}/{nombreDestinatario}'):
                if path != 'Documento.pdf':
                    numBoleta, idMapsa = (int(x) for x in path.strip().split('_'))
                    reportePath: str = f'{DELIVEREDDATAPATH}/{nombreDestinatario}/{path}/Reporte_{numBoleta}.pdf'
                    boletaPath: str = f'{DELIVEREDDATAPATH}/{nombreDestinatario}/{path}/Boleta_{numBoleta}.pdf'
                    anexoPath: str = f'{DELIVEREDDATAPATH}/{nombreDestinatario}/{path}/Anexo_{numBoleta}.pdf'
                    pdfMerger.append(reportePath)
                    pdfMerger.append(boletaPath)
                    if os.path.exists(anexoPath):
                        pdfMerger.append(anexoPath)
            pdfMerger.write(f'{DELIVEREDDATAPATH}/{nombreDestinatario}/Documento.pdf')
        pdfMerger.close()
        
    def saveDeudorName(self):
        idMapsaSet: int = self.casosTable.item(self.casosTable.focus())['values'][0]
        numBoletaSet: int = int(self.numBoletaEntry.get())
        with open(f'{DELIVEREDDATAPATH}/{self.destinatarioDropdown.get()}/{numBoletaSet}_{idMapsaSet}/DeudorName.txt', 'w') as file:
            file.write(self.nombreDeudorEntry.get())
            
    def saveParams(self):
        idMapsaSet: int = self.casosTable.item(self.casosTable.focus())['values'][0]
        numBoletaSet: int = int(self.numBoletaEntry.get())
        destinatarioSet: Destinatario = None
        destinatario: Destinatario
        for destinatario in self.destinatarios:
            if destinatario.nombreDestinatario == self.destinatarioDropdown.get():
                destinatarioSet = destinatario
                break
        beneficiarioSet: str = self.nombreBeneficiarioDropdown.get()
        clienteSet: str = self.clienteDropdown.get()
        deudorSet: str = self.apellidoDeudorEntry.get()
        montoTotalSet: str = self.gastoTotalEntry.get()     
        with open(f'{DELIVEREDDATAPATH}/{destinatarioSet.nombreDestinatario}/{numBoletaSet}_{idMapsaSet}/Data_{numBoletaSet}.txt', 'w') as file:
            file.write(f'{destinatarioSet.nombreDestinatario},{destinatarioSet.correoDestinatario},{numBoletaSet},{idMapsaSet},{beneficiarioSet},{clienteSet},{deudorSet},{montoTotalSet}')
        
    def generateReport(self):  
        dataReceived: list[str] = [dirName for dirName in os.listdir(f'{DELIVEREDDATAPATH}/{self.destinatarioDropdown.get()}')]
        data: str
        idMapsaSet: int = self.casosTable.item(self.casosTable.focus())['values'][0]
        numBoletaSet: int = int(self.numBoletaEntry.get())
        destinatarioSet: Destinatario = None
        destinatario: Destinatario
        for destinatario in self.destinatarios:
            if destinatario.nombreDestinatario == self.destinatarioDropdown.get():
                destinatarioSet = destinatario
                break        
        for data in dataReceived:
            numBoleta: int = int(data.strip().split('_')[0])
            idMapsa: int = int(data.strip().split('_')[1])
            reporteData: ReporteData = self.sacConnector.getReporteData(numBoleta=numBoleta, idMapsa=idMapsa, destinatarioSet=destinatarioSet)
            reporteData.overwriteDeudorName(newDeudorName=self.nombreDeudorEntry.get())
            if reporteData and idMapsa == idMapsaSet and numBoleta == numBoletaSet:
                pdfGenerator: PDFGenerator = PDFGenerator()
                pdfGenerator.generateReporte(reporteData=reporteData)
                break
                    
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
        self.thumbnailFrame.pack(side=RIGHT)
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
            if (DUARTE in text) or (GYD in text):
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
            if (DUARTE in text) or (GYD in text):
                fechaEmisionString: str = text.split('\n')[19][15::].strip()
            else:
                fechaEmisionString: str = text.split('\n')[9][7::].strip()
            fechaEmision: date = getDateFromSpanishFormat(stringDate=fechaEmisionString)
            self.fechaBoletaEntry.delete(0, END)
            self.fechaBoletaEntry.insert(0, fechaEmision.strftime("%d-%m-%Y"))
        except Exception:
            pass
        
    def getGastoTotalFromFile(self):
        try:
            reader: PdfReader = PdfReader(self.boletaPath)
            text: str = reader.pages[0].extract_text().strip()
            if (DUARTE in text) or (GYD in text):
                total: int = int(text.split('\n')[-1][7::].replace('.',''))
            else:
                total: int = int(text.split('\n')[16][20::].replace('.',''))
            self.gastoTotalEntry.delete(0, END)
            self.gastoTotalEntry.insert(0, total)
        except Exception:
            pass
        
    def runSender(self):
        try:
            if not os.path.exists(DELIVEREDDATAPATH):
                messagebox.showerror(title='Error', message='No hay reportes para enviar')
                return
            senderJob: SACSenderJob = SACSenderJob()
            senderJob.sendReports()
            messagebox.showinfo(title='Éxito', message='Reportes enviados')
        except Exception as e:
            print(e)
            messagebox.showerror(title='Error', message='SAC Sender no pudo ejecutarse')
        
    def openServicioGUI(self):
        addServicioGUI: AddServicioGUI = AddServicioGUI(container=self)
        
    def removeServicio(self):
        if not self.serviciosTable.selection():
            return
        selectedItem = self.serviciosTable.selection()[0]
        self.serviciosTable.delete(selectedItem)
        self.serviciosTable.configure(height=self.addedServicios)
    
    def addServicio(self, servicio: Servicio):
        self.serviciosTable.insert('', END, values=(servicio.codigo, servicio.nota, servicio.monto))
        self.serviciosTable.configure(height=self.addedServicios)
        
    def clienteSelectionEvent(self, key=None):
        self.setDestinatario()
        self.populateCasos()    
    
    def setDestinatario(self, key=None):
        cliente: Cliente
        for cliente in self.clientes:
            if self.clienteDropdown.get() == cliente.nombreCliente:
                idCliente: int = cliente.idCliente
        selectedDestinatario: Destinatario = self.sacConnector.getDestinatarioByCliente(idCliente=idCliente)
        index: int = [destinatario.nombreDestinatario for destinatario in self.destinatarios].index(selectedDestinatario.nombreDestinatario)
        self.destinatarioDropdown.current(index)
    
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
            self.setDestinatario()
    
    def clearForm(self):
        self.boletaPath = ''
        self.anexosPaths.clear()
        self.numBoletaEntry.delete(0, END)
        self.fechaBoletaEntry.delete(0, END)
        self.rutBeneficiarioEntry.delete(0, END)
        self.nombreBeneficiarioDropdown.set('')
        self.rutDeudorEntry.delete(0, END)
        self.apellidoDeudorEntry.delete(0, END)
        self.nombreDeudorEntry.delete(0, END)
        self.clienteDropdown.set('')
        self.gastoTotalEntry.delete(0, END)
        self.destinatarioDropdown.set('')
        self.casosTable.delete(*self.casosTable.get_children())
        self.serviciosTable.delete(*self.serviciosTable.get_children())
        self.destinatarioDropdown.set('')
        self.uploadedAnexosLabel.config(text='No se han subido anexos')
        self.uploadedBoletaLabel.config(text='No se ha subido boleta')

        self.master.destroy()
        self.master.update()
        app: App = App()