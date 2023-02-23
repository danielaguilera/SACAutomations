from ReporteData import ReporteData
from Metadata import *
from GlobalFunctions import *
from SACConnector import SACConnector
from PDFGenerator import PDFGenerator

numBoleta : int = 6109
year = 2022

if __name__ == '__main__':    
    sacConnector: SACConnector = SACConnector()
    reporteData: ReporteData = sacConnector.getReporteData(numBoleta=numBoleta)
    pdfGenerator: PDFGenerator = PDFGenerator()
    pdfGenerator.generateReporte(reporteData=reporteData)



