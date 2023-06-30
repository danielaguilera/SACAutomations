from Clases.Caso import Caso

class Deudor:
    def __init__(self, rawName: str = '', rutDeudor: str = '', apellidoDeudor: str = '', idCliente: int = 0, nombreDeudor: str = '', casoAsociado: Caso = None):
        self.rutDeudor = rutDeudor
        self.apellidoDeudor = apellidoDeudor
        self.nombreDeudor = nombreDeudor
        self.idCliente = idCliente
        self.rawName = rawName
        self.casoAsociado = casoAsociado
        
    def __str__(self):
        return str(self.__dict__)