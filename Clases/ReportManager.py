from tkinter import *
from tkinter import ttk
from Clases.SACConnector import SACConnector
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
        self.toplevel = Toplevel()
        self.toplevel.title(string='Reportes a enviar')
        self.thumbnailFrame = Frame(master=self.toplevel)
        self.thumbnailFrame.pack(side=RIGHT)
        self.reporteImage = None
        self.thumbnail = Label(master=self.thumbnailFrame)
        self.sacConnector: SACConnector = SACConnector()
        self.reportFrame = Frame(master=self.toplevel)
        self.reportFrame.pack(expand=True, fill=BOTH)
        self.reportColumns = ['Destinatario', 'Email', '# Boleta', 'ID Mapsa', 'Beneficiario', 'Cliente', 'Deudor', 'Monto Total (CLP)']
        self.reportTable = ttk.Treeview(master=self.reportFrame, columns=self.reportColumns, show='headings', height=10)
        for columnName in self.reportColumns:
            self.reportTable.heading(columnName, text=columnName)
            self.reportTable.column(columnName, width=150)
        self.reportTable.pack(expand=True, fill=BOTH, anchor=CENTER, padx=5)
        self.reportTable.bind('<<TreeviewSelect>>', self.displayThumbnail)
        
        self.actionFrame = Frame(master=self.toplevel)
        self.actionFrame.pack(expand=True, fill=BOTH)
        self.deleteButton = Button(master=self.actionFrame, text='Eliminar reporte', width=40, height=1, font=('Helvetica bold', 20), command=self.deleteReport)
        self.deleteButton.pack(expand=False, fill=BOTH)
        
        self.getReports()
        
    def getReports(self):
        self.reportTable.delete(*self.reportTable.get_children())
        nombreDestinatario: str
        print('GET REPORTS')
        if not os.path.exists(DELIVEREDDATAPATH):
            print('AAAAAAAAAAAA')
            messagebox.showerror(title='ERROR', message='No se han cargado boletas para enviar.\nNo hay nada que mostrar.')
            return
        for nombreDestinatario in os.listdir(DELIVEREDDATAPATH):
            self.reportTable.insert('', END, iid=nombreDestinatario, values=(nombreDestinatario,'','','','','','',''), open=True)
            for dirName in os.listdir(f'{DELIVEREDDATAPATH}/{nombreDestinatario}'):
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
            
        self.reporteImage = PhotoImage(file='thumbnail.png')
        self.thumbnail.config(image=self.reporteImage)
        self.thumbnail.pack()
    
    def deleteReport(self):
        data = self.reportTable.item(self.reportTable.selection()[0])['values']
        if not(data[2] and data[3]):
            return
        numBoleta: int = int(data[2])
        idMapsa: int = int(data[3])
        nombreDestinatario: str = self.reportTable.item(self.reportTable.parent(self.reportTable.selection()[0]))['values'][0]
        self.sacConnector.deleteBoletaData(numBoleta=numBoleta, idMapsa=idMapsa)
        deleteIfExists(f'{DELIVEREDDATAPATH}/{nombreDestinatario}/{numBoleta}_{idMapsa}')
        deleteIfEmpty(f'{DELIVEREDDATAPATH}/{nombreDestinatario}')
        deleteIfEmpty(f'{DELIVEREDDATAPATH}')
        messagebox.showinfo(title='INFO', message='Reporte borrado')
        self.getReports()
        self.thumbnailFrame.pack_forget()
        
                
        
                    