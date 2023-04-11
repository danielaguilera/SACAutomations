from Clases.ReporteData import ReporteData
from Utils.Metadata import *
from Utils.GlobalFunctions import *
from Clases.SACConnector import SACConnector
from Clases.PDFGenerator import PDFGenerator
from Clases.FileGrouper import FileGrouper, DocumentoUnificado
from Clases.MailSender import MailSender
import os
import shutil
import sys

if __name__ == '__main__':
    
    # Checking whether there is data to send:
    if not os.path.exists(DELIVEREDDATAPATH):
        print('No se han recibido datos, saliendo...')
        sys.exit()
    
    # Generating reports:
    fileGrouper: FileGrouper = FileGrouper()
    dataReceived: list[str] = [dirName for dirName in os.listdir(DELIVEREDDATAPATH)]
    sacConnector: SACConnector = SACConnector()
    data: str
    for data in dataReceived:
        numBoleta: int = data.strip().split('_')[0]
        idMapsa: int = data.strip().split('_')[1]
        reporteData: ReporteData = sacConnector.getReporteData(numBoleta=numBoleta, idMapsa=idMapsa)
        if reporteData:
            pdfGenerator: PDFGenerator = PDFGenerator()
            pdfGenerator.generateReporte(reporteData=reporteData)
            fileGrouper.addReporte(reporte=reporteData)
            
    # Exporting full documents:
    fileGrouper.generateUnifiedPDFs()
    
    # Sending emails:
    with open(MAILDATA) as file:
        senderUsername, senderPassword = file.readline().strip().split(',')
    smtpServer: str = SMTPSERVER
    smtpPort: int = SMTPPORT
    mailSender: MailSender = MailSender(senderUsername=senderUsername, senderPassword=senderPassword, smtpServer=smtpServer, smtpPort=smtpPort)
    for documento in fileGrouper.documentosUnificados:
        mailSender.sendUnifiedDocument(documento)
        
    # Setting boleta data as printed:
    reporte: ReporteData
    for reporte in fileGrouper.reportes:
        sacConnector.setBoletaAsPrinted(reporte=reporte)
        
    # Erasing generated folders:
    deleteIfExists(RESULTPATH)
    deleteIfExists(DELIVEREDDATAPATH)
    
    
    
        



