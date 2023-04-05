from Clases.Servicio import Servicio
from datetime import date

class Boleta:
    def __init__(self, idMapsa: int, numBoleta: int, fechaEmision: date, rutBeneficiario: str, servicios: list[Servicio]):
        self.idMapsa: int = idMapsa
        self.numBoleta: int = numBoleta
        self.fechaEmision: date = fechaEmision
        self.rutBeneficiario: str = rutBeneficiario
        self.servicios: list[Servicio] = servicios