from tkinter import *
from tkinter import ttk
from Clases.SACConnector import SACConnector
from Clases.Servicio import Servicio
from tkinter import messagebox

class RendicionGUI:
    def __init__(self, container, ):
        self.container = container
        self.toplevel = Toplevel()
        self.toplevel.title(string='Número rendición')
        