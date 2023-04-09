from Clases.ReporteData import ReporteData
from Utils.Metadata import *
from Utils.GlobalFunctions import *
from Clases.SACConnector import SACConnector
from Clases.PDFGenerator import PDFGenerator
from Clases.FileGrouper import FileGrouper
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
    numsBoleta: list[int] = [int(dirName) for dirName in os.listdir(DELIVEREDDATAPATH)]
    for numBoleta in numsBoleta:
        sacConnector: SACConnector = SACConnector()
        reporteData: ReporteData = sacConnector.getReporteData(numBoleta=numBoleta)
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
    sacConnector
    
    
    # Erasing generated folders:
    deleteIfExists(GENERATEDREPORTSPATH)
    deleteIfExists(RESULTPATH)
    deleteIfExists(DELIVEREDDATAPATH)
    
    
    
        



