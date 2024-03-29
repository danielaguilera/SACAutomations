from Clases.Beneficiario import Beneficiario
from Clases.Servicio import Servicio
from Clases.Destinatario import Destinatario
from Utils.Metadata import *

class ReporteData:
    def __init__(self, numBoleta: int, beneficiario: Beneficiario, servicios: list[Servicio], destinatario: Destinatario, idMapsa: int = 0):
        self.numBoleta = numBoleta
        self.idMapsa = idMapsa
        self.beneficiario = beneficiario
        self.servicios = servicios
        self.destinatario = destinatario
        
    def overwriteDeudorName(self, newDeudorName: str):
        servicio: Servicio
        for servicio in self.servicios:
            servicio.nombreDeudor = newDeudorName
        
    @property
    def sumaTotal(self):
        return sum([servicio.monto for servicio in self.servicios])
    
    @property
    def sumaLiquida(self):
        return 0.8*self.sumaTotal
    
    def __repr__(self):
        return self.__dict__
        
    def __str__(self):
        return self.__dict__