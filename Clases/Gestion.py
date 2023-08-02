from datetime import date, datetime
from Utils.Metadata import *
from Utils.GlobalFunctions import *

class Gestion:
    def __init__(self, idJuicio: int, timestamp: datetime, tipo: str, user: str = 'SACAutomations') -> None:
        self.idJuicio: int = idJuicio
        self.fecha: str = transformDateToSpanishBrief(date=timestamp, point=False, english=False)
        self.gestion: str = PLPREQUESTCODE if tipo == PLP else PLPBREACHEDCODE
        self.nota: str = PLP if tipo == PLP else PLPINCUMPLIDO
        self.control: str = timestamp.strftime('%m/%d/%Y %I:%M:%S %p')
        self.user: str = user
        