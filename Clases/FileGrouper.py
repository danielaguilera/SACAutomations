from Clases.ReporteData import ReporteData
from Clases.Destinatario import Destinatario
from Utils.Metadata import *
from Utils.GlobalFunctions import *
from PyPDF2 import PdfMerger
import os

class FileGrouper:
    def __init__(self):
        self.documentosUnificados: list[DocumentoUnificado] = []
        
    def addReporte(self, reporte: ReporteData) -> None:
        documentoUnificado: DocumentoUnificado
        for documentoUnificado in self.documentosUnificados:
            if documentoUnificado.destinatario.nombreDestinatario == reporte.destinatario.nombreDestinatario:
                documentoUnificado.addNumBoleta(reporte.numBoleta)
                return
        newDocumento: DocumentoUnificado = DocumentoUnificado(destinatario=reporte.destinatario)
        newDocumento.addNumBoleta(reporte.numBoleta)
        self.documentosUnificados.append(newDocumento)
            
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
        
    def addNumBoleta(self, numBoleta: int):
        self.numsBoletas.append(numBoleta)
        
    def generateUnifiedPDF(self):
        paths: list[str] = []
        pdfMerger: PdfMerger = PdfMerger()
        for numBoleta in self.numsBoletas:
            reportePath: str = f'{GENERATEDREPORTSPATH}/Semana_{getWeekMondayTimeStamp()}/Reporte_{numBoleta}.pdf'
            boletaPath: str = f'{DELIVEREDDATAPATH}/{numBoleta}/Boleta_{numBoleta}.pdf'
            anexoPath: str = f'{DELIVEREDDATAPATH}/{numBoleta}/Anexo_{numBoleta}.pdf'
            paths.append(reportePath)
            paths.append(boletaPath)
            if os.path.exists(anexoPath):
                paths.append(anexoPath)
        path: str
        for path in paths:
            pdfMerger.append(path)
        pdfMerger.write(f'{RESULTPATH}/{self.destinatario.nombreDestinatario}.pdf')
        pdfMerger.close()       

        
        
        
