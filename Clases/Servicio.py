from datetime import datetime

class Servicio:
    def __init__(self, monto : int = 0, nota : str = '', codigo : str = '', rutDeudor : str = '', apellidoDeudor : str = '', nombreDeudor : str = '', idCliente : int = 0, nombreCliente : str = '', boleta : int = 0, fecha : str = ''):
        self.rutDeudor: str = rutDeudor
        self.apellidoDeudor: str = apellidoDeudor
        self.nombreDeudor: str = nombreDeudor
        self.idCliente: int = idCliente
        self.nombreCliente: int = nombreCliente
        self.boleta: int = boleta
        self.fecha: str = fecha
        self.monto: int = monto
        self.nota: str = nota
        self.codigo: str = codigo
        
    @property
    def codigoHeader(self):
        return self.codigo.split(' ')[0]
        
    def __str__(self):
        return str(self.__dict__)
    
    def __repr__(self):
        return self.__str__()
