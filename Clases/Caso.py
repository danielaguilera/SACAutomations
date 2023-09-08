from datetime import datetime

class Caso:
    def __init__(self, idMapsa: int, nombreEstado: str, fechaAsignado: datetime, bsecs: str | int, apellidoDeudor: str, nombreDeudor: str, rutDeudor: str, idCliente: int, nombreCliente: str, factura: str = '', lastGestionDate: datetime = None):
        self.idMapsa = idMapsa
        self.nombreEstado = nombreEstado
        self.fechaAsignado = fechaAsignado
        self.bsecs = bsecs
        self.apellidoDeudor = apellidoDeudor
        self.nombreDeudor = nombreDeudor
        self.rutDeudor = rutDeudor
        self.idCliente = idCliente
        self.nombreCliente = nombreCliente
        self.nombreEstadoAnterior = nombreEstado
        self.factura = factura
        self.lastGestionDate = lastGestionDate
        
    def __repr__(self):
        return f'{self.idMapsa} - {self.rutDeudor} - {self.apellidoDeudor} - Estado actual: {self.nombreEstado}'
    
    def __str__(self):
        return f'{self.idMapsa} - {self.rutDeudor} - {self.apellidoDeudor} - Estado actual: {self.nombreEstado}'