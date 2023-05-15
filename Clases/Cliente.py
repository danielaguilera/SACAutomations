class Cliente:
    def __init__(self, idCliente : int, nombreCliente : str):
        self.idCliente = idCliente
        self.nombreCliente = nombreCliente
        
    def __str__(self):
        return str(self.__dict__)
