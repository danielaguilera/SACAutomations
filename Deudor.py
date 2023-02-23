class Deudor:
    def __init__(self, rutDeudor: str, apellidoDeudor: str, idCliente: int, nombreDeudor: str = ''):
        self.rutDeudor = rutDeudor
        self.apellidoDeudor = apellidoDeudor
        self.nombreDeudor = nombreDeudor
        self.idCliente = idCliente
        
    def __str__(self):
        return str(self.__dict__)