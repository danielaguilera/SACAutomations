from Clases.ReporteData import ReporteData
from Utils.Metadata import *
from Utils.GlobalFunctions import *
from Clases.SACConnector import SACConnector
from Clases.PDFGenerator import PDFGenerator
from Clases.FileGrouper import FileGrouper
from Clases.MailSender import MailSender
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
            pdfGenerator.generateReporte(reporteData=reporteData)
            fileGrouper.addReporte(reporte=reporteData)
            
    # Exporting full documents:
    fileGrouper.generateUnifiedPDFs()
    
    # Sending emails:
    with open(MAILDATA) as file:
        senderUsername, senderPassword = file.readline().strip().split(',')
        print(senderUsername)
        print(senderPassword)
    smtpServer: str = SMTPSERVER
    smtpPort: int = SMTPPORT
    mailSender: MailSender = MailSender(senderUsername=senderUsername, senderPassword=senderPassword, smtpServer=smtpServer, smtpPort=smtpPort)
    for documento in fileGrouper.documentosUnificados:
        mailSender.sendUnifiedDocument(documento)
    
    
        



