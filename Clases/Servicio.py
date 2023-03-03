from datetime import datetime

class Servicio:
    def __init__(self, rutDeudor : str, apellidoDeudor : str, nombreDeudor : str, idCliente : int, nombreCliente : str, boleta : int, fecha : str, monto : int, nota : str, codigo : str):
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
        
    def __str__(self):
        return str(self.__dict__)
    
    def __repr__(self):
        return self.__str__()
