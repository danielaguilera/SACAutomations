from datetime import datetime

class Servicio:
    def __init__(self, rutDeudor : str, apellidoDeudor : str, nombreDeudor : str, idCliente : int, nombreCliente : str, boleta : int, fecha : str, monto : int, nota : str, codigo : str):
        self.rutDeudor = rutDeudor
        self.apellidoDeudor = apellidoDeudor
        self.nombreDeudor = nombreDeudor
        self.idCliente = idCliente
        self.nombreCliente = nombreCliente
        self.boleta = boleta
        self.fecha = fecha
        self.monto = monto
        self.nota = nota
        self.codigo = codigo
        
    def __str__(self):
        return str(self.__dict__)
    
    def __repr__(self):
        return self.__str__()
