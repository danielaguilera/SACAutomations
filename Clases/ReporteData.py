from Clases.Beneficiario import Beneficiario
from Clases.Servicio import Servicio
from Clases.Destinatario import Destinatario

class ReporteData:
    def __init__(self, numBoleta: int, beneficiario: Beneficiario, servicios: list[Servicio], destinatario: Destinatario):
        self.numBoleta = numBoleta
        self.beneficiario = beneficiario
        self.servicios = servicios
        self.destinatario = destinatario
        
    @property
    def sumaTotal(self):
        return sum([servicio.monto for servicio in self.servicios])