from tkinter import *
from tkinter import ttk

from PyPDF2 import PdfMerger
from Clases.SACConnector import SACConnector
from Clases.SACSenderJob import SACSenderJob
from Utils.GlobalFunctions import *
from Utils.Metadata import *
from Clases.Servicio import Servicio
from tkinter import messagebox
import os
import shutil
from PIL import ImageTk, Image
import glob, sys, fitz

class ReportManager:
    def __init__(self, container):
        self.container = container
        self.toplevel = Toplevel(background='seashell4')
        self.toplevel.title(string='Reportes a enviar')
        self.thumbnailFrame = Frame(master=self.toplevel)
        self.thumbnailFrame.pack(side=RIGHT)
        self.reporteImage = None
        self.thumbnail = Label(master=self.thumbnailFrame)
        self.sacConnector: SACConnector = SACConnector()
        self.reportFrame = Frame(master=self.toplevel)
        self.reportFrame.pack(expand=True, fill=BOTH)
        self.reportColumns = ['Destinatario', 'Email', '# Boleta', 'ID Mapsa', 'Beneficiario', 'Cliente', 'Deudor', 'Monto Total (CLP)']
        self.columnWidths = [200, 150, 50, 150, 100, 100, 100]
        self.reportTable = ttk.Treeview(master=self.reportFrame, columns=self.reportColumns, show='headings', height=10)
        for columnName in self.reportColumns:
            self.reportTable.heading(columnName, text=columnName)
            self.reportTable.column(columnName, width=150)
        self.reportTable.pack(expand=True, fill=BOTH, anchor=CENTER, padx=5)
        self.reportTable.bind('<<TreeviewSelect>>', self.displayThumbnail)
        
        self.actionFrame = Frame(master=self.toplevel)
        self.actionFrame.pack(expand=True, fill=BOTH)

        self.sendButton = Button(master=self.actionFrame, text='Enviar todo', width=40, height=1, font=('Helvetica bold', 15), fg = 'black', bg='RoyalBlue1', command=self.sendAllReports)
        self.sendButton.pack(expand=False, fill=BOTH)   

        self.sendDestinatarioButton = Button(master=self.actionFrame, text='Enviar todo del destinatario', width=40, height=1, font=('Helvetica bold', 15), fg = 'black', bg='lawngreen', command=self.sendDestinatarioReports)
        self.sendDestinatarioButton.pack(expand=False, fill=BOTH)      

        self.deleteButton = Button(master=self.actionFrame, text='Eliminar reporte', width=40, height=1, font=('Helvetica bold', 15), fg = 'black', bg='indian red', command=self.deleteReport)
        self.deleteButton.pack(expand=False, fill=BOTH)
        
        self.getReports()
        
    def getReports(self):
        if not os.path.exists(DELIVEREDDATAPATH):
            return
        self.reportTable.delete(*self.reportTable.get_children())
        nombreDestinatario: str
        for nombreDestinatario in os.listdir(DELIVEREDDATAPATH):
            self.reportTable.insert('', END, iid=nombreDestinatario, values=(nombreDestinatario,'','','','','','',''), open=True)
            for dirName in os.listdir(f'{DELIVEREDDATAPATH}/{nombreDestinatario}'):
                if dirName != 'Documento.pdf':
                    numBoleta, idMapsa = [int(x) for x in dirName.strip().split('_')]
                    with open(f'{DELIVEREDDATAPATH}/{nombreDestinatario}/{numBoleta}_{idMapsa}/Data_{numBoleta}.txt') as file:
                        data = file.readline().strip().split(',')
                        nombreDestinatario = data[0]
                        mailDestinatario = data[1]
                        numBoleta = data[2]
                        idMapsa = data[3]
                        nombreBeneficiario = data[4]
                        nombreCliente = data[5]
                        nombreDeudor = data[6]
                        montoTotal = data[7]
                        tableData = ('-','-',numBoleta,idMapsa,nombreBeneficiario,nombreCliente,nombreDeudor,montoTotal)
                        self.reportTable.insert(nombreDestinatario, END, values=tableData, open=True)
                    self.reportTable.item(nombreDestinatario, values=(nombreDestinatario, mailDestinatario,'','','','','',''))
    
    def displayThumbnail(self, key=None):
        data = self.reportTable.item(self.reportTable.selection()[0])['values']
        if not(data[2] and data[3]):
            return
        numBoleta: int = int(data[2])
        idMapsa: int = int(data[3])
        nombreDestinatario: str = self.reportTable.item(self.reportTable.parent(self.reportTable.selection()[0]))['values'][0]
        
        zoom_x = 1.0  # horizontal zoom
        zoom_y = 1.0  # vertical zoom
        mat = fitz.Matrix(zoom_x, zoom_y)  # zoom factor 2 in each dimension

        filename = f'{DELIVEREDDATAPATH}/{nombreDestinatario}/{numBoleta}_{idMapsa}/Reporte_{numBoleta}.pdf' 
        
        doc = fitz.open(filename)  # open document
        for page in doc:  # iterate through the pages
            pix = page.get_pixmap(matrix=mat)  # render page to an image
            pix.save("thumbnail.png")  # store image as a PNG
        doc.close()
            
        self.reporteImage = PhotoImage(file='thumbnail.png')
        self.thumbnail.config(image=self.reporteImage)
        self.thumbnail.pack()
    
    def deleteReport(self):
        if not self.reportTable.focus():
            return
        data = self.reportTable.item(self.reportTable.selection()[0])['values']
        if not(data[2] and data[3]):
            return
        if not messagebox.askyesno(title='Aviso', message='¿Estás segur@ de que quieres borrar los datos para esta boleta?'):
            return
        numBoleta: int = int(data[2])
        idMapsa: int = int(data[3])
        nombreDestinatario: str = self.reportTable.item(self.reportTable.parent(self.reportTable.selection()[0]))['values'][0]
        self.sacConnector.deleteBoletaData(numBoleta=numBoleta, idMapsa=idMapsa)
        deleteIfExists(f'{DELIVEREDDATAPATH}/{nombreDestinatario}/{numBoleta}_{idMapsa}')
        deleteIfEmpty(f'{DELIVEREDDATAPATH}/{nombreDestinatario}')
        deleteIfEmpty(f'{DELIVEREDDATAPATH}')
        self.updateUnifiedDocument(nombreDestinatario=nombreDestinatario)
        messagebox.showinfo(title='INFO', message='Reporte borrado')
        self.resetForm()
        with open(ACTIVITYLOGFILE, 'a') as file:
            file.write(f'{str(datetime.now())}: {USER} eliminó los archivos de boleta a enviar (NUMERO BOLETA: {numBoleta} - ID MAPSA: {idMapsa}) del destinatario {nombreDestinatario}\n')
        
    def resetForm(self):
        self.toplevel.destroy()
        self.toplevel.update()
        reportManager: ReportManager = ReportManager(container=self.container)

    def sendDestinatarioReports(self):
        if not self.reportTable.focus():
            return
        data = self.reportTable.item(self.reportTable.selection()[0])['values']
        if data[2]:
            return
        nombreDestinatario: str = data[0]
        if not messagebox.askyesno(title='Aviso', message=f'Se enviarán todas las boletas de esta semana para {nombreDestinatario}. \n¿Deseas continuar?'):
            return
        try:
            senderJob: SACSenderJob = SACSenderJob()
            senderJob.sendSingleDestinatarioReports(nombreDestinatario=nombreDestinatario)
            messagebox.showinfo(title='Éxito', message='Reportes enviados')
            self.resetForm()
        except Exception as e:
            print(e)
            messagebox.showerror(title='Error', message='SAC Sender no pudo ejecutarse')

    def sendAllReports(self):
        if not messagebox.askyesno(title='Aviso', message='Se enviarán todas las boletas de esta semana. \n¿Deseas continuar?'):
            return
        try:
            if not os.path.exists(DELIVEREDDATAPATH):
                messagebox.showerror(title='Error', message='No hay reportes para enviar')
                return
            senderJob: SACSenderJob = SACSenderJob()
            senderJob.sendReports()
            messagebox.showinfo(title='Éxito', message='Reportes enviados')
            self.resetForm()
        except Exception as e:
            print(e)
            messagebox.showerror(title='Error', message='SAC Sender no pudo ejecutarse')
        
    def updateUnifiedDocument(self, nombreDestinatario: str):
        if not os.path.exists(DELIVEREDDATAPATH):
            return
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
        if not os.path.exists(f'{GENERATEDREPORTSPATH}/Semana_{getWeekMondayTimeStamp()}/{nombreDestinatario}'):
            os.makedirs(f'{GENERATEDREPORTSPATH}/Semana_{getWeekMondayTimeStamp()}/{nombreDestinatario}')
        shutil.copy(f'{DELIVEREDDATAPATH}/{nombreDestinatario}/Documento.pdf', f'{GENERATEDREPORTSPATH}/Semana_{getWeekMondayTimeStamp()}/{nombreDestinatario}/Documento.pdf')
        pdfMerger.close()

    def generateUnifiedDocument(self):
        if not os.path.exists(DELIVEREDDATAPATH):
            return
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
            if not os.path.exists(f'{GENERATEDREPORTSPATH}/Semana_{getWeekMondayTimeStamp()}/{nombreDestinatario}'):
                os.makedirs(f'{GENERATEDREPORTSPATH}/Semana_{getWeekMondayTimeStamp()}/{nombreDestinatario}')
            shutil.copy(f'{DELIVEREDDATAPATH}/{nombreDestinatario}/Documento.pdf', f'{GENERATEDREPORTSPATH}/Semana_{getWeekMondayTimeStamp()}/{nombreDestinatario}/Documento.pdf')
        pdfMerger.close()
        
                
        
                    