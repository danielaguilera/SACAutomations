class Destinatario:
    def __init__(self, nombreDestinatario: str, correoDestinatario: str):
        self.nombreDestinatario = nombreDestinatario
        self.correoDestinatario = correoDestinatario
        
    def __str__(self):
        return str(self.__dict__)