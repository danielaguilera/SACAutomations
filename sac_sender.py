from PyPDF2 import PdfMerger
from Clases.Destinatario import Destinatario
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
    # Checks if there is data:
    if not os.path.exists(DELIVEREDDATAPATH):
        print('No hay datos para enviar')
        sys.exit()
        
    # Sending emails:
    with open(MAILDATA, 'r') as file:
        senderUsername, senderPassword = file.readline().strip().split(',')
    smtpServer: str = SMTPSERVER
    smtpPort: int = SMTPPORT
    mailSender: MailSender = MailSender(senderUsername=senderUsername, senderPassword=senderPassword, smtpServer=smtpServer, smtpPort=smtpPort)
    boletasSent = []
    
    for nombreDestinatario in os.listdir(path=f'{DELIVEREDDATAPATH}'):
        pdfMerger: PdfMerger = PdfMerger()
        for path in os.listdir(path=f'{DELIVEREDDATAPATH}/{nombreDestinatario}'):
            if path != 'Documento.pdf':
                numBoleta, idMapsa = (int(x) for x in path.strip().split('_'))
                with open(f'{DELIVEREDDATAPATH}/{nombreDestinatario}/{path}/Data_{numBoleta}.txt','r') as file:
                    correoDestinatario: str = file.readline().strip().split(',')[1] 
                boletasSent.append((numBoleta, idMapsa))
        destinatario: Destinatario = Destinatario(nombreDestinatario=nombreDestinatario, correoDestinatario=correoDestinatario)
        mailSender.sendUnifiedDocument(destinatario=destinatario)  
    
    # Setting boleta data as printed:
    boletaData: tuple
    sacConnector: SACConnector = SACConnector()
    for boletaData in boletasSent:
        numBoleta, idMapsa = boletaData
        sacConnector.setBoletaAsPrinted(numBoleta=numBoleta, idMapsa=idMapsa)
        
    # Erasing generated folders:
    deleteIfExists(DELIVEREDDATAPATH)
    
    
    
        



