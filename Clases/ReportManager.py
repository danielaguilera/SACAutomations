from tkinter import *
from tkinter import ttk
from Clases.SACConnector import SACConnector
from Utils.Metadata import *
from Clases.Servicio import Servicio
from tkinter import messagebox
import os

class ReportManager:
    def __init__(self, container):
        self.container = container
        self.toplevel = Toplevel()
        self.toplevel.title(string='Reportes a enviar')
        self.sacConnector: SACConnector = SACConnector()
        
        self.reportFrame = Frame(master=self.toplevel)
        self.reportFrame.pack(expand=True, fill=BOTH)
        self.reportColumns = ['Destinatario', 'Email', '# Boleta', 'ID Mapsa', 'Beneficiario', 'Cliente', 'Deudor', 'Monto Total (CLP)']
        self.reportTable = ttk.Treeview(master=self.reportFrame, columns=self.reportColumns, show='headings', height=3)
        for columnName in self.reportColumns:
            self.reportTable.heading(columnName, text=columnName)
            self.reportTable.column(columnName, width=100)
        self.reportTable.pack(expand=True, fill=BOTH, anchor=CENTER)
        
        self.getReports()
        
    def getReports(self):
        nombreDestinatario: str
        for nombreDestinatario in os.listdir(RESULTPATH):
            with open(f'{RESULTPATH}/{nombreDestinatario}/Boletas.txt', 'r') as file:
                for line in file.readlines():
                    print(line)