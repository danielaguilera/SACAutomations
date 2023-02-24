from Clases.ReporteData import ReporteData
from Clases.Destinatario import Destinatario
from collections import defaultdict

class FileGrouper:
    def __init__(self):
        self.reportes: list[ReporteData] = []
        self.grupos: defaultdict[list[int]] = defaultdict(list[int])
    
    def getDestinatarios(self):
        destinatarios: list[Destinatario] = []
        for reporte in self.reportes:
            reporte.destinatario
        
    def addReporte(self, reporte: ReporteData):
        self.reportes.append(reporte)
        self.grupos[reporte.destinatario.nombreDestinatario].append('')
        
        ### ES NECESARIO ASOCIAR REPORTES COND ESTINATARIOS
        
        
        
