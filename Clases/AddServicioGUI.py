from tkinter import *
from tkinter import ttk
from Clases.SACConnector import SACConnector
from Clases.Servicio import Servicio
from tkinter import messagebox

class AddServicioGUI:
    def __init__(self, container):
        self.container = container
        self.toplevel = Toplevel()
        self.toplevel.title(string='Agregar servicio')
        self.sacConnector = SACConnector()
        self.codigos = self.sacConnector.getAllCodigos()
        
        self.formFrame = Frame(master=self.toplevel)
        self.formFrame.pack(expand=True, fill=BOTH)
        self.headers = ['Código', 'Nota', 'Monto ($)']
        for index, header in enumerate(self.headers):
            Label(master=self.formFrame, text=header).grid(row=0, column=index, padx=5, pady=5)
            if index == 0:
                self.codigoDropdown = ttk.Combobox(master=self.formFrame, state='readonly', values=self.codigos)
                self.codigoDropdown.grid(row=1, column=index, padx=5, pady=5)
            elif index == 1:
                self.notaEntry = Entry(master=self.formFrame)
                self.notaEntry.grid(row=1, column=index, padx=5, pady=5)
            elif index == 2:
                self.montoEntry = Entry(master=self.formFrame)
                self.montoEntry.grid(row=1, column=index, padx=5, pady=5)
        self.actionFrame = Frame(master=self.toplevel)
        self.actionFrame.pack(expand=True, fill=BOTH)
        self.saveButton = Button(master=self.actionFrame, text='Añadir', command=self.saveForm)
        self.saveButton.pack(expand=True, fill=BOTH)
        
    def saveForm(self):
        if not self.montoEntry.get().isdigit():
            messagebox.showerror(title='Error', message='El monto debe ser un número entero')
            return
        if not self.codigoDropdown.get():
            messagebox.showerror(title='Error', message='Debe seleccionar un código')
            return
        nota: str = self.notaEntry.get()
        monto: int = int(self.montoEntry.get())
        codigo: int = self.codigoDropdown.get()
        servicio = Servicio(nota=nota, monto=monto, codigo=codigo)
        self.container.addServicio(servicio=servicio)
        self.toplevel.destroy()
        self.toplevel.update()
        
        
                
        
            
            
         