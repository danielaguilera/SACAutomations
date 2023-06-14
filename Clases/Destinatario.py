class Destinatario:
    def __init__(self, nombreDestinatario: str, correoDestinatario: str, cc: list[str] = [], id: int = 0):
        self.id = id
        self.cc = cc
        self.nombreDestinatario = nombreDestinatario
        self.correoDestinatario = correoDestinatario
        
    def __str__(self):
        return str(self.__dict__)