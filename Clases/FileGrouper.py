from Clases.ReporteData import ReporteData
from Clases.Destinatario import Destinatario
from Utils.Metadata import *
from Utils.GlobalFunctions import *
from PyPDF2 import PdfMerger
import os

class FileGrouper:
    def __init__(self):
        self.documentosUnificados: list[DocumentoUnificado] = []
        self.reportes: list[ReporteData] = []
        
    def addReporte(self, reporte: ReporteData) -> None:
        documentoUnificado: DocumentoUnificado
        for documentoUnificado in self.documentosUnificados:
            if documentoUnificado.destinatario.nombreDestinatario == reporte.destinatario.nombreDestinatario:
                documentoUnificado.addNumBoleta(numBoleta=reporte.numBoleta, idMapsa=reporte.idMapsa)
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
            reportePath: str = f'{DELIVEREDDATAPATH}/{numBoleta}_{idMapsa}/Reporte_{numBoleta}.pdf'
            boletaPath: str = f'{DELIVEREDDATAPATH}/{numBoleta}_{idMapsa}/Boleta_{numBoleta}.pdf'
            anexoPath: str = f'{DELIVEREDDATAPATH}/{numBoleta}_{idMapsa}/Anexo_{numBoleta}.pdf'
            paths.append(reportePath)
            paths.append(boletaPath)
            if os.path.exists(anexoPath):
                paths.append(anexoPath)
        path: str
        for path in paths:
            pdfMerger.append(path)
        if not os.path.exists(f'{RESULTPATH}/{self.destinatario.nombreDestinatario}'):
            os.makedirs(f'{RESULTPATH}/{self.destinatario.nombreDestinatario}')
        pdfMerger.write(f'{RESULTPATH}/{self.destinatario.nombreDestinatario}/Documento.pdf')
        with open(f'{RESULTPATH}/{self.destinatario.nombreDestinatario}/Boletas.txt','a') as file:
            for numBoleta, idMapsa in zip(self.numsBoletas, self.idsMapsa):
                file.write(f'{numBoleta},{idMapsa}\n')
        pdfMerger.close()  ### Esta función debiese ejecutarse en sac sender, no en ui (ya que debe hacerse cuando todos los reportes estén ya generados)

        
        
        
