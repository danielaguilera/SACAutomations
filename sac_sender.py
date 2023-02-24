from Clases.ReporteData import ReporteData
from Utils.Metadata import *
from Utils.GlobalFunctions import *
from Clases.SACConnector import SACConnector
from Clases.PDFGenerator import PDFGenerator
from Clases.FileGrouper import FileGrouper
import os

if __name__ == '__main__':
    fileGrouper: FileGrouper = FileGrouper()
    
    # Generating reports:
    numsBoleta: list[int] = [int(dirName) for dirName in os.listdir(DELIVEREDDATAPATH)]
    for numBoleta in numsBoleta:
        sacConnector: SACConnector = SACConnector()
        reporteData: ReporteData = sacConnector.getReporteData(numBoleta=numBoleta)
        if reporteData:
            pdfGenerator: PDFGenerator = PDFGenerator()
            reporte: ReporteData = pdfGenerator.generateReporte(reporteData=reporteData)
            fileGrouper.addReporte(reporte=reporte)
            
    # Exporting full documents:
    
    
        



