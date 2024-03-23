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
        self.headers = ['Código', 'Nota', 'Monto ($)', '']
        for index, header in enumerate(self.headers):
            Label(master=self.formFrame, text=header).grid(row=0, column=index, padx=5, pady=5)
            if index == 0:
                self.codigoDropdown = ttk.Combobox(master=self.formFrame, state='readonly', values=self.codigos, width=35)
                self.codigoDropdown.grid(row=1, column=index, padx=5, pady=5)
                self.codigoDropdown.bind("<<ComboboxSelected>>", self.writeCodeNote)
            elif index == 1:
                self.notaEntry = Entry(master=self.formFrame, justify='center')
                self.notaEntry.grid(row=1, column=index, padx=5, pady=5)
            elif index == 2:
                self.montoEntry = Entry(master=self.formFrame, justify='center')
                self.montoEntry.grid(row=1, column=index, padx=5, pady=5)
            elif index == 3:
                self.setTotalButton = Button(master=self.formFrame, text='Poner monto restante', fg = 'black', bg='RoyalBlue1', command=self.setTotalAmount)
                self.setTotalButton.grid(row=1, column=index, padx=5, pady=5)
        self.actionFrame = Frame(master=self.toplevel)
        self.actionFrame.pack(expand=True, fill=BOTH)
        self.saveButton = Button(master=self.actionFrame, text='Añadir', fg = 'black', bg='SeaGreen3', command=self.saveForm)
        self.saveButton.pack(expand=True, fill=BOTH)
    
    @property
    def totalAmount(self) -> int:
        data: str = self.container.gastoTotalEntry.get()
        if data.isdigit():
            return int(data)
        else:
            return 0    
        
    @property
    def remainingAmount(self) -> int:
        return self.totalAmount - self.container.servicioSum
    
    def writeCodeNote(self, key=None):
        self.notaEntry.delete(0, END)
        self.notaEntry.insert(0, 'cod ' + self.codigoDropdown.get().strip().split(' ')[0])
    
    def setTotalAmount(self):
        if self.totalAmount:
            self.montoEntry.delete(0, END)
            self.montoEntry.insert(0, self.remainingAmount)
        
    def saveForm(self):
        if not self.montoEntry.get().isdigit():
            messagebox.showerror(title='Error', message='El monto debe ser un número entero')
            return
        if not self.codigoDropdown.get():
            messagebox.showerror(title='Error', message='Debe seleccionar un código')
            return
        
        nota: str = self.notaEntry.get()
        monto: int = int(self.montoEntry.get())
        if monto > self.remainingAmount:
            messagebox.showerror(title='Error', message='Se excede el monto restante')
            return
        codigo: int = self.codigoDropdown.get()
        servicio = Servicio(nota=nota, monto=monto, codigo=codigo)
        self.container.addServicio(servicio=servicio)
        self.toplevel.destroy()
        self.toplevel.update()
        
        
                
        
            
            
         