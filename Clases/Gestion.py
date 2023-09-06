from datetime import date, datetime
from Utils.Metadata import *
from Utils.GlobalFunctions import *

class Gestion:
    def __init__(self, idJuicio: int, timestamp: datetime, tipo: str, user: str = 'SACAutomations') -> None:
        self.idJuicio: int = idJuicio
        self.fecha: str = transformDateToSpanishBrief(date=timestamp, point=False, english=False)
        self.gestion: str = self.getGestionCode(tipo)
        self.nota: str = tipo
        self.control: str = timestamp.strftime('%m/%d/%Y %I:%M:%S %p')
        self.user: str = user
        
    def getGestionCode(self, tipo: str):
        if tipo == PLP:
            return PLPREQUESTCODE
        elif tipo == PLPBREACHED:
            return PLPBREACHEDCODE
        else:
            return JUDICIAL_COLLECTION_ACTIONS[tipo]
        