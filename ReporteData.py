from Beneficiario import Beneficiario
from Servicio import Servicio
from Destinatario import Destinatario

class ReporteData:
    def __init__(self, numBoleta: int, beneficiario: Beneficiario, servicios: list[Servicio], destinatario: Destinatario):
        self.numBoleta = numBoleta
        self.beneficiario = beneficiario
        self.servicios = servicios
        self.destinatario = destinatario