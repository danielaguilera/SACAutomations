from Clases.ReporteData import ReporteData
from Clases.Destinatario import Destinatario
from Utils.Metadata import *
from Utils.GlobalFunctions import *
from PyPDF2 import PdfMerger
import os

# BUG CON NUMS BOLETAS, HAY QUE AGREGAR EL ID MAPSA!!!

class FileGrouper:
    def __init__(self):
        self.documentosUnificados: list[DocumentoUnificado] = []
        self.reportes: list[ReporteData] = []
        
    def addReporte(self, reporte: ReporteData) -> None:
        documentoUnificado: DocumentoUnificado
        for documentoUnificado in self.documentosUnificados:
            if documentoUnificado.destinatario.nombreDestinatario == reporte.destinatario.nombreDestinatario:
                documentoUnificado.addNumBoleta(reporte.numBoleta)
                return
        newDocumento: DocumentoUnificado = DocumentoUnificado(destinatario=reporte.destinatario)
        newDocumento.addNumBoleta(numBoleta=reporte.numBoleta, idMapsa=reporte.idMapsa)
        self.documentosUnificados.append(newDocumento)
        self.reportes.append(reporte)
            
    def getGrupos(self) -> str:
        outputString: str = ''
        documento: DocumentoUnificado
        for documento in self.documentosUnificados:
            outputString += f'{documento.destinatario.nombreDestinatario}: {",".join(str(x) for x in documento.numsBoletas)} \n'
        return outputString
    
    def generateUnifiedPDFs(self):
        documento: DocumentoUnificado
        for documento in self.documentosUnificados:
            documento.generateUnifiedPDF()

class DocumentoUnificado:
    def __init__(self, destinatario: Destinatario):
        self.destinatario: Destinatario = destinatario
        self.numsBoletas: list[int] = []
        self.idsMapsa: list[int] = []
        
    def addNumBoleta(self, numBoleta: int, idMapsa: int):
        self.numsBoletas.append(numBoleta)
        self.idsMapsa.append(idMapsa)
    
    def generateUnifiedPDF(self):
        paths: list[str] = []
        pdfMerger: PdfMerger = PdfMerger()
        for numBoleta, idMapsa in zip(self.numsBoletas, self.idsMapsa):
            reportePath: str = f'{GENERATEDREPORTSPATH}/Semana_{getWeekMondayTimeStamp()}/Reporte_{numBoleta}_{idMapsa}.pdf'
            boletaPath: str = f'{DELIVEREDDATAPATH}/{numBoleta}_{idMapsa}/Boleta_{numBoleta}.pdf'
            anexoPath: str = f'{DELIVEREDDATAPATH}/{numBoleta}_{idMapsa}/Anexo_{numBoleta}.pdf'
            paths.append(reportePath)
            paths.append(boletaPath)
            if os.path.exists(anexoPath):
                paths.append(anexoPath)
        path: str
        for path in paths:
            pdfMerger.append(path)
        if not os.path.exists(RESULTPATH):
            os.makedirs(RESULTPATH)
        pdfMerger.write(f'{RESULTPATH}/{self.destinatario.nombreDestinatario}.pdf')
        pdfMerger.close()       

        
        
        
