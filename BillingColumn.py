from datetime import datetime

class BillingColumn:
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
