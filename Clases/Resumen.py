from Clases.Beneficiario import Beneficiario
from Clases.Boleta import Boleta
from Clases.Caso import Caso
from Clases.Cliente import Cliente
from Clases.Destinatario import Destinatario
from Clases.Servicio import Servicio

class Resumen:
    def __init__(self, boleta: Boleta, caso: Caso, beneficiario: Beneficiario, servicios: list[Servicio], cliente: Cliente, destinatario: Destinatario, numeroRendicion: int = 0):
        self.boleta: Boleta = boleta
        self.caso: Caso = caso
        self.beneficiario: Beneficiario = beneficiario
        self.servicios: list[Servicio] = servicios
        self.cliente: Cliente = cliente
        self.destinatario: Destinatario = destinatario
        self.numeroRendicion = numeroRendicion
