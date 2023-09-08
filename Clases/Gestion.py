from datetime import date, datetime
from Clases.Caso import Caso
from Utils.Metadata import *
from Utils.GlobalFunctions import *

class Gestion:
    def __init__(self, idJuicio: int = 0, timestamp: datetime = datetime.now(), tipo: str = '', user: str = 'SACAutomations', rutDeudor: str = '', nombreDeudor: str = '') -> None:
        self.idJuicio: int = idJuicio
        self.fecha: str = transformDateToSpanishBrief(date=timestamp, point=False, english=False)
        self.gestion: str = self.getGestionCode(tipo)
        self.nota: str = tipo
        self.control: str = timestamp.strftime('%m/%d/%Y %I:%M:%S %p')
        self.user: str = user
        self.rutDeudor: str = rutDeudor
        self.nombreDeudor: str = nombreDeudor
        
    def getGestionCode(self, tipo: str):
        if tipo == PLP:
            return PLPREQUESTCODE
        elif tipo == PLPBREACHED:
            return PLPBREACHEDCODE
        else:
            return JUDICIAL_COLLECTION_ACTIONS.get(tipo, tipo)
        