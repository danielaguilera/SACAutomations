from Beneficiario import Beneficiario
from Boleta import Boleta
from Cliente import Cliente
from Deudor import Deudor

class InvoiceData:
    def __init__(self, deudor : Deudor, cliente : Cliente, beneficiario : Beneficiario, boleta : Boleta):
        self.deudor : Deudor = deudor
        self.cliente : Cliente = cliente
        self.beneficiario : Beneficiario = beneficiario
        self.boleta : Boleta = boleta
