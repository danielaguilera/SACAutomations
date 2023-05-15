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

class SACSenderJob:
    def __init__(self):
        pass
    
    def sendReports(self):
        # Checks if there is data:
        if not os.path.exists(DELIVEREDDATAPATH):
            print('No hay datos para enviar')
            sys.exit()        

        # Sending emails:
        with open(MAILDATA, 'r') as file:
            senderUsername, senderPassword = file.readline().strip().split(',')
        smtpServer: str = SMTPSERVERGYD
        smtpPort: int = SMTPPORTGYD
        mailSender: MailSender = MailSender(senderUsername=senderUsername, senderPassword=senderPassword, smtpServer=smtpServer, smtpPort=smtpPort)
        boletasSent = []
        
        for nombreDestinatario in os.listdir(path=f'{DELIVEREDDATAPATH}'):
            for path in os.listdir(path=f'{DELIVEREDDATAPATH}/{nombreDestinatario}'):
                if path != 'Documento.pdf':
                    numBoleta, idMapsa = (int(x) for x in path.strip().split('_'))
                    with open(f'{DELIVEREDDATAPATH}/{nombreDestinatario}/{path}/Data_{numBoleta}.txt','r') as file:
                        correoDestinatario: str = file.readline().strip().split(',')[1] 
                    boletasSent.append((numBoleta, idMapsa))
            destinatario: Destinatario = Destinatario(nombreDestinatario=nombreDestinatario, correoDestinatario=correoDestinatario)
            mailSender.sendUnifiedDocument(destinatario=destinatario)  
            if not os.path.exists(f'{GENERATEDREPORTSPATH}/Semana_{getWeekMondayTimeStamp()}/{nombreDestinatario}'):
                os.makedirs(f'{GENERATEDREPORTSPATH}/Semana_{getWeekMondayTimeStamp()}/{nombreDestinatario}')
            shutil.copy(f'{DELIVEREDDATAPATH}/{nombreDestinatario}/Documento.pdf', f'{GENERATEDREPORTSPATH}/Semana_{getWeekMondayTimeStamp()}/{nombreDestinatario}/Documento.pdf')     
        
        # Setting boleta data as printed:
        boletaData: tuple
        sacConnector: SACConnector = SACConnector()
        for boletaData in boletasSent:
            numBoleta, idMapsa = boletaData
            sacConnector.setBoletaAsPrinted(numBoleta=numBoleta, idMapsa=idMapsa)
            
        # Erasing generated folders:
        deleteIfExists(DELIVEREDDATAPATH)