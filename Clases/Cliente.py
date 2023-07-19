class Cliente:
    def __init__(self, idCliente : int, nombreCliente : str, factura: str = ''):
        self.idCliente = idCliente
        self.nombreCliente = nombreCliente
        self.factura = factura
        
    def __str__(self):
        return str(self.__dict__)
